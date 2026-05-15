# Slosh Admin Frontend

基于 Vue 2 + Vite 构建的后台管理前端项目。

## 技术栈

- **框架**: Vue 2.7.16
- **构建工具**: Vite 7.3.3
- **路由**: Vue Router 3.6.5
- **HTTP 客户端**: Axios 1.16.1
- **样式**: CSS3

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

启动后访问: http://localhost:5173

### 生产构建

```bash
npm run build
```

### 预览构建结果

```bash
npm run preview
```

## 环境变量配置

复制 `.env.example` 文件并修改配置：

```bash
cp .env.example .env
```

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| VITE_API_BASE_URL | 后端 API 基础地址 | http://127.0.0.1:8044/api/v1 |

## 项目结构

