"use client";

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { TrendingUp, TrendingDown } from "lucide-react";

interface StockChartData {
  date: string;
  price: number;
  volume: number;
}

interface StockChartProps {
  ticker: string;
  company_name: string;
  period: string;
  data: StockChartData[];
  current_price: number;
}

export function StockChart({ ticker, company_name, period, data, current_price }: StockChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4">
        <p className="text-sm text-destructive">No data available for {ticker}</p>
      </div>
    );
  }

  const firstPrice = data[0]?.price || 0;
  const priceChange = current_price - firstPrice;
  const priceChangePercent = ((priceChange / firstPrice) * 100).toFixed(2);
  const isPositive = priceChange >= 0;

  return (
    <div className="w-full space-y-4 rounded-xl border bg-card p-6 shadow-lg">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-2xl font-bold">{ticker}</h3>
            <span className="rounded-full bg-muted px-2 py-1 text-xs text-muted-foreground">
              {period}
            </span>
          </div>
          <p className="text-sm text-muted-foreground">{company_name}</p>
        </div>
        <div className="text-right">
          <p className="text-3xl font-bold">${current_price.toFixed(2)}</p>
          <div className={`flex items-center gap-1 ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
            {isPositive ? (
              <TrendingUp className="h-4 w-4" />
            ) : (
              <TrendingDown className="h-4 w-4" />
            )}
            <span className="text-sm font-semibold">
              {isPositive ? '+' : ''}{priceChange.toFixed(2)} ({priceChangePercent}%)
            </span>
          </div>
        </div>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
          <XAxis 
            dataKey="date" 
            tick={{ fontSize: 12 }}
            className="text-muted-foreground"
          />
          <YAxis 
            tick={{ fontSize: 12 }}
            className="text-muted-foreground"
            domain={['dataMin - 5', 'dataMax + 5']}
          />
          <Tooltip 
            contentStyle={{
              backgroundColor: 'hsl(var(--card))',
              border: '1px solid hsl(var(--border))',
              borderRadius: '0.5rem',
            }}
            labelStyle={{ color: 'hsl(var(--foreground))' }}
          />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="price" 
            stroke="hsl(var(--primary))" 
            strokeWidth={2}
            dot={false}
            name="Price ($)"
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 rounded-lg bg-muted/50 p-4">
        <div>
          <p className="text-xs text-muted-foreground">Period Start</p>
          <p className="font-semibold">${firstPrice.toFixed(2)}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Current</p>
          <p className="font-semibold">${current_price.toFixed(2)}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Data Points</p>
          <p className="font-semibold">{data.length}</p>
        </div>
      </div>
    </div>
  );
}

