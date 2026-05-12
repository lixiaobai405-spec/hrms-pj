<template>
  <div class="page">
    <el-card>
      <template #header>
        <div class="header">
          <div class="title">员工管理</div>
          <div class="right">
            <el-button type="primary" @click="openCreate">+ 新增员工</el-button>
            <el-button @click="loadAll">刷新</el-button>
          </div>
        </div>
      </template>

      <!-- 筛选区 -->
      <el-form :inline="true" class="filters">
        <el-form-item label="部门">
          <el-select v-model="q.dept_id" clearable placeholder="全部">
            <el-option v-for="d in departments" :key="d.dept_id" :label="d.dept_name" :value="d.dept_id" />
          </el-select>
        </el-form-item>

        <el-form-item label="岗位">
          <el-select v-model="q.pos_id" clearable placeholder="全部">
            <el-option v-for="p in positions" :key="p.pos_id" :label="p.pos_name" :value="p.pos_id" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="q.status" clearable placeholder="全部">
            <el-option label="在职" :value="1" />
            <el-option label="离职" :value="2" />
            <el-option label="试用" :value="3" />
          </el-select>
        </el-form-item>

        <el-form-item label="关键字">
          <el-input
            v-model="q.keyword"
            clearable
            placeholder="姓名/工号"
            @keyup.enter="onSearch"
            style="width: 220px"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="onSearch">查询</el-button>
          <el-button @click="onReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格 -->
      <el-table :data="pagedRows" v-loading="loading" border>
        <el-table-column prop="emp_id" label="ID" width="80" />
        <el-table-column prop="emp_no" label="工号" width="120" />
        <el-table-column prop="emp_name" label="姓名" width="140" />
        <el-table-column label="部门" width="160">
          <template #default="{ row }">{{ deptName(row.dept_id) }}</template>
        </el-table-column>
        <el-table-column label="岗位" width="160">
          <template #default="{ row }">{{ posName(row.pos_id) }}</template>
        </el-table-column>
        <el-table-column prop="hire_date" label="入职日期" width="130" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" plain @click="openDetail(row)">详情</el-button>
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-popconfirm title="确认删除该员工？" @confirm="deleteEmployee(row.emp_id)">
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
    <el-dialog v-model="dlgOpen" :title="form.emp_id ? '编辑员工' : '新增员工'" width="520px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="工号">
          <el-input v-model="form.emp_no" :disabled="!!form.emp_id" placeholder="如：E1003" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="form.emp_name" placeholder="如：ZhangSan" />
        </el-form-item>
        <el-form-item label="性别">
          <el-select v-model="form.gender" clearable placeholder="可选">
            <el-option label="男" :value="1" />
            <el-option label="女" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="form.phone" clearable />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" clearable />
        </el-form-item>
        <el-form-item label="部门">
          <el-select v-model="form.dept_id" placeholder="请选择">
            <el-option v-for="d in departments" :key="d.dept_id" :label="d.dept_name" :value="d.dept_id" />
          </el-select>
        </el-form-item>
        <el-form-item label="岗位">
          <el-select v-model="form.pos_id" placeholder="请选择">
            <el-option v-for="p in positions" :key="p.pos_id" :label="p.pos_name" :value="p.pos_id" />
          </el-select>
        </el-form-item>
        <el-form-item label="入职日期">
          <el-date-picker v-model="form.hire_date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status">
            <el-option label="在职" :value="1" />
            <el-option label="离职" :value="2" />
            <el-option label="试用" :value="3" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dlgOpen=false">取消</el-button>
        <el-button type="primary" @click="submit">保存</el-button>
      </template>
    </el-dialog>

    <!-- 详情抽屉（Drawer） -->
    <el-drawer v-model="detailOpen" title="员工详情" direction="rtl" size="420px">
      <div v-if="detailRow" class="drawer-body">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="工号">{{ detailRow.emp_no }}</el-descriptions-item>
          <el-descriptions-item label="姓名">{{ detailRow.emp_name }}</el-descriptions-item>
          <el-descriptions-item label="部门">{{ deptName(detailRow.dept_id) }}</el-descriptions-item>
          <el-descriptions-item label="岗位">{{ posName(detailRow.pos_id) }}</el-descriptions-item>
          <el-descriptions-item label="入职日期">{{ detailRow.hire_date }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ statusText(detailRow.status) }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ detailRow.phone || "-" }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ detailRow.email || "-" }}</el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">最近 5 条薪资（可选加分）</el-divider>
        <el-table :data="recentSalaries" size="small" border v-loading="detailLoading">
          <el-table-column prop="salary_month" label="月份" width="110" />
          <el-table-column prop="net_salary" label="实发" width="110" />
          <el-table-column prop="base_salary" label="基本" width="110" />
        </el-table>

        <el-divider content-position="left">最近 5 条考勤（可选加分）</el-divider>
        <el-table :data="recentAttendance" size="small" border v-loading="detailLoading">
          <el-table-column prop="att_date" label="日期" width="120" />
          <el-table-column prop="att_status" label="状态" width="110">
            <template #default="{ row }">{{ row?.att_status ? statusTextFromAtt(row.att_status) : "-" }}</template>
          </el-table-column>
          <el-table-column prop="remark" label="备注" />
        </el-table>
      </div>
      <div v-else class="drawer-body">
        <el-empty description="请选择员工查看详情" />
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import http from "../api/http";
import { ElMessage } from "element-plus";

