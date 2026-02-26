<template>
  <view class="container">
    <!-- 标签页 -->
    <view class="tabs">
      <view 
        class="tab-item" 
        :class="{ active: activeTab === 'all' }"
        @click="switchTab('all')"
      >
        全部
      </view>
      <view 
        class="tab-item" 
        :class="{ active: activeTab === 'renting' }"
        @click="switchTab('renting')"
      >
        我租的
      </view>
      <view 
        class="tab-item" 
        :class="{ active: activeTab === 'lending' }"
        @click="switchTab('lending')"
      >
        我出租的
      </view>
    </view>

    <!-- 订单列表 -->
    <scroll-view class="order-list" scroll-y @scrolltolower="loadMore">
      <view 
        v-for="order in orders" 
        :key="order.id"
        class="order-card"
        @click="goToDetail(order.id)"
      >
        <view class="order-header">
          <text class="order-no">{{ order.order_no }}</text>
          <text class="order-status" :class="order.status">{{ getStatusText(order.status) }}</text>
        </view>
        
        <view class="order-body">
          <view class="product-info">
            <text class="game-name">{{ order.product && order.product.game_name }}</text>
            <text class="product-title">{{ order.product && order.product.title }}</text>
          </view>
          <view class="order-price">
            <text class="label">租金</text>
            <text class="value">¥{{ order.rent_amount }}</text>
          </view>
          <view class="order-price">
            <text class="label">押金</text>
            <text class="value">¥{{ order.deposit_amount }}</text>
          </view>
        </view>
        
        <view class="order-footer">
          <text class="time">{{ formatTime(order.created_at) }}</text>
          <view class="role-badge" :class="getUserRole(order)">
            {{ getUserRoleText(order) }}
          </view>
        </view>
      </view>
      
      <view v-if="loading" class="loading">
        <text>加载中...</text>
      </view>
      
      <view v-if="!loading && orders.length === 0" class="empty">
        <text>暂无订单</text>
      </view>
    </scroll-view>
  </view>
</template>

<script>
import { api } from '@/utils/api.js'
import { useUserStore } from '@/store/user.js'

export default {
  data() {
    return {
      activeTab: 'all',
      orders: [],
      page: 1,
      loading: false,
      hasMore: true
    }
  },
  
  onShow() {
    this.loadOrders()
  },
  
  methods: {
    async loadOrders() {
      if (this.loading) return
      this.loading = true
      
      try {
        let res
        const params = { page: this.page, page_size: 20 }
        
        if (this.activeTab === 'renting') {
          res = await api.orders.renting()
        } else if (this.activeTab === 'lending') {
          res = await api.orders.lending()
        } else {
          res = await api.orders.list(params)
        }
        
        if (this.page === 1) {
          this.orders = res
        } else {
          this.orders = [...this.orders, ...res]
        }
        
        this.hasMore = res.length === 20
      } catch (e) {
        uni.showToast({
          title: '加载失败',
          icon: 'none'
        })
      } finally {
        this.loading = false
      }
    },
    
    switchTab(tab) {
      this.activeTab = tab
      this.page = 1
      this.orders = []
      this.loadOrders()
    },
    
    loadMore() {
      if (!this.hasMore || this.loading) return
      this.page++
      this.loadOrders()
    },
    
    goToDetail(id) {
      uni.navigateTo({
        url: `/pages/order/detail?id=${id}`
      })
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
    
    getUserRole(order) {
      const userStore = useUserStore()
      if (!userStore.user) return ''
      if (order.renter_id === userStore.user.id) return 'renter'
      if (order.lender_id === userStore.user.id) return 'lender'
      return ''
    },
    
    getUserRoleText(order) {
      const role = this.getUserRole(order)
      const map = { 'renter': '我是租客', 'lender': '我是房东' }
      return map[role] || ''
    },
    
    formatTime(time) {
      if (!time) return ''
      return time.substring(0, 16).replace('T', ' ')
    }
  }
}
</script>

<style>
.container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f5f5;
}

.tabs {
  display: flex;
  background-color: #fff;
  padding: 20rpx;
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 15rpx 0;
  font-size: 28rpx;
  color: #666;
  position: relative;
}

.tab-item.active {
  color: #00D4AA;
  font-weight: bold;
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 60rpx;
  height: 4rpx;
  background-color: #00D4AA;
  border-radius: 2rpx;
}

.order-list {
  flex: 1;
  padding: 20rpx;
}

.order-card {
  background-color: #fff;
  border-radius: 16rpx;
  padding: 25rpx;
  margin-bottom: 20rpx;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.order-no {
  font-size: 24rpx;
  color: #999;
}

.order-status {
  font-size: 24rpx;
  padding: 4rpx 16rpx;
  border-radius: 20rpx;
}

.order-status.PENDING_PAYMENT {
  background-color: #fff7e6;
  color: #ff9f43;
}

.order-status.PAID {
  background-color: #e6f7ff;
  color: #1890ff;
}

.order-status.RETURNED {
  background-color: #f6ffed;
  color: #52c41a;
}

.order-status.COMPLETED {
  background-color: #f5f5f5;
  color: #999;
}

.order-status.DISPUTE {
  background-color: #fff1f0;
  color: #ff4d4f;
}

.order-body {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15rpx 0;
  border-bottom: 1rpx solid #f5f5f5;
}

.product-info {
  flex: 1;
}

.game-name {
  display: block;
  font-size: 26rpx;
  color: #666;
}

.product-title {
  display: block;
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
  margin-top: 5rpx;
}

.order-price {
  text-align: right;
}

.order-price .label {
  display: block;
  font-size: 22rpx;
  color: #999;
}

.order-price .value {
  display: block;
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
}

.order-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 15rpx;
}

.time {
  font-size: 22rpx;
  color: #999;
}

.role-badge {
  font-size: 22rpx;
  padding: 4rpx 12rpx;
  border-radius: 20rpx;
}

.role-badge.renter {
  background-color: #e6f7ff;
  color: #1890ff;
}

.role-badge.lender {
  background-color: #f6ffed;
  color: #52c41a;
}

.loading, .empty {
  text-align: center;
  padding: 40rpx;
  color: #999;
  font-size: 26rpx;
}
</style>
