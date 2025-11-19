# AI Agent Chat Backend

This is the backend for the AI Agent Chat application, built with Agno and FastAPI.

## Setup

1. **Create a virtual environment (recommended):**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Create a `.env` file in the backend directory:**

```bash
# backend/.env
OPENAI_API_KEY=your_openai_api_key_here
```

Replace `your_openai_api_key_here` with your actual OpenAI API key. You can get one from [OpenAI Platform](https://platform.openai.com/api-keys).

## Running the Backend

```bash
uvicorn backend.agentic_chat:app --reload
```

The backend will start on `http://localhost:8000`

## API Documentation

Once the server is running, you can view the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Available Endpoints

- `/agui` - AG-UI interface for the agent (used by the frontend)
- `/agents` - List available agents
- `/health` - Health check endpoint
- And more...

## Agent Features

The investment analyst agent includes:

- **YFinance Tools** - Get stock prices, analyst recommendations, and fundamentals
- **OpenAI GPT-4o** - Powered by GPT-4o for intelligent responses
- **Markdown Formatting** - Responses are formatted in markdown with tables

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |

## Troubleshooting

### ModuleNotFoundError

If you get module not found errors, make sure you've:
1. Activated your virtual environment
2. Installed all requirements: `pip install -r requirements.txt`

### API Key Issues

If you get authentication errors:
1. Make sure your `.env` file exists in the `backend/` directory
2. Verify your OpenAI API key is correct
3. Check that you have credits available in your OpenAI account

