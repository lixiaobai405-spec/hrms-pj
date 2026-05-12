import { createRouter, createWebHistory } from "vue-router";
import AdminLayout from "../layouts/AdminLayout.vue";

import DashboardView from "../views/DashboardView.vue";
import OrgView from "../views/OrgView.vue";
import EmployeesView from "../views/EmployeesView.vue";
import SalariesView from "../views/SalariesView.vue";
import AttendanceView from "../views/AttendanceView.vue";
import ReportsView from "../views/ReportsView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      component: AdminLayout,
      children: [
        { path: "", name: "dashboard", component: DashboardView },
        { path: "employees", name: "employees", component: EmployeesView },
        { path: "org", name: "org", component: OrgView },
        { path: "salaries", name: "salaries", component: SalariesView },
        { path: "attendance", name: "attendance", component: AttendanceView },
        { path: "reports", name: "reports", component: ReportsView },
      ],
    },
  ],
});

export default router;
