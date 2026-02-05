<template>
  <el-dialog
    v-model="visible"
    :title="dialogTitle"
    width="500px"
    :close-on-click-modal="false"
    destroy-on-close
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="100px"
      class="category-form"
    >
      <!-- 分类名称 -->
      <el-form-item label="分类名称" prop="name">
        <el-input
          v-model="formData.name"
          placeholder="请输入分类名称"
          maxlength="20"
          show-word-limit
          clearable
        />
      </el-form-item>

      <!-- 类型选择 -->
      <el-form-item label="类型" prop="type">
        <el-radio-group v-model="formData.type" :disabled="isEditChild">
          <el-radio label="income">
            <el-icon><Money /></el-icon>
            收入
          </el-radio>
          <el-radio label="expense">
            <el-icon><Wallet /></el-icon>
            支出
          </el-radio>
        </el-radio-group>
      </el-form-item>

      <!-- 上级分类选择（仅二级分类时显示） -->
      <el-form-item
        v-if="showParentSelector"
        label="上级分类"
        prop="parentId"
      >
        <el-select
          v-model="formData.parentId"
          placeholder="请选择上级分类"
          filterable
          clearable
          :disabled="isEditChild"
          class="parent-select"
        >
          <el-option
            v-for="cat in parentCategories"
            :key="cat.id"
            :label="cat.name"
            :value="cat.id"
          >
            <span>{{ cat.name }}</span>
            <el-tag
              :type="cat.type === 'income' ? 'success' : 'warning'"
              size="small"
              effect="plain"
              class="option-tag"
            >
              {{ cat.type === 'income' ? '收入' : '支出' }}
            </el-tag>
          </el-option>
        </el-select>
        <div class="form-tip" v-if="!isEditChild">
          选择一个一级分类作为上级，不选则为一级分类
        </div>
      </el-form-item>

      <!-- 图标选择 -->
      <el-form-item label="图标" prop="icon">
        <div class="icon-selector">
          <div
            class="icon-preview"
            :class="{ 'has-icon': formData.icon }"
            @click="showIconPicker = true"
          >
            <el-icon v-if="formData.icon" :size="28">
              <component :is="formData.icon" />
            </el-icon>
            <el-icon v-else :size="28" class="placeholder">
              <Picture />
            </el-icon>
          </div>
          <div class="icon-actions">
            <el-button
              v-if="formData.icon"
              type="primary"
              link
              @click="showIconPicker = true"
            >
              更换图标
            </el-button>
            <el-button
              v-else
              type="primary"
              link
              @click="showIconPicker = true"
            >
              选择图标
            </el-button>
            <el-button
              v-if="formData.icon"
              type="info"
              link
              @click="formData.icon = ''"
            >
              清除
            </el-button>
          </div>
        </div>
      </el-form-item>
    </el-form>

    <!-- 图标选择弹窗 -->
    <IconPicker
      v-model:visible="showIconPicker"
      v-model:selected="formData.icon"
      :type="formData.type"
    />

    <!-- 弹窗底部 -->
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">
        确定
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Money,
  Wallet,
  Picture
} from '@element-plus/icons-vue'
import IconPicker from './IconPicker.vue'

// Props
const props = defineProps({
  category: {
    type: Object,
    default: null
  },
  parentId: {
    type: [Number, String],
    default: null
  },
  mode: {
    type: String,
    default: 'add'
  }
})

// Emits
const emit = defineEmits(['success'])

// 响应式数据
const visible = ref(false)
const formRef = ref(null)
const submitting = ref(false)
const showIconPicker = ref(false)

// 模拟一级分类数据（后续替换为 store 数据）
const parentCategories = ref([
  { id: 1, name: '收入', type: 'income' },
  { id: 2, name: '支出', type: 'expense' }
])

// 表单数据
const formData = ref({
  id: null,
  name: '',
  type: 'expense',
  parentId: null,
  icon: ''
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { min: 1, max: 20, message: '分类名称长度为1-20个字符', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择类型', trigger: 'change' }
  ],
  parentId: [
    { required: true, message: '请选择上级分类', trigger: 'change' }
  ]
}

// 计算属性
const dialogTitle = computed(() => {
  switch (props.mode) {
    case 'add':
      return '新增一级分类'
    case 'addChild':
      return '新增子分类'
    case 'edit':
      return '编辑分类'
    default:
      return '分类表单'
  }
})

const showParentSelector = computed(() => {
  // 新增时显示（可选），编辑子分类时隐藏
  return props.mode !== 'edit' || !props.category?.parentId
})

const isEditChild = computed(() => {
  return props.mode === 'edit' && props.category?.parentId
})

// 方法
const open = async () => {
  visible.value = true
  await nextTick()
  
  // 重置表单
  resetForm()
  
  // 如果是编辑模式，填充数据
  if (props.mode === 'edit' && props.category) {
    formData.value = {
      id: props.category.id,
      name: props.category.name,
      type: props.category.type,
      parentId: props.category.parentId || null,
      icon: props.category.icon || ''
    }
  }
  
  // 如果是新增子分类模式，设置上级分类
  if (props.mode === 'addChild' && props.parentId) {
    formData.value.parentId = props.parentId
    // 根据上级分类类型自动设置类型
    const parentCat = parentCategories.value.find(c => c.id === props.parentId)
    if (parentCat) {
      formData.value.type = parentCat.type
    }
  }
}

const resetForm = () => {
  formData.value = {
    id: null,
    name: '',
    type: 'expense',
    parentId: null,
    icon: ''
  }
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

const handleClose = () => {
  visible.value = false
  resetForm()
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    // 准备提交数据
    const submitData = { ...formData.value }
    
    // 如果是一级分类，清除 parentId
    if (!submitData.parentId) {
      delete submitData.parentId
    }
    
    // 如果没有图标，清除 icon 字段
    if (!submitData.icon) {
      delete submitData.icon
    }
    
    // 触发成功事件
    emit('success', submitData)
    
    visible.value = false
    ElMessage.success(props.mode === 'edit' ? '更新成功' : '添加成功')
  } catch (error) {
    console.error('表单验证失败:', error)
  } finally {
    submitting.value = false
  }
}

// 监听类型变化，清除不兼容的图标
watch(() => formData.value.type, (newType) => {
  // 如果需要根据类型过滤图标，可以在这里处理
  // 当前简化处理，不做限制
})

// 暴露方法给父组件
defineExpose({
  open
})
</script>

<style scoped>
.category-form {
  padding: 10px 0;
}

.parent-select {
  width: 100%;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.icon-selector {
  display: flex;
  align-items: center;
  gap: 16px;
}

.icon-preview {
  width: 60px;
  height: 60px;
  border: 2px dashed #dcdfe6;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #f5f7fa;
}

.icon-preview:hover {
  border-color: #409eff;
  background: #ecf5ff;
}

.icon-preview.has-icon {
  border-style: solid;
  border-color: #409eff;
  background: #ecf5ff;
  color: #409eff;
}

.icon-preview .placeholder {
  color: #c0c4cc;
}

.icon-actions {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

:deep(.el-radio-group) {
  display: flex;
  gap: 20px;
}

:deep(.el-radio) {
  display: flex;
  align-items: center;
  gap: 6px;
}

.option-tag {
  margin-left: 8px;
}
</style>
