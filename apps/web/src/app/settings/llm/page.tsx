"use client";

import { useState, useEffect } from "react";
import { Plus, Trash2, Check, X, Loader2 } from "lucide-react";

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
        return <div className="p-6 text-center">Loading...</div>;
    }

    return (
        <div className="min-h-screen bg-gray-50 p-6">
            <div className="max-w-4xl mx-auto">
                <div className="flex justify-between items-center mb-6">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">LLM Providers</h1>
                        <p className="text-gray-600 mt-1">Configure multiple LLM API keys with automatic failover</p>
                    </div>
                    <button
                        onClick={() => setShowAddForm(true)}
                        className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                    >
                        <Plus size={20} />
                        Add Provider
                    </button>
                </div>

                {showAddForm && (
                    <div className="bg-white p-6 rounded-lg shadow-md mb-6">
                        <h2 className="text-xl font-semibold mb-4">Add New Provider</h2>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Provider</label>
                                <select
                                    value={newProvider.provider}
                                    onChange={(e) => setNewProvider({ ...newProvider, provider: e.target.value, model: "" })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                >
                                    {PROVIDER_OPTIONS.map(p => (
                                        <option key={p.id} value={p.id}>{p.name}</option>
                                    ))}
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Model</label>
                                <select
                                    value={newProvider.model}
                                    onChange={(e) => setNewProvider({ ...newProvider, model: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                >
                                    <option value="">Select a model</option>
                                    {selectedProviderInfo?.models.map(m => (
                                        <option key={m} value={m}>{m}</option>
                                    ))}
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">API Key</label>
                                <input
                                    type="password"
                                    value={newProvider.api_key}
                                    onChange={(e) => setNewProvider({ ...newProvider, api_key: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                    placeholder="sk-..."
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Priority (lower = higher priority)</label>
                                <input
                                    type="number"
                                    value={newProvider.priority}
                                    onChange={(e) => setNewProvider({ ...newProvider, priority: parseInt(e.target.value) })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                    min="1"
                                />
                            </div>

                            <div className="flex gap-3">
                                <button
                                    onClick={() => testProvider(newProvider.provider, newProvider.model, newProvider.api_key)}
                                    disabled={!newProvider.model || !newProvider.api_key || testing !== null}
                                    className="flex-1 bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 disabled:opacity-50 flex items-center justify-center gap-2"
                                >
                                    {testing === newProvider.provider ? <Loader2 size={16} className="animate-spin" /> : null}
                                    Test Connection
                                </button>
                                <button
                                    onClick={addProvider}
                                    disabled={!newProvider.model || !newProvider.api_key}
                                    className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                                >
                                    Add Provider
                                </button>
                                <button
                                    onClick={() => setShowAddForm(false)}
                                    className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300"
                                >
                                    Cancel
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                <div className="space-y-4">
                    {providers.length === 0 ? (
                        <div className="bg-white p-8 rounded-lg shadow-md text-center text-gray-500">
                            No LLM providers configured. Add one to get started!
                        </div>
                    ) : (
                        providers.map((p) => (
                            <div key={p.id} className="bg-white p-6 rounded-lg shadow-md flex items-center justify-between">
                                <div className="flex-1">
                                    <div className="flex items-center gap-3">
                                        <span className="text-2xl font-bold text-gray-400">#{p.priority}</span>
                                        <div>
                                            <h3 className="text-lg font-semibold text-gray-900 capitalize">{p.provider}</h3>
                                            <p className="text-sm text-gray-600">{p.model}</p>
                                        </div>
                                        {p.is_active ? (
                                            <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs font-medium">
                                                <Check size={12} className="inline mr-1" />
                                                Active
                                            </span>
                                        ) : (
                                            <span className="bg-red-100 text-red-800 px-2 py-1 rounded text-xs font-medium">
                                                <X size={12} className="inline mr-1" />
                                                Disabled
                                            </span>
                                        )}
                                    </div>
                                    <div className="mt-2 text-sm text-gray-600">
                                        {p.consecutive_failures > 0 && (
                                            <span className="text-red-600">⚠️ {p.consecutive_failures} failures</span>
                                        )}
                                        {p.last_used_at && (
                                            <span className="ml-4">Last used: {new Date(p.last_used_at).toLocaleString()}</span>
                                        )}
                                    </div>
                                </div>
                                <button
                                    onClick={() => deleteProvider(p.id)}
                                    className="text-red-600 hover:text-red-800 p-2"
                                    title="Delete"
                                >
                                    <Trash2 size={20} />
                                </button>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
}
