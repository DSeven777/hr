<template>
  <div class="space-y-4">
    <div class="flex justify-between items-center">
      <h2 class="text-xl font-bold text-gray-800">候选人库</h2>
    </div>
    
    <el-card shadow="never" class="mb-4">
        <el-form :inline="true">
            <el-form-item label="筛选岗位">
                <el-select v-model="filterJobId" placeholder="全部岗位" clearable @change="fetchCandidates">
                    <el-option
                      v-for="job in jobs"
                      :key="job.id"
                      :label="job.title"
                      :value="job.id"
                    />
                </el-select>
            </el-form-item>
        </el-form>
    </el-card>

    <el-card shadow="hover">
      <el-table :data="candidates" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="phone" label="电话" width="150" />
        <el-table-column label="匹配岗位" min-width="150">
             <template #default="{ row }">
                 <el-tag size="small">{{ getJobName(row.matched_job_id) }}</el-tag>
             </template>
        </el-table-column>
        <el-table-column prop="match_score" label="匹配分" width="100" sortable>
             <template #default="{ row }">
                 <span :class="getScoreClass(row.match_score)">{{ row.match_score }}</span>
             </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
             <el-button link type="primary" size="small" @click="viewDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog v-model="dialogVisible" title="候选人详情" width="60%">
        <div v-if="currentCandidate">
             <el-descriptions title="基本信息" :column="2" border>
                <el-descriptions-item label="姓名">{{ currentCandidate.name }}</el-descriptions-item>
                <el-descriptions-item label="电话">{{ currentCandidate.phone }}</el-descriptions-item>
                <el-descriptions-item label="邮箱">{{ currentCandidate.email }}</el-descriptions-item>
                <el-descriptions-item label="匹配岗位">{{ getJobName(currentCandidate.matched_job_id) }}</el-descriptions-item>
             </el-descriptions>
             
             <div class="mt-4">
                 <h4 class="font-bold mb-2">个人简介</h4>
                 <p class="text-sm bg-gray-50 p-2 rounded">{{ currentCandidate.summary }}</p>
             </div>
             
             <div class="mt-4">
                 <h4 class="font-bold mb-2">匹配分析</h4>
                 <div class="text-sm bg-blue-50 p-2 rounded whitespace-pre-wrap">{{ currentCandidate.match_analysis }}</div>
             </div>
        </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

const candidates = ref([])
const jobs = ref([])
const loading = ref(false)
const filterJobId = ref<number | undefined>(undefined)

const dialogVisible = ref(false)
const currentCandidate = ref<any>(null)

const fetchJobs = async () => {
    try {
        const res = await axios.get('/api/v1/jobs')
        jobs.value = res.data
    } catch (e) {
        console.error(e)
    }
}

const fetchCandidates = async () => {
  loading.value = true
  try {
    const params: any = {}
    if (filterJobId.value) params.job_id = filterJobId.value
    
    const res = await axios.get('/api/v1/candidates', { params })
    candidates.value = res.data
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const getJobName = (jobId: number) => {
    const job = jobs.value.find((j: any) => j.id === jobId)
    return job ? job.title : jobId
}

const getScoreClass = (score: number) => {
    if (score >= 80) return 'text-green-600 font-bold'
    if (score >= 60) return 'text-orange-500 font-bold'
    return 'text-red-500'
}

const viewDetail = (row: any) => {
    currentCandidate.value = row
    dialogVisible.value = true
}

onMounted(() => {
  fetchJobs()
  fetchCandidates()
})
</script>
