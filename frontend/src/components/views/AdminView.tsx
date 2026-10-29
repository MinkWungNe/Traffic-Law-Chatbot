"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useAuthStore } from "@/stores/useAuthStore";
import { useChatStore } from "@/stores/useChatStore";
import { adminApi } from "@/lib/api";
import { UserProfile, AuditLogItem } from "@/types/chat";
import { BenchmarkDashboard } from "@/components/admin/BenchmarkDashboard";
import {
  Users,
  Shield,
  Search,
  Lock,
  Unlock,
  KeyRound,
  Trash2,
  RefreshCw,
  FileText,
  X,
  AlertTriangle,
  CheckCircle,
  Clock,
  Globe,
  Monitor,
  BarChart3,
} from "lucide-react";

export const AdminView: React.FC = () => {
  const { user, isAdmin } = useAuthStore();
  const { setActiveTab } = useChatStore();

  const [currentTab, setCurrentTab] = useState<"users" | "audit" | "benchmark">("users");

  // Users State
  const [users, setUsers] = useState<UserProfile[]>([]);
  const [userTotal, setUserTotal] = useState(0);
  const [userSearch, setUserSearch] = useState("");
  const [isLoadingUsers, setIsLoadingUsers] = useState(false);

  // Audit Logs State
  const [auditLogs, setAuditLogs] = useState<AuditLogItem[]>([]);
  const [auditTotal, setAuditTotal] = useState(0);
  const [auditFilter, setAuditFilter] = useState("");
  const [isLoadingAudit, setIsLoadingAudit] = useState(false);
  const [selectedLog, setSelectedLog] = useState<AuditLogItem | null>(null);

  // Action Modals State
  const [resetModalUser, setResetModalUser] = useState<UserProfile | null>(null);
  const [newPasswordInput, setNewPasswordInput] = useState("");
  const [isSubmittingReset, setIsSubmittingReset] = useState(false);

  const [notification, setNotification] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const showNotification = (type: "success" | "error", text: string) => {
    setNotification({ type, text });
    setTimeout(() => setNotification(null), 4000);
  };

  const fetchUsers = useCallback(async () => {
    setIsLoadingUsers(true);
    try {
      const data = await adminApi.listUsers(1, 50, userSearch);
      setUsers(data.users);
      setUserTotal(data.total);
    } catch (err: any) {
      showNotification("error", err.message || "Lỗi tải danh sách người dùng.");
    } finally {
      setIsLoadingUsers(false);
    }
  }, [userSearch]);

  const fetchAuditLogs = useCallback(async () => {
    setIsLoadingAudit(true);
    try {
      const data = await adminApi.listAuditLogs(1, 50, auditFilter);
      setAuditLogs(data.logs);
      setAuditTotal(data.total);
    } catch (err: any) {
      showNotification("error", err.message || "Lỗi tải nhật ký kiểm toán.");
    } finally {
      setIsLoadingAudit(false);
    }
  }, [auditFilter]);

  useEffect(() => {
    if (isAdmin) {
      if (currentTab === "users") {
        fetchUsers();
      } else {
        fetchAuditLogs();
      }
    }
  }, [isAdmin, currentTab, fetchUsers, fetchAuditLogs]);

  // Hành động Khóa / Mở khóa
  const handleToggleStatus = async (targetUser: UserProfile) => {
    const nextStatus = !targetUser.is_active;
    const confirmMsg = nextStatus
      ? `Bạn có chắc muốn MỞ KHÓA tài khoản ${targetUser.email}?`
      : `Bạn có chắc muốn KHÓA tài khoản ${targetUser.email}?`;

    if (!window.confirm(confirmMsg)) return;

    try {
      const res = await adminApi.updateUserStatus(targetUser.id, nextStatus, "Thao tác bởi Admin qua Dashboard");
      showNotification("success", res.message);
      fetchUsers();
    } catch (err: any) {
      showNotification("error", err.message || "Thao tác thất bại.");
    }
  };

  // Hành động Đặt lại mật khẩu
  const handleResetPasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resetModalUser || !newPasswordInput.trim()) return;
    setIsSubmittingReset(true);
    try {
      const res = await adminApi.resetUserPassword(resetModalUser.id, newPasswordInput.trim());
      showNotification("success", res.message);
      setResetModalUser(null);
      setNewPasswordInput("");
    } catch (err: any) {
      showNotification("error", err.message || "Đặt lại mật khẩu thất bại.");
    } finally {
      setIsSubmittingReset(false);
    }
  };

  // Hành động Xóa mềm tài khoản
  const handleDeleteUser = async (targetUser: UserProfile) => {
    const confirmMsg = `XÁC NHẬN: Bạn có chắc chắn muốn XÓA MỀM tài khoản ${targetUser.email}?\n(Tài khoản sẽ bị vô hiệu hóa nhưng lịch sử kiểm toán vẫn được bảo lưu).`;
    if (!window.confirm(confirmMsg)) return;

    try {
      const res = await adminApi.deleteUser(targetUser.id);
      showNotification("success", res.message);
      fetchUsers();
    } catch (err: any) {
      showNotification("error", err.message || "Xóa người dùng thất bại.");
    }
  };

  if (!isAdmin) {
    return (
      <div className="flex-1 h-screen flex flex-col items-center justify-center p-6 text-center select-none bg-canvas">
        <Shield size={48} className="text-red-500 mb-3" />
        <h2 className="text-xl font-bold text-primary-navy mb-2">Quyền truy cập bị từ chối</h2>
        <p className="text-[13.5px] text-slate-500 mb-4 max-w-md">
          Trang này chỉ dành riêng cho tài khoản Quản trị viên (Super Admin). Vui lòng đăng nhập với tài khoản hợp lệ.
        </p>
        <button
          onClick={() => setActiveTab("login")}
          className="px-4 py-2 rounded-xl bg-accent-red text-white text-[13px] font-semibold shadow-xs cursor-pointer"
        >
          Đến trang Đăng nhập
        </button>
      </div>
    );
  }

  return (
    <div className="flex-1 h-screen flex flex-col overflow-hidden bg-slate-50 select-none">
      {/* HEADER QUẢN TRỊ */}
      <header className="h-[60px] shrink-0 bg-white border-b border-slate-200 px-6 flex items-center justify-center z-10">
        <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200 shadow-2xs">
          <button
            onClick={() => setCurrentTab("users")}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-[12.5px] font-semibold transition-all cursor-pointer ${
              currentTab === "users" ? "bg-white text-primary-navy shadow-xs font-bold" : "text-slate-600 hover:text-slate-900"
            }`}
          >
            <Users size={15} />
            <span>Quản lý Tài khoản ({userTotal})</span>
          </button>
          <button
            onClick={() => setCurrentTab("audit")}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-[12.5px] font-semibold transition-all cursor-pointer ${
              currentTab === "audit" ? "bg-white text-primary-navy shadow-xs font-bold" : "text-slate-600 hover:text-slate-900"
            }`}
          >
            <FileText size={15} />
            <span>Nhật ký Kiểm toán ({auditTotal})</span>
          </button>
          {/* Tạm thời ẩn tab Xem báo cáo chất lượng AI */}
          {/*
          <button
            onClick={() => setCurrentTab("benchmark")}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-[12.5px] font-semibold transition-all cursor-pointer ${
              currentTab === "benchmark" ? "bg-white text-primary-navy shadow-xs font-bold" : "text-slate-600 hover:text-slate-900"
            }`}
          >
            <BarChart3 size={15} />
            <span>Xem báo cáo chất lượng AI</span>
          </button>
          */}
        </div>
      </header>

      {/* THÔNG BÁO ALERT NỔI */}
      {notification && (
        <div
          className={`mx-6 mt-4 p-3 rounded-xl border flex items-center justify-between text-[13px] shadow-sm animate-in fade-in duration-200 ${
            notification.type === "success"
              ? "bg-emerald-50 border-emerald-200 text-emerald-800"
              : "bg-red-50 border-red-200 text-red-800"
          }`}
        >
          <div className="flex items-center gap-2">
            {notification.type === "success" ? <CheckCircle size={16} /> : <AlertTriangle size={16} />}
            <span>{notification.text}</span>
          </div>
          <button onClick={() => setNotification(null)} className="cursor-pointer">
            <X size={14} />
          </button>
        </div>
      )}

      {/* NỘI DUNG CHÍNH THEO TAB */}
      <div className="flex-1 overflow-y-auto p-6">
        {/* TAB 1: QUẢN LÝ TÀI KHOẢN */}
        {currentTab === "users" && (
          <div className="flex flex-col gap-4 max-w-6xl mx-auto">
            {/* Toolbar tìm kiếm & Làm mới */}
            <div className="flex items-center justify-between gap-3 bg-white p-3 rounded-2xl border border-slate-200 shadow-2xs">
              <div className="relative flex-1 max-w-md">
                <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  placeholder="Tìm kiếm tài khoản theo email..."
                  value={userSearch}
                  onChange={(e) => setUserSearch(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && fetchUsers()}
                  className="w-full h-[38px] pl-9 pr-3 rounded-xl bg-slate-50 border border-slate-200 text-[13px] text-slate-800 placeholder:text-slate-400 outline-none focus:bg-white focus:border-slate-300"
                />
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => fetchUsers()}
                  disabled={isLoadingUsers}
                  className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-[12.5px] font-semibold transition-colors cursor-pointer"
                >
                  <RefreshCw size={14} className={isLoadingUsers ? "animate-spin" : ""} />
                  <span>Làm mới</span>
                </button>
              </div>
            </div>

            {/* Bảng Người dùng */}
            <div className="bg-white rounded-2xl border border-slate-200 shadow-2xs overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-[13px] border-collapse">
                  <thead>
                    <tr className="border-b border-slate-200 bg-slate-50/80 text-slate-500 font-semibold text-[11.5px] uppercase tracking-wider">
                      <th className="py-3 px-4">Tài khoản (Email)</th>
                      <th className="py-3 px-4">Vai trò</th>
                      <th className="py-3 px-4">Trạng thái</th>
                      <th className="py-3 px-4">Ngày tạo</th>
                      <th className="py-3 px-4 text-right">Thao tác</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 text-slate-700">
                    {users.map((u) => {
                      const isMe = u.id === user?.id;
                      return (
                        <tr key={u.id} className="hover:bg-slate-50/60 transition-colors">
                          <td className="py-3 px-4">
                            <div className="flex items-center gap-2.5">
                              <div className="w-8 h-8 rounded-full bg-slate-200 text-slate-700 font-bold flex items-center justify-center text-[12px] uppercase">
                                {u.email.charAt(0)}
                              </div>
                              <div className="flex flex-col">
                                <span className="font-semibold text-slate-900">{u.email}</span>
                                {isMe && (
                                  <span className="text-[10.5px] text-accent-red font-medium">
                                    (Tài khoản hiện tại của bạn)
                                  </span>
                                )}
                              </div>
                            </div>
                          </td>
                          <td className="py-3 px-4">
                            <span
                              className={`px-2 py-0.5 rounded-md text-[11px] font-bold uppercase tracking-wider ${
                                u.role === "admin"
                                  ? "bg-purple-100 text-purple-700 border border-purple-200"
                                  : "bg-blue-100 text-blue-700 border border-blue-200"
                              }`}
                            >
                              {u.role}
                            </span>
                          </td>
                          <td className="py-3 px-4">
                            {u.is_active ? (
                              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11.5px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                                Đang hoạt động
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11.5px] font-medium bg-red-50 text-red-700 border border-red-200">
                                <span className="w-1.5 h-1.5 rounded-full bg-red-500" />
                                Đã bị khóa
                              </span>
                            )}
                          </td>
                          <td className="py-3 px-4 text-slate-500 text-[12px]">
                            {u.created_at ? new Date(u.created_at).toLocaleDateString("vi-VN") : "—"}
                          </td>
                          <td className="py-3 px-4 text-right">
                            <div className="flex items-center justify-end gap-1.5">
                              {/* Nút Đổi mật khẩu */}
                              <button
                                onClick={() => setResetModalUser(u)}
                                className="p-1.5 rounded-lg text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition-colors cursor-pointer"
                                title="Admin đặt lại mật khẩu"
                              >
                                <KeyRound size={16} />
                              </button>

                              {/* Nút Khóa / Mở khóa (không thể khóa chính mình) */}
                              {!isMe && (
                                <button
                                  onClick={() => handleToggleStatus(u)}
                                  className={`p-1.5 rounded-lg transition-colors cursor-pointer ${
                                    u.is_active
                                      ? "text-amber-600 hover:bg-amber-50"
                                      : "text-emerald-600 hover:bg-emerald-50"
                                  }`}
                                  title={u.is_active ? "Khóa tài khoản" : "Mở khóa tài khoản"}
                                >
                                  {u.is_active ? <Lock size={16} /> : <Unlock size={16} />}
                                </button>
                              )}

                              {/* Nút Xóa mềm (không thể xóa chính mình) */}
                              {!isMe && (
                                <button
                                  onClick={() => handleDeleteUser(u)}
                                  className="p-1.5 rounded-lg text-red-500 hover:bg-red-50 transition-colors cursor-pointer"
                                  title="Xóa tài khoản (Xóa mềm)"
                                >
                                  <Trash2 size={16} />
                                </button>
                              )}
                            </div>
                          </td>
                        </tr>
                      );
                    })}

                    {users.length === 0 && !isLoadingUsers && (
                      <tr>
                        <td colSpan={5} className="py-8 text-center text-slate-400">
                          Không tìm thấy người dùng nào phù hợp.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: NHẬT KÝ KIỂM TOÁN (AUDIT LOGS) */}
        {currentTab === "audit" && (
          <div className="flex flex-col gap-4 max-w-6xl mx-auto">
            {/* Toolbar lọc sự kiện */}
            <div className="flex items-center justify-between gap-3 bg-white p-3 rounded-2xl border border-slate-200 shadow-2xs">
              <div className="flex items-center gap-2">
                <span className="text-[12.5px] font-semibold text-slate-700">Lọc theo hành động:</span>
                <select
                  value={auditFilter}
                  onChange={(e) => setAuditFilter(e.target.value)}
                  className="h-[36px] px-3 rounded-xl bg-slate-50 border border-slate-200 text-[12.5px] text-slate-800 outline-none cursor-pointer focus:bg-white"
                >
                  <option value="">-- Tất cả sự kiện --</option>
                  <option value="LOGIN_SUCCESS">LOGIN_SUCCESS (Đăng nhập thành công)</option>
                  <option value="LOGIN_FAILED">LOGIN_FAILED (Đăng nhập thất bại)</option>
                  <option value="REGISTER_SUCCESS">REGISTER_SUCCESS (Đăng ký mới)</option>
                  <option value="ADMIN_LOCK_USER">ADMIN_LOCK_USER (Khóa tài khoản)</option>
                  <option value="ADMIN_UNLOCK_USER">ADMIN_UNLOCK_USER (Mở khóa)</option>
                  <option value="ADMIN_RESET_PASSWORD">ADMIN_RESET_PASSWORD (Đổi mật khẩu)</option>
                  <option value="ADMIN_DELETE_USER">ADMIN_DELETE_USER (Xóa người dùng)</option>
                  <option value="PASSWORD_CHANGE">PASSWORD_CHANGE (User tự đổi pass)</option>
                </select>
              </div>

              <button
                onClick={() => fetchAuditLogs()}
                disabled={isLoadingAudit}
                className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-[12.5px] font-semibold transition-colors cursor-pointer"
              >
                <RefreshCw size={14} className={isLoadingAudit ? "animate-spin" : ""} />
                <span>Làm mới</span>
              </button>
            </div>

            {/* Bảng Audit Log */}
            <div className="bg-white rounded-2xl border border-slate-200 shadow-2xs overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-[13px] border-collapse">
                  <thead>
                    <tr className="border-b border-slate-200 bg-slate-50/80 text-slate-500 font-semibold text-[11.5px] uppercase tracking-wider">
                      <th className="py-3 px-4">Thời gian</th>
                      <th className="py-3 px-4">Người thực hiện</th>
                      <th className="py-3 px-4">Hành động</th>
                      <th className="py-3 px-4">Đối tượng tác động</th>
                      <th className="py-3 px-4">IP Client</th>
                      <th className="py-3 px-4 text-right">Chi tiết</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 text-slate-700">
                    {auditLogs.map((log) => {
                      const isDanger =
                        log.action.includes("FAILED") ||
                        log.action.includes("LOCK") ||
                        log.action.includes("DELETE");
                      return (
                        <tr
                          key={log.id}
                          onClick={() => setSelectedLog(log)}
                          className="hover:bg-slate-50 cursor-pointer transition-colors"
                        >
                          <td className="py-3 px-4 text-slate-500 font-mono text-[12px] whitespace-nowrap">
                            <div className="flex items-center gap-1.5">
                              <Clock size={13} className="text-slate-400 shrink-0" />
                              <span>{new Date(log.created_at).toLocaleString("vi-VN")}</span>
                            </div>
                          </td>
                          <td className="py-3 px-4 font-medium text-slate-900">{log.actor_email}</td>
                          <td className="py-3 px-4">
                            <span
                              className={`px-2 py-0.5 rounded-md text-[11px] font-mono font-bold tracking-tight ${
                                isDanger
                                  ? "bg-red-50 text-red-700 border border-red-200"
                                  : "bg-emerald-50 text-emerald-700 border border-emerald-200"
                              }`}
                            >
                              {log.action}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-slate-600">{log.target_email || "—"}</td>
                          <td className="py-3 px-4 font-mono text-[12px] text-slate-500">
                            {log.ip_address || "local"}
                          </td>
                          <td className="py-3 px-4 text-right">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                setSelectedLog(log);
                              }}
                              className="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-[11.5px] font-semibold transition-colors cursor-pointer"
                            >
                              Xem JSON
                            </button>
                          </td>
                        </tr>
                      );
                    })}

                    {auditLogs.length === 0 && !isLoadingAudit && (
                      <tr>
                        <td colSpan={6} className="py-8 text-center text-slate-400">
                          Chưa có bản ghi nhật ký kiểm toán nào.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: BÁO CÁO ĐO LƯỜNG CHẤT LƯỢNG AI */}
        {currentTab === "benchmark" && <BenchmarkDashboard />}
      </div>

      {/* MODAL 1: ĐẶT LẠI MẬT KHẨU */}
      {resetModalUser && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl border border-slate-200 w-full max-w-md p-6 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2 text-primary-navy">
                <KeyRound size={20} className="text-accent-red" />
                <h3 className="font-bold text-[16px]">Đặt lại mật khẩu</h3>
              </div>
              <button
                onClick={() => setResetModalUser(null)}
                className="text-slate-400 hover:text-slate-700 cursor-pointer"
              >
                <X size={18} />
              </button>
            </div>

            <p className="text-[13px] text-slate-600 mb-4">
              Bạn đang đặt lại mật khẩu cho tài khoản: <strong className="text-slate-900">{resetModalUser.email}</strong>.
            </p>

            <form onSubmit={handleResetPasswordSubmit} className="flex flex-col gap-3">
              <div>
                <label className="text-[12px] font-semibold text-slate-700 mb-1 block">
                  Mật khẩu mới (tối thiểu 6 ký tự)
                </label>
                <input
                  type="password"
                  required
                  minLength={6}
                  value={newPasswordInput}
                  onChange={(e) => setNewPasswordInput(e.target.value)}
                  placeholder="Nhập mật khẩu mới..."
                  className="w-full h-[40px] px-3 rounded-xl border border-slate-200 text-[13px] outline-none focus:border-accent-red"
                />
              </div>

              <div className="flex items-center justify-end gap-2 mt-2">
                <button
                  type="button"
                  onClick={() => setResetModalUser(null)}
                  className="px-4 py-2 rounded-xl text-slate-600 hover:bg-slate-100 text-[13px] font-semibold cursor-pointer"
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  disabled={isSubmittingReset}
                  className="px-4 py-2 rounded-xl bg-accent-red text-white text-[13px] font-semibold shadow-xs hover:bg-red-700 transition-colors cursor-pointer"
                >
                  {isSubmittingReset ? "Đang xử lý..." : "Xác nhận đặt lại"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 2: CHI TIẾT AUDIT LOG JSON */}
      {selectedLog && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl border border-slate-200 w-full max-w-2xl p-6 flex flex-col max-h-[85vh] animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4 shrink-0">
              <div className="flex items-center gap-2">
                <FileText size={20} className="text-accent-red" />
                <h3 className="font-bold text-[16px] text-primary-navy">Chi tiết Sự kiện Kiểm toán</h3>
              </div>
              <button
                onClick={() => setSelectedLog(null)}
                className="text-slate-400 hover:text-slate-700 cursor-pointer"
              >
                <X size={18} />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto pr-1 flex flex-col gap-4 text-[13px]">
              <div className="grid grid-cols-2 gap-3 bg-slate-50 p-3 rounded-xl border border-slate-200">
                <div>
                  <span className="text-[11px] text-slate-400 font-semibold uppercase block">Hành động:</span>
                  <span className="font-mono font-bold text-accent-red">{selectedLog.action}</span>
                </div>
                <div>
                  <span className="text-[11px] text-slate-400 font-semibold uppercase block">Thời gian:</span>
                  <span className="font-mono">{new Date(selectedLog.created_at).toLocaleString("vi-VN")}</span>
                </div>
                <div>
                  <span className="text-[11px] text-slate-400 font-semibold uppercase block">Người thực hiện:</span>
                  <span className="font-semibold text-slate-800">{selectedLog.actor_email}</span>
                </div>
                <div>
                  <span className="text-[11px] text-slate-400 font-semibold uppercase block">Đối tượng tác động:</span>
                  <span className="font-semibold text-slate-800">{selectedLog.target_email || "—"}</span>
                </div>
              </div>

              <div className="flex items-center gap-4 text-slate-600 text-[12px]">
                <div className="flex items-center gap-1.5">
                  <Globe size={14} className="text-slate-400" />
                  <span>IP: {selectedLog.ip_address || "Không rõ"}</span>
                </div>
                <div className="flex items-center gap-1.5 truncate">
                  <Monitor size={14} className="text-slate-400 shrink-0" />
                  <span className="truncate" title={selectedLog.user_agent || ""}>
                    UA: {selectedLog.user_agent || "Không rõ"}
                  </span>
                </div>
              </div>

              <div>
                <span className="text-[12px] font-semibold text-slate-700 block mb-1">
                  Metadata & Chi tiết Payload (JSON):
                </span>
                <pre className="p-3 rounded-xl bg-slate-900 text-emerald-400 font-mono text-[12px] overflow-x-auto leading-relaxed border border-slate-800">
                  {JSON.stringify(selectedLog.details || {}, null, 2)}
                </pre>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-100 flex justify-end shrink-0 mt-2">
              <button
                onClick={() => setSelectedLog(null)}
                className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-[13px] font-semibold cursor-pointer"
              >
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
