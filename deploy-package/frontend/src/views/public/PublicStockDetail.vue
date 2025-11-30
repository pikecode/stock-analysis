<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const stockCode = route.params.code
</script>

<template>
  <div class="public-page">
    <header class="header">
      <div class="container">
        <div class="logo" @click="router.push('/')">
          <span class="logo-icon">📈</span>
          <span class="logo-text">Stock Analysis</span>
        </div>
        <el-button type="primary" @click="router.push('/login')">登录查看更多</el-button>
      </div>
    </header>

    <div class="container main-content">
      <el-card>
        <h1>股票详情 - {{ stockCode }}</h1>
        <el-alert type="info" :closable="false">
          公开页面展示基础信息，登录后可查看完整数据和分析报表
        </el-alert>
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
</style>