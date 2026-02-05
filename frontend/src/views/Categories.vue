<template>
  <div class="categories-container">
    <div class="page-header">
      <h2>分类管理</h2>
      <el-button type="primary" @click="handleAdd">新增分类</el-button>
    </div>

    <!-- 分类统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon income"><Money /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ incomeCount }}</div>
              <div class="stat-label">收入分类</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon expense"><Wallet /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ expenseCount }}</div>
              <div class="stat-label">支出分类</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon total"><Grid /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ totalCount }}</div>
              <div class="stat-label">总分类数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 类型切换标签页 -->
    <el-tabs v-model="activeType" class="type-tabs">
      <el-tab-pane label="全部" name="all"></el-tab-pane>
      <el-tab-pane label="收入" name="income"></el-tab-pane>
      <el-tab-pane label="支出" name="expense"></el-tab-pane>
    </el-tabs>

    <!-- 分类树形结构 -->
    <el-card class="categories-card">
      <el-tree
        v-if="filteredCategories.length > 0"
        :data="filteredCategories"
        :props="treeProps"
        node-key="id"
        default-expand-all
        :expand-on-click-node="false"
        class="category-tree"
      >
        <template #default="{ node, data }">
          <div class="category-node">
            <div class="node-content">
              <!-- 图标 -->
              <el-icon v-if="data.icon" class="category-icon" :size="20">
                <component :is="data.icon" />
              </el-icon>
              <el-icon v-else class="category-icon placeholder" :size="20">
                <Folder />
              </el-icon>

              <!-- 分类名称 -->
              <span class="category-name">{{ data.name }}</span>

              <!-- 预设标签 -->
              <el-tag
                v-if="data.isPreset"
                type="info"
                size="small"
                effect="plain"
                class="preset-tag"
              >
                预设
              </el-tag>

              <!-- 类型标签 -->
              <el-tag
                :type="data.type === 'income' ? 'success' : 'warning'"
                size="small"
                effect="light"
                class="type-tag"
              >
                {{ data.type === 'income' ? '收入' : '支出' }}
              </el-tag>

              <!-- 二级分类数量 -->
              <span v-if="data.children && data.children.length > 0" class="child-count">
                ({{ data.children.length }})
              </span>
            </div>

            <!-- 操作按钮 -->
            <div class="node-actions" v-if="!data.isPreset || isAdmin">
              <el-button
                v-if="!data.parentId"
                type="primary"
                link
                size="small"
                @click="handleAddChild(data)"
              >
                <el-icon><Plus /></el-icon>
                添加子分类
              </el-button>
              <el-button
                type="primary"
                link
                size="small"
                @click="handleEdit(data)"
              >
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button
                type="danger"
                link
                size="small"
                @click="handleDelete(data)"
              >
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
          </div>
        </template>
      </el-tree>

      <!-- 空状态 -->
      <el-empty
        v-else
        description="暂无分类数据"
        :image-size="120"
      >
        <el-button type="primary" @click="handleAdd">添加第一个分类</el-button>
      </el-empty>
    </el-card>

    <!-- 分类表单弹窗 -->
    <CategoryForm
      ref="categoryFormRef"
      :category="selectedCategory"
      :parent-id="parentId"
      :mode="formMode"
      @success="onFormSuccess"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Money,
  Wallet,
  Grid,
  Folder,
  Plus,
  Edit,
  Delete
} from '@element-plus/icons-vue'
import CategoryForm from './CategoryForm.vue'

// 响应式数据
const activeType = ref('all')
const categoryFormRef = ref(null)
const selectedCategory = ref(null)
const parentId = ref(null)
const formMode = ref('add')

// 模拟分类数据（后续替换为 store 数据）
const categories = ref([
  {
    id: 1,
    name: '收入',
    type: 'income',
    isPreset: true,
    children: [
      { id: 11, name: '工资', parentId: 1, type: 'income', icon: 'Money', isPreset: true },
      { id: 12, name: '奖金', parentId: 1, type: 'income', icon: 'Gift', isPreset: true },
      { id: 13, name: '投资', parentId: 1, type: 'income', icon: 'TrendCharts', isPreset: false }
    ]
  },
  {
    id: 2,
    name: '支出',
    type: 'expense',
    isPreset: true,
    children: [
      { id: 21, name: '餐饮', parentId: 2, type: 'expense', icon: 'Food', isPreset: true },
      { id: 22, name: '交通', parentId: 2, type: 'expense', icon: 'Van', isPreset: true },
      { id: 23, name: '购物', parentId: 2, type: 'expense', icon: 'ShoppingCart', isPreset: true },
      { id: 24, name: '娱乐', parentId: 2, type: 'expense', icon: 'Film', isPreset: false }
    ]
  }
])

