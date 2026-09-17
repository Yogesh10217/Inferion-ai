"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { Brain, Search, Clock, ShieldCheck, UserCheck, RefreshCw, Zap } from "lucide-react";
import { Topbar } from "@/components/dashboard/Topbar";
import { StatCard } from "@/components/dashboard/StatCard";
import { DataTable } from "@/components/dashboard/DataTable";
import { memoryEntries } from "@/lib/mock-data";

type MemoryTier = "Working" | "Conversation" | "Semantic" | "Profile" | "Session" | "Episodic";

export default function MemoryPage() {
  const [activeTier, setActiveTier] = useState<MemoryTier>("Working");
  const [searchQuery, setSearchQuery] = useState("");

  const tiers: MemoryTier[] = ["Working", "Conversation", "Semantic", "Profile", "Session", "Episodic"];

  const currentData = memoryEntries[activeTier] || [];

  const filteredData = React.useMemo(() => {
    if (!searchQuery) return currentData;
    return currentData.filter(
      (m) =>
        m.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
        m.userId.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [currentData, searchQuery]);

  const columns = [
    {
      key: "id",
      header: "ID",
      render: (item: any) => <span className="font-mono text-[10px] text-slate-500">{item.id}</span>,
    },
    {
      key: "userId",
      header: "User / Session ID",
      render: (item: any) => <span className="font-mono text-slate-300">{item.userId}</span>,
    },
    {
      key: "content",
      header: "Memory Content Payload",
      render: (item: any) => (
        <span className="font-mono text-xs text-slate-200">{item.content}</span>
      ),
    },
    {
      key: "score",
      header: "Relevance Score",
      render: (item: any) => (
        <span className="rounded bg-blue-500/10 px-2 py-0.5 font-mono text-[10px] font-bold text-blue-400">
          {(item.score * 100).toFixed(0)}%
        </span>
      ),
    },
    {
      key: "ttl",
      header: "Retention / TTL",
      render: (item: any) => (
        <span className="font-mono text-[10px] text-slate-400">{item.ttl}</span>
      ),
    },
    {
      key: "createdAt",
      header: "Timestamp",
      render: (item: any) => (
        <span className="font-mono text-[10px] text-slate-500">{item.createdAt}</span>
      ),
    },
  ];

  return (
    <div className="flex min-h-screen flex-col">
      <Topbar title="6-Tier Context Memory Browser" subtitle="Inspect working, conversation, semantic, profile, session, and episodic memory layers" />

      <main className="flex-1 space-y-6 p-6">
        {/* Tier Info Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Brain className="h-5 w-5 text-blue-400" />
            <span className="text-xs text-slate-300">
              Active Store: Redis + Vector HNSW Memory Subsystem
            </span>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard label="Memory Tiers" value="6 Active Tiers" sub="Short & Long-term" />
          <StatCard label="Working Memory Hits" value="98.4%" trend={+1.2} sub="Zero cold starts" />
          <StatCard label="Semantic Entities" value="1,420" sub="Vector-linked" />
          <StatCard label="Episodic Trace Log" value="8,920" sub="Audited daily" />
        </div>

        {/* 6-Tier Tabs */}
        <div className="flex space-x-2 border-b border-slate-800 pb-2 overflow-x-auto">
          {tiers.map((t) => (
            <button
              key={t}
              onClick={() => {
                setActiveTier(t);
                setSearchQuery("");
              }}
              className={`rounded-lg px-4 py-2 text-xs font-semibold transition-all whitespace-nowrap ${
                activeTier === t
                  ? "bg-blue-600 text-white shadow-md shadow-blue-500/20"
                  : "bg-slate-900/60 text-slate-400 hover:bg-slate-800 hover:text-slate-200"
              }`}
            >
              {t} Memory ({memoryEntries[t]?.length || 0})
            </button>
          ))}
        </div>

        {/* Search & Data Table */}
        <DataTable
          columns={columns}
          data={filteredData}
          searchKey="content"
          searchPlaceholder={`Search ${activeTier} memory entries...`}
        />
      </main>
    </div>
  );
}
