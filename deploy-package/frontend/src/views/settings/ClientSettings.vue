<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores'

const authStore = useAuthStore()
const loading = ref(false)

const handleLogout = async () => {
  loading.value = true
  try {
    await authStore.logout()
    ElMessage.success('已退出登录')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="settings-container">
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <span class="title">⚙️ 用户设置</span>
        </div>
      </template>

      <!-- 用户信息 -->
      <el-row :gutter="20" class="settings-row">
        <el-col :span="24">
          <h3 class="section-title">个人信息</h3>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="settings-row">
        <el-col :span="12">
          <div class="info-item">
            <span class="label">用户名：</span>
            <span class="value">{{ authStore.user?.username }}</span>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="info-item">
            <span class="label">邮箱：</span>
            <span class="value">{{ authStore.user?.email || '-' }}</span>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="settings-row">
        <el-col :span="12">
          <div class="info-item">
            <span class="label">联系方式：</span>
            <span class="value">{{ authStore.user?.phone || '-' }}</span>
          </div>
        </el-col>
      </el-row>

      <!-- 账户权限 -->
      <el-row :gutter="20" class="settings-row" style="margin-top: 20px">
        <el-col :span="24">
          <h3 class="section-title">账户权限</h3>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="settings-row">
        <el-col :span="24">
          <div class="info-item">
            <span class="label">可用功能：</span>
            <span class="value">
              <el-tag
                v-for="permission in authStore.permissions"
                :key="permission"
                type="success"
                style="margin-right: 8px; margin-bottom: 8px"
              >
                {{ permission }}
              </el-tag>
            </span>
          </div>
        </el-col>
      </el-row>

      <!-- 温馨提示 -->
      <el-row :gutter="20" class="settings-row" style="margin-top: 20px">
        <el-col :span="24">
          <el-alert
            title="温馨提示"
            type="info"
            :closable="false"
          >
            <p style="margin: 0">
              您当前拥有以下权限：股票查询、概念查询、排名查询和报表分析。
              如需获取更多功能，请联系系统管理员。
            </p>
          </el-alert>
        </el-col>
      </el-row>

      <!-- 操作按钮 -->
      <el-row :gutter="20" class="settings-row" style="margin-top: 30px">
        <el-col :span="24">
          <el-button
            type="danger"
            :loading="loading"
            @click="handleLogout"
          >
            退出登录
          </el-button>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<style scoped>
.settings-container {
  padding: 0;
}

.settings-card {
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

.settings-row {
  margin-bottom: 16px;
}

.section-title {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  margin: 20px 0 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e4e7eb;
}

.info-item {
  display: flex;
  align-items: flex-start;
  padding: 8px 0;
}

.label {
  color: #606266;
  margin-right: 12px;
  min-width: 80px;
  flex-shrink: 0;
}

.value {
  color: #303133;
  flex-wrap: wrap;
  display: flex;
}
</style>