// 树形组件配置
const treeProps = {
  label: 'name',
  children: 'children'
}

// 计算属性
const filteredCategories = computed(() => {
  if (activeType.value === 'all') {
    return categories.value
  }
  return categories.value.filter(cat => cat.type === activeType.value)
})

const incomeCount = computed(() => {
  let count = 0
  categories.value.forEach(cat => {
    if (cat.type === 'income') {
      count += 1 + (cat.children?.length || 0)
    }
  })
  return count
})

const expenseCount = computed(() => {
  let count = 0
  categories.value.forEach(cat => {
    if (cat.type === 'expense') {
      count += 1 + (cat.children?.length || 0)
    }
  })
  return count
})

const totalCount = computed(() => {
  return incomeCount.value + expenseCount.value
})

const isAdmin = ref(true) // 假设当前用户是管理员

// 方法
const handleAdd = () => {
  selectedCategory.value = null
  parentId.value = null
  formMode.value = 'add'
  categoryFormRef.value?.open()
}

const handleAddChild = (parent) => {
  selectedCategory.value = null
  parentId.value = parent.id
  formMode.value = 'addChild'
  categoryFormRef.value?.open()
}

const handleEdit = (category) => {
  selectedCategory.value = category
  formMode.value = 'edit'
  categoryFormRef.value?.open()
}

const handleDelete = async (category) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除分类"${category.name}"吗？${
        category.children?.length > 0 ? '该分类下的子分类也将被删除。' : ''
      }`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // TODO: 调用 store 删除分类
    ElMessage.success('删除成功')

    // 从本地数据中移除（模拟）
    const parentIndex = categories.value.findIndex(
      cat => cat.id === category.parentId || cat.id === category.id
    )
    if (parentIndex !== -1) {
      if (category.parentId) {
        // 删除子分类
        const childIndex = categories.value[parentIndex].children?.findIndex(
          child => child.id === category.id
        )
        if (childIndex !== -1) {
          categories.value[parentIndex].children.splice(childIndex, 1)
        }
      } else {
        // 删除一级分类
        categories.value.splice(parentIndex, 1)
      }
    }
  } catch {
    // 用户取消
  }
}

const onFormSuccess = (formData) => {
  // TODO: 调用 store 保存分类
  ElMessage.success(formMode.value === 'edit' ? '更新成功' : '添加成功')

  // 模拟更新本地数据
  if (formMode.value === 'add') {
    categories.value.push({
      id: Date.now(),
      name: formData.name,
      type: formData.type,
      icon: formData.icon,
      isPreset: false,
      children: []
    })
  } else if (formMode.value === 'addChild') {
    const parentIndex = categories.value.findIndex(cat => cat.id === parentId.value)
    if (parentIndex !== -1) {
      if (!categories.value[parentIndex].children) {
        categories.value[parentIndex].children = []
      }
      categories.value[parentIndex].children.push({
        id: Date.now(),
        name: formData.name,
        type: formData.type,
        parentId: parentId.value,
        icon: formData.icon,
        isPreset: false
      })
    }
  } else if (formMode.value === 'edit') {
    const updateCategory = (cats) => {
      cats.forEach(cat => {
        if (cat.id === formData.id) {
          Object.assign(cat, formData)
        }
        if (cat.children) {
          updateCategory(cat.children)
        }
      })
    }
    updateCategory(categories.value)
  }
}
</script>

<style scoped>
.categories-container {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 12px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon.income {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  color: white;
}

.stat-icon.expense {
  background: linear-gradient(135deg, #e6a23c 0%, #f0c78a 100%);
  color: white;
}

.stat-icon.total {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  color: white;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.type-tabs {
  margin-bottom: 20px;
}

.categories-card {
  border-radius: 12px;
}

.category-tree {
  padding: 10px 0;
}

.category-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
  width: 100%;
}

.node-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.category-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #409eff;
}

.category-icon.placeholder {
  color: #909399;
}

.category-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.preset-tag {
  font-size: 12px;
  margin-left: 8px;
}

.type-tag {
  font-size: 12px;
}

.child-count {
  font-size: 12px;
  color: #909399;
  margin-left: 4px;
}

.node-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .categories-container {
    padding: 12px;
  }

  .page-header h2 {
    font-size: 20px;
  }

  .stat-value {
    font-size: 24px;
  }

  .node-actions {
    display: none;
  }

  .category-node:hover .node-actions {
    display: flex;
  }
}
</style>
