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
  yField: {
    type: String,
    default: 'balance'
  },
  name: {
    type: String,
    default: '结余'
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
  
  const xData = props.data.map(item => {
    if (typeof item[props.xField] === 'number') {
      return `${item.year}-${String(item[props.xField]).padStart(2, '0')}`
    }
    return item[props.xField]
  })
  
  const yData = props.data.map(item => item[props.yField] || 0)
  
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
      formatter: function(params) {
        const data = params[0]
        return `${data.name}<br/>${data.marker} ${data.seriesName}: ¥${data.value.toFixed(2)}`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: xData,
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
        name: props.name,
        type: 'line',
        data: yData,
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: {
          width: 3
        },
        itemStyle: {
          color: function(params) {
            return params.value >= 0 ? '#67c23a' : '#f56c6c'
          }
        },
        areaStyle: {
          color: function(params) {
            const color = new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: params.value >= 0 ? 'rgba(103, 194, 58, 0.3)' : 'rgba(245, 108, 108, 0.3)' },
              { offset: 1, color: params.value >= 0 ? 'rgba(103, 194, 58, 0.05)' : 'rgba(245, 108, 108, 0.05)' }
            ])
            return color
          }
        }
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
