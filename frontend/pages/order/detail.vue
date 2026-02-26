<template>
  <view class="container">
    <!-- 订单状态 -->
    <view class="status-card">
      <view class="status-icon" :class="order.status">
        {{ getStatusIcon(order.status) }}
      </view>
      <view class="status-text">{{ getStatusText(order.status) }}</view>
      <view class="status-desc">{{ getStatusDesc(order.status) }}</view>
    </view>

    <!-- 交易进度 -->
    <view class="progress-section">
      <view class="progress-title">交易进度</view>
      <view class="progress-steps">
        <view class="step" :class="{ active: stepIndex >= 1 }">
          <view class="step-dot">1</view>
          <text class="step-text">创建订单</text>
        </view>
        <view class="step-line" :class="{ active: stepIndex >= 2 }"></view>
        <view class="step" :class="{ active: stepIndex >= 2 }">
          <view class="step-dot">2</view>
          <text class="step-text">支付</text>
        </view>
        <view class="step-line" :class="{ active: stepIndex >= 3 }"></view>
        <view class="step" :class="{ active: stepIndex >= 3 }">
          <view class="step-dot">3</view>
          <text class="step-text">租用</text>
        </view>
        <view class="step-line" :class="{ active: stepIndex >= 4 }"></view>
        <view class="step" :class="{ active: stepIndex >= 4 }">
          <view class="step-dot">4</view>
          <text class="step-text">归还</text>
        </view>
        <view class="step-line" :class="{ active: stepIndex >= 5 }"></view>
        <view class="step" :class="{ active: stepIndex >= 5 }">
          <view class="step-dot">5</view>
          <text class="step-text">完成</text>
        </view>
      </view>
    </view>

    <!-- 订单信息 -->
    <view class="order-info">
      <view class="info-title">订单信息</view>
      <view class="info-item">
        <text class="label">订单号</text>
        <text class="value">{{ order.order_no }}</text>
      </view>
      <view class="info-item">
        <text class="label">商品</text>
        <text class="value">{{ order.product && order.product.title }}</text>
      </view>
      <view class="info-item">
        <text class="label">租赁时长</text>
        <text class="value">{{ order.rental_hours }}小时</text>
      </view>
      <view class="info-item">
        <text class="label">租金</text>
        <text class="value price">¥{{ order.rent_amount }}</text>
      </view>
      <view class="info-item">
        <text class="label">押金</text>
        <text class="value price">¥{{ order.deposit_amount }}</text>
      </view>
      <view class="info-item">
        <text class="label">佣金</text>
        <text class="value">¥{{ order.commission_fee }}</text>
      </view>
      <view class="info-item total">
        <text class="label">合计</text>
        <text class="value">¥{{ order.total_amount }}</text>
      </view>
    </view>

    <!-- 联系方式 (支付后可见) -->
    <view class="contact-section" v-if="canShowContact">
      <view class="info-title">联系方式</view>
      <view class="contact-card">
        <view class="contact-item">
          <text class="label">{{ isRenter ? '卖家' : '买家' }}微信号</text>
          <view class="wechat-info">
            <text class="wechat-id">{{ contactWechatId }}</text>
            <button class="copy-btn" @click="copyWechat">复制</button>
          </view>
        </view>
        <view class="contact-tip">
          <text>请添加对方微信获取账号密码，沟通时注意文明</text>
        </view>
      </view>
    </view>

    <!-- 验号倒计时 -->
    <view class="verify-section" v-if="order.status === 'RETURNED' && isLender">
      <view class="verify-card">
        <view class="verify-title">验号确认</view>
        <view class="verify-time">
          剩余时间: {{ remainingTime }}
        </view>
        <view class="verify-tip">
          请检查账号是否正常，确认后押金将退还给租客
        </view>
        <view class="verify-btns">
          <button class="btn-confirm" @click="handleConfirm">确认无误</button>
          <button class="btn-dispute" @click="showDisputeModal = true">有异常</button>
        </view>
      </view>
    </view>

    <!-- 底部操作栏 -->
    <view class="bottom-bar" v-if="showActionBar">
      <!-- 待支付 -->
      <template v-if="order.status === 'PENDING_PAYMENT'">
        <button class="btn-primary" @click="handlePay">立即支付</button>
        <button class="btn-default" @click="handleCancel">取消订单</button>
      </template>
      
      <!-- 租用中 (租客) -->
      <template v-else-if="order.status === 'PAID' && isRenter">
        <button class="btn-primary" @click="handleReturn">确认归还</button>
      </template>
      
      <!-- 租用中 (房东) -->
      <template v-else-if="order.status === 'PAID' && isLender">
        <view class="waiting-tip">等待租客归还...</view>
      </template>
    </view>

    <!-- 维权弹窗 -->
    <uni-modal v-model="showDisputeModal" title="发起维权">
      <view class="dispute-form">
        <textarea 
          v-model="disputeReason" 
          placeholder="请描述账号异常情况..."
          class="dispute-textarea"
        />
      </view>
      <view slot="footer" class="modal-footer">
        <button @click="showDisputeModal = false">取消</button>
        <button class="btn-primary" @click="handleDispute">提交</button>
      </view>
    </uni-modal>
  </view>