const loading = ref(false);
const employees = ref<any[]>([]);
const departments = ref<any[]>([]);
const positions = ref<any[]>([]);

// 查询条件
const q = reactive<{ dept_id: number | null; pos_id: number | null; status: number | null; keyword: string }>({
  dept_id: null,
  pos_id: null,
  status: null,
  keyword: "",
});

// 分页
const page = ref(1);
const pageSize = ref(10);

watch([() => q.dept_id, () => q.pos_id, () => q.status, () => q.keyword], () => {
  page.value = 1; // 筛选变化重置页码
});

function deptName(id: number) {
  return departments.value.find((d) => d.dept_id === id)?.dept_name ?? `#${id}`;
}
function posName(id: number) {
  return positions.value.find((p) => p.pos_id === id)?.pos_name ?? `#${id}`;
}
function statusText(v: number) {
  return v === 1 ? "在职" : v === 2 ? "离职" : "试用";
}
function statusTagType(v: number) {
  return v === 1 ? "success" : v === 2 ? "info" : "warning";
}

/**
 * 将考勤状态数值转换为文本。
 * @param v 考勤状态：1正常/2迟到/3早退/4缺勤
 * @returns 状态文本
 */
function statusTextFromAtt(v: number) {
  return v === 1 ? "正常" : v === 2 ? "迟到" : v === 3 ? "早退" : "缺勤";
}

