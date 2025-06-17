import argparse
import logging
import os
import requests
import uvicorn
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from mcp.server import Server
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

mcp = FastMCP("demo-amap-sse")
BASE_URL = "https://restapi.amap.com/v5/place"
API_KEY = os.environ.get("GAODE_API_WEB")


def http_get(uri, params=None):
    url = f"{BASE_URL}/{uri}"
    try:
        logger.info(f"http_get url: {url}")
        resp = requests.get(url, params=params)
        logger.info(f"http_get resp: {resp}")
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}
    except Exception as e:
        return {"success": False, "message": str(e)}


@mcp.tool(description="根据搜索关键词，获取地点（POI）的经纬度坐标")
def get_location_coordination(keywords: str) -> str:
    logger.info(f"get_location_coordination 入参: {keywords}")
    params = {
        "key": API_KEY,
        "keywords": keywords,
    }

    result = http_get("text", params)
    logger.info(f"get_location_coordination 响应: {result}")
    if result["success"] and result["data"].get("pois"):
        poi = result["data"].get("pois")[0]
        return f"POI: {keywords}, 坐标: {poi['location']}"
    return "未找到POI坐标"


@mcp.tool(description="根据指定坐标搜索附近的地点（POI)")
def search_nearby_pois(keywords: str, location: str) -> str:
    """根据指定坐标搜索附近的地点（POI)"""
    logger.info(f"search_nearby_pois 入参: {keywords}, {location}")
    params = {
        "key": API_KEY,
        "keywords": keywords,
        "location": location
    }
    result = http_get("around", params)
    logger.info(f"search_nearby_pois 响应: {result}")
    if result["success"] and result["data"].get("pois"):
        results = []
        for poi in result["data"]["pois"][:3]:
            results.append(f"名称: {poi['name']}, 地址: {poi['address']}, 坐标: {poi['location']}")
        return "\n".join(results)
    return "未找到符合条件的POI"


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """创建SSE的服务"""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request):
        async with sse.connect_sse(request.scope, request.receive, request._send) as (read_stream, write_stream):
            await mcp_server.run(read_stream, write_stream, mcp_server.create_initialization_options(),)

    async def handle_messages(request: Request):
        await sse.handle_post_message(request.scope, request.receive, request._send)

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Route("/messages/", endpoint=handle_messages, methods=["POST"]),
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
    # mcp.run(transport='sse')
