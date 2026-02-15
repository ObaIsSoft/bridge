import asyncio
import os
from app.services.webmcp import WebMCPService

# Create a dummy HTML file that mocks WebMCP
MOCK_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>WebMCP Mock</title>
    <script>
        window.modelContext = {
            getTools: async () => [
                {
                    name: "mock_search",
                    type: "imperative",
                    description: "Search for mock items",
                    parameters: {
                        type: "object",
                        properties: {
                            query: { type: "string" }
                        }
                    }
                }
            ],
            executeTool: async (name, params) => {
                console.log("Executing", name, params);
                if (name === "mock_search") {
                    return [{ id: 1, name: "Mock Result: " + params.query }];
                }
                throw new Error("Unknown tool");
            }
        };
    </script>
</head>
<body>
    <h1>WebMCP Mock Page</h1>
</body>
</html>
"""

async def test_manual():
    # Write mock file
    with open("mock_webmcp.html", "w") as f:
        f.write(MOCK_HTML)
    
    file_url = f"file://{os.path.abspath('mock_webmcp.html')}"
    print(f"Testing against {file_url}")
    
    async with WebMCPService(headless=True) as service:
        print("Discovering tools...")
        tools = await service.discover_tools(file_url)
        print(f"Found tools: {tools}")
        
        if tools and tools[0]['name'] == 'mock_search':
            print("SUCCESS: Discovery works")
        else:
            print("FAILURE: Discovery failed")
            
        print("Executing tool...")
        result = await service.execute_tool(file_url, "mock_search", {"query": "test_query"})
        print(f"Execution result: {result}")
        
        if result['status'] == 'success' and result['result'][0]['id'] == 1:
            print("SUCCESS: Execution works")
        else:
            print("FAILURE: Execution failed")

    # Cleanup
    os.remove("mock_webmcp.html")

if __name__ == "__main__":
    asyncio.run(test_manual())
