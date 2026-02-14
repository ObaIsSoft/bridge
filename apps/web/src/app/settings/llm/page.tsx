"use client";

import { useState, useEffect } from "react";
import { Plus, Trash2, Check, X, Loader2, Brain } from "lucide-react";

interface LLMProvider {
    id: string;
    provider: string;
    model: string;
    priority: number;
    is_active: boolean;
    consecutive_failures: number;
    last_used_at: string | null;
    last_error: string | null;
}

const PROVIDER_OPTIONS = [
    { id: "openai", name: "OpenAI", models: ["gpt-5.2-instant", "gpt-4.5-turbo", "gpt-4o-mini", "o1", "o1-mini"] },
    { id: "anthropic", name: "Anthropic", models: ["claude-opus-4.6", "claude-sonnet-4.5", "claude-haiku-4.5"] },
    { id: "google", name: "Google Gemini", models: ["gemini-3-deep-think", "gemini-2.5-pro", "gemini-2.5-flash"] },
    { id: "mistral", name: "Mistral AI", models: ["mistral-large-2", "mistral-medium-3", "codestral-latest"] },
    { id: "cohere", name: "Cohere", models: ["command-r-plus", "command-r", "command-r-7b"] },
    { id: "groq", name: "Groq", models: ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"] },
    { id: "openrouter", name: "OpenRouter", models: ["openai/gpt-4.5-turbo", "anthropic/claude-opus-4"] },
    { id: "ollama", name: "Ollama (Local)", models: ["llama3.3", "llama3.1", "mistral", "qwen2.5"] },
];

export default function LLMSettingsPage() {
    const [providers, setProviders] = useState<LLMProvider[]>([]);
    const [loading, setLoading] = useState(true);
    const [showAddForm, setShowAddForm] = useState(false);
    const [newProvider, setNewProvider] = useState({ provider: "openai", model: "", api_key: "", priority: 1 });
    const [testing, setTesting] = useState<string | null>(null);

    useEffect(() => {
        fetchProviders();
    }, []);

    const fetchProviders = async () => {
        try {
            const apiKey = localStorage.getItem("bridge_api_key");
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/llm/providers`, {
                headers: { "X-API-Key": apiKey || "" },
            });
            if (res.ok) {
                const data = await res.json();
                setProviders(data);
            }
        } catch (error) {
            console.error("Failed to fetch providers", error);
        } finally {
            setLoading(false);
        }
    };

    const addProvider = async () => {
        try {
            const apiKey = localStorage.getItem("bridge_api_key");
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/llm/providers`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-API-Key": apiKey || "",
                },
                body: JSON.stringify(newProvider),
            });

            if (res.ok) {
                await fetchProviders();
                setShowAddForm(false);
                setNewProvider({ provider: "openai", model: "", api_key: "", priority: 1 });
            }
        } catch (error) {
            console.error("Failed to add provider", error);
        }
    };

    const deleteProvider = async (id: string) => {
        if (!confirm("Delete this LLM provider?")) return;
        try {
            const apiKey = localStorage.getItem("bridge_api_key");
            await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/llm/providers/${id}`, {
                method: "DELETE",
                headers: { "X-API-Key": apiKey || "" },
            });
            await fetchProviders();
        } catch (error) {
            console.error("Failed to delete provider", error);
        }
    };

    const testProvider = async (provider: string, model: string, api_key: string) => {
        setTesting(provider);
        try {
            const bridgeApiKey = localStorage.getItem("bridge_api_key");
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/llm/providers/test`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-API-Key": bridgeApiKey || "",
                },
                body: JSON.stringify({ provider, model, api_key }),
            });

            const result = await res.json();
            alert(result.status === "success" ? `✅ Test successful! (${result.latency_ms}ms)` : `❌ Test failed: ${result.error}`);
        } catch (error) {
            alert(`❌ Test failed: ${error}`);
        } finally {
            setTesting(null);
        }
    };

    const selectedProviderInfo = PROVIDER_OPTIONS.find(p => p.id === newProvider.provider);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <Loader2 className="h-8 w-8 text-primary animate-spin" />
            </div>
        );
    }

    return (
        <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-700">
            {/* Header */}
            <div className="flex justify-between items-start">
                <div>
                    <h1 className="text-5xl font-black tracking-tighter text-white mb-2 text-glow">LLM Providers</h1>
                    <p className="text-zinc-500 max-w-lg font-medium">
                        Configure multiple LLM API keys with automatic failover and priority-based selection.
                    </p>
                </div>
                <button
                    onClick={() => setShowAddForm(true)}
                    className="glass px-6 py-3 rounded-xl flex items-center gap-2 text-white font-semibold hover:bg-primary/10 border border-primary/20 transition-all"
                >
                    <Plus size={20} className="text-primary" />
                    Add Provider
                </button>
            </div>

            {/* Add Provider Form */}
            {showAddForm && (
                <div className="glass rounded-3xl p-8 shadow-2xl border border-white/10 animate-in slide-in-from-top duration-300">
                    <div className="flex items-center gap-4 mb-6">
                        <div className="p-3 rounded-2xl bg-primary/10 border border-primary/20">
                            <Brain className="h-6 w-6 text-primary" />
                        </div>
                        <h2 className="text-2xl font-black text-white tracking-tight">Add New Provider</h2>
                    </div>

                    <div className="space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-2">
                                <label className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest ml-1">Provider</label>
                                <select
                                    value={newProvider.provider}
                                    onChange={(e) => setNewProvider({ ...newProvider, provider: e.target.value, model: "" })}
                                    className="w-full rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-white outline-none focus:border-primary/50 focus:bg-white/10 transition-all"
                                >
                                    {PROVIDER_OPTIONS.map(p => (
                                        <option key={p.id} value={p.id} className="bg-zinc-900">{p.name}</option>
                                    ))}
                                </select>
                            </div>

                            <div className="space-y-2">
                                <label className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest ml-1">Model</label>
                                <select
                                    value={newProvider.model}
                                    onChange={(e) => setNewProvider({ ...newProvider, model: e.target.value })}
                                    className="w-full rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-white outline-none focus:border-primary/50 focus:bg-white/10 transition-all"
                                >
                                    <option value="" className="bg-zinc-900">Select a model</option>
                                    {selectedProviderInfo?.models.map(m => (
                                        <option key={m} value={m} className="bg-zinc-900">{m}</option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest ml-1">API Key</label>
                            <input
                                type="password"
                                value={newProvider.api_key}
                                onChange={(e) => setNewProvider({ ...newProvider, api_key: e.target.value })}
                                className="w-full rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-white outline-none focus:border-primary/50 focus:bg-white/10 transition-all placeholder:text-zinc-600"
                                placeholder="sk-..."
                            />
                        </div>

                        <div className="space-y-2">
                            <label className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest ml-1">Priority (lower = higher)</label>
                            <input
                                type="number"
                                value={newProvider.priority}
                                onChange={(e) => setNewProvider({ ...newProvider, priority: parseInt(e.target.value) })}
                                className="w-full rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-white outline-none focus:border-primary/50 focus:bg-white/10 transition-all"
                                min="1"
                            />
                        </div>

                        <div className="flex gap-3 pt-4">
                            <button
                                onClick={() => testProvider(newProvider.provider, newProvider.model, newProvider.api_key)}
                                disabled={!newProvider.model || !newProvider.api_key || testing !== null}
                                className="flex-1 glass px-6 py-3 rounded-xl font-semibold text-white hover:bg-white/10 border border-white/10 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                            >
                                {testing === newProvider.provider ? <Loader2 size={16} className="animate-spin" /> : null}
                                Test Connection
                            </button>
                            <button
                                onClick={addProvider}
                                disabled={!newProvider.model || !newProvider.api_key}
                                className="flex-1 bg-primary text-black px-6 py-3 rounded-xl font-bold hover:bg-primary/90 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                Add Provider
                            </button>
                            <button
                                onClick={() => setShowAddForm(false)}
                                className="glass px-6 py-3 rounded-xl font-semibold text-white hover:bg-white/10 border border-white/10 transition-all"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Providers List */}
            <div className="space-y-4">
                {providers.length === 0 ? (
                    <div className="glass rounded-3xl p-12 text-center shadow-2xl border border-white/10">
                        <Brain className="h-16 w-16 text-zinc-600 mx-auto mb-4" />
                        <p className="text-zinc-500 font-medium">No LLM providers configured. Add one to get started!</p>
                    </div>
                ) : (
                    providers.map((p) => (
                        <div key={p.id} className="glass rounded-3xl p-6 shadow-xl border border-white/10 flex items-center justify-between hover:border-primary/20 transition-all group">
                            <div className="flex items-center gap-6 flex-1">
                                <div className="flex items-center justify-center h-12 w-12 rounded-xl bg-primary/10 border border-primary/20 text-primary font-black text-xl">
                                    #{p.priority}
                                </div>
                                <div className="flex-1">
                                    <div className="flex items-center gap-3 mb-1">
                                        <h3 className="text-lg font-bold text-white capitalize">{p.provider}</h3>
                                        {p.is_active ? (
                                            <span className="bg-primary/10 border border-primary/20 text-primary px-2 py-1 rounded-lg text-xs font-bold flex items-center gap-1">
                                                <Check size={12} />
                                                Active
                                            </span>
                                        ) : (
                                            <span className="bg-red-500/10 border border-red-500/20 text-red-400 px-2 py-1 rounded-lg text-xs font-bold flex items-center gap-1">
                                                <X size={12} />
                                                Disabled
                                            </span>
                                        )}
                                    </div>
                                    <p className="text-sm text-zinc-500 font-mono">{p.model}</p>
                                    {(p.consecutive_failures > 0 || p.last_used_at) && (
                                        <div className="mt-2 flex items-center gap-4 text-xs">
                                            {p.consecutive_failures > 0 && (
                                                <span className="text-red-400">⚠️ {p.consecutive_failures} failures</span>
                                            )}
                                            {p.last_used_at && (
                                                <span className="text-zinc-600">Last used: {new Date(p.last_used_at).toLocaleString()}</span>
                                            )}
                                        </div>
                                    )}
                                </div>
                            </div>
                            <button
                                onClick={() => deleteProvider(p.id)}
                                className="p-3 rounded-xl text-red-400 hover:bg-red-500/10 border border-transparent hover:border-red-500/20 transition-all opacity-0 group-hover:opacity-100"
                                title="Delete"
                            >
                                <Trash2 size={18} />
                            </button>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
