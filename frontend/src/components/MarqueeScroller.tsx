"use client";

import React from "react";

interface LogoItem {
  name: string;
  src: string;
  gradient: string;
  hexStart: string;
  hexEnd: string;
}

const LOGOS: LogoItem[] = [
  {
    name: "Procure",
    src: "/logos/procure.svg",
    gradient: "linear-gradient(135deg, #3b82f6, #1d4ed8)",
    hexStart: "#3b82f6",
    hexEnd: "#1d4ed8",
  },
  {
    name: "Shopify",
    src: "/logos/shopify.svg",
    gradient: "linear-gradient(135deg, #eab308, #ca8a04)",
    hexStart: "#eab308",
    hexEnd: "#ca8a04",
  },
  {
    name: "Blender",
    src: "/logos/blender.svg",
    gradient: "linear-gradient(135deg, #f97316, #2563eb)",
    hexStart: "#f97316",
    hexEnd: "#2563eb",
  },
  {
    name: "Figma",
    src: "/logos/figma.svg",
    gradient: "linear-gradient(135deg, #a855f7, #7e22ce)",
    hexStart: "#a855f7",
    hexEnd: "#7e22ce",
  },
  {
    name: "Spotify",
    src: "/logos/spotify.svg",
    gradient: "linear-gradient(135deg, #ec4899, #ef4444)",
    hexStart: "#ec4899",
    hexEnd: "#ef4444",
  },
  {
    name: "Lottielab",
    src: "/logos/lottielab.svg",
    gradient: "linear-gradient(135deg, #84cc16, #10b981)",
    hexStart: "#84cc16",
    hexEnd: "#10b981",
  },
  {
    name: "Google Cloud",
    src: "/logos/google-cloud.svg",
    gradient: "linear-gradient(135deg, #38bdf8, #0284c7)",
    hexStart: "#38bdf8",
    hexEnd: "#0284c7",
  },
  {
    name: "Bing",
    src: "/logos/bing.svg",
    gradient: "linear-gradient(135deg, #06b6d4, #0d9488)",
    hexStart: "#06b6d4",
    hexEnd: "#0d9488",
  },
];

export const MarqueeScroller: React.FC = () => {
  // Render array twice inline to ensure a seamless loop
  const duplicatedLogos = [...LOGOS, ...LOGOS];

  return (
    <div className="mt-10 w-full max-w-[1400px] mx-auto overflow-hidden relative">
      <div
        className="w-full overflow-hidden"
        style={{
          maskImage:
            "linear-gradient(to right, transparent, black 10%, black 90%, transparent)",
          WebkitMaskImage:
            "linear-gradient(to right, transparent, black 10%, black 90%, transparent)",
        }}
      >
        <div className="animate-marquee flex items-center gap-4 py-2">
          {duplicatedLogos.map((logo, index) => (
            <div
              key={`${logo.name}-${index}`}
              className="group relative h-24 w-40 shrink-0 flex items-center justify-center rounded-full bg-white border border-slate-200/60 shadow-sm hover:border-slate-300 transition-all overflow-hidden cursor-pointer"
            >
              {/* Gradient hover background */}
              <div
                className="absolute inset-0 scale-150 opacity-0 group-hover:scale-100 group-hover:opacity-100 transition-all duration-500 rounded-full"
                style={{ background: logo.gradient }}
              />

              {/* Logo Image */}
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={logo.src}
                alt={logo.name}
                className="w-10 h-10 object-contain relative z-10 transition-all duration-300 group-hover:brightness-0 group-hover:invert"
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
