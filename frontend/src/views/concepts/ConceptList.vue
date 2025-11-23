<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { conceptApi } from '@/api'
import type { Concept } from '@/types'
import { Search } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)
const concepts = ref<Concept[]>([])
const total = ref(0)

const searchParams = ref({
  keyword: '',
  category: '',
  page: 1,
  page_size: 20,
})

const fetchData = async () => {
  loading.value = true
  try {
    const res = await conceptApi.getList(searchParams.value)
    concepts.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  searchParams.value.page = 1
  fetchData()
}

const handlePageChange = (page: number) => {
  searchParams.value.page = page
  fetchData()
}

const handleSizeChange = (size: number) => {
  searchParams.value.page_size = size
  searchParams.value.page = 1
  fetchData()
}

const goToDetail = (id: number) => {
  router.push(`/concepts/${id}`)
}

onMounted(fetchData)
</script>

<template>
  <div class="concept-list">
    <div class="page-header">
      <h1 class="page-title">概念列表</h1>
    </div>

    <el-card>
      <div class="search-form">
        <el-input
          v-model="searchParams.keyword"
          placeholder="搜索概念名称"
          :prefix-icon="Search"
          clearable
          style="width: 240px"
          @keyup.enter="handleSearch"
        />
        <el-input
          v-model="searchParams.category"
          placeholder="分类"
          clearable
          style="width: 150px"
        />
        <el-button type="primary" @click="handleSearch">搜索</el-button>
      </div>

      <el-table :data="concepts" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="concept_name" label="概念名称">
          <template #default="{ row }">
            <el-link type="primary" @click="goToDetail(row.id)">
              {{ row.concept_name }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="150">
          <template #default="{ row }">
            <el-tag v-if="row.category" type="info">{{ row.category }}</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ row.created_at?.slice(0, 19).replace('T', ' ') }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button type="primary" link @click="goToDetail(row.id)"> 详情 </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="searchParams.page"
          v-model:page-size="searchParams.page_size"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>
  </div>
</template>
