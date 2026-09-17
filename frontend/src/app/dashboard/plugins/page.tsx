"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { Puzzle, CheckCircle2, PauseCircle, PlayCircle, AlertTriangle, ShieldCheck, Power, Search } from "lucide-react";
import { Topbar } from "@/components/dashboard/Topbar";
import { StatCard } from "@/components/dashboard/StatCard";
import { PluginStateBadge } from "@/components/dashboard/Badge";
import { plugins, PluginState } from "@/lib/mock-data";

export default function PluginsPage() {
  const [pluginList, setPluginList] = useState(plugins);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("All");

  const categories = ["All", "Observability", "Security", "Performance", "Integrations", "FinOps", "Identity"];

  const togglePluginState = (id: string) => {
    setPluginList((prev) =>
      prev.map((p) => {
        if (p.id !== id) return p;
        const nextState: PluginState = p.state === "active" ? "paused" : "active";
        return { ...p, state: nextState };
      })
    );
  };

  const filteredPlugins = React.useMemo(() => {
    return pluginList.filter((p) => {
      const matchesCat = selectedCategory === "All" || p.category === selectedCategory;
      const matchesSearch =
        p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.description.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesCat && matchesSearch;
    });
  }, [pluginList, selectedCategory, searchQuery]);

  return (
    <div className="flex min-h-screen flex-col">
      <Topbar title="Plugin Registry & Lifecycle Manager" subtitle="Manage dynamic middleware extensions, observability, security redaction, and caching plugins" />

      <main className="flex-1 space-y-6 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Puzzle className="h-5 w-5 text-blue-400" />
            <span className="text-xs text-slate-300">
              7-State Hot-Pluggable Plugin Runtime Architecture
            </span>
          </div>
          <span className="text-xs text-slate-400">7 Active Lifecycle Hooks Exposed</span>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard label="Total Installed Plugins" value={pluginList.length} sub="Across 6 categories" />
          <StatCard label="Active Extensions" value={pluginList.filter((p) => p.state === "active").length} trend={+1} sub="Executing on hook points" />
          <StatCard label="Paused / Disabled" value={pluginList.filter((p) => p.state === "paused" || p.state === "disabled").length} sub="Hot-swappable" />
          <StatCard label="Plugin Errors" value={pluginList.filter((p) => p.state === "error").length} sub="Auto-isolated sandbox" />
        </div>

        {/* Category Filters & Search */}
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
          <div className="flex space-x-2 overflow-x-auto pb-1">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition-all whitespace-nowrap ${
                  selectedCategory === cat
                    ? "bg-blue-600 text-white"
                    : "bg-slate-900/60 text-slate-400 hover:bg-slate-800 hover:text-slate-200"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          <div className="relative w-full sm:w-64">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search plugin registry..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full rounded-lg border border-slate-800 bg-slate-900 py-2 pl-9 pr-4 text-xs text-slate-200 focus:border-blue-500 focus:outline-none"
            />
          </div>
        </div>

        {/* Plugin Cards Grid */}
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredPlugins.map((plugin) => (
            <motion.div
              key={plugin.id}
              whileHover={{ y: -2 }}
              className="flex flex-col justify-between rounded-xl border border-slate-800 bg-[#070e1c]/80 p-5 backdrop-blur-md transition-all hover:border-slate-700"
            >
              <div>
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-sm font-semibold text-slate-100">{plugin.name}</h3>
                    <div className="flex items-center space-x-2 mt-0.5">
                      <span className="font-mono text-[10px] text-slate-400">v{plugin.version}</span>
                      <span className="text-[10px] text-slate-500">• {plugin.author}</span>
                    </div>
                  </div>
                  <PluginStateBadge state={plugin.state} />
                </div>

                <p className="mt-3 text-xs leading-relaxed text-slate-400">
                  {plugin.description}
                </p>

                <div className="mt-4">
                  <span className="block text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-1">
                    Intercept Hooks:
                  </span>
                  <div className="flex flex-wrap gap-1">
                    {plugin.hooks.map((hk) => (
                      <span
                        key={hk}
                        className="rounded border border-slate-800 bg-slate-900 px-2 py-0.5 font-mono text-[10px] text-blue-400"
                      >
                        {hk}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="mt-6 flex items-center justify-between border-t border-slate-800/80 pt-4">
                <span className="rounded bg-slate-900 px-2 py-1 font-mono text-[10px] text-slate-400">
                  {plugin.category}
                </span>

                <button
                  onClick={() => togglePluginState(plugin.id)}
                  disabled={plugin.state === "error" || plugin.state === "uninstalling"}
                  className={`inline-flex items-center justify-center rounded-lg px-3 py-1.5 text-xs font-semibold transition-all ${
                    plugin.state === "active"
                      ? "border border-amber-500/30 bg-amber-500/10 text-amber-400 hover:bg-amber-500/20"
                      : plugin.state === "paused" || plugin.state === "installed"
                      ? "border border-emerald-500/30 bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20"
                      : "opacity-40 cursor-not-allowed bg-slate-900 text-slate-500"
                  }`}
                >
                  <Power className="mr-1.5 h-3.5 w-3.5" />
                  {plugin.state === "active" ? "Pause Plugin" : "Activate Plugin"}
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      </main>
    </div>
  );
}
