<script>
export default {
  onLaunch: function() {
    console.log('App Launch')
    // 检查登录状态
    this.checkLogin()
  },
  methods: {
    checkLogin() {
      const token = uni.getStorageSync('token')
      if (token) {
        // 验证token有效性
        this.$api.auth.getProfile()
          .then(res => {
            this.$store.commit('setUser', res.data)
          })
          .catch(() => {
            this.logout()
          })
      }
    },
    logout() {
      uni.removeStorageSync('token')
      uni.removeStorageSync('user')
      this.$store.commit('setUser', null)
    }
  }
}
</script>

<style>
@import '@/uni.scss';

page {
  background-color: #f5f5f5;
}
</style>
