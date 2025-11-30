<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores'
import type { FormInstance, FormRules } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const formRef = ref<FormInstance>()
const loading = ref(false)

onMounted(() => {
  // Component mounted
})

const form = reactive({
  username: '',
  password: '',
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const handleLogin = async () => {
  if (!form.username) {
    ElMessage.warning('请输入用户名')
    return
  }
  if (!form.password) {
    ElMessage.warning('请输入密码')
    return
  }

  loading.value = true

  try {
    const success = await authStore.login(form, 'client')

    if (success) {
      if (authStore.clientUser?.role === 'ADMIN') {
        ElMessage.error('管理员用户请使用管理员登录页面')
        await authStore.logout('client')
        form.username = ''
        form.password = ''
        return
      }

      ElMessage.success('登录成功')
      await new Promise(resolve => setTimeout(resolve, 100))
      const redirect = (route.query.redirect as string) || '/'
      router.push(redirect)
    }
    // Error message is already shown by API interceptor
  } catch (error: any) {
    // Unexpected errors not handled by interceptor
    if (error?.response?.status !== 401 && error?.response?.status !== 400) {
      ElMessage.error('登录失败: ' + (error?.message || '请稍后重试'))
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-container">
    <div class="login-box">
      <h2 class="login-title">Stock Analysis</h2>
      <p class="login-subtitle">股票概念分析系统</p>

      <el-form ref="formRef" :model="form" :rules="rules">
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            :prefix-icon="User"
            size="large"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            :prefix-icon="Lock"
            size="large"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            size="large"
            class="login-btn"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
  width: 400px;
  padding: 40px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.login-title {
  text-align: center;
  margin: 0 0 8px;
  font-size: 28px;
  color: #333;
}

.login-subtitle {
  text-align: center;
  margin: 0 0 30px;
  color: #909399;
}

.login-btn {
  width: 100%;
}
</style>
