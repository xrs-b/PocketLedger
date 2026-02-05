<template>
  <footer class="app-footer">
    <slot>&copy; {{ currentYear }} PocketLedger. All rights reserved.</slot>
  </footer>
</template>

<script setup>
import { computed } from 'vue'

const currentYear = computed(() => new Date().getFullYear())
</script>

<style scoped>
.app-footer {
  padding: 20px;
  text-align: center;
  color: #909399;
  font-size: 14px;
}
</style>
