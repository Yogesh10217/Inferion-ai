"use client";

import React from "react";
import { motion } from "framer-motion";

interface FeatureCardProps {
  icon: string;
  title: string;
  description: string;
  delay?: number;
}

const FeatureCard: React.FC<FeatureCardProps> = ({ icon, title, description, delay = 0 }) => (
  <motion.div
    initial={{ opacity: 0, y: 24 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
    transition={{ duration: 0.6, delay, ease: [0.16, 1, 0.3, 1] }}
    className="p-6 bg-white rounded-3xl border border-slate-200/60 shadow-sm hover:shadow-md hover:border-slate-300 transition-all group"
  >
    <div className="text-2xl mb-3">{icon}</div>
    <h3 className="font-display font-semibold text-[15px] text-[#0a1b33] mb-2">{title}</h3>
    <p className="text-[13px] text-[#64748b] leading-relaxed">{description}</p>
  </motion.div>
);

interface StepProps {
  number: string;
  title: string;
  code: string;
  delay?: number;
}

const QuickStartStep: React.FC<StepProps> = ({ number, title, code, delay = 0 }) => (
  <motion.div
    initial={{ opacity: 0, x: -20 }}
    whileInView={{ opacity: 1, x: 0 }}
    viewport={{ once: true }}
    transition={{ duration: 0.6, delay, ease: [0.16, 1, 0.3, 1] }}
    className="flex gap-4"
  >
    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#0a152d] text-white text-xs font-bold flex items-center justify-center">
      {number}
    </div>
    <div className="flex-1">
      <p className="text-[13px] font-semibold text-[#0a1b33] mb-2">{title}</p>
      <div className="bg-slate-900 rounded-2xl px-4 py-3 font-mono text-[11px] text-slate-300 leading-relaxed">
        {code}
      </div>
    </div>
  </motion.div>
);

const FEATURES = [
  {
    icon: "🔀",
    title: "9-Stage Intelligent Router",
    description: "Routes every AI request to the optimal provider — cost, latency, capability, and health all weighed automatically.",
  },
  {
    icon: "🏢",
    title: "Enterprise Multi-Tenancy",
    description: "Full org → workspace → user hierarchy with per-tenant budgets, API keys, RBAC roles, and complete resource isolation.",
  },
  {
    icon: "🤖",
    title: "Autonomous Agent Framework",
    description: "Four planning strategies (ZeroShot, ReAct, Plan-Execute, Tree of Thought) with tool use, approval gates, and human-in-the-loop.",
  },
  {
    icon: "🧠",
    title: "6-Tier Memory Platform",
    description: "Working, Conversation, Semantic, Profile, Session, and Episodic tiers with composite ranking to retrieve the most relevant memories.",
  },
  {
    icon: "📚",
    title: "Knowledge & RAG Pipeline",
    description: "Ingest any document collection, chunk → embed → store in Pinecone/Milvus/Qdrant/FAISS, then hybrid semantic + keyword search with reranking.",
  },
  {
    icon: "⚡",
    title: "DAG Workflow Engine",
    description: "Define multi-step AI pipelines as code. Parallel branches, conditional edges, checkpoint & recovery, and reusable templates.",
  },
  {
    icon: "🛡️",
    title: "Resilience & Reliability",
    description: "Automatic failover across providers, circuit breakers, exponential backoff, bulkhead isolation, and SLO error-budget tracking.",
  },
  {
    icon: "💰",
    title: "FinOps & Budget Control",
    description: "Per-tenant cost attribution, hard budget limits, subscription plans, automated invoicing, anomaly detection, and chargeback reports.",
  },
  {
    icon: "🔐",
    title: "Security & Compliance",
    description: "JWT/API key auth, SOC2/GDPR controls, audit logging, content filtering, IP allowlists, and SSO integration.",
  },
];

const MEMORY_TIERS = [
  { color: "bg-red-400", label: "Working", desc: "Current execution scratchpad" },
  { color: "bg-orange-400", label: "Conversation", desc: "Multi-turn message history" },
  { color: "bg-yellow-400", label: "Semantic", desc: "Learned facts & domain knowledge" },
  { color: "bg-emerald-400", label: "Profile", desc: "User preferences & patterns" },
  { color: "bg-blue-400", label: "Session", desc: "Active project context" },
  { color: "bg-purple-400", label: "Episodic", desc: "Historical runs for recall" },
];

const STACK_ITEMS = [
  { name: "FastAPI", icon: "⚡", desc: "High-performance async Python API gateway" },
  { name: "PostgreSQL", icon: "🐘", desc: "Primary relational database for all entities" },
  { name: "Redis", icon: "🔴", desc: "Token-bucket rate limiting & response caching" },
  { name: "Prometheus", icon: "📊", desc: "Metrics scraping and alerting rules" },
  { name: "Grafana", icon: "📈", desc: "9 pre-built real-time visual dashboards" },
  { name: "Docker", icon: "🐳", desc: "Full-stack containerized deployment" },
];

export const ContentSections: React.FC = () => {
  return (
    <div className="w-full max-w-[1400px] mx-auto space-y-6 mt-6 px-0">

      {/* ── SECTION 1: What Is Inferion AI ─────────────────────────── */}
      <motion.section
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        className="bg-white rounded-[40px] border border-slate-200/50 shadow-sm overflow-hidden"
      >
        <div className="px-8 md:px-16 py-12 md:py-14">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-100 text-[11px] font-semibold text-blue-700 mb-4">
                ⚡ One platform. Infinite scale.
              </div>
              <h2 className="font-display text-[32px] md:text-[40px] font-semibold text-[#0a1b33] leading-tight mb-4">
                What is<br />Inferion AI?
              </h2>
              <p className="text-[14px] text-[#64748b] leading-relaxed mb-6">
                An <strong className="text-[#0a1b33]">enterprise-grade AI gateway and autonomous agent platform</strong> that sits between your apps and every AI model in the world — adding intelligent routing, multi-tenancy, billing, compliance, RAG, memory, and full autonomous agent execution.
              </p>
              <p className="text-[14px] text-[#64748b] leading-relaxed">
                100% OpenAI-compatible. Change one line of code to gain enterprise control — zero other changes required.
              </p>
            </div>

            <div className="space-y-3">
              {[
                { problem: "💸 Runaway AI costs", fix: "Route cheaply — smart model selection per task" },
                { problem: "🔒 No access control", fix: "JWT, RBAC, API keys, SSO out-of-the-box" },
                { problem: "📊 Zero visibility", fix: "Grafana dashboards + full audit logs" },
                { problem: "🔀 Vendor lock-in", fix: "Automatic failover: OpenAI → Ollama → Anthropic" },
                { problem: "🤖 LLMs just answer", fix: "Autonomous agents that actually do things" },
              ].map((item, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: 20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: i * 0.08 }}
                  className="flex items-start gap-3 p-3.5 rounded-2xl border border-slate-100 bg-slate-50/60"
                >
                  <span className="text-xs text-slate-500 flex-1">{item.problem}</span>
                  <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-100 px-2 py-0.5 rounded-full whitespace-nowrap">{item.fix}</span>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </motion.section>

      {/* ── SECTION 2: How It Works ─────────────────────────────────── */}
      <motion.section
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        className="bg-white rounded-[40px] border border-slate-200/50 shadow-sm overflow-hidden"
      >
        <div className="px-8 md:px-16 py-12 md:py-14">
          <div className="text-center mb-10">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-100 border border-slate-200 text-[11px] font-semibold text-slate-600 mb-3">
              🏗️ Architecture
            </div>
            <h2 className="font-display text-[28px] md:text-[34px] font-semibold text-[#0a1b33]">
              How Inferion AI Works
            </h2>
            <p className="text-[14px] text-[#64748b] mt-2 max-w-xl mx-auto">
              A transparent gateway layer that intelligently proxies, enriches, and governs every AI request.
            </p>
          </div>

          {/* Flow Diagram */}
          <div className="flex flex-wrap items-center justify-center gap-2 mb-10">
            {[
              { label: "Your App", sub: "Any SDK or REST client", color: "bg-blue-50 border-blue-100 text-blue-700" },
              { label: "→", sub: "", color: "bg-transparent border-transparent text-slate-400 text-lg font-bold" },
              { label: "Inferion AI", sub: "Gateway · Auth · Routing", color: "bg-[#0a152d] border-[#0a152d] text-white" },
              { label: "→", sub: "", color: "bg-transparent border-transparent text-slate-400 text-lg font-bold" },
              { label: "OpenAI", sub: "Cloud LLMs", color: "bg-purple-50 border-purple-100 text-purple-700" },
              { label: "→", sub: "", color: "bg-transparent border-transparent text-slate-400 text-lg font-bold" },
              { label: "Ollama", sub: "Local models", color: "bg-emerald-50 border-emerald-100 text-emerald-700" },
              { label: "→", sub: "", color: "bg-transparent border-transparent text-slate-400 text-lg font-bold" },
              { label: "Anthropic", sub: "& more providers", color: "bg-amber-50 border-amber-100 text-amber-700" },
            ].map((node, i) =>
              node.sub === "" ? (
                <span key={i} className="text-slate-400 text-2xl font-light hidden sm:block">→</span>
              ) : (
                <div key={i} className={`px-4 py-3 rounded-2xl border text-center min-w-[100px] ${node.color}`}>
                  <div className="text-[12px] font-bold">{node.label}</div>
                  <div className="text-[10px] opacity-70 mt-0.5">{node.sub}</div>
                </div>
              )
            )}
          </div>

          {/* 9-Stage Router */}
          <div className="bg-slate-50 rounded-3xl border border-slate-200/60 p-6">
            <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-4">9-Stage Intelligent Routing Pipeline</p>
            <div className="flex flex-wrap gap-2">
              {[
                "1. Capability Filter",
                "2. Rule Evaluation",
                "3. Policy Check",
                "4. Health Check",
                "5. Weighted Scoring",
                "6. Provider Ranking",
                "7. Selection",
                "8. Failover",
                "9. Final Decision",
              ].map((stage, i) => (
                <span
                  key={i}
                  className="px-3 py-1.5 bg-white text-[11px] font-semibold text-[#0a1b33] rounded-full border border-slate-200/70 shadow-sm"
                >
                  {stage}
                </span>
              ))}
            </div>
          </div>
        </div>
      </motion.section>

      {/* ── SECTION 3: 9 Feature Cards ──────────────────────────────── */}
      <motion.section
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.7 }}
        className="bg-white rounded-[40px] border border-slate-200/50 shadow-sm overflow-hidden"
      >
        <div className="px-8 md:px-16 py-12 md:py-14">
          <div className="text-center mb-10">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-100 border border-slate-200 text-[11px] font-semibold text-slate-600 mb-3">
              🚀 Platform Capabilities
            </div>
            <h2 className="font-display text-[28px] md:text-[34px] font-semibold text-[#0a1b33]">
              Everything You Need to Ship AI at Scale
            </h2>
            <p className="text-[14px] text-[#64748b] mt-2">
              One self-hosted platform replacing 5+ SaaS tools.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {FEATURES.map((f, i) => (
              <FeatureCard key={i} {...f} delay={i * 0.06} />
            ))}
          </div>
        </div>
      </motion.section>

      {/* ── SECTION 4: Memory Tiers ──────────────────────────────────── */}
      <motion.section
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.7 }}
        className="bg-white rounded-[40px] border border-slate-200/50 shadow-sm overflow-hidden"
      >
        <div className="px-8 md:px-16 py-12 md:py-14">
          <div className="grid md:grid-cols-2 gap-12 items-start">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-50 border border-purple-100 text-[11px] font-semibold text-purple-700 mb-4">
                🧠 6-Tier Memory Platform
              </div>
              <h2 className="font-display text-[28px] md:text-[34px] font-semibold text-[#0a1b33] leading-tight mb-3">
                Your AI Remembers Everything
              </h2>
              <p className="text-[14px] text-[#64748b] leading-relaxed mb-6">
                Six memory tiers ensure the right context is retrieved at the right moment — across sessions, users, and time. Composite ranking combines similarity, recency, importance, and confidence.
              </p>
              <div className="bg-slate-900 rounded-2xl p-4 font-mono text-[11px] text-slate-300 leading-relaxed">
                <span className="text-emerald-400"># Store a memory</span><br />
                <span className="text-slate-400">client.memory.create(</span><br />
                <span className="text-slate-400">  content=</span><span className="text-amber-300">&quot;User prefers concise Python code&quot;</span><br />
                <span className="text-slate-400">)</span><br /><br />
                <span className="text-emerald-400"># Semantic search</span><br />
                <span className="text-slate-400">results = client.memory.search(</span><br />
                <span className="text-amber-300">  &quot;What coding style does this user prefer?&quot;</span><br />
                <span className="text-slate-400">)</span>
              </div>
            </div>

            <div className="space-y-3">
              {MEMORY_TIERS.map((tier, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: 20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: i * 0.08 }}
                  className="flex items-center gap-3 p-3.5 rounded-2xl border border-slate-100 bg-slate-50/60"
                >
                  <div className={`w-3 h-3 rounded-full flex-shrink-0 ${tier.color}`} />
                  <div>
                    <span className="text-[13px] font-semibold text-[#0a1b33]">{tier.label}</span>
                    <span className="text-[12px] text-[#64748b] ml-2">{tier.desc}</span>
                  </div>
                </motion.div>
              ))}

              <div className="mt-4 p-4 rounded-2xl bg-slate-900 text-[11px] text-slate-400 font-mono leading-relaxed">
                <span className="text-slate-500">Score =</span>{" "}
                <span className="text-blue-400">(0.4 × Similarity)</span>{" "}
                <span className="text-slate-500">+</span>{" "}
                <span className="text-emerald-400">(0.2 × Recency)</span>{" "}
                <span className="text-slate-500">+</span>{" "}
                <span className="text-amber-400">(0.2 × Importance)</span>{" "}
                <span className="text-slate-500">+</span>{" "}
                <span className="text-purple-400">(0.2 × Confidence)</span>
              </div>
            </div>
          </div>
        </div>
      </motion.section>

      {/* ── SECTION 5: Quick Start ───────────────────────────────────── */}
      <motion.section
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.7 }}
        className="bg-white rounded-[40px] border border-slate-200/50 shadow-sm overflow-hidden"
      >
        <div className="px-8 md:px-16 py-12 md:py-14">
          <div className="grid md:grid-cols-2 gap-12 items-start">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-100 text-[11px] font-semibold text-emerald-700 mb-4">
                ⚡ Quick Start
              </div>
              <h2 className="font-display text-[28px] md:text-[34px] font-semibold text-[#0a1b33] leading-tight mb-3">
                Up and Running in Minutes
              </h2>
              <p className="text-[14px] text-[#64748b] leading-relaxed mb-8">
                Clone, configure, and launch. The interactive Swagger docs at <span className="font-mono text-blue-600 text-[12px]">localhost:8002/docs</span> let you explore every endpoint immediately.
              </p>

              <div className="space-y-5">
                <QuickStartStep number="1" title="Clone the repository" code={`git clone https://github.com/Yogesh10217/Inferion-ai.git\ncd Inferion-ai`} delay={0.1} />
                <QuickStartStep number="2" title="Install dependencies" code={`python -m venv .venv\n.venv\\Scripts\\activate   # Windows\npip install -r requirements.txt`} delay={0.2} />
                <QuickStartStep number="3" title="Configure & launch" code={`cp .env.example .env\n# Add your OPENAI_API_KEY to .env\nuvicorn app.main:app --port 8002 --reload`} delay={0.3} />
              </div>
            </div>

            <div className="space-y-4">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-100 text-[11px] font-semibold text-blue-700 mb-2">
                🐳 Full Stack via Docker
              </div>
              <div className="bg-slate-900 rounded-2xl p-4 font-mono text-[12px] text-slate-300 leading-relaxed mb-4">
                docker compose up -d --build
              </div>

              <div className="space-y-2">
                {[
                  { label: "API + Swagger UI", url: "localhost:8002/docs", color: "text-blue-600" },
                  { label: "Grafana Dashboards", url: "localhost:3000  (admin/admin)", color: "text-emerald-600" },
                  { label: "Prometheus Metrics", url: "localhost:9090", color: "text-orange-500" },
                  { label: "Raw Metrics", url: "localhost:8002/metrics", color: "text-purple-600" },
                ].map((item, i) => (
                  <div key={i} className="flex items-center justify-between p-3 rounded-2xl bg-slate-50 border border-slate-100">
                    <span className="text-[12px] font-semibold text-[#0a1b33]">{item.label}</span>
                    <span className={`font-mono text-[11px] ${item.color}`}>{item.url}</span>
                  </div>
                ))}
              </div>

              <div className="mt-4 p-4 rounded-2xl bg-slate-50 border border-slate-200">
                <p className="text-[11px] font-semibold text-slate-600 mb-2">Drop-in OpenAI replacement:</p>
                <div className="bg-slate-900 rounded-xl p-3 font-mono text-[10px] text-slate-300 leading-relaxed">
                  <span className="text-slate-500"># Before</span><br />
                  <span className="text-red-400">base_url=&quot;https://api.openai.com/v1&quot;</span><br /><br />
                  <span className="text-slate-500"># After — full enterprise control</span><br />
                  <span className="text-emerald-400">base_url=&quot;http://your-engine:8002/v1&quot;</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </motion.section>

      {/* ── SECTION 6: Tech Stack ────────────────────────────────────── */}
      <motion.section
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.7 }}
        className="bg-white rounded-[40px] border border-slate-200/50 shadow-sm overflow-hidden"
      >
        <div className="px-8 md:px-16 py-12 md:py-14">
          <div className="text-center mb-10">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-100 border border-slate-200 text-[11px] font-semibold text-slate-600 mb-3">
              🛠️ Tech Stack
            </div>
            <h2 className="font-display text-[28px] md:text-[34px] font-semibold text-[#0a1b33]">
              Built on Battle-Tested Infrastructure
            </h2>
            <p className="text-[14px] text-[#64748b] mt-2">
              Open-source, self-hosted, zero vendor lock-in.
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-8">
            {STACK_ITEMS.map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.07 }}
                className="p-4 bg-slate-50 rounded-2xl border border-slate-100 hover:bg-white hover:border-slate-200 hover:shadow-sm transition-all"
              >
                <div className="text-xl mb-1">{item.icon}</div>
                <div className="text-[13px] font-bold text-[#0a1b33]">{item.name}</div>
                <div className="text-[11px] text-[#64748b] mt-0.5">{item.desc}</div>
              </motion.div>
            ))}
          </div>

          {/* Observability row */}
          <div className="p-5 rounded-3xl bg-[#0a152d] text-white flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="font-display text-[15px] font-semibold">Full Observability Stack Included</p>
              <p className="text-[12px] text-slate-400 mt-0.5">Prometheus + Grafana + OpenTelemetry + AlertManager — pre-configured and ready.</p>
            </div>
            <div className="flex flex-wrap gap-2">
              {["SLO Dashboard", "Cache Metrics", "Provider Routing", "Batching Stats", "System Overview"].map((d) => (
                <span key={d} className="px-3 py-1 bg-white/10 border border-white/10 rounded-full text-[11px] font-medium">{d}</span>
              ))}
            </div>
          </div>
        </div>
      </motion.section>

      {/* ── SECTION 7: Multi-Tenancy Explainer ──────────────────────── */}
      <motion.section
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.7 }}
        className="bg-white rounded-[40px] border border-slate-200/50 shadow-sm overflow-hidden"
      >
        <div className="px-8 md:px-16 py-12 md:py-14">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-50 border border-amber-100 text-[11px] font-semibold text-amber-700 mb-4">
                🏢 Multi-Tenancy
              </div>
              <h2 className="font-display text-[28px] md:text-[34px] font-semibold text-[#0a1b33] leading-tight mb-3">
                Full Org → Workspace → User Hierarchy
              </h2>
              <p className="text-[14px] text-[#64748b] leading-relaxed mb-5">
                Isolate every team, set independent budgets and quotas, and grant fine-grained RBAC roles — all without sharing infrastructure. Perfect for large enterprises and SaaS products serving multiple customers.
              </p>
              <ul className="space-y-2 text-[13px] text-[#64748b]">
                {[
                  "Per-tenant API keys (sk_...) and JWT tokens",
                  "Admin, Developer, and Viewer roles",
                  "One team's usage never affects another",
                  "Budget enforcement at the middleware layer",
                  "Subscription plans with quota inheritance",
                ].map((item, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-emerald-500 mt-0.5">✓</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-slate-50 rounded-3xl border border-slate-200 p-6 font-mono text-[12px] text-slate-700 leading-relaxed">
              <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-4">Example Org Structure</p>
              <div className="space-y-1.5">
                <div className="text-[#0a1b33] font-bold">📦 Your Company (Organization)</div>
                <div className="ml-4">├── 👨‍💻 <span className="text-blue-600">Engineering Team</span></div>
                <div className="ml-12 text-slate-500">Budget: $2,000/mo  |  50k req/day</div>
                <div className="ml-4">├── 💼 <span className="text-emerald-600">Sales Team</span></div>
                <div className="ml-12 text-slate-500">Budget: $500/mo   |  10k req/day</div>
                <div className="ml-4">└── 📊 <span className="text-amber-600">Finance Team</span></div>
                <div className="ml-12 text-slate-500">Budget: $1,000/mo |  5k req/day</div>
              </div>
              <div className="mt-4 p-3 bg-white rounded-xl border border-slate-200">
                <p className="text-[10px] font-semibold text-slate-500 mb-1">Request Budget Flow</p>
                <div className="text-[11px] text-slate-600 space-y-0.5">
                  <div>Request → Budget check → Rate limit → ✅ Proceed</div>
                  <div className="text-red-400">           OR → 429 Blocked</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </motion.section>

      {/* ── SECTION 8: CTA Footer ────────────────────────────────────── */}
      <motion.section
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.7 }}
        className="bg-[#0a152d] rounded-[40px] overflow-hidden"
      >
        <div className="px-8 md:px-16 py-12 md:py-14 text-center">
          <h2 className="font-display text-[28px] md:text-[36px] font-semibold text-white leading-tight mb-3">
            Ready to deploy Inferion AI?
          </h2>
          <p className="text-[14px] text-slate-400 max-w-xl mx-auto mb-8">
            Self-hosted, open-source, and free. Replace 5 SaaS tools with a single platform you fully control.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-3">
            <a
              href="https://github.com/Yogesh10217/Inferion-ai"
              target="_blank"
              rel="noreferrer"
              className="bg-white text-[#0a152d] font-semibold text-[13px] px-6 py-3 rounded-full hover:bg-slate-100 transition-all flex items-center gap-2"
            >
              ⭐ View on GitHub
            </a>
            <a
              href="http://localhost:8002/docs"
              target="_blank"
              rel="noreferrer"
              className="bg-white/10 text-white border border-white/20 font-semibold text-[13px] px-6 py-3 rounded-full hover:bg-white/20 transition-all"
            >
              📖 API Docs
            </a>
            <a
              href="mailto:eyogesh104@gmail.com"
              className="bg-white/10 text-white border border-white/20 font-semibold text-[13px] px-6 py-3 rounded-full hover:bg-white/20 transition-all"
            >
              ✉️ Contact Us
            </a>
          </div>

          <div className="mt-8 flex flex-wrap items-center justify-center gap-4 text-[11px] text-slate-500">
            {["Python 3.10+", "FastAPI", "MIT License", "OpenAI Compatible", "Docker Ready", "Prometheus Monitored"].map((tag) => (
              <span key={tag} className="px-3 py-1 bg-white/5 border border-white/10 rounded-full">{tag}</span>
            ))}
          </div>
        </div>
      </motion.section>

    </div>
  );
};