</template>

<script>
import { api } from '@/utils/api.js'
import { useUserStore } from '@/store/user.js'

export default {
  data() {
    return {
      orderId: null,
      order: {},
      contactWechatId: '',
      remainingTime: '',
      showDisputeModal: false,
      disputeReason: '',
      timer: null
    }
  },
  
  computed: {
    userInfo() {
      const userStore = useUserStore()
      return userStore.user || {}
    },
    
    isRenter() {
      return this.order.renter_id === this.userInfo.id
    },
    
    isLender() {
      return this.order.lender_id === this.userInfo.id
    },
    
    canShowContact() {
      return ['PAID', 'RETURNED', 'COMPLETED'].includes(this.order.status)
    },
    
    showActionBar() {
      return ['PENDING_PAYMENT', 'PAID', 'RETURNED'].includes(this.order.status) &&
        (this.isRenter || this.isLender)
    },
    
    stepIndex() {
      const map = {
        'PENDING_PAYMENT': 1,
        'PAID': 2,
        'RETURNED': 4,
        'COMPLETED': 5,
        'CANCELLED': 0,
        'DISPUTE': 0
      }
      return map[this.order.status] || 0
    }
  },
  
  onLoad(options) {
    this.orderId = options.id
    this.loadOrder()
  },
  
  onUnload() {
    if (this.timer) {
      clearInterval(this.timer)
    }
  },
  
  methods: {
    async loadOrder() {
      try {
        uni.showLoading({ title: '加载中' })
        const res = await api.orders.detail(this.orderId)
        this.order = res
        
        // 如果可以显示联系方式，获取联系方式
        if (this.canShowContact) {
          this.loadContact()
        }
        
        // 如果是待验号状态，开始倒计时
        if (this.order.status === 'RETURNED') {
          this.startCountdown()
        }
        
        uni.hideLoading()
      } catch (e) {
        uni.hideLoading()
        uni.showToast({
          title: '加载失败',
          icon: 'none'
        })
      }
    },
    
    async loadContact() {
      try {
        const res = await api.orders.contact(this.orderId)
        this.contactWechatId = res.wechat_id
      } catch (e) {
        console.error(e)
      }
    },
    
    startCountdown() {
      this.updateRemainingTime()
      this.timer = setInterval(() => {
        this.updateRemainingTime()
      }, 1000)
    },
    
    updateRemainingTime() {
      if (!this.order.verify_deadline) return
      
      const deadline = new Date(this.order.verify_deadline).getTime()
      const now = Date.now()
      const diff = deadline - now
      
      if (diff <= 0) {
        this.remainingTime = '已超时'
        if (this.timer) {
          clearInterval(this.timer)
        }
        return
      }
      
      const hours = Math.floor(diff / (1000 * 60 * 60))
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
      const seconds = Math.floor((diff % (1000 * 60)) / 1000)
      
      this.remainingTime = `${hours}小时${minutes}分${seconds}秒`
    },
    
    getStatusIcon(status) {
      const map = {
        'PENDING_PAYMENT': '⏰',
        'PAID': '🔑',
        'RETURNED': '🔍',
        'COMPLETED': '✅',
        'CANCELLED': '❌',
        'DISPUTE': '⚠️'
      }
      return map[status] || '📋'
    },
    
    getStatusText(status) {
      const map = {
        'PENDING_PAYMENT': '待支付',
        'PAID': '租用中',
        'RETURNED': '待验号',
        'COMPLETED': '已完成',
        'CANCELLED': '已取消',
        'DISPUTE': '纠纷中'
      }
      return map[status] || status
    },
    
    getStatusDesc(status) {
      const map = {
        'PENDING_PAYMENT': '请尽快完成支付',
        'PAID': '账号使用中，请注意时间',
        'RETURNED': '请在48小时内验号确认',
        'COMPLETED': '交易已完成',
        'CANCELLED': '订单已取消',
        'DISPUTE': '请联系客服处理'
      }
      return map[status] || ''
    },
    
    copyWechat() {
      uni.setClipboardData({
        data: this.contactWechatId,
        success: () => {
          uni.showToast({
            title: '已复制微信号',
            icon: 'success'
          })
        }
      })
    },
    
    async handlePay() {
      try {
        await api.orders.pay(this.orderId)
        uni.showToast({
          title: '支付成功',
          icon: 'success'
        })
        this.loadOrder()
      } catch (e) {
        uni.showToast({
          title: e.message || '支付失败',
          icon: 'none'
        })
      }
    },
    
    async handleCancel() {
      uni.showModal({
        title: '提示',
        content: '确定要取消订单吗？',
        success: async (res) => {
          if (res.confirm) {
            try {
              await api.orders.cancel(this.orderId)
              uni.showToast({
                title: '订单已取消',
                icon: 'success'
              })
              setTimeout(() => {
                uni.navigateBack()
              }, 1500)
            } catch (e) {
              uni.showToast({
                title: e.message || '取消失败',
                icon: 'none'
              })
            }
          }
        }
      })
    },
    
    async handleReturn() {
      uni.showModal({
        title: '确认归还',
        content: '确认要归还账号吗？',
        success: async (res) => {
          if (res.confirm) {
            try {
              await api.orders.return(this.orderId, '')
              uni.showToast({
                title: '已确认归还',
                icon: 'success'
              })
              this.loadOrder()
            } catch (e) {
              uni.showToast({
                title: e.message || '操作失败',
                icon: 'none'
              })
            }
          }
        }
      })
    },
    
    async handleConfirm() {
      uni.showModal({
        title: '确认验号',
        content: '确认账号无异常，押金将退还给租客',
        success: async (res) => {
          if (res.confirm) {
            try {
              await api.orders.confirm(this.orderId, '')
              uni.showToast({
                title: '确认成功',
                icon: 'success'
              })
              this.loadOrder()
            } catch (e) {
              uni.showToast({
                title: e.message || '操作失败',
                icon: 'none'
              })
            }
          }
        }
      })
    },
    
    async handleDispute() {
      if (!this.disputeReason || this.disputeReason.length < 10) {
        uni.showToast({
          title: '请详细描述异常情况',
          icon: 'none'
        })
        return
      }
      
      try {
        await api.orders.dispute(this.orderId, this.disputeReason, '')
        uni.showToast({
          title: '已提交维权',
          icon: 'success'
        })
        this.showDisputeModal = false
        this.loadOrder()
      } catch (e) {
        uni.showToast({
          title: e.message || '提交失败',
          icon: 'none'
        })
      }
    }
  }
}
</script>

