
"use client";

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { bridgesApi } from '@/lib/api';
import { Save, ArrowLeft, Terminal, Key } from 'lucide-react';
import Link from 'next/link';

export default function BridgeSettings() {
    const params = useParams();
    const router = useRouter();
    const id = params.id as string;

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    // Store full bridge object to merge updates
    const [bridge, setBridge] = useState<any>(null);

    // Form State for specific editable fields
    const [authConfig, setAuthConfig] = useState<string>("{}");
    const [interactionScript, setInteractionScript] = useState<string>("[]");
    const [bridgeName, setBridgeName] = useState("");

    useEffect(() => {
        loadBridge();
    }, [id]);

    const loadBridge = async () => {
        try {
            const data = await bridgesApi.get(id);
            setBridge(data);
            setBridgeName(data.name);
            setAuthConfig(JSON.stringify(data.auth_config || {}, null, 2));
            setInteractionScript(JSON.stringify(data.interaction_script || [], null, 2));
        } catch (err: any) {
            toast.error("Failed to load settings");
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async () => {
        setSaving(true);
        try {
            // Validate JSON
            let parsedAuth, parsedScript;
            try {
                parsedAuth = JSON.parse(authConfig);
            } catch (e) {
                toast.error("Invalid JSON in Auth Config");
                setSaving(false);
                return;
            }

            try {
                parsedScript = JSON.parse(interactionScript);
                if (!Array.isArray(parsedScript)) {
                    toast.error("Interaction Script must be an Array");
                    setSaving(false);
                    return;
                }
            } catch (e) {
                toast.error("Invalid JSON in Interaction Script");
                setSaving(false);
                return;
            }

            // Merge with existing bridge data because PUT requires all fields
            // Assuming the backend uses Pydantic model which expects full object or defaults
            // We spread specific fields we want to keep + updates
            await bridgesApi.update(id, {
                ...bridge,
                auth_config: parsedAuth,
                interaction_script: parsedScript
            });

            toast.success("Settings saved successfully");
        } catch (err: any) {
            toast.error(err.message || "Failed to save settings");
        } finally {
            setSaving(false);
        }
    };

    if (loading) return <div className="p-10 text-white">Loading...</div>;

    return (
        <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <Link href={`/bridges/${id}`} className="p-2 hover:bg-white/10 rounded-full transition-colors text-zinc-400 hover:text-white">
                        <ArrowLeft className="h-6 w-6" />
                    </Link>
                    <div>
                        <h1 className="text-3xl font-bold text-white">Settings: {bridgeName}</h1>
                        <p className="text-zinc-400">Configure User Simulation & Authentication</p>
                    </div>
                </div>
                <button
                    onClick={handleSave}
                    disabled={saving}
                    className="bg-primary text-black px-6 py-2 rounded-lg font-bold hover:scale-105 transition-transform flex items-center gap-2 disabled:opacity-50"
                >
                    <Save className="h-4 w-4" />
                    {saving ? "Saving..." : "Save Changes"}
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Auth Config */}
                <div className="glass rounded-xl p-6 border border-white/5 space-y-4">
                    <div className="flex items-center gap-2 mb-2">
                        <Key className="h-5 w-5 text-primary" />
                        <h2 className="text-xl font-bold text-white">Authentication</h2>
                    </div>
                    <p className="text-sm text-zinc-400">
                        JSON Configuration for Login or Cookies.
                        <br />Example: <code>{`{ "type": "cookie", "cookies": [...] }`}</code>
                    </p>
                    <textarea
                        value={authConfig}
                        onChange={(e) => setAuthConfig(e.target.value)}
                        className="w-full h-96 bg-black/50 border border-white/10 rounded-lg p-4 font-mono text-sm text-green-400 focus:outline-none focus:border-primary/50"
                        spellCheck={false}
                    />
                </div>

                {/* Interaction Script */}
                <div className="glass rounded-xl p-6 border border-white/5 space-y-4">
                    <div className="flex items-center gap-2 mb-2">
                        <Terminal className="h-5 w-5 text-primary" />
                        <h2 className="text-xl font-bold text-white">Interaction Script</h2>
                    </div>
                    <p className="text-sm text-zinc-400">
                        Array of steps to execute (Click, Scroll, Wait).
                        <br />Example: <code>{`[ { "action": "click", "selector": "#btn" } ]`}</code>
                    </p>
                    <textarea
                        value={interactionScript}
                        onChange={(e) => setInteractionScript(e.target.value)}
                        className="w-full h-96 bg-black/50 border border-white/10 rounded-lg p-4 font-mono text-sm text-yellow-400 focus:outline-none focus:border-primary/50"
                        spellCheck={false}
                    />
                </div>
            </div>
        </div>
    );
}
