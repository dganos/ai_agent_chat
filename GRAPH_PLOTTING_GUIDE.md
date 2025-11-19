# 📊 Stock Chart Plotting - Complete Implementation Guide

## 🎯 Overview

This feature allows your AI agent to plot interactive stock price charts in the chat interface using the AG-UI protocol.

## 🔄 How It Works - The Complete Flow

### **1. User Request → Agent**
```
User: "Show me a chart for AAPL stock"
```

### **2. Agent → Backend Tool**
The AI agent (GPT-4o) recognizes the request and calls the `plot_stock_chart` tool:

```python
# backend/agentic_chat.py
@tool(external_execution=True)  # ← Marks this for frontend execution
def plot_stock_chart(ticker: str, period: str = "1mo") -> dict:
    # Fetches real stock data using yfinance
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    
    # Returns structured data
    return {
        "type": "stock_chart",
        "ticker": "AAPL",
        "company_name": "Apple Inc.",
        "period": "1mo",
        "data": [
            {"date": "2024-01-01", "price": 150.25, "volume": 1000000},
            # ... more data points
        ],
        "current_price": 155.50
    }
```

### **3. AG-UI Protocol → Frontend**
The data flows through:
- **Agno backend** (`/agui` endpoint)
- **AG-UI protocol**
- **CopilotKit runtime** (`/api/copilotkit`)
- **Frontend action handler**

### **4. Frontend → Chart Rendering**
The frontend receives the data and renders it:

```typescript
// frontend/app/page.tsx
useCopilotAction({
  name: "plot_stock_chart",
  handler: async (data) => {
    // Receives the chart data
    return data;
  },
  render: ({ args }) => {
    // Renders the StockChart component
    return <StockChart {...args} />
  }
})
```

### **5. Chart Display**
The `StockChart` component uses Recharts to display:
- **Interactive line chart** with price history
- **Current price** with change indicator
- **Period selector** (1d, 1mo, 1y, etc.)
- **Statistics** (start price, current, data points)

---

## 📁 Files Modified

### Backend (`backend/`)
```
backend/agentic_chat.py
├── Added: import yfinance as yf
├── Added: @tool plot_stock_chart()
└── Updated: agent.tools list
```

### Frontend (`frontend/`)
```
frontend/
├── package.json
│   └── Added: "recharts": "^2.15.0"
├── components/StockChart.tsx (NEW)
│   └── Interactive chart component
└── app/page.tsx
    ├── Import: useCopilotAction
    └── Registered: plot_stock_chart action handler
```

---

## 🚀 How to Use

### **Step 1: Install Dependencies**

```bash
# Backend
cd backend
pip install yfinance

# Frontend
cd frontend
npm install
```

### **Step 2: Start Both Servers**

```bash
# Terminal 1 - Backend
cd backend
uvicorn backend.agentic_chat:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### **Step 3: Test in Chat**

Try these commands:

```
1. "Show me a chart for AAPL"
2. "Plot Tesla stock for the last 6 months"
3. "Can you visualize Microsoft's stock performance this year?"
4. "Show me GOOGL stock chart"
```

---

## 🎨 Features

### Chart Features
✅ **Interactive tooltips** - Hover to see exact prices  
✅ **Responsive design** - Works on all screen sizes  
✅ **Dark mode support** - Automatically adapts  
✅ **Price change indicators** - Shows % gain/loss with colors  
✅ **Loading states** - Smooth loading animation  
✅ **Error handling** - Graceful failure messages  

### Supported Time Periods
- `1d` - 1 day
- `5d` - 5 days
- `1mo` - 1 month (default)
- `3mo` - 3 months
- `6mo` - 6 months
- `1y` - 1 year
- `2y` - 2 years
- `5y` - 5 years
- `max` - Maximum available

---

## 🔧 Customization

### Change Chart Colors
Edit `frontend/components/StockChart.tsx`:

```typescript
<Line 
  stroke="hsl(var(--primary))"  // ← Change this
  strokeWidth={2}
