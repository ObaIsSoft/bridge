"use client";

import { ShieldAlert, RefreshCw, FileText, CheckCircle2, AlertTriangle, ExternalLink } from "lucide-react";
import { useState, useEffect } from "react";
import { bridgesApi } from "@/lib/api";

export default function SecurityPage() {
    const [loading, setLoading] = useState(false);
    const [isDeep, setIsDeep] = useState(false);
    const [findings, setFindings] = useState<any[]>([]);
    const [scannedAt, setScannedAt] = useState<string | null>(null);

    const runScan = async () => {
        setLoading(true);
        try {
            const data = isDeep ? await bridgesApi.scanDeep() : await bridgesApi.scan();
            setFindings(data.findings);
            setScannedAt(new Date(data.scanned_at).toLocaleString());
        } catch (err) {
            console.error("Scan failed:", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        runScan();
    }, []);

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-white flex items-center gap-3">
                        <ShieldAlert className="w-8 h-8 text-red-500" />
                        Security Audit
                    </h1>
                    <p className="text-zinc-400 mt-1">
                        Real-time scanning for exposed API keys and sensitive credentials.
                    </p>
                </div>
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2 bg-zinc-900 border border-zinc-800 px-3 py-1.5 rounded-lg">
                        <span className="text-xs font-medium text-zinc-500 uppercase tracking-wider">Deep Audit</span>
                        <button
                            onClick={() => setIsDeep(!isDeep)}
                            className={`w-10 h-5 rounded-full transition-colors relative ${isDeep ? 'bg-red-500' : 'bg-zinc-700'}`}
                        >
                            <div className={`absolute top-1 w-3 h-3 bg-white rounded-full transition-all ${isDeep ? 'left-6' : 'left-1'}`} />
                        </button>
                    </div>
                    <button
                        onClick={runScan}
                        disabled={loading}
                        className="bg-white text-black px-4 py-2 rounded-lg font-medium hover:bg-zinc-200 transition-all flex items-center gap-2 disabled:opacity-50"
                    >
                        <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                        {loading ? 'Scanning...' : 'Run Audit'}
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-4 flex flex-col items-center justify-center text-center space-y-2">
                    <span className="text-zinc-500 text-sm font-medium">Total Issues</span>
                    <span className={`text-4xl font-bold ${findings.length > 0 ? 'text-red-500' : 'text-green-500'}`}>
                        {findings.length}
                    </span>
                </div>
                <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-4 flex flex-col items-center justify-center text-center space-y-2 col-span-2">
                    <span className="text-zinc-500 text-sm font-medium">Audit Summary</span>
                    <div className="flex items-center gap-3">
                        {findings.length > 0 ? (
                            <>
                                <AlertTriangle className="w-6 h-6 text-amber-500" />
                                <span className="text-lg text-white font-medium">Potential Leaks Detected</span>
                            </>
                        ) : (
                            <>
                                <CheckCircle2 className="w-6 h-6 text-green-500" />
                                <span className="text-lg text-white font-medium">System Secure</span>
                            </>
                        )}
                        <span className="text-zinc-500 text-sm ml-2">Last run: {scannedAt || 'Never'}</span>
                    </div>
                </div>
                <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-4 flex flex-col items-center justify-center text-center space-y-2">
                    <span className="text-zinc-500 text-sm font-medium">Live Monitoring</span>
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                        <span className="text-sm text-green-500 font-medium">Active</span>
                    </div>
                </div>
            </div>

            <div className="bg-black border border-zinc-800 rounded-xl overflow-hidden">
                <div className="bg-zinc-900 border-b border-zinc-800 px-6 py-4 flex items-center gap-2">
                    <FileText className="w-5 h-5 text-zinc-400" />
                    <h2 className="text-lg font-semibold text-white">Detection Log</h2>
                </div>
                <div className="divide-y divide-zinc-800">
                    {findings.length === 0 ? (
                        <div className="p-12 text-center space-y-4">
                            <div className="bg-green-500/10 w-16 h-16 rounded-full flex items-center justify-center mx-auto border border-green-500/20">
                                <CheckCircle2 className="w-8 h-8 text-green-500" />
                            </div>
                            <div className="max-w-xs mx-auto">
                                <p className="text-white font-medium">All systems clear!</p>
                                <p className="text-sm text-zinc-500">No exposed keys or secrets found.</p>
                            </div>
                        </div>
                    ) : (
                        findings.map((finding, idx) => (
                            <div key={idx} className="px-6 py-4 flex items-center justify-between hover:bg-zinc-900/30 transition-colors group">
                                <div className="space-y-1">
                                    <div className="flex items-center gap-2">
                                        <span className="bg-red-500/10 text-red-500 border border-red-500/20 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider">
                                            {finding.type}
                                        </span>
                                        <span className="text-zinc-300 font-mono text-xs">{finding.match}</span>
                                        {finding.validation_status && (
                                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${finding.validation_status === 'active' ? 'bg-red-500/20 text-red-500 border border-red-500/30' :
                                                    finding.validation_status === 'revoked' ? 'bg-green-500/20 text-green-500 border border-green-500/30' :
                                                        'bg-zinc-500/20 text-zinc-500 border border-zinc-500/30'
                                                }`}>
                                                {finding.validation_status}
                                            </span>
                                        )}
                                    </div>
                                    <p className="text-sm text-zinc-500 font-mono flex items-center gap-1.5">
                                        <FileText className="w-3.5 h-3.5" />
                                        {finding.source === 'git_history' ? 'Git History' : finding.file?.replace('/Users/obafemi/bridge/', '')}
                                    </p>
                                </div>
                                <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                                    <button className="text-zinc-400 hover:text-white flex items-center gap-1 text-sm bg-zinc-800 px-3 py-1.5 rounded-lg transition-colors border border-zinc-700">
                                        Fix Leaked Key <ExternalLink className="w-3.5 h-3.5" />
                                    </button>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-red-500/5 border border-red-500/10 rounded-xl p-6 space-y-4">
                    <h3 className="text-red-500 font-semibold flex items-center gap-2">
                        <ShieldAlert className="w-4 h-4" />
                        Immediate Remediation
                    </h3>
                    <ul className="space-y-3 text-sm text-zinc-400">
                        <li className="flex flex-col gap-2">
                            <div className="flex gap-2">
                                <span className="text-red-500 font-bold">1.</span>
                                <span>Revoke the leaked key immediately.</span>
                            </div>
                        </li>
                        <li className="flex flex-col gap-2">
                            <div className="flex gap-2">
                                <span className="text-red-500 font-bold">2.</span>
                                <span>Rotation: Generate a new key and update environment variables.</span>
                            </div>
                        </li>
                        <li className="flex flex-col gap-2">
                            <div className="flex gap-2">
                                <span className="text-red-500 font-bold">3.</span>
                                <span>Git History: Purge secrets from history:</span>
                            </div>
                            <code className="bg-black/40 p-2 rounded border border-red-500/20 text-red-400 text-xs font-mono">
                                git filter-repo --invert-paths --path [FILENAME]
                            </code>
                        </li>
                    </ul>
                </div>
                <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-6 space-y-4">
                    <h3 className="text-white font-semibold flex items-center gap-2">
                        Proactive Prevention
                    </h3>
                    <p className="text-sm text-zinc-400 leading-relaxed">
                        Continuous monitoring is <span className="text-green-500 font-medium whitespace-nowrap">Active</span>. Any file saved in the <code>apps/</code> directory is automatically scanned.
                    </p>
                    <button className="w-full bg-zinc-800 text-white px-4 py-2 rounded-lg font-medium hover:bg-zinc-700 transition-all text-sm border border-zinc-700">
                        View Monitoring Logs
                    </button>
                </div>
            </div>
        </div>
    );
}
