<template>
  <el-container class="root">
    <!-- 侧边栏 -->
    <el-aside class="aside" width="220px">
      <div class="brand">
        <div class="logo">HR</div>
        <div class="name">人力资源管理系统</div>
      </div>

      <el-menu
        :default-active="activePath"
        class="menu"
        router
      >
        <el-menu-item index="/">
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/employees">
          <span>员工管理</span>
        </el-menu-item>
        <el-menu-item index="/org">
          <span>组织架构</span>
        </el-menu-item>
        <el-menu-item index="/salaries">
          <span>薪资管理</span>
        </el-menu-item>
        <el-menu-item index="/attendance">
          <span>考勤管理</span>
        </el-menu-item>
        <el-menu-item index="/reports">
          <span>统计报表</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <!-- 顶部栏 -->
      <el-header class="header">
        <div class="header-left">
          <div class="page-title">{{ pageTitle }}</div>
        </div>
        <div class="header-right">
          <el-tag type="info">dev</el-tag>
          <div class="user">hrms_user</div>
        </div>
      </el-header>

      <!-- 主内容 -->
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();
const activePath = computed(() => route.path);

const pageTitle = computed(() => {
  switch (route.path) {
    case "/":
      return "仪表盘";
    case "/employees":
      return "员工管理";
    case "/org":
      return "组织架构";
    case "/salaries":
      return "薪资管理";
    case "/attendance":
      return "考勤管理";
    case "/reports":
      return "统计报表";
    default:
      return "";
  }
});
</script>

<style scoped>
.root {
  height: 100vh;
  background: #f5f7fb;
}

.aside {
  background: #ffffff;
  border-right: 1px solid #e6eaf2;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  height: 56px;
  padding: 0 14px;
  border-bottom: 1px solid #e6eaf2;
}

.logo {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  background: #2f6bff;
  color: #fff;
  display: grid;
  place-items: center;
  font-weight: 700;
}

.name {
  font-weight: 700;
  color: #1f2937;
  font-size: 14px;
}

.menu {
  border-right: none;
}

.header {
  background: rgba(255, 255, 255, 0.92);
  border-bottom: 1px solid #e6eaf2;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.page-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user {
  color: #6b7280;
  font-size: 13px;
}

.main {
  padding: 0;
  background: #f5f7fb;
}
</style>