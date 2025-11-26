<script setup lang="ts">
import { useAuthStore } from '@/stores'
const authStore = useAuthStore()
</script>

<template>
  <div class="user-profile">
    <h1>个人中心</h1>
    <el-card>
      <el-descriptions title="用户信息" :column="2">
        <el-descriptions-item label="用户名">
          {{ authStore.user?.username || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="邮箱">
          {{ authStore.user?.email || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="角色">
          {{ authStore.user?.role || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag type="success">激活</el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<style scoped>
.user-profile {
  padding: 20px;
}
h1 {
  margin-bottom: 24px;
}
</style>
