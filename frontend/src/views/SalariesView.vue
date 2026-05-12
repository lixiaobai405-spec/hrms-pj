<template>
  <div class="page">
    <el-card>
      <template #header>
        <div class="header">
          <div class="title">薪资管理</div>
          <div class="right">
            <el-button type="primary" @click="openCreate">+ 新增薪资</el-button>
            <el-button @click="loadAll">刷新</el-button>
          </div>
        </div>
      </template>

      <!-- 筛选区 -->
      <el-form :inline="true" class="filters">
        <el-form-item label="月份">
          <el-date-picker
            v-model="q.month"
            type="month"
            value-format="YYYY-MM"
            placeholder="选择月份"
            @change="onMonthChange"
          />
        </el-form-item>

        <el-form-item label="部门">
          <el-select v-model="q.dept_id" clearable placeholder="全部" style="width: 200px">
            <el-option v-for="d in departments" :key="d.dept_id" :label="d.dept_name" :value="d.dept_id" />
          </el-select>
        </el-form-item>

        <el-form-item label="员工">
          <el-select v-model="q.emp_id" clearable placeholder="全部" style="width: 200px">
            <el-option
              v-for="e in employeesForSelect"
              :key="e.emp_id"
              :label="`${e.emp_no} ${e.emp_name}`"
              :value="e.emp_id"
            />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="onSearch">查询</el-button>
          <el-button @click="onReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格 -->
      <el-table :data="pagedRows" v-loading="loading" border>
        <el-table-column prop="salary_id" label="ID" width="80" />
        <el-table-column label="员工" width="220">
          <template #default="{ row }">{{ empLabel(row.emp_id) }}</template>
        </el-table-column>
        <el-table-column label="部门" width="160">
          <template #default="{ row }">{{ deptLabelByEmp(row.emp_id) }}</template>
        </el-table-column>
        <el-table-column prop="salary_month" label="月份" width="110" />
        <el-table-column prop="base_salary" label="基本工资" width="120" />
        <el-table-column prop="bonus" label="奖金" width="100" />
        <el-table-column prop="allowance" label="补贴" width="100" />
        <el-table-column prop="deduction" label="扣款" width="100" />
        <el-table-column prop="net_salary" label="实发" width="120" />

        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-popconfirm title="确认删除该薪资记录？" @confirm="deleteSalary(row.salary_id)">
              <template #reference>
                <el-button size="small" type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pager">
        <el-pagination
          background
          layout="prev, pager, next, sizes, total"
          :total="filteredRows.length"
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
        />
      </div>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dlgOpen" :title="form.salary_id ? '编辑薪资' : '新增薪资'" width="560px">
      <el-form :model="form" label-width="110px">
        <el-form-item label="员工">
          <el-select v-model="form.emp_id" :disabled="!!form.salary_id" placeholder="请选择" style="width: 260px">
            <el-option v-for="e in employees" :key="e.emp_id" :label="`${e.emp_no} ${e.emp_name}`" :value="e.emp_id" />
          </el-select>
        </el-form-item>

        <el-form-item label="月份">
          <el-date-picker
            v-model="form.salary_month"
            type="month"
            value-format="YYYY-MM"
            :disabled="!!form.salary_id"
            placeholder="YYYY-MM"
          />
        </el-form-item>

        <el-form-item label="基本工资">
          <el-input-number v-model="form.base_salary" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="奖金">
          <el-input-number v-model="form.bonus" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="补贴">
          <el-input-number v-model="form.allowance" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="扣款">
          <el-input-number v-model="form.deduction" :min="0" :precision="2" />
        </el-form-item>

        <el-alert
          type="info"
          show-icon
          title="提示：同一员工同一月份只能录入一条薪资记录（数据库唯一约束）。"
          :closable="false"
        />
      </el-form>

      <template #footer>
        <el-button @click="dlgOpen=false">取消</el-button>
        <el-button type="primary" @click="submit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import http from "../api/http";
import { ElMessage } from "element-plus";

const loading = ref(false);
const salaries = ref<any[]>([]);
const employees = ref<any[]>([]);
const departments = ref<any[]>([]);

// 筛选条件
const q = reactive<{ month: string; emp_id: number | null; dept_id: number | null }>({
  month: currentMonth(),
  emp_id: null,
  dept_id: null,
});

// 分页
const page = ref(1);
const pageSize = ref(10);

watch([() => q.month, () => q.emp_id, () => q.dept_id], () => {
  page.value = 1;
});

function currentMonth() {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  return `${y}-${m}`;
}