<style>
.container {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 140rpx;
}

.status-card {
  background: linear-gradient(135deg, #00D4AA, #00B894);
  padding: 50rpx 30rpx;
  text-align: center;
  color: #fff;
}

.status-icon {
  font-size: 60rpx;
  margin-bottom: 10rpx;
}

.status-text {
  font-size: 36rpx;
  font-weight: bold;
  margin-bottom: 10rpx;
}

.status-desc {
  font-size: 26rpx;
  opacity: 0.9;
}

.progress-section {
  background-color: #fff;
  margin: 20rpx;
  border-radius: 16rpx;
  padding: 30rpx;
}

.progress-title {
  font-size: 28rpx;
  font-weight: bold;
  margin-bottom: 30rpx;
}

.progress-steps {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.step-dot {
  width: 40rpx;
  height: 40rpx;
  border-radius: 50%;
  background-color: #ddd;
  color: #fff;
  font-size: 22rpx;
  line-height: 40rpx;
  text-align: center;
  margin-bottom: 10rpx;
}

.step.active .step-dot {
  background-color: #00D4AA;
}

.step-text {
  font-size: 20rpx;
  color: #999;
}

.step.active .step-text {
  color: #00D4AA;
}

.step-line {
  flex: 1;
  height: 2rpx;
  background-color: #ddd;
  margin: 0 5rpx 20rpx;
}

.step-line.active {
  background-color: #00D4AA;
}

.order-info {
  background-color: #fff;
  margin: 20rpx;
  border-radius: 16rpx;
  padding: 30rpx;
}

.info-title {
  font-size: 28rpx;
  font-weight: bold;
  margin-bottom: 20rpx;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 15rpx 0;
  border-bottom: 1rpx solid #f5f5f5;
}

.info-item .label {
  font-size: 26rpx;
  color: #999;
}

.info-item .value {
  font-size: 26rpx;
  color: #333;
}

.info-item .value.price {
  color: #ff6b6b;
  font-weight: bold;
}

.info-item.total {
  border-bottom: none;
  margin-top: 10rpx;
}

.info-item.total .value {
  font-size: 32rpx;
  color: #ff6b6b;
  font-weight: bold;
}

.contact-section {
  background-color: #fff;
  margin: 20rpx;
  border-radius: 16rpx;
  padding: 30rpx;
}

.contact-card {
  background-color: #f9f9f9;
  border-radius: 12rpx;
  padding: 20rpx;
}

.contact-item {
  margin-bottom: 15rpx;
}

.contact-item .label {
  display: block;
  font-size: 24rpx;
  color: #666;
  margin-bottom: 10rpx;
}

.wechat-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.wechat-id {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
}

.copy-btn {
  background-color: #00D4AA;
  color: #fff;
  font-size: 22rpx;
  padding: 10rpx 20rpx;
  border-radius: 30rpx;
  border: none;
}

.contact-tip {
  font-size: 22rpx;
  color: #999;
  margin-top: 15rpx;
}

.verify-section {
  margin: 20rpx;
}

.verify-card {
  background-color: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  text-align: center;
}

.verify-title {
  font-size: 28rpx;
  font-weight: bold;
  margin-bottom: 20rpx;
}

.verify-time {
  font-size: 32rpx;
  color: #ff6b6b;
  font-weight: bold;
  margin-bottom: 20rpx;
}

.verify-tip {
  font-size: 24rpx;
  color: #999;
  margin-bottom: 30rpx;
}

.verify-btns {
display: flex;
  gap: 20rpx;
}

.btn-confirm {
  flex: 1;
  background-color: #00D4AA;
  color: #fff;
  border-radius: 40rpx;
  border: none;
}

.btn-dispute {
  flex: 1;
  background-color: #ff6b6b;
  color: #fff;
  border-radius: 40rpx;
  border: none;
}

.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  gap: 20rpx;
  padding: 20rpx 30rpx;
  background-color: #fff;
  box-shadow: 0 -2rpx 10rpx rgba(0, 0, 0, 0.1);
}

.bottom-bar button {
  flex: 1;
  height: 80rpx;
  border-radius: 40rpx;
  font-size: 28rpx;
  border: none;
}

.btn-primary {
  background-color: #00D4AA;
  color: #fff;
}

.btn-default {
  background-color: #f5f5f5;
  color: #666;
}

.waiting-tip {
  flex: 1;
  text-align: center;
  line-height: 80rpx;
  font-size: 28rpx;
  color: #999;
}

.dispute-form {
  padding: 20rpx;
}

.dispute-textarea {
  width: 100%;
  height: 200rpx;
  padding: 20rpx;
  background-color: #f9f9f9;
  border-radius: 12rpx;
  font-size: 26rpx;
}

.modal-footer {
  display: flex;
  gap: 20rpx;
}

.modal-footer button {
  flex: 1;
}
</style>
