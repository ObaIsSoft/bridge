"use client";

import React, { useState } from 'react';
import {
    Globe,
    Code,
    Layout,
    ChevronRight,
    Sparkles,
    Save,
    Loader2
} from 'lucide-react';
import { bridgesApi } from '@/lib/api';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';

export default function NewBridgePage() {
    const router = useRouter();
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        target_url: '',
        extraction_schema: '{\n  "title": "string",\n  "url": "url"\n}',
        selectors: '{}'
    });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            const schema = JSON.parse(formData.extraction_schema);
            const selectors = formData.selectors ? JSON.parse(formData.selectors) : {};
            await bridgesApi.create({
                name: formData.name,
                target_url: formData.target_url,
                domain: new URL(formData.target_url).hostname,
                extraction_schema: schema,
                selectors: selectors
            });
            toast.success("Bridge created successfully!");
            router.push('/bridges');
        } catch (err: any) {
            toast.error(err.message || "Failed to create bridge");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto space-y-8 animate-in slide-in-from-right-4 duration-500">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">Create New Bridge</h1>
                <p className="text-muted-foreground">Turn any website into a structured API in seconds.</p>
            </div>

            <form onSubmit={handleSubmit} className="grid gap-8 md:grid-cols-[1fr_300px]">
                <div className="space-y-6">
                    <div className="rounded-xl border bg-card p-6 shadow-sm space-y-4">
                        <h3 className="text-lg font-semibold flex items-center gap-2">
                            <Globe className="h-5 w-5 text-primary" />
                            1. Target Details
                        </h3>
                        <div className="grid gap-4">
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Bridge Name</label>
                                <input
                                    type="text"
                                    required
                                    value={formData.name}
                                    onChange={e => setFormData({ ...formData, name: e.target.value })}
                                    placeholder="e.g., Hacker News Top Stories"
                                    className="w-full rounded-md border bg-background px-3 py-2 text-sm outline-none focus:ring-1 focus:ring-ring"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Target URL</label>
                                <input
                                    type="url"
                                    required
                                    value={formData.target_url}
                                    onChange={e => setFormData({ ...formData, target_url: e.target.value })}
                                    placeholder="https://news.ycombinator.com"
                                    className="w-full rounded-md border bg-background px-3 py-2 text-sm outline-none focus:ring-1 focus:ring-ring"
                                />
                            </div>
                        </div>
                    </div>

                    <div className="rounded-xl border bg-card p-6 shadow-sm space-y-4">
                        <h3 className="text-lg font-semibold flex items-center gap-2">
                            <Layout className="h-5 w-5 text-primary" />
                            2. Data Schema
                        </h3>
                        <p className="text-xs text-muted-foreground">Define what data you want to extract. Our AI will handle the mapping.</p>
                        <textarea
                            rows={6}
                            required
                            value={formData.extraction_schema}
                            onChange={e => setFormData({ ...formData, extraction_schema: e.target.value })}
                            placeholder={`{
  "title": "string",
  "link": "url"
}`}
                            className="w-full font-mono text-sm rounded-md border bg-background px-3 py-2 outline-none focus:ring-1 focus:ring-ring"
                        />
                    </div>

                    <div className="rounded-xl border bg-card p-6 shadow-sm space-y-4">
                        <h3 className="text-lg font-semibold flex items-center gap-2">
                            <Code className="h-5 w-5 text-primary" />
                            3. Selectors (Optional)
                        </h3>
                        <p className="text-xs text-muted-foreground">Map schema fields to CSS selectors for precision.</p>
                        <textarea
                            rows={4}
                            value={formData.selectors}
                            onChange={e => setFormData({ ...formData, selectors: e.target.value })}
                            placeholder={`{
  "title": ".post-title",
  "link": "a.storylink"
}`}
                            className="w-full font-mono text-sm rounded-md border bg-background px-3 py-2 outline-none focus:ring-1 focus:ring-ring"
                        />
                    </div>

                    <div className="flex items-center justify-end gap-4">
                        <button
                            type="button"
                            onClick={() => router.back()}
                            className="px-4 py-2 text-sm font-medium rounded-md hover:bg-accent transition-colors">
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={loading}
                            className="inline-flex items-center gap-2 rounded-md bg-primary px-6 py-2 text-sm font-medium text-primary-foreground shadow hover:bg-primary/90 transition-colors disabled:opacity-50">
                            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                            Save & Test Bridge
                        </button>
                    </div>
                </div>

                <div className="space-y-6">
                    <div className="rounded-xl border bg-primary/5 p-6 shadow-sm border-primary/20">
                        <h4 className="font-semibold flex items-center gap-2 text-primary">
                            <Sparkles className="h-4 w-4" />
                            AI Assistant
                        </h4>
                        <div className="mt-4 space-y-4 text-xs leading-relaxed text-muted-foreground">
                            <p>Just paste the URL and I'll try to guess the schema for you.</p>
                            <div className="p-3 bg-white rounded border border-dashed text-[10px] font-mono whitespace-pre overflow-hidden">
                                {`Analyzing URL...
Detected: List View
Suggested Fields: 
[title, url, timestamp]`}
                            </div>
                            <button
                                type="button"
                                className="w-full py-2 bg-primary text-primary-foreground rounded-md font-bold text-[10px] shadow-sm">
                                AUTO-FILL SCHEMA
                            </button>
                        </div>
                    </div>

                    <div className="p-4 rounded-xl bg-orange-50 border border-orange-200">
                        <h4 className="text-orange-900 font-semibold text-xs flex items-center gap-2">
                            <Code className="h-3 w-3" />
                            Developer Tip
                        </h4>
                        <p className="text-orange-800 text-[10px] mt-2 leading-relaxed">
                            Use specific page URLs rather than landing pages for higher extraction accuracy on paginated data.
                        </p>
                    </div>
                </div>
            </form>
        </div>
    );
}
