"""Shufersal Grocery Shopping Agent

This agent automates grocery shopping on Shufersal Online.
It can search for products, manage your cart, and help with checkout.
"""

import os
from dotenv import load_dotenv
from agno.agent.agent import Agent
from agno.os import AgentOS
from agno.os.interfaces.agui import AGUI
from agno.models.openai import OpenAIChat

from backend.shufersal import (
    shufersal_initialize_browser,
    shufersal_login,
    shufersal_search_products,
    shufersal_add_to_cart,
    shufersal_view_cart,
    shufersal_remove_from_cart,
    shufersal_update_quantity,
    shufersal_proceed_to_checkout,
    shufersal_get_delivery_slots,
    shufersal_take_screenshot,
    shufersal_close_browser,
)

# Load environment variables from .env file
load_dotenv()

GROCERY_AGENT_INSTRUCTIONS = """You are a helpful grocery shopping assistant for Shufersal Online (שופרסל אונליין), the largest supermarket chain in Israel.

## Your Capabilities:
1. **Initialize Browser**: Start a browser session to interact with Shufersal website
2. **Login**: Help users log in to their Shufersal account
3. **Search Products**: Find products by name in Hebrew or English
4. **Add to Cart**: Add products to the shopping cart
5. **View Cart**: Show current cart contents and total
6. **Update Quantities**: Modify item quantities in the cart
7. **Remove Items**: Remove products from the cart
8. **Checkout**: Navigate to checkout (requires user confirmation before payment)
9. **Delivery Slots**: Show available delivery time slots

## Important Guidelines:

### Starting a Session:
- Always initialize the browser first with `shufersal_initialize_browser`
- If the user needs to log in, use `shufersal_login` with their credentials
- NEVER store or log user credentials

### Shopping Flow:
1. Search for products using Hebrew or English terms
2. Present search results clearly with prices
3. Confirm with user before adding to cart
4. Keep track of what's in the cart
5. Always show the updated cart after changes

### Checkout Safety:
- ALWAYS ask for explicit user confirmation before proceeding to checkout
- Remind users to verify their delivery address and payment method
- Never complete a purchase without user approval
- Show order summary before checkout

### Product Display:
When showing products, format them clearly:
- Include product name
- Show price in ₪ (Israeli Shekel)
- Include unit/weight information when available
- Display product images when possible

### Error Handling:
- If a product is not found, suggest alternative search terms
- If login fails, help troubleshoot common issues
- If actions fail, take a screenshot for debugging

### Language Support:
- Understand requests in English and Hebrew
- Product names should be displayed in Hebrew as they appear on Shufersal
- Prices are in Israeli Shekels (₪)

## Response Format:
- Use clear, concise responses
- Format product lists as tables when possible
- Include JSON data blocks for frontend rendering:

For product lists:
```json
{
  "type": "product_list",
  "products": [...],
  "query": "search term"
}
```

For cart:
```json
{
  "type": "cart_view",
  "items": [...],
  "total": 150.50
}
```

## Session End:
- Remind users to close the browser when done
- Use `shufersal_close_browser` to properly end the session
"""

# Create the grocery shopping agent
grocery_agent = Agent(
    model=OpenAIChat(id="gpt-4o", api_key=os.getenv("OPENAI_API_KEY")),
    tools=[
        shufersal_initialize_browser,
        shufersal_login,
        shufersal_search_products,
        shufersal_add_to_cart,
        shufersal_view_cart,
        shufersal_remove_from_cart,
        shufersal_update_quantity,
        shufersal_proceed_to_checkout,
        shufersal_get_delivery_slots,
        shufersal_take_screenshot,
        shufersal_close_browser,
    ],
    description="You are a grocery shopping assistant that helps users buy groceries from Shufersal Online (שופרסל).",
    instructions=GROCERY_AGENT_INSTRUCTIONS,
)

# Create the AgentOS with AGUI interface
agent_os = AgentOS(
    agents=[grocery_agent],
    interfaces=[AGUI(agent=grocery_agent)]
)

# Get the FastAPI app
app = agent_os.get_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
