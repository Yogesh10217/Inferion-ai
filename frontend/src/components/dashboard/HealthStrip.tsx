"use client";

import React from "react";
import { systemHealth } from "@/lib/mock-data";
import { StatusBadge } from "./Badge";

export function HealthStrip() {
  return (
    <div className="rounded-xl border border-slate-800 bg-[#070e1c]/80 p-4 backdrop-blur-md">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          System Infrastructure Status
        </h3>
        <span className="flex items-center space-x-1.5 text-[11px] text-emerald-400">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500"></span>
          </span>
          <span>All Core Systems Operational</span>
        </span>
      </div>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
        {systemHealth.map((sys) => (
          <div
            key={sys.name}
            className="flex flex-col justify-between rounded-lg border border-slate-800/80 bg-slate-900/40 p-2.5 transition-all hover:border-slate-700"
          >
            <div className="flex items-center justify-between">
              <span className="truncate text-xs font-medium text-slate-200">{sys.name}</span>
            </div>
            <div className="mt-2 flex items-center justify-between">
              <StatusBadge status={sys.status as any} />
              <span className="font-mono text-[10px] text-slate-400">{sys.latency}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
