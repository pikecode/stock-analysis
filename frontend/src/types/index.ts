// User types
export interface User {
  id: number
  username: string
  email: string
  phone?: string
  avatar_url?: string
  status: string
  role: 'admin' | 'vip' | 'normal'
}

export interface LoginRequest {
  username: string
  password: string
}

export interface Token {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

// Stock types
export interface Stock {
  id: number
  stock_code: string
  stock_name?: string
  exchange_prefix?: string
  exchange_name?: string
  created_at: string
}

export interface StockWithConcepts extends Stock {
  concepts: ConceptBrief[]
}

// Concept types
export interface Concept {
  id: number
  concept_name: string
  category?: string
  description?: string
  created_at: string
}

export interface ConceptBrief {
  id: number
  concept_name: string
  category?: string
}

// Ranking types
export interface RankingItem {
  rank: number
  stock_code: string
  stock_name?: string
  trade_value: number
}

export interface ConceptRanking {
  concept_id: number
  concept_name: string
  trade_date: string
  metric_code: string
  rankings: RankingItem[]
}

export interface StockRankingHistory {
  trade_date: string
  rank: number
  trade_value: number
}

export interface TopNCountItem {
  concept_id: number
  concept_name: string
  top_n_count: number
  top_n_rate: number
}

// Summary types
export interface DailySummary {
  trade_date: string
  total_value: number
  avg_value: number
  max_value: number
  min_value: number
  median_value?: number
  top10_sum?: number
}

// Import types
export interface ImportBatch {
  id: number
  file_name: string
  file_type: string
  metric_code?: string
  data_date?: string
  status: string
  compute_status: string
  total_rows: number
  success_rows: number
  error_rows: number
  started_at?: string
  completed_at?: string
  created_at: string
}

export interface MetricType {
  id: number
  code: string
  name: string
  file_pattern?: string
}

// Common types
export interface PaginatedResponse<T> {
  total: number
  items: T[]
}

export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}
