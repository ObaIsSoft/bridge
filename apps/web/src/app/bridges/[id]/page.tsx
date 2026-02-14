"use client";

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { toast } from 'sonner';
import {
    Shield,
    ShieldCheck,
    ShieldAlert,
    Github,
    Twitter,
    Linkedin,
    Mail,
    Send,
    CheckCircle2,
    AlertTriangle,
    Lock
} from 'lucide-react';
import { bridgesApi, handshakeApi } from '@/lib/api';

export default function BridgeDashboard() {
    const params = useParams();
    const id = params.id as string;

    const [bridge, setBridge] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [handshakeStatus, setHandshakeStatus] = useState<string | null>(null);

    useEffect(() => {
        loadBridge();
    }, [id]);

    const loadBridge = async () => {
        try {
            const data = await bridgesApi.get(id);
            setBridge(data);
        } catch (err: any) {
            toast.error("Failed to load bridge details");
        } finally {
            setLoading(false);
        }
    };

    const handleHandshake = async (method: string, recipient: string) => {
        if (!confirm(`Initialize handshake via ${method} to ${recipient}?`)) return;

        try {
            await handshakeApi.initiate({
                domain: bridge.domain,
                method,
                recipient,
                context: `Bridge: ${bridge.name}`
            });
            toast.success("Handshake initiated! Check your inbox/notifications.");
            setHandshakeStatus("PENDING");
        } catch (err: any) {
            toast.error(err.message);
        }
    };

    if (loading) return <div className="p-10 text-white">Loading...</div>;
    if (!bridge) return <div className="p-10 text-white">Bridge not found</div>;

    const perm = bridge.permission || {};
    const isAllowed = perm.status === "ALLOWED";

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-4xl font-bold text-white mb-2">{bridge.name}</h1>
                    <p className="text-zinc-400 font-mono">{bridge.domain}</p>
                </div>
                <div className={`px-4 py-2 rounded-full border ${isAllowed ? 'bg-green-500/10 border-green-500/20 text-green-500' : 'bg-red-500/10 border-red-500/20 text-red-500'} flex items-center gap-2`}>
                    {isAllowed ? <CheckCircle2 className="h-5 w-5" /> : <Lock className="h-5 w-5" />}
                    <span className="font-bold tracking-wider">{perm.status || "UNKNOWN"}</span>
                </div>
            </div>

            {/* Ethical Moat */}
            <div className="glass rounded-3xl p-8 border border-white/5">
                <div className="flex items-center gap-3 mb-6">
                    <Shield className="h-8 w-8 text-primary" />
                    <h2 className="text-2xl font-bold text-white">Ethical Moat</h2>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {/* Status & Compliance */}
                    <div className="space-y-4">
                        <h3 className="text-zinc-400 text-sm uppercase tracking-widest font-bold">Compliance Status</h3>
                        <div className="flex gap-4">
                            <div className="flex-1 bg-white/5 rounded-xl p-4 border border-white/5">
                                <div className="text-zinc-500 text-xs mb-1">Robots.txt</div>
                                <div className="text-white font-mono">{perm.robots_txt ? "✅ Respected" : "❌ Missing"}</div>
                            </div>
                            <div className="flex-1 bg-white/5 rounded-xl p-4 border border-white/5">
                                <div className="text-zinc-500 text-xs mb-1">Security.txt</div>
                                <div className="text-white font-mono">{perm.security_txt ? "✅ Found" : "❌ Missing"}</div>
                            </div>
                        </div>
                    </div>

                    {/* Contact Discovery */}
                    <div className="space-y-4">
                        <h3 className="text-zinc-400 text-sm uppercase tracking-widest font-bold">Discovered Contacts</h3>
                        <div className="grid grid-cols-1 gap-2">
                            {perm.contact_email ? (
                                <ContactRow icon={Mail} label="Email" value={perm.contact_email} action={() => handleHandshake('EMAIL', perm.contact_email)} />
                            ) : (
                                <div className="text-zinc-600 text-sm italic">No email found</div>
                            )}

                            {perm.twitter_handle && (
                                <ContactRow icon={Twitter} label="Twitter" value={perm.twitter_handle} action={() => handleHandshake('TWITTER', perm.twitter_handle)} />
                            )}

                            {perm.github_handle && (
                                <ContactRow icon={Github} label="GitHub" value={perm.github_handle} action={() => handleHandshake('GITHUB', perm.github_handle)} />
                            )}

                            {perm.linkedin_handle && (
                                <ContactRow icon={Linkedin} label="LinkedIn" value={perm.linkedin_handle} action={() => handleHandshake('LINKEDIN', perm.linkedin_handle)} />
                            )}
                        </div>
                    </div>
                </div>

                {/* Handshake Action */}
                {!isAllowed && (
                    <div className="mt-8 p-6 bg-yellow-500/10 border border-yellow-500/20 rounded-2xl flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <AlertTriangle className="h-8 w-8 text-yellow-500" />
                            <div>
                                <h3 className="text-white font-bold text-lg">Permission Required</h3>
                                <p className="text-zinc-400 text-sm">You must perform a Handshake to access this data ethically.</p>
                            </div>
                        </div>
                        <button
                            onClick={() => {
                                if (perm.contact_email) handleHandshake('EMAIL', perm.contact_email);
                                else if (perm.twitter_handle) handleHandshake('TWITTER', perm.twitter_handle);
                                else if (perm.github_handle) handleHandshake('GITHUB', perm.github_handle);
                                else toast.error("No contact method available to initiate protocol.");
                            }}
                            className="bg-yellow-500 text-black px-6 py-3 rounded-xl font-bold hover:scale-105 transition-transform flex items-center gap-2">
                            <Send className="h-4 w-4" /> Initiate Protocol
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}

function ContactRow({ icon: Icon, label, value, action }: any) {
    return (
        <div className="flex items-center justify-between bg-white/5 p-3 rounded-lg border border-white/5 group hover:border-primary/50 transition-colors">
            <div className="flex items-center gap-3">
                <div className="p-2 bg-black/30 rounded-lg text-zinc-400 group-hover:text-primary transition-colors">
                    <Icon className="h-4 w-4" />
                </div>
                <div className="text-sm text-zinc-300 font-mono truncate max-w-[200px]">{value}</div>
            </div>
            <button
                onClick={action}
                className="text-xs bg-primary/10 text-primary px-3 py-1.5 rounded-md hover:bg-primary hover:text-black transition-colors font-bold"
            >
                Connect
            </button>
        </div>
    );
}
