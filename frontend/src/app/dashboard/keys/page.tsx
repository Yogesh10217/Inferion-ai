"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { Key, Plus, ShieldCheck, Copy, Check, Trash2, RotateCw } from "lucide-react";
import { Topbar } from "@/components/dashboard/Topbar";
import { StatCard } from "@/components/dashboard/StatCard";
import { RoleBadge, StatusBadge } from "@/components/dashboard/Badge";
import { DataTable } from "@/components/dashboard/DataTable";
import { Modal } from "@/components/dashboard/Modal";
import { apiKeys } from "@/lib/mock-data";

export default function KeysPage() {
  const [keysList, setKeysList] = useState(apiKeys);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  // New Key Form
  const [keyName, setKeyName] = useState("");
  const [org, setOrg] = useState("Acme Corp");
  const [workspace, setWorkspace] = useState("Engineering");
  const [role, setRole] = useState("developer");

  const handleCopy = (keyStr: string) => {
    navigator.clipboard.writeText(keyStr);
    setCopiedKey(keyStr);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const handleCreate = () => {
    if (!keyName) return;
    const newKeyItem = {
      id: `key-00${keysList.length + 1}`,
      key: `sk_live_${workspace.toLowerCase()}_${Math.random().toString(36).substring(2, 9)}`,
      name: keyName,
      org,
      workspace,
      role,
      status: "active",
      lastUsed: "Just now",
      quotaUsed: 0,
      quotaMax: 10000,
      costMtd: 0,
    };
    setKeysList([newKeyItem, ...keysList]);
    setKeyName("");
    setCreateModalOpen(false);
  };

  const handleRevoke = (id: string) => {
    setKeysList((prev) =>
      prev.map((k) => (k.id === id ? { ...k, status: "revoked" } : k))
    );
  };

  const columns = [
    {
      key: "name",
      header: "Key Name / ID",
      render: (item: typeof apiKeys[0]) => (
        <div>
          <div className="font-semibold text-slate-200">{item.name}</div>
          <div className="flex items-center space-x-2 mt-0.5">
            <span className="font-mono text-[10px] text-slate-400">{item.key}</span>
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleCopy(item.key);
              }}
              className="text-slate-500 hover:text-slate-300"
            >
              {copiedKey === item.key ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
            </button>
          </div>
        </div>
      ),
    },
    {
      key: "workspace",
      header: "Workspace / Org",
      render: (item: typeof apiKeys[0]) => (
        <div>
          <div className="text-slate-300">{item.workspace}</div>
          <div className="text-[10px] text-slate-500">{item.org}</div>
        </div>
      ),
    },
    {
      key: "role",
      header: "RBAC Role",
      render: (item: typeof apiKeys[0]) => <RoleBadge role={item.role as any} />,
    },
    {
      key: "status",
      header: "Status",
      render: (item: typeof apiKeys[0]) => <StatusBadge status={item.status as any} />,
    },
    {
      key: "quotaUsed",
      header: "Daily Quota Usage",
      render: (item: typeof apiKeys[0]) => (
        <div className="w-32">
          <div className="flex justify-between text-[10px] text-slate-400 mb-1">
            <span>{item.quotaUsed.toLocaleString()}</span>
            <span>{item.quotaMax.toLocaleString()} req</span>
          </div>
          <div className="h-1.5 w-full rounded-full bg-slate-800">
            <div
              className={`h-1.5 rounded-full ${
                item.quotaUsed / item.quotaMax > 0.8 ? "bg-amber-500" : "bg-blue-500"
              }`}
              style={{ width: `${Math.min((item.quotaUsed / item.quotaMax) * 100, 100)}%` }}
            />
          </div>
        </div>
      ),
    },
    {
      key: "costMtd",
      header: "MTD Cost",
      render: (item: typeof apiKeys[0]) => (
        <span className="font-mono text-slate-200">${item.costMtd.toFixed(2)}</span>
      ),
    },
    {
      key: "actions",
      header: "Actions",
      render: (item: typeof apiKeys[0]) => (
        <div className="flex items-center space-x-2">
          {item.status === "active" && (
            <button
              onClick={() => handleRevoke(item.id)}
              className="rounded p-1 text-slate-400 hover:bg-rose-500/10 hover:text-rose-400"
              title="Revoke Key"
            >
              <Trash2 className="h-3.5 w-3.5" />
            </button>
          )}
        </div>
      ),
    },
  ];

  return (
    <div className="flex min-h-screen flex-col">
      <Topbar title="API Keys & Access Management" subtitle="Manage Organization & Workspace API keys with granular RBAC permissions" />

      <main className="flex-1 space-y-6 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="h-4 w-4 text-emerald-400" />
            <span className="text-xs text-slate-300">SHA-256 Hashed Keys • TLS 1.3 Strict Enforcement</span>
          </div>
          <button
            onClick={() => setCreateModalOpen(true)}
            className="inline-flex items-center justify-center rounded-lg bg-blue-600 px-4 py-2 text-xs font-semibold text-white hover:bg-blue-500"
          >
            <Plus className="mr-1.5 h-3.5 w-3.5" /> Create New Key
          </button>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard label="Total API Keys" value={keysList.length} sub="Across 3 organizations" />
          <StatCard label="Active Keys" value={keysList.filter((k) => k.status === "active").length} trend={+2} sub="Enforced via RBAC" />
          <StatCard label="Revoked Keys" value={keysList.filter((k) => k.status === "revoked").length} sub="Audit trail active" />
          <StatCard label="Total Cost MTD" value={`$${keysList.reduce((acc, k) => acc + k.costMtd, 0).toFixed(2)}`} sub="Across all keys" />
        </div>

        <DataTable
          columns={columns}
          data={keysList}
          searchKey="name"
          searchPlaceholder="Search key name or ID..."
        />
      </main>

      <Modal
        open={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        title="Create API Key"
        subtitle="Generate a new sk_live API key with scoped role permissions"
      >
        <div className="space-y-4 text-xs">
          <div>
            <label className="block text-slate-400 mb-1">Key Description / Name</label>
            <input
              type="text"
              placeholder="e.g. Production Analytics Worker"
              value={keyName}
              onChange={(e) => setKeyName(e.target.value)}
              className="w-full rounded-lg border border-slate-800 bg-slate-900 p-2.5 text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-400 mb-1">Organization</label>
              <select
                value={org}
                onChange={(e) => setOrg(e.target.value)}
                className="w-full rounded-lg border border-slate-800 bg-slate-900 p-2.5 text-slate-200"
              >
                <option value="Acme Corp">Acme Corp</option>
                <option value="TechStart Inc">TechStart Inc</option>
              </select>
            </div>
            <div>
              <label className="block text-slate-400 mb-1">Workspace</label>
              <select
                value={workspace}
                onChange={(e) => setWorkspace(e.target.value)}
                className="w-full rounded-lg border border-slate-800 bg-slate-900 p-2.5 text-slate-200"
              >
                <option value="Engineering">Engineering</option>
                <option value="Sales">Sales</option>
                <option value="Finance">Finance</option>
                <option value="HR">HR</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-slate-400 mb-1">RBAC Scope Role</label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="w-full rounded-lg border border-slate-800 bg-slate-900 p-2.5 text-slate-200"
            >
              <option value="developer">Developer (Full inference access)</option>
              <option value="admin">Admin (Full administrative control)</option>
              <option value="viewer">Viewer (Read-only inference)</option>
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
              onClick={handleCreate}
              className="rounded-lg bg-blue-600 px-4 py-2 font-semibold text-white hover:bg-blue-500"
            >
              Generate Key
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
