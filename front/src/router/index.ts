import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layout/MainLayout.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: MainLayout,
      redirect: '/jobs',
      children: [
        {
          path: 'jobs',
          name: 'jobs',
          component: () => import('../views/JobListView.vue')
        },
        {
          path: 'jobs/create',
          name: 'job-create',
          component: () => import('../views/JobCreateView.vue')
        },
        {
          path: 'match',
          name: 'match',
          component: () => import('../views/MatchingWorkbenchView.vue')
        },
        {
            path: 'candidates',
            name: 'candidates',
            component: () => import('../views/CandidateListView.vue')
        }
      ]
    }
  ]
})

export default router
