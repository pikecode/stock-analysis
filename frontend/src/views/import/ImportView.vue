<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
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
let pollInterval: ReturnType<typeof setInterval> | null = null

const formData = ref({
  file_type: 'TXT',
  metric_code: '',
})

const fileList = ref<UploadFile[]>([])

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
      <h1 class="page-title">数据导入</h1>
    </div>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card header="上传文件">
          <el-form label-width="100px">
            <el-form-item label="文件类型">
              <el-radio-group v-model="formData.file_type">
                <el-radio value="CSV">CSV (股票-概念关系)</el-radio>
                <el-radio value="TXT">TXT (指标数据)</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="指标类型" v-if="formData.file_type === 'TXT'">
              <el-select v-model="formData.metric_code" placeholder="选择指标" style="width: 100%">
                <el-option
                  v-for="m in metrics"
                  :key="m.code"
                  :label="`${m.name} (${m.code})`"
                  :value="m.code"
                />
              </el-select>
              <div style="font-size: 12px; color: #999; margin-top: 4px;">
                数据日期将从文件名自动解析（如: TTV_20240101.txt）
              </div>
            </el-form-item>

            <el-form-item label="选择文件">
              <el-upload
                drag
                :auto-upload="false"
                :file-list="fileList"
                :on-change="handleFileChange"
                :limit="1"
                accept=".csv,.txt"
              >
                <el-icon class="el-icon--upload"><Upload /></el-icon>
                <div class="el-upload__text">
                  拖拽文件到此处，或 <em>点击上传</em>
                </div>
                <template #tip>
                  <div class="el-upload__tip">
                    支持 CSV 和 TXT 格式文件
                  </div>
                </template>
              </el-upload>
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                @click="handleUpload"
                :loading="loading"
                :disabled="uploading"
              >
                {{ uploading ? '处理中...' : '开始上传' }}
              </el-button>
            </el-form-item>

            <!-- Upload Progress Section -->
            <el-form-item v-if="uploading">
              <div class="progress-section">
                <div class="progress-header">
                  <span class="progress-title">处理进度</span>
                  <span class="progress-percent">{{ uploadProgress }}%</span>
                </div>
                <el-progress :percentage="uploadProgress" />

                <!-- Status Display -->
                <div v-if="currentBatch" class="status-info">
                  <el-alert
                    v-if="currentBatch.status === 'pending'"
                    title="等待处理"
                    type="info"
                    :closable="false"
                    description="文件已上传，等待服务器处理..."
                  />
                  <el-alert
                    v-else-if="currentBatch.status === 'processing'"
                    title="处理中"
                    type="warning"
                    :closable="false"
                  >
                    <template #description>
                      <div v-if="currentBatch.file_type === 'CSV'">
                        正在导入股票-概念关系数据...
                      </div>
                      <div v-else>
                        <div>正在导入指标数据...</div>
                        <div v-if="currentBatch.compute_status === 'pending'" style="margin-top: 4px;">
                          计算状态: <el-tag type="info">等待计算</el-tag>
                        </div>
                        <div v-else-if="currentBatch.compute_status === 'computing'" style="margin-top: 4px;">
                          计算状态: <el-tag type="warning">计算中</el-tag>
                        </div>
                      </div>
                    </template>
                  </el-alert>
                  <el-alert
                    v-else-if="currentBatch.status === 'completed' || currentBatch.status === 'success'"
                    title="导入成功"
                    type="success"
                    :closable="false"
                  >
                    <template #description>
                      <div>成功: {{ currentBatch.success_rows }} / 失败: {{ currentBatch.error_rows }} / 总计: {{ currentBatch.total_rows }}</div>
                      <div v-if="currentBatch.file_type === 'TXT'" style="margin-top: 4px;">
                        排名计算: <el-tag type="success">已完成</el-tag>
                      </div>
                    </template>
                  </el-alert>
                  <el-alert
                    v-else-if="currentBatch.status === 'failed'"
                    title="导入失败"
                    type="error"
                    :closable="false"
                    :description="currentBatch.error_message || '未知错误'"
                  />
                </div>
              </div>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card header="文件格式说明">
          <el-collapse>
            <el-collapse-item title="CSV 格式 (股票-概念关系)" name="csv">
              <div class="format-desc">
                <p>用于导入股票与概念的关联关系</p>
                <pre>股票代码,股票名称,概念
000001,平安银行,银行;金融科技
600000,浦发银行,银行</pre>
              </div>
            </el-collapse-item>
            <el-collapse-item title="TXT 格式 (指标数据)" name="txt">
              <div class="format-desc">
                <p>用于导入每日指标数据，文件名需包含日期</p>
                <p>例如: TTV_20240101.txt</p>
                <pre>SH600000	1234567.89
SZ000001	987654.32
BJ430047	12345.67</pre>
                <p>格式: 股票代码(带前缀)[Tab]指标值</p>
              </div>
            </el-collapse-item>
          </el-collapse>
        </el-card>

        <el-card header="指标类型" style="margin-top: 20px">
          <el-table :data="metrics" stripe>
            <el-table-column prop="code" label="代码" width="100" />
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="file_pattern" label="文件匹配" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.format-desc {
  font-size: 13px;
  color: #606266;
}

.format-desc pre {
  background: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}

.progress-section {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  border: 1px solid #ebeef5;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.progress-title {
  font-weight: 500;
  color: #303133;
}

.progress-percent {
  font-size: 18px;
  font-weight: bold;
  color: #409eff;
}

.status-info {
  margin-top: 12px;
}

.status-info :deep(.el-alert) {
  margin-bottom: 8px;
}

.status-info :deep(.el-alert:last-child) {
  margin-bottom: 0;
}
</style>
