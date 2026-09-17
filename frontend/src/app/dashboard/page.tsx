"use client";

import React from "react";
import { motion } from "framer-motion";
import { Activity, DollarSign, Bot, Zap, CheckCircle2, AlertTriangle } from "lucide-react";
import { Topbar } from "@/components/dashboard/Topbar";
import { StatCard } from "@/components/dashboard/StatCard";
import { RequestAreaChart, ProviderBarChart } from "@/components/dashboard/Charts";
import {
  overviewStats,
  requestTimeSeries,
  providerVolume,
  systemHealth,
  recentRoutingDecisions,
} from "@/lib/mock-data";

function fmt(n: number) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(2)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(0)}k`;
  return n.toString();
}

export default function DashboardPage() {
  return (
    <div className="flex flex-col min-h-full">
      <Topbar title="Overview" subtitle="Platform health at a glance" />

      <main className="flex-1 p-6 space-y-6">
        {/* ── Stats Row ──────────────────────────────────────────────────────── */}
        <div className="grid grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-4">
          <StatCard label="Total Requests (MTD)" value={fmt(overviewStats.totalRequests)} trend={8.4} sub="vs last month" icon={<Activity className="w-4 h-4 text-[#0a1b33]" />} accent="bg-slate-50" delay={0} />
          <StatCard label="Cost Today" value={`$${overviewStats.costToday}`} trend={-3.1} sub="vs yesterday" icon={<DollarSign className="w-4 h-4 text-emerald-600" />} accent="bg-emerald-50" delay={0.06} />
          <StatCard label="Active Agents" value={overviewStats.activeAgents} sub="currently running" icon={<Bot className="w-4 h-4 text-blue-600" />} accent="bg-blue-50" delay={0.12} />
          <StatCard label="P99 Latency" value={`${overviewStats.p99LatencyMs}ms`} trend={-12.3} sub="improving" icon={<Zap className="w-4 h-4 text-amber-500" />} accent="bg-amber-50" delay={0.18} />
          <StatCard label="Success Rate" value={`${overviewStats.successRate}%`} trend={0.1} sub="last 24h" delay={0.24} />
          <StatCard label="Tokens Today" value={fmt(overviewStats.tokensToday)} trend={5.2} sub="vs yesterday" delay={0.30} />
        </div>

        {/* ── Charts Row ─────────────────────────────────────────────────────── */}
        <div className="grid lg:grid-cols-2 gap-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="bg-white rounded-2xl border border-slate-200/60 p-5"
          >
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-display font-semibold text-[14px] text-[#0a1b33]">Requests (7d)</h3>
                <p className="text-[11px] text-slate-400">Daily volume across all tenants</p>
              </div>
              <span className="px-2.5 py-1 bg-slate-50 border border-slate-200 rounded-full text-[11px] font-medium text-slate-600">
                7 days
              </span>
            </div>
            <RequestAreaChart data={requestTimeSeries} />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.28 }}
            className="bg-white rounded-2xl border border-slate-200/60 p-5"
          >
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-display font-semibold text-[14px] text-[#0a1b33]">Provider Volume</h3>
                <p className="text-[11px] text-slate-400">Requests by provider this month</p>
              </div>
            </div>
            <ProviderBarChart data={providerVolume} />
          </motion.div>
        </div>

        {/* ── System Health + Recent Decisions ───────────────────────────────── */}
        <div className="grid lg:grid-cols-5 gap-4">
          {/* Health Strip */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.34 }}
            className="lg:col-span-2 bg-white rounded-2xl border border-slate-200/60 p-5"
          >
            <h3 className="font-display font-semibold text-[14px] text-[#0a1b33] mb-4">System Health</h3>
            <div className="space-y-2.5">
              {systemHealth.map((s, i) => (
                <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100">
                  <div className="flex items-center gap-2">
                    {s.status === "healthy" ? (
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 flex-shrink-0" />
                    ) : (
                      <AlertTriangle className="w-3.5 h-3.5 text-amber-500 flex-shrink-0" />
                    )}
                    <span className="text-[12px] font-medium text-[#0a1b33]">{s.name}</span>
                  </div>
                  <span className="font-mono text-[11px] text-slate-400">{s.latency}</span>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Recent Routing Decisions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="lg:col-span-3 bg-white rounded-2xl border border-slate-200/60 p-5"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-display font-semibold text-[14px] text-[#0a1b33]">Recent Routing Decisions</h3>
              <span className="text-[11px] text-blue-600 font-medium cursor-pointer hover:underline">View all →</span>
            </div>
            <div className="space-y-2.5">
              {recentRoutingDecisions.slice(0, 5).map((d) => (
                <div key={d.id} className="flex items-start gap-3 p-3 rounded-xl bg-slate-50 border border-slate-100 hover:border-slate-200 transition-all">
                  <div className="w-2 h-2 rounded-full bg-emerald-500 mt-1.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1.5 flex-wrap">
                      <span className="text-[12px] font-semibold text-[#0a1b33]">{d.workspace}</span>
                      <span className="text-[11px] text-slate-400">→</span>
                      <span className="text-[11px] font-mono text-blue-600">{d.model}</span>
                      <span className="text-[11px] text-slate-400">→</span>
                      <span className="text-[11px] font-semibold text-[#0a1b33]">{d.selectedProvider}</span>
                    </div>
                    <p className="text-[11px] text-slate-400 mt-0.5 truncate">{d.reason}</p>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <div className="text-[11px] font-mono text-slate-600">{d.latencyMs}ms</div>
                    <div className="text-[10px] text-slate-400">${d.costUsd.toFixed(4)}</div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </main>
    </div>
  );
}
