"use client";

import React from "react";
import { Bell, Search } from "lucide-react";

interface TopbarProps {
  title: string;
  subtitle?: string;
}

export function Topbar({ title, subtitle }: TopbarProps) {
  return (
    <header className="h-14 bg-white border-b border-slate-200/60 flex items-center justify-between px-6 flex-shrink-0">
      <div>
        <h1 className="font-display font-semibold text-[15px] text-[#0a1b33] leading-none">
          {title}
        </h1>
        {subtitle && (
          <p className="text-[11px] text-slate-400 mt-0.5">{subtitle}</p>
        )}
      </div>

      <div className="flex items-center gap-3">
        {/* Search */}
        <div className="relative hidden sm:block">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            placeholder="Search..."
            className="pl-8 pr-3 py-1.5 rounded-lg border border-slate-200 text-[12px] text-[#0a1b33] bg-slate-50 focus:outline-none focus:ring-1 focus:ring-[#0a152d] w-44"
          />
        </div>

        {/* Notification */}
        <button className="relative p-2 rounded-lg hover:bg-slate-50 transition-colors">
          <Bell className="w-4 h-4 text-slate-400" />
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-emerald-500" />
        </button>

        {/* Avatar */}
        <div className="w-7 h-7 rounded-full bg-[#0a152d] flex items-center justify-center text-white text-[11px] font-bold cursor-pointer">
          A
        </div>
      </div>
    </header>
  );
}
