import asyncio
from fastmcp import Client, FastMCP
from mcp.server.fastmcp import Image
from mcp.types import ImageContent
from rich import print
import base64

client = Client("http://127.0.0.1:8878/mcp")


async def main():
    async with client:
        # Basic server interaction
        await client.ping()

        # List available operations
        tools = await client.list_tools()
        resources = await client.list_resources()
        prompts = await client.list_prompts()

        # Execute operations
        result = await client.call_tool("navigate_to_url", {"url": "https://www.linkedin.com/in/brenda-b-86705122/recent-activity/all/"})
        print(result)
        await asyncio.sleep(2)
        result = await client.call_tool("page_evaluate", {"script": "document.title"})
        print(result)
        await asyncio.sleep(2)
        result: Image = await client.call_tool("get_page_screenshot", {})
        # save the image to a file
        image:ImageContent = result.content[0]
        image_data = base64.b64decode(image.data)
        
        with open("screenshot.png", "wb") as f:
            f.write(image_data)
        print("Screenshot saved successfully!")

asyncio.run(main())