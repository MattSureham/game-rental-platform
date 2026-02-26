<template>
  <view class="container">
    <!-- 商品图片 -->
    <swiper class="product-swiper" indicator-dots autoplay circular>
      <swiper-item v-for="(img, index) in product.images" :key="index">
        <image :src="img" mode="aspectFill" class="slide-image"/>
      </swiper-item>
      <swiper-item v-if="!product.images || product.images.length === 0">
        <image src="/static/default-game.png" mode="aspectFill" class="slide-image"/>
      </swiper-item>
    </swiper>

    <!-- 商品信息 -->
    <view class="product-info">
      <view class="product-header">
        <view class="product-title">{{ product.title }}</view>
        <view class="product-game">{{ product.game_name }}</view>
      </view>
      
      <view class="price-section">
        <view class="price-row">
          <text class="label">时租金</text>
          <text class="price">¥{{ product.hourly_price }}/时</text>
        </view>
        <view class="price-row" v-if="product.daily_price">
          <text class="label">日租金</text>
          <text class="price">¥{{ product.daily_price }}/天</text>
        </view>
        <view class="price-row">
          <text class="label">押金</text>
          <text class="price deposit">¥{{ product.deposit }}</text>
        </view>
      </view>

      <view class="description-section">
        <view class="section-title">商品描述</view>
        <view class="description">{{ product.description || '暂无描述' }}</view>
      </view>

      <view class="owner-section">
        <view class="section-title">卖家信息</view>
        <view class="owner-info">
          <image class="avatar" :src="product.owner && product.owner.avatar_url || '/static/default-avatar.png'" />
          <text class="nickname">{{ product.owner && product.owner.nickname || '匿名卖家' }}</text>
          <text class="credit">信誉: {{ product.owner && product.owner.credit_score || 100 }}分</text>
        </view>
      </view>
    </view>

    <!-- 底部操作栏 -->
    <view class="bottom-bar">
      <view class="bar-left">
        <view class="info-item">
          <text class="label">租金:</text>
          <text class="value">¥{{ rentalAmount }}</text>
        </view>
        <view class="info-item">
          <text class="label">押金:</text>
          <text class="value">¥{{ product.deposit }}</text>
        </view>
      </view>
      <view class="bar-right">
        <button class="rent-btn" @click="goToCreateOrder">立即租用</button>
      </view>
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
      rentalType: 'hourly'
    }
  },
  
  computed: {
    rentalAmount() {
      if (!this.product.hourly_price) return 0
      if (this.rentalType === 'hourly') {
        return (this.product.hourly_price * this.rentalHours).toFixed(2)
      } else {
        return (this.product.daily_price * (this.rentalHours / 24)).toFixed(2)
      }
    }
  },
  
  onLoad(options) {
    this.productId = options.id
    this.loadProduct()
  },
  
  methods: {
    async loadProduct() {
      try {
        uni.showLoading({ title: '加载中' })
        const res = await api.products.detail(this.productId)
        this.product = res
        uni.hideLoading()
      } catch (e) {
        uni.hideLoading()
        uni.showToast({
          title: '加载失败',
          icon: 'none'
        })
      }
    },
    
    goToCreateOrder() {
      const userStore = useUserStore()
      if (!userStore.isLoggedIn) {
        uni.navigateTo({
          url: '/pages/user/profile'
        })
        return
      }
      
      // 检查是否是自己的商品
      if (userStore.user && this.product.owner_id === userStore.user.id) {
        uni.showToast({
          title: '不能租用自己的商品',
          icon: 'none'
        })
        return
      }
      
      uni.navigateTo({
        url: `/pages/order/create?productId=${this.productId}&hours=1`
      })
    }
  }
}
</script>

<style>
.container {
  padding-bottom: 120rpx;
}

.product-swiper {
  width: 100%;
  height: 500rpx;
}

.slide-image {
  width: 100%;
  height: 100%;
}

.product-info {
  padding: 30rpx;
  background-color: #fff;
}

.product-header {
  margin-bottom: 30rpx;
}

.product-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 10rpx;
}

.product-game {
  font-size: 26rpx;
  color: #666;
}

.price-section {
  background-color: #f9f9f9;
  border-radius: 12rpx;
  padding: 20rpx;
  margin-bottom: 30rpx;
}

.price-row {
  display: flex;
  justify-content: space-between;
  padding: 10rpx 0;
}

.price-row .label {
  font-size: 26rpx;
  color: #666;
}

.price-row .price {
  font-size: 30rpx;
  font-weight: bold;
  color: #ff6b6b;
}

.price-row .deposit {
  color: #ff9f43;
}

.description-section, .owner-section {
  margin-bottom: 30rpx;
}

.section-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 15rpx;
}

.description {
  font-size: 26rpx;
  color: #666;
  line-height: 1.6;
}

.owner-info {
  display: flex;
  align-items: center;
  padding: 20rpx;
  background-color: #f9f9f9;
  border-radius: 12rpx;
}

.avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  margin-right: 20rpx;
}

.nickname {
  flex: 1;
  font-size: 28rpx;
  color: #333;
}

.credit {
  font-size: 24rpx;
  color: #00D4AA;
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

.bar-left {
  flex: 1;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 5rpx 0;
}

.info-item .label {
  font-size: 24rpx;
  color: #666;
}

.info-item .value {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
}

.rent-btn {
  background-color: #00D4AA;
  color: #fff;
  font-size: 28rpx;
  padding: 20rpx 60rpx;
  border-radius: 40rpx;
  border: none;
}
</style>
