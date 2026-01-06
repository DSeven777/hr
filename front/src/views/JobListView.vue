<template>
  <div class="space-y-4">
    <div class="flex justify-between items-center">
      <h2 class="text-xl font-bold text-gray-800">岗位列表</h2>
      <el-button type="primary" @click="$router.push('/jobs/create')">
        <el-icon class="mr-1"><Plus /></el-icon> 发布新岗位
      </el-button>
    </div>

    <el-card shadow="hover">
      <el-table :data="jobs" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="职位名称" min-width="150" />
        <el-table-column prop="department" label="部门" width="120" />
        <el-table-column prop="required_experience_years" label="经验要求" width="100">
             <template #default="{ row }">
                 {{ row.required_experience_years }} 年
             </template>
        </el-table-column>
        <el-table-column label="技能要求" min-width="200">
          <template #default="{ row }">
            <div class="flex gap-1 flex-wrap">
              <el-tag v-for="skill in row.required_skills" :key="skill" size="small" effect="plain">
                {{ skill }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
             <el-button link type="primary" size="small" @click="goToMatch(row.id)">去匹配</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { Plus } from '@element-plus/icons-vue'

const router = useRouter()
const jobs = ref([])
const loading = ref(false)

const fetchJobs = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/v1/jobs')
    jobs.value = res.data
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const goToMatch = (jobId: number) => {
    router.push({ name: 'match', query: { jobId } })
}

onMounted(() => {
  fetchJobs()
})
</script>
