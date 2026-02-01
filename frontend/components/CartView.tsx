"use client";

import { ShoppingCart, Trash2, Plus, Minus, CreditCard, Package } from "lucide-react";

interface CartItem {
  index: number;
  name: string;
  price: number | null;
  priceDisplay: string;
  quantity: number;
  image: string;
}

interface CartViewProps {
  items: CartItem[];
  total: number | null;
  totalDisplay: string;
  onUpdateQuantity?: (itemName: string, quantity: number) => void;
  onRemoveItem?: (itemName: string) => void;
  onCheckout?: () => void;
}

export function CartView({
  items,
  total,
  totalDisplay,
  onUpdateQuantity,
  onRemoveItem,
  onCheckout,
}: CartViewProps) {
  const isEmpty = !items || items.length === 0;

  return (
    <div className="overflow-hidden rounded-xl border border-white/20 bg-white/40 shadow-lg backdrop-blur-sm dark:border-white/10 dark:bg-black/30">
      {/* Header */}
      <div className="flex items-center gap-3 border-b border-gray-200 bg-white/50 px-4 py-3 dark:border-gray-700 dark:bg-black/40">
        <ShoppingCart className="h-5 w-5 text-blue-500" />
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white" dir="rtl">
          עגלת הקניות
        </h3>
        {!isEmpty && (
          <span className="ml-auto rounded-full bg-blue-100 px-2.5 py-0.5 text-sm font-medium text-blue-800 dark:bg-blue-900 dark:text-blue-200">
            {items.length} פריטים
          </span>
        )}
      </div>

      {/* Cart Items */}
      <div className="max-h-[400px] overflow-y-auto">
        {isEmpty ? (
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <ShoppingCart className="mb-4 h-12 w-12 text-gray-300 dark:text-gray-600" />
            <p className="text-gray-500 dark:text-gray-400" dir="rtl">
              העגלה ריקה
            </p>
            <p className="mt-1 text-sm text-gray-400 dark:text-gray-500" dir="rtl">
              חפש מוצרים והוסף אותם לעגלה
            </p>
          </div>
        ) : (
          <ul className="divide-y divide-gray-200 dark:divide-gray-700">
            {items.map((item, index) => (
              <li key={index} className="flex items-center gap-4 p-4">
                {/* Product Image */}
                <div className="h-16 w-16 flex-shrink-0 overflow-hidden rounded-lg bg-gray-100 dark:bg-gray-800">
                  {item.image ? (
                    <img
                      src={item.image}
                      alt={item.name}
                      className="h-full w-full object-cover"
                      onError={(e) => {
                        (e.target as HTMLImageElement).style.display = "none";
                      }}
                    />
                  ) : (
                    <div className="flex h-full items-center justify-center">
                      <Package className="h-6 w-6 text-gray-400" />
                    </div>
                  )}
                </div>

                {/* Product Details */}
                <div className="flex-1 min-w-0">
                  <h4 className="truncate text-sm font-medium text-gray-900 dark:text-white" dir="rtl">
                    {item.name}
                  </h4>
                  <p className="mt-1 text-sm text-green-600 dark:text-green-400" dir="rtl">
                    {item.priceDisplay || (item.price ? `₪${item.price.toFixed(2)}` : "")}
                  </p>
                </div>

                {/* Quantity Controls */}
                <div className="flex items-center gap-2">
                  <div className="flex items-center rounded-lg border border-gray-200 dark:border-gray-600">
                    <button
                      onClick={() => onUpdateQuantity?.(item.name, Math.max(1, item.quantity - 1))}
                      className="p-1.5 text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 rounded-l-lg transition-colors"
                    >
                      <Minus className="h-3 w-3" />
                    </button>
                    <span className="min-w-[1.5rem] text-center text-sm font-medium">
                      {item.quantity}
                    </span>
                    <button
                      onClick={() => onUpdateQuantity?.(item.name, item.quantity + 1)}
                      className="p-1.5 text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 rounded-r-lg transition-colors"
                    >
                      <Plus className="h-3 w-3" />
                    </button>
                  </div>

                  {/* Remove Button */}
                  <button
                    onClick={() => onRemoveItem?.(item.name)}
                    className="p-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                    title="הסר מהעגלה"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Footer with Total and Checkout */}
      {!isEmpty && (
        <div className="border-t border-gray-200 bg-gray-50/50 p-4 dark:border-gray-700 dark:bg-black/20">
          <div className="flex items-center justify-between mb-4">
            <span className="text-base font-medium text-gray-900 dark:text-white" dir="rtl">
              סה&quot;כ לתשלום:
            </span>
            <span className="text-xl font-bold text-green-600 dark:text-green-400">
              {totalDisplay || (total ? `₪${total.toFixed(2)}` : "---")}
            </span>
          </div>

          <button
            onClick={onCheckout}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-green-500 to-green-600 px-4 py-3 text-sm font-medium text-white shadow-lg transition-all hover:from-green-600 hover:to-green-700 active:scale-[0.98]"
          >
            <CreditCard className="h-4 w-4" />
            <span dir="rtl">המשך לתשלום</span>
          </button>

          <p className="mt-2 text-center text-xs text-gray-500 dark:text-gray-400" dir="rtl">
            * המחירים כוללים מע&quot;מ
          </p>
        </div>
      )}
    </div>
  );
}

interface CartSummaryProps {
  itemCount: number;
  total: number | null;
  totalDisplay: string;
}

export function CartSummary({ itemCount, total, totalDisplay }: CartSummaryProps) {
  return (
    <div className="inline-flex items-center gap-3 rounded-full border border-white/20 bg-white/40 px-4 py-2 shadow-lg backdrop-blur-sm dark:border-white/10 dark:bg-black/30">
      <div className="relative">
        <ShoppingCart className="h-5 w-5 text-blue-500" />
        {itemCount > 0 && (
          <span className="absolute -right-2 -top-2 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-xs font-bold text-white">
            {itemCount}
          </span>
        )}
      </div>
      <span className="text-sm font-medium text-gray-900 dark:text-white">
        {totalDisplay || (total ? `₪${total.toFixed(2)}` : "₪0.00")}
      </span>
    </div>
  );
}
