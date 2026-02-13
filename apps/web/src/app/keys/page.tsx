"use client";

import React, { useEffect, useState } from 'react';
import {
    Key,
    Plus,
    Copy,
    Trash2,
    CheckCircle2,
    ShieldCheck,
    AlertCircle
} from 'lucide-react';
import { keysApi } from '@/lib/api';

export default function KeysPage() {
    const [keys, setKeys] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [copiedId, setCopiedId] = useState<string | null>(null);

    useEffect(() => {
        keysApi.list()
            .then(setKeys)
            .finally(() => setLoading(false));
    }, []);

    const copyToClipboard = (id: string, key: string) => {
        navigator.clipboard.writeText(key);
        setCopiedId(id);
        setTimeout(() => setCopiedId(null), 2000);
    };

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-4xl font-bold tracking-tight text-white mb-2 text-glow">API Keys</h1>
                    <p className="text-zinc-400 max-w-lg">Manage your authentication keys to access the Bridge API securely.</p>
                </div>
                <button className="inline-flex items-center justify-center rounded-xl bg-primary px-6 py-3 text-sm font-bold text-black shadow-[0_0_20px_rgba(16,185,129,0.3)] transition-all hover:scale-105 active:scale-95 group">
                    <Plus className="mr-2 h-5 w-5 transition-transform group-hover:rotate-90" />
                    GENERATE KEY
                </button>
            </div>

            <div className="grid gap-4">
                {loading ? (
                    <div className="grid gap-4">
                        {[1, 2].map(i => (
                            <div key={i} className="h-28 glass animate-pulse rounded-2xl" />
                        ))}
                    </div>
                ) : keys.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-32 text-center glass rounded-3xl border-dashed border-white/10">
                        <div className="h-20 w-20 rounded-2xl bg-white/5 flex items-center justify-center mb-6">
                            <Key className="h-10 w-10 text-white opacity-20" />
                        </div>
                        <h3 className="text-2xl font-bold text-white mb-2">No keys found</h3>
                        <p className="text-zinc-500 max-w-sm mx-auto mb-8">Generate an API key to allow your applications to securely fetch data from your extraction bridges.</p>
                        <button className="bg-white text-black px-8 py-3 rounded-xl font-bold hover:bg-zinc-200 transition-all hover:scale-105">
                            GENERATE FIRST KEY
                        </button>
                    </div>
                ) : (
                    <div className="grid gap-4">
                        {keys.map((key) => (
                            <div key={key.id} className="glass glass-hover rounded-2xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-4 group">
                                <div className="space-y-3">
                                    <div className="flex items-center gap-3">
                                        <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center border border-primary/20">
                                            <ShieldCheck className="h-5 w-5 text-primary" />
                                        </div>
                                        <div>
                                            <h3 className="font-bold text-white text-lg">{key.name || 'Default Production Key'}</h3>
                                            <div className="flex items-center gap-2 mt-0.5">
                                                <div className="h-1.5 w-1.5 rounded-full bg-primary shadow-[0_0_8px_rgba(16,185,129,0.8)]" />
                                                <span className="text-[10px] font-bold text-primary uppercase tracking-widest leading-none">Status: Active</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-2 bg-black/30 p-2 rounded-lg border border-white/5 w-fit">
                                        <code className="text-xs text-zinc-400 font-mono tracking-wider">
                                            {key.key.substring(0, 10)}<span className="opacity-30">**************************</span>
                                        </code>
                                        <button
                                            onClick={() => copyToClipboard(key.id, key.key)}
                                            className="p-1.5 hover:bg-white/5 rounded-md text-zinc-500 hover:text-white transition-colors"
                                        >
                                            {copiedId === key.id ? (
                                                <CheckCircle2 className="h-4 w-4 text-primary" />
                                            ) : (
                                                <Copy className="h-4 w-4" />
                                            )}
                                        </button>
                                    </div>
                                </div>

                                <div className="flex items-center gap-6 self-end md:self-center">
                                    <div className="text-right">
                                        <p className="text-[10px] text-zinc-500 uppercase tracking-widest font-bold mb-1">Last Sync</p>
                                        <p className="text-xs text-zinc-300 font-medium">{key.last_used_at ? new Date(key.last_used_at).toLocaleDateString() : 'Never Active'}</p>
                                    </div>
                                    <div className="h-10 w-[1px] bg-white/5 hidden md:block" />
                                    <button className="h-11 w-11 flex items-center justify-center rounded-xl bg-white/5 border border-white/5 hover:bg-red-500/10 hover:text-red-500 hover:border-red-500/20 transition-all">
                                        <Trash2 className="h-5 w-5" />
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            <div className="glass bg-amber-500/5 border-amber-500/10 rounded-2xl p-6 flex gap-4 items-start">
                <div className="p-2 bg-amber-500/10 rounded-lg">
                    <AlertCircle className="h-6 w-6 text-amber-500" />
                </div>
                <div className="space-y-1">
                    <h3 className="font-bold text-amber-500 uppercase tracking-widest text-xs">Security Advisory</h3>
                    <p className="text-sm text-amber-200/50 leading-relaxed max-w-2xl">
                        Keep your keys encrypted and never expose them in client-side codebases. Compromised keys should be rotated immediately using the command center.
                    </p>
                </div>
            </div>
        </div>
    );
}
