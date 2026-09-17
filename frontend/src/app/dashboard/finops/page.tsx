"use client";

import React from "react";
import { motion } from "framer-motion";
import { DollarSign, TrendingUp, PieChart, BarChart3, Wallet, CreditCard, ShieldAlert } from "lucide-react";
import { Topbar } from "@/components/dashboard/Topbar";
import { StatCard } from "@/components/dashboard/StatCard";
import { StackedCostChart, ModelCostChart } from "@/components/dashboard/Charts";
import { workspaceBudgets, costByModel, dailyCostTrend } from "@/lib/mock-data";

export default function FinOpsPage() {
  const totalSpentMtd = workspaceBudgets.reduce((acc, w) => acc + w.usedMtd, 0);
  const totalBudgetMtd = workspaceBudgets.reduce((acc, w) => acc + w.budgetMtd, 0);

  return (
    <div className="flex min-h-screen flex-col">
      <Topbar title="FinOps & Cost Intelligence" subtitle="Real-time token cost allocation, tenant budgets, and model cost comparisons" />

      <main className="flex-1 space-y-6 p-6">
        {/* Top summary */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <DollarSign className="h-5 w-5 text-emerald-400" />
            <span className="text-xs text-slate-300">
              Token Cost Engine: Real-time per-token billing active
            </span>
          </div>
          <span className="text-xs text-slate-400">Billing Cycle: Sep 1 – Sep 30, 2026</span>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard label="Total Spent MTD" value={`$${totalSpentMtd.toLocaleString()}`} trend={+8.4} sub={`Of $${totalBudgetMtd.toLocaleString()} budget`} />
          <StatCard label="Cost Today" value="$47.83" trend={-3.2} sub="213,892 requests" />
          <StatCard label="Token Efficiency" value="64% Saved" sub="via Local Ollama routing" />
          <StatCard label="Cost Per 1M Tokens" value="$0.58" sub="Weighted average" />
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="rounded-xl border border-slate-800 bg-[#070e1c]/80 p-5 backdrop-blur-md">
            <h3 className="text-sm font-semibold text-slate-100 mb-1">Daily Cost Trend by Workspace</h3>
            <p className="text-xs text-slate-400 mb-4">Daily spending broken down across top teams</p>
            <StackedCostChart data={dailyCostTrend as any} />
          </div>

          <div className="rounded-xl border border-slate-800 bg-[#070e1c]/80 p-5 backdrop-blur-md">
            <h3 className="text-sm font-semibold text-slate-100 mb-1">Cost by Model Provider</h3>
            <p className="text-xs text-slate-400 mb-4">Total MTD spending across models</p>
            <ModelCostChart data={costByModel as any} />
          </div>
        </div>

        {/* Workspace Budget Utilization Table */}
        <div className="rounded-xl border border-slate-800 bg-[#070e1c]/80 p-5 backdrop-blur-md">
          <h3 className="text-sm font-semibold text-slate-100 mb-4">Workspace Budget Allocation & Utilization</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="border-b border-slate-800 bg-[#0a152d]/60 text-slate-400">
                <tr>
                  <th className="px-4 py-3">Workspace</th>
                  <th className="px-4 py-3">Organization</th>
                  <th className="px-4 py-3">Requests MTD</th>
                  <th className="px-4 py-3">Budget MTD</th>
                  <th className="px-4 py-3">Spent MTD</th>
                  <th className="px-4 py-3">Utilization</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
                {workspaceBudgets.map((w) => {
                  const pct = Math.min((w.usedMtd / w.budgetMtd) * 100, 100);
                  return (
                    <tr key={w.workspace} className="hover:bg-slate-800/30">
                      <td className="px-4 py-3 font-semibold text-slate-200">{w.workspace}</td>
                      <td className="px-4 py-3 text-slate-400">{w.org}</td>
                      <td className="px-4 py-3 text-slate-300">{w.requests.toLocaleString()}</td>
                      <td className="px-4 py-3 text-slate-300">${w.budgetMtd.toLocaleString()}</td>
                      <td className="px-4 py-3 text-slate-200 font-bold">${w.usedMtd.toLocaleString()}</td>
                      <td className="px-4 py-3">
                        <div className="flex items-center space-x-2">
                          <div className="h-1.5 w-24 rounded-full bg-slate-800">
                            <div
                              className={`h-1.5 rounded-full ${
                                pct > 80 ? "bg-rose-500" : pct > 60 ? "bg-amber-500" : "bg-emerald-500"
                              }`}
                              style={{ width: `${pct}%` }}
                            />
                          </div>
                          <span className="text-[10px] text-slate-400">{pct.toFixed(0)}%</span>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}
