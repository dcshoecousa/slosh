# 第一阶段：构建阶段
FROM node:20-alpine AS builder

# 设置工作目录
WORKDIR /app

# 复制 package.json 和 package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm ci --only=production

# 复制项目文件
COPY . .

# 构建生产版本
RUN npm run build

# 第二阶段：生产阶段（使用 nginx 作为静态文件服务器）
FROM nginx:1.25-alpine

# 复制 nginx 配置文件
COPY nginx.conf /etc/nginx/nginx.conf

# 复制构建产物到 nginx 静态目录
COPY --from=builder /app/dist /usr/share/nginx/html

# 暴露端口
EXPOSE 80

# 启动 nginx
CMD ["nginx", "-g", "daemon off;"]
