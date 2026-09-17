"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { Building2, ChevronRight, ChevronDown, Users, Plus, Shield, Layers } from "lucide-react";
import { Topbar } from "@/components/dashboard/Topbar";
import { StatCard } from "@/components/dashboard/StatCard";
import { StatusBadge } from "@/components/dashboard/Badge";
import { Modal } from "@/components/dashboard/Modal";
import { organizations } from "@/lib/mock-data";

export default function OrgsPage() {
  const [expandedOrg, setExpandedOrg] = useState<string>("org-001");
  const [createModalOpen, setCreateModalOpen] = useState(false);

  return (
    <div className="flex min-h-screen flex-col">
      <Topbar title="Tenants & Organizations" subtitle="Multi-tenant hierarchy tree, workspace isolation, user roles, and quota governance" />

      <main className="flex-1 space-y-6 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Building2 className="h-5 w-5 text-blue-400" />
            <span className="text-xs text-slate-300">Strict Multi-Tenant Isolation Active (Logical DB + Redis key scoping)</span>
          </div>
          <button
            onClick={() => setCreateModalOpen(true)}
            className="inline-flex items-center justify-center rounded-lg bg-blue-600 px-4 py-2 text-xs font-semibold text-white hover:bg-blue-500"
          >
            <Plus className="mr-1.5 h-3.5 w-3.5" /> Create Organization
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard label="Total Organizations" value={organizations.length} sub="Enterprise, Growth, Trial" />
          <StatCard label="Total Workspaces" value="8 Workspaces" sub="Across all tenants" />
          <StatCard label="Total Provisioned Users" value="43 Users" sub="RBAC Enforced" />
          <StatCard label="Tenant Isolation Level" value="Level 3" sub="Logical DB + Key namespace" />
        </div>

        {/* Hierarchy Tree */}
        <div className="space-y-4">
          {organizations.map((org) => {
            const isExpanded = expandedOrg === org.id;
            return (
              <div
                key={org.id}
                className="rounded-xl border border-slate-800 bg-[#070e1c]/80 backdrop-blur-md overflow-hidden"
              >
                {/* Org Header */}
                <div
                  onClick={() => setExpandedOrg(isExpanded ? "" : org.id)}
                  className="flex cursor-pointer items-center justify-between p-4 hover:bg-slate-800/40 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    {isExpanded ? (
                      <ChevronDown className="h-4 w-4 text-blue-400" />
                    ) : (
                      <ChevronRight className="h-4 w-4 text-slate-500" />
                    )}
                    <Building2 className="h-5 w-5 text-blue-400" />
                    <div>
                      <h3 className="text-sm font-semibold text-slate-100">{org.name}</h3>
                      <span className="font-mono text-[10px] text-slate-500">{org.id}</span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-4">
                    <span className="rounded-md border border-slate-800 bg-slate-900 px-2.5 py-1 text-xs font-medium text-slate-300">
                      {org.plan} Plan
                    </span>
                    <StatusBadge status={org.status as any} />
                    <span className="text-xs text-slate-400">
                      {org.workspaces.length} Workspaces
                    </span>
                  </div>
                </div>

                {/* Workspaces List (Expanded) */}
                {isExpanded && (
                  <div className="border-t border-slate-800 bg-slate-900/40 p-4 space-y-3">
                    <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                      Workspaces in {org.name}
                    </h4>

                    <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
                      {org.workspaces.map((ws) => (
                        <div
                          key={ws.id}
                          className="rounded-lg border border-slate-800 bg-[#070e1c] p-4 transition-all hover:border-slate-700"
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-semibold text-xs text-slate-200">{ws.name}</span>
                            <span className="font-mono text-[10px] text-slate-500">{ws.id}</span>
                          </div>

                          <div className="mt-3 space-y-2 text-xs">
                            <div className="flex justify-between text-slate-400">
                              <span>Users:</span>
                              <span className="font-mono text-slate-200">{ws.users} members</span>
                            </div>
                            <div className="flex justify-between text-slate-400">
                              <span>Monthly Budget:</span>
                              <span className="font-mono text-slate-200">${ws.budgetMtd}</span>
                            </div>
                            <div>
                              <div className="flex justify-between text-[10px] text-slate-400 mb-1">
                                <span>Daily Quota:</span>
                                <span>{ws.usedDay.toLocaleString()} / {ws.quotaDay.toLocaleString()} req</span>
                              </div>
                              <div className="h-1.5 w-full rounded-full bg-slate-800">
                                <div
                                  className="h-1.5 rounded-full bg-blue-500"
                                  style={{ width: `${(ws.usedDay / ws.quotaDay) * 100}%` }}
                                />
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </main>

      {/* Create Org Modal */}
      <Modal
        open={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        title="Create New Organization"
        subtitle="Provision a tenant with isolated database workspace schemas and quota policies"
      >
        <div className="space-y-4 text-xs">
          <div>
            <label className="block text-slate-400 mb-1">Organization Name</label>
            <input
              type="text"
              placeholder="e.g. Apex Global Systems"
              className="w-full rounded-lg border border-slate-800 bg-slate-900 p-2.5 text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-slate-400 mb-1">Subscription Plan</label>
            <select className="w-full rounded-lg border border-slate-800 bg-slate-900 p-2.5 text-slate-200">
              <option value="Enterprise">Enterprise (Unlimited Workspaces + Dedicated Ollama cluster)</option>
              <option value="Growth">Growth (Up to 10 Workspaces)</option>
              <option value="Startup">Startup (Up to 3 Workspaces)</option>
            </select>
          </div>

          <div className="flex justify-end space-x-2 pt-2">
            <button
              onClick={() => setCreateModalOpen(false)}
              className="rounded-lg border border-slate-800 bg-slate-900 px-4 py-2 text-slate-400 hover:bg-slate-800"
            >
              Cancel
            </button>
            <button
              onClick={() => {
                alert("Organization provisioned with isolated tenant schemas!");
                setCreateModalOpen(false);
              }}
              className="rounded-lg bg-blue-600 px-4 py-2 font-semibold text-white hover:bg-blue-500"
            >
              Provision Organization
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