function empLabel(emp_id: number) {
  const e = employees.value.find((x) => x.emp_id === emp_id);
  return e ? `${e.emp_no} ${e.emp_name}` : `#${emp_id}`;
}

/**
 * 根据员工ID查找其部门名称（用于表格展示/筛选）。
 * @param emp_id 员工ID
 * @returns 部门名称（找不到则返回“-”）
 */
function deptLabelByEmp(emp_id: number) {
  const e = employees.value.find((x) => x.emp_id === emp_id);
  if (!e?.dept_id) return "-";
  return departments.value.find((d) => d.dept_id === e.dept_id)?.dept_name ?? `#${e.dept_id}`;
}

/**
 * 筛选区员工下拉：当选择了部门时，仅展示该部门员工，便于定位录入。
 */
const employeesForSelect = computed(() => {
  if (!q.dept_id) return employees.value;
  return employees.value.filter((e) => e.dept_id === q.dept_id);
});

const filteredRows = computed(() => {
  return salaries.value.filter((s) => {
    if (q.month && s.salary_month !== q.month) return false;
    if (q.emp_id && s.emp_id !== q.emp_id) return false;
    if (q.dept_id) {
      const e = employees.value.find((x) => x.emp_id === s.emp_id);
      if (!e || e.dept_id !== q.dept_id) return false;
    }
    return true;
  });
});

const pagedRows = computed(() => {
  const start = (page.value - 1) * pageSize.value;
  return filteredRows.value.slice(start, start + pageSize.value);
});

async function loadAll() {
  loading.value = true;
  try {
    const [dRes, eRes, sRes] = await Promise.all([http.get("/departments"), http.get("/employees"), http.get("/salaries")]);
    departments.value = dRes.data;
    employees.value = eRes.data;
    salaries.value = sRes.data;
  } finally {
    loading.value = false;
  }
}

function onMonthChange() {
  page.value = 1;
}
function onSearch() {
  page.value = 1;
}
function onReset() {
  q.month = currentMonth();
  q.emp_id = null;
  q.dept_id = null;
  page.value = 1;
}

// 弹窗表单
const dlgOpen = ref(false);
const form = reactive<any>({
  salary_id: null,
  emp_id: null,
  salary_month: "",
  base_salary: 0,
  bonus: 0,
  allowance: 0,
  deduction: 0,
});

function openCreate() {
  Object.assign(form, {
    salary_id: null,
    emp_id: employees.value[0]?.emp_id ?? null,
    salary_month: q.month || currentMonth(),
    base_salary: 0,
    bonus: 0,
    allowance: 0,
    deduction: 0,
  });
  dlgOpen.value = true;
}

function openEdit(row: any) {
  Object.assign(form, {
    salary_id: row.salary_id,
    emp_id: row.emp_id,
    salary_month: row.salary_month,
    base_salary: Number(row.base_salary ?? 0),
    bonus: Number(row.bonus ?? 0),
    allowance: Number(row.allowance ?? 0),
    deduction: Number(row.deduction ?? 0),
  });
  dlgOpen.value = true;
}

async function submit() {
  if (!form.emp_id) return ElMessage.warning("请选择员工");
  if (!form.salary_month) return ElMessage.warning("请选择月份");

  try {
    if (form.salary_id) {
      await http.put(`/salaries/${form.salary_id}`, {
        base_salary: form.base_salary,
        bonus: form.bonus,
        allowance: form.allowance,
        deduction: form.deduction,
      });
      ElMessage.success("更新成功");
    } else {
      await http.post("/salaries", {
        emp_id: form.emp_id,
        salary_month: form.salary_month,
        base_salary: form.base_salary,
        bonus: form.bonus,
        allowance: form.allowance,
        deduction: form.deduction,
      });
      ElMessage.success("新增成功");
    }
    dlgOpen.value = false;
    await loadAll();
  } catch (e: any) {
    // 提示：错误提示已在 src/api/http.ts 的响应拦截器中统一处理
  }
}

async function deleteSalary(salary_id: number) {
  await http.delete(`/salaries/${salary_id}`);
  ElMessage.success("删除成功");
  await loadAll();
}

onMounted(loadAll);
</script>

<style scoped>
.page { padding: 16px; background: #f5f7fb; min-height: 100vh; }
.header { display: flex; align-items: center; justify-content: space-between; }
.title { font-size: 18px; font-weight: 600; color: #1f2937; }
.right { display: flex; gap: 10px; }
.filters { margin-bottom: 12px; }
.pager { display: flex; justify-content: flex-end; margin-top: 12px; }
</style>
