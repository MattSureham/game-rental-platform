<template>
  <view class="container">
    <!-- 用户信息 -->
    <view class="section">
      <view class="section-title">个人信息</view>
      <view class="form-item">
        <text class="label">昵称</text>
        <input 
          v-model="formData.nickname" 
          class="input" 
          placeholder="请输入昵称"
        />
      </view>
      <view class="form-item">
        <text class="label">手机号</text>
        <input 
          v-model="formData.phone" 
          class="input" 
          type="number"
          maxlength="11"
          placeholder="请输入手机号(可选)"
        />
      </view>
    </view>

    <!-- 微信联系方式 -->
    <view class="section">
      <view class="section-title">交易联系方式</view>
      <view class="form-item">
        <text class="label">微信号</text>
        <view class="wechat-wrapper">
          <input 
            v-model="formData.wechat_id" 
            class="input" 
            placeholder="请输入微信号"
          />
          <text class="tip" v-if="!formData.wechat_id">用于交易时联系</text>
        </view>
      </view>
      <view class="form-tip">
        <text class="icon">ℹ️</text>
        <text class="text">微信号仅在订单支付后才会展示给交易对方，用于账号交接。平台不会在任何公开页面显示您的微信号。</text>
      </view>
    </view>

    <!-- 角色设置 -->
    <view class="section">
      <view class="section-title">角色设置</view>
      <view class="role-selector">
        <view 
          class="role-item"
          :class="{ active: formData.role === 'renter' }"
          @click="formData.role = 'renter'"
        >
          <text class="role-icon">🎮</text>
          <text class="role-name">我想要租号</text>
          <text class="role-desc">体验高端账号</text>
        </view>
        <view 
          class="role-item"
          :class="{ active: formData.role === 'lender' }"
          @click="formData.role = 'lender'"
        >
          <text class="role-icon">💰</text>
          <text class="role-name">我想要出租</text>
          <text class="role-desc">闲置账号变现</text>
        </view>
      </view>
    </view>

    <!-- 保存按钮 -->
    <view class="submit-section">
      <button class="save-btn" @click="handleSave" :disabled="saving">
        {{ saving ? '保存中...' : '保存修改' }}
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
      formData: {
        nickname: '',
        phone: '',
        wechat_id: '',
        role: 'renter'
      },
      saving: false
    }
  },
  
  onLoad() {
    this.loadProfile()
  },
  
  methods: {
    async loadProfile() {
      try {
        const res = await api.auth.getProfile()
        this.formData = {
          nickname: res.nickname || '',
          phone: res.phone || '',
          wechat_id: res.wechat_id || '',
          role: res.role || 'renter'
        }
      } catch (e) {
        uni.showToast({
          title: '加载失败',
          icon: 'none'
        })
      }
    },
    
    async handleSave() {
      this.saving = true
      
      try {
        // 保存基本信息
        await api.auth.updateProfile({
          nickname: this.formData.nickname,
          phone: this.formData.phone,
          role: this.formData.role
        })
        
        // 如果微信号有变化，更新微信号
        const userStore = useUserStore()
        if (this.formData.wechat_id && this.formData.wechat_id !== userStore.user.wechat_id) {
          await api.auth.updateWechatId(this.formData.wechat_id)
        }
        
        // 刷新用户信息
        await userStore.fetchProfile()
        
        uni.showToast({
          title: '保存成功',
          icon: 'success'
        })
        
        setTimeout(() => {
          uni.navigateBack()
        }, 1500)
      } catch (e) {
        uni.showToast({
          title: e.message || '保存失败',
          icon: 'none'
        })
      } finally {
        this.saving = false
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

.section {
  background-color: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
}

.section-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 30rpx;
}

.form-item {
  display: flex;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #f5f5f5;
}

.form-item:last-child {
  border-bottom: none;
}

.form-item .label {
  width: 140rpx;
  font-size: 28rpx;
  color: #666;
}

.form-item .input {
  flex: 1;
  font-size: 28rpx;
  color: #333;
}

.wechat-wrapper {
  flex: 1;
}

.wechat-wrapper .tip {
  display: block;
  font-size: 22rpx;
  color: #999;
  margin-top: 10rpx;
}

.form-tip {
  display: flex;
  padding: 20rpx;
  background-color: #f9f9f9;
  border-radius: 12rpx;
  margin-top: 20rpx;
}

.form-tip .icon {
  font-size: 28rpx;
  margin-right: 10rpx;
}

.form-tip .text {
  flex: 1;
  font-size: 24rpx;
  color: #999;
  line-height: 1.6;
}

.role-selector {
  display: flex;
  gap: 20rpx;
}

.role-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30rpx;
  background-color: #f5f5f5;
  border-radius: 12rpx;
  border: 4rpx solid transparent;
}

.role-item.active {
  border-color: #00D4AA;
  background-color: #e6fcf5;
}

.role-icon {
  font-size: 60rpx;
  margin-bottom: 15rpx;
}

.role-name {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 10rpx;
}

.role-desc {
  font-size: 24rpx;
  color: #999;
}

.submit-section {
  margin-top: 40rpx;
}

.save-btn {
  width: 100%;
  height: 90rpx;
  background-color: #00D4AA;
  color: #fff;
  font-size: 32rpx;
  border-radius: 45rpx;
  border: none;
}

.save-btn[disabled] {
  background-color: #ccc;
}
</style>
