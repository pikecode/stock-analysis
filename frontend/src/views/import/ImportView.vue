<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { importApi } from '@/api'
import type { MetricType, ImportBatch } from '@/types'
import { Upload } from '@element-plus/icons-vue'
import type { UploadFile, UploadFiles } from 'element-plus'

const loading = ref(false)
const uploading = ref(false)
const metrics = ref<MetricType[]>([])
const uploadProgress = ref(0)
const currentBatchId = ref<number | null>(null)
const currentBatch = ref<ImportBatch | null>(null)
const activeStep = ref(0)
let pollInterval: ReturnType<typeof setInterval> | null = null

const fileTypeOptions = [
  { label: 'CSV (股票-概念关系)', value: 'CSV' },
  { label: 'TXT (指标数据)', value: 'TXT' },
]

const formData = ref({
  file_type: 'TXT',
  metric_code: 'EEE', // 默认选择 EEE
})

const fileList = ref<UploadFile[]>([])

// Check if upload is allowed
const canUpload = computed(() => {
  const hasFile = fileList.value.length > 0
  const hasMetric = formData.value.file_type === 'CSV' || formData.value.metric_code !== ''
  return hasFile && hasMetric
})

// Progress color based on percentage
const getProgressColor = computed(() => {
  if (uploadProgress.value < 30) return '#F56C6C'
  if (uploadProgress.value < 70) return '#E6A23C'
  return '#67C23A'
})

// Get step status
const getStepStatus = (stepIndex: number) => {
  if (activeStep.value > stepIndex) return 'finish'
  if (activeStep.value === stepIndex) return 'process'
  return 'wait'
}

// Format file size
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

const fetchMetrics = async () => {
  try {
    metrics.value = await importApi.getMetrics()
  } catch {
    metrics.value = []
  }
}

const handleFileChange = (file: UploadFile, files: UploadFiles) => {
  fileList.value = files.slice(-1) // Only keep last file

  // Auto detect metric from filename
  const fileName = file.name.toLowerCase()
  for (const metric of metrics.value) {
    if (metric.file_pattern && fileName.includes(metric.file_pattern.toLowerCase())) {
      formData.value.metric_code = metric.code
      break
    }
  }

  // Auto detect file type
  if (fileName.endsWith('.csv')) {
    formData.value.file_type = 'CSV'
  } else if (fileName.endsWith('.txt')) {
    formData.value.file_type = 'TXT'
  }
}

// Polling to check batch status
const pollBatchStatus = async () => {
  if (!currentBatchId.value) return

  try {
    const batch = await importApi.getBatch(currentBatchId.value)
    currentBatch.value = batch

    // Update progress based on status
    if (batch.status === 'pending') {
      uploadProgress.value = 20
    } else if (batch.status === 'processing') {
      if (batch.file_type === 'CSV') {
        uploadProgress.value = 50
      } else {
        // For TXT, include compute progress
        if (batch.compute_status === 'pending') {
          uploadProgress.value = 50
        } else if (batch.compute_status === 'computing') {
          uploadProgress.value = 75
        } else if (batch.compute_status === 'completed') {
          uploadProgress.value = 95
        }
      }
    } else if (batch.status === 'completed' || batch.status === 'success') {
      uploadProgress.value = 100
      stopPolling()
      const successRows = batch.success_rows || 0
      const totalRows = batch.total_rows || 0
      const errorRows = batch.error_rows || 0
      ElMessage.success(
        `导入成功！成功: ${successRows}, 失败: ${errorRows}, 总计: ${totalRows}`
      )
      resetForm()
    } else if (batch.status === 'failed') {
      uploadProgress.value = 0
      stopPolling()
      const errorMsg = batch.error_message || '导入失败'
      ElMessage.error(`导入失败: ${errorMsg}`)
      resetForm()
    }
  } catch (error) {
    console.error('轮询状态失败:', error)
  }
}

const startPolling = () => {
  if (pollInterval) clearInterval(pollInterval)
  pollInterval = setInterval(pollBatchStatus, 2000) // 每2秒检查一次
}

