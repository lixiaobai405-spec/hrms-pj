import axios from "axios";
import { ElMessage } from "element-plus";

// 统一 axios 实例：所有请求都走 /api（由 Vite proxy / Nginx 反代处理）
const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  timeout: 15000,
});

// 请求拦截：可统一加 token（后续如果做登录）
http.interceptors.request.use(
  /**
   * 请求拦截器：在这里可以统一追加 Authorization 等请求头。
   * @param config Axios 请求配置
   * @returns 处理后的 Axios 请求配置
   */
  (config) => {
    return config;
  }
);

// 响应拦截：统一错误提示
http.interceptors.response.use(
  /**
   * 响应成功处理：直接透传响应。
   * @param resp Axios 响应
   * @returns Axios 响应
   */
  (resp) => resp,
  /**
   * 响应失败处理：统一弹出错误提示，并将错误继续抛出。
   * @param error Axios 错误对象
   * @returns Promise reject
   */
  (error) => {
    const status = error?.response?.status;
    const detail =
      error?.response?.data?.detail ??
      error?.response?.data ??
      error?.message ??
      "请求失败";

    const msg = String(detail);

    // 数据库唯一约束（MySQL 1062 / duplicate）友好提示
    if (msg.toLowerCase().includes("duplicate") || msg.includes("1062")) {
      ElMessage.error("数据重复：请检查唯一约束字段（如工号/手机号/邮箱/同月薪资/同日考勤）");
      return Promise.reject(error);
    }

    // 常见 HTTP 状态码提示
    if (status === 404) ElMessage.error("接口不存在（404）");
    else if (status === 422) ElMessage.error("参数校验失败（422）");
    else if (status === 500) ElMessage.error("服务器错误（500）");
    else ElMessage.error(`请求失败：${msg}`);

    return Promise.reject(error);
  }
);

export default http;
