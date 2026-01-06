<template>
  <div class="h-full flex flex-col space-y-4">
    <div class="flex justify-between items-center">
      <h2 class="text-xl font-bold text-gray-800">简历匹配工作台</h2>
    </div>

    <!-- 顶部操作区 -->
    <el-card shadow="never" class="mb-4">
      <div class="flex items-end gap-4">
        <div class="flex-1">
          <label class="block text-sm font-medium text-gray-700 mb-1">选择岗位</label>
          <el-select v-model="selectedJobId" placeholder="请选择要进行匹配的岗位" class="w-full">
            <el-option
              v-for="job in jobs"
              :key="job.id"
              :label="job.title + ' - ' + job.department"
              :value="job.id"
            />
          </el-select>
        </div>
        <div class="flex-1">
           <!-- Placeholder for stats or other info -->
        </div>
      </div>
    </el-card>

    <!-- 主体区域：左侧上传，右侧结果 -->
    <div class="flex-1 flex gap-4 min-h-0">
      <!-- 左侧：上传区 -->
      <div class="w-1/3 flex flex-col gap-4">
        <el-upload
          class="upload-demo flex-1 flex flex-col"
          drag
          multiple
          :auto-upload="false"
          :on-change="handleFileChange"
          :on-remove="handleFileRemove"
          :file-list="fileList"
          action="#"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            拖拽 PDF 简历到此处，或 <em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              仅支持 PDF 文件
            </div>
          </template>
        </el-upload>
        
        <el-button 
            type="primary" 
            size="large" 
            :disabled="!selectedJobId || fileList.length === 0 || processing"
            :loading="processing"
            @click="startMatching"
        >
            {{ processing ? '正在分析中...' : '开始批量匹配' }}
        </el-button>
      </div>

      <!-- 右侧：结果列表 -->
      <div class="w-2/3 bg-white rounded-lg border border-gray-200 flex flex-col">
        <div class="p-4 border-b border-gray-100 flex justify-between items-center">
            <span class="font-bold text-gray-700">实时匹配结果 ({{ results.length }})</span>
            <el-button v-if="results.length > 0" link type="danger" @click="clearResults">清空</el-button>
        </div>
        
        <el-table :data="results" style="width: 100%" height="100%" stripe>
           <el-table-column label="状态" width="80">
              <template #default="{ row }">
                  <el-icon v-if="row.status === 'success'" color="green"><CircleCheckFilled /></el-icon>
                  <el-icon v-else color="red"><CircleCloseFilled /></el-icon>
              </template>
           </el-table-column>
           <el-table-column label="候选人" min-width="120">
               <template #default="{ row }">
                   <div v-if="row.status === 'success'">
                       <div class="font-medium">{{ row.data.resume.name }}</div>
                       <div class="text-xs text-gray-500 truncate">{{ row.data.resume.email }}</div>
                   </div>
                   <div v-else>
                       {{ row.filename }}
                   </div>
               </template>
           </el-table-column>
           <el-table-column label="匹配度" width="180">
               <template #default="{ row }">
                   <div v-if="row.status === 'success'" class="flex items-center gap-2">
                       <el-progress 
                        :percentage="row.data.match_result.overall_score" 
                        :status="getScoreStatus(row.data.match_result.overall_score)" 
                        class="w-24"
                       />
                       <span class="text-sm font-bold">{{ row.data.match_result.overall_score }}</span>
                   </div>
                   <div v-else class="text-red-500 text-xs">
                       {{ row.error }}
                   </div>
               </template>
           </el-table-column>
           <el-table-column label="评价摘要" min-width="200" show-overflow-tooltip>
               <template #default="{ row }">
                   <span v-if="row.status === 'success'">{{ row.data.match_result.summary }}</span>
               </template>
           </el-table-column>
           <el-table-column label="操作" width="100" fixed="right">
               <template #default="{ row }">
                   <el-button v-if="row.status === 'success'" link type="primary" size="small" @click="viewDetail(row)">详情</el-button>
               </template>
           </el-table-column>
        </el-table>
      </div>
    </div>
    
    <!-- 详情弹窗 -->
    <el-dialog v-model="dialogVisible" title="匹配详情" width="70%">
        <div v-if="currentDetail" class="grid grid-cols-2 gap-6">
            <div>
                <h3 class="font-bold mb-2">简历信息</h3>
                <pre class="bg-gray-50 p-4 rounded text-sm overflow-auto max-h-96 whitespace-pre-wrap">{{ JSON.stringify(currentDetail.data.resume, null, 2) }}</pre>
            </div>
            <div>
                <h3 class="font-bold mb-2">匹配分析</h3>
                <div class="bg-blue-50 p-4 rounded text-sm mb-4">
                    <p class="font-bold">得分: {{ currentDetail.data.match_result.overall_score }}</p>
                    <p class="mt-2">{{ currentDetail.data.match_result.summary }}</p>
                </div>
                <div class="bg-green-50 p-4 rounded text-sm">
                    <p class="font-bold">推荐理由:</p>
                    <p class="mt-2">{{ currentDetail.data.match_result.recommendation }}</p>
                </div>
            </div>
        </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { UploadFilled, CircleCheckFilled, CircleCloseFilled } from '@element-plus/icons-vue'