const stopPolling = () => {
  if (pollInterval) {
    clearInterval(pollInterval)
    pollInterval = null
  }
}

const resetForm = () => {
  fileList.value = []
  formData.value.metric_code = ''
  uploading.value = false
  currentBatchId.value = null
  currentBatch.value = null
  uploadProgress.value = 0
}

const handleUpload = async () => {
  if (!fileList.value.length) {
    ElMessage.warning('请选择文件')
    return
  }

  const file = fileList.value[0]
  if (!file.raw) {
    ElMessage.error('文件读取失败')
    return
  }

  if (formData.value.file_type === 'TXT' && !formData.value.metric_code) {
    ElMessage.warning('请选择指标类型')
    return
  }

  loading.value = true
  uploading.value = true
  uploadProgress.value = 10

  try {
    const data = new FormData()
    data.append('file', file.raw)
    data.append('file_type', formData.value.file_type)
    if (formData.value.metric_code) {
      data.append('metric_code', formData.value.metric_code)
    }

    const res = await importApi.upload(data)
    uploadProgress.value = 30
    currentBatchId.value = res.batch_id

    ElMessage.info(`文件上传成功，正在处理...`)

    // Start polling to track progress
    startPolling()
  } catch (error: any) {
    loading.value = false
    uploading.value = false
    uploadProgress.value = 0
    ElMessage.error(error?.response?.data?.detail || '上传失败')
  } finally {
    loading.value = false
  }
}

// Clean up on unmount
onUnmounted(() => {
  stopPolling()
})

onMounted(fetchMetrics)
</script>

