<template>
  <div class="page">
    <el-card>
      <template #header>
        <div class="header">
          <div class="title">组织架构</div>
          <div class="hint">部门与岗位管理（CRUD）</div>
        </div>
      </template>

      <el-tabs v-model="active">
        <el-tab-pane label="部门管理" name="departments">
          <div class="toolbar">
            <el-button type="primary" @click="openDeptCreate">+ 新增部门</el-button>
            <el-button @click="loadDepartments">刷新</el-button>
          </div>

          <el-table :data="departments" v-loading="deptLoading" border>
            <el-table-column prop="dept_id" label="ID" width="80" />
            <el-table-column prop="dept_name" label="部门名称" />
            <el-table-column prop="parent_dept_id" label="上级部门ID" width="120" />
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button size="small" @click="openDeptEdit(row)">编辑</el-button>
                <el-popconfirm title="确认删除该部门？" @confirm="deleteDepartment(row.dept_id)">
                  <template #reference>
                    <el-button size="small" type="danger">删除</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="岗位管理" name="positions">
          <div class="toolbar">
            <el-button type="primary" @click="openPosCreate">+ 新增岗位</el-button>
            <el-button @click="loadPositions">刷新</el-button>
          </div>

          <el-table :data="positions" v-loading="posLoading" border>
            <el-table-column prop="pos_id" label="ID" width="80" />
            <el-table-column prop="pos_name" label="岗位名称" />
            <el-table-column prop="level_no" label="等级" width="100" />
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button size="small" @click="openPosEdit(row)">编辑</el-button>
                <el-popconfirm title="确认删除该岗位？" @confirm="deletePosition(row.pos_id)">
                  <template #reference>
                    <el-button size="small" type="danger">删除</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 部门弹窗 -->
    <el-dialog v-model="deptDialogOpen" :title="deptForm.dept_id ? '编辑部门' : '新增部门'" width="420px">
      <el-form :model="deptForm" label-width="100px">
        <el-form-item label="部门名称">
          <el-input v-model="deptForm.dept_name" placeholder="如：研发部" />
        </el-form-item>
        <el-form-item label="上级部门ID">
          <el-input v-model.number="deptForm.parent_dept_id" placeholder="可留空" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="deptDialogOpen=false">取消</el-button>
        <el-button type="primary" @click="submitDepartment">保存</el-button>
      </template>
    </el-dialog>

    <!-- 岗位弹窗 -->
    <el-dialog v-model="posDialogOpen" :title="posForm.pos_id ? '编辑岗位' : '新增岗位'" width="420px">
      <el-form :model="posForm" label-width="100px">
        <el-form-item label="岗位名称">
          <el-input v-model="posForm.pos_name" placeholder="如：后端工程师" />
        </el-form-item>
        <el-form-item label="岗位等级">
          <el-input v-model.number="posForm.level_no" placeholder="如：1/2/3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="posDialogOpen=false">取消</el-button>
        <el-button type="primary" @click="submitPosition">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import http from "../api/http";
import { ElMessage } from "element-plus";

const active = ref<"departments" | "positions">("departments");

const deptLoading = ref(false);
const posLoading = ref(false);
const departments = ref<any[]>([]);
const positions = ref<any[]>([]);

async function loadDepartments() {
  deptLoading.value = true;
  try {
    const res = await http.get("/departments");
    departments.value = res.data;
  } finally {
    deptLoading.value = false;
  }
}

async function loadPositions() {
  posLoading.value = true;
  try {
    const res = await http.get("/positions");
    positions.value = res.data;
  } finally {
    posLoading.value = false;
  }
}

// ---- 部门 CRUD ----
const deptDialogOpen = ref(false);
const deptForm = reactive<{ dept_id?: number; dept_name: string; parent_dept_id: number | null }>({
  dept_name: "",
  parent_dept_id: null,
});

function openDeptCreate() {
  deptForm.dept_id = undefined;
  deptForm.dept_name = "";
  deptForm.parent_dept_id = null;
  deptDialogOpen.value = true;
}

function openDeptEdit(row: any) {
  deptForm.dept_id = row.dept_id;
  deptForm.dept_name = row.dept_name;
  deptForm.parent_dept_id = row.parent_dept_id ?? null;
  deptDialogOpen.value = true;
}

async function submitDepartment() {
  if (!deptForm.dept_name?.trim()) {
    ElMessage.warning("请输入部门名称");
    return;
  }
  if (deptForm.dept_id) {
    await http.put(`/departments/${deptForm.dept_id}`, {
      dept_name: deptForm.dept_name,
      parent_dept_id: deptForm.parent_dept_id,
    });
    ElMessage.success("更新成功");
  } else {
    await http.post("/departments", {
      dept_name: deptForm.dept_name,
      parent_dept_id: deptForm.parent_dept_id,
    });
    ElMessage.success("新增成功");
  }
  deptDialogOpen.value = false;
  await loadDepartments();
}

async function deleteDepartment(dept_id: number) {
  await http.delete(`/departments/${dept_id}`);
  ElMessage.success("删除成功");
  await loadDepartments();
}

// ---- 岗位 CRUD ----
const posDialogOpen = ref(false);
const posForm = reactive<{ pos_id?: number; pos_name: string; level_no: number }>({
  pos_name: "",
  level_no: 1,
});

function openPosCreate() {
  posForm.pos_id = undefined;
  posForm.pos_name = "";
  posForm.level_no = 1;
  posDialogOpen.value = true;
}

function openPosEdit(row: any) {
  posForm.pos_id = row.pos_id;
  posForm.pos_name = row.pos_name;
  posForm.level_no = row.level_no ?? 1;
  posDialogOpen.value = true;
}

async function submitPosition() {
  if (!posForm.pos_name?.trim()) {
    ElMessage.warning("请输入岗位名称");
    return;
  }
  if (posForm.pos_id) {
    await http.put(`/positions/${posForm.pos_id}`, {
      pos_name: posForm.pos_name,
      level_no: posForm.level_no,
    });
    ElMessage.success("更新成功");
  } else {
    await http.post("/positions", {
      pos_name: posForm.pos_name,
      level_no: posForm.level_no,
    });
    ElMessage.success("新增成功");
  }
  posDialogOpen.value = false;
  await loadPositions();
}

async function deletePosition(pos_id: number) {
  await http.delete(`/positions/${pos_id}`);
  ElMessage.success("删除成功");
  await loadPositions();
}

onMounted(async () => {
  await loadDepartments();
  await loadPositions();
});
</script>

<style scoped>
.page {
  padding: 16px;
  background: #f5f7fb;
  min-height: 100vh;
}
.header {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}
.hint {
  font-size: 12px;
  color: #6b7280;
}
.toolbar {
  display: flex;
  gap: 10px;
  margin: 12px 0;
}
</style>
