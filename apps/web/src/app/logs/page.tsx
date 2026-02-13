"use client";

import React, { useEffect, useState } from 'react';
import {
    History,
    Search,
    Filter,
    ArrowUpRight,
    ToyBrick,
    Clock,
    Database,
    AlertCircle,
    CheckCircle2
} from 'lucide-react';
import { bridgesApi } from '@/lib/api';

export default function LogsPage() {
    const [logs, setLogs] = useState<any[]>([]);
    const [stats, setStats] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [allLogs, statsData] = await Promise.all([
                    bridgesApi.getAllLogs(),
                    bridgesApi.getStats()
                ]);
                setLogs(allLogs);
                setStats(statsData);
            } catch (err) {
                console.error("Error fetching data:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div>
                <h1 className="text-4xl font-bold tracking-tight text-white mb-2 text-glow">Extraction Logs</h1>
                <p className="text-zinc-400 max-w-lg">Monitor the historical performance and results of your extraction bridges.</p>
            </div>

            <div className="glass rounded-2xl overflow-hidden shadow-2xl">
                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left">
                        <thead>
                            <tr className="bg-white/5 border-b border-white/10">
                                <th className="px-6 py-4 font-bold text-zinc-400 uppercase tracking-widest text-[10px]">Timestamp</th>
                                <th className="px-6 py-4 font-bold text-zinc-400 uppercase tracking-widest text-[10px]">Bridge</th>
                                <th className="px-6 py-4 font-bold text-zinc-400 uppercase tracking-widest text-[10px]">Method</th>
                                <th className="px-6 py-4 font-bold text-zinc-400 uppercase tracking-widest text-[10px]">Status</th>
                                <th className="px-6 py-4 font-bold text-zinc-400 uppercase tracking-widest text-[10px] text-right">Latency</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {loading ? (
                                Array.from({ length: 5 }).map((_, i) => (
                                    <tr key={i} className="animate-pulse">
                                        <td colSpan={5} className="px-6 py-6 bg-white/5" />
                                    </tr>
                                ))
                            ) : logs.length === 0 ? (
                                <tr>
                                    <td colSpan={5} className="px-6 py-20 text-center text-zinc-500 italic">
                                        No extraction logs found. Logs will appear here once your bridges start running.
                                    </td>
                                </tr>
                            ) : (
                                logs.map((log) => (
                                    <tr key={log.id} className="hover:bg-white/5 transition-colors group">
                                        <td className="px-6 py-4 text-zinc-400 whitespace-nowrap">
                                            {new Date(log.created_at).toLocaleString()}
                                        </td>
                                        <td className="px-6 py-4 font-semibold text-white group-hover:text-primary transition-colors">
                                            {log.bridgeName || 'Unknown Bridge'}
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-white/5 text-zinc-400 border border-white/10">
                                                {log.method}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-2">
                                                {log.status_code >= 200 && log.status_code < 300 ? (
                                                    <div className="flex items-center gap-1.5 text-primary">
                                                        <CheckCircle2 className="h-4 w-4" />
                                                        <span className="font-bold">{log.status_code}</span>
                                                    </div>
                                                ) : (
                                                    <div className="flex items-center gap-1.5 text-red-400">
                                                        <AlertCircle className="h-4 w-4" />
                                                        <span className="font-bold">{log.status_code}</span>
                                                    </div>
                                                )}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 text-right tabular-nums text-zinc-400 font-mono">
                                            {log.latency_ms}ms
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {[
                    { label: 'Success Rate', value: stats?.success_rate ?? '...', icon: CheckCircle2, color: 'text-primary' },
                    { label: 'Total Content', value: stats?.total_data_volume ?? '...', icon: Database, color: 'text-purple-500' },
                    { label: 'Avg Latency', value: stats?.avg_latency ?? '...', icon: Clock, color: 'text-blue-500' }
                ].map((stat, i) => (
                    <div key={i} className="glass p-6 rounded-2xl flex items-center gap-4 group hover:border-primary/20 transition-all duration-300">
                        <div className={`p-3 rounded-xl bg-white/5 ${stat.color} group-hover:scale-110 transition-transform`}>
                            <stat.icon className="h-6 w-6" />
                        </div>
                        <div>
                            <p className="text-[10px] text-zinc-500 uppercase tracking-widest font-bold mb-1">{stat.label}</p>
                            <p className="text-2xl font-black text-white">{stat.value}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
