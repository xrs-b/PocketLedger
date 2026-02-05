<template>
  <div class="empty-state">
    <el-empty :image="image" :description="description">
      <template v-if="$slots.image">
        <slot name="image" />
      </template>
      
      <template v-if="$slots.default">
        <slot />
      </template>
      
      <template v-if="$slots.footer">
        <slot name="footer" />
      </template>
      
      <el-button v-if="showAction" type="primary" @click="$emit('action')">
        {{ actionText }}
      </el-button>
    </el-empty>
  </div>
</template>

<script setup>
defineProps({
  image: {
    type: String,
    default: ''
  },
  description: {
    type: String,
    default: '暂无数据'
  },
  showAction: {
    type: Boolean,
    default: false
  },
  actionText: {
    type: String,
    default: '去添加'
  }
})

defineEmits(['action'])
</script>

<style scoped>
.empty-state {
  padding: 40px 0;
}

.empty-state :deep(.el-empty) {
  padding: 20px 0;
}

.empty-state :deep(.el-empty__description p) {
  font-size: 14px;
  color: #909399;
}
</style>