/>
```

### Add More Chart Types
You can add bar charts, area charts, or candlestick charts using Recharts:

```typescript
import { AreaChart, Area } from 'recharts';
// or
import { BarChart, Bar } from 'recharts';
```

### Add Volume Chart
Already included in data! Just uncomment in StockChart.tsx:

```typescript
<Line 
  type="monotone" 
  dataKey="volume" 
  stroke="hsl(var(--secondary))" 
  name="Volume"
/>
```

---

## 🐛 Troubleshooting

### Chart not showing?

**Check 1: Backend running?**
```bash
curl http://localhost:8000/agui
```

**Check 2: Frontend installed dependencies?**
```bash
cd frontend && npm install
```

**Check 3: Browser console errors?**
Open DevTools (F12) and check for errors

### Wrong data displayed?

**Check 1: Ticker symbol correct?**
Only use valid stock symbols (AAPL, TSLA, etc.)

**Check 2: Market hours?**
Some tickers may not have recent data outside market hours

---

## 🎯 Example Conversations

### Example 1: Basic Chart
```
You: "Show me Apple stock chart"
Agent: "Here's the stock chart for AAPL..."
[Interactive chart displays with last 1 month data]
```

### Example 2: Custom Period
```
You: "Plot Tesla stock for the last year"
Agent: "Here's TSLA's performance over the past year..."
[Chart shows 1 year of data]
```

### Example 3: Comparison Request
```
You: "Compare AAPL and MSFT"
Agent: "Let me show you both..."
[Two separate charts display]
```

---

## 📊 Data Flow Diagram

```
┌─────────────┐
│    User     │ "Show me AAPL chart"
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  CopilotChat    │ User message
│  (Frontend UI)  │
└────────┬────────┘
         │
         ▼
┌──────────────────┐
│  CopilotKit      │ POST /api/copilotkit
│  Runtime (FE)    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  AG-UI Protocol  │ WebSocket/HTTP
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Agno Backend    │ /agui endpoint
│  Agent + GPT-4o  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ plot_stock_chart │ @tool(external_execution=True)
│   (Backend)      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   YFinance API   │ Fetch real stock data
└────────┬─────────┘
         │
         ▼ Returns data
┌──────────────────┐
│  useCopilotAction│ Receives data
│   (Frontend)     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  StockChart      │ Renders with Recharts
│  Component       │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   User sees      │ Interactive chart! 📈
│   chart          │
└──────────────────┘
```

---

## 🎓 Key Concepts

### 1. **External Execution**
```python
@tool(external_execution=True)
```
- Marks tool for frontend execution
- Data returned to frontend, not to agent
- Enables rich UI rendering

### 2. **AG-UI Protocol**
- Standard protocol for agent-UI communication
- Handles tool calls, responses, streaming
- Works with any AG-UI compatible framework

### 3. **useCopilotAction**
- CopilotKit hook for registering actions
- Handles both execution and rendering
- Supports streaming and async operations

---

## 🚀 Next Steps

Want to enhance this further?

1. **Add more chart types** (candlestick, area, bar)
2. **Add technical indicators** (MA, RSI, MACD)
3. **Add comparison charts** (multiple stocks)
4. **Add real-time updates** (WebSocket streaming)
5. **Add export functionality** (PNG, CSV)
6. **Add drawing tools** (trendlines, annotations)

---

## 📝 Notes

- **Rate limits**: YFinance has rate limits for requests
- **Market hours**: Some data only available during market hours
- **Historical data**: Free tier has limitations
- **Performance**: Large datasets may slow rendering

---

## ✅ Testing Checklist

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Can request a chart for AAPL
- [ ] Chart displays correctly
- [ ] Hover tooltips work
- [ ] Dark mode works
- [ ] Different periods work (1d, 1mo, 1y)
- [ ] Error handling works (invalid ticker)
- [ ] Loading state displays
- [ ] Responsive on mobile

---

**Happy charting! 📊✨**

