<template>
  <el-container class="h-screen w-full">
    <el-aside width="240px" class="bg-slate-900 text-white flex flex-col">
      <div class="p-6 border-b border-slate-700">
        <h1 class="text-xl font-bold flex items-center gap-2">
          <el-icon><Briefcase /></el-icon>
          AI Recruitment
        </h1>
      </div>
      
      <el-menu
        active-text-color="#409EFF"
        background-color="#0f172a"
        class="border-r-0 flex-1"
        text-color="#fff"
        :default-active="$route.path"
        router
      >
        <el-menu-item index="/jobs">
          <el-icon><Management /></el-icon>
          <span>岗位管理</span>
        </el-menu-item>
        <el-menu-item index="/match">
          <el-icon><Connection /></el-icon>
          <span>简历匹配</span>
        </el-menu-item>
        <el-menu-item index="/candidates">
            <el-icon><User /></el-icon>
            <span>候选人库</span>
        </el-menu-item>
      </el-menu>
      
      <div class="p-4 border-t border-slate-700 text-xs text-slate-500 text-center">
        v1.0.0
      </div>
    </el-aside>
    
    <el-container class="bg-gray-50">
      <el-header class="bg-white border-b flex items-center justify-between px-6">
        <div class="text-lg font-medium text-gray-800">
          {{ currentRouteName }}
        </div>
        <div class="flex items-center gap-4">
           <el-avatar :size="32" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
           <span class="text-sm text-gray-600">HR Admin</span>
        </div>
      </el-header>
      
      <el-main class="p-6 overflow-hidden flex flex-col">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Briefcase, Connection, Management, User } from '@element-plus/icons-vue'

const route = useRoute()

const currentRouteName = computed(() => {
  switch(route.name) {
    case 'jobs': return '岗位管理'
    case 'job-create': return '发布新岗位'
    case 'match': return '简历匹配工作台'
    case 'candidates': return '候选人库'
    default: return ''
  }
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
