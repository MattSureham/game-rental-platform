import { defineStore } from 'pinia'
import api from '@/utils/api.js'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    token: uni.getStorageSync('token') || null
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.token,
    userInfo: (state) => state.user
  },
  
  actions: {
    async login(code) {
      try {
        const res = await api.auth.login(code)
        this.token = res.access_token
        this.user = res.user
        uni.setStorageSync('token', res.access_token)
        uni.setStorageSync('user', res.user)
        return res
      } catch (e) {
        throw e
      }
    },
    
    async fetchProfile() {
      try {
        const res = await api.auth.getProfile()
        this.user = res
        uni.setStorageSync('user', res)
        return res
      } catch (e) {
        this.logout()
        throw e
      }
    },
    
    logout() {
      this.token = null
      this.user = null
      uni.removeStorageSync('token')
      uni.removeStorageSync('user')
    },
    
    async updateWechatId(wechat_id) {
      const res = await api.auth.updateWechatId(wechat_id)
      await this.fetchProfile()
      return res
    }
  }
})
