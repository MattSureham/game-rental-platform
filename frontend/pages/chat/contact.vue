<template>
  <view class="container">
    <!-- 联系方式展示 -->
    <view class="contact-card">
      <view class="card-title">{{ isRenter ? '卖家' : '买家' }}联系方式</view>
      
      <view class="wechat-section">
        <text class="label">微信号</text>
        <view class="wechat-value">
          <text class="id">{{ wechatId }}</text>
          <button class="copy-btn" @click="copyWechat">复制</button>
        </view>
      </view>
      
      <view class="tip-section">
        <view class="tip-title">温馨提示</view>
        <view class="tip-list">
          <text>1. 请复制上方微信号，搜索并添加对方为好友</text>
          <text>2. 添加好友时备注"游戏账号租赁"，便于对方通过</text>
          <text>3. 通过微信获取账号密码或扫码登录</text>
          <text>4. 沟通时请保持文明礼貌</text>
          <text>5. 如遇问题可在平台发起维权</text>
        </view>
      </view>
    </view>
    
    <!-- 操作按钮 -->
    <view class="action-section">
      <button class="contact-btn" open-type="contact" v-if="false">
        联系客服
      </button>
      <button class="done-btn" @click="handleDone">
        我知道了
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
      orderId: null,
      wechatId: '',
      isRenter: false
    }
  },
  
  onLoad(options) {
    this.orderId = options.orderId
    this.isRenter = options.isRenter === 'true'
    this.loadContact()
  },
  
  methods: {
    async loadContact() {
      try {
        const res = await api.orders.contact(this.orderId)
        this.wechatId = res.wechat_id
      } catch (e) {
        uni.showToast({
          title: '获取联系方式失败',
          icon: 'none'
        })
      }
    },
    
    copyWechat() {
      uni.setClipboardData({
        data: this.wechatId,
        success: () => {
          uni.showToast({
            title: '已复制微信号',
            icon: 'success'
          })
        }
      })
    },
    
    handleDone() {
      uni.navigateBack()
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

.contact-card {
  background-color: #fff;
  border-radius: 16rpx;
  padding: 40rpx;
}

.card-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  text-align: center;
  margin-bottom: 40rpx;
}

.wechat-section {
  background-color: #f9f9f9;
  border-radius: 12rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
}

.wechat-section .label {
  display: block;
  font-size: 26rpx;
  color: #666;
  margin-bottom: 15rpx;
}

.wechat-value {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.wechat-value .id {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
}

.copy-btn {
  background-color: #00D4AA;
  color: #fff;
  font-size: 24rpx;
  padding: 15rpx 30rpx;
  border-radius: 30rpx;
  border: none;
}

.tip-section {
  background-color: #fff7e6;
  border-radius: 12rpx;
  padding: 25rpx;
}

.tip-title {
  font-size: 26rpx;
  font-weight: bold;
  color: #ff9f43;
  margin-bottom: 15rpx;
}

.tip-list text {
  display: block;
  font-size: 24rpx;
  color: #666;
  line-height: 1.8;
}

.action-section {
  margin-top: 40rpx;
}

.contact-btn {
  width: 100%;
  height: 90rpx;
  background-color: #fff;
  color: #00D4AA;
  font-size: 28rpx;
  border-radius: 45rpx;
  border: 2rpx solid #00D4AA;
  margin-bottom: 20rpx;
}

.done-btn {
  width: 100%;
  height: 90rpx;
  background-color: #00D4AA;
  color: #fff;
  font-size: 28rpx;
  border-radius: 45rpx;
  border: none;
}
</style>
