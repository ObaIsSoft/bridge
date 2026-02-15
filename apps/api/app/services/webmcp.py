import logging
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

logger = logging.getLogger(__name__)

class WebMCPService:
    """
    Service for discovering and executing WebMCP tools on a webpage.
    Uses Playwright to control a browser instance (ideally Chrome Canary)
    with WebMCP flags enabled.
    """
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
    
    async def __aenter__(self):
        """Launch browser with WebMCP flags."""
        self.playwright = await async_playwright().start()
        
        # Try to launch Chrome (Canary if available path provided, else default Chromium)
        # Note: In production, one would point `executable_path` to Chrome Canary
        try:
            self.browser = await self.playwright.chromium.launch(
                channel="chrome", # Attempts to use installed Chrome
                headless=self.headless,
                args=[
                    "--enable-features=WebMCP",
                    "--enable-experimental-web-platform-features",
                    "--no-sandbox", # Often needed in containerized envs
                    "--disable-setuid-sandbox"
                ]
            )
        except Exception as e:
            logger.warning(f"Failed to launch 'chrome' channel, falling back to bundled chromium: {e}")
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    "--enable-features=WebMCP",
                    "--enable-experimental-web-platform-features"
                ]
            )
            
        self.context = await self.browser.new_context()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup resources."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def discover_tools(self, url: str) -> List[Dict[str, Any]]:
        """
        Navigate to a URL and discover WebMCP tools exposed on `window.modelContext`.
        
        Returns a list of tool definitions.
        """
        page = await self.context.new_page()
        
        # Debug Console
        page.on("console", lambda msg: logger.info(f"BROWSER CONSOLE: {msg.text}"))
        page.on("pageerror", lambda exc: logger.error(f"BROWSER ERROR: {exc}"))

        try:
            # Inject Polyfill/Shim ALWAYS for debugging
            await page.add_init_script("""
                console.log("Polyfill script starting...");
                try {
                    const params = new URLSearchParams(window.location.search);
                    console.log("Injecting WebMCP Shim...");
                    
                    const registry = [];
                    
                    const mockContext = {
                        registerTool: (tool) => {
                            console.log("Shim: Tool registered:", tool.name);
                            registry.push(tool);
                        },
                        getTools: async () => registry,
                        executeTool: async (name, params) => {
                             console.log("Shim: Executing", name, params);
                             return { status: "success", result: "Executed via shim" };
                        }
                    };
                    
                    window.modelContext = mockContext;
                    navigator.modelContext = mockContext;
                    console.log("Shim injected successfully. window.modelContext is now:", typeof window.modelContext);
                } catch (e) {
                    console.error("Shim injection failed:", e);
                }
            """)

            # Navigate to the page
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            except Exception as nav_error:
                logger.error(f"Navigation failed: {nav_error}")
                return []

            # Check for WebMCP presence
            has_webmcp = await page.evaluate("() => typeof window.modelContext !== 'undefined'")
            logger.info(f"WebMCP Check Result: {has_webmcp}")
            
            if not has_webmcp:
                # Try to see why
                debug_info = await page.evaluate("() => ({ windowKeys: Object.keys(window).filter(k => k.includes('model')), navigatorKeys: Object.keys(navigator).filter(k => k.includes('model')) })")
                logger.info(f"Debug Info: {debug_info}")
                logger.info(f"No WebMCP global found on {url}")
                return []
            
            # 2. Get tool definitions
            tools = await page.evaluate("""
                async () => {
                    try {
                        // Allow small delay for page scripts to register tools
                        await new Promise(r => setTimeout(r, 1000));
                        
                        if (typeof window.modelContext.getTools === 'function') {
                            const tools = await window.modelContext.getTools();
                            return tools.map(t => ({
                                tool_name: t.name,
                                tool_type: t.type || 'unknown',
                                description: t.description || '',
                                parameters_schema: t.parameters || {} 
                            }));
                        }
                        return [];
                    } catch (e) {
                        console.error("WebMCP getTools error:", e);
                        return [];
                    }
                }
            """)
            
            logger.info(f"Discovered {len(tools)} tools on {url}")
            return tools
            
        except Exception as e:
            logger.error(f"Error discovering tools on {url}: {e}")
            return []
        finally:
            await page.close()

    async def execute_tool(self, url: str, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a WebMCP tool on a page.
        """
        page = await self.context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            result = await page.evaluate("""
                async ({name, params}) => {
                    if (!window.modelContext) throw new Error("WebMCP not available");
                    
                    // Call executeTool
                    // Note: The spec might evolve, assuming executeTool(name, params)
                    return await window.modelContext.executeTool(name, params);
                }
            """, {"name": tool_name, "params": parameters})
            
            return {"status": "success", "result": result}
            
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return {"status": "error", "error": str(e)}
        finally:
            await page.close()
