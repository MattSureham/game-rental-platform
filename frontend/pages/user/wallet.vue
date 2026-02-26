<template>
  <view class="container">
    <!-- 余额展示 -->
    <view class="balance-section">
      <view class="balance-label">{{ type === 'recharge' ? '充值' : '提现' }}</view>
      <view class="balance-value">¥{{ amount }}</view>
    </view>

    <!-- 充值/提现表单 -->
    <view class="form-section" v-if="type === 'recharge'">
      <view class="form-title">选择充值金额</view>
      <view class="amount-grid">
        <view 
          v-for="a in rechargeOptions" 
          :key="a"
          class="amount-item"
          :class="{ active: amount === a }"
          @click="selectAmount(a)"
        >
          ¥{{ a }}
        </view>
      </view>
      <view class="custom-amount">
        <text>自定义:</text>
        <input 
          v-model.number="amount" 
          type="digit" 
          class="amount-input"
          placeholder="请输入金额"
          @input="onAmountInput"
        />
      </view>
    </view>

    <view class="form-section" v-else>
      <view class="form-title">输入提现金额</view>
      <view class="input-wrapper">
        <text class="currency">¥</text>
        <input 
          v-model.number="amount" 
          type="digit" 
          class="amount-input large"
          placeholder="0.00"
          @input="onAmountInput"
        />
      </view>
      <view class="balance-tip">
        当前余额: ¥{{ balanceInfo.balance }}
        <text class="all-btn" @click="amount = balanceInfo.balance">全部提现</text>
      </view>
    </view>

    <!-- 提交按钮 -->
    <view class="submit-section">
      <button 
        class="submit-btn" 
        @click="handleSubmit"
        :disabled="!amount || amount <= 0 || submitting"
      >
        {{ submitting ? '处理中...' : (type === 'recharge' ? '立即充值' : '立即提现') }}
      </button>
    </view>

    <!-- 交易记录 -->
    <view class="record-section">
      <view class="section-title">交易记录</view>
      <view class="record-list">
        <view 
          v-for="log in logs" 
          :key="log.id"
          class="record-item"
        >
          <view class="record-info">
            <text class="record-type">{{ getTypeText(log.type) }}</text>
            <text class="record-desc">{{ log.description }}</text>
          </view>
          <view class="record-amount" :class="log.direction">
            {{ log.direction === 'income' ? '+' : '-' }}¥{{ log.amount }}
          </view>
        </view>
        <view v-if="logs.length === 0" class="empty">
          暂无记录
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { api } from '@/utils/api.js'

export default {
  data() {
    return {
      type: 'recharge',
      amount: 0,
      rechargeOptions: [10, 30, 50, 100, 200, 500],
      balanceInfo: {},
      logs: [],
      submitting: false
    }
  },
  
  onLoad(options) {
    this.type = options.type || 'recharge'
    this.loadBalance()
    this.loadLogs()
  },
  
  methods: {
    async loadBalance() {
      try {
        const res = await api.wallet.balance()
        this.balanceInfo = res
      } catch (e) {
        console.error(e)
      }
    },
    
    async loadLogs() {
      try {
        const res = await api.wallet.logs()
        this.logs = res
      } catch (e) {
        console.error(e)
      }
    },
    
    selectAmount(a) {
      this.amount = a
    },
    
    onAmountInput(e) {
      this.amount = parseFloat(e.detail.value) || 0
    },
    
    getTypeText(type) {
      const map = {
        'RECHARGE': '充值',
        'PAYMENT': '支付',
        'DEPOSIT_REFUND': '押金退还',
        'RENTAL_INCOME': '租金收入',
        'COMMISSION': '佣金',
        'WITHDRAWAL': '提现'
      }
      return map[type] || type
    },
    
    async handleSubmit() {
      if (!this.amount || this.amount <= 0) {
        uni.showToast({
          title: '请输入有效金额',
          icon: 'none'
        })
        return
      }
      
      if (this.type === 'withdraw' && this.amount > this.balanceInfo.balance) {
        uni.showToast({
          title: '余额不足',
          icon: 'none'
        })
        return
      }
      
      this.submitting = true
      
      try {
        if (this.type === 'recharge') {
          await api.wallet.recharge(this.amount)
          uni.showToast({
            title: '充值成功',
            icon: 'success'
          })
        } else {
          await api.wallet.withdraw(this.amount)
          uni.showToast({
            title: '提现成功',
            icon: 'success'
          })
        }
        
        // 刷新数据
        this.loadBalance()
        this.loadLogs()
        
        setTimeout(() => {
          uni.navigateBack()
        }, 1500)
      } catch (e) {
        uni.showToast({
          title: e.message || '操作失败',
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
}

.balance-section {
  background: linear-gradient(135deg, #00D4AA, #00B894);
  padding: 60rpx 30rpx;
  text-align: center;
}

.balance-label {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 20rpx;
}

.balance-value {
  font-size: 72rpx;
  font-weight: bold;
  color: #fff;
}

.form-section {
  background-color: #fff;
  margin: 30rpx;
  border-radius: 16rpx;
  padding: 30rpx;
}

.form-title {
  font-size: 28rpx;
  font-weight: bold;
  margin-bottom: 30rpx;
}

.amount-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
}

.amount-item {
  width: calc(33.33% - 14rpx);
  height: 100rpx;
  line-height: 100rpx;
  text-align: center;
  background-color: #f5f5f5;
  border-radius: 12rpx;
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.amount-item.active {
  background-color: #00D4AA;
  color: #fff;
}

.custom-amount {
  display: flex;
  align-items: center;
  margin-top: 30rpx;
  padding: 20rpx;
  background-color: #f5f5f5;
  border-radius: 12rpx;
}

.custom-amount text {
  font-size: 28rpx;
  color: #666;
  margin-right: 20rpx;
}

.amount-input {
  flex: 1;
  height: 60rpx;
  font-size: 32rpx;
}

.amount-input.large {
  height: 80rpx;
  font-size: 48rpx;
}

.input-wrapper {
  display: flex;
  align-items: center;
  padding: 30rpx;
  background-color: #f5f5f5;
  border-radius: 12rpx;
}

.currency {
  font-size: 48rpx;
  font-weight: bold;
  color: #333;
  margin-right: 20rpx;
}

.balance-tip {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20rpx;
  font-size: 26rpx;
  color: #666;
}

.all-btn {
  color: #00D4AA;
}

.submit-section {
  padding: 0 30rpx;
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

.record-section {
  background-color: #fff;
  margin: 30rpx;
  border-radius: 16rpx;
  padding: 30rpx;
}

.section-title {
  font-size: 28rpx;
  font-weight: bold;
  margin-bottom: 20rpx;
}

.record-list {
  max-height: 500rpx;
  overflow-y: auto;
}

.record-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #f5f5f5;
}

.record-item:last-child {
  border-bottom: none;
}

.record-info {
  flex: 1;
}

.record-type {
  display: block;
  font-size: 28rpx;
  color: #333;
  margin-bottom: 5rpx;
}

.record-desc {
  display: block;
  font-size: 24rpx;
  color: #999;
}

.record-amount {
  font-size: 32rpx;
  font-weight: bold;
}

.record-amount.income {
  color: #52c41a;
}

.record-amount.expense {
  color: #ff6b6b;
}

.empty {
  text-align: center;
  padding: 40rpx;
  color: #999;
  font-size: 26rpx;
}
</style>
