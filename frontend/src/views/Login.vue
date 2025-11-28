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

// 页面加载时输出调试信息
onMounted(() => {
  console.clear()
  console.log('%c✅ Login 页面已加载', 'color: green; font-size: 14px; font-weight: bold;')
  console.log('当前路由:', route.path)
  console.log('authStore 已初始化')
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
  console.log('🔵 handleLogin 被调用了!')

  // 最基础的检查
  if (!form.username) {
    console.warn('❌ 用户名为空')
    ElMessage.warning('请输入用户名')
    return
  }
  if (!form.password) {
    console.warn('❌ 密码为空')
    ElMessage.warning('请输入密码')
    return
  }

  console.log('✓ 表单数据有效:', { username: form.username })

  loading.value = true

  try {
    console.log('➡️ 开始调用 authStore.login()...')
    const success = await authStore.login(form)
    console.log('⬅️ authStore.login() 返回:', success)

    if (success) {
      console.log('✅ 登录成功！')
      ElMessage.success('登录成功')

      // 重定向
      const redirect = authStore.isAdmin ? '/admin' : authStore.isCustomer ? '/reports' : '/'
      console.log('📍 重定向到:', redirect)
      router.push(redirect)
    } else {
      console.log('❌ 登录失败')
      ElMessage.error('用户名或密码错误')
    }
  } catch (error: any) {
    console.error('💥 异常:', error)
    ElMessage.error('登录失败: ' + (error?.message || '请稍后重试'))
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

      <div style="border: 1px solid #ccc; padding: 10px; margin-bottom: 20px; border-radius: 4px; background: #f5f7fa;">
        <p style="font-size: 12px; color: #666; margin: 0 0 8px;">
          📝 测试凭证：
        </p>
        <p style="font-size: 12px; color: #666; margin: 0 0 4px;">
          • 用户名: <code>admin</code>  密码: <code>Admin@123</code>
        </p>
        <p style="font-size: 12px; color: #666; margin: 0;">
          • 用户名: <code>customer</code>  密码: <code>customer123</code>
        </p>
      </div>

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

      <div style="margin-top: 15px; padding: 10px; background: #f0f9ff; border: 1px solid #b3d8ff; border-radius: 4px;">
        <p style="font-size: 11px; color: #0066cc; margin: 0;">
          💡 打开浏览器开发者工具（F12）→ Console 标签，可以看到登录过程的详细日志
        </p>
      </div>
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
