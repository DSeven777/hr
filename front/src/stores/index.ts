import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    isLoading: false
  }),
  actions: {
    setLoading(status: boolean) {
      this.isLoading = status
    }
  }
})
