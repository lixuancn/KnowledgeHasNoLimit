import sys
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="uv",
    args=[
        "run",
        "--with",
        "mcp[cli]",
        "--with-editable",
        "~/www/lanecn/KnowledgeHasNoLimit/xingyunyang01_geek02/achievement",
        "mcp",
        "run",
        "~/www/lanecn/KnowledgeHasNoLimit/xingyunyang01_geek02/achievement/server.py"
    ],
    env=None
)


async def run_stdio():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("tools: ", tools)
            score = await session.call_tool(name="get_score_by_name", arguments={"name": "张三"})
            print("score: ", score)


async def connect_to_sse_server(server_url: str):
    """连接到MCP服务"""
    async with sse_client(url=server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("Init SSE Client...")
            print("Listen tools...")
            response = await session.list_tools()
            tools = response.tools
            print("Connected to server with tools: ", [tool.name + ": " + tool.description for tool in tools])
            score = await session.call_tool(name="get_score_by_name", arguments={"name": "张三"})
            print("score: ", score)


async def main():
    if len(sys.argv) < 2:
        print("Usage: uv run client.py <URL of SSE MCP server (i.e. http://localhost:8080/sse)>")
        sys.exit(1)
    await connect_to_sse_server(server_url=sys.argv[1])


if __name__ == "__main__":
    # asyncio.run(run_stdio())
    asyncio.run(main())
