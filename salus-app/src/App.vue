<template>
  <div class="app-container">
    <el-container>
      <el-aside width="200px" class="sidebar">
        <div class="logo">
          <h2>Salus</h2>
        </div>
        <el-menu
          :router="true"
          :default-active="activeRoute"
          class="sidebar-menu"
          background-color="#001529"
          text-color="#fff"
          active-text-color="#409EFF"
        >
          <el-menu-item index="/">
            <i class="el-icon-s-home"></i>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/dashboard">
            <i class="el-icon-s-marketing"></i>
            <span>仪表盘</span>
          </el-menu-item>
          <el-menu-item index="/tasks">
            <i class="el-icon-date"></i>
            <span>训练任务</span>
          </el-menu-item>
          <el-menu-item index="/exercises">
            <el-icon><Aim /></el-icon>
            <span>运动配置</span>
          </el-menu-item>
          <el-menu-item index="/cycles">
            <el-icon><RefreshRight /></el-icon>
            <span>康复周期</span>
          </el-menu-item>
          <el-menu-item index="/timer">
            <el-icon><Timer /></el-icon>
            <span>Tabata计时器</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header height="60px">
          <div class="header-content">
            <h1>术后康复训练管理系统</h1>
          </div>
        </el-header>
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
// 导入Element Plus图标
import { Aim, RefreshRight, Timer } from '@element-plus/icons-vue'
</script>

<style>
body {
  margin: 0;
  padding: 0;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f7f7f7;
}

.app-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.el-header {
  background-color: #fff;
  color: #333;
  line-height: 60px;
  border-bottom: 1px solid #eee;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
}

.el-aside {
  background-color: #f7f7f7;
  border-right: 1px solid #eee;
}

.sidebar {
  background-color: #001529;
  color: #fff;
}

.logo {
  height: 60px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo h2 {
  color: #fff;
  margin: 0;
  font-size: 24px;
}

.el-aside {
  background-color: #001529;
  border-right: none;
}

.sidebar-menu {
  border-right: none;
}

.el-main {
  padding: 20px;
  background-color: #f7f7f7;
}
</style>