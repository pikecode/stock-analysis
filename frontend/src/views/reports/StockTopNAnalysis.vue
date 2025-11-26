<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)

onMounted(() => {
  loadData()
})

const loadData = async () => {
  loading.value = true
  try {
    // API 调用将在此处进行
    ElMessage.success('数据加载成功')
  } catch (error) {
    ElMessage.error('数据加载失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="analysis">
    <el-card class="report-card">
      <template #header>
        <div class="card-header">
          <span class="title">🔝 Top N 分析</span>
        </div>
      </template>

      <el-empty description="暂无 Top N 分析数据" :image-size="200" />
    </el-card>
  </div>
</template>

<style scoped>
.analysis {
  padding: 0;
}

.report-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}
</style>
