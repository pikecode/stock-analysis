<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { importApi } from '@/api'
import type { MetricType } from '@/types'
import { Upload } from '@element-plus/icons-vue'
import type { UploadFile, UploadFiles } from 'element-plus'

const loading = ref(false)
const metrics = ref<MetricType[]>([])

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
  try {
    const data = new FormData()
    data.append('file', file.raw)
    data.append('file_type', formData.value.file_type)
    if (formData.value.metric_code) {
      data.append('metric_code', formData.value.metric_code)
    }

    const res = await importApi.upload(data)
    ElMessage.success(res.message || '上传成功')
    fileList.value = []
    formData.value.metric_code = ''
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '上传失败')
  } finally {
    loading.value = false
  }
}

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
              <el-button type="primary" @click="handleUpload" :loading="loading">
                开始上传
              </el-button>
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
</style>
