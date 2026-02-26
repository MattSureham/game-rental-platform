<template>
  <view class="container">
    <!-- 商品信息 -->
    <view class="product-card">
      <image 
        class="product-image" 
        :src="product.images && product.images[0] ? product.images[0] : '/static/default-game.png'" 
        mode="aspectFill"
      />
      <view class="product-info">
        <view class="product-title">{{ product.title }}</view>
        <view class="product-game">{{ product.game_name }}</view>
        <view class="product-price">
          <text>时租: ¥{{ product.hourly_price }}/时</text>
          <text class="deposit">押金: ¥{{ product.deposit }}</text>
        </view>
      </view>
    </view>

    <!-- 租赁选项 -->
    <view class="options-card">
      <view class="option-title">租赁时长</view>
      <view class="hours-selector">
        <view 
          v-for="h in hourOptions" 
          :key="h"
          class="hour-item"
          :class="{ active: rentalHours === h }"
          @click="selectHour(h)"
        >
          {{ h }}小时
        </view>
      </view>
      <view class="custom-hours">
        <text>自定义:</text>
        <input 
          v-model.number="rentalHours" 
          type="number" 
          class="hours-input"
          @change="validateHours"
        />
        <text>小时</text>
      </view>
    </view>

    <!-- 费用明细 -->
    <view class="fee-card">
      <view class="fee-title">费用明细</view>
      <view class="fee-item">
        <text>租金 (¥{{ product.hourly_price }} × {{ rentalHours }}小时)</text>
        <text class="fee-value">¥{{ rentAmount }}</text>
      </view>
      <view class="fee-item">
        <text>押金</text>
        <text class="fee-value">¥{{ product.deposit }}</text>
      </view>
      <view class="fee-item total">
        <text>合计</text>
        <text class="fee-value">¥{{ totalAmount }}</text>
      </view>
    </view>

    <!-- 余额提示 -->
    <view class="balance-card" v-if="balanceInfo">
      <view class="balance-item">
        <text>当前余额</text>
        <text class="balance-value">¥{{ balanceInfo.balance }}</text>
      </view>
      <view class="balance-item" v-if="balanceInfo.balance < totalAmount">
        <text>还需充值</text>
        <text class="balance-value need">¥{{ totalAmount - balanceInfo.balance }}</text>
      </view>
      <view class="balance-tip" v-if="balanceInfo.balance < totalAmount">
        余额不足，请先充值
      </view>
    </view>

    <!-- 底部操作栏 -->
    <view class="bottom-bar">
      <view class="total-info">
        <text class="label">合计:</text>
        <text class="amount">¥{{ totalAmount }}</text>
      </view>
      <button 
        class="submit-btn" 
        @click="handleSubmit"
        :disabled="submitting || (balanceInfo && balanceInfo.balance < totalAmount)"
      >
        {{ submitting ? '提交中...' : '确认支付' }}
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
      productId: null,
      product: {},
      rentalHours: 1,
      hourOptions: [1, 2, 3, 6, 12, 24, 48],
      balanceInfo: null,
      submitting: false
    }
  },
  
  computed: {
    rentAmount() {
      if (!this.product.hourly_price) return 0
      return (this.product.hourly_price * this.rentalHours).toFixed(2)
    },
    
    totalAmount() {
      if (!this.product.deposit) return this.rentAmount
      return (parseFloat(this.rentAmount) + parseFloat(this.product.deposit)).toFixed(2)
    }
  },
  
  onLoad(options) {
    this.productId = options.productId
    this.rentalHours = parseInt(options.hours) || 1
    this.loadProduct()
    this.loadBalance()
  },
  
  methods: {
    async loadProduct() {
      try {
        const res = await api.products.detail(this.productId)
        this.product = res
      } catch (e) {
        uni.showToast({
          title: '加载失败',
          icon: 'none'
        })
      }
    },
    
    async loadBalance() {
      try {
        const res = await api.wallet.balance()
        this.balanceInfo = res
      } catch (e) {
        console.error(e)
      }
    },
    
    selectHour(h) {
      this.rentalHours = h
    },
    
    validateHours() {
      if (this.rentalHours < 1) this.rentalHours = 1
      if (this.rentalHours > 720) this.rentalHours = 720
    },
    
    async handleSubmit() {
      this.submitting = true
      
      try {
        // 创建订单
        const orderRes = await api.orders.create({
          product_id: this.productId,
          rental_type: 'hourly',
          rental_hours: this.rentalHours
        })
        
        // 支付订单
        await api.orders.pay(orderRes.id)
        
        uni.showToast({
          title: '支付成功',
          icon: 'success'
        })
        
        // 跳转到订单详情
        setTimeout(() => {
          uni.redirectTo({
            url: `/pages/order/detail?id=${orderRes.id}`
          })
        }, 1500)
      } catch (e) {
        uni.showToast({
          title: e.message || '支付失败',
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
  padding-bottom: 140rpx;
}

.product-card {
  display: flex;
  background-color: #fff;
  padding: 30rpx;
  margin: 20rpx;
  border-radius: 16rpx;
}

.product-image {
  width: 160rpx;
  height: 160rpx;
  border-radius: 12rpx;
  background-color: #eee;
}

.product-info {
  flex: 1;
  margin-left: 20rpx;
}

.product-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 10rpx;
}

.product-game {
  font-size: 24rpx;
  color: #666;
  margin-bottom: 15rpx;
}

.product-price {
  font-size: 24rpx;
  color: #666;
}

.product-price .deposit {
  margin-left: 20rpx;
  color: #ff9f43;
}

.options-card {
  background-color: #fff;
  padding: 30rpx;
  margin: 20rpx;
  border-radius: 16rpx;
}

.option-title {
  font-size: 28rpx;
  font-weight: bold;
  margin-bottom: 20rpx;
}

.hours-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 15rpx;
}

.hour-item {
  padding: 15rpx 30rpx;
  background-color: #f5f5f5;
  border-radius: 30rpx;
  font-size: 26rpx;
  color: #666;
}

.hour-item.active {
  background-color: #00D4AA;
  color: #fff;
}

.custom-hours {
  display: flex;
  align-items: center;
  margin-top: 20rpx;
  font-size: 26rpx;
  color: #666;
}

.hours-input {
  width: 120rpx;
  height: 60rpx;
  margin: 0 15rpx;
  padding: 0 20rpx;
  background-color: #f5f5f5;
  border-radius: 12rpx;
  text-align: center;
}

.fee-card {
  background-color: #fff;
  padding: 30rpx;
  margin: 20rpx;
  border-radius: 16rpx;
}

.fee-title {
  font-size: 28rpx;
  font-weight: bold;
  margin-bottom: 20rpx;
}

.fee-item {
  display: flex;
  justify-content: space-between;
  padding: 15rpx 0;
  font-size: 26rpx;
  color: #666;
}

.fee-item.total {
  border-top: 1rpx solid #f5f5f5;
  margin-top: 15rpx;
  padding-top: 20rpx;
  font-weight: bold;
  color: #333;
}

.fee-item .fee-value {
  color: #333;
}

.fee-item.total .fee-value {
  color: #ff6b6b;
  font-size: 32rpx;
}

.balance-card {
  background-color: #fff;
  padding: 30rpx;
  margin: 20rpx;
  border-radius: 16rpx;
}

.balance-item {
  display: flex;
  justify-content: space-between;
  padding: 10rpx 0;
  font-size: 26rpx;
}

.balance-value {
  font-weight: bold;
}

.balance-value.need {
  color: #ff6b6b;
}

.balance-tip {
  font-size: 24rpx;
  color: #ff6b6b;
  margin-top: 15rpx;
}

.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  padding: 20rpx 30rpx;
  background-color: #fff;
  box-shadow: 0 -2rpx 10rpx rgba(0, 0, 0, 0.1);
}

.total-info {
  margin-right: 30rpx;
}

.total-info .label {
  font-size: 26rpx;
  color: #666;
}

.total-info .amount {
  font-size: 36rpx;
  font-weight: bold;
  color: #ff6b6b;
}

.submit-btn {
  flex: 1;
  height: 80rpx;
  background-color: #00D4AA;
  color: #fff;
  font-size: 28rpx;
  border-radius: 40rpx;
  border: none;
}

.submit-btn[disabled] {
  background-color: #ccc;
}
</style>
