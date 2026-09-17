"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { Settings, Server, Shield, Database, Bell, Save, CheckCircle2, Moon, Sun } from "lucide-react";
import { Topbar } from "@/components/dashboard/Topbar";
import { API_BASE_URL } from "@/lib/mock-data";

export default function SettingsPage() {
  const [apiUrl, setApiUrl] = useState(API_BASE_URL);
  const [redisUrl, setRedisUrl] = useState("redis://localhost:6379/0");
  const [ollamaUrl, setOllamaUrl] = useState("http://localhost:11434");
  const [defaultModel, setDefaultModel] = useState("gpt-4o");
  const [logLevel, setLogLevel] = useState("INFO");
  const [savedSuccess, setSavedSuccess] = useState(false);

  const handleSave = () => {
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  return (
    <div className="flex min-h-screen flex-col">
      <Topbar title="Control Plane Settings" subtitle="Configure backend API endpoints, cache settings, default models, and system logging" />

      <main className="flex-1 space-y-6 p-6 max-w-4xl">
        {savedSuccess && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center space-x-2 rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4 text-xs font-semibold text-emerald-400"
          >
            <CheckCircle2 className="h-4 w-4" />
            <span>Control plane configuration saved successfully! Active endpoints updated.</span>
          </motion.div>
        )}

        {/* Endpoint Configuration */}
        <div className="rounded-xl border border-slate-800 bg-[#070e1c]/80 p-5 backdrop-blur-md space-y-4">
          <div className="flex items-center space-x-2 border-b border-slate-800 pb-3">
            <Server className="h-4 w-4 text-blue-400" />
            <h3 className="text-sm font-semibold text-slate-100">API Gateway & Infrastructure Endpoints</h3>
          </div>

          <div className="space-y-4 text-xs">
            <div>
              <label className="block text-slate-400 mb-1">FastAPI Gateway Base URL</label>
              <input
                type="text"
                value={apiUrl}
                onChange={(e) => setApiUrl(e.target.value)}
                className="w-full rounded-lg border border-slate-800 bg-slate-900 p-2.5 font-mono text-slate-200 focus:border-blue-500 focus:outline-none"
              />
              <p className="mt-1 text-[10px] text-slate-500">
                Change to point this admin UI to a live backend deployment or local Docker container.
              </p>
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label className="block text-slate-400 mb-1">Redis Cache URL</label>
                <input
                  type="text"
                  value={redisUrl}
                  onChange={(e) => setRedisUrl(e.target.value)}
                  className="w-full rounded-lg border border-slate-800 bg-slate-900 p-2.5 font-mono text-slate-200 focus:border-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Ollama Local Instance URL</label>
                <input
                  type="text"
                  value={ollamaUrl}
                  onChange={(e) => setOllamaUrl(e.target.value)}
                  className="w-full rounded-lg border border-slate-800 bg-slate-900 p-2.5 font-mono text-slate-200 focus:border-blue-500 focus:outline-none"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Inference Defaults */}
        <div className="rounded-xl border border-slate-800 bg-[#070e1c]/80 p-5 backdrop-blur-md space-y-4">
          <div className="flex items-center space-x-2 border-b border-slate-800 pb-3">
            <Database className="h-4 w-4 text-blue-400" />
            <h3 className="text-sm font-semibold text-slate-100">Inference Defaults & Routing Policy</h3>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 text-xs">
            <div>
              <label className="block text-slate-400 mb-1">Default Fallback Model</label>
              <select
                value={defaultModel}
                onChange={(e) => setDefaultModel(e.target.value)}
                className="w-full rounded-lg border border-slate-800 bg-slate-900 p-2.5 text-slate-200"
              >
                <option value="gpt-4o">OpenAI GPT-4o (Primary)</option>
                <option value="llama3">Ollama Llama3 (Local Fallback)</option>
                <option value="claude-3-5-sonnet">Anthropic Claude 3.5 Sonnet</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-400 mb-1">Gateway Log Level</label>
              <select
                value={logLevel}
                onChange={(e) => setLogLevel(e.target.value)}
                className="w-full rounded-lg border border-slate-800 bg-slate-900 p-2.5 text-slate-200"
              >
                <option value="DEBUG">DEBUG (Verbose trace logs)</option>
                <option value="INFO">INFO (Standard production logs)</option>
                <option value="WARNING">WARNING (Errors & Warnings only)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end pt-2">
          <button
            onClick={handleSave}
            className="inline-flex items-center justify-center rounded-lg bg-blue-600 px-5 py-2.5 text-xs font-semibold text-white shadow-lg shadow-blue-500/20 hover:bg-blue-500"
          >
            <Save className="mr-2 h-4 w-4" /> Save Configuration
          </button>
        </div>
      </main>
    </div>
  );
}
