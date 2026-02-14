'use client';

import React, { useState } from 'react';
import { cn } from '@/lib/utils';
import {
    LayoutDashboard,
    ToyBrick,
    Key,
    Settings,
    History,
    ShieldCheck,
    Cpu,
    ShieldAlert,
    Brain,
    ChevronLeft,
    ChevronRight
} from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

const sidebarItems = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Bridges', href: '/bridges', icon: ToyBrick },
    { name: 'API Keys', href: '/keys', icon: Key },
    { name: 'Security Audit', href: '/dashboard/security', icon: ShieldAlert },
    { name: 'MCP', href: '/dashboard/mcp', icon: Cpu },
    { name: 'LLM Providers', href: '/settings/llm', icon: Brain },
    { name: 'Extraction Logs', href: '/logs', icon: History },
    { name: 'Permissions', href: '/permissions', icon: ShieldCheck },
    { name: 'Settings', href: '/settings', icon: Settings },
];

export default function Sidebar({ className }: { className?: string }) {
    const [collapsed, setCollapsed] = useState(false);
    const pathname = usePathname();

    return (
        <div className={cn(
            "pb-12 h-screen border-r border-white/5 bg-black/40 backdrop-blur-xl transition-all duration-300 relative",
            collapsed ? "w-20" : "w-64",
            className
        )}>
            {/* Toggle Button */}
            <button
                onClick={() => setCollapsed(!collapsed)}
                className="absolute -right-3 top-8 z-50 h-6 w-6 rounded-full bg-primary border border-white/10 flex items-center justify-center hover:scale-110 transition-transform shadow-lg"
            >
                {collapsed ? (
                    <ChevronRight className="h-3 w-3 text-black" />
                ) : (
                    <ChevronLeft className="h-3 w-3 text-black" />
                )}
            </button>

            <div className="space-y-4 py-6">
                <div className="px-6 py-2">
                    <div className={cn(
                        "flex items-center gap-2 mb-8 transition-all duration-300",
                        collapsed && "justify-center"
                    )}>
                        <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center shadow-[0_0_15px_rgba(16,185,129,0.5)] flex-shrink-0">
                            <ToyBrick className="h-5 w-5 text-black" />
                        </div>
                        {!collapsed && (
                            <h2 className="text-xl font-bold tracking-tighter text-white text-glow whitespace-nowrap">
                                Bridge
                            </h2>
                        )}
                    </div>
                    <div className="space-y-1.5">
                        {sidebarItems.map((item) => {
                            const isActive = pathname === item.href || pathname?.startsWith(item.href + '/');
                            return (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    className={cn(
                                        "group flex items-center rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200 border relative",
                                        collapsed ? "justify-center" : "",
                                        isActive
                                            ? "text-white bg-primary/10 border-primary/20"
                                            : "text-zinc-400 hover:text-white hover:bg-white/5 border-transparent hover:border-white/5"
                                    )}
                                    title={collapsed ? item.name : undefined}
                                >
                                    <item.icon className={cn(
                                        "h-4 w-4 transition-colors duration-200 flex-shrink-0",
                                        collapsed ? "" : "mr-3",
                                        isActive ? "text-primary" : "group-hover:text-primary"
                                    )} />
                                    {!collapsed && <span className="whitespace-nowrap">{item.name}</span>}
                                </Link>
                            );
                        })}
                    </div>
                </div>
            </div>

            {!collapsed && (
                <div className="absolute bottom-8 left-6 right-6 animate-in fade-in duration-300">
                    <div className="p-4 rounded-xl bg-primary/5 border border-primary/10">
                        <p className="text-[10px] font-bold text-primary uppercase tracking-widest mb-1">Status</p>
                        <div className="flex items-center gap-2">
                            <div className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse" />
                            <span className="text-xs text-white/70 font-medium">Bridge.dev Nodes Active</span>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
