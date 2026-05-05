import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        
        try:
            # Connect to the existing Chrome instance
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            
            # CDP connections usually have one default context
            context = browser.contexts[0]
            
            page = await context.new_page()
            
            # Execute your actions
            await page.goto("https://www.linkedin.com", wait_until="domcontentloaded")
            title = await page.title()
            print(f"Successfully connected to: {title}")
            
            # Perform a small task
            await page.screenshot(path="screenshot.png")
            print("Screenshot saved.")
            await asyncio.sleep(1000000)
            # IMPORTANT: Use disconnect() instead of close()
            # close() will kill the entire chrome process you started in the terminal.
            await browser.disconnect()
            print("Disconnected from browser.")

        except Exception as e:
            print(f"Error connecting: {e}")

if __name__ == "__main__":
    asyncio.run(main())