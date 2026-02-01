"use client";

import { ShoppingCart, Plus, Minus, Package } from "lucide-react";
import { useState } from "react";

interface Product {
  id: string;
  name: string;
  price: number | null;
  priceDisplay: string;
  image: string;
  unit: string;
  index: number;
}

interface ProductCardProps {
  product: Product;
  onAddToCart?: (product: Product, quantity: number) => void;
}

export function ProductCard({ product, onAddToCart }: ProductCardProps) {
  const [quantity, setQuantity] = useState(1);
  const [isAdding, setIsAdding] = useState(false);

  const handleAddToCart = () => {
    setIsAdding(true);
    onAddToCart?.(product, quantity);
    setTimeout(() => setIsAdding(false), 500);
  };

  return (
    <div className="group relative flex flex-col overflow-hidden rounded-xl border border-white/20 bg-white/40 shadow-lg backdrop-blur-sm transition-all hover:shadow-xl hover:border-white/30 dark:border-white/10 dark:bg-black/30">
      {/* Product Image */}
      <div className="relative aspect-square overflow-hidden bg-gray-100 dark:bg-gray-800">
        {product.image ? (
          <img
            src={product.image}
            alt={product.name}
            className="h-full w-full object-cover transition-transform group-hover:scale-105"
            onError={(e) => {
              (e.target as HTMLImageElement).style.display = "none";
            }}
          />
        ) : (
          <div className="flex h-full items-center justify-center">
            <Package className="h-12 w-12 text-gray-400" />
          </div>
        )}
      </div>

      {/* Product Info */}
      <div className="flex flex-1 flex-col p-4">
        <h3 className="mb-2 line-clamp-2 text-sm font-medium text-gray-900 dark:text-white" dir="rtl">
          {product.name}
        </h3>

        {product.unit && (
          <p className="mb-2 text-xs text-gray-500 dark:text-gray-400" dir="rtl">
            {product.unit}
          </p>
        )}

        <div className="mt-auto">
          {/* Price */}
          <div className="mb-3 flex items-baseline gap-1" dir="rtl">
            <span className="text-lg font-bold text-green-600 dark:text-green-400">
              {product.priceDisplay || (product.price ? `₪${product.price.toFixed(2)}` : "מחיר לא זמין")}
            </span>
          </div>

          {/* Quantity Controls */}
          <div className="flex items-center gap-2">
            <div className="flex items-center rounded-lg border border-gray-200 dark:border-gray-600">
              <button
                onClick={() => setQuantity(Math.max(1, quantity - 1))}
                className="p-2 text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 rounded-l-lg transition-colors"
              >
                <Minus className="h-4 w-4" />
              </button>
              <span className="min-w-[2rem] text-center text-sm font-medium">
                {quantity}
              </span>
              <button
                onClick={() => setQuantity(quantity + 1)}
                className="p-2 text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 rounded-r-lg transition-colors"
              >
                <Plus className="h-4 w-4" />
              </button>
            </div>

            {/* Add to Cart Button */}
            <button
              onClick={handleAddToCart}
              disabled={isAdding}
              className={`flex flex-1 items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-medium text-white transition-all ${
                isAdding
                  ? "bg-green-500"
                  : "bg-blue-500 hover:bg-blue-600 active:scale-95"
              }`}
            >
              <ShoppingCart className="h-4 w-4" />
              {isAdding ? "נוסף!" : "הוסף לסל"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

interface ProductListProps {
  products: Product[];
  query?: string;
  onAddToCart?: (product: Product, quantity: number) => void;
}

export function ProductList({ products, query, onAddToCart }: ProductListProps) {
  if (!products || products.length === 0) {
    return (
      <div className="rounded-xl border border-yellow-200 bg-yellow-50 p-4 dark:border-yellow-800 dark:bg-yellow-900/20">
        <p className="text-center text-yellow-800 dark:text-yellow-200" dir="rtl">
          לא נמצאו מוצרים{query ? ` עבור "${query}"` : ""}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {query && (
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white" dir="rtl">
            תוצאות חיפוש: "{query}"
          </h3>
          <span className="rounded-full bg-blue-100 px-3 py-1 text-sm text-blue-800 dark:bg-blue-900 dark:text-blue-200">
            {products.length} מוצרים
          </span>
        </div>
      )}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
        {products.map((product, index) => (
          <ProductCard
            key={product.id || index}
            product={product}
            onAddToCart={onAddToCart}
          />
        ))}
      </div>
    </div>
  );
}
