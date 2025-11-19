"""Example: Agno Agent with Finance tools

This example shows how to create an Agno Agent with tools (YFinanceTools) and expose it in an AG-UI compatible way.
"""
import os
from dotenv import load_dotenv
from agno.agent.agent import Agent
from agno.os import AgentOS
from agno.os.interfaces.agui import AGUI
from agno.models.openai import OpenAIChat
from agno.tools.yfinance import YFinanceTools
from agno.tools import tool
import yfinance as yf
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()


@tool()
def plot_stock_chart(ticker: str, period: str = "1mo") -> dict:
    """
    Fetch and plot stock price history chart. Returns data for frontend visualization.

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, TSLA, MSFT)
        period: Time period - "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"
    
    Returns:
        Chart data with dates and prices for frontend rendering
    """
    try:
        # Fetch stock data
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        
        # Prepare data for chart
        chart_data = []
        for date, row in hist.iterrows():
            chart_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "price": round(float(row['Close']), 2),
                "volume": int(row['Volume']),
            })
        
        # Get company info
        info = stock.info
        company_name = info.get('longName', ticker)
        
        return {
            "type": "stock_chart",
            "ticker": ticker.upper(),
            "company_name": company_name,
            "period": period,
            "data": chart_data,
            "current_price": chart_data[-1]["price"] if chart_data else None,
        }
    except Exception as e:
        return {
            "type": "error",
            "message": f"Failed to fetch data for {ticker}: {str(e)}"
        }


agent = Agent(
  model=OpenAIChat(id="gpt-4o", api_key=os.getenv("OPENAI_API_KEY")),
  tools=[
    YFinanceTools(),
    plot_stock_chart,
  ],
  description="You are an investment analyst that researches stock prices, analyst recommendations, and stock fundamentals. You can plot interactive stock charts.",
  instructions="""Format your response using markdown and use tables to display data where possible. 

When asked to show a chart or visualize stock data:
1. Use the plot_stock_chart tool - it will return a JSON object with chart data
2. After the tool executes successfully, you MUST include the COMPLETE JSON result in your response
3. Wrap it in a JSON code block exactly like this:

```json
{
  "type": "stock_chart",
  "ticker": "AAPL",
  "company_name": "Apple Inc.",
  "period": "1mo",
  "data": [...],
  "current_price": 150.25
}
```

Include the ENTIRE data array - do not truncate it. The frontend needs this JSON to render an interactive chart.
You can add commentary before or after the JSON code block.""",
)

agent_os = AgentOS(
  agents=[agent],
  interfaces=[AGUI(agent=agent)]
)

app = agent_os.get_app()