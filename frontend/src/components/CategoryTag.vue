<template>
  <el-tag 
    :type="tagType" 
    :size="size" 
    :effect="effect"
    round
  >
    <slot>{{ name }}</slot>
  </el-tag>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  name: {
    type: String,
    required: true
  },
  type: {
    type: String,
    default: 'expense' // 'income' | 'expense'
  },
  size: {
    type: String,
    default: 'default' // 'large' | 'default' | 'small'
  },
  effect: {
    type: String,
    default: 'light' // 'dark' | 'light' | 'plain'
  }
})

const tagType = computed(() => {
  if (props.type === 'income') {
    return 'success'
  }
  
  // 根据分类名称返回对应颜色
  const colorMap = {
    餐饮: 'warning',
    交通: 'primary',
    娱乐: 'info',
    购物: 'danger',
    居住: '',
    医疗: 'danger',
    教育: '',
    人情: 'warning',
    工资: 'success',
    奖金: 'success',
    投资: 'success',
    其他: 'info'
  }
  
  return colorMap[props.name] || 'info'
})
</script>
