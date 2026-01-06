<template>
  <div class="max-w-4xl mx-auto space-y-6">
    <div class="flex items-center gap-4 mb-6">
      <el-button @click="$router.back()" circle icon="ArrowLeft" />
      <h2 class="text-xl font-bold text-gray-800">发布新岗位</h2>
    </div>

    <!-- AI 解析区域 -->
    <el-card class="bg-blue-50 border-blue-100" shadow="never">
      <template #header>
        <div class="flex justify-between items-center">
          <span class="flex items-center gap-2 font-medium text-blue-800">
            <el-icon><MagicStick /></el-icon> AI 智能解析
          </span>
          <el-button type="primary" :loading="parsing" @click="parseJob" :disabled="!rawText">
            一键解析
          </el-button>
        </div>
      </template>
      <el-input
        v-model="rawText"
        type="textarea"
        :rows="6"
        placeholder="请粘贴原始 JD 文本（如：职位描述、任职要求等）..."
      />
    </el-card>

    <!-- 表单区域 -->
    <el-card shadow="hover">
      <el-form :model="form" label-width="100px" ref="formRef">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="职位名称" required>
              <el-input v-model="form.title" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="所属部门">
              <el-input v-model="form.department" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
            <el-col :span="12">
                <el-form-item label="经验要求">
                    <el-input-number v-model="form.required_experience_years" :min="0" :max="20" />
                    <span class="ml-2 text-gray-500">年</span>
                </el-form-item>
            </el-col>
            <el-col :span="12">
                <el-form-item label="学历要求">
                    <el-input v-model="form.degree_requirement" />
                </el-form-item>
            </el-col>
        </el-row>

        <el-form-item label="核心技能">
           <el-select
              v-model="form.required_skills"
              multiple
              filterable
              allow-create
              default-first-option
              placeholder="输入技能并回车"
              class="w-full"
            />
        </el-form-item>
        
        <el-form-item label="加分技能">
           <el-select
              v-model="form.nice_to_have_skills"
              multiple
              filterable
              allow-create
              default-first-option
              placeholder="输入技能并回车"
              class="w-full"
            />
        </el-form-item>

        <el-form-item label="岗位职责">
          <el-input type="textarea" :rows="4" v-model="form.responsibilities" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="submitJob">确认发布</el-button>
          <el-button @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { MagicStick, ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const rawText = ref('')
const parsing = ref(false)
const submitting = ref(false)

const form = reactive({
  title: '',
  department: '',
  required_skills: [] as string[],
  nice_to_have_skills: [] as string[],
  required_experience_years: 0,
  degree_requirement: '',
  responsibilities: ''
})

const parseJob = async () => {
  if (!rawText.value) return
  parsing.value = true
  try {
    const res = await axios.post('/api/v1/job/parse', { text: rawText.value })
    const data = res.data
    // Map response to form
    form.title = data['Job Title'] || ''
    form.department = data['Department'] || ''
    form.required_skills = data['Required Skills'] || []
    form.nice_to_have_skills = data['Nice to have Skills'] || []
    form.required_experience_years = data['Required Experience Years'] || 0
    form.degree_requirement = data['Degree Requirement'] || ''
    form.responsibilities = data['Responsibilities'] || ''
    
    ElMessage.success('解析成功')
  } catch (error) {
    ElMessage.error('解析失败')
    console.error(error)
  } finally {
    parsing.value = false
  }
}

const submitJob = async () => {
  if (!form.title) {
      ElMessage.warning('职位名称不能为空')
      return
  }
  submitting.value = true
  try {
      // Backend expects CamelCase keys matching JobDescription model or Pydantic will auto convert?
      // Wait, Backend JobDescription model uses Field(alias="Job Title"). 
      // If I send snake_case keys (title, department...), Pydantic usually accepts them if `populate_by_name=True`.
      // Let's check JobDescription model in src/domain/job.py.
      // If it doesn't support population by name, I need to send aliases.
      
      // Let's try sending aliases as per JobDescription definition.
      // Actually, let's look at `src/domain/job.py` via Read tool if needed.
      // But typically Pydantic V2 config allows both.
      // Let's assume aliases are needed to be safe or snake_case if it's standard Pydantic.
      // The `create_job` endpoint expects `JobDescription`.
      // `create_job` in `main.py` accesses `job.title`, `job.department`.
      
      // I will send the object with keys matching `JobDescription` fields.
      // Let's check `src/domain/job.py` quickly to be sure about keys.
      
      const payload = {
          "Job Title": form.title,
          "Department": form.department,
          "Required Skills": form.required_skills,
          "Nice to have Skills": form.nice_to_have_skills,
          "Required Experience Years": form.required_experience_years,
          "Degree Requirement": form.degree_requirement,
          "Responsibilities": form.responsibilities
      }
      
      await axios.post('/api/v1/jobs', payload)
      ElMessage.success('发布成功')
      router.push('/jobs')
  } catch (error) {
      ElMessage.error('发布失败')
      console.error(error)
  } finally {
      submitting.value = false
  }
}
</script>