import type { UploadUserFile } from 'element-plus'

const route = useRoute()
const jobs = ref([])
const selectedJobId = ref<number | undefined>(undefined)
const fileList = ref<UploadUserFile[]>([])
const results = ref<any[]>([])
const processing = ref(false)

// Detail Dialog
const dialogVisible = ref(false)
const currentDetail = ref<any>(null)

const fetchJobs = async () => {
  try {
    const res = await axios.get('/api/v1/jobs')
    jobs.value = res.data
    // If jobId in query, select it
    if (route.query.jobId) {
        const id = Number(route.query.jobId)
        if (jobs.value.find((j: any) => j.id === id)) {
            selectedJobId.value = id
        }
    }
  } catch (error) {
    console.error(error)
  }
}

const handleFileChange = (file: UploadUserFile, files: UploadUserFile[]) => {
  fileList.value = files
}

const handleFileRemove = (file: UploadUserFile, files: UploadUserFile[]) => {
  fileList.value = files
}

const getScoreStatus = (score: number) => {
    if (score >= 80) return 'success'
    if (score >= 60) return 'warning'
    return 'exception'
}

const viewDetail = (row: any) => {
    currentDetail.value = row
    dialogVisible.value = true
}

const clearResults = () => {
    results.value = []
}

// *** Streaming Implementation ***
const startMatching = async () => {
    if (!selectedJobId.value || fileList.value.length === 0) return
    
    processing.value = true
    // results.value = [] // Optional: clear previous results? Let's append or clear. Let's clear for now.
    
    const formData = new FormData()
    formData.append('job_id', String(selectedJobId.value))
    fileList.value.forEach(file => {
        if (file.raw) {
            formData.append('files', file.raw)
        }
    })

    try {
        const response = await fetch('/api/v1/application/batch-submit', {
            method: 'POST',
            body: formData
        })

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
        }

        const reader = response.body?.getReader()
        if (!reader) throw new Error('ReadableStream not supported')
        
        const decoder = new TextDecoder()
        let buffer = ''

        while (true) {
            const { done, value } = await reader.read()
            if (done) break
            
            buffer += decoder.decode(value, { stream: true })
            const lines = buffer.split('\n')
            
            // Keep the last incomplete chunk in buffer
            buffer = lines.pop() || ''
            
            for (const line of lines) {
                if (line.trim()) {
                    try {
                        const result = JSON.parse(line)
                        results.value.push(result)
                    } catch (e) {
                        console.error('JSON Parse Error', e, line)
                    }
                }
            }
        }
        
        // Process any remaining buffer
        if (buffer.trim()) {
             try {
                const result = JSON.parse(buffer)
                results.value.push(result)
            } catch (e) {
                console.error('JSON Parse Error', e, buffer)
            }
        }

    } catch (error) {
        console.error('Matching failed', error)
        // Add error row
        results.value.push({
            status: 'error',
            filename: 'Batch Process Error',
            error: String(error)
        })
    } finally {
        processing.value = false
        // Optionally clear files on success?
    }
}

onMounted(() => {
  fetchJobs()
})
</script>
