"use client";

import React, { useEffect, useState } from 'react';
import { toast } from 'sonner';
import {
    ToyBrick,
    Plus,
    Play,
    Trash2,
    MoreHorizontal,
    ExternalLink,
    AlertCircle,
    CheckCircle2,
    Clock
} from 'lucide-react';
import Link from 'next/link';
import { bridgesApi } from '@/lib/api';

export default function BridgesPage() {
    const [bridges, setBridges] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    const loadBridges = () => {
        setLoading(true);
        bridgesApi.list()
            .then(setBridges)
            .finally(() => setLoading(false));
    };

    useEffect(() => {
        loadBridges();
    }, []);

    const handleRun = async (id: string) => {
        try {
            await bridgesApi.run(id);
            toast.success("Extraction task started!");
        } catch (err: any) {
            toast.error(err.message);
        }
    };

    const handleDelete = async (id: string) => {
        if (!confirm("Are you sure you want to delete this bridge?")) return;
        try {
            await bridgesApi.delete(id);
            toast.success("Bridge deleted successfully");
            loadBridges();
        } catch (err: any) {
            toast.error(err.message);
        }
    };

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-4xl font-bold tracking-tight text-white mb-2">Bridges</h1>
                    <p className="text-zinc-400 max-w-lg">Manage your website-to-API bridges and monitor their real-time status.</p>
                </div>
                <Link
                    href="/bridges/new"
                    className="inline-flex items-center justify-center rounded-xl bg-primary px-6 py-3 text-sm font-bold text-black shadow-[0_0_20px_rgba(16,185,129,0.3)] transition-all hover:scale-105 active:scale-95 group"
                >
                    <Plus className="mr-2 h-5 w-5 transition-transform group-hover:rotate-90" />
                    CREATE BRIDGE
                </Link>
            </div>

            {loading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {[1, 2, 3, 4, 5, 6].map(i => (
                        <div key={i} className="h-48 glass animate-pulse rounded-2xl" />
                    ))}
                </div>
            ) : bridges.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-32 text-center glass rounded-3xl border-dashed border-white/10">
                    <div className="h-20 w-20 rounded-2xl bg-white/5 flex items-center justify-center mb-6">
                        <ToyBrick className="h-10 w-10 text-white opacity-20" />
                    </div>
                    <h3 className="text-2xl font-bold text-white mb-2">Build your first bridge</h3>
                    <p className="text-zinc-500 max-w-sm mx-auto mb-8">Transform any static or dynamic website into a clean, structured REST API in seconds.</p>
                    <Link href="/bridges/new" className="bg-white text-black px-8 py-3 rounded-xl font-bold hover:bg-zinc-200 transition-all hover:scale-105">
                        START BUILDING
                    </Link>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {bridges.map((bridge) => (
                        <div key={bridge.id} className="glass glass-hover rounded-2xl p-6 flex flex-col justify-between group overflow-hidden relative">
                            <div className="absolute top-0 right-0 p-3 opacity-0 group-hover:opacity-100 transition-opacity">
                                <ExternalLink className="h-4 w-4 text-zinc-500 hover:text-white cursor-pointer" onClick={() => window.open(bridge.target_url, '_blank')} />
                            </div>

                            <div className="space-y-4">
                                <div className="flex items-center gap-3">
                                    <div className="h-10 w-10 rounded-xl bg-white/5 flex items-center justify-center border border-white/10 group-hover:border-primary/30 transition-colors">
                                        <ToyBrick className="h-5 w-5 text-zinc-400 group-hover:text-primary" />
                                    </div>
                                    <div>
                                        <h3 className="font-bold text-white text-lg leading-tight truncate max-w-[180px]">{bridge.name}</h3>
                                        <p className="text-xs text-zinc-500 font-mono">{bridge.domain}</p>
                                    </div>
                                </div>

                                <div className="flex items-center gap-4 text-xs font-medium py-2">
                                    <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/5 border border-white/5">
                                        {bridge.status === 'active' ? (
                                            <>
                                                <div className="h-1.5 w-1.5 rounded-full bg-primary shadow-[0_0_8px_rgba(16,185,129,0.8)]" />
                                                <span className="text-primary uppercase tracking-wider text-[10px] font-bold">Active</span>
                                            </>
                                        ) : (
                                            <>
                                                <div className="h-1.5 w-1.5 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.8)]" />
                                                <span className="text-red-500 uppercase tracking-wider text-[10px] font-bold">Error</span>
                                            </>
                                        )}
                                    </div>
                                    <div className="flex items-center gap-1 text-zinc-500">
                                        <Clock className="h-3 w-3" />
                                        <span>{bridge.last_successful_extraction ? 'Loaded' : 'Never'}</span>
                                    </div>
                                </div>
                            </div>

                            <div className="mt-8 pt-4 border-t border-white/5 flex items-center justify-between">
                                <div className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest leading-none">
                                    Last Key Sync: <span className="text-zinc-300">Recently</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <button
                                        onClick={() => handleRun(bridge.id)}
                                        className="h-9 w-9 flex items-center justify-center rounded-lg bg-white/5 border border-white/5 hover:bg-primary hover:text-black hover:border-primary transition-all group/run" title="Run Extraction">
                                        <Play className="h-4 w-4 fill-current group-hover/run:scale-110 transition-transform" />
                                    </button>
                                    <button
                                        onClick={() => handleDelete(bridge.id)}
                                        className="h-9 w-9 flex items-center justify-center rounded-lg bg-white/5 border border-white/5 hover:bg-red-500/20 hover:text-red-500 hover:border-red-500/30 transition-all p-2" title="Delete">
                                        <Trash2 className="h-4 w-4" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
