<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <div class="not-found">
    <h1>404</h1>
    <p>页面不存在</p>
    <el-button type="primary" @click="router.push('/')">返回首页</el-button>
  </div>
</template>

<style scoped>
.not-found {
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.not-found h1 {
  font-size: 100px;
  color: #909399;
  margin: 0;
}

.not-found p {
  font-size: 20px;
  color: #606266;
  margin: 20px 0;
}
</style>
