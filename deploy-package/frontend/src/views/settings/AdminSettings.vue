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
          <span class="title">⚙️ 系统设置</span>
        </div>
      </template>

      <!-- 用户信息 -->
      <el-row :gutter="20" class="settings-row">
        <el-col :span="24">
          <h3 class="section-title">用户信息</h3>
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
            <span class="label">角色：</span>
            <span class="value">
              <el-tag
                v-for="role in authStore.roles"
                :key="role"
                type="success"
                style="margin-right: 8px"
              >
                {{ role }}
              </el-tag>
            </span>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="info-item">
            <span class="label">权限数：</span>
            <span class="value">{{ authStore.permissions.length }}</span>
          </div>
        </el-col>
      </el-row>

      <!-- 权限列表 -->
      <el-row :gutter="20" class="settings-row" style="margin-top: 20px">
        <el-col :span="24">
          <h3 class="section-title">权限列表</h3>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="settings-row">
        <el-col :span="24">
          <div class="permission-list">
            <el-tag
              v-for="permission in authStore.permissions"
              :key="permission"
              type="info"
              style="margin-right: 8px; margin-bottom: 8px"
            >
              {{ permission }}
            </el-tag>
          </div>
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
  align-items: center;
  padding: 8px 0;
}

.label {
  color: #606266;
  margin-right: 12px;
  min-width: 80px;
}

.value {
  color: #303133;
}

.permission-list {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
}
</style>
