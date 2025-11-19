"use client";

import { CopilotKit } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";
import { TrendingUp } from "lucide-react";
import { StockChart } from "@/components/StockChart";
import { ReactNode } from "react";

export default function Home() {
  return (
    <CopilotKit
      runtimeUrl="/api/copilotkit"
      agent="investment-analyst"
      showDevConsole={true}
    >
      <ChatInterface />
    </CopilotKit>
  );
}

function ChatInterface() {
  // Custom text renderer to handle chart data in JSON code blocks
  const textRenderer = (text: string): ReactNode => {
    try {
      // Look for JSON code blocks with chart data
      const jsonBlockMatch = text.match(/```json\s*\n?([\s\S]*?)\n?```/);
      if (jsonBlockMatch) {
        try {
          const chartData = JSON.parse(jsonBlockMatch[1]);
          if (chartData.type === "stock_chart" && chartData.data && chartData.ticker) {
            // Remove the JSON code block from the text
            const textWithoutJson = text.replace(jsonBlockMatch[0], '').trim();
            return (
              <div className="space-y-4">
                {textWithoutJson && <div className="prose dark:prose-invert max-w-none">{textWithoutJson}</div>}
                <StockChart
                  ticker={chartData.ticker}
                  company_name={chartData.company_name || chartData.ticker}
                  period={chartData.period || "1mo"}
                  data={chartData.data}
                  current_price={chartData.current_price}
                />
              </div>
            );
          }
        } catch (parseError) {
          console.error("Error parsing JSON from code block:", parseError);
        }
      }
      
      // Also try to find inline JSON (without code blocks)
      const inlineJsonMatch = text.match(/\{[^{}]*"type":\s*"stock_chart"[\s\S]*?"data":\s*\[[\s\S]*?\][\s\S]*?\}/);
      if (inlineJsonMatch) {
        try {
          const chartData = JSON.parse(inlineJsonMatch[0]);
          if (chartData.type === "stock_chart" && chartData.data && chartData.ticker) {
            const textWithoutJson = text.replace(inlineJsonMatch[0], '').trim();
            return (
              <div className="space-y-4">
                {textWithoutJson && <div className="prose dark:prose-invert max-w-none">{textWithoutJson}</div>}
                <StockChart
                  ticker={chartData.ticker}
                  company_name={chartData.company_name || chartData.ticker}
                  period={chartData.period || "1mo"}
                  data={chartData.data}
                  current_price={chartData.current_price}
                />
              </div>
            );
          }
        } catch (parseError) {
          console.error("Error parsing inline JSON:", parseError);
        }
      }
    } catch (e) {
      console.error("Error in textRenderer:", e);
    }
    
    // Return the text as-is if no chart data found
    return text;
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden p-4 sm:p-6 lg:p-8">
      {/* Animated Colorful Blurred Background */}
      <div className="absolute inset-0 -z-10">
        {/* Base gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-slate-950 dark:via-blue-950 dark:to-purple-950" />
        
        {/* Animated blobs */}
        <div className="absolute -left-1/4 top-0 h-96 w-96 animate-blob rounded-full bg-purple-300 opacity-70 blur-3xl mix-blend-multiply filter dark:bg-purple-700 dark:opacity-30" />
        <div className="animation-delay-2000 absolute -right-1/4 top-0 h-96 w-96 animate-blob rounded-full bg-yellow-300 opacity-70 blur-3xl mix-blend-multiply filter dark:bg-yellow-700 dark:opacity-30" />
        <div className="animation-delay-4000 absolute -bottom-8 left-1/3 h-96 w-96 animate-blob rounded-full bg-pink-300 opacity-70 blur-3xl mix-blend-multiply filter dark:bg-pink-700 dark:opacity-30" />
        <div className="animation-delay-6000 absolute bottom-0 right-1/4 h-96 w-96 animate-blob rounded-full bg-blue-300 opacity-70 blur-3xl mix-blend-multiply filter dark:bg-blue-700 dark:opacity-30" />
      </div>

      {/* Glass Chat Window */}
      <div className="relative w-full max-w-5xl">
        <div className="overflow-hidden rounded-3xl border border-white/20 bg-white/30 shadow-2xl backdrop-blur-xl dark:border-white/10 dark:bg-black/30">
          {/* Header */}
          <div className="border-b border-white/20 bg-white/50 px-6 py-4 backdrop-blur-xl dark:border-white/10 dark:bg-black/40">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 shadow-lg">
                <TrendingUp className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-900 dark:text-white">
                  AI Investment Analyst
                </h1>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  Powered by GPT-4o & YFinance
                </p>
              </div>
            </div>
          </div>

          {/* Chat Area */}
          <div className="h-[70vh] overflow-hidden">
            <CopilotChat
              className="h-full bg-transparent"
              instructions="You are an investment analyst that researches stock prices, analyst recommendations, and stock fundamentals. Format your responses using markdown and use tables to display data where possible."
              labels={{
                title: "AI Investment Analyst",
                initial: "Hello! 👋 I'm your AI investment analyst. I can help you research stock prices, analyst recommendations, and stock fundamentals. What would you like to know?",
                placeholder: "Ask about stocks, market trends, or investment analysis...",
              }}
              makeSystemMessage={(message) => {
                // Intercept messages to render charts
                if (message.role === "assistant" && typeof message.content === "string") {
                  const content = textRenderer(message.content);
                  if (content !== message.content) {
                    return { ...message, content };
                  }
                }
                return message;
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

