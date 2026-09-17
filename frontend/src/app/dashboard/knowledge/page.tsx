"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { Database, Upload, Search, FileText, Layers, HardDrive, CheckCircle2, RefreshCw } from "lucide-react";
import { Topbar } from "@/components/dashboard/Topbar";
import { StatCard } from "@/components/dashboard/StatCard";
import { StatusBadge } from "@/components/dashboard/Badge";
import { Modal } from "@/components/dashboard/Modal";
import { knowledgeBases, documentChunks } from "@/lib/mock-data";

export default function KnowledgePage() {
  const [selectedKb, setSelectedKb] = useState(knowledgeBases[0]);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  const filteredChunks = React.useMemo(() => {
    if (!searchQuery) return documentChunks;
    return documentChunks.filter(
      (c) =>
        c.text.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.source.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [searchQuery]);

  return (
    <div className="flex min-h-screen flex-col">
      <Topbar title="RAG Document & Embedding Visualizer" subtitle="Manage vector indexes, chunk stores, and hybrid semantic retrieval" />

      <main className="flex-1 space-y-6 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="flex h-3 w-3 rounded-full bg-emerald-400"></span>
            <span className="text-xs text-slate-300">Hybrid Search: HNSW Dense + BM25 Sparse Active</span>
          </div>
          <button
            onClick={() => setUploadModalOpen(true)}
            className="inline-flex items-center justify-center rounded-lg bg-blue-600 px-4 py-2 text-xs font-semibold text-white hover:bg-blue-500"
          >
            <Upload className="mr-1.5 h-3.5 w-3.5" /> Ingest New Document
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard label="Knowledge Bases" value={knowledgeBases.length} sub="FAISS, Qdrant, Pinecone" />
          <StatCard label="Total Chunks" value="10,162" sub="Embedded & Indexed" />
          <StatCard label="Total Vector Storage" value="23.8 MB" sub="In-Memory Index" />
          <StatCard label="Embedding Model" value="text-embedding-3" sub="OpenAI 1536-dim" />
        </div>

        {/* Knowledge Bases Selector Grid */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {knowledgeBases.map((kb) => (
            <div
              key={kb.id}
              onClick={() => setSelectedKb(kb)}
              className={`cursor-pointer rounded-xl border p-4 transition-all ${
                selectedKb.id === kb.id
                  ? "border-blue-500 bg-blue-500/10 shadow-lg shadow-blue-500/10"
                  : "border-slate-800 bg-[#070e1c]/80 hover:border-slate-700"
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-2">
                  <Database className="h-4 w-4 text-blue-400" />
                  <h3 className="text-xs font-semibold text-slate-100">{kb.name}</h3>
                </div>
                <StatusBadge status={kb.status as any} />
              </div>

              <div className="mt-4 space-y-1 font-mono text-[11px] text-slate-400">
                <div className="flex justify-between">
                  <span>Docs:</span>
                  <span className="text-slate-200">{kb.documents}</span>
                </div>
                <div className="flex justify-between">
                  <span>Chunks:</span>
                  <span className="text-slate-200">{kb.chunks.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span>Vector DB:</span>
                  <span className="text-slate-200">{kb.vectorStore}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Search & Chunk Explorer */}
        <div className="rounded-xl border border-slate-800 bg-[#070e1c]/80 p-5 backdrop-blur-md">
          <div className="mb-4 flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
            <div>
              <h3 className="text-sm font-semibold text-slate-100">
                Vector Chunk Inspector — {selectedKb.name}
              </h3>
              <p className="text-xs text-slate-400">
                Vector store: {selectedKb.vectorStore} • Model: {selectedKb.embeddingModel}
              </p>
            </div>

            <div className="relative w-full sm:w-72">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Search semantic chunk preview..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full rounded-lg border border-slate-800 bg-slate-900 py-2 pl-9 pr-4 text-xs text-slate-200 placeholder-slate-500 focus:border-blue-500 focus:outline-none"
              />
            </div>
          </div>

          <div className="space-y-3">
            {filteredChunks.map((chunk) => (
              <motion.div
                key={chunk.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="rounded-lg border border-slate-800 bg-slate-900/60 p-4 transition-all hover:border-slate-700"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <FileText className="h-4 w-4 text-slate-400" />
                    <span className="font-mono text-xs font-semibold text-slate-200">{chunk.source}</span>
                    <span className="font-mono text-[10px] text-slate-500">{chunk.id}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-[10px] text-slate-400">Cosine Score:</span>
                    <span className="rounded bg-emerald-500/10 px-2 py-0.5 font-mono text-[10px] font-bold text-emerald-400">
                      {chunk.score.toFixed(2)}
                    </span>
                  </div>
                </div>

                <p className="mt-2 font-mono text-xs text-slate-300 leading-relaxed bg-[#050B14] p-3 rounded-md border border-slate-800/80">
                  "{chunk.text}"
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </main>

      {/* Upload Document Modal */}
      <Modal
        open={uploadModalOpen}
        onClose={() => setUploadModalOpen(false)}
        title="Ingest Document into Knowledge Base"
        subtitle="Automatic chunking, embedding generation, and vector index updates"
      >
        <div className="space-y-4 text-xs">
          <div>
            <label className="block text-slate-400 mb-1">Target Knowledge Base</label>
            <select className="w-full rounded-lg border border-slate-800 bg-slate-900 p-2.5 text-slate-200">
              {knowledgeBases.map((kb) => (
                <option key={kb.id} value={kb.id}>{kb.name} ({kb.vectorStore})</option>
              ))}
            </select>
          </div>

          <div className="rounded-xl border border-dashed border-slate-700 bg-slate-900/40 p-8 text-center">
            <Upload className="mx-auto h-8 w-8 text-slate-500" />
            <p className="mt-2 font-medium text-slate-300">Drag & drop document files here</p>
            <p className="text-[10px] text-slate-500 mt-1">Supports Markdown (.md), PDF, TXT, JSON (Max 50MB)</p>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-400 mb-1">Chunk Size (tokens)</label>
              <input type="number" defaultValue={512} className="w-full rounded-lg border border-slate-800 bg-slate-900 p-2 text-slate-200" />
            </div>
            <div>
              <label className="block text-slate-400 mb-1">Overlap (tokens)</label>
              <input type="number" defaultValue={64} className="w-full rounded-lg border border-slate-800 bg-slate-900 p-2 text-slate-200" />
            </div>
          </div>

          <div className="flex justify-end space-x-2 pt-2">
            <button
              onClick={() => setUploadModalOpen(false)}
              className="rounded-lg border border-slate-800 bg-slate-900 px-4 py-2 text-slate-400 hover:bg-slate-800"
            >
              Cancel
            </button>
            <button
              onClick={() => {
                alert("Document ingestion pipeline started! Vector index updating.");
                setUploadModalOpen(false);
              }}
              className="rounded-lg bg-blue-600 px-4 py-2 font-semibold text-white hover:bg-blue-500"
            >
              Start Ingestion
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
