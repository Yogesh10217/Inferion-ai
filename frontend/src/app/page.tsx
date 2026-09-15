import React from "react";
import { HeroSection } from "@/components/HeroSection";
import { MarqueeScroller } from "@/components/MarqueeScroller";
import { ContentSections } from "@/components/ContentSections";

export default function Home() {
  return (
    <main className="min-h-screen bg-[#f9fafb] py-8 px-4 sm:px-6 lg:px-8 flex flex-col">
      {/* Hero Container with Video & Floating Navbar */}
      <HeroSection />

      {/* Seamless Marquee Logo Scroller */}
      <MarqueeScroller />

      {/* Informational Content Sections */}
      <ContentSections />
    </main>
  );
}
