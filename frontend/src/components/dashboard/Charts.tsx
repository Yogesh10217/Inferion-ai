"use client";

import React from "react";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

// ── Shared tooltip styles ──────────────────────────────────────────────────────
const tooltipStyle = {
  backgroundColor: "#ffffff",
  border: "1px solid #e2e8f0",
  borderRadius: "12px",
  boxShadow: "0 4px 16px rgba(0,0,0,0.06)",
  fontSize: "12px",
  color: "#0a1b33",
};

// ── Area Chart ─────────────────────────────────────────────────────────────────
interface RequestAreaChartProps {
  data: { date: string; requests: number; cost: number }[];
}

export function RequestAreaChart({ data }: RequestAreaChartProps) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <AreaChart data={data} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
        <defs>
          <linearGradient id="reqGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#0a152d" stopOpacity={0.15} />
            <stop offset="95%" stopColor="#0a152d" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
        <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
        <Tooltip contentStyle={tooltipStyle} formatter={(v: number) => [v.toLocaleString(), "Requests"]} />
        <Area type="monotone" dataKey="requests" stroke="#0a152d" strokeWidth={2} fill="url(#reqGradient)" dot={false} />
      </AreaChart>
    </ResponsiveContainer>
  );
}

// ── Provider Bar Chart ─────────────────────────────────────────────────────────
interface ProviderBarChartProps {
  data: { provider: string; requests: number }[];
}

export function ProviderBarChart({ data }: ProviderBarChartProps) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} margin={{ top: 4, right: 4, left: -20, bottom: 0 }} barSize={20}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
        <XAxis dataKey="provider" tick={{ fontSize: 10, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
        <Tooltip contentStyle={tooltipStyle} formatter={(v: number) => [v.toLocaleString(), "Requests"]} />
        <Bar dataKey="requests" fill="#0a152d" radius={[6, 6, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

// ── Stacked Cost Bar Chart ─────────────────────────────────────────────────────
interface StackedCostChartProps {
  data: { day: string; eng: number; sales: number; finance: number; hr: number }[];
}

export function StackedCostChart({ data }: StackedCostChartProps) {
  return (
    <ResponsiveContainer width="100%" height={240}>
      <BarChart data={data} margin={{ top: 4, right: 4, left: -20, bottom: 0 }} barSize={24}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
        <XAxis dataKey="day" tick={{ fontSize: 10, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} tickFormatter={(v) => `$${v}`} />
        <Tooltip contentStyle={tooltipStyle} formatter={(v: number, name: string) => [`$${v}`, name.charAt(0).toUpperCase() + name.slice(1)]} />
        <Legend wrapperStyle={{ fontSize: "11px", color: "#64748b" }} />
        <Bar dataKey="eng" name="Engineering" stackId="a" fill="#0a152d" radius={[0, 0, 0, 0]} />
        <Bar dataKey="finance" name="Finance" stackId="a" fill="#3b82f6" />
        <Bar dataKey="sales" name="Sales" stackId="a" fill="#6366f1" />
        <Bar dataKey="hr" name="HR" stackId="a" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

// ── Cost by Model Bar Chart ────────────────────────────────────────────────────
interface ModelCostChartProps {
  data: { model: string; cost: number }[];
}

export function ModelCostChart({ data }: ModelCostChartProps) {
  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={data} layout="vertical" margin={{ top: 4, right: 16, left: 8, bottom: 0 }} barSize={14}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false} />
        <XAxis type="number" tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} tickFormatter={(v) => `$${v}`} />
        <YAxis type="category" dataKey="model" tick={{ fontSize: 11, fill: "#64748b" }} axisLine={false} tickLine={false} width={110} />
        <Tooltip contentStyle={tooltipStyle} formatter={(v: number) => [`$${v}`, "Cost MTD"]} />
        <Bar dataKey="cost" fill="#0a152d" radius={[0, 6, 6, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
