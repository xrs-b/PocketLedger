<template>
  <div class="empty-state">
    <el-empty :description="description">
      <template v-if="$slots.image">
        <slot name="image" />
      </template>
      <template v-else>
        <el-icon class="empty-icon"><icon-name /></el-icon>
      </template>
      <template v-if="$slots.actions">
        <div class="empty-actions">
          <slot name="actions" />
        </div>
      </template>
    </el-empty>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'

defineProps({
  description: {
    type: String,
    default: '暂无数据'
  },
  iconName: {
    type: Object,
    default: null
  }
})
</script>

<style scoped>
.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 64px;
  color: #c0c4cc;
}

.empty-actions {
  margin-top: 20px;
}
</style>
