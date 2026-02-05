<template>
  <div ref="chartRef" :style="{ width, height }"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: {
    type: Array,
    required: true,
    default: () => []
  },
  width: {
    type: String,
    default: '100%'
  },
  height: {
    type: String,
    default: '300px'
  },
  title: {
    type: String,
    default: ''
  },
  xField: {
    type: String,
    default: 'month'
  },
  incomeKey: {
    type: String,
    default: 'total_income'
  },
  expenseKey: {
    type: String,
    default: 'total_expense'
  }
})

const chartRef = ref(null)
let chart = null

function initChart() {
  if (!chartRef.value) return
  
  chart = echarts.init(chartRef.value)
  updateChart()
}

function updateChart() {
  if (!chart || !props.data.length) return
  
  const months = props.data.map(item => {
    if (typeof item[props.xField] === 'number') {
      return `${item.year}-${String(item[props.xField]).padStart(2, '0')}`
    }
    return item[props.xField]
  })
  
  const incomeData = props.data.map(item => item[props.incomeKey] || 0)
  const expenseData = props.data.map(item => item[props.expenseKey] || 0)
  
  const option = {
    title: {
      text: props.title,
      left: 'center',
      textStyle: {
        fontSize: 14,
        fontWeight: 'normal'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function(params) {
        let result = params[0].name + '<br/>'
        params.forEach(param => {
          result += `${param.marker} ${param.seriesName}: ¥${param.value.toFixed(2)}<br/>`
        })
        return result
      }
    },
    legend: {
      data: ['收入', '支出'],
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: months,
      axisLabel: {
        interval: 0,
        rotate: 30
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '¥{value}'
      }
    },
    series: [
      {
        name: '收入',
        type: 'bar',
        data: incomeData,
        itemStyle: {
          color: '#67c23a'
        },
        barWidth: '30%'
      },
      {
        name: '支出',
        type: 'bar',
        data: expenseData,
        itemStyle: {
          color: '#f56c6c'
        },
        barWidth: '30%'
      }
    ]
  }
  
  chart.setOption(option)
}

function handleResize() {
  chart?.resize()
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
})

watch(() => props.data, updateChart, { deep: true })
</script>
