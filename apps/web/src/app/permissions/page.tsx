"use client";

import React from 'react';
import { Shield, ShieldAlert, Users, Lock, ChevronRight, CheckCircle2, AlertTriangle, Key } from 'lucide-react';

export default function PermissionsPage() {
    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Permissions & RBAC</h1>
                    <p className="text-muted-foreground">Manage user roles and resource access control policies.</p>
                </div>
                <div className="px-3 py-1 bg-amber-500/10 border border-amber-500/20 text-amber-500 text-[10px] font-bold rounded-full uppercase tracking-wider">
                    Enterprise Feature
                </div>
            </div>

            <div className="grid gap-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="p-6 rounded-xl border bg-card/50 space-y-3">
                        <Users className="h-6 w-6 text-primary" />
                        <h3 className="font-semibold text-white">Teams</h3>
                        <p className="text-xs text-zinc-500 leading-relaxed">Organize users into teams and assign shared permissions to bridges and API keys.</p>
                    </div>
                    <div className="p-6 rounded-xl border bg-card/50 space-y-3">
                        <Shield className="h-6 w-6 text-green-500" />
                        <h3 className="font-semibold text-white">Policies</h3>
                        <p className="text-xs text-zinc-500 leading-relaxed">Define fine-grained JSON policies to restrict IP ranges or extraction frequency per key.</p>
                    </div>
                    <div className="p-6 rounded-xl border bg-card/50 space-y-3">
                        <Lock className="h-6 w-6 text-amber-500" />
                        <h3 className="font-semibold text-white">Audit Logs</h3>
                        <p className="text-xs text-zinc-500 leading-relaxed">Full history of who modified which bridge and when. Compliance-ready reporting.</p>
                    </div>
                </div>

                <div className="rounded-xl border border-dashed border-zinc-800 bg-card/20 p-12 text-center space-y-4">
                    <ShieldAlert className="h-12 w-12 mx-auto text-zinc-700" />
                    <h3 className="text-lg font-semibold text-white">Advanced RBAC is limited in Beta</h3>
                    <p className="text-sm text-zinc-500 max-w-md mx-auto">
                        We are currently perfecting the multi-tenant isolation layer. Comprehensive role-based access control will be enabled in the next major update.
                    </p>
                    <button className="text-primary text-sm font-medium hover:underline flex items-center gap-1 mx-auto" onClick={() => alert("Interest recorded!")}>
                        Request Early Access <ChevronRight className="h-3 w-3" />
                    </button>
                </div>

                <div className="bg-red-500/5 border border-red-500/10 rounded-xl p-6 flex gap-4 items-start">
                    <AlertTriangle className="h-6 w-6 text-red-500 shrink-0" />
                    <div className="space-y-1">
                        <h3 className="font-semibold text-red-500">Security Notice</h3>
                        <p className="text-sm text-red-200/50 leading-relaxed">
                            During the Beta period, all users with a valid Clerk authentication session have administrative access to this workspace. Do not share your login credentials.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