const filteredRows = computed(() => {
  const kw = q.keyword.trim().toLowerCase();
  return employees.value.filter((e) => {
    if (q.dept_id && e.dept_id !== q.dept_id) return false;
    if (q.pos_id && e.pos_id !== q.pos_id) return false;
    if (q.status && e.status !== q.status) return false;
    if (kw) {
      const s = `${e.emp_no ?? ""} ${e.emp_name ?? ""}`.toLowerCase();
      if (!s.includes(kw)) return false;
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
    const [dRes, pRes, eRes] = await Promise.all([
      http.get("/departments"),
      http.get("/positions"),
      http.get("/employees"),
    ]);
    departments.value = dRes.data;
    positions.value = pRes.data;
    employees.value = eRes.data;
  } finally {
    loading.value = false;
  }
}

function onSearch() {
  // 当前为前端过滤；后续若要后端分页/筛选，可改为请求带参数
  page.value = 1;
}
function onReset() {
  q.dept_id = null;
  q.pos_id = null;
  q.status = null;
  q.keyword = "";
  page.value = 1;
}

// 弹窗表单
const dlgOpen = ref(false);
const form = reactive<any>({
  emp_id: null,
  emp_no: "",
  emp_name: "",
  gender: null,
  phone: "",
  email: "",
  dept_id: null,
  pos_id: null,
  hire_date: "",
  status: 1,
});

// 详情抽屉状态
const detailOpen = ref(false);
const detailLoading = ref(false);
const detailRow = ref<any | null>(null);
const recentSalaries = ref<any[]>([]);
const recentAttendance = ref<any[]>([]);

/**
 * 打开员工详情抽屉，并加载可选的“最近 5 条薪资/考勤记录”。
 * - 基本信息：直接使用当前表格行数据（无需改后端）
 * - 最近记录：基于现有接口拉取列表后前端筛选（小数据量场景足够）
 * @param row 员工表格行数据
 */
async function openDetail(row: any) {
  detailRow.value = row;
  detailOpen.value = true;
  await loadRecentRecords(row.emp_id);
}

/**
 * 加载某个员工的最近 5 条薪资与考勤记录（前端筛选）。
 * @param emp_id 员工ID
 */
async function loadRecentRecords(emp_id: number) {
  detailLoading.value = true;
  try {
    const [sRes, aRes] = await Promise.all([http.get("/salaries"), http.get("/attendance")]);
    const sList: any[] = Array.isArray(sRes.data) ? sRes.data : [];
    const aList: any[] = Array.isArray(aRes.data) ? aRes.data : [];

    recentSalaries.value = sList
      .filter((x) => x?.emp_id === emp_id)
      .sort((a, b) => String(b?.salary_month || "").localeCompare(String(a?.salary_month || "")))
      .slice(0, 5);

    recentAttendance.value = aList
      .filter((x) => x?.emp_id === emp_id)
      .sort((a, b) => String(b?.att_date || "").localeCompare(String(a?.att_date || "")))
      .slice(0, 5);
  } catch {
    // 提示：错误提示已在 src/api/http.ts 的响应拦截器中统一处理
    recentSalaries.value = [];
    recentAttendance.value = [];
  } finally {
    detailLoading.value = false;
  }
}

function openCreate() {
  Object.assign(form, {
    emp_id: null,
    emp_no: "",
    emp_name: "",
    gender: null,
    phone: "",
    email: "",
    dept_id: departments.value[0]?.dept_id ?? null,
    pos_id: positions.value[0]?.pos_id ?? null,
    hire_date: "",
    status: 1,
  });
  dlgOpen.value = true;
}

function openEdit(row: any) {
  Object.assign(form, {
    emp_id: row.emp_id,
    emp_no: row.emp_no,
    emp_name: row.emp_name,
    gender: row.gender ?? null,
    phone: row.phone ?? "",
    email: row.email ?? "",
    dept_id: row.dept_id,
    pos_id: row.pos_id,
    hire_date: row.hire_date,
    status: row.status,
  });
  dlgOpen.value = true;
}

async function submit() {
  if (!form.emp_no?.trim()) return ElMessage.warning("请输入工号");
  if (!form.emp_name?.trim()) return ElMessage.warning("请输入姓名");
  if (!form.dept_id) return ElMessage.warning("请选择部门");
  if (!form.pos_id) return ElMessage.warning("请选择岗位");
  if (!form.hire_date) return ElMessage.warning("请选择入职日期");

  try {
    if (form.emp_id) {
      await http.put(`/employees/${form.emp_id}`, {
        emp_name: form.emp_name,
        gender: form.gender,
        phone: form.phone || null,
        email: form.email || null,
        dept_id: form.dept_id,
        pos_id: form.pos_id,
        hire_date: form.hire_date,
        status: form.status,
      });
      ElMessage.success("更新成功");
    } else {
      await http.post("/employees", {
        emp_no: form.emp_no,
        emp_name: form.emp_name,
        gender: form.gender,
        phone: form.phone || null,
        email: form.email || null,
        dept_id: form.dept_id,
        pos_id: form.pos_id,
        hire_date: form.hire_date,
        status: form.status,
      });
      ElMessage.success("新增成功");
    }
    dlgOpen.value = false;
    await loadAll();
  } catch (e: any) {
    // 提示：错误提示已在 src/api/http.ts 的响应拦截器中统一处理
  }
}

async function deleteEmployee(emp_id: number) {
  await http.delete(`/employees/${emp_id}`);
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
.drawer-body { padding-right: 2px; }
</style>
