import asyncio
from fastmcp import Client, FastMCP
from mcp.server.fastmcp import Image
from mcp.types import ImageContent
from rich import print
import base64

client = Client("http://localhost:9090/mcp")

client2 = Client("http://localhost:8931/mcp")
async def main():
    async with client2:
        async with client:

            result = await client2.call_tool("browser_navigate", {"url": "https://www.linkedin.com/mynetwork/grow/"})
            print(result)

            await client2.call_tool("browser_wait_for", {"time": 10000})

            result = await client.call_tool("linkedin_send_message_to", {"user_name": "Roshan Yadav", "message": "Hello, how are you?"})
            print(result)

            result = await client2.call_tool("browser_close", {})
            print(result)

            result = await client.call_tool("linkedin_close_page", {})
            print(result)

asyncio.run(main())