<template>
  <div class="import-view">
    <div class="page-header">
      <h1 class="page-title">📊 数据导入</h1>
      <p class="page-subtitle">上传CSV或TXT文件进行股票数据导入和指标分析</p>
    </div>

    <div class="import-container">
      <!-- Steps -->
      <el-steps :active="activeStep" align-center class="steps-container">
        <el-step title="选择文件类型" :status="getStepStatus(0)" />
        <el-step title="配置导入参数" :status="getStepStatus(1)" />
        <el-step title="选择文件" :status="getStepStatus(2)" />
        <el-step title="上传并处理" :status="getStepStatus(3)" />
      </el-steps>

      <el-row :gutter="20" style="margin-top: 30px;">
        <!-- Upload Form -->
        <el-col :xl="16" :lg="18" :md="24" :offset-xl="4" :offset-lg="3">
          <el-card class="upload-card">
            <template #header>
              <div class="card-header">
                <span>📁 导入向导</span>
                <span v-if="!uploading" class="card-step">步骤 {{ activeStep + 1 }}/4</span>
              </div>
            </template>

            <el-form label-width="100px" class="import-form">
              <!-- Step 1: File Type Selection -->
              <div class="form-section" v-if="!uploading">
                <div class="section-title">第1步: 选择文件类型</div>
                <el-form-item label="文件类型">
                  <el-segmented v-model="formData.file_type" :options="fileTypeOptions" size="large" />
                  <div class="file-type-hint">
                    <span v-if="formData.file_type === 'CSV'">
                      💾 CSV 文件: 导入股票与概念的关联关系（股票代码、股票名称、概念）
                    </span>
                    <span v-else>
                      📈 TXT 文件: 导入每日指标数据（交易量、活跃度等指标）
                    </span>
                  </div>
                </el-form-item>
              </div>

              <!-- Step 2: Metric Selection (TXT only) -->
              <div class="form-section" v-if="!uploading && formData.file_type === 'TXT'">
                <div class="section-title">第2步: 选择指标类型</div>
                <el-form-item label="指标类型" required>
                  <el-radio-group v-model="formData.metric_code" class="metric-radio-group">
                    <el-radio
                      v-for="m in metrics"
                      :key="m.code"
                      :label="m.code"
                      size="large"
                      border
                    >
                      <div class="radio-content">
                        <span class="radio-name">{{ m.name }}</span>
                        <span class="radio-code">{{ m.code }}</span>
                      </div>
                    </el-radio>
                  </el-radio-group>
                  <div class="field-hint">
                    💡 文件名应包含日期（如: TTV_20240101.txt），日期将自动解析
                  </div>
                </el-form-item>
              </div>

              <!-- Step 3: File Upload -->
              <div class="form-section" v-if="!uploading">
                <div class="section-title">第3步: 选择文件</div>
                <el-form-item label="文件选择" required>
                  <div class="upload-wrapper">
                    <el-upload
                      drag
                      :auto-upload="false"
                      :file-list="fileList"
                      :on-change="handleFileChange"
                      :limit="1"
                      :accept="formData.file_type === 'CSV' ? '.csv' : '.txt'"
                      class="drag-upload"
                    >
                      <el-icon class="upload-icon"><Upload /></el-icon>
                      <div class="upload-text">
                        <div class="upload-title">拖拽或点击上传</div>
                        <div class="upload-desc">
                          支持 {{ formData.file_type }} 格式，文件大小不超过 100MB
                        </div>
                      </div>
                    </el-upload>
                  </div>
                </el-form-item>

                <!-- File Info -->
                <el-form-item v-if="fileList.length > 0" label="文件信息">
                  <div class="file-info-box">
                    <div class="file-info-item">
                      <span class="info-label">文件名:</span>
                      <span class="info-value">{{ fileList[0].name }}</span>
                    </div>
                    <div class="file-info-item">
                      <span class="info-label">文件大小:</span>
                      <span class="info-value">{{ formatFileSize(fileList[0].size || 0) }}</span>
                    </div>
                  </div>
                </el-form-item>
              </div>

              <!-- Step 4: Upload Action -->
              <div class="form-section" v-if="!uploading">
                <el-form-item>
                  <el-button
                    type="primary"
                    size="large"
                    @click="handleUpload"
                    :loading="loading"
                    :disabled="!canUpload"
                    class="upload-btn"
                  >
                    <el-icon><Upload /></el-icon>
                    开始导入
                  </el-button>
                  <span class="button-hint">点击开始上传文件并进行处理</span>
                </el-form-item>
              </div>

              <!-- Progress Section -->
              <div v-if="uploading" class="uploading-section">
                <div class="progress-container">
                  <!-- Animated Steps -->
                  <div class="process-steps">
                    <div class="process-step" :class="{ active: uploadProgress >= 10 }">
                      <div class="step-circle">1</div>
                      <div class="step-label">上传文件</div>
                    </div>
                    <div class="process-arrow" :class="{ active: uploadProgress >= 30 }"></div>
                    <div class="process-step" :class="{ active: uploadProgress >= 30 }">
                      <div class="step-circle">2</div>
                      <div class="step-label">数据解析</div>
                    </div>
                    <div class="process-arrow" :class="{ active: uploadProgress >= 50 }"></div>
                    <div class="process-step" :class="{ active: uploadProgress >= 50 }">
                      <div class="step-circle">3</div>
                      <div class="step-label">{{ formData.file_type === 'CSV' ? '导入完成' : '计算排名' }}</div>
                    </div>
                  </div>

                  <!-- Progress Bar -->
                  <div class="progress-bar-container" style="margin-top: 30px;">
                    <div class="progress-header">
                      <span class="progress-label">总进度</span>
                      <span class="progress-percent">{{ uploadProgress }}%</span>
                    </div>
                    <el-progress :percentage="uploadProgress" :color="getProgressColor" />
                  </div>

                  <!-- Status Info -->
                  <div v-if="currentBatch" class="status-container">
                    <el-alert
                      v-if="currentBatch.status === 'pending'"
                      title="⏳ 等待处理"
                      type="info"
                      :closable="false"
                    >
                      <template #description>
                        文件已上传，系统正在准备处理...
                      </template>
                    </el-alert>

                    <el-alert
                      v-else-if="currentBatch.status === 'processing'"
                      title="⚙️ 处理中"
                      type="warning"
                      :closable="false"
                    >
                      <template #description>
                        <div class="processing-details">
                          <div v-if="currentBatch.file_type === 'CSV'">
                            ✓ 正在导入股票-概念关系数据...
                          </div>
                          <div v-else>
                            ✓ 正在导入指标数据...
                            <div v-if="currentBatch.compute_status === 'pending'" style="margin-top: 8px;">
                              计算状态: <el-tag type="info">等待计算</el-tag>
                            </div>
                            <div v-else-if="currentBatch.compute_status === 'computing'" style="margin-top: 8px;">
                              计算状态: <el-tag type="warning">计算排名中</el-tag>
                            </div>
                          </div>
                        </div>
                      </template>
                    </el-alert>

                    <el-alert
                      v-else-if="currentBatch.status === 'completed' || currentBatch.status === 'success'"
                      title="✅ 导入成功"
                      type="success"
                      :closable="false"
                    >
                      <template #description>
                        <div class="success-details">
                          <div class="stat-row">
                            <span class="stat-label">成功:</span>
                            <span class="stat-value success">{{ currentBatch.success_rows }}</span>
                            <span class="stat-label">失败:</span>
                            <span class="stat-value error">{{ currentBatch.error_rows }}</span>
                            <span class="stat-label">总计:</span>
                            <span class="stat-value">{{ currentBatch.total_rows }}</span>
                          </div>
                          <div v-if="currentBatch.file_type === 'TXT'" style="margin-top: 8px;">
                            排名计算: <el-tag type="success">已完成</el-tag>
                          </div>
                        </div>
                      </template>
                    </el-alert>

                    <el-alert
                      v-else-if="currentBatch.status === 'failed'"
                      title="❌ 导入失败"
                      type="error"
                      :closable="false"
                    >
                      <template #description>
                        {{ currentBatch.error_message || '未知错误' }}
                      </template>
                    </el-alert>
                  </div>
                </div>
              </div>
            </el-form>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<style scoped>
