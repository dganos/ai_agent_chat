"use client";

import { CopilotKit } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";
import { ShoppingCart } from "lucide-react";
import { ProductList } from "@/components/ProductCard";
import { CartView } from "@/components/CartView";
import { BrowserStatus, LoginStatus } from "@/components/BrowserStatus";
import { ReactNode } from "react";

export default function Home() {
  return (
    <CopilotKit
      runtimeUrl="/api/copilotkit"
      agent="grocery-assistant"
      showDevConsole={true}
    >
      <ChatInterface />
    </CopilotKit>
  );
}

function ChatInterface() {
  // Custom text renderer to handle grocery data in JSON code blocks
  const textRenderer = (text: string): ReactNode => {
    try {
      // Look for JSON code blocks with various data types
      const jsonBlockMatch = text.match(/```json\s*\n?([\s\S]*?)\n?```/);
      if (jsonBlockMatch) {
        try {
          const data = JSON.parse(jsonBlockMatch[1]);
          const textWithoutJson = text.replace(jsonBlockMatch[0], '').trim();

          // Handle different data types
          if (data.type === "product_list" && data.products) {
            return (
              <div className="space-y-4">
                {textWithoutJson && (
                  <div className="prose dark:prose-invert max-w-none" dir="rtl">
                    {textWithoutJson}
                  </div>
                )}
                <ProductList
                  products={data.products}
                  query={data.query}
                />
              </div>
            );
          }

          if (data.type === "cart_view" && data.items) {
            return (
              <div className="space-y-4">
                {textWithoutJson && (
                  <div className="prose dark:prose-invert max-w-none" dir="rtl">
                    {textWithoutJson}
                  </div>
                )}
                <CartView
                  items={data.items}
                  total={data.total}
                  totalDisplay={data.total_display || data.totalDisplay}
                />
              </div>
            );
          }

          if (data.type === "browser_status") {
            const status = data.status === "initialized" || data.success
              ? "ready"
              : data.status === "closed"
              ? "closed"
              : data.success === false
              ? "error"
              : "idle";
            return (
              <div className="space-y-4">
                {textWithoutJson && (
                  <div className="prose dark:prose-invert max-w-none" dir="rtl">
                    {textWithoutJson}
                  </div>
                )}
                <BrowserStatus
                  status={status}
                  currentUrl={data.current_url || data.url}
                  pageTitle={data.page_title || data.title}
                  message={data.message}
                  error={data.error}
                />
              </div>
            );
          }

          if (data.type === "login_status") {
            return (
              <div className="space-y-4">
                {textWithoutJson && (
                  <div className="prose dark:prose-invert max-w-none" dir="rtl">
                    {textWithoutJson}
                  </div>
                )}
                <LoginStatus
                  isLoggedIn={data.success}
                  message={data.message}
                  error={data.error}
                />
              </div>
            );
          }

          if (data.type === "cart_action") {
            const isSuccess = data.success;
            return (
              <div className="space-y-4">
                {textWithoutJson && (
                  <div className="prose dark:prose-invert max-w-none" dir="rtl">
                    {textWithoutJson}
                  </div>
                )}
                <div
                  className={`rounded-lg border p-4 ${
                    isSuccess
                      ? "border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20"
                      : "border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20"
                  }`}
                >
                  <p
                    className={`font-medium ${
                      isSuccess
                        ? "text-green-800 dark:text-green-200"
                        : "text-red-800 dark:text-red-200"
                    }`}
                    dir="rtl"
                  >
                    {data.message || (isSuccess ? "הפעולה בוצעה בהצלחה" : "הפעולה נכשלה")}
                  </p>
                  {data.error && (
                    <p className="mt-1 text-sm text-red-600 dark:text-red-400" dir="rtl">
                      {data.error}
                    </p>
                  )}
                </div>
              </div>
            );
          }

          if (data.type === "checkout_view") {
            return (
              <div className="space-y-4">
                {textWithoutJson && (
                  <div className="prose dark:prose-invert max-w-none" dir="rtl">
                    {textWithoutJson}
                  </div>
                )}
                <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4 dark:border-yellow-800 dark:bg-yellow-900/20">
                  <p className="font-medium text-yellow-800 dark:text-yellow-200" dir="rtl">
                    {data.warning || "בדוק את פרטי ההזמנה לפני השלמת הרכישה"}
                  </p>
                  {data.message && (
                    <p className="mt-1 text-sm text-yellow-700 dark:text-yellow-300" dir="rtl">
                      {data.message}
                    </p>
                  )}
                </div>
              </div>
            );
          }

          if (data.type === "delivery_slots" && data.slots) {
            return (
              <div className="space-y-4">
                {textWithoutJson && (
                  <div className="prose dark:prose-invert max-w-none" dir="rtl">
                    {textWithoutJson}
                  </div>
                )}
                <div className="rounded-lg border border-white/20 bg-white/40 p-4 dark:border-white/10 dark:bg-black/30">
                  <h4 className="mb-3 font-medium text-gray-900 dark:text-white" dir="rtl">
                    זמני משלוח זמינים:
                  </h4>
                  <ul className="space-y-2">
                    {data.slots.map((slot: any, index: number) => (
                      <li
                        key={index}
                        className={`rounded-md p-2 ${
                          slot.available
                            ? "bg-green-50 text-green-800 dark:bg-green-900/20 dark:text-green-200"
                            : "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400"
                        }`}
                        dir="rtl"
                      >
                        {slot.text}
                        {!slot.available && " (לא זמין)"}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            );
          }

        } catch (parseError) {
          console.error("Error parsing JSON from code block:", parseError);
        }
      }

      // Also try to find inline JSON (without code blocks)
      const inlineJsonMatch = text.match(/\{[^{}]*"type":\s*"(product_list|cart_view|browser_status|login_status|cart_action)"[\s\S]*?\}/);
      if (inlineJsonMatch) {
        try {
          const data = JSON.parse(inlineJsonMatch[0]);
          // Similar handling as above but for inline JSON
          if (data.type === "product_list" && data.products) {
            const textWithoutJson = text.replace(inlineJsonMatch[0], '').trim();
            return (
              <div className="space-y-4">
                {textWithoutJson && (
                  <div className="prose dark:prose-invert max-w-none" dir="rtl">
                    {textWithoutJson}
                  </div>
                )}
                <ProductList products={data.products} query={data.query} />
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

    // Return the text as-is if no special data found
    return text;
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden p-4 sm:p-6 lg:p-8">
      {/* Animated Colorful Blurred Background */}
      <div className="absolute inset-0 -z-10">
        {/* Base gradient - green theme for grocery */}
        <div className="absolute inset-0 bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50 dark:from-slate-950 dark:via-green-950 dark:to-emerald-950" />

        {/* Animated blobs */}
        <div className="absolute -left-1/4 top-0 h-96 w-96 animate-blob rounded-full bg-green-300 opacity-70 blur-3xl mix-blend-multiply filter dark:bg-green-700 dark:opacity-30" />
        <div className="animation-delay-2000 absolute -right-1/4 top-0 h-96 w-96 animate-blob rounded-full bg-yellow-300 opacity-70 blur-3xl mix-blend-multiply filter dark:bg-yellow-700 dark:opacity-30" />
        <div className="animation-delay-4000 absolute -bottom-8 left-1/3 h-96 w-96 animate-blob rounded-full bg-teal-300 opacity-70 blur-3xl mix-blend-multiply filter dark:bg-teal-700 dark:opacity-30" />
        <div className="animation-delay-6000 absolute bottom-0 right-1/4 h-96 w-96 animate-blob rounded-full bg-emerald-300 opacity-70 blur-3xl mix-blend-multiply filter dark:bg-emerald-700 dark:opacity-30" />
      </div>

      {/* Glass Chat Window */}
      <div className="relative w-full max-w-5xl">
        <div className="overflow-hidden rounded-3xl border border-white/20 bg-white/30 shadow-2xl backdrop-blur-xl dark:border-white/10 dark:bg-black/30">
          {/* Header */}
          <div className="border-b border-white/20 bg-white/50 px-6 py-4 backdrop-blur-xl dark:border-white/10 dark:bg-black/40">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 shadow-lg">
                <ShoppingCart className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-900 dark:text-white">
                  Shufersal Shopping Assistant
                </h1>
                <p className="text-sm text-slate-600 dark:text-slate-400" dir="rtl">
                  עוזר קניות חכם לשופרסל אונליין
                </p>
              </div>
            </div>
          </div>

          {/* Chat Area */}
          <div className="h-[70vh] overflow-hidden">
            <CopilotChat
              className="h-full bg-transparent"
              instructions="You are a grocery shopping assistant for Shufersal Online. Help users find products, add items to cart, and complete their grocery shopping. Always respond in a friendly and helpful manner. When displaying product search results, format them as a numbered list with name and price."
              labels={{
                title: "Shufersal Shopping Assistant",
                initial: "שלום! אני העוזר החכם לקניות בשופרסל אונליין. אני יכול לעזור לך למצוא מוצרים, להוסיף אותם לסל, ולסיים את הקנייה. במה אוכל לעזור?",
                placeholder: "חפש מוצרים או שאל אותי משהו...",
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
