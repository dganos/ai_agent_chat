# AI Agent Chat Frontend

A modern, responsive chat interface for interacting with your AI investment analyst agent built with Agno.

## Features

- 🎨 Modern, clean UI with Tailwind CSS
- 💬 Real-time chat interface powered by CopilotKit
- 📊 Integration with Agno backend agent
- 🌓 Dark mode support
- 📱 Fully responsive design
- ⚡ Built with Next.js 15 and React 19

## Getting Started

### Prerequisites

- Node.js 20+
- npm, yarn, pnpm, or bun
- Running Agno backend on `http://localhost:8000`

### Installation

1. Install dependencies:

```bash
npm install
```

2. Configure environment variables:

Create a `.env.local` file in the root directory (already created):

```env
AGNO_AGENT_URL=http://localhost:8000
```

3. Start the development server:

```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
frontend/
├── app/
│   ├── api/
│   │   └── copilotkit/
│   │       └── route.ts          # API route for agent communication
│   ├── globals.css               # Global styles
│   ├── layout.tsx                # Root layout
│   └── page.tsx                  # Home page with chat interface
├── public/                       # Static assets
├── .env.local                    # Environment variables
├── next.config.ts                # Next.js configuration
├── tailwind.config.ts            # Tailwind CSS configuration
├── tsconfig.json                 # TypeScript configuration
└── package.json                  # Dependencies
```

## Usage

### Starting a Chat

1. The chat sidebar opens automatically when you load the page
2. Type your questions about stocks, market data, or investment analysis
3. The AI agent will respond with detailed information, often formatted in tables

### Example Queries

- "What's the current price of AAPL?"
- "Show me analyst recommendations for TSLA"
- "Analyze the fundamentals of MSFT"
- "Compare GOOGL and META stock performance"

## Backend Integration

This frontend connects to your Agno backend agent via the `/api/copilotkit` route. Make sure your backend is running before starting the frontend:

```bash
# In the backend directory
uvicorn backend.agentic_chat:app --reload
```

The backend should be accessible at `http://localhost:8000`.

## Customization

### Changing the Agent Name

Edit `app/page.tsx` and `app/api/copilotkit/route.ts` to change the agent name from "investment-analyst" to your preferred name.

### Styling

- Modify `app/globals.css` for global styles
- Update `tailwind.config.ts` for theme customization
- Edit component styles directly in `app/page.tsx`

### Backend URL

Update the `AGNO_AGENT_URL` in `.env.local` if your backend runs on a different port or host.

## Build for Production

```bash
npm run build
npm start
```

## Technologies Used

- **Next.js 15** - React framework with App Router
- **React 19** - UI library
- **CopilotKit** - Agentic chat framework
- **Tailwind CSS** - Utility-first CSS framework
- **TypeScript** - Type-safe JavaScript

## Troubleshooting

### Agent not responding

- Ensure your Agno backend is running on `http://localhost:8000`
- Check that the AGUI interface is properly exposed in your backend
- Verify the agent name matches in both frontend and backend

### Styling issues

- Clear Next.js cache: `rm -rf .next`
- Reinstall dependencies: `rm -rf node_modules && npm install`

### Port already in use

Change the port in `package.json`:

```json
"dev": "next dev -p 3001"
```

## License

MIT

