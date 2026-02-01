"""Shufersal Online grocery shopping automation tools.

This module provides tools for automating grocery shopping on Shufersal Online.
"""

import asyncio
import re
from typing import Dict, Any, List, Optional
from agno.tools import tool
from backend.browser import browser_manager


# Shufersal URLs
SHUFERSAL_BASE_URL = "https://www.shufersal.co.il"
SHUFERSAL_LOGIN_URL = f"{SHUFERSAL_BASE_URL}/online/he/login"
SHUFERSAL_HOME_URL = f"{SHUFERSAL_BASE_URL}/online/he"
SHUFERSAL_CART_URL = f"{SHUFERSAL_BASE_URL}/online/he/cart"
SHUFERSAL_CHECKOUT_URL = f"{SHUFERSAL_BASE_URL}/online/he/checkout"


def run_async(coro):
    """Run an async function synchronously."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


@tool()
def shufersal_initialize_browser(headless: bool = False) -> Dict[str, Any]:
    """
    Initialize the browser for Shufersal shopping.
    Call this first before any other Shufersal operations.

    Args:
        headless: Whether to run browser in headless mode (default: False for debugging)

    Returns:
        Status of browser initialization
    """
    async def _init():
        await browser_manager.initialize(headless=headless)
        result = await browser_manager.navigate(SHUFERSAL_HOME_URL)
        return {
            "type": "browser_status",
            "status": "initialized",
            "success": result["success"],
            "current_url": result.get("url", ""),
            "page_title": result.get("title", ""),
            "message": "Browser initialized and navigated to Shufersal homepage" if result["success"] else f"Failed to initialize: {result.get('error', 'Unknown error')}"
        }

    return run_async(_init())


@tool()
def shufersal_login(email: str, password: str) -> Dict[str, Any]:
    """
    Log in to Shufersal Online with the provided credentials.

    Args:
        email: The user's email address for Shufersal account
        password: The user's password

    Returns:
        Login status and user information
    """
    async def _login():
        # Navigate to login page
        await browser_manager.navigate(SHUFERSAL_LOGIN_URL)
        await asyncio.sleep(2)

        page = await browser_manager.get_page()

        # Try to find and fill login form
        try:
            # Wait for login form
            await page.wait_for_selector('input[type="email"], input[name="email"], input[placeholder*="מייל"], input[id*="email"]', timeout=10000)

            # Fill email
            email_selectors = [
                'input[type="email"]',
                'input[name="email"]',
                'input[placeholder*="מייל"]',
                'input[id*="email"]',
                '#username',
                'input[name="username"]'
            ]

            email_filled = False
            for selector in email_selectors:
                try:
                    await page.fill(selector, email, timeout=2000)
                    email_filled = True
                    break
                except:
                    continue

            if not email_filled:
                return {
                    "type": "login_status",
                    "success": False,
                    "error": "Could not find email input field"
                }

            # Fill password
            password_selectors = [
                'input[type="password"]',
                'input[name="password"]',
                '#password'
            ]

            password_filled = False
            for selector in password_selectors:
                try:
                    await page.fill(selector, password, timeout=2000)
                    password_filled = True
                    break
                except:
                    continue

            if not password_filled:
                return {
                    "type": "login_status",
                    "success": False,
                    "error": "Could not find password input field"
                }

            # Click login button
            login_button_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("כניסה")',
                'button:has-text("התחבר")',
                '.login-button',
                '#login-button'
            ]

            login_clicked = False
            for selector in login_button_selectors:
                try:
                    await page.click(selector, timeout=2000)
                    login_clicked = True
                    break
                except:
                    continue

            if not login_clicked:
                # Try pressing Enter
                await page.keyboard.press("Enter")

            # Wait for navigation
            await asyncio.sleep(3)
            await page.wait_for_load_state("networkidle", timeout=15000)

            # Check if login was successful by looking for user indicators
            current_url = page.url

            # Check for error messages
            error_selectors = [
                '.error-message',
                '.login-error',
                '[class*="error"]',
                '.alert-danger'
            ]

            for selector in error_selectors:
                try:
                    error_el = await page.query_selector(selector)
                    if error_el:
                        error_text = await error_el.text_content()
                        if error_text and error_text.strip():
                            return {
                                "type": "login_status",
                                "success": False,
                                "error": f"Login failed: {error_text.strip()}"
                            }
                except:
                    continue

            # Check if we're on a logged-in page
            if "login" not in current_url.lower():
                return {
                    "type": "login_status",
                    "success": True,
                    "message": "Successfully logged in to Shufersal",
                    "current_url": current_url
                }
            else:
                return {
                    "type": "login_status",
                    "success": False,
                    "error": "Login may have failed - still on login page",
                    "current_url": current_url
                }

        except Exception as e:
            return {
                "type": "login_status",
                "success": False,
                "error": f"Login error: {str(e)}"
            }

    return run_async(_login())


@tool()
def shufersal_search_products(query: str, max_results: int = 10) -> Dict[str, Any]:
    """
    Search for products on Shufersal Online.

    Args:
        query: The search term (e.g., "חלב", "לחם", "eggs")
        max_results: Maximum number of products to return (default: 10)

    Returns:
        List of products matching the search query with prices and details
    """
    async def _search():
        page = await browser_manager.get_page()

        # Navigate to search or use search bar
        search_url = f"{SHUFERSAL_BASE_URL}/online/he/search?q={query}"
        await browser_manager.navigate(search_url)
        await asyncio.sleep(2)

        try:
            # Wait for products to load
            await page.wait_for_selector('[class*="product"], [data-product], .miglog-prod, .product-item', timeout=15000)
            await asyncio.sleep(1)

            # Extract products
            products = await page.evaluate('''(maxResults) => {
                const products = [];
                const productCards = document.querySelectorAll('[class*="product"], [data-product], .miglog-prod, .product-item, [class*="ProductCard"], [class*="productCard"]');

                for (let i = 0; i < Math.min(productCards.length, maxResults); i++) {
                    const card = productCards[i];

                    // Try to extract product info
                    const nameEl = card.querySelector('[class*="name"], [class*="title"], h2, h3, .product-name, .product-title');
                    const priceEl = card.querySelector('[class*="price"], .price, [class*="Price"]');
                    const imageEl = card.querySelector('img');
                    const unitEl = card.querySelector('[class*="unit"], [class*="weight"], .unit-price');

                    // Get product ID from data attributes or href
                    let productId = card.dataset.productId || card.dataset.id || '';
                    if (!productId) {
                        const link = card.querySelector('a[href*="product"]');
                        if (link) {
                            const match = link.href.match(/product[/-]?(\\d+)/i);
                            if (match) productId = match[1];
                        }
                    }

                    const name = nameEl ? nameEl.textContent.trim() : '';
                    const priceText = priceEl ? priceEl.textContent.trim() : '';
                    const price = priceText.replace(/[^\\d.]/g, '');
                    const image = imageEl ? imageEl.src : '';
                    const unit = unitEl ? unitEl.textContent.trim() : '';

                    if (name) {
                        products.push({
                            id: productId || `product-${i}`,
                            name: name,
                            price: price ? parseFloat(price) : null,
                            priceDisplay: priceText,
                            image: image,
                            unit: unit,
                            index: i
                        });
                    }
                }

                return products;
            }''', max_results)

            return {
                "type": "product_list",
                "success": True,
                "query": query,
                "products": products,
                "count": len(products),
                "message": f"Found {len(products)} products for '{query}'"
            }

        except Exception as e:
            return {
                "type": "product_list",
                "success": False,
                "query": query,
                "error": f"Search error: {str(e)}",
                "products": []
            }

    return run_async(_search())


@tool()
def shufersal_add_to_cart(product_name: str, quantity: int = 1) -> Dict[str, Any]:
    """
    Add a product to the shopping cart.
    First searches for the product, then adds it to cart.

    Args:
        product_name: Name or search term for the product
        quantity: Number of units to add (default: 1)

    Returns:
        Status of adding product to cart
    """
    async def _add():
        page = await browser_manager.get_page()

        # First search for the product
        search_url = f"{SHUFERSAL_BASE_URL}/online/he/search?q={product_name}"
        await browser_manager.navigate(search_url)
        await asyncio.sleep(2)

        try:
            # Wait for products to load
            await page.wait_for_selector('[class*="product"], [data-product], .miglog-prod, .product-item', timeout=15000)
            await asyncio.sleep(1)

            # Find and click the first add to cart button
            add_button_selectors = [
                'button[class*="add"], button[class*="Add"]',
                '[class*="addToCart"], [class*="add-to-cart"]',
                'button:has-text("הוסף")',
                'button:has-text("לסל")',
                '[data-action="add"]',
                '.add-to-cart-button',
                'button[aria-label*="הוסף"]'
            ]

            added = False
            for selector in add_button_selectors:
                try:
                    buttons = await page.query_selector_all(selector)
                    if buttons and len(buttons) > 0:
                        # Click the first add button
                        await buttons[0].click()
                        added = True
                        break
                except:
                    continue

            if not added:
                # Try clicking on the product first then finding add button
                try:
                    product_card = await page.query_selector('[class*="product"], .product-item')
                    if product_card:
                        await product_card.click()
                        await asyncio.sleep(1)

                        for selector in add_button_selectors:
                            try:
                                await page.click(selector, timeout=2000)
                                added = True
                                break
                            except:
                                continue
                except:
                    pass

            await asyncio.sleep(1)

            # Handle quantity if more than 1
            if added and quantity > 1:
                for _ in range(quantity - 1):
                    try:
                        # Try to find quantity increase button
                        plus_selectors = [
                            'button[class*="plus"], button[class*="increase"]',
                            'button:has-text("+")',
                            '[data-action="increase"]',
                            '.quantity-plus'
                        ]

                        for selector in plus_selectors:
                            try:
                                await page.click(selector, timeout=1000)
                                await asyncio.sleep(0.3)
                                break
                            except:
                                continue
                    except:
                        break

            if added:
                # Get the product name that was added
                product_info = await page.evaluate('''() => {
                    const nameEl = document.querySelector('[class*="product"] [class*="name"], .product-name, h1, h2');
                    return nameEl ? nameEl.textContent.trim() : '';
                }''')

                return {
                    "type": "cart_action",
                    "action": "add",
                    "success": True,
                    "product": product_name,
                    "product_found": product_info,
                    "quantity": quantity,
                    "message": f"Added {quantity}x '{product_name}' to cart"
                }
            else:
                return {
                    "type": "cart_action",
                    "action": "add",
                    "success": False,
                    "product": product_name,
                    "error": "Could not find add to cart button"
                }

        except Exception as e:
            return {
                "type": "cart_action",
                "action": "add",
                "success": False,
                "product": product_name,
                "error": f"Error adding to cart: {str(e)}"
            }

    return run_async(_add())


@tool()
def shufersal_view_cart() -> Dict[str, Any]:
    """
    View the current shopping cart contents.

    Returns:
        Cart contents including products, quantities, and total price
    """
    async def _view_cart():
        page = await browser_manager.get_page()

        await browser_manager.navigate(SHUFERSAL_CART_URL)
        await asyncio.sleep(2)

        try:
            # Wait for cart to load
            await page.wait_for_load_state("networkidle", timeout=15000)
            await asyncio.sleep(1)

            # Extract cart items
            cart_data = await page.evaluate('''() => {
                const items = [];
                const cartItems = document.querySelectorAll('[class*="cart-item"], [class*="cartItem"], .cart-product, [class*="CartItem"]');

                cartItems.forEach((item, index) => {
                    const nameEl = item.querySelector('[class*="name"], [class*="title"], .product-name');
                    const priceEl = item.querySelector('[class*="price"], .price, [class*="Price"]');
                    const quantityEl = item.querySelector('[class*="quantity"], input[type="number"], .qty');
                    const imageEl = item.querySelector('img');

                    const name = nameEl ? nameEl.textContent.trim() : '';
                    const priceText = priceEl ? priceEl.textContent.trim() : '';
                    const price = priceText.replace(/[^\\d.]/g, '');
                    const quantity = quantityEl ? (quantityEl.value || quantityEl.textContent.trim()) : '1';
                    const image = imageEl ? imageEl.src : '';

                    if (name) {
                        items.push({
                            index: index,
                            name: name,
                            price: price ? parseFloat(price) : null,
                            priceDisplay: priceText,
                            quantity: parseInt(quantity) || 1,
                            image: image
                        });
                    }
                });

                // Get total
                const totalEl = document.querySelector('[class*="total"], .cart-total, [class*="Total"]');
                const totalText = totalEl ? totalEl.textContent.trim() : '';
                const total = totalText.replace(/[^\\d.]/g, '');

                return {
                    items: items,
                    totalDisplay: totalText,
                    total: total ? parseFloat(total) : null
                };
            }''')

            return {
                "type": "cart_view",
                "success": True,
                "items": cart_data["items"],
                "item_count": len(cart_data["items"]),
                "total": cart_data["total"],
                "total_display": cart_data["totalDisplay"],
                "message": f"Cart has {len(cart_data['items'])} items"
            }

        except Exception as e:
            return {
                "type": "cart_view",
                "success": False,
                "error": f"Error viewing cart: {str(e)}",
                "items": []
            }

    return run_async(_view_cart())


@tool()
def shufersal_remove_from_cart(product_name: str) -> Dict[str, Any]:
    """
    Remove a product from the shopping cart.

    Args:
        product_name: Name of the product to remove (partial match)

    Returns:
        Status of removing product from cart
    """
    async def _remove():
        page = await browser_manager.get_page()

        # Make sure we're on the cart page
        if "cart" not in page.url.lower():
            await browser_manager.navigate(SHUFERSAL_CART_URL)
            await asyncio.sleep(2)

        try:
            # Find the cart item with matching name and remove it
            removed = await page.evaluate('''(productName) => {
                const cartItems = document.querySelectorAll('[class*="cart-item"], [class*="cartItem"], .cart-product');

                for (const item of cartItems) {
                    const nameEl = item.querySelector('[class*="name"], [class*="title"], .product-name');
                    const name = nameEl ? nameEl.textContent.trim().toLowerCase() : '';

                    if (name.includes(productName.toLowerCase())) {
                        // Find and click remove button
                        const removeBtn = item.querySelector(
                            'button[class*="remove"], button[class*="delete"], ' +
                            '[class*="remove"], [class*="delete"], ' +
                            'button:has-text("הסר"), button:has-text("מחק")'
                        );

                        if (removeBtn) {
                            removeBtn.click();
                            return { found: true, removed: true, name: name };
                        }
                        return { found: true, removed: false, name: name };
                    }
                }
                return { found: false, removed: false };
            }''', product_name)

            await asyncio.sleep(1)

            if removed["removed"]:
                return {
                    "type": "cart_action",
                    "action": "remove",
                    "success": True,
                    "product": product_name,
                    "message": f"Removed '{removed.get('name', product_name)}' from cart"
                }
            elif removed["found"]:
                return {
                    "type": "cart_action",
                    "action": "remove",
                    "success": False,
                    "product": product_name,
                    "error": "Found product but could not find remove button"
                }
            else:
                return {
                    "type": "cart_action",
                    "action": "remove",
                    "success": False,
                    "product": product_name,
                    "error": f"Product '{product_name}' not found in cart"
                }

        except Exception as e:
            return {
                "type": "cart_action",
                "action": "remove",
                "success": False,
                "product": product_name,
                "error": f"Error removing from cart: {str(e)}"
            }

    return run_async(_remove())


@tool()
def shufersal_update_quantity(product_name: str, quantity: int) -> Dict[str, Any]:
    """
    Update the quantity of a product in the cart.

    Args:
        product_name: Name of the product (partial match)
        quantity: New quantity to set

    Returns:
        Status of quantity update
    """
    async def _update():
        page = await browser_manager.get_page()

        if "cart" not in page.url.lower():
            await browser_manager.navigate(SHUFERSAL_CART_URL)
            await asyncio.sleep(2)

        try:
            updated = await page.evaluate('''(args) => {
                const { productName, quantity } = args;
                const cartItems = document.querySelectorAll('[class*="cart-item"], [class*="cartItem"], .cart-product');

                for (const item of cartItems) {
                    const nameEl = item.querySelector('[class*="name"], [class*="title"], .product-name');
                    const name = nameEl ? nameEl.textContent.trim().toLowerCase() : '';

                    if (name.includes(productName.toLowerCase())) {
                        // Find quantity input
                        const qtyInput = item.querySelector('input[type="number"], [class*="quantity"] input');
                        if (qtyInput) {
                            qtyInput.value = quantity;
                            qtyInput.dispatchEvent(new Event('change', { bubbles: true }));
                            return { found: true, updated: true, name: name };
                        }
                        return { found: true, updated: false, name: name };
                    }
                }
                return { found: false, updated: false };
            }''', {"productName": product_name, "quantity": quantity})

            await asyncio.sleep(1)

            if updated["updated"]:
                return {
                    "type": "cart_action",
                    "action": "update_quantity",
                    "success": True,
                    "product": product_name,
                    "quantity": quantity,
                    "message": f"Updated '{updated.get('name', product_name)}' quantity to {quantity}"
                }
            elif updated["found"]:
                return {
                    "type": "cart_action",
                    "action": "update_quantity",
                    "success": False,
                    "product": product_name,
                    "error": "Found product but could not update quantity"
                }
            else:
                return {
                    "type": "cart_action",
                    "action": "update_quantity",
                    "success": False,
                    "product": product_name,
                    "error": f"Product '{product_name}' not found in cart"
                }

        except Exception as e:
            return {
                "type": "cart_action",
                "action": "update_quantity",
                "success": False,
                "error": f"Error updating quantity: {str(e)}"
            }

    return run_async(_update())


@tool()
def shufersal_proceed_to_checkout() -> Dict[str, Any]:
    """
    Proceed to checkout page.
    IMPORTANT: This will show the checkout page but will NOT complete the purchase.
    The user must manually review and confirm the order.

    Returns:
        Checkout page information and order summary
    """
    async def _checkout():
        page = await browser_manager.get_page()

        # First get cart summary
        if "cart" not in page.url.lower():
            await browser_manager.navigate(SHUFERSAL_CART_URL)
            await asyncio.sleep(2)

        try:
            # Click checkout button
            checkout_selectors = [
                'button:has-text("לקופה")',
                'button:has-text("המשך לתשלום")',
                'a[href*="checkout"]',
                '[class*="checkout-button"]',
                'button[class*="checkout"]'
            ]

            clicked = False
            for selector in checkout_selectors:
                try:
                    await page.click(selector, timeout=3000)
                    clicked = True
                    break
                except:
                    continue

            if not clicked:
                await browser_manager.navigate(SHUFERSAL_CHECKOUT_URL)

            await asyncio.sleep(3)
            await page.wait_for_load_state("networkidle", timeout=15000)

            # Get order summary
            summary = await page.evaluate('''() => {
                const items = [];
                const summaryItems = document.querySelectorAll('[class*="order-item"], [class*="summary-item"], [class*="checkout-item"]');

                summaryItems.forEach(item => {
                    const nameEl = item.querySelector('[class*="name"], [class*="title"]');
                    const priceEl = item.querySelector('[class*="price"]');
                    const qtyEl = item.querySelector('[class*="quantity"], [class*="qty"]');

                    if (nameEl) {
                        items.push({
                            name: nameEl.textContent.trim(),
                            price: priceEl ? priceEl.textContent.trim() : '',
                            quantity: qtyEl ? qtyEl.textContent.trim() : '1'
                        });
                    }
                });

                const totalEl = document.querySelector('[class*="total"], [class*="Total"]');
                const deliveryEl = document.querySelector('[class*="delivery"], [class*="shipping"]');

                return {
                    items: items,
                    total: totalEl ? totalEl.textContent.trim() : '',
                    delivery: deliveryEl ? deliveryEl.textContent.trim() : ''
                };
            }''')

            return {
                "type": "checkout_view",
                "success": True,
                "current_url": page.url,
                "order_summary": summary,
                "message": "Navigated to checkout page. Please review your order and complete payment manually.",
                "warning": "DO NOT PROCEED WITHOUT USER CONFIRMATION - This is the checkout page. The user must review and confirm the order before completing the purchase."
            }

        except Exception as e:
            return {
                "type": "checkout_view",
                "success": False,
                "error": f"Error proceeding to checkout: {str(e)}"
            }

    return run_async(_checkout())


@tool()
def shufersal_get_delivery_slots() -> Dict[str, Any]:
    """
    Get available delivery time slots.

    Returns:
        List of available delivery dates and times
    """
    async def _get_slots():
        page = await browser_manager.get_page()

        try:
            # Navigate to checkout if not there
            if "checkout" not in page.url.lower():
                await browser_manager.navigate(SHUFERSAL_CHECKOUT_URL)
                await asyncio.sleep(2)

            # Look for delivery slot selection
            await page.wait_for_selector('[class*="delivery"], [class*="slot"], [class*="time"]', timeout=10000)

            slots = await page.evaluate('''() => {
                const slots = [];
                const slotElements = document.querySelectorAll('[class*="slot"], [class*="time-option"], [class*="delivery-option"]');

                slotElements.forEach((el, index) => {
                    const text = el.textContent.trim();
                    const isAvailable = !el.classList.contains('disabled') &&
                                       !el.classList.contains('unavailable') &&
                                       !el.hasAttribute('disabled');

                    if (text) {
                        slots.push({
                            index: index,
                            text: text,
                            available: isAvailable
                        });
                    }
                });

                return slots;
            }''')

            return {
                "type": "delivery_slots",
                "success": True,
                "slots": slots,
                "count": len(slots),
                "message": f"Found {len(slots)} delivery slots"
            }

        except Exception as e:
            return {
                "type": "delivery_slots",
                "success": False,
                "error": f"Error getting delivery slots: {str(e)}",
                "slots": []
            }

    return run_async(_get_slots())


@tool()
def shufersal_take_screenshot(filename: str = "shufersal_screenshot.png") -> Dict[str, Any]:
    """
    Take a screenshot of the current page for debugging.

    Args:
        filename: Name of the screenshot file (default: shufersal_screenshot.png)

    Returns:
        Screenshot status and file path
    """
    async def _screenshot():
        result = await browser_manager.screenshot(path=filename, full_page=True)
        if result["success"]:
            return {
                "type": "screenshot",
                "success": True,
                "path": filename,
                "message": f"Screenshot saved to {filename}"
            }
        return {
            "type": "screenshot",
            "success": False,
            "error": result.get("error", "Unknown error")
        }

    return run_async(_screenshot())


@tool()
def shufersal_close_browser() -> Dict[str, Any]:
    """
    Close the browser session.
    Call this when done with shopping.

    Returns:
        Browser close status
    """
    async def _close():
        await browser_manager.close()
        return {
            "type": "browser_status",
            "status": "closed",
            "success": True,
            "message": "Browser session closed"
        }

    return run_async(_close())
