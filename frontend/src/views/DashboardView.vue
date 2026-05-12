<template>
  <div class="page">
    <el-card>
      <template #header>
        <div class="title">仪表盘</div>
      </template>

      <div class="row">
        <div>后端健康检查：</div>
        <el-tag v-if="loading" type="info">请求中...</el-tag>
        <el-tag v-else-if="ok" type="success">OK</el-tag>
        <el-tag v-else type="danger">失败</el-tag>
      </div>

      <pre class="box">{{ data }}</pre>

      <el-button type="primary" @click="fetchHealth">重新请求</el-button>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import http from "../api/http";

const loading = ref(false);
const ok = ref(false);
const data = ref<any>(null);

async function fetchHealth() {
  loading.value = true;
  try {
    const res = await http.get("/health");
    data.value = res.data;
    ok.value = true;
  } catch (e: any) {
    ok.value = false;
    data.value = { error: String(e) };
  } finally {
    loading.value = false;
  }
}

onMounted(fetchHealth);
</script>

<style scoped>
.page { padding: 16px; background: #f5f7fb; min-height: calc(100vh - 0px); }
.title { font-weight: 600; }
.row { display: flex; gap: 12px; align-items: center; margin-bottom: 12px; }
.box { background: #0b1020; color: #e5e7eb; padding: 12px; border-radius: 8px; overflow: auto; }
</style>
