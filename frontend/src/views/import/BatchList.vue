<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { importApi } from '@/api'
import type { ImportBatch } from '@/types'
import { Refresh } from '@element-plus/icons-vue'

const loading = ref(false)
const allBatches = ref<ImportBatch[]>([])
const activeTab = ref('all') // 'all', 'csv', 'txt'
const activeMetricTab = ref('TTV') // For TXT tab: 'TTV', 'EEE'

const searchParams = ref({
  status: '',
  page: 1,
  page_size: 20,
})

const statusOptions = [
  { label: '全部', value: '' },
  { label: '处理中', value: 'processing' },
  { label: '成功', value: 'success' },
  { label: '失败', value: 'failed' },
]

// Filter batches by file type
const batches = computed(() => {
  if (activeTab.value === 'csv') {
    return allBatches.value.filter(b => b.file_type === 'CSV')
  } else if (activeTab.value === 'txt') {
    // Further filter by metric type for TXT tab
    return allBatches.value.filter(b => b.file_type === 'TXT' && b.metric_code === activeMetricTab.value)
  }
  return allBatches.value
})

const fetchData = async () => {
  loading.value = true
  try {
    allBatches.value = await importApi.getBatches(searchParams.value)
  } finally {
    loading.value = false
  }
}

const handleRecompute = async (batch: ImportBatch) => {
  try {
    await ElMessageBox.confirm('确定要重新计算该批次的排名和汇总吗？', '提示', {
      type: 'warning',
    })
    await importApi.recompute(batch.id)
    ElMessage.success('重新计算任务已提交')
    fetchData()
  } catch {
    // Cancelled
  }
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'success':
      return 'success'
    case 'failed':
      return 'danger'
    case 'processing':
      return 'warning'
    case 'completed':
      return 'success'
    default:
      return 'info'
  }
}

const getStatusLabel = (status: string) => {
  switch (status) {
    case 'success':
    case 'completed':
      return '成功'
    case 'failed':
      return '失败'
    case 'processing':
      return '处理中'
    case 'pending':
      return '等待中'
    default:
      return status
  }
}

const getComputeStatusLabel = (row: ImportBatch) => {
  if (row.file_type === 'CSV') {
    return '不适用'
  }
  return getStatusLabel(row.compute_status)
}

// Watch tab change to refresh data
watch(() => activeTab.value, () => {
  searchParams.value.page = 1
})

onMounted(fetchData)
</script>

<template>
  <div class="batch-list">
    <div class="page-header">
      <h1 class="page-title">导入记录</h1>
      <el-button type="primary" :icon="Refresh" @click="fetchData">刷新</el-button>
    </div>

    <el-card>
      <!-- Tab 布局区分 CSV 和 TXT -->
      <el-tabs v-model="activeTab">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane label="CSV (股票-概念关系)" name="csv" />
        <el-tab-pane label="TXT (指标数据)" name="txt">
          <!-- Sub-tabs for metric types within TXT -->
          <el-tabs v-model="activeMetricTab" style="margin-top: -10px">
            <el-tab-pane label="TTV (成交金额)" name="TTV" />
            <el-tab-pane label="EEE (活跃度)" name="EEE" />
          </el-tabs>
        </el-tab-pane>
      </el-tabs>

      <div class="search-form">
        <el-select v-model="searchParams.status" placeholder="状态" style="width: 120px">
          <el-option
            v-for="opt in statusOptions"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </el-select>
        <el-button type="primary" @click="fetchData">搜索</el-button>
      </div>

      <!-- 全部和 CSV 共用的简化表格 -->
      <el-table v-if="activeTab === 'all' || activeTab === 'csv'" :data="batches" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="file_name" label="文件名" show-overflow-tooltip />
        <el-table-column v-if="activeTab === 'all'" prop="file_type" label="类型" width="80" />
        <el-table-column prop="status" label="导入状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="记录数" width="150">
          <template #default="{ row }">
            <span>
              成功: {{ row.success_rows }} / 总计: {{ row.total_rows }}
            </span>
            <span v-if="row.error_rows > 0" style="color: #f56c6c">
              (失败: {{ row.error_rows }})
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ row.created_at?.slice(0, 19).replace('T', ' ') }}
          </template>
        </el-table-column>
      </el-table>

      <!-- TXT 专用的完整表格（包含日期、计算状态和重新计算按钮） -->
      <el-table v-if="activeTab === 'txt'" :data="batches" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="file_name" label="文件名" show-overflow-tooltip />
        <el-table-column prop="data_date" label="数据日期" width="120" />
        <el-table-column prop="status" label="导入状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="compute_status" label="计算状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.file_type === 'CSV'" type="info">不适用</el-tag>
            <el-tag v-else :type="getStatusType(row.compute_status)">
              {{ getComputeStatusLabel(row) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="记录数" width="150">
          <template #default="{ row }">
            <span>
              成功: {{ row.success_rows }} / 总计: {{ row.total_rows }}
            </span>
            <span v-if="row.error_rows > 0" style="color: #f56c6c">
              (失败: {{ row.error_rows }})
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ row.created_at?.slice(0, 19).replace('T', ' ') }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button
              type="primary"
              link
              @click="handleRecompute(row)"
              :disabled="row.status !== 'completed' && row.status !== 'success'"
            >
              重新计算
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: bold;
}

.search-form {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}
</style>
