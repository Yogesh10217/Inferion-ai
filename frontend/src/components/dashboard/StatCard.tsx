"use client";

import React from "react";
import { motion } from "framer-motion";
import { TrendingUp, TrendingDown } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string | number;
  sub?: string;
  trend?: number; // positive = up, negative = down
  icon?: React.ReactNode;
  accent?: string; // tailwind color class for the icon bg
  delay?: number;
}

export function StatCard({
  label,
  value,
  sub,
  trend,
  icon,
  accent = "bg-slate-50",
  delay = 0,
}: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay, ease: [0.16, 1, 0.3, 1] }}
      className="bg-white rounded-2xl border border-slate-200/60 p-5 hover:shadow-sm hover:border-slate-300 transition-all"
    >
      <div className="flex items-start justify-between mb-3">
        <span className="text-[12px] font-medium text-[#64748b]">{label}</span>
        {icon && (
          <div className={`p-2 rounded-xl ${accent}`}>{icon}</div>
        )}
      </div>
      <div className="font-display font-bold text-[24px] text-[#0a1b33] leading-none mb-1.5">
        {value}
      </div>
      <div className="flex items-center gap-1.5">
        {trend !== undefined && (
          <span
            className={`flex items-center gap-0.5 text-[11px] font-semibold ${
              trend >= 0 ? "text-emerald-600" : "text-red-500"
            }`}
          >
            {trend >= 0 ? (
              <TrendingUp className="w-3 h-3" />
            ) : (
              <TrendingDown className="w-3 h-3" />
            )}
            {Math.abs(trend)}%
          </span>
        )}
        {sub && (
          <span className="text-[11px] text-slate-400">{sub}</span>
        )}
      </div>
    </motion.div>
  );
}
