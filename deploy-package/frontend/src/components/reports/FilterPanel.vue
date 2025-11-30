<script setup lang="ts">
import { ref, reactive } from 'vue'
import type { FormInstance } from 'element-plus'

interface FilterData {
  startDate: string
  endDate: string
  metricCode: string
  conceptId?: number
  stockCode?: string
  topN?: number
}

defineProps<{
  loading?: boolean
  showConceptId?: boolean
  showStockCode?: boolean
  showTopN?: boolean
}>()

const emit = defineEmits<{
  submit: [data: FilterData]
}>()

const formRef = ref<FormInstance>()

const formData = reactive<FilterData>({
  startDate: '',
  endDate: '',
  metricCode: 'TTV',
  conceptId: undefined,
  stockCode: undefined,
  topN: 10,
})

const metricOptions = [
  { label: '总交易额(TTV)', value: 'TTV' },
  { label: '筹码分布(EEE)', value: 'EEE' },
]

const handleSubmit = async () => {
  await formRef.value?.validate()
  emit('submit', formData)
}

const handleReset = () => {
  formRef.value?.resetFields()
}
</script>

<template>
  <el-card class="filter-panel" :body-style="{ padding: '20px' }">
    <el-form ref="formRef" :model="formData" label-width="100px" :disabled="loading">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="6">
          <el-form-item label="开始日期" prop="startDate" :rules="{ required: true, message: '请选择开始日期' }">
            <el-date-picker v-model="formData.startDate" type="date" placeholder="选择开始日期" />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-form-item label="结束日期" prop="endDate" :rules="{ required: true, message: '请选择结束日期' }">
            <el-date-picker v-model="formData.endDate" type="date" placeholder="选择结束日期" />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-form-item label="指标代码" prop="metricCode">
            <el-select v-model="formData.metricCode" placeholder="选择指标">
              <el-option v-for="option in metricOptions" :key="option.value" :label="option.label" :value="option.value" />
            </el-select>
          </el-form-item>
        </el-col>

        <el-col v-if="showConceptId" :xs="24" :sm="12" :md="6">
          <el-form-item label="概念ID" prop="conceptId">
            <el-input-number v-model="formData.conceptId" :min="1" placeholder="输入概念ID" />
          </el-form-item>
        </el-col>

        <el-col v-if="showStockCode" :xs="24" :sm="12" :md="6">
          <el-form-item label="股票代码" prop="stockCode">
            <el-input v-model="formData.stockCode" placeholder="输入股票代码" clearable />
          </el-form-item>
        </el-col>

        <el-col v-if="showTopN" :xs="24" :sm="12" :md="6">
          <el-form-item label="Top N" prop="topN">
            <el-input-number v-model="formData.topN" :min="1" :max="100" />
          </el-form-item>
        </el-col>

        <el-col :xs="24" :md="12" :lg="24" class="button-group">
          <el-button type="primary" @click="handleSubmit" :loading="loading">查询</el-button>
          <el-button @click="handleReset" :disabled="loading">重置</el-button>
        </el-col>
      </el-row>
    </el-form>
  </el-card>
</template>

<style scoped>
.filter-panel {
  margin-bottom: 20px;
}

.button-group {
  display: flex;
  justify-content: flex-start;
  gap: 10px;
}
</style>
