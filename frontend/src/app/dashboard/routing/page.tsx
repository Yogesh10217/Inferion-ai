"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { ChevronDown, ChevronRight, CheckCircle2, AlertTriangle, XCircle } from "lucide-react";
import { Topbar } from "@/components/dashboard/Topbar";
import { StatusBadge } from "@/components/dashboard/Badge";
import { routingStages, providerHealth, recentRoutingDecisions } from "@/lib/mock-data";

export default function RoutingPage() {
  const [expandedDecision, setExpandedDecision] = useState<string | null>(null);
  const [activeStage, setActiveStage] = useState<number | null>(null);

  return (
    <div className="flex flex-col min-h-full">
      <Topbar title="Routing Tracer" subtitle="9-stage intelligent pipeline — live decisions & provider health" />

      <main className="flex-1 p-6 space-y-6">
        {/* ── 9-Stage Pipeline ─────────────────────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="bg-white rounded-2xl border border-slate-200/60 p-6"
        >
          <div className="flex items-center justify-between mb-5">
            <div>
              <h3 className="font-display font-semibold text-[15px] text-[#0a1b33]">9-Stage Routing Pipeline</h3>
              <p className="text-[12px] text-slate-400 mt-0.5">Click any stage to see details</p>
            </div>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-100 text-[11px] font-semibold text-emerald-700">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              Pipeline Active
            </span>
          </div>

          {/* Pipeline flow */}
          <div className="flex flex-wrap gap-2 mb-6">
            {routingStages.map((s, i) => (
              <React.Fragment key={s.stage}>
                <button
                  onClick={() => setActiveStage(activeStage === s.stage ? null : s.stage)}
                  className={`flex items-center gap-1.5 px-3 py-2 rounded-xl border text-[12px] font-semibold transition-all ${
                    activeStage === s.stage
                      ? "bg-[#0a152d] text-white border-[#0a152d] shadow-sm"
                      : "bg-white text-[#0a1b33] border-slate-200 hover:border-slate-300 hover:shadow-sm"
                  }`}
                >
                  <span>{s.icon}</span>
                  <span>{s.stage}. {s.name}</span>
                </button>
                {i < routingStages.length - 1 && (
                  <div className="flex items-center text-slate-300">
                    <ChevronRight className="w-4 h-4" />
                  </div>
                )}
              </React.Fragment>
            ))}
          </div>

          {/* Stage detail panel */}
          {activeStage !== null && (() => {
            const stage = routingStages.find((s) => s.stage === activeStage)!;
            return (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                className="p-4 rounded-2xl bg-slate-50 border border-slate-200"
              >
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-lg">{stage.icon}</span>
                  <span className="font-display font-semibold text-[14px] text-[#0a1b33]">
                    Stage {stage.stage}: {stage.name}
                  </span>
                </div>
                <p className="text-[13px] text-[#64748b]">{stage.desc}</p>
              </motion.div>
            );
          })()}
        </motion.div>

        {/* ── Provider Health Scoreboard ────────────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="bg-white rounded-2xl border border-slate-200/60 p-6"
        >
          <h3 className="font-display font-semibold text-[15px] text-[#0a1b33] mb-4">Provider Health Scoreboard</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-[13px]">
              <thead>
                <tr className="text-left text-[11px] text-slate-400 font-medium border-b border-slate-100">
                  <th className="pb-3 pr-4">Provider</th>
                  <th className="pb-3 pr-4">Status</th>
                  <th className="pb-3 pr-4">Health Score</th>
                  <th className="pb-3 pr-4">Latency (ms)</th>
                  <th className="pb-3 pr-4">Error Rate</th>
                  <th className="pb-3">Circuit Breaker</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {providerHealth.map((p) => (
                  <tr key={p.name} className="hover:bg-slate-50/60 transition-colors">
                    <td className="py-3 pr-4 font-medium text-[#0a1b33]">{p.name}</td>
                    <td className="py-3 pr-4">
                      <StatusBadge status={p.status as "healthy" | "degraded" | "offline"} />
                    </td>
                    <td className="py-3 pr-4">
                      <div className="flex items-center gap-2">
                        <div className="w-20 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${p.score > 80 ? "bg-emerald-500" : p.score > 40 ? "bg-amber-400" : "bg-red-500"}`}
                            style={{ width: `${p.score}%` }}
                          />
                        </div>
                        <span className="text-[12px] font-mono text-[#0a1b33]">{p.score}</span>
                      </div>
                    </td>
                    <td className="py-3 pr-4 font-mono text-slate-600">{p.latency > 0 ? `${p.latency}ms` : "—"}</td>
                    <td className="py-3 pr-4 font-mono">
                      <span className={p.errorRate > 2 ? "text-red-600" : "text-slate-600"}>{p.errorRate}%</span>
                    </td>
                    <td className="py-3">
                      <span className={`font-mono text-[11px] px-2 py-0.5 rounded-full ${
                        p.circuitBreaker === "closed" ? "bg-emerald-50 text-emerald-700" :
                        p.circuitBreaker === "half-open" ? "bg-amber-50 text-amber-700" :
                        "bg-red-50 text-red-700"
                      }`}>
                        {p.circuitBreaker}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>

        {/* ── Recent Routing Decisions ──────────────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="bg-white rounded-2xl border border-slate-200/60 p-6"
        >
          <h3 className="font-display font-semibold text-[15px] text-[#0a1b33] mb-4">Routing Decision Log</h3>
          <div className="space-y-2">
            {recentRoutingDecisions.map((d) => (
              <div key={d.id} className="border border-slate-100 rounded-2xl overflow-hidden">
                <button
                  onClick={() => setExpandedDecision(expandedDecision === d.id ? null : d.id)}
                  className="w-full flex items-center justify-between p-4 text-left hover:bg-slate-50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0" />
                    <div>
                      <span className="text-[13px] font-semibold text-[#0a1b33]">{d.workspace}</span>
                      <span className="text-[12px] text-slate-400 mx-2">→</span>
                      <span className="font-mono text-[12px] text-blue-600">{d.model}</span>
                      <span className="text-[12px] text-slate-400 mx-2">→</span>
                      <span className="text-[12px] font-medium text-[#0a1b33]">{d.selectedProvider}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-[11px] font-mono text-slate-500">{d.latencyMs}ms</span>
                    <span className="text-[11px] px-2 py-0.5 rounded-full bg-slate-50 border border-slate-200 text-slate-600 font-medium">{d.stage}</span>
                    <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform ${expandedDecision === d.id ? "rotate-180" : ""}`} />
                  </div>
                </button>

                {expandedDecision === d.id && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="px-4 pb-4 grid grid-cols-2 sm:grid-cols-4 gap-3"
                  >
                    {[
                      { label: "Organization", value: d.org },
                      { label: "Cost", value: `$${d.costUsd.toFixed(4)}` },
                      { label: "Stage", value: d.stage },
                      { label: "Timestamp", value: new Date(d.timestamp).toLocaleTimeString() },
                    ].map(({ label, value }) => (
                      <div key={label} className="p-3 bg-slate-50 rounded-xl border border-slate-100">
                        <div className="text-[10px] text-slate-400 font-medium mb-1">{label}</div>
                        <div className="text-[12px] font-semibold text-[#0a1b33]">{value}</div>
                      </div>
                    ))}
                    <div className="col-span-2 sm:col-span-4 p-3 bg-blue-50 border border-blue-100 rounded-xl">
                      <div className="text-[10px] text-blue-600 font-semibold mb-1">Routing Reason</div>
                      <div className="text-[12px] text-[#0a1b33]">{d.reason}</div>
                    </div>
                  </motion.div>
                )}
              </div>
            ))}
          </div>
        </motion.div>
      </main>
    </div>
  );
}
