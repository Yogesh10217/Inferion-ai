"use client";

import React from "react";
import { routingStages } from "@/lib/mock-data";
import { ArrowRight } from "lucide-react";

export function RoutingPipeline() {
  return (
    <div className="w-full space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-200">
          9-Stage Dynamic Routing Pipeline Architecture
        </h3>
        <span className="text-xs text-slate-400">Deterministic & Dynamic Multi-Criteria Engine</span>
      </div>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-9">
        {routingStages.map((stg, idx) => (
          <div
            key={stg.stage}
            className="relative flex flex-col justify-between rounded-xl border border-slate-800 bg-[#070e1c]/90 p-3 backdrop-blur-md transition-all hover:border-blue-500/50 hover:shadow-lg hover:shadow-blue-500/10"
          >
            <div>
              <div className="flex items-center justify-between">
                <span className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-500/10 font-mono text-[10px] font-bold text-blue-400">
                  {stg.stage}
                </span>
                <span className="text-lg">{stg.icon}</span>
              </div>
              <h4 className="mt-2 text-xs font-semibold text-slate-100">{stg.name}</h4>
              <p className="mt-1 text-[10px] leading-relaxed text-slate-400">{stg.desc}</p>
            </div>
            {idx < routingStages.length - 1 && (
              <div className="hidden lg:block absolute -right-2 top-1/2 -translate-y-1/2 z-10">
                <ArrowRight className="h-3 w-3 text-slate-600" />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
