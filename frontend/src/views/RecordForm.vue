<template>
  <div class="record-form-page">
    <el-card>
      <template #header>
        <h3>{{ isEdit ? '编辑记账' : '新增记账' }}</h3>
      </template>
      
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
      >
        <!-- 类型选择 -->
        <el-form-item label="类型" prop="type">
          <el-radio-group v-model="form.type">
            <el-radio-button label="expense">支出</el-radio-button>
            <el-radio-button label="income">收入</el-radio-button>
          </el-radio-group>
        </el-form-item>
        
        <!-- 金额输入 -->
        <el-form-item label="金额" prop="amount">
          <el-input-number
            v-model="form.amount"
            :precision="2"
            :min="0.01"
            :max="99999999"
            style="width: 100%"
          />
        </el-form-item>
        
        <!-- 分类选择 -->
        <el-form-item label="分类" prop="category_id">
          <el-select
            v-model="form.category_id"
            placeholder="请选择分类"
            style="width: 100%"
            filterable
          >
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        
        <!-- 日期选择 -->
        <el-form-item label="日期" prop="date">
          <el-date-picker
            v-model="form.date"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        
        <!-- 备注 -->
        <el-form-item label="备注">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="添加备注..."
          />
        </el-form-item>
        
        <!-- 项目选择（可选） -->
        <el-form-item label="项目">
          <el-select
            v-model="form.project_id"
            placeholder="选择项目（可选）"
            style="width: 100%"
            clearable
          >
            <el-option
              v-for="proj in projects"
              :key="proj.id"
              :label="proj.name"
              :value="proj.id"
            />
          </el-select>
        </el-form-item>
        
        <!-- AA制 -->
        <el-form-item label="AA制">
          <el-switch v-model="form.is_aa" active-text="启用AA分摊" />
        </el-form-item>
        
        <!-- 提交按钮 -->
        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            @click="handleSubmit"
          >
            {{ isEdit ? '保存修改' : '提交' }}
          </el-button>
          <el-button @click="handleCancel">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import client from '@/api/client'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const formRef = ref(null)
const loading = ref(false)
const categories = ref([])
const projects = ref([])

const isEdit = computed(() => !!route.params.id)

const form = reactive({
  type: 'expense',
  amount: 0.01,
  category_id: null,
  date: new Date().toISOString().split('T')[0],
  description: '',
  project_id: null,
  is_aa: false
})

const rules = {
  type: [
    { required: true, message: '请选择类型', trigger: 'change' }
  ],
  amount: [
    { required: true, message: '请输入金额', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '金额必须大于0', trigger: 'blur' }
  ],
  category_id: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ],
  date: [
    { required: true, message: '请选择日期', trigger: 'change' }
  ]
}

onMounted(async () => {
  await Promise.all([
    fetchCategories(),
    fetchProjects()
  ])
  
  if (isEdit.value) {
    await fetchRecord()
  }
})

async function fetchCategories() {
  try {
    const response = await client.get('/categories')
    categories.value = response
  } catch (error) {
    ElMessage.error('获取分类失败')
  }
}

async function fetchProjects() {
  try {
    const response = await client.get('/projects')
    projects.value = response.projects
  } catch (error) {
    ElMessage.error('获取项目失败')
  }
}

async function fetchRecord() {
  try {
    const response = await client.get(`/records/${route.params.id}`)
    Object.assign(form, response)
  } catch (error) {
    ElMessage.error('获取记录失败')
    router.push('/records')
  }
}

async function handleSubmit() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    loading.value = true
    try {
      if (isEdit.value) {
        await client.put(`/records/${route.params.id}`, form)
        ElMessage.success('修改成功')
      } else {
        await client.post('/records', form)
        ElMessage.success('提交成功')
      }
      router.push('/records')
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    } finally {
      loading.value = false
    }
  })
}

function handleCancel() {
  router.push('/records')
}
</script>

<style scoped>
.record-form-page {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}
</style>
