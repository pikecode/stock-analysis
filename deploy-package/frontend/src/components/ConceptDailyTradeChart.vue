<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import VChart from 'vue-echarts'

interface DailySummary {
  trade_date: string
  total_trade_value: number | null
  stock_count: number
}

interface Props {
  conceptId: number
  conceptName: string
  metricCode: string
  startDate: string
  endDate: string
}

const props = defineProps<Props>()

const loading = ref(false)
const dailyData = ref<DailySummary[]>([])
const chartOption = ref({})

const initChart = async () => {
  console.log('ConceptDailyTradeChart initChart 开始执行:', {
    conceptId: props.conceptId,
    conceptName: props.conceptName,
    startDate: props.startDate,
    endDate: props.endDate,
    metricCode: props.metricCode
  })

  loading.value = true
  try {
    const url = `/api/v1/concepts/${props.conceptId}/daily-trade-summary?` +
      `start_date=${props.startDate}&` +
      `end_date=${props.endDate}&` +
      `metric_code=${props.metricCode}`
    console.log('发送 API 请求:', url)

    const response = await fetch(url)

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`)
    }

    const data = await response.json()
    dailyData.value = data.daily_summary || []
    console.log('获取到每日交易总和数据:', dailyData.value.length, '条记录')

    // Generate chart option
    const dates = dailyData.value.map(item => item.trade_date)
    const tradeValues = dailyData.value.map(item => item.total_trade_value)
    const stockCounts = dailyData.value.map(item => item.stock_count)

    chartOption.value = {
      tooltip: {
        trigger: 'axis',
        formatter: (params: any) => {
          if (Array.isArray(params) && params.length > 0) {
            const date = params[0].axisValue
            const tradeValue = params[0].value !== null ? `交易总和: ${formatValue(params[0].value)}` : '交易总和: -'
            const count = params[1].value !== null ? `股票数: ${params[1].value}` : '股票数: -'
            return `${date}<br/>${tradeValue}<br/>${count}`
          }
          return ''
        }
      },
      legend: {
        data: ['每日交易总和', '股票数量'],
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
          name: '交易总和',
          position: 'left',
          axisLabel: {
            formatter: (value: number) => formatValue(value)
          }
        },
        {
          type: 'value',
          name: '股票数',
          position: 'right',
          axisLabel: {
            formatter: (value: number) => Math.round(value)
          }
        }
      ],
      series: [
        {
          name: '每日交易总和',
          data: tradeValues,
          type: 'line',
          smooth: true,
          yAxisIndex: 0,
          itemStyle: {
            color: '#67C26A'
          },
          areaStyle: {
            color: 'rgba(103, 194, 106, 0.2)'
          }
        },
        {
          name: '股票数量',
          data: stockCounts,
          type: 'bar',
          yAxisIndex: 1,
          itemStyle: {
            color: '#E6A23C'
          }
        }
      ]
    }
  } catch (error) {
    ElMessage.error(`加载概念每日交易总和失败: ${error}`)
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
  console.log('ConceptDailyTradeChart 组件已挂载:', {
    conceptId: props.conceptId,
    conceptName: props.conceptName,
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
    console.log('ConceptDailyTradeChart props 日期变化检测到:', {
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
  <div class="concept-daily-trade-chart">
    <div class="chart-title">
      <h4>{{ conceptName }} - 每日交易总和趋势</h4>
      <span v-if="loading" class="loading-indicator">加载中...</span>
    </div>
    <div v-if="!loading" class="chart-wrapper">
      <VChart
        :option="chartOption"
        autoresize
        style="height: 350px; width: 100%"
      />
    </div>
    <div v-else class="loading-placeholder">
      <p>正在加载图表数据...</p>
    </div>
  </div>
</template>

<style scoped>
.concept-daily-trade-chart {
  width: 100%;
}

.chart-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.chart-title h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.loading-indicator {
  font-size: 12px;
  color: #909399;
}

.chart-wrapper {
  background: #fafafa;
  border-radius: 4px;
  padding: 8px;
}

.loading-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 350px;
  background: #f9fafc;
  border-radius: 4px;
  color: #909399;
}
</style>
