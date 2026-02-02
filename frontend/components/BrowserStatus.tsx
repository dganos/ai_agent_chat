"use client";

import { Globe, Loader2, CheckCircle, XCircle, AlertCircle } from "lucide-react";

interface BrowserStatusProps {
  status: "idle" | "initializing" | "ready" | "error" | "closed";
  currentUrl?: string;
  pageTitle?: string;
  message?: string;
  error?: string;
}

export function BrowserStatus({
  status,
  currentUrl,
  pageTitle,
  message,
  error,
}: BrowserStatusProps) {
  const getStatusInfo = () => {
    switch (status) {
      case "initializing":
        return {
          icon: <Loader2 className="h-5 w-5 animate-spin text-blue-500" />,
          label: "מפעיל דפדפן...",
          bgColor: "bg-blue-50 dark:bg-blue-900/20",
          borderColor: "border-blue-200 dark:border-blue-800",
          textColor: "text-blue-800 dark:text-blue-200",
        };
      case "ready":
        return {
          icon: <CheckCircle className="h-5 w-5 text-green-500" />,
          label: "דפדפן מוכן",
          bgColor: "bg-green-50 dark:bg-green-900/20",
          borderColor: "border-green-200 dark:border-green-800",
          textColor: "text-green-800 dark:text-green-200",
        };
      case "error":
        return {
          icon: <XCircle className="h-5 w-5 text-red-500" />,
          label: "שגיאה",
          bgColor: "bg-red-50 dark:bg-red-900/20",
          borderColor: "border-red-200 dark:border-red-800",
          textColor: "text-red-800 dark:text-red-200",
        };
      case "closed":
        return {
          icon: <Globe className="h-5 w-5 text-gray-400" />,
          label: "דפדפן סגור",
          bgColor: "bg-gray-50 dark:bg-gray-900/20",
          borderColor: "border-gray-200 dark:border-gray-800",
          textColor: "text-gray-600 dark:text-gray-400",
        };
      default:
        return {
          icon: <Globe className="h-5 w-5 text-gray-400" />,
          label: "לא פעיל",
          bgColor: "bg-gray-50 dark:bg-gray-900/20",
          borderColor: "border-gray-200 dark:border-gray-800",
          textColor: "text-gray-600 dark:text-gray-400",
        };
    }
  };

  const statusInfo = getStatusInfo();

  return (
    <div
      className={`rounded-lg border ${statusInfo.borderColor} ${statusInfo.bgColor} p-4`}
    >
      <div className="flex items-center gap-3">
        {statusInfo.icon}
        <div className="flex-1">
          <p className={`font-medium ${statusInfo.textColor}`} dir="rtl">
            {statusInfo.label}
          </p>
          {message && (
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400" dir="rtl">
              {message}
            </p>
          )}
          {error && (
            <p className="mt-1 text-sm text-red-600 dark:text-red-400" dir="rtl">
              {error}
            </p>
          )}
        </div>
      </div>

      {currentUrl && status === "ready" && (
        <div className="mt-3 rounded-md bg-white/50 p-2 dark:bg-black/20">
          <p className="text-xs text-gray-500 dark:text-gray-400">URL:</p>
          <p className="truncate text-sm text-gray-700 dark:text-gray-300">
            {currentUrl}
          </p>
          {pageTitle && (
            <>
              <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">כותרת:</p>
              <p className="truncate text-sm text-gray-700 dark:text-gray-300" dir="rtl">
                {pageTitle}
              </p>
            </>
          )}
        </div>
      )}
    </div>
  );
}

interface LoginStatusProps {
  isLoggedIn: boolean;
  message?: string;
  error?: string;
}

export function LoginStatus({ isLoggedIn, message, error }: LoginStatusProps) {
  return (
    <div
      className={`rounded-lg border p-4 ${
        isLoggedIn
          ? "border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20"
          : error
          ? "border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20"
          : "border-yellow-200 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-900/20"
      }`}
    >
      <div className="flex items-center gap-3">
        {isLoggedIn ? (
          <CheckCircle className="h-5 w-5 text-green-500" />
        ) : error ? (
          <XCircle className="h-5 w-5 text-red-500" />
        ) : (
          <AlertCircle className="h-5 w-5 text-yellow-500" />
        )}
        <div>
          <p
            className={`font-medium ${
              isLoggedIn
                ? "text-green-800 dark:text-green-200"
                : error
                ? "text-red-800 dark:text-red-200"
                : "text-yellow-800 dark:text-yellow-200"
            }`}
            dir="rtl"
          >
            {isLoggedIn ? "מחובר לחשבון" : error ? "שגיאת התחברות" : "לא מחובר"}
          </p>
          {(message || error) && (
            <p
              className={`mt-1 text-sm ${
                error
                  ? "text-red-600 dark:text-red-400"
                  : "text-gray-600 dark:text-gray-400"
              }`}
              dir="rtl"
            >
              {message || error}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
