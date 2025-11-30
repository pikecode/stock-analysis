<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores'
import { ElMessage } from 'element-plus'
import { Lock, User } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

onMounted(() => {
  // Component mounted
})

const form = ref({
  username: '',
  password: '',
})

const loading = ref(false)

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  loading.value = true

  try {
    const success = await authStore.login(form.value, 'admin')

    if (!success) {
      ElMessage.error('用户名或密码错误')
      return
    }

    if (authStore.adminUser?.role !== 'ADMIN') {
      ElMessage.error(`此页面仅限管理员访问。您的角色为: ${authStore.adminUser?.role || '未知'}`)
      await authStore.logout('admin')
      form.value.username = ''
      form.value.password = ''
      return
    }

    ElMessage.success('登录成功')
    const redirect = (route.query.redirect as string) || '/admin'
    router.push(redirect)
  } catch (error: any) {
    ElMessage.error('登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="admin-login">
    <div class="login-container">
      <div class="login-box">
        <div class="login-header">
          <div class="logo">
            <span class="logo-icon">🔐</span>
            <h1>管理员登录</h1>
          </div>
          <p class="subtitle">Stock Analysis 管理后台</p>
        </div>

        <el-form class="login-form" @submit.prevent="handleLogin">
          <el-form-item>
            <el-input
              v-model="form.username"
              size="large"
              placeholder="管理员用户名"
              :prefix-icon="User"
              @keyup.enter="handleLogin"
            />
          </el-form-item>

          <el-form-item>
            <el-input
              v-model="form.password"
              type="password"
              size="large"
              placeholder="管理员密码"
              :prefix-icon="Lock"
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="loading"
              style="width: 100%"
              @click="handleLogin"
            >
              登 录
            </el-button>
          </el-form-item>
        </el-form>

        <div class="login-footer">
          <el-link type="info" @click="router.push('/')">← 返回首页</el-link>
          <el-link type="info" @click="router.push('/login')">客户登录</el-link>
        </div>

        <el-alert type="warning" :closable="false" style="margin-top: 20px">
          <template #title>
            <div style="font-size: 12px;">
              此页面仅限管理员访问。如果您是普通用户，请使用
              <el-link type="primary" @click="router.push('/login')">客户登录</el-link>
              页面。
            </div>
          </template>
        </el-alert>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-login {
  min-height: 100vh;
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-container {
  width: 100%;
  max-width: 450px;
}

.login-box {
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.logo-icon {
  font-size: 36px;
}

.login-header h1 {
  font-size: 28px;
  color: #2c3e50;
  margin: 0;
}

.subtitle {
  color: #95a5a6;
  margin-top: 8px;
  font-size: 14px;
}

.login-form {
  margin-top: 32px;
}

.login-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #ecf0f1;
}
</style>