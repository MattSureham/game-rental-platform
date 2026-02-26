<template>
  <view class="container">
    <!-- 搜索栏 -->
    <view class="search-bar">
      <view class="search-input">
        <text class="icon">🔍</text>
        <input 
          v-model="keyword" 
          placeholder="搜索游戏账号" 
          @confirm="handleSearch"
        />
      </view>
    </view>

    <!-- 分类筛选 -->
    <scroll-view class="category-scroll" scroll-x>
      <view 
        class="category-item" 
        :class="{ active: !category }"
        @click="selectCategory('')"
      >
        全部
      </view>
      <view 
        v-for="cat in categories" 
        :key="cat.id"
        class="category-item"
        :class="{ active: category === cat.name }"
        @click="selectCategory(cat.name)"
      >
        {{ cat.name }}
      </view>
    </scroll-view>

    <!-- 商品列表 -->
    <scroll-view 
      class="product-list" 
      scroll-y 
      @scrolltolower="loadMore"
    >
      <view class="product-grid">
        <view 
          v-for="item in products" 
          :key="item.id"
          class="product-card"
          @click="goToDetail(item.id)"
        >
          <image 
            class="product-image" 
            :src="item.images && item.images[0] ? item.images[0] : '/static/default-game.png'" 
            mode="aspectFill"
          />
          <view class="product-info">
            <view class="product-title">{{ item.title }}</view>
            <view class="product-game">{{ item.game_name }}</view>
            <view class="product-price">
              <text class="price">¥{{ item.hourly_price }}/时</text>
              <text class="deposit">押金: ¥{{ item.deposit }}</text>
            </view>
          </view>
          <view class="product-status" :class="item.status">
            {{ getStatusText(item.status) }}
          </view>
        </view>
      </view>
      
      <view v-if="loading" class="loading">
        <text>加载中...</text>
      </view>
      
      <view v-if="!loading && products.length === 0" class="empty">
        <text>暂无商品</text>
      </view>
    </scroll-view>
  </view>
</template>

<script>
import { api } from '@/utils/api.js'

export default {
  data() {
    return {
      keyword: '',
      category: '',
      categories: [],
      products: [],
      page: 1,
      loading: false,
      hasMore: true
    }
  },
  
  onLoad() {
    this.loadCategories()
    this.loadProducts()
  },
  
  onShow() {
    // 刷新商品列表
    this.page = 1
    this.products = []
    this.loadProducts()
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
    
    async loadProducts() {
      if (this.loading) return
      this.loading = true
      
      try {
        const res = await api.products.list({
          category: this.category,
          keyword: this.keyword,
          page: this.page,
          page_size: 20
        })
        
        if (this.page === 1) {
          this.products = res
        } else {
          this.products = [...this.products, ...res]
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
    
    handleSearch() {
      this.page = 1
      this.products = []
      this.loadProducts()
    },
    
    selectCategory(cat) {
      this.category = cat
      this.page = 1
      this.products = []
      this.loadProducts()
    },
    
    loadMore() {
      if (!this.hasMore || this.loading) return
      this.page++
      this.loadProducts()
    },
    
    goToDetail(id) {
      uni.navigateTo({
        url: `/pages/product/detail?id=${id}`
      })
    },
    
    getStatusText(status) {
      const map = {
        'available': '可租',
        'rented': '租用中',
        'offline': '已下架'
      }
      return map[status] || status
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

.search-bar {
  padding: 20rpx 30rpx;
  background-color: #fff;
}

.search-input {
  display: flex;
  align-items: center;
  background-color: #f5f5f5;
  border-radius: 40rpx;
  padding: 15rpx 30rpx;
}

.search-input .icon {
  margin-right: 15rpx;
}

.search-input input {
  flex: 1;
  font-size: 28rpx;
}

.category-scroll {
  white-space: nowrap;
  background-color: #fff;
  padding: 0 20rpx 20rpx;
}

.category-item {
  display: inline-block;
  padding: 10rpx 30rpx;
  margin-right: 20rpx;
  font-size: 26rpx;
  color: #666;
  background-color: #f5f5f5;
  border-radius: 30rpx;
}

.category-item.active {
  background-color: #00D4AA;
  color: #fff;
}

.product-list {
  flex: 1;
  padding: 20rpx;
}

.product-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
}

.product-card {
  width: calc(50% - 10rpx);
  background-color: #fff;
  border-radius: 16rpx;
  overflow: hidden;
  position: relative;
}

.product-image {
  width: 100%;
  height: 240rpx;
  background-color: #eee;
}

.product-info {
  padding: 20rpx;
}

.product-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-game {
  font-size: 24rpx;
  color: #999;
  margin: 8rpx 0;
}

.product-price {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.product-price .price {
  font-size: 28rpx;
  color: #ff6b6b;
  font-weight: bold;
}

.product-price .deposit {
  font-size: 22rpx;
  color: #999;
}

.product-status {
  position: absolute;
  top: 10rpx;
  right: 10rpx;
  padding: 4rpx 16rpx;
  font-size: 20rpx;
  border-radius: 20rpx;
  background-color: rgba(0, 0, 0, 0.5);
  color: #fff;
}

.product-status.available {
  background-color: #00D4AA;
}

.product-status.rented {
  background-color: #ff6b6b;
}

.loading, .empty {
  text-align: center;
  padding: 40rpx;
  color: #999;
  font-size: 26rpx;
}
</style>
