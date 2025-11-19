import {
  CopilotRuntime,
  ExperimentalEmptyAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime";
import { HttpAgent } from "@ag-ui/client";
import { NextRequest } from "next/server";

// Handle POST requests
export async function POST(req: NextRequest) {
  // Get the backend agent URL from environment variables
  const AGNO_AGENT_URL = process.env.AGNO_AGENT_URL || "http://localhost:8000";

  // Create the Agno agent connection using HttpAgent
  // Agno exposes the AG-UI interface at /agui endpoint
  const investmentAnalystAgent = new HttpAgent({
    url: `${AGNO_AGENT_URL}/agui`,
  });

  // Initialize the CopilotRuntime with the agent
  const runtime = new CopilotRuntime({
    agents: {
      "investment-analyst": investmentAnalystAgent,
    },
  });

  // Setup the endpoint handler
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter: new ExperimentalEmptyAdapter(),
    endpoint: "/api/copilotkit",
  });

  // Handle the request
  return handleRequest(req);
}

