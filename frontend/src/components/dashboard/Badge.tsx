"use client";

import React from "react";
import { CheckCircle2, AlertTriangle, XCircle, Clock } from "lucide-react";

type Status = "healthy" | "degraded" | "offline" | "indexing" | "indexed" | "active" | "paused" | "error" | "installed" | "loading" | "uninstalling" | "disabled" | "running" | "idle" | "revoked";

const STATUS_CONFIG: Record<
  Status,
  { label: string; color: string; dot: string; icon?: React.ReactNode }
> = {
  healthy: { label: "Healthy", color: "text-emerald-700 bg-emerald-50 border-emerald-100", dot: "bg-emerald-500", icon: <CheckCircle2 className="w-3 h-3" /> },
  degraded: { label: "Degraded", color: "text-amber-700 bg-amber-50 border-amber-100", dot: "bg-amber-400", icon: <AlertTriangle className="w-3 h-3" /> },
  offline: { label: "Offline", color: "text-red-700 bg-red-50 border-red-100", dot: "bg-red-500", icon: <XCircle className="w-3 h-3" /> },
  indexing: { label: "Indexing…", color: "text-blue-700 bg-blue-50 border-blue-100", dot: "bg-blue-400 animate-pulse", icon: <Clock className="w-3 h-3" /> },
  indexed: { label: "Indexed", color: "text-emerald-700 bg-emerald-50 border-emerald-100", dot: "bg-emerald-500", icon: <CheckCircle2 className="w-3 h-3" /> },
  active: { label: "Active", color: "text-emerald-700 bg-emerald-50 border-emerald-100", dot: "bg-emerald-500" },
  paused: { label: "Paused", color: "text-slate-600 bg-slate-50 border-slate-200", dot: "bg-slate-400" },
  error: { label: "Error", color: "text-red-700 bg-red-50 border-red-100", dot: "bg-red-500" },
  installed: { label: "Installed", color: "text-blue-700 bg-blue-50 border-blue-100", dot: "bg-blue-400" },
  loading: { label: "Loading", color: "text-purple-700 bg-purple-50 border-purple-100", dot: "bg-purple-400 animate-pulse" },
  uninstalling: { label: "Uninstalling", color: "text-orange-700 bg-orange-50 border-orange-100", dot: "bg-orange-400 animate-pulse" },
  disabled: { label: "Disabled", color: "text-slate-500 bg-slate-50 border-slate-100", dot: "bg-slate-300" },
  running: { label: "Running", color: "text-blue-700 bg-blue-50 border-blue-100", dot: "bg-blue-500 animate-pulse" },
  idle: { label: "Idle", color: "text-slate-600 bg-slate-50 border-slate-200", dot: "bg-slate-400" },
  revoked: { label: "Revoked", color: "text-red-700 bg-red-50 border-red-100", dot: "bg-red-400" },
};

interface BadgeProps {
  status: Status | string;
  dot?: boolean;
}

export function StatusBadge({ status, dot = true }: BadgeProps) {
  const cfg = STATUS_CONFIG[status as Status] ?? {
    label: status,
    color: "text-slate-600 bg-slate-50 border-slate-200",
    dot: "bg-slate-400",
  };
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-[11px] font-semibold ${cfg.color}`}>
      {dot && <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot}`} />}
      {cfg.icon}
      {cfg.label}
    </span>
  );
}

// ── Role Badge ─────────────────────────────────────────────────────────────────
const ROLE_CONFIG: Record<string, string> = {
  admin: "text-purple-700 bg-purple-50 border-purple-100",
  developer: "text-blue-700 bg-blue-50 border-blue-100",
  viewer: "text-slate-600 bg-slate-50 border-slate-200",
};

export function RoleBadge({ role }: { role: string }) {
  const color = ROLE_CONFIG[role] ?? "text-slate-600 bg-slate-50 border-slate-200";
  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full border text-[11px] font-semibold ${color}`}>
      {role}
    </span>
  );
}

// ── Strategy Badge ─────────────────────────────────────────────────────────────
const STRATEGY_CONFIG: Record<string, string> = {
  ZeroShot: "text-slate-700 bg-slate-50 border-slate-200",
  ReAct: "text-blue-700 bg-blue-50 border-blue-100",
  PlanExecute: "text-purple-700 bg-purple-50 border-purple-100",
  TreeOfThought: "text-amber-700 bg-amber-50 border-amber-100",
};

export function StrategyBadge({ strategy }: { strategy: string }) {
  const color = STRATEGY_CONFIG[strategy] ?? "text-slate-700 bg-slate-50 border-slate-200";
  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full border text-[11px] font-semibold ${color}`}>
      {strategy}
    </span>
  );
}

export function PluginStateBadge({ state }: { state: string }) {
  return <StatusBadge status={state} />;
}
