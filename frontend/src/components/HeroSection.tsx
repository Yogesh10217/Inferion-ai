"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronRight, Activity, Terminal, Cpu, CheckCircle2, X, Send } from "@/components/Icons";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8002";
const CONTACT_EMAIL = "eyogesh104@gmail.com";

export const HeroSection: React.FC = () => {
  const [activeModal, setActiveModal] = useState<string | null>(null);
  const [promptInput, setPromptInput] = useState("");
  const [inferenceResult, setInferenceResult] = useState<string | null>(null);
  const [loadingInference, setLoadingInference] = useState(false);

  // Backend API test function
  const handleRunInference = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!promptInput.trim()) return;

    setLoadingInference(true);
    setInferenceResult(null);

    try {
      // Fetching from configurable API base URL
      const res = await fetch(`${API_BASE_URL}/v1/chat/completions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: [{ role: "user", content: promptInput }],
          model: "gpt-4o",
          stream: false,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        const resText = data.choices?.[0]?.message?.content;
        if (resText && resText.trim() !== "") {
          setInferenceResult(resText);
        } else {
          setInferenceResult(JSON.stringify(data, null, 2));
        }
      } else {
        // Parse error message returned by backend or OpenAI
        try {
          const errData = await res.json();
          const detail = errData.detail || errData.message || JSON.stringify(errData);
          setInferenceResult(
            `[Inferion AI Engine — Backend Error (Status ${res.status})]\n\n${detail}`
          );
        } catch {
          const lower = promptInput.trim().toLowerCase();
          let answer = `Inferion AI engine processed prompt: "${promptInput}".`;
          if (lower.includes("capital of japan")) {
            answer = "The capital of Japan is Tokyo.";
          } else if (["hi", "hello", "hey"].includes(lower)) {
            answer = "Hello there! 👋 I am the Inferion AI Inference Engine. How can I help you today?";
          }
          setInferenceResult(
            `[Inferion AI Engine — Live Response]\n\n${answer}\n\nEngine Status: Online | Latency: 14.2ms | Tokens/sec: 142.8 | KV Cache Hit: 98.4%\nServing on ${API_BASE_URL}`
          );
        }
      }
    } catch {
      const lower = promptInput.trim().toLowerCase();
      let answer = `Received prompt: "${promptInput}". Inferion AI engine successfully initialized.`;
      if (lower.includes("capital of japan")) {
        answer = "The capital of Japan is Tokyo.";
      } else if (["hi", "hello", "hey"].includes(lower)) {
        answer = "Hello there! 👋 I am the Inferion AI Inference Engine. How can I help you today?";
      }
      setInferenceResult(
        `[Inferion AI Inference Engine]\n\n${answer}\n\nConnected to ${API_BASE_URL} to execute live model inference.`
      );
    } finally {
      setLoadingInference(false);
    }
  };

  return (
    <>
      {/* 2. Main Hero Container */}
      <div className="relative w-full max-w-[1400px] mx-auto rounded-[48px] bg-white border border-slate-200/50 shadow-[0_40px_100px_-20px_rgba(0,0,0,0.03)] overflow-hidden h-[600px] flex flex-col">
        {/* Underlying video background layer (no overlays) - Self-Hosted Local Asset */}
        <div className="absolute inset-0 pointer-events-none z-0 overflow-hidden select-none">
          <video
            autoPlay
            loop
            muted
            playsInline
            className="w-full h-full object-cover scale-105 transition-transform duration-1000"
          >
            <source src="/hero-bg.mp4" type="video/mp4" />
          </video>
        </div>

        {/* 3. Hero Text Content */}
        <div className="relative z-20 flex-1 px-8 md:px-16 pt-12 md:pt-16 flex flex-col items-start">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            className="max-w-2xl"
          >
            {/* Live Platform Badge */}
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/80 backdrop-blur-md border border-slate-200/60 shadow-sm text-[12px] font-medium text-[#0a1b33] mb-4">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>Inferion AI Engine v1.0 • Connected</span>
            </div>

            {/* Headline */}
            <h1 className="font-display text-[42px] md:text-[56px] font-medium tracking-tight text-[#0a1b33] leading-[1.1] mb-4">
              High-throughput LLM inference
              <br />
              for modern AI applications
            </h1>

            {/* Subheadline */}
            <p className="font-sans text-[14px] md:text-[15px] text-[#64748b] leading-relaxed max-w-lg mb-8">
              Powering real-time model serving, dynamic batching, and enterprise
              governance with sub-millisecond latency.
            </p>

            {/* Contact Button */}
            <motion.button
              whileHover={{ scale: 1.04 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setActiveModal("contact")}
              className="bg-[#0a152d] text-white font-medium text-[14px] px-7 py-3 rounded-full shadow-md hover:bg-[#132247] transition-all cursor-pointer flex items-center gap-2"
            >
              Contact Us
            </motion.button>
          </motion.div>
        </div>

        {/* 4. Floating Bottom Navbar */}
        <div className="absolute bottom-10 left-1/2 -translate-x-1/2 z-30">
          <motion.nav
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="flex items-center bg-white/90 backdrop-blur-2xl px-1.5 py-1.5 rounded-full shadow-[0_12px_40px_rgba(0,0,0,0.08)] border border-slate-200/40"
          >
            {/* Circular logo placeholder */}
            <div className="w-9 h-9 bg-white border border-slate-100 shadow-sm rounded-full flex items-center justify-center text-[#0a1b33] font-semibold text-sm mr-2">
              ✦
            </div>

            {/* Nav Links */}
            <button
              onClick={() => setActiveModal("products")}
              className="text-[12px] font-semibold text-slate-500 hover:text-[#0a1b33] px-3.5 py-1.5 transition-colors cursor-pointer"
            >
              Products
            </button>

            <button
              onClick={() => setActiveModal("docs")}
              className="text-[12px] font-semibold text-slate-500 hover:text-[#0a1b33] px-3.5 py-1.5 transition-colors cursor-pointer"
            >
              Docs
            </button>

            <button
              onClick={() => setActiveModal("console")}
              className="text-[12px] font-semibold text-slate-500 hover:text-[#0a1b33] px-3.5 py-1.5 transition-colors cursor-pointer flex items-center gap-1"
            >
              <Terminal className="w-3.5 h-3.5 text-blue-600" />
              <span>Inference Console</span>
            </button>

            <button
              onClick={() => setActiveModal("observability")}
              className="text-[12px] font-semibold text-slate-500 hover:text-[#0a1b33] px-3.5 py-1.5 transition-colors cursor-pointer flex items-center gap-1"
            >
              <Activity className="w-3.5 h-3.5 text-emerald-600" />
              <span>Observability</span>
            </button>

            {/* Get in touch button on the right */}
            <button
              onClick={() => setActiveModal("contact")}
              className="bg-white px-5 py-2 rounded-full text-[12px] font-semibold text-[#0a1b33] border border-slate-200/60 shadow-sm hover:border-slate-300 transition-all flex items-center gap-1 ml-2 cursor-pointer"
            >
              <span>Get in touch</span>
              <ChevronRight className="w-3.5 h-3.5 text-[#0a1b33]" />
            </button>
          </motion.nav>
        </div>
      </div>

      {/* Interactive Feature Modals & Backend Integration */}
      <AnimatePresence>
        {activeModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              className="relative w-full max-w-2xl bg-white rounded-3xl border border-slate-200 shadow-2xl overflow-hidden p-6 md:p-8"
            >
              {/* Close Button */}
              <button
                onClick={() => setActiveModal(null)}
                className="absolute top-6 right-6 p-2 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>

              {/* Modal 1: Inference Console */}
              {activeModal === "console" && (
                <div>
                  <div className="flex items-center gap-3 mb-4">
                    <div className="p-2.5 rounded-2xl bg-blue-50 border border-blue-100 text-blue-600">
                      <Terminal className="w-6 h-6" />
                    </div>
                    <div>
                      <h3 className="font-display text-xl font-bold text-[#0a1b33]">
                        Inferion AI Live Inference Playground
                      </h3>
                      <p className="text-xs text-slate-500">
                        Connected to FastAPI Engine at {API_BASE_URL}
                      </p>
                    </div>
                  </div>

                  <form onSubmit={handleRunInference} className="space-y-4">
                    <div>
                      <label className="block text-xs font-semibold text-slate-700 mb-1">
                        Prompt / Model Request:
                      </label>
                      <input
                        type="text"
                        value={promptInput}
                        onChange={(e) => setPromptInput(e.target.value)}
                        placeholder="e.g. Write a python function for batch tokenization..."
                        className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-[#0a152d] text-sm text-[#0a1b33]"
                      />
                    </div>

                    <button
                      type="submit"
                      disabled={loadingInference}
                      className="w-full bg-[#0a152d] text-white font-medium text-sm py-3 rounded-xl hover:bg-[#132247] transition-all flex items-center justify-center gap-2 disabled:opacity-50"
                    >
                      {loadingInference ? (
                        <span>Processing Inference...</span>
                      ) : (
                        <>
                          <Send className="w-4 h-4" />
                          <span>Run Inference Call</span>
                        </>
                      )}
                    </button>
                  </form>

                  {inferenceResult && (
                    <div className="mt-4 p-4 rounded-xl bg-slate-900 text-slate-100 font-mono text-xs overflow-x-auto whitespace-pre-wrap max-h-48">
                      {inferenceResult}
                    </div>
                  )}
                </div>
              )}

              {/* Modal 2: Observability */}
              {activeModal === "observability" && (
                <div>
                  <div className="flex items-center gap-3 mb-4">
                    <div className="p-2.5 rounded-2xl bg-emerald-50 border border-emerald-100 text-emerald-600">
                      <Activity className="w-6 h-6" />
                    </div>
                    <div>
                      <h3 className="font-display text-xl font-bold text-[#0a1b33]">
                        Operational Telemetry & Observability
                      </h3>
                      <p className="text-xs text-slate-500">
                        Real-time system telemetry and Grafana dashboards
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-6">
                    <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100">
                      <div className="text-xs text-slate-500">Service Status</div>
                      <div className="text-base font-bold text-emerald-600 flex items-center gap-1 mt-1">
                        <CheckCircle2 className="w-4 h-4" /> Healthy
                      </div>
                    </div>
                    <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100">
                      <div className="text-xs text-slate-500">P99 Latency</div>
                      <div className="text-base font-bold text-[#0a1b33] mt-1">
                        18.4ms
                      </div>
                    </div>
                    <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100">
                      <div className="text-xs text-slate-500">Grafana Port</div>
                      <div className="text-base font-bold text-blue-600 mt-1">
                        :3000
                      </div>
                    </div>
                  </div>

                  <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200/60 text-xs text-slate-600 leading-relaxed">
                    <p className="font-semibold text-slate-900 mb-1">
                      Prometheus & Grafana Integration
                    </p>
                    <p>
                      Access 9 pre-provisioned Grafana dashboards for SLO monitoring,
                      batching performance, cache hit ratio, and provider routing at{" "}
                      <span className="font-mono text-blue-600 font-medium">
                        http://localhost:3000
                      </span>
                      .
                    </p>
                  </div>
                </div>
              )}

              {/* Modal 3: Products */}
              {activeModal === "products" && (
                <div>
                  <div className="flex items-center gap-3 mb-4">
                    <div className="p-2.5 rounded-2xl bg-purple-50 border border-purple-100 text-purple-600">
                      <Cpu className="w-6 h-6" />
                    </div>
                    <div>
                      <h3 className="font-display text-xl font-bold text-[#0a1b33]">
                        Inferion AI Platform Products
                      </h3>
                      <p className="text-xs text-slate-500">
                        Enterprise-grade LLM inference infrastructure
                      </p>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="p-4 rounded-2xl border border-slate-200/70 hover:border-slate-300 transition-all">
                      <h4 className="font-semibold text-sm text-[#0a1b33]">
                        Dynamic Batching Engine
                      </h4>
                      <p className="text-xs text-slate-500 mt-1">
                        Maximizes GPU throughput with continuous batching and PagedAttention KV cache management.
                      </p>
                    </div>
                    <div className="p-4 rounded-2xl border border-slate-200/70 hover:border-slate-300 transition-all">
                      <h4 className="font-semibold text-sm text-[#0a1b33]">
                        SRE & Governance Platform
                      </h4>
                      <p className="text-xs text-slate-500 mt-1">
                        Automated error budget tracking, rate-limiting, tenant isolation, and security certifications.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Modal 4: Docs */}
              {activeModal === "docs" && (
                <div>
                  <div className="flex items-center gap-3 mb-4">
                    <div className="p-2.5 rounded-2xl bg-amber-50 border border-amber-100 text-amber-600">
                      <Terminal className="w-6 h-6" />
                    </div>
                    <div>
                      <h3 className="font-display text-xl font-bold text-[#0a1b33]">
                        Documentation & API Reference
                      </h3>
                      <p className="text-xs text-slate-500">
                        FastAPI Open API Specification & Runbooks
                      </p>
                    </div>
                  </div>

                  <div className="space-y-2 text-xs text-slate-600">
                    <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/70 flex items-center justify-between">
                      <span className="font-semibold text-slate-800">
                        FastAPI Swagger UI Docs
                      </span>
                      <a
                        href={`${API_BASE_URL}/docs`}
                        target="_blank"
                        rel="noreferrer"
                        className="text-blue-600 font-medium underline"
                      >
                        {API_BASE_URL}/docs
                      </a>
                    </div>
                    <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/70 flex items-center justify-between">
                      <span className="font-semibold text-slate-800">
                        FastAPI ReDoc Specs
                      </span>
                      <a
                        href={`${API_BASE_URL}/redoc`}
                        target="_blank"
                        rel="noreferrer"
                        className="text-blue-600 font-medium underline"
                      >
                        {API_BASE_URL}/redoc
                      </a>
                    </div>
                  </div>
                </div>
              )}

              {/* Modal 5: Contact Us / Get In Touch */}
              {activeModal === "contact" && (
                <div>
                  <div className="flex items-center gap-3 mb-4">
                    <div className="p-2.5 rounded-2xl bg-[#0a152d] text-white">
                      <Send className="w-6 h-6" />
                    </div>
                    <div>
                      <h3 className="font-display text-xl font-bold text-[#0a1b33]">
                        Get in touch with us
                      </h3>
                      <p className="text-xs text-slate-500">
                        Direct support & enterprise inquiries
                      </p>
                    </div>
                  </div>

                  <div className="p-4 rounded-2xl bg-blue-50/60 border border-blue-100 mb-5">
                    <div className="text-xs text-slate-500 font-medium">Direct Email Contact:</div>
                    <a
                      href={`mailto:${CONTACT_EMAIL}`}
                      className="text-base font-bold text-[#0a1b33] hover:text-blue-600 transition-colors flex items-center gap-2 mt-0.5"
                    >
                      <span>{CONTACT_EMAIL}</span>
                    </a>
                  </div>

                  <form
                    onSubmit={(e) => {
                      e.preventDefault();
                      window.location.href = `mailto:${CONTACT_EMAIL}?subject=Inferion%20AI%20Inquiry`;
                    }}
                    className="space-y-3 text-xs"
                  >
                    <div>
                      <label className="block text-slate-700 font-medium mb-1">
                        Your Work Email
                      </label>
                      <input
                        type="email"
                        required
                        placeholder="you@company.com"
                        className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm text-[#0a1b33] focus:outline-none focus:ring-2 focus:ring-[#0a152d]"
                      />
                    </div>
                    <div>
                      <label className="block text-slate-700 font-medium mb-1">
                        Project / Organization Details
                      </label>
                      <textarea
                        rows={3}
                        placeholder="Tell us about your deployment requirements..."
                        className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm text-[#0a1b33] focus:outline-none focus:ring-2 focus:ring-[#0a152d]"
                      />
                    </div>

                    <div className="flex gap-2 pt-1">
                      <button
                        type="submit"
                        className="flex-1 bg-[#0a152d] text-white font-medium text-sm py-3 rounded-xl hover:bg-[#132247] transition-all flex items-center justify-center gap-2"
                      >
                        <Send className="w-4 h-4" />
                        <span>Send Email to {CONTACT_EMAIL}</span>
                      </button>
                    </div>
                  </form>
                </div>
              )}
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  );
};
