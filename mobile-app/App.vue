<script>
import { onLaunch } from '@dcloudio/uni-app'
import { useUserStore } from './store/user'

export default {
  onLaunch() {
    // 恢复本地登录态（离线可用，token 持久化于 uni.storage）
    const userStore = useUserStore()
    userStore.restore()
  },
  onShow() {},
  onHide() {}
}
</script>

<style lang="scss">
/* 全局样式见 uni.scss，此处仅做基础兜底 */
page {
  background-color: #f8f5ef;
  font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  font-size: 28rpx;
  color: #3d3529;
}
</style>
