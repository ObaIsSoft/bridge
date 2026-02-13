"use client";

import { Terminal, Copy, Download, ExternalLink, Cpu } from "lucide-react";
import { useState } from "react";

export default function MCPPage() {
    const [copied, setCopied] = useState(false);

    const configSnippet = `{
  "mcpServers": {
    "api-bridge": {
      "command": "python3",
      "args": [
        "${process.env.NEXT_PUBLIC_API_BRIDGE_PATH || "/Users/obafemi/bridge"}/apps/mcp-server/main.py"
      ],
      "env": {
        "API_URL": "http://localhost:8000"
      }
    }
  }
}`;

    const copyToClipboard = () => {
        navigator.clipboard.writeText(configSnippet);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-white">
                        Model Context Protocol
                    </h1>
                    <p className="text-zinc-400 mt-1">
                        Integrate your API Bridges as native tools in AI clients like Claude
                        Desktop.
                    </p>
                </div>
                <div className="bg-amber-500/10 border border-amber-500/20 px-3 py-1 rounded-full flex items-center gap-2">
                    <Cpu className="w-4 h-4 text-amber-500" />
                    <span className="text-xs font-medium text-amber-500">MCP Ready</span>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-6 space-y-4">
                    <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                        <Terminal className="w-5 h-5 text-amber-500" />
                        Quick Setup
                    </h2>
                    <div className="space-y-3">
                        <p className="text-sm text-zinc-400 leading-relaxed">
                            1. Ensure you have the <span className="text-white font-medium">MCP SDK</span> installed in your Python environment.
                        </p>
                        <p className="text-sm text-zinc-400 leading-relaxed">
                            2. Open your <span className="text-white font-medium">Claude Desktop Config</span> file (Settings &gt; Developer &gt; Edit Config).
                        </p>
                        <p className="text-sm text-zinc-400 leading-relaxed">
                            3. Paste the configuration snippet on the right into your <span className="code text-amber-400 bg-amber-400/10 px-1 rounded">mcpServers</span> list.
                        </p>
                        <p className="text-sm text-zinc-400 leading-relaxed">
                            4. Restart Claude Desktop.
                        </p>
                    </div>
                    <div className="pt-4">
                        <a
                            href="https://modelcontextprotocol.io"
                            target="_blank"
                            className="text-xs text-amber-500 hover:text-amber-400 flex items-center gap-1 transition-colors"
                        >
                            Learn more about MCP <ExternalLink className="w-3 h-3" />
                        </a>
                    </div>
                </div>

                <div className="bg-black border border-zinc-800 rounded-xl overflow-hidden flex flex-col">
                    <div className="bg-zinc-900 border-b border-zinc-800 px-4 py-2 flex items-center justify-between">
                        <span className="text-xs font-mono text-zinc-500 italic">claude_desktop_config.json</span>
                        <button
                            onClick={copyToClipboard}
                            className="text-xs text-zinc-400 hover:text-white flex items-center gap-1.5 transition-colors"
                        >
                            {copied ? "Copied!" : "Copy code"}
                            <Copy className="w-3.5 h-3.5" />
                        </button>
                    </div>
                    <pre className="p-4 overflow-x-auto">
                        <code className="text-xs font-mono text-amber-200 leading-relaxed">
                            {configSnippet}
                        </code>
                    </pre>
                </div>
            </div>

            <div className="bg-zinc-900/30 border border-zinc-800/50 rounded-xl p-8 text-center space-y-4">
                <div className="bg-amber-500/10 w-16 h-16 rounded-full flex items-center justify-center mx-auto border border-amber-500/20">
                    <Download className="w-8 h-8 text-amber-500" />
                </div>
                <div className="max-w-md mx-auto space-y-2">
                    <h3 className="text-lg font-medium text-white">Missing Dependencies?</h3>
                    <p className="text-sm text-zinc-400">
                        If this is your first time using MCP, you'll need to install the SDK and dependencies in your local environment.
                    </p>
                </div>
                <button className="bg-white text-black px-6 py-2 rounded-lg font-medium hover:bg-zinc-200 transition-colors inline-flex items-center gap-2">
                    Install MCP SDK
                    <ExternalLink className="w-4 h-4" />
                </button>
            </div>
        </div>
    );
}
