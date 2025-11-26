<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title: string
  subtitle?: string
  loading?: boolean
  height?: number | string
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  height: 400,
})

const containerHeight = computed(() => {
  if (typeof props.height === 'number') {
    return `${props.height}px`
  }
  return props.height
})
</script>

<template>
  <el-card class="chart-card" :body-style="{ padding: '20px' }">
    <template #header>
      <div class="card-header">
        <div>
          <div class="card-title">{{ title }}</div>
          <div v-if="subtitle" class="card-subtitle">{{ subtitle }}</div>
        </div>
      </div>
    </template>

    <el-skeleton v-if="loading" :rows="5" animated />
    <div v-else :style="{ height: containerHeight }">
      <slot />
    </div>
  </el-card>
</template>

<style scoped>
.chart-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.card-subtitle {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
