import asyncio
from fastmcp import Client, FastMCP
from mcp.server.fastmcp import Image
from mcp.types import ImageContent
from rich import print
import base64

client = Client("http://localhost:9090/mcp")

client2 = Client("http://localhost:8931/mcp")
async def main():
    async with client:
        # Basic server interaction
        await client.ping()
        tools = await client.list_tools()

        result = await client.call_tool("linkedin_send_message_to", {"user_name": "Roshan Yadav", "message": "Hello, how are you?"})
        print(result)

    async with client2:
        await client2.ping()
        tools = await client2.list_tools()
        
        result = await client2.call_tool("browser_navigate", {"url": "https://www.linkedin.com/in/roshan-yadav-b545551a0/"})
        print(result)

asyncio.run(main())