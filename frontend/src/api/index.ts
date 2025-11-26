import request from './request'
import type {
  LoginRequest,
  Token,
  User,
  Stock,
  StockWithConcepts,
  Concept,
  ConceptRanking,
  TopNCountItem,
  DailySummary,
  ImportBatch,
  MetricType,
  PaginatedResponse,
} from '@/types'

// Auth API
export const authApi = {
  login(data: LoginRequest) {
    return request.post<any, Token>('/auth/login', data)
  },
  refresh(refreshToken: string) {
    return request.post<any, Token>('/auth/refresh', { refresh_token: refreshToken })
  },
  logout() {
    return request.post('/auth/logout')
  },
  getMe() {
    return request.get<any, User>('/auth/me')
  },
}

// Stock API
export const stockApi = {
  getList(params: { keyword?: string; exchange?: string; page?: number; page_size?: number }) {
    return request.get<any, PaginatedResponse<Stock>>('/stocks', { params })
  },
  getDetail(stockCode: string) {
    return request.get<any, StockWithConcepts>(`/stocks/${stockCode}`)
  },
  getConcepts(stockCode: string) {
    return request.get<any, { stock_code: string; stock_name: string; concepts: any[] }>(
      `/stocks/${stockCode}/concepts`
    )
  },
}

// Concept API
export const conceptApi = {
  getList(params: { keyword?: string; category?: string; page?: number; page_size?: number }) {
    return request.get<any, PaginatedResponse<Concept>>('/concepts', { params })
  },
  getDetail(conceptId: number) {
    return request.get<any, Concept>(`/concepts/${conceptId}`)
  },
  getStocks(conceptId: number, params: { page?: number; page_size?: number }) {
    return request.get<any, any>(`/concepts/${conceptId}/stocks`, { params })
  },
}

// Ranking API
export const rankingApi = {
  getConceptRanking(
    conceptId: number,
    params: { trade_date: string; metric_code?: string; limit?: number }
  ) {
    return request.get<any, ConceptRanking>(`/rankings/concept/${conceptId}`, { params })
  },
  getStockHistory(
    stockCode: string,
    params: { concept_id: number; start_date: string; end_date: string; metric_code?: string }
  ) {
    return request.get<any, any>(`/rankings/stock/${stockCode}`, { params })
  },
  getTopNCount(
    stockCode: string,
    params: {
      start_date: string
      end_date: string
      top_n?: number
      concept_id?: number
      metric_code?: string
    }
  ) {
    return request.get<any, { statistics: TopNCountItem[] }>(
      `/rankings/stock/${stockCode}/top-n-count`,
      { params }
    )
  },
}

// Summary API
export const summaryApi = {
  getConceptSummary(
    conceptId: number,
    params: { start_date: string; end_date: string; metric_code?: string }
  ) {
    return request.get<any, { summaries: DailySummary[] }>(`/summaries/concept/${conceptId}`, {
      params,
    })
  },
  compareMetrics(conceptId: number, params: { trade_date: string; metric_codes?: string }) {
    return request.get<any, any>(`/summaries/concept/${conceptId}/compare`, { params })
  },
}

// Import API
export const importApi = {
  upload(formData: FormData) {
    return request.post<any, { batch_id: number; status: string; message: string }>(
      '/import/upload',
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    )
  },
  getBatches(params: { status?: string; page?: number; page_size?: number }) {
    return request.get<any, ImportBatch[]>('/import/batches', { params })
  },
  getBatch(batchId: number) {
    return request.get<any, ImportBatch>(`/import/batches/${batchId}`)
  },
  recompute(batchId: number) {
    return request.post<any, any>(`/import/batches/${batchId}/recompute`)
  },
  getMetrics() {
    return request.get<any, MetricType[]>('/import/metrics')
  },
}

// Report API
export const reportApi = {
  // Get stocks ranked in a concept within date range
  getConceptStocksInRange(
    conceptId: number,
    params: {
      start_date: string
      end_date: string
      metric_code?: string
      limit?: number
      use_latest_date?: boolean
    }
  ) {
    return request.get<any, any>(`/rankings/concept/${conceptId}/stocks-in-range`, { params })
  },

  // Get stock concepts ranked by value
  getStockConceptsRanked(
    stockCode: string,
    params: { trade_date: string; metric_code?: string }
  ) {
    return request.get<any, any>(`/stocks/${stockCode}/concepts-ranked`, { params })
  },

  // Get stock ranking history in a concept
  getStockRankingHistory(
    stockCode: string,
    params: {
      concept_id: number
      start_date: string
      end_date: string
      metric_code?: string
    }
  ) {
    return request.get<any, any>(`/rankings/stock/${stockCode}`, { params })
  },

  // Get times stock appeared in top N
  getTopNCount(
    stockCode: string,
    params: {
      start_date: string
      end_date: string
      top_n?: number
      concept_id?: number
      metric_code?: string
    }
  ) {
    return request.get<any, any>(`/rankings/stock/${stockCode}/top-n-count`, { params })
  },
}
