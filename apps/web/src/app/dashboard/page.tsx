"use client";

import React, { useEffect, useState } from 'react';
import {
    ToyBrick,
    Key,
    Activity,
    ArrowUpRight,
    Plus
} from 'lucide-react';
import Link from 'next/link';
import { bridgesApi } from '@/lib/api';

export default function DashboardPage() {
    const [stats, setStats] = useState<any>(null);
    const [pulse, setPulse] = useState<any>(null);
    const [bridges, setBridges] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        Promise.all([
            bridgesApi.getStats(),
            bridgesApi.getSecurityPulse(),
            bridgesApi.list()
        ]).then(([statsData, pulseData, bridgesData]) => {
            setStats(statsData);
            setPulse(pulseData);
            setBridges(bridgesData);
        }).finally(() => setLoading(false));
    }, []);

    const statsConfig = [
        {
            name: 'Active Bridges',
            value: stats?.active_bridges ?? '0',
            icon: ToyBrick,
            change: stats?.active_bridges_change ?? '+0',
            changeType: (stats?.active_bridges_change?.startsWith('-')) ? 'decrease' : 'increase'
        },
        {
            name: 'Success Rate',
            value: stats?.success_rate ?? '0%',
            icon: Activity,
            change: stats?.success_rate_change ?? '+0%',
            changeType: (stats?.success_rate_change?.startsWith('-')) ? 'decrease' : 'increase'
        },
        {
            name: 'Total Data',
            value: stats?.total_data_volume ?? '0 MB',
            icon: Key,
            change: stats?.total_data_volume_change ?? '+0%',
            changeType: (stats?.total_data_volume_change?.startsWith('-')) ? 'decrease' : 'increase'
        },
    ];

    return (
        <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div>
                    <h1 className="text-5xl font-black tracking-tighter text-white mb-2 text-glow">
                        Command Center
                    </h1>
                    <p className="text-zinc-500 max-w-md font-medium">Monitoring your Bridge.dev infrastructure and extraction nodes in real-time.</p>
                </div>
                <div className="flex items-center gap-3">
                    <div className="hidden md:flex flex-col items-end mr-2">
                        <span className="text-[10px] font-bold text-primary uppercase tracking-widest">Global Status</span>
                        <span className="text-xs text-zinc-400">{stats ? 'Node Cluster Online' : 'Connecting...'}</span>
                    </div>
                    <Link
                        href="/bridges/new"
                        className="inline-flex items-center justify-center rounded-2xl bg-primary px-8 py-4 text-sm font-black text-black shadow-[0_0_30px_rgba(16,185,129,0.3)] transition-all hover:scale-105 active:scale-95 group"
                    >
                        <Plus className="mr-2 h-5 w-5 transition-transform group-hover:rotate-90" />
                        DEPLOY NEW NODE
                    </Link>
                </div>
            </div>

            <div className="grid gap-6 md:grid-cols-3">
                {statsConfig.map((stat, i) => (
                    <div key={stat.name} className="glass p-8 rounded-3xl group hover:border-primary/20 transition-all duration-500 relative overflow-hidden">
                        <div className="absolute -right-4 -top-4 h-24 w-24 bg-primary/5 rounded-full blur-3xl group-hover:bg-primary/10 transition-colors" />
                        <div className="flex items-center justify-between relative z-10">
                            <div className="p-3 rounded-2xl bg-white/5 text-zinc-400 group-hover:text-primary transition-colors">
                                <stat.icon className="h-6 w-6" />
                            </div>
                            <div className={`flex items-center gap-1 text-[10px] font-black uppercase tracking-widest px-2 py-1 rounded-full ${stat.changeType === 'increase' ? 'bg-primary/10 text-primary' : 'bg-red-500/10 text-red-500'
                                }`}>
                                {stat.change}
                            </div>
                        </div>
                        <div className="mt-6 relative z-10">
                            <p className="text-xs font-bold text-zinc-500 uppercase tracking-widest mb-1">{stat.name}</p>
                            {loading ? (
                                <div className="h-10 w-24 bg-white/5 animate-pulse rounded-xl" />
                            ) : (
                                <h2 className="text-4xl font-black text-white tracking-tight">{stat.value}</h2>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            <div className="grid gap-8 lg:grid-cols-12">
                <div className="lg:col-span-8 space-y-4">
                    <div className="flex items-center justify-between px-2">
                        <h3 className="text-lg font-bold text-white uppercase tracking-widest flex items-center gap-2">
                            <Activity className="h-4 w-4 text-primary" />
                            Active Infrastructure
                        </h3>
                        <Link href="/bridges" className="text-[10px] font-bold text-zinc-500 hover:text-primary tracking-widest uppercase transition-colors">
                            View All Nodes
                        </Link>
                    </div>

                    <div className="glass rounded-3xl p-1 shadow-2xl">
                        {loading ? (
                            <div className="p-8 space-y-4">
                                {[1, 2].map(i => <div key={i} className="h-16 w-full bg-white/5 animate-pulse rounded-2xl" />)}
                            </div>
                        ) : bridges.length > 0 ? (
                            <div className="p-4 space-y-2">
                                {bridges.slice(0, 3).map((bridge: any) => (
                                    <div key={bridge.id} className="flex items-center justify-between p-4 rounded-2xl bg-white/5 hover:bg-white/10 transition-colors group">
                                        <div className="flex items-center gap-4">
                                            <div className="h-2 w-2 rounded-full bg-primary shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                                            <div>
                                                <p className="text-sm font-bold text-white">{bridge.name}</p>
                                                <p className="text-[10px] text-zinc-500 uppercase tracking-widest">{bridge.domain}</p>
                                            </div>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-[10px] font-black text-primary uppercase">{bridge.status}</p>
                                            <p className="text-[10px] text-zinc-600 font-mono italic">
                                                {bridge.last_successful_extraction ? new Date(bridge.last_successful_extraction).toLocaleTimeString() : 'No activity'}
                                            </p>
                                        </div>
                                    </div>
                                ))}
                                {bridges.length > 3 && (
                                    <div className="px-4 py-2">
                                        <p className="text-[10px] text-zinc-600 uppercase font-black tracking-widest">
                                            + {bridges.length - 3} more nodes operational
                                        </p>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="flex flex-col items-center justify-center py-20 text-center rounded-[2.5rem]">
                                <div className="h-16 w-16 rounded-2xl bg-white/5 flex items-center justify-center mb-6">
                                    <ToyBrick className="h-8 w-8 text-zinc-600" />
                                </div>
                                <h4 className="text-xl font-bold text-white mb-2">No active extraction nodes</h4>
                                <p className="text-zinc-500 max-w-xs mx-auto mb-8 text-sm">Deploy your first bridge to start generating high-performance APIs from any digital interface.</p>
                                <Link href="/bridges/new" className="bg-primary/10 text-primary border border-primary/20 px-8 py-3 rounded-xl font-bold hover:bg-primary hover:text-black transition-all">
                                    INITIALIZE DEPLOYMENT
                                </Link>
                            </div>
                        )}
                    </div>
                </div>

                <div className="lg:col-span-4 space-y-4">
                    <div className="flex items-center justify-between px-2">
                        <h3 className="text-lg font-bold text-white uppercase tracking-widest flex items-center gap-2">
                            <ArrowUpRight className="h-4 w-4 text-primary" />
                            Security Pulse
                        </h3>
                    </div>

                    <div className="glass rounded-3xl p-6 space-y-6">
                        <div className="space-y-4">
                            {[
                                { label: 'Auth Health', status: pulse?.auth_health ?? 'Pending', color: 'bg-primary' },
                                { label: 'Token Leakage', status: pulse?.token_leakage ?? 'Scanning', color: 'bg-primary' },
                                { label: 'Audit Log', status: pulse?.audit_log ?? 'Active', color: 'bg-primary' }
                            ].map((item, i) => (
                                <div key={i} className="flex items-center justify-between group cursor-help">
                                    <span className="text-xs font-bold text-zinc-500 uppercase tracking-widest">{item.label}</span>
                                    <div className="flex items-center gap-2">
                                        <span className="text-[10px] font-black text-white uppercase">{item.status}</span>
                                        <div className={`h-1.5 w-1.5 rounded-full ${item.color} shadow-[0_0_8px_rgba(16,185,129,0.5)]`} />
                                    </div>
                                </div>
                            ))}
                        </div>

                        <div className="pt-6 border-t border-white/5">
                            <div className="bg-black/40 rounded-2xl p-4 border border-white/5">
                                <p className="text-[10px] font-bold text-zinc-600 uppercase tracking-widest mb-2">{pulse?.last_event?.label || 'Event Feed'}</p>
                                <p className="text-xs text-zinc-300 leading-relaxed font-medium">
                                    {pulse?.last_event?.message || 'Awaiting telemetry...'}
                                </p>
                                <div className="mt-3 text-[9px] font-mono text-zinc-700">{pulse?.last_event?.time || '---'}</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
