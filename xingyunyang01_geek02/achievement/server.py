from mcp.server.fastmcp import FastMCP
from mcp.server import Server

from starlette.routing import Mount, Route
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
import uvicorn
import argparse

# Create an MCP server
mcp = FastMCP("achievement")


# Add an get score tool
@mcp.tool()
def get_score_by_name(name: str) -> str:
    """根据员工的姓名获取该员工的绩效得分"""
    if name == "张三":
        return "name: 张三 绩效评分: 85.9"
    elif name == "李四":
        return "name: 李四 绩效评分: 92.7"
    else:
        return "未搜到该员工的绩效"


@mcp.resource("file://info.md")
def get_file() -> str:
    """读取info.md的内容，从而获取员工的信息，例如性别等"""
    with open("~/www/lanecn/KnowledgeHasNoLimit/xingyunyang01_geek02/achievement/info.md", "r",
              encoding="utf-8") as f:
        return f.read()


@mcp.prompt()
def prompt(name: str) -> str:
    """创建一个 prompt，用于对员工进行绩效评价"""
    return f"""绩效满分是100分，请获取{name}的绩效评分，并给出评价"""


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """创建SSE的服务"""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


if __name__ == "__main__":
    mcp_server = mcp._mcp_server
    parser = argparse.ArgumentParser(description="Run MCP SSE-based server")
    parser.add_argument('--host', default="0.0.0.0", help='Host to bind to')
    parser.add_argument('--port', type=int, default=18080, help='Port to listen on')
    args = parser.parse_args()
    starlette_app = create_starlette_app(mcp_server, debug=True)
    uvicorn.run(starlette_app, host=args.host, port=args.port)
