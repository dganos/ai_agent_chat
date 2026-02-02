"""Browser Manager using Playwright for web automation.

This module provides a singleton browser manager for Shufersal automation.
"""

import asyncio
from typing import Optional, Dict, Any, List
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright


class BrowserManager:
    """Singleton browser manager for Playwright automation."""

    _instance: Optional["BrowserManager"] = None
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._initialized = True

    async def initialize(self, headless: bool = True) -> None:
        """Initialize the browser if not already initialized."""
        async with self._lock:
            if self._browser is None:
                self._playwright = await async_playwright().start()
                self._browser = await self._playwright.chromium.launch(
                    headless=headless,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                    ]
                )
                self._context = await self._browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    locale="he-IL",
                    timezone_id="Asia/Jerusalem",
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                self._page = await self._context.new_page()

    async def get_page(self) -> Page:
        """Get the current page, initializing if needed."""
        if self._page is None:
            await self.initialize()
        return self._page

    async def navigate(self, url: str, wait_for: str = "networkidle") -> Dict[str, Any]:
        """Navigate to a URL."""
        page = await self.get_page()
        try:
            await page.goto(url, wait_until=wait_for, timeout=30000)
            return {
                "success": True,
                "url": page.url,
                "title": await page.title()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def click(self, selector: str, timeout: int = 10000) -> Dict[str, Any]:
        """Click an element."""
        page = await self.get_page()
        try:
            await page.click(selector, timeout=timeout)
            await page.wait_for_load_state("networkidle", timeout=10000)
            return {"success": True, "selector": selector}
        except Exception as e:
            return {"success": False, "error": str(e), "selector": selector}

    async def fill(self, selector: str, text: str, timeout: int = 10000) -> Dict[str, Any]:
        """Fill text into an input field."""
        page = await self.get_page()
        try:
            await page.fill(selector, text, timeout=timeout)
            return {"success": True, "selector": selector}
        except Exception as e:
            return {"success": False, "error": str(e), "selector": selector}

    async def type_text(self, selector: str, text: str, delay: int = 50) -> Dict[str, Any]:
        """Type text into an input field with delay (more human-like)."""
        page = await self.get_page()
        try:
            await page.type(selector, text, delay=delay)
            return {"success": True, "selector": selector}
        except Exception as e:
            return {"success": False, "error": str(e), "selector": selector}

    async def press_key(self, key: str) -> Dict[str, Any]:
        """Press a keyboard key."""
        page = await self.get_page()
        try:
            await page.keyboard.press(key)
            return {"success": True, "key": key}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def wait_for_selector(self, selector: str, timeout: int = 10000, state: str = "visible") -> Dict[str, Any]:
        """Wait for a selector to appear."""
        page = await self.get_page()
        try:
            await page.wait_for_selector(selector, timeout=timeout, state=state)
            return {"success": True, "selector": selector}
        except Exception as e:
            return {"success": False, "error": str(e), "selector": selector}

    async def get_text(self, selector: str) -> Dict[str, Any]:
        """Get text content from an element."""
        page = await self.get_page()
        try:
            element = await page.query_selector(selector)
            if element:
                text = await element.text_content()
                return {"success": True, "text": text.strip() if text else ""}
            return {"success": False, "error": "Element not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_all_texts(self, selector: str) -> Dict[str, Any]:
        """Get text content from all matching elements."""
        page = await self.get_page()
        try:
            elements = await page.query_selector_all(selector)
            texts = []
            for el in elements:
                text = await el.text_content()
                if text:
                    texts.append(text.strip())
            return {"success": True, "texts": texts, "count": len(texts)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_attribute(self, selector: str, attribute: str) -> Dict[str, Any]:
        """Get an attribute from an element."""
        page = await self.get_page()
        try:
            element = await page.query_selector(selector)
            if element:
                value = await element.get_attribute(attribute)
                return {"success": True, "value": value}
            return {"success": False, "error": "Element not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def screenshot(self, path: Optional[str] = None, full_page: bool = False) -> Dict[str, Any]:
        """Take a screenshot."""
        page = await self.get_page()
        try:
            screenshot_bytes = await page.screenshot(path=path, full_page=full_page)
            return {
                "success": True,
                "path": path,
                "size": len(screenshot_bytes) if screenshot_bytes else 0
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def evaluate(self, script: str) -> Dict[str, Any]:
        """Evaluate JavaScript in the page."""
        page = await self.get_page()
        try:
            result = await page.evaluate(script)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def scroll_to_bottom(self) -> Dict[str, Any]:
        """Scroll to the bottom of the page."""
        page = await self.get_page()
        try:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(0.5)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def scroll_into_view(self, selector: str) -> Dict[str, Any]:
        """Scroll an element into view."""
        page = await self.get_page()
        try:
            element = await page.query_selector(selector)
            if element:
                await element.scroll_into_view_if_needed()
                return {"success": True, "selector": selector}
            return {"success": False, "error": "Element not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def close(self) -> None:
        """Close the browser."""
        async with self._lock:
            if self._browser:
                await self._browser.close()
                self._browser = None
            if self._playwright:
                await self._playwright.stop()
                self._playwright = None
            self._context = None
            self._page = None


# Global browser manager instance
browser_manager = BrowserManager()
