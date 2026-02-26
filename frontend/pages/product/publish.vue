<template>
  <view class="container">
    <view class="form-section">
      <!-- 游戏分类 -->
      <view class="form-item">
        <view class="form-label">游戏分类</view>
        <picker :range="categories" range-key="name" @change="onCategoryChange">
          <view class="picker-value">
            {{ formData.game_category || '请选择游戏分类' }}
          </view>
        </picker>
      </view>

      <!-- 游戏名称 -->
      <view class="form-item">
        <view class="form-label">游戏名称</view>
        <input 
          v-model="formData.game_name" 
          class="form-input" 
          placeholder="如: 王者荣耀"
        />
      </view>

      <!-- 商品标题 -->
      <view class="form-item">
        <view class="form-label">商品标题</view>
        <input 
          v-model="formData.title" 
          class="form-input" 
          placeholder="简短描述你的账号优势"
        />
      </view>

      <!-- 商品描述 -->
="form-item">
      <view class        <view class="form-label">商品描述</view>
        <textarea 
          v-model="formData.description" 
          class="form-textarea" 
          placeholder="详细描述账号情况: 英雄皮肤、段位、装备等"
        />
      </view>

      <!-- 时租金 -->
      <view class="form-item">
        <view class="form-label">时租金 (元/小时)</view>
        <input 
          v-model.number="formData.hourly_price" 
          class="form-input" 
          type="digit"
          placeholder="请输入租金"
        />
      </view>

      <!-- 日租金 -->
      <view class="form-item">
        <view class="form-label">日租金 (元/天)</view>
        <input 
          v-model.number="formData.daily_price" 
          class="form-input" 
          type="digit"
          placeholder="可选"
        />
      </view>

      <!-- 押金 -->
      <view class="form-item">
        <view class="form-label">押金 (元)</view>
        <input 
          v-model.number="formData.deposit" 
          class="form-input" 
          type="digit"
          placeholder="请输入押金金额"
        />
      </view>

      <!-- 您的微信号 -->
      <view class="form-item" v-if="!userInfo.wechat_id">
        <view class="form-label">微信号</view>
        <view class="wechat-tip">
          <text>发布商品需要先绑定微信号</text>
          <button class="bind-btn" @click="goToSetWechat">去绑定</button>
        </view>
      </view>
    </view>

    <!-- 提交按钮 -->
    <view class="submit-section">
      <button class="submit-btn" @click="handleSubmit" :disabled="submitting">
        {{ submitting ? '发布中...' : '发布商品' }}
      </button>
    </view>
  </view>
</template>

<script>
import { api } from '@/utils/api.js'
import { useUserStore } from '@/store/user.js'

export default {
  data() {
    return {
      categories: [],
      formData: {
        game_category: '',
        game_name: '',
        title: '',
        description: '',
        hourly_price: null,
        daily_price: null,
        deposit: null,
        images: []
      },
      submitting: false
    }
  },
  
  computed: {
    userInfo() {
      const userStore = useUserStore()
      return userStore.user || {}
    }
  },
  
  onLoad() {
    this.loadCategories()
    this.checkWechatId()
  },
  
  methods: {
    async loadCategories() {
      try {
        const res = await api.products.categories()
        this.categories = res
      } catch (e) {
        console.error(e)
      }
    },
    
    async checkWechatId() {
      const userStore = useUserStore()
      if (!userStore.isLoggedIn) {
        uni.navigateTo({
          url: '/pages/user/profile'
        })
        return
      }
      await userStore.fetchProfile()
    },
    
    onCategoryChange(e) {
      this.formData.game_category = this.categories[e.detail.value].name
    },
    
    goToSetWechat() {
      uni.navigateTo({
        url: '/pages/user/settings'
      })
    },
    
    async handleSubmit() {
      // 验证
      if (!this.formData.game_category) {
        uni.showToast({ title: '请选择游戏分类', icon: 'none' })
        return
      }
      if (!this.formData.game_name) {
        uni.showToast({ title: '请输入游戏名称', icon: 'none' })
        return
      }
      if (!this.formData.title) {
        uni.showToast({ title: '请输入商品标题', icon: 'none' })
        return
      }
      if (!this.formData.hourly_price || this.formData.hourly_price <= 0) {
        uni.showToast({ title: '请输入时租金', icon: 'none' })
        return
      }
      if (!this.formData.deposit || this.formData.deposit < 0) {
        uni.showToast({ title: '请输入押金金额', icon: 'none' })
        return
      }
      
      this.submitting = true
      
      try {
        const res = await api.products.create(this.formData)
        uni.showToast({
          title: '发布成功',
          icon: 'success'
        })
        setTimeout(() => {
          uni.navigateBack()
        }, 1500)
      } catch (e) {
        uni.showToast({
          title: e.message || '发布失败',
          icon: 'none'
        })
      } finally {
        this.submitting = false
      }
    }
  }
}
</script>

<style>
.container {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 30rpx;
}

.form-section {
  background-color: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
}

.form-item {
  margin-bottom: 30rpx;
}

.form-label {
  font-size: 28rpx;
  color: #333;
  font-weight: bold;
  margin-bottom: 15rpx;
}

.form-input {
  width: 100%;
  height: 80rpx;
  padding: 0 20rpx;
  background-color: #f9f9f9;
  border-radius: 12rpx;
  font-size: 28rpx;
}

.form-textarea {
  width: 100%;
  height: 200rpx;
  padding: 20rpx;
  background-color: #f9f9f9;
  border-radius: 12rpx;
  font-size: 28rpx;
}

.picker-value {
  height: 80rpx;
  padding: 0 20rpx;
  background-color: #f9f9f9;
  border-radius: 12rpx;
  font-size: 28rpx;
  line-height: 80rpx;
  color: #666;
}

.wechat-tip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx;
  background-color: #fff7e6;
  border-radius: 12rpx;
}

.wechat-tip text {
  font-size: 26rpx;
  color: #ff9f43;
}

.bind-btn {
  background-color: #ff9f43;
  color: #fff;
  font-size: 24rpx;
  padding: 10rpx 30rpx;
  border-radius: 30rpx;
  border: none;
}

.submit-section {
  margin-top: 40rpx;
}

.submit-btn {
  width: 100%;
  height: 90rpx;
  background-color: #00D4AA;
  color: #fff;
  font-size: 32rpx;
  border-radius: 45rpx;
  border: none;
}

.submit-btn[disabled] {
  background-color: #ccc;
}
</style>
