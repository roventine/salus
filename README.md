# Salus - 术后AI康复助手

Salus 是一个专为术后康复训练设计系统，帮助用户规划和管理术后康复训练，提高康复效率。

## 项目结构

项目由两部分组成：

- `salus-api`: 后端 API 服务，基于 Python 开发
- `salus-app`: 前端应用，基于 Vue.js 开发

## 功能特点

- 康复周期管理：创建和管理康复训练周期
- 训练任务管理：安排和跟踪日常训练任务
- 运动类型配置：自定义不同类型的康复运动
- Tabata 计时器：辅助训练的计时工具
- 数据统计与可视化：查看康复进度和统计数据
- 批量配置：快速为多个时间段配置训练计划

## 技术栈

### 前端
- Vue.js
- Element Plus UI 组件库
- ECharts 数据可视化
- Axios HTTP 客户端

### 后端
- Python
- Flask Web 框架
- SQLite 数据库

## 安装与运行

### 后端 API

```bash
# 进入后端目录
cd salus-api

# 创建并激活虚拟环境
python -m venv .venv
.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行应用
python app.py
```

### 前端应用
```
# 进入前端目录
cd salus-app

# 安装依赖
npm install

# 开发模式运行
npm run dev

# 构建生产版本
npm run build
```