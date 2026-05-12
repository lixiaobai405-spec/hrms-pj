<template>
  <div class="page">
    <el-card>
      <template #header>
        <div class="header">
          <div class="title">统计报表</div>
          <div class="right">
            <el-form :inline="true">
              <el-form-item label="月份">
                <el-date-picker v-model="month" type="month" value-format="YYYY-MM" @change="loadAll" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="loadAll">刷新</el-button>
              </el-form-item>
            </el-form>
          </div>
        </div>
      </template>

      <el-row :gutter="12">
        <!-- 部门人数 -->
        <el-col :span="12">
          <el-card class="inner" shadow="never">
            <template #header><div class="inner-title">各部门在职人数</div></template>
            <div ref="deptCountChartRef" class="chart"></div>
            <el-table :data="deptCountRows" size="small" border style="margin-top:12px">
              <el-table-column prop="dept_name" label="部门" />
              <el-table-column prop="emp_count" label="人数" width="90" />
            </el-table>
          </el-card>
        </el-col>

        <!-- 部门薪资汇总 -->
        <el-col :span="12">
          <el-card class="inner" shadow="never">
            <template #header><div class="inner-title">部门月度薪资汇总（{{ month }}）</div></template>
            <div ref="deptSalaryChartRef" class="chart"></div>
            <el-table :data="deptSalaryRows" size="small" border style="margin-top:12px">
              <el-table-column prop="dept_name" label="部门" />
              <el-table-column prop="total_salary" label="总薪资" width="120" />
            </el-table>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="12" style="margin-top:12px">
        <!-- 迟到TopN -->
        <el-col :span="24">
          <el-card class="inner" shadow="never">
            <template #header><div class="inner-title">月度迟到次数 TopN（{{ month }}）</div></template>
            <div ref="lateTopChartRef" class="chart"></div>
            <el-table :data="lateTopRows" size="small" border style="margin-top:12px">
              <el-table-column prop="emp_name" label="员工" />
              <el-table-column prop="late_times" label="迟到次数" width="120" />
            </el-table>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";
import http from "../api/http";
import * as echarts from "echarts";

function currentMonth() {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  return `${y}-${m}`;
}

const month = ref(currentMonth());

// 数据
const deptCountRows = ref<any[]>([]);
const deptSalaryRows = ref<any[]>([]);
const lateTopRows = ref<any[]>([]);

// 图表容器
const deptCountChartRef = ref<HTMLDivElement | null>(null);
const deptSalaryChartRef = ref<HTMLDivElement | null>(null);
const lateTopChartRef = ref<HTMLDivElement | null>(null);

let deptCountChart: echarts.ECharts | null = null;
let deptSalaryChart: echarts.ECharts | null = null;
let lateTopChart: echarts.ECharts | null = null;

function renderDeptCount() {
  if (!deptCountChartRef.value) return;
  deptCountChart = deptCountChart ?? echarts.init(deptCountChartRef.value);
  const x = deptCountRows.value.map((r) => r.dept_name);
  const y = deptCountRows.value.map((r) => r.emp_count);

  deptCountChart.setOption({
    grid: { left: 40, right: 20, top: 30, bottom: 40 },
    xAxis: { type: "category", data: x, axisLabel: { rotate: 20 } },
    yAxis: { type: "value" },
    tooltip: { trigger: "axis" },
    series: [{ type: "bar", data: y, itemStyle: { color: "#2F6BFF", borderRadius: [6, 6, 0, 0] } }],
  });
}

function renderDeptSalary() {
  if (!deptSalaryChartRef.value) return;
  deptSalaryChart = deptSalaryChart ?? echarts.init(deptSalaryChartRef.value);
  const x = deptSalaryRows.value.map((r) => r.dept_name);
  const y = deptSalaryRows.value.map((r) => Number(r.total_salary));

  deptSalaryChart.setOption({
    grid: { left: 50, right: 20, top: 30, bottom: 40 },
    xAxis: { type: "category", data: x, axisLabel: { rotate: 20 } },
    yAxis: { type: "value" },
    tooltip: { trigger: "axis" },
    series: [{ type: "bar", data: y, itemStyle: { color: "#16A34A", borderRadius: [6, 6, 0, 0] } }],
  });
}

function renderLateTop() {
  if (!lateTopChartRef.value) return;
  lateTopChart = lateTopChart ?? echarts.init(lateTopChartRef.value);
  const y = lateTopRows.value.map((r) => r.emp_name);
  const x = lateTopRows.value.map((r) => r.late_times);

  lateTopChart.setOption({
    grid: { left: 80, right: 20, top: 20, bottom: 30 },
    xAxis: { type: "value" },
    yAxis: { type: "category", data: y },
    tooltip: { trigger: "axis" },
    series: [{ type: "bar", data: x, itemStyle: { color: "#F59E0B", borderRadius: [0, 6, 6, 0] } }],
  });
}

async function loadAll() {
  const [cRes, sRes, lRes] = await Promise.all([
    http.get("/stats/dept-employee-count"),
    http.get("/stats/dept-salary-total", { params: { month: month.value } }),
    http.get("/stats/late-top", { params: { month: month.value } }),
  ]);
  deptCountRows.value = cRes.data;
  deptSalaryRows.value = sRes.data;
  lateTopRows.value = lRes.data;

  renderDeptCount();
  renderDeptSalary();
  renderLateTop();
}

function handleResize() {
  deptCountChart?.resize();
  deptSalaryChart?.resize();
  lateTopChart?.resize();
}

onMounted(async () => {
  await loadAll();
  window.addEventListener("resize", handleResize);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", handleResize);
  deptCountChart?.dispose();
  deptSalaryChart?.dispose();
  lateTopChart?.dispose();
});
</script>

<style scoped>
.page { padding: 16px; background: #f5f7fb; min-height: 100vh; }
.header { display: flex; align-items: center; justify-content: space-between; }
.title { font-size: 18px; font-weight: 600; color: #1f2937; }
.right { display: flex; align-items: center; }
.inner-title { font-weight: 600; color: #1f2937; }
.inner { border: 1px solid #e6eaf2; border-radius: 12px; }
.chart { width: 100%; height: 280px; }
</style>
