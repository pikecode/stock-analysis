<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { importApi } from '@/api'
import type { ImportBatch } from '@/types'
import { Refresh } from '@element-plus/icons-vue'

const loading = ref(false)
const batches = ref<ImportBatch[]>([])

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

const fetchData = async () => {
  loading.value = true
  try {
    batches.value = await importApi.getBatches(searchParams.value)
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
    default:
      return 'info'
  }
}

const getStatusLabel = (status: string) => {
  switch (status) {
    case 'success':
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

onMounted(fetchData)
</script>

<template>
  <div class="batch-list">
    <div class="page-header">
      <h1 class="page-title">导入记录</h1>
      <el-button type="primary" :icon="Refresh" @click="fetchData">刷新</el-button>
    </div>

    <el-card>
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

      <el-table :data="batches" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="file_name" label="文件名" show-overflow-tooltip />
        <el-table-column prop="file_type" label="类型" width="80" />
        <el-table-column prop="metric_code" label="指标" width="80" />
        <el-table-column prop="data_date" label="数据日期" width="120" />
        <el-table-column prop="status" label="导入状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="compute_status" label="计算状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.compute_status)">
              {{ getStatusLabel(row.compute_status) }}
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
              :disabled="row.status !== 'success'"
            >
              重新计算
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>
