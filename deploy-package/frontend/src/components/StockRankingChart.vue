<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import VChart from 'vue-echarts'

interface RankingData {
  trade_date: string
  rank: number | null
  trade_value: number | null
}

interface Props {
  conceptId: number
  conceptName: string
  stockCode: string
  stockName: string
  metricCode: string
  startDate: string
  endDate: string
}

const props = defineProps<Props>()

const loading = ref(false)
const rankingData = ref<RankingData[]>([])
const chartOption = ref({})

const chartKey = computed(() => `chart-${props.conceptId}-${props.stockCode}`)

const initChart = async () => {
  console.log('initChart 开始执行:', {
    conceptId: props.conceptId,
    stockCode: props.stockCode,
    startDate: props.startDate,
    endDate: props.endDate,
    metricCode: props.metricCode
  })

  loading.value = true
  try {
    const url = `/api/v1/concepts/${props.conceptId}/stock-rank-history?` +
      `stock_code=${props.stockCode}&` +
      `start_date=${props.startDate}&` +
      `end_date=${props.endDate}&` +
      `metric_code=${props.metricCode}`
    console.log('发送 API 请求:', url)

    const response = await fetch(url)

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`)
    }

    const data = await response.json()
    rankingData.value = data.history || []

    // Generate chart option
    const dates = rankingData.value.map(item => item.trade_date)
    const ranks = rankingData.value.map(item => item.rank)
    const tradeValues = rankingData.value.map(item => item.trade_value)

    chartOption.value = {
      tooltip: {
        trigger: 'axis',
        formatter: (params: any) => {
          if (Array.isArray(params) && params.length > 0) {
            const date = params[0].axisValue
            const rank = params[0].value !== null ? `排名: ${params[0].value}` : '排名: -'
            const value = params[1].value !== null ? `交易量: ${formatValue(params[1].value)}` : '交易量: -'
            return `${date}<br/>${rank}<br/>${value}`
          }
          return ''
        }
      },
      legend: {
        data: ['排名', '交易量'],
        top: 30
      },
      grid: {
        left: '10%',
        right: '10%',
        top: '15%',
        bottom: '15%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: dates,
        boundaryGap: false
      },
      yAxis: [
        {
          type: 'value',
          name: '排名',
          position: 'left',
          inverse: true,
          axisLabel: {
            formatter: (value: number) => Math.round(value)
          }
        },
        {
          type: 'value',
          name: '交易量',
          position: 'right',
          axisLabel: {
            formatter: (value: number) => formatValue(value)
          }
        }
      ],
      series: [
        {
          name: '排名',
          data: ranks,
          type: 'line',
          smooth: true,
          yAxisIndex: 0,
          itemStyle: {
            color: '#409EFF'
          },
          areaStyle: {
            color: 'rgba(64, 158, 255, 0.2)'
          }
        },
        {
          name: '交易量',
          data: tradeValues,
          type: 'line',
          smooth: true,
          yAxisIndex: 1,
          itemStyle: {
            color: '#67C26A'
          },
          areaStyle: {
            color: 'rgba(103, 194, 106, 0.2)'
          }
        }
      ]
    }
  } catch (error) {
    ElMessage.error(`加载排名数据失败: ${error}`)
    console.error(error)
  } finally {
    loading.value = false
  }
}

const formatValue = (value: number | null): string => {
  if (value === null || value === undefined) return '-'
  if (value >= 100000000) {
    return (value / 100000000).toFixed(2) + '亿'
  } else if (value >= 10000) {
    return (value / 10000).toFixed(2) + '万'
  }
  return value.toFixed(0)
}

onMounted(() => {
  console.log('StockRankingChart 组件已挂载:', {
    conceptId: props.conceptId,
    stockCode: props.stockCode,
    startDate: props.startDate,
    endDate: props.endDate,
    metricCode: props.metricCode
  })
  initChart()
})

// 监听日期范围变化，自动重新加载数据
watch(
  () => [props.startDate, props.endDate],
  (newVal, oldVal) => {
    console.log('StockRankingChart props 日期变化检测到:', {
      oldVal,
      newVal,
      startDate: props.startDate,
      endDate: props.endDate
    })
    initChart()
  },
  { deep: false }
)
</script>

<template>
  <div class="stock-ranking-chart">
    <div class="chart-title">
      {{ stockName }}({{ stockCode }}) 在 {{ conceptName }} 中的排名趋势
    </div>
    <el-skeleton :loading="loading" animated>
      <VChart :key="chartKey" :option="chartOption" style="width: 100%; height: 400px" />
    </el-skeleton>
  </div>
</template>

<style scoped>
.stock-ranking-chart {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-top: 20px;
}
</style>
