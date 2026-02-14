import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/sidebar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "API Bridge Platform",
  description: "Auto-generate APIs for the un-API'd web",
};

import { Toaster } from "sonner";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className} suppressHydrationWarning>
        <Toaster position="top-right" richColors theme="dark" />
        <div className="flex">
          <Sidebar className="w-64 hidden md:block" />
          <div className="flex-1 flex flex-col h-screen overflow-hidden">
            <header className="h-16 border-b border-white/5 flex items-center justify-between px-6 bg-black/40 backdrop-blur-xl">
              <div className="font-black text-white tracking-widest text-xs uppercase">Bridge.dev</div>
              <div className="ml-auto flex items-center space-x-4">
                {/* Auth Status */}
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/5">
                  <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                  <span className="text-[10px] font-bold text-zinc-300 uppercase tracking-wider">Demo Admin</span>
                </div>
              </div>
            </header>
            <main className="flex-1 overflow-y-auto p-6">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}
