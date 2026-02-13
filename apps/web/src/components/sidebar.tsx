import React from 'react';
import { cn } from '@/lib/utils';
import {
    LayoutDashboard,
    ToyBrick,
    Key,
    Settings,
    History,
    ShieldCheck,
    Cpu,
    ShieldAlert
} from 'lucide-react';
import Link from 'next/link';

const sidebarItems = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Bridges', href: '/bridges', icon: ToyBrick },
    { name: 'API Keys', href: '/keys', icon: Key },
    { name: 'Security Audit', href: '/dashboard/security', icon: ShieldAlert },
    { name: 'MCP', href: '/dashboard/mcp', icon: Cpu },
    { name: 'Extraction Logs', href: '/logs', icon: History },
    { name: 'Permissions', href: '/permissions', icon: ShieldCheck },
    { name: 'Settings', href: '/settings', icon: Settings },
];

export default function Sidebar({ className }: { className?: string }) {
    return (
        <div className={cn("pb-12 h-screen border-r border-white/5 bg-black/40 backdrop-blur-xl w-64", className)}>
            <div className="space-y-4 py-6">
                <div className="px-6 py-2">
                    <div className="flex items-center gap-2 mb-8">
                        <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center shadow-[0_0_15px_rgba(16,185,129,0.5)]">
                            <ToyBrick className="h-5 w-5 text-black" />
                        </div>
                        <h2 className="text-xl font-bold tracking-tighter text-white text-glow">
                            Bridge
                        </h2>
                    </div>
                    <div className="space-y-1.5">
                        {sidebarItems.map((item) => (
                            <Link
                                key={item.href}
                                href={item.href}
                                className="group flex items-center rounded-lg px-3 py-2.5 text-sm font-medium text-zinc-400 hover:text-white hover:bg-white/5 transition-all duration-200 border border-transparent hover:border-white/5"
                            >
                                <item.icon className="mr-3 h-4 w-4 group-hover:text-primary transition-colors duration-200" />
                                <span>{item.name}</span>
                            </Link>
                        ))}
                    </div>
                </div>
            </div>

            <div className="absolute bottom-8 left-6 right-6">
                <div className="p-4 rounded-xl bg-primary/5 border border-primary/10">
                    <p className="text-[10px] font-bold text-primary uppercase tracking-widest mb-1">Status</p>
                    <div className="flex items-center gap-2">
                        <div className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse" />
                        <span className="text-xs text-white/70 font-medium">Bridge.dev Nodes Active</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
