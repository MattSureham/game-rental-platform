<template>
  <view class="container">
    <!-- 用户信息头部 -->
    <view class="user-header">
      <view class="user-info" v-if="userInfo">
        <image 
          class="avatar" 
          :src="userInfo.avatar_url || '/static/default-avatar.png'" 
          mode="aspectFill"
        />
        <view class="info">
          <view class="nickname">{{ userInfo.nickname || '未设置昵称' }}</view>
          <view class="credit">信誉分: {{ userInfo.credit_score || 100 }}</view>
        </view>
      </view>
      <view class="login-tip" v-else>
        <text>登录后可享受更多服务</text>
        <button class="login-btn" @click="handleLogin">微信登录</button>
      </view>
    </view>

    <!-- 余额卡片 -->
    <view class="balance-card" v-if="userInfo">
      <view class="balance-item">
        <text class="label">余额</text>
        <text class="value">¥{{ balanceInfo.balance || 0 }}</text>
      </view>
      <view class="balance-actions">
        <button class="action-btn" @click="goToRecharge">充值</button>
        <button class="action-btn outline" @click="goToWithdraw">提现</button>
      </view>
    </view>

    <!-- 功能菜单 -->
    <view class="menu-section" v-if="userInfo">
      <view class="menu-item" @click="goToMyProducts">
        <text class="icon">📦</text>
        <text class="label">我的商品</text>
        <text class="arrow">></text>
      </view>
      <view class="menu-item" @click="goToRenting">
        <text class="icon">🔑</text>
        <text class="label">正在租用</text>
        <text class="arrow">></text>
      </view>
      <view class="menu-item" @click="goToLending">
        <text class="icon">💰</text>
        <text class="label">出租中</text>
        <text class="arrow">></text>
      </view>
    </view>

    <view class="menu-section">
      <view class="menu-item" @click="goToSettings">
        <text class="icon">⚙️</text>
        <text class="label">设置</text>
        <text class="arrow">></text>
      </view>
      <view class="menu-item" @click="goToHelp">
        <text class="icon">❓</text>
        <text class="label">帮助中心</text>
        <text class="arrow">></text>
      </view>
    </view>

    <view class="logout-section" v-if="userInfo">
      <button class="logout-btn" @click="handleLogout">退出登录</button>
    </view>
  </view>
</template>

<script>
import { api } from '@/utils/api.js'
import { useUserStore } from '@/store/user.js'

export default {
  data() {
    return {
      balanceInfo: null
    }
  },
  
  computed: {
    userInfo() {
      const userStore = useUserStore()
      return userStore.user
    }
  },
  
  onShow() {
    if (this.userInfo) {
      this.loadBalance()
    }
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
    
    handleLogin() {
      // 模拟微信登录
      uni.getUserProfile({
        desc: '用于完善用户资料',
        success: (res) => {
          // 获取用户信息成功
          console.log(res)
          // 这里应该调用 uni.login 获取 code，然后调用后端登录
          uni.showLoading({ title: '登录中' })
          
          // 模拟登录
          this.simulateLogin()
        },
        fail: () => {
          // 用户拒绝
          // 模拟登录流程
          this.simulateLogin()
        }
      })
    },
    
    async simulateLogin() {
      const userStore = useUserStore()
      try {
        // 使用模拟的 code 登录
        await userLogin('simulate_code_12345')
        
        uni.hideLoading()
        uni.showToast({
          title: '登录成功',
          icon: 'success'
        })
        
        this.loadBalance()
      } catch (e) {
        uni.hideLoading()
        uni.showToast({
          title: '登录失败',
          icon: 'none'
        })
      }
    },
    
    async userLogin(code) {
      const userStore = useUserStore()
      await userStore.login(code)
    },
    
    handleLogout() {
      uni.showModal({
        title: '提示',
        content: '确定要退出登录吗？',
        success: (res) => {
          if (res.confirm) {
            const userStore = useUserStore()
            userStore.logout()
            uni.showToast({
              title: '已退出',
              icon: 'success'
            })
          }
        }
      })
    },
    
    goToRecharge() {
      uni.navigateTo({
        url: '/pages/user/wallet?type=recharge'
      })
    },
    
    goToWithdraw() {
      uni.navigateTo({
        url: '/pages/user/wallet?type=withdraw'
      })
    },
    
    goToMyProducts() {
      uni.switchTab({
        url: '/pages/index/index'
      })
    },
    
    goToRenting() {
      uni.navigateTo({
        url: '/pages/order/list?tab=renting'
      })
    },
    
    goToLending() {
      uni.navigateTo({
        url: '/pages/order/list?tab=lending'
      })
    },
    
    goToSettings() {
      uni.navigateTo({
        url: '/pages/user/settings'
      })
    },
    
    goToHelp() {
      uni.showToast({
        title: '帮助中心开发中',
        icon: 'none'
      })
    }
  }
}
</script>

<style>
.container {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.user-header {
  background: linear-gradient(135deg, #00D4AA, #00B894);
  padding: 60rpx 30rpx;
}

.user-info {
  display: flex;
  align-items: center;
}

.avatar {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  border: 4rpx solid #fff;
}

.info {
  margin-left: 30rpx;
}

.nickname {
  font-size: 36rpx;
  font-weight: bold;
  color: #fff;
  margin-bottom: 10rpx;
}

.credit {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.9);
}

.login-tip {
  text-align: center;
}

.login-tip text {
  display: block;
  color: #fff;
  font-size: 28rpx;
  margin-bottom: 30rpx;
}

.login-btn {
  background-color: #fff;
  color: #00D4AA;
  font-size: 28rpx;
  padding: 20rpx 60rpx;
  border-radius: 40rpx;
  border: none;
}

.balance-card {
  background-color: #fff;
  margin: -30rpx 30rpx 30rpx;
  border-radius: 16rpx;
  padding: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.1);
}

.balance-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.balance-item .label {
  font-size: 28rpx;
  color: #666;
}

.balance-item .value {
  font-size: 48rpx;
  font-weight: bold;
  color: #ff6b6b;
}

.balance-actions {
  display: flex;
  gap: 20rpx;
}

.action-btn {
  flex: 1;
  height: 70rpx;
  background-color: #00D4AA;
  color: #fff;
  font-size: 26rpx;
  border-radius: 35rpx;
  border: none;
}

.action-btn.outline {
  background-color: #fff;
  color: #00D4AA;
  border: 2rpx solid #00D4AA;
}

.menu-section {
  background-color: #fff;
  margin: 20rpx;
  border-radius: 16rpx;
  overflow: hidden;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1rpx solid #f5f5f5;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item .icon {
  font-size: 40rpx;
  margin-right: 20rpx;
}

.menu-item .label {
  flex: 1;
  font-size: 28rpx;
  color: #333;
}

.menu-item .arrow {
  color: #ccc;
  font-size: 28rpx;
}

.logout-section {
  padding: 40rpx 30rpx;
}

.logout-btn {
  width: 100%;
  height: 80rpx;
  background-color: #fff;
  color: #ff6b6b;
  font-size: 28rpx;
  border-radius: 40rpx;
  border: none;
}
</style>
