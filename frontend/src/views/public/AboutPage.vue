<script setup lang="ts">
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<template>
  <div class="public-page">
    <header class="header">
      <div class="container">
        <div class="logo" @click="router.push('/')">
          <span class="logo-icon">📈</span>
          <span class="logo-text">Stock Analysis</span>
        </div>
        <el-button type="primary" @click="router.push('/login')">登录</el-button>
      </div>
    </header>

    <div class="container main-content">
      <el-card>
        <h1>关于我们</h1>
        <p>Stock Analysis 是一个专业的股票数据分析平台，提供实时股票行情、概念板块分析和专业报表功能。</p>
        <p>我们致力于为投资者提供准确、及时、全面的市场数据和分析工具。</p>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.public-page {
  min-height: 100vh;
  background: #f5f7fa;
}
.header {
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 0 20px;
  margin-bottom: 24px;
}
.header .container {
  max-width: 1200px;
  margin: 0 auto;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.logo {
  display: flex;
  align-items: center;
  font-size: 20px;
  font-weight: bold;
  cursor: pointer;
}
.logo-icon {
  font-size: 28px;
  margin-right: 8px;
}
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}
.main-content {
  padding: 40px 20px;
}
p {
  margin: 16px 0;
  line-height: 1.8;
  color: #606266;
}
</style>
