import { defineStore } from 'pinia'
import { ref } from 'vue'
import { stockApi, conceptApi, importApi } from '@/api'
import type { Stock, Concept, MetricType } from '@/types'

export const useStockStore = defineStore('stock', () => {
  const stocks = ref<Stock[]>([])
  const stocksTotal = ref(0)
  const concepts = ref<Concept[]>([])
  const conceptsTotal = ref(0)
  const metrics = ref<MetricType[]>([])
  const loading = ref(false)

  async function fetchStocks(params: {
    keyword?: string
    exchange?: string
    page?: number
    page_size?: number
  }) {
    loading.value = true
    try {
      const res = await stockApi.getList(params)
      stocks.value = res.items
      stocksTotal.value = res.total
    } finally {
      loading.value = false
    }
  }

  async function fetchConcepts(params: {
    keyword?: string
    category?: string
    page?: number
    page_size?: number
  }) {
    loading.value = true
    try {
      const res = await conceptApi.getList(params)
      concepts.value = res.items
      conceptsTotal.value = res.total
    } finally {
      loading.value = false
    }
  }

  async function fetchMetrics() {
    if (metrics.value.length > 0) return
    try {
      metrics.value = await importApi.getMetrics()
    } catch {
      metrics.value = []
    }
  }

  return {
    stocks,
    stocksTotal,
    concepts,
    conceptsTotal,
    metrics,
    loading,
    fetchStocks,
    fetchConcepts,
    fetchMetrics,
  }
})
