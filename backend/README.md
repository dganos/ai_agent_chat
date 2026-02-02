# Shufersal Grocery Shopping Agent

An AI-powered grocery shopping assistant for Shufersal Online (שופרסל אונליין), the largest supermarket chain in Israel.

## Features

- **Natural Language Interface**: Talk to the assistant in Hebrew or English
- **Product Search**: Find products by name or category
- **Cart Management**: Add, remove, and update item quantities
- **Checkout Assistance**: Navigate to checkout with order review
- **Delivery Slots**: View available delivery times
- **Browser Automation**: Powered by Playwright for reliable web automation

## Prerequisites

- Python 3.9+
- Node.js 18+
- A Shufersal Online account
- OpenAI API key

## Installation

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```

5. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```

6. Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

## Running the Application

### Start the Backend (Grocery Agent)

```bash
cd backend
uvicorn backend.grocery_agent:app --reload --host 0.0.0.0 --port 8000
```

### Start the Frontend

```bash
cd frontend
npm run dev
```

Open http://localhost:3000 in your browser.

## Usage

### Getting Started

1. Open the application in your browser
2. Start by telling the assistant to initialize the browser:
   > "Initialize the browser" or "התחל"

3. Log in to your Shufersal account:
   > "Log in with email@example.com and password123"

4. Search for products:
   > "Find milk" or "חפש חלב"

5. Add items to cart:
   > "Add 2 milk to cart" or "הוסף חלב לסל"

6. View your cart:
   > "Show my cart" or "הצג את העגלה"

7. Proceed to checkout:
   > "Proceed to checkout" or "המשך לתשלום"

### Available Commands

| Command | Description |
|---------|-------------|
| Initialize browser | Start the browser session |
| Login | Log in to your Shufersal account |
| Search [product] | Search for products |
| Add [product] to cart | Add item to shopping cart |
| View cart | Show cart contents |
| Remove [product] | Remove item from cart |
| Update quantity | Change item quantity |
| Checkout | Navigate to checkout page |
| Delivery slots | Show available delivery times |
| Close browser | End the session |

## Security Notes

- **Credentials**: Never store your Shufersal password in plain text. Provide it at runtime.
- **Sessions**: Browser sessions are isolated and temporary.
- **Checkout**: The assistant will always ask for confirmation before proceeding to checkout.

## Architecture

```
backend/
├── grocery_agent.py      # Main agent with AI model and tools
├── browser/
│   ├── __init__.py
│   └── browser_manager.py # Playwright browser automation
├── shufersal/
│   ├── __init__.py
│   └── shufersal_tools.py # Shufersal-specific automation tools
└── requirements.txt

frontend/
├── app/
│   ├── page.tsx          # Main chat interface
│   └── api/copilotkit/   # API routes
├── components/
│   ├── ProductCard.tsx   # Product display components
│   ├── CartView.tsx      # Shopping cart component
│   └── BrowserStatus.tsx # Browser status indicators
```

## Tools Reference

### shufersal_initialize_browser
Initialize the browser for shopping.

### shufersal_login
Log in to Shufersal account with credentials.

### shufersal_search_products
Search for products by name or keyword.

### shufersal_add_to_cart
Add a product to the shopping cart.

### shufersal_view_cart
View current cart contents and total.

### shufersal_remove_from_cart
Remove a product from the cart.

### shufersal_update_quantity
Update the quantity of an item in the cart.

### shufersal_proceed_to_checkout
Navigate to checkout (requires user confirmation).

### shufersal_get_delivery_slots
Get available delivery time slots.

### shufersal_take_screenshot
Take a screenshot for debugging.

### shufersal_close_browser
Close the browser session.

## Alternative: Investment Analyst Agent

To run the original investment analyst agent instead:

```bash
uvicorn backend.agentic_chat:app --reload --host 0.0.0.0 --port 8000
```

Note: You'll need to update the frontend to use `investment-analyst` agent instead of `grocery-assistant`.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |

## Troubleshooting

### Browser won't start
- Make sure Playwright browsers are installed: `playwright install chromium`
- Check if Chrome is installed on your system

### Login fails
- Verify your Shufersal credentials
- Check if there's a CAPTCHA (take a screenshot to debug)
- Try with `headless=False` to see the browser

### Products not found
- Try different search terms (Hebrew often works better)
- Check your internet connection

### Cart actions fail
- Make sure you're logged in
- Try navigating to the cart first

### ModuleNotFoundError
If you get module not found errors, make sure you've:
1. Activated your virtual environment
2. Installed all requirements: `pip install -r requirements.txt`
3. Installed Playwright: `playwright install chromium`

### API Key Issues
If you get authentication errors:
1. Make sure your `.env` file exists in the `backend/` directory
2. Verify your OpenAI API key is correct
3. Check that you have credits available in your OpenAI account
