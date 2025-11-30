<script setup lang="ts" generic="T extends Record<string, any>">
import { computed } from 'vue'

interface ColumnConfig {
  prop: keyof T
  label: string
  width?: string | number
  align?: 'left' | 'center' | 'right'
  formatter?: (row: T, column: any, cellValue: any, index: number) => string | number
}

interface Props {
  data: T[]
  columns: ColumnConfig[]
  loading?: boolean
  striped?: boolean
  maxHeight?: number | string
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  striped: true,
  maxHeight: 600,
})

const tableMaxHeight = computed(() => {
  if (typeof props.maxHeight === 'number') {
    return `${props.maxHeight}px`
  }
  return props.maxHeight
})
</script>

<template>
  <el-table
    :data="data"
    :stripe="striped"
    :max-height="tableMaxHeight"
    :default-sort="{ prop: 'rank', order: 'ascending' }"
    v-loading="loading"
  >
    <el-table-column
      v-for="column in columns"
      :key="String(column.prop)"
      :prop="String(column.prop)"
      :label="column.label"
      :width="column.width"
      :align="column.align || 'left'"
      :formatter="column.formatter"
    />
  </el-table>
</template>

<style scoped>
:deep(.el-table__header-wrapper) {
  overflow-x: hidden;
}
</style>