/* Page header */
.import-view {
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
}

.page-title {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

/* Main container */
.import-container {
  max-width: 1400px;
}

/* Steps indicator */
.steps-container {
  margin-bottom: 30px;
}

:deep(.el-steps) {
  background: transparent;
}

/* Upload card */
.upload-card {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  font-weight: 500;
}

.card-step {
  font-size: 12px;
  color: #909399;
  font-weight: normal;
}

/* Form sections */
.import-form {
  padding: 0;
}

.form-section {
  margin-bottom: 24px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 6px;
}

.form-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid #409eff;
  display: inline-block;
}

/* File type hints */
.file-type-hint {
  margin-top: 8px;
  font-size: 13px;
  color: #606266;
  padding: 8px 12px;
  background: #fff;
  border-left: 3px solid #409eff;
  border-radius: 2px;
}

/* Form field hints */
.field-hint {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
  padding: 6px 8px;
  background: #f5f7fa;
  border-radius: 3px;
}

/* Metric radio group */
.metric-radio-group {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

:deep(.metric-radio-group .el-radio) {
  margin-right: 0;
  width: 100%;
}

:deep(.metric-radio-group .el-radio.is-bordered) {
  padding: 12px 16px;
  border-radius: 6px;
  border: 2px solid #dcdfe6;
  transition: all 0.3s ease;
}

:deep(.metric-radio-group .el-radio.is-bordered:hover) {
  border-color: #409eff;
  background: #ecf5ff;
}

:deep(.metric-radio-group .el-radio.is-bordered.is-checked) {
  border-color: #409eff;
  background: #ecf5ff;
}

.radio-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  margin-left: 8px;
}

.radio-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.radio-code {
  font-size: 12px;
  color: #909399;
  background: #f5f7fa;
  padding: 2px 8px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
}

/* Upload wrapper */
.upload-wrapper {
  margin: 0;
}

:deep(.drag-upload) {
  width: 100%;
}

:deep(.el-upload-dragger) {
  width: 100%;
  padding: 40px 20px;
  background: #f5f7fa;
  border: 2px dashed #c0c4cc;
  border-radius: 6px;
  transition: all 0.3s ease;
}

