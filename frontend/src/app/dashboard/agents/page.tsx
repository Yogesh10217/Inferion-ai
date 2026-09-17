"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { Bot, Play, Terminal, Cpu, Clock, Zap, CheckCircle2, AlertTriangle, Layers } from "lucide-react";
import { Topbar } from "@/components/dashboard/Topbar";
import { StatCard } from "@/components/dashboard/StatCard";
import { StatusBadge, StrategyBadge } from "@/components/dashboard/Badge";
import { Modal } from "@/components/dashboard/Modal";
import { agents, agentRunLog } from "@/lib/mock-data";

export default function AgentsPage() {
  const [selectedAgent, setSelectedAgent] = useState<typeof agents[0] | null>(null);
  const [runModalOpen, setRunModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<"overview" | "logs">("overview");

  // Form state
  const [prompt, setPrompt] = useState("Scan repository for failing test cases and suggest fixes.");
  const [strategy, setStrategy] = useState("ReAct");

  return (
    <div className="flex min-h-screen flex-col">
      <Topbar title="Agent Execution Sandbox" subtitle="Autonomous LLM agents with tool execution and multi-step planning" />

      <main className="flex-1 space-y-6 p-6">
        {/* Top Actions & Summary */}
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
          <div className="flex items-center space-x-2">
            <span className="flex h-3 w-3 rounded-full bg-emerald-400"></span>
            <span className="text-xs text-slate-300">
              6 Active Agent Runtimes Configured
            </span>
          </div>
          <button
            onClick={() => setRunModalOpen(true)}
            className="inline-flex items-center justify-center rounded-lg bg-blue-600 px-4 py-2 text-xs font-semibold text-white transition-colors hover:bg-blue-500"
          >
            <Play className="mr-1.5 h-3.5 w-3.5 fill-current" /> Run Agent Sandbox
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard label="Total Agent Runtimes" value={agents.length} sub="ReAct, PlanExecute, ToT" />
          <StatCard label="Active Runtimes" value={agents.filter((a) => a.status === "running" || a.status === "idle").length} trend={+12} sub="Ready for execution" />
          <StatCard label="Total Executions" value="3,227" sub="Last 30 days" />
          <StatCard label="Avg Execution Latency" value="2.8s" sub="Across all strategies" />
        </div>

        {/* Agents Card Grid */}
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {agents.map((agent) => (
            <motion.div
              key={agent.id}
              whileHover={{ y: -2 }}
              className="flex flex-col justify-between rounded-xl border border-slate-800 bg-[#070e1c]/80 p-5 backdrop-blur-md transition-all hover:border-slate-700"
            >
              <div>
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-blue-500/20 bg-blue-500/10 text-blue-400">
                      <Bot className="h-5 w-5" />
                    </div>
                    <div>
                      <h3 className="text-sm font-semibold text-slate-100">{agent.name}</h3>
                      <span className="font-mono text-[10px] text-slate-400">{agent.id}</span>
                    </div>
                  </div>
                  <StatusBadge status={agent.status as any} />
                </div>

                <div className="mt-4 flex items-center space-x-2">
                  <span className="text-[11px] text-slate-400">Strategy:</span>
                  <StrategyBadge strategy={agent.strategy as any} />
                </div>

                <div className="mt-3 flex flex-wrap gap-1">
                  {agent.tools.map((t) => (
                    <span
                      key={t}
                      className="rounded border border-slate-800 bg-slate-900/80 px-2 py-0.5 font-mono text-[10px] text-slate-300"
                    >
                      {t}
                    </span>
                  ))}
                </div>
              </div>

              <div className="mt-6 border-t border-slate-800/80 pt-4">
                <div className="grid grid-cols-3 gap-2 text-center text-xs">
                  <div>
                    <span className="block text-[10px] text-slate-500">Runs</span>
                    <span className="font-mono font-semibold text-slate-200">{agent.totalRuns}</span>
                  </div>
                  <div>
                    <span className="block text-[10px] text-slate-500">Avg Time</span>
                    <span className="font-mono font-semibold text-slate-200">{(agent.avgLatencyMs / 1000).toFixed(1)}s</span>
                  </div>
                  <div>
                    <span className="block text-[10px] text-slate-500">Budget</span>
                    <span className="font-mono font-semibold text-slate-200">${agent.budgetUsed} / ${agent.budgetMax}</span>
                  </div>
                </div>

                <button
                  onClick={() => setSelectedAgent(agent)}
                  className="mt-4 w-full rounded-lg border border-slate-800 bg-slate-900/60 py-1.5 text-center text-xs font-medium text-slate-300 transition-colors hover:bg-slate-800 hover:text-white"
                >
                  View Execution Log & Specs
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      </main>

      {/* Agent Detail Modal */}
      <Modal
        open={!!selectedAgent}
        onClose={() => setSelectedAgent(null)}
        title={selectedAgent?.name || "Agent Detail"}
        subtitle={`ID: ${selectedAgent?.id} — Strategy: ${selectedAgent?.strategy}`}
      >
        {selectedAgent && (
          <div className="space-y-4">
            <div className="flex border-b border-slate-800 text-xs">
              <button
                onClick={() => setActiveTab("overview")}
                className={`pb-2 pr-4 font-medium transition-colors ${
                  activeTab === "overview" ? "border-b-2 border-blue-500 text-blue-400" : "text-slate-400"
                }`}
              >
                Overview & Configuration
              </button>
              <button
                onClick={() => setActiveTab("logs")}
                className={`pb-2 px-4 font-medium transition-colors ${
                  activeTab === "logs" ? "border-b-2 border-blue-500 text-blue-400" : "text-slate-400"
                }`}
              >
                Live Execution Stream ({agentRunLog.length} steps)
              </button>
            </div>

            {activeTab === "overview" ? (
              <div className="space-y-4 text-xs">
                <div className="grid grid-cols-2 gap-4 rounded-lg border border-slate-800 bg-slate-900/40 p-4">
                  <div>
                    <span className="text-slate-400">Planner Strategy:</span>
                    <p className="font-medium text-slate-200">{selectedAgent.strategy}</p>
                  </div>
                  <div>
                    <span className="text-slate-400">Current Status:</span>
                    <div className="mt-1">
                      <StatusBadge status={selectedAgent.status as any} />
                    </div>
                  </div>
                  <div>
                    <span className="text-slate-400">Total Executions:</span>
                    <p className="font-mono text-slate-200">{selectedAgent.totalRuns}</p>
                  </div>
                  <div>
                    <span className="text-slate-400">Budget Limit:</span>
                    <p className="font-mono text-slate-200">${selectedAgent.budgetUsed} / ${selectedAgent.budgetMax}</p>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold text-slate-200 mb-2">Available Tools</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedAgent.tools.map((t) => (
                      <div key={t} className="rounded-md border border-slate-800 bg-slate-900 px-3 py-1 font-mono text-slate-300">
                        {t}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="max-h-96 overflow-y-auto space-y-2 font-mono text-[11px]">
                {agentRunLog.map((log) => (
                  <div key={log.step} className="rounded-lg border border-slate-800/80 bg-slate-900/60 p-3">
                    <div className="flex items-center justify-between text-[10px] text-slate-500 mb-1">
                      <span className="font-semibold uppercase text-blue-400">Step {log.step} — {log.type}</span>
                      <span>{log.timestamp}</span>
                    </div>
                    <p className="text-slate-300 whitespace-pre-wrap">{log.content || log.input}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </Modal>

      {/* Run Agent Modal */}
      <Modal
        open={runModalOpen}
        onClose={() => setRunModalOpen(false)}
        title="Execute Agent Task"
        subtitle="Prompt the agent and watch real-time planning, tool execution, and response synthesis"
      >
        <div className="space-y-4 text-xs">
          <div>
            <label className="block text-slate-400 mb-1">Select Strategy</label>
            <select
              value={strategy}
              onChange={(e) => setStrategy(e.target.value)}
              className="w-full rounded-lg border border-slate-800 bg-slate-900 p-2.5 text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="ReAct">ReAct (Reason + Act loop)</option>
              <option value="PlanExecute">Plan & Execute (Explicit step planning)</option>
              <option value="TreeOfThought">Tree-of-Thought (Parallel branching)</option>
              <option value="ZeroShot">ZeroShot Direct</option>
            </select>
          </div>

          <div>
            <label className="block text-slate-400 mb-1">Task Prompt</label>
            <textarea
              rows={4}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="w-full rounded-lg border border-slate-800 bg-slate-900 p-2.5 font-mono text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <div className="flex justify-end space-x-2 pt-2">
            <button
              onClick={() => setRunModalOpen(false)}
              className="rounded-lg border border-slate-800 bg-slate-900 px-4 py-2 text-slate-400 hover:bg-slate-800"
            >
              Cancel
            </button>
            <button
              onClick={() => {
                alert("Agent task launched! Simulated execution stream initialized.");
                setRunModalOpen(false);
              }}
              className="rounded-lg bg-blue-600 px-4 py-2 font-semibold text-white hover:bg-blue-500"
            >
              Launch Execution
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
