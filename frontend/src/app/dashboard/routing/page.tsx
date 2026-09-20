"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  ChevronDown,
  ChevronRight,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Plus,
  X,
  Cpu,
  Check,
  Trash2,
} from "lucide-react";
import { Topbar } from "@/components/dashboard/Topbar";
import { StatusBadge } from "@/components/dashboard/Badge";
import { routingStages, providerHealth as initialHealth, recentRoutingDecisions } from "@/lib/mock-data";
import { registerNewModel, deleteModel } from "@/lib/api";

export default function RoutingPage() {
  const [expandedDecision, setExpandedDecision] = useState<string | null>(null);
  const [activeStage, setActiveStage] = useState<number | null>(null);
  const [providers, setProviders] = useState(initialHealth);

  // Modal State
  const [showAddModal, setShowAddModal] = useState(false);
  const [modelId, setModelId] = useState("");
  const [provider, setProvider] = useState("OpenAI");
  const [contextWindow, setContextWindow] = useState("128000");
  const [promptCost, setPromptCost] = useState("0.0015");
  const [completionCost, setCompletionCost] = useState("0.0060");
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const handleRegisterModel = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!modelId.trim()) return;

    setSubmitting(true);
    setSuccessMsg(null);

    const newModelData = {
      id: modelId.trim(),
      provider: provider,
      context_window: parseInt(contextWindow) || 128000,
      promptCost: parseFloat(promptCost) || 0,
      completionCost: parseFloat(completionCost) || 0,
    };

    const res = await registerNewModel(newModelData);

    // Update local scoreboard UI state
    setProviders((prev) => [
      {
        name: `${provider} ${modelId.trim()}`,
        status: "healthy",
        score: 98,
        latency: 12,
        errorRate: 0.0,
        circuitBreaker: "closed",
      },
      ...prev,
    ]);

    setSubmitting(false);
    setSuccessMsg(`Model '${modelId.trim()}' registered successfully!`);

    setTimeout(() => {
      setShowAddModal(false);
      setModelId("");
      setSuccessMsg(null);
    }, 1200);
  };

  return (
    <div className="flex flex-col min-h-full">
      <Topbar title="Routing Tracer & Model Registry" subtitle="9-stage intelligent pipeline — live decisions, model registry & provider health" />

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
                  className={`flex items-center gap-1.5 px-3 py-2 rounded-xl border text-[12px] font-semibold transition-all cursor-pointer ${
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

        {/* ── Provider Health & Model Registry Scoreboard ─────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="bg-white rounded-2xl border border-slate-200/60 p-6"
        >
          <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
            <div>
              <h3 className="font-display font-semibold text-[15px] text-[#0a1b33]">Provider & Model Scoreboard</h3>
              <p className="text-[12px] text-slate-400">Registered LLM models, status, and health metrics</p>
            </div>

            {/* + Add New Model UI Button */}
            <button
              onClick={() => setShowAddModal(true)}
              className="bg-[#0a152d] text-white font-medium text-[13px] px-4 py-2 rounded-xl shadow-sm hover:bg-[#132247] transition-all flex items-center gap-2 cursor-pointer"
            >
              <Plus className="w-4 h-4" />
              <span>Register New Model</span>
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-[13px]">
              <thead>
                <tr className="text-left text-[11px] text-slate-400 font-medium border-b border-slate-100">
                  <th className="pb-3 pr-4">Provider / Model</th>
                  <th className="pb-3 pr-4">Status</th>
                  <th className="pb-3 pr-4">Health Score</th>
                  <th className="pb-3 pr-4">Latency (ms)</th>
                  <th className="pb-3 pr-4">Error Rate</th>
                  <th className="pb-3 pr-4">Circuit Breaker</th>
                  <th className="pb-3 text-right pr-2">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {providers.map((p) => (
                  <tr key={p.name} className="hover:bg-slate-50/60 transition-colors">
                    <td className="py-3 pr-4 font-medium text-[#0a1b33] flex items-center gap-2">
                      <Cpu className="w-4 h-4 text-blue-600 flex-shrink-0" />
                      <span>{p.name}</span>
                    </td>
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
                    <td className="py-3 pr-4">
                      <span className={`font-mono text-[11px] px-2 py-0.5 rounded-full ${
                        p.circuitBreaker === "closed" ? "bg-emerald-50 text-emerald-700" :
                        p.circuitBreaker === "half-open" ? "bg-amber-50 text-amber-700" :
                        "bg-red-50 text-red-700"
                      }`}>
                        {p.circuitBreaker}
                      </span>
                    </td>
                    <td className="py-3 text-right pr-2">
                      <button
                        onClick={async () => {
                          await deleteModel(p.name);
                          setProviders((prev) => prev.filter((item) => item.name !== p.name));
                        }}
                        title={`Delete ${p.name}`}
                        className="p-1.5 rounded-lg hover:bg-red-50 text-slate-400 hover:text-red-600 transition-colors cursor-pointer inline-flex items-center justify-center"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
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
                  className="w-full flex items-center justify-between p-4 text-left hover:bg-slate-50 transition-colors cursor-pointer"
                >
                  <div className="flex items-center gap-3">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0" />
                    <div>
                      <span className="text-[13px] font-semibold text-[#0a1b33]">{d.workspace}</span>
                      <span className="text-[12px] text-slate-400 mx-2">→</span>
                      <span className="font-mono text-[12px] text-blue-600">{d.model}</span>
                      <span className="text-[12px] text-slate-400 mx-2">via</span>
                      <span className="text-[13px] font-medium text-[#0a1b33]">{d.selectedProvider}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-600 font-medium">
                      {d.stage}
                    </span>
                    <span className="font-mono text-[12px] text-slate-500">{d.latencyMs}ms</span>
                    <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform ${expandedDecision === d.id ? "rotate-180" : ""}`} />
                  </div>
                </button>
                {expandedDecision === d.id && (
                  <div className="px-4 pb-4 pt-1 bg-slate-50 border-t border-slate-100 text-[12px] space-y-1">
                    <div className="text-slate-500"><strong className="text-slate-700">Timestamp:</strong> {d.timestamp}</div>
                    <div className="text-slate-500"><strong className="text-slate-700">Cost:</strong> ${d.costUsd.toFixed(4)}</div>
                    <div className="text-slate-500"><strong className="text-slate-700">Reason:</strong> {d.reason}</div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </motion.div>
      </main>

      {/* ── Add Model UI Modal ────────────────────────────────────────────── */}
      <AnimatePresence>
        {showAddModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              className="relative w-full max-w-lg bg-white rounded-3xl border border-slate-200 shadow-2xl p-6 md:p-8 overflow-hidden"
            >
              <button
                onClick={() => setShowAddModal(false)}
                className="absolute top-6 right-6 p-2 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>

              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 rounded-2xl bg-blue-50 border border-blue-100 text-blue-600">
                  <Cpu className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="font-display text-lg font-bold text-[#0a1b33]">
                    Register New AI Model
                  </h3>
                  <p className="text-xs text-slate-500">
                    Add a custom LLM model to the Inferion Routing Gateway
                  </p>
                </div>
              </div>

              {successMsg && (
                <div className="mb-4 p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-medium flex items-center gap-2">
                  <Check className="w-4 h-4 text-emerald-600" />
                  <span>{successMsg}</span>
                </div>
              )}

              <form onSubmit={handleRegisterModel} className="space-y-4 text-xs">
                <div>
                  <label className="block text-slate-700 font-semibold mb-1">
                    Model ID / Name:
                  </label>
                  <input
                    type="text"
                    required
                    value={modelId}
                    onChange={(e) => setModelId(e.target.value)}
                    placeholder="e.g. gpt-4o, claude-3-5-sonnet, llama3-70b, custom-fine-tuned-v1"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm text-[#0a1b33] focus:outline-none focus:ring-2 focus:ring-[#0a152d]"
                  />
                </div>

                <div>
                  <label className="block text-slate-700 font-semibold mb-1">
                    Model Provider:
                  </label>
                  <select
                    value={provider}
                    onChange={(e) => setProvider(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm text-[#0a1b33] focus:outline-none focus:ring-2 focus:ring-[#0a152d]"
                  >
                    <option value="OpenAI">OpenAI</option>
                    <option value="Anthropic">Anthropic</option>
                    <option value="Ollama (Local)">Ollama (Local $0)</option>
                    <option value="AWS Bedrock">AWS Bedrock</option>
                    <option value="Google Gemini">Google Gemini</option>
                    <option value="Azure OpenAI">Azure OpenAI</option>
                    <option value="Cohere">Cohere</option>
                    <option value="Mistral">Mistral AI</option>
                    <option value="Custom Private GPU">Custom Private GPU</option>
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-slate-700 font-semibold mb-1">
                      Context Window (Tokens):
                    </label>
                    <input
                      type="number"
                      value={contextWindow}
                      onChange={(e) => setContextWindow(e.target.value)}
                      placeholder="128000"
                      className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm text-[#0a1b33] focus:outline-none focus:ring-2 focus:ring-[#0a152d]"
                    />
                  </div>
                  <div>
                    <label className="block text-slate-700 font-semibold mb-1">
                      Prompt Cost ($/1k):
                    </label>
                    <input
                      type="number"
                      step="0.0001"
                      value={promptCost}
                      onChange={(e) => setPromptCost(e.target.value)}
                      placeholder="0.0015"
                      className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm text-[#0a1b33] focus:outline-none focus:ring-2 focus:ring-[#0a152d]"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-slate-700 font-semibold mb-1">
                    Completion Cost ($/1k):
                  </label>
                  <input
                    type="number"
                    step="0.0001"
                    value={completionCost}
                    onChange={(e) => setCompletionCost(e.target.value)}
                    placeholder="0.0060"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm text-[#0a1b33] focus:outline-none focus:ring-2 focus:ring-[#0a152d]"
                  />
                </div>

                <div className="pt-2">
                  <button
                    type="submit"
                    disabled={submitting}
                    className="w-full bg-[#0a152d] text-white font-medium text-sm py-3 rounded-xl hover:bg-[#132247] transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
                  >
                    {submitting ? (
                      <span>Registering Model...</span>
                    ) : (
                      <>
                        <Plus className="w-4 h-4" />
                        <span>Register Model in Gateway</span>
                      </>
                    )}
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