:deep(.el-upload-dragger:hover) {
  border-color: #409eff;
  background: #ecf5ff;
}

.upload-icon {
  font-size: 48px;
  color: #409eff;
  margin-bottom: 12px;
}

.upload-text {
  text-align: center;
}

.upload-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.upload-desc {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* File info box */
.file-info-box {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  border-left: 3px solid #67c23a;
}

.file-info-item {
  display: flex;
  align-items: center;
  font-size: 13px;
  margin: 4px 0;
}

.info-label {
  color: #909399;
  margin-right: 8px;
  min-width: 60px;
}

.info-value {
  color: #303133;
  word-break: break-all;
}

/* Upload button */
.upload-btn {
  width: 100%;
  height: 40px;
  font-size: 15px;
  font-weight: 500;
}

.button-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
  display: block;
}

/* Uploading section */
.uploading-section {
  padding: 20px;
}

.progress-container {
  background: #f5f7fa;
  padding: 30px;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

/* Animated process steps */
.process-steps {
  display: flex;
  justify-content: space-around;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px 0;
}

.process-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  opacity: 0.5;
  transition: all 0.3s ease;
}

.process-step.active {
  opacity: 1;
}

.step-circle {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: #e4e7ed;
  color: #909399;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 16px;
  transition: all 0.3s ease;
}

.process-step.active .step-circle {
  background: #409eff;
  color: white;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.3);
}

.step-label {
  margin-top: 8px;
  font-size: 12px;
  color: #606266;
  text-align: center;
  transition: all 0.3s ease;
}

.process-step.active .step-label {
  color: #303133;
  font-weight: 500;
}

/* Process arrows */
.process-arrow {
  flex: 1;
  height: 2px;
  background: #e4e7ed;
  margin: 0 10px;
  max-width: 60px;
  transition: all 0.3s ease;
}

.process-arrow.active {
  background: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

/* Progress bar */
.progress-bar-container {
  background: white;
  padding: 16px;
  border-radius: 6px;
  border: 1px solid #ebeef5;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.progress-label {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
}

.progress-percent {
  font-size: 18px;
  font-weight: bold;
  color: #409eff;
}

:deep(.el-progress) {
  margin-top: 8px;
}

/* Status container */
.status-container {
  margin-top: 20px;
}

:deep(.el-alert) {
  margin-bottom: 12px;
}

:deep(.el-alert:last-child) {
  margin-bottom: 0;
}

.processing-details {
  line-height: 1.6;
}

.success-details {
  line-height: 1.6;
}

.stat-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.stat-label {
  color: #606266;
  font-size: 13px;
}

.stat-value {
  font-weight: 600;
  color: #303133;
}

.stat-value.success {
  color: #67c23a;
}

.stat-value.error {
  color: #f56c6c;
}

/* Responsive design */
@media (max-width: 1024px) {
  .import-view {
    padding: 16px;
  }

  .page-title {
    font-size: 24px;
  }

  .process-steps {
    flex-wrap: wrap;
    gap: 20px;
  }

  .process-arrow {
    display: none;
  }

  .process-step {
    flex: 0 1 calc(50% - 10px);
  }

  :deep(.el-row) {
    row-gap: 20px;
  }
}

@media (max-width: 768px) {
  .import-view {
    padding: 12px;
  }

  .page-title {
    font-size: 20px;
  }

  .page-header {
    margin-bottom: 20px;
  }

  .form-section {
    padding: 12px;
    margin-bottom: 16px;
  }

  .steps-container {
    margin-bottom: 20px;
  }

  :deep(.el-steps) {
    font-size: 12px;
  }

  .progress-container {
    padding: 16px;
  }

  .upload-icon {
    font-size: 36px;
  }

  :deep(.el-upload-dragger) {
    padding: 30px 15px;
  }

  .process-steps {
    flex-direction: column;
    gap: 16px;
  }

  .step-circle {
    width: 40px;
    height: 40px;
    font-size: 14px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .card-step {
    align-self: flex-end;
  }
}
</style>
