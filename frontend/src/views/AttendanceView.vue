<template>
  <div class="page">
    <el-card>
      <template #header>
        <div class="header">
          <div class="title">考勤管理</div>
          <div class="right">
            <el-button type="primary" @click="openCreate">+ 新增考勤</el-button>
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
            @change="onSearch"
          />
        </el-form-item>

        <el-form-item label="员工">
          <el-select v-model="q.emp_id" clearable placeholder="全部" style="width: 200px">
            <el-option v-for="e in employees" :key="e.emp_id" :label="`${e.emp_no} ${e.emp_name}`" :value="e.emp_id" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="q.att_status" clearable placeholder="全部" style="width: 160px">
            <el-option label="正常" :value="1" />
            <el-option label="迟到" :value="2" />
            <el-option label="早退" :value="3" />
            <el-option label="缺勤" :value="4" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="onSearch">查询</el-button>
          <el-button @click="onReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格 -->
      <el-table :data="pagedRows" v-loading="loading" border>
        <el-table-column prop="att_id" label="ID" width="80" />
        <el-table-column label="员工" width="220">
          <template #default="{ row }">{{ empLabel(row.emp_id) }}</template>
        </el-table-column>
        <el-table-column prop="att_date" label="日期" width="130" />
        <el-table-column prop="check_in" label="上班时间" width="120" />
        <el-table-column prop="check_out" label="下班时间" width="120" />
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="attTagType(row.att_status)">{{ attText(row.att_status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="180" />

        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-popconfirm title="确认删除该考勤记录？" @confirm="deleteAtt(row.att_id)">
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
    <el-dialog v-model="dlgOpen" :title="form.att_id ? '编辑考勤' : '新增考勤'" width="560px">
      <el-form :model="form" label-width="110px">
        <el-form-item label="员工">
          <el-select v-model="form.emp_id" :disabled="!!form.att_id" placeholder="请选择" style="width: 260px">
            <el-option v-for="e in employees" :key="e.emp_id" :label="`${e.emp_no} ${e.emp_name}`" :value="e.emp_id" />
          </el-select>
        </el-form-item>

        <el-form-item label="考勤日期">
          <el-date-picker
            v-model="form.att_date"
            type="date"
            value-format="YYYY-MM-DD"
            :disabled="!!form.att_id"
            placeholder="YYYY-MM-DD"
          />
        </el-form-item>

        <el-form-item label="上班时间">
          <el-time-picker v-model="form.check_in" value-format="HH:mm:ss" placeholder="可空" />
        </el-form-item>

        <el-form-item label="下班时间">
          <el-time-picker v-model="form.check_out" value-format="HH:mm:ss" placeholder="可空" />
        </el-form-item>

        <el-form-item label="考勤状态">
          <el-select v-model="form.att_status" style="width: 200px">
            <el-option label="正常" :value="1" />
            <el-option label="迟到" :value="2" />
            <el-option label="早退" :value="3" />
            <el-option label="缺勤" :value="4" />
          </el-select>
        </el-form-item>

        <el-form-item label="备注">
          <el-input v-model="form.remark" clearable />
        </el-form-item>

        <el-alert
          type="info"
          show-icon
          title="提示：同一员工同一天只能录入一条考勤记录（数据库唯一约束）。"
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
const employees = ref<any[]>([]);
const records = ref<any[]>([]);

// 筛选条件
const q = reactive<{ month: string; emp_id: number | null; att_status: number | null }>({
  month: currentMonth(),
  emp_id: null,
  att_status: null,
});

// 分页
const page = ref(1);
const pageSize = ref(10);

watch([() => q.month, () => q.emp_id, () => q.att_status], () => {
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

function attText(v: number) {
  return v === 1 ? "正常" : v === 2 ? "迟到" : v === 3 ? "早退" : "缺勤";
}
function attTagType(v: number) {
  return v === 1 ? "success" : v === 2 ? "warning" : v === 3 ? "info" : "danger";
}

const filteredRows = computed(() => {
  // 这里用前端过滤（基于 att_date 的 YYYY-MM 前缀）
  return records.value.filter((r) => {
    if (q.month && String(r.att_date).slice(0, 7) !== q.month) return false;
    if (q.emp_id && r.emp_id !== q.emp_id) return false;
    if (q.att_status && r.att_status !== q.att_status) return false;
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
    const [eRes, aRes] = await Promise.all([
      http.get("/employees"),
      http.get("/attendance"),
    ]);
    employees.value = eRes.data;
    records.value = aRes.data;
  } finally {
    loading.value = false;
  }
}

function onSearch() {
  page.value = 1;
}
function onReset() {
  q.month = currentMonth();
  q.emp_id = null;
  q.att_status = null;
  page.value = 1;
}

// 弹窗表单
const dlgOpen = ref(false);
const form = reactive<any>({
  att_id: null,
  emp_id: null,
  att_date: "",
  check_in: "",
  check_out: "",
  att_status: 1,
  remark: "",
});

function openCreate() {
  Object.assign(form, {
    att_id: null,
    emp_id: employees.value[0]?.emp_id ?? null,
    att_date: "",
    check_in: "",
    check_out: "",
    att_status: 1,
    remark: "",
  });
  dlgOpen.value = true;
}

function openEdit(row: any) {
  Object.assign(form, {
    att_id: row.att_id,
    emp_id: row.emp_id,
    att_date: row.att_date,
    check_in: row.check_in ?? "",
    check_out: row.check_out ?? "",
    att_status: row.att_status,
    remark: row.remark ?? "",
  });
  dlgOpen.value = true;
}

async function submit() {
  if (!form.emp_id) return ElMessage.warning("请选择员工");
  if (!form.att_date) return ElMessage.warning("请选择考勤日期");

  try {
    if (form.att_id) {
      await http.put(`/attendance/${form.att_id}`, {
        check_in: form.check_in || null,
        check_out: form.check_out || null,
        att_status: form.att_status,
        remark: form.remark || null,
      });
      ElMessage.success("更新成功");
    } else {
      await http.post("/attendance", {
        emp_id: form.emp_id,
        att_date: form.att_date,
        check_in: form.check_in || null,
        check_out: form.check_out || null,
        att_status: form.att_status,
        remark: form.remark || null,
      });
      ElMessage.success("新增成功");
    }
    dlgOpen.value = false;
    await loadAll();
  } catch (e: any) {
    // 提示：错误提示已在 src/api/http.ts 的响应拦截器中统一处理
  }
}

async function deleteAtt(att_id: number) {
  await http.delete(`/attendance/${att_id}`);
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
