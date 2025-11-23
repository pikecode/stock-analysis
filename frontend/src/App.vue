<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores'

const authStore = useAuthStore()

onMounted(() => {
  authStore.fetchUser()
})
</script>

<template>
  <router-view />
</template>

<style>
html,
body {
  margin: 0;
  padding: 0;
  height: 100%;
}

#app {
  height: 100%;
}
</style>
