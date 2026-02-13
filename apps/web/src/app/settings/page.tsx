"use client";

import React, { useEffect, useState } from 'react';
import {
    Settings as SettingsIcon,
    Globe,
    Bell,
    Shield,
    Settings2,
    Plus,
    Trash2,
    Database,
    ChevronRight,
    Save
} from 'lucide-react';
import { webhooksApi, systemApi } from '@/lib/api';

export default function SettingsPage() {
    const [webhooks, setWebhooks] = useState<any[]>([]);
    const [health, setHealth] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [newWebhook, setNewWebhook] = useState({ name: '', url: '' });

    const loadData = () => {
        setLoading(true);
        Promise.all([
            webhooksApi.list(),
            systemApi.getHealth()
        ]).then(([webhooksData, healthData]) => {
            setWebhooks(webhooksData);
            setHealth(healthData);
        })
            .catch(err => console.error(err))
            .finally(() => setLoading(false));
    };

    useEffect(() => {
        loadData();
        const interval = setInterval(() => {
            systemApi.getHealth().then(setHealth).catch(() => { });
        }, 5000);
        return () => clearInterval(interval);
    }, []);

    const handleCreateWebhook = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await webhooksApi.create(newWebhook);
            setNewWebhook({ name: '', url: '' });
            loadData();
        } catch (err: any) {
            alert(err.message);
        }
    };

    const handleDeleteWebhook = async (id: string) => {
        if (!confirm("Delete this webhook?")) return;
        try {
            await webhooksApi.delete(id);
            loadData();
        } catch (err: any) {
            alert(err.message);
        }
    };

    return (
        <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div>
                <h1 className="text-5xl font-black tracking-tighter text-white mb-2 text-glow">Settings</h1>
                <p className="text-zinc-500 max-w-lg font-medium">Configure global platform behavior, notifications, and delivery webhooks.</p>
            </div>

            <div className="grid gap-8">
                <div className="glass rounded-3xl p-8 space-y-8 shadow-2xl relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-8 opacity-5">
                        <Bell className="h-32 w-32 text-white" />
                    </div>

                    <div className="flex items-center gap-4 relative z-10">
                        <div className="p-3 rounded-2xl bg-primary/10 border border-primary/20">
                            <Bell className="h-6 w-6 text-primary" />
                        </div>
                        <div>
                            <h2 className="text-2xl font-black text-white tracking-tight">Webhooks</h2>
                            <p className="text-sm text-zinc-500 font-medium">Transmit real-time extraction payloads to external endpoints.</p>
                        </div>
                    </div>

                    <form onSubmit={handleCreateWebhook} className="space-y-6 pt-8 border-t border-white/5 relative z-10">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-2">
                                <label className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest ml-1">Webhook Alias</label>
                                <input
                                    required
                                    value={newWebhook.name}
                                    onChange={e => setNewWebhook({ ...newWebhook, name: e.target.value })}
                                    placeholder="Production Delivery"
                                    className="w-full rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-white outline-none focus:border-primary/50 focus:bg-white/10 transition-all placeholder:text-zinc-600"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest ml-1">Endpoint URL</label>
                                <input
                                    required
                                    type="url"
                                    value={newWebhook.url}
                                    onChange={e => setNewWebhook({ ...newWebhook, url: e.target.value })}
                                    placeholder="https://api.yourdomain.com/webhook"
                                    className="w-full rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-white outline-none focus:border-primary/50 focus:bg-white/10 transition-all placeholder:text-zinc-600"
                                />
                            </div>
                        </div>
                        <button type="submit" className="bg-white text-black px-8 py-3 rounded-xl font-bold hover:bg-zinc-200 transition-all hover:scale-105 active:scale-95 flex items-center gap-2">
                            <Plus className="h-4 w-4" />
                            REGISTER WEBHOOK
                        </button>
                    </form>

                    <div className="grid gap-3 pt-4">
                        {loading ? (
                            <div className="h-20 glass animate-pulse rounded-2xl mt-4" />
                        ) : webhooks.length === 0 ? (
                            <div className="py-12 flex flex-col items-center justify-center border border-dashed border-white/5 rounded-2xl bg-white/1 tracking-tight">
                                <p className="text-zinc-600 font-medium">No active webhooks configured</p>
                            </div>
                        ) : (
                            webhooks.map((hook) => (
                                <div key={hook.id} className="flex items-center justify-between p-5 rounded-2xl bg-white/5 border border-white/5 hover:border-white/10 transition-all group">
                                    <div className="space-y-1">
                                        <p className="font-bold text-white leading-tight">{hook.name}</p>
                                        <p className="text-xs text-zinc-500 truncate max-w-sm font-mono opacity-60 group-hover:opacity-100 transition-opacity">{hook.url}</p>
                                    </div>
                                    <div className="flex items-center gap-4">
                                        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-primary/10 border border-primary/20">
                                            <div className="h-1 w-1 rounded-full bg-primary animate-pulse" />
                                            <span className="text-[9px] font-bold text-primary uppercase tracking-widest">Active</span>
                                        </div>
                                        <button
                                            onClick={() => handleDeleteWebhook(hook.id)}
                                            className="h-9 w-9 flex items-center justify-center rounded-lg bg-white/5 text-zinc-500 hover:text-red-500 hover:bg-red-500/10 transition-all">
                                            <Trash2 className="h-4 w-4" />
                                        </button>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                <div className="grid md:grid-cols-2 gap-8">
                    <div className="glass rounded-3xl p-8 space-y-6 shadow-xl">
                        <div className="flex items-center gap-4">
                            <div className="p-3 rounded-2xl bg-amber-500/10 border border-amber-500/20">
                                <Database className="h-6 w-6 text-amber-500" />
                            </div>
                            <div>
                                <h2 className="text-xl font-black text-white tracking-tight">Health</h2>
                                <p className="text-sm text-zinc-500 font-medium">Internal sub-system performance.</p>
                            </div>
                        </div>

                        <div className="grid gap-3">
                            {[
                                { label: 'Database Node', status: health?.database === 'connected' ? 'Optimal' : 'Checking...', color: health?.database === 'connected' ? 'text-primary' : 'text-amber-500' },
                                { label: 'Redis Cluster', status: health?.redis === 'connected' ? 'Connected' : 'Checking...', color: health?.redis === 'connected' ? 'text-primary' : 'text-amber-500' },
                                { label: 'Extraction Engine', status: health?.playwright === 'ready' ? 'Ready' : 'Initializing...', color: health?.playwright === 'ready' ? 'text-primary' : 'text-amber-500' }
                            ].map((item, i) => (
                                <div key={i} className="flex items-center justify-between p-4 rounded-xl bg-white/3 border border-white/5">
                                    <span className="text-xs font-bold text-zinc-500 uppercase tracking-widest">{item.label}</span>
                                    <span className={`text-[10px] font-black uppercase tracking-widest ${item.color}`}>{item.status}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="glass rounded-3xl p-8 space-y-6 shadow-xl relative overflow-hidden flex flex-col justify-between">
                        <div className="flex items-center gap-4">
                            <div className="p-3 rounded-2xl bg-blue-500/10 border border-blue-500/20">
                                <Shield className="h-6 w-6 text-blue-500" />
                            </div>
                            <div>
                                <h2 className="text-xl font-black text-white tracking-tight">Security</h2>
                                <p className="text-sm text-zinc-500 font-medium">Platform hardening status.</p>
                            </div>
                        </div>

                        <div className="p-5 rounded-2xl bg-white/3 border border-white/5">
                            <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-2">Encryption Mode</p>
                            <p className="text-xl font-black text-white tracking-tight">AES-256-GCM</p>
                            <p className="text-[10px] text-zinc-600 font-mono mt-1">Status: Enforced Globally</p>
                        </div>

                        <div className="flex justify-end gap-3 mt-4">
                            <button className="px-8 py-3 border border-white/10 rounded-xl font-bold hover:bg-white/5 transition-all text-sm text-white/50">CANCEL</button>
                            <button className="px-8 py-3 bg-primary text-black rounded-xl font-black hover:scale-105 transition-all text-sm flex items-center gap-2 shadow-[0_0_20px_rgba(16,185,129,0.3)]">
                                <Save className="h-4 w-4" />
                                SAVE SYSTEM
                            </button>
                        </div>
                    </div>
                </div>
            </div >
        </div >
    );
}
