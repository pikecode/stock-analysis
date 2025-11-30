<script setup lang="ts">
import { ref, onMounted } from 'vue'

const stats = ref({
  totalStocks: 0,
  totalConcepts: 0,
  totalUsers: 0,
  todayImports: 0
})

onMounted(() => {
  // 模拟数据加载
  stats.value = {
    totalStocks: 4523,
    totalConcepts: 256,
    totalUsers: 128,
    todayImports: 5
  }
})
</script>

<template>
  <div class="admin-dashboard">
    <h1>管理后台</h1>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card>
          <el-statistic title="股票总数" :value="stats.totalStocks" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <el-statistic title="概念总数" :value="stats.totalConcepts" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <el-statistic title="用户总数" :value="stats.totalUsers" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <el-statistic title="今日导入" :value="stats.todayImports" />
        </el-card>
      </el-col>
    </el-row>

    <el-card class="chart-card">
      <template #header>
        <span>系统概览</span>
      </template>
      <el-empty description="图表功能开发中" />
    </el-card>
  </div>
</template>

<style scoped>
.admin-dashboard {
  padding: 20px;
}

h1 {
  margin-bottom: 24px;
}

.stats-row {
  margin-bottom: 24px;
}

.chart-card {
  margin-top: 24px;
}
</style>
