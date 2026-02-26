# 后端配置文件
# 开发环境配置

# 服务器配置
HOST = "0.0.0.0"
PORT = 8000

# 数据库配置
DATABASE_URL = "sqlite:///./game_rental.db"
# 生产环境使用 MySQL:
# DATABASE_URL = "mysql+pymysql://user:password@localhost:3306/game_rental"

# JWT 配置
SECRET_KEY = "your-secret-key-change-in-production-please-use-env-variable"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天

# 微信配置 (需要替换为真实配置)
WECHAT_APPID = "your_wechat_appid"
WECHAT_SECRET = "your_wechat_secret"

# 佣金配置
COMMISSION_RATE = 0.10  # 10%

# 验号期限 (小时)
VERIFY_DEADLINE_HOURS = 48

# 加密配置
ENCRYPTION_KEY = "your-32-byte-encryption-key-here"
