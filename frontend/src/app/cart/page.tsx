

'use client';

import { useCart } from '@/context/CartContext';
import Link from 'next/link';
// const { cart, removeFromCart, updateQuantity, getTotalItems } = useCart();  // ← Add updateQuantity

export default function CartPage() {
  const { cart, removeFromCart, getTotalItems, updateQuantity } = useCart();

  // Calculate total price
  const getTotalPrice = () => {
    return cart.reduce((total, item) => total + (item.price * item.quantity), 0);
  };

  if (cart.length === 0) {
    return (
      <div className="container mx-auto p-8">
        <h1 className="text-3xl font-bold mb-8">Shopping Cart</h1>
        <div className="text-center py-16">
          <p className="text-xl text-gray-600 mb-4">Your cart is empty</p>
          <Link 
            href="/products" 
            className="bg-blue-600 text-white px-6 py-3 rounded hover:bg-blue-700"
          >
            Continue Shopping
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8">Shopping Cart</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Cart Items */}
        <div className="lg:col-span-2">
          {cart.map((item) => (
  <div 
    key={item.id} 
    className="border rounded-lg p-4 mb-4 flex justify-between items-center"
  >
    <div className="flex-1">
      <h2 className="text-xl font-semibold">{item.name}</h2>
      <p className="text-gray-600 mt-1">{item.description}</p>
      <p className="text-lg font-bold text-green-600 mt-2">
        Rs. {item.price} each
      </p>
      
      {/* Quantity Controls */}
      <div className="flex items-center gap-3 mt-3">
        <span className="text-gray-600">Quantity:</span>
        <button
          onClick={() => updateQuantity(item.id, item.quantity - 1)}
          className="bg-gray-200 hover:bg-gray-300 w-8 h-8 rounded flex items-center justify-center font-bold"
        >
          -
        </button>
        <span className="font-semibold text-lg w-8 text-center">
          {item.quantity}
        </span>
        <button
          onClick={() => updateQuantity(item.id, item.quantity + 1)}
          className="bg-gray-200 hover:bg-gray-300 w-8 h-8 rounded flex items-center justify-center font-bold"
        >
          +
        </button>
      </div>
    </div>
    
    <div className="text-right ml-4">
      <p className="text-xl font-bold mb-4">
        Rs. {(item.price * item.quantity).toFixed(2)}
      </p>
      <button
        onClick={() => removeFromCart(item.id)}
        className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
      >
        Remove
      </button>
    </div>
  </div>
))}
        </div>

        {/* Order Summary */}
        <div className="lg:col-span-1">
          <div className="border rounded-lg p-6 sticky top-8">
            <h2 className="text-2xl font-bold mb-4">Order Summary</h2>
            
            <div className="space-y-3 mb-6">
              <div className="flex justify-between">
                <span className="text-gray-600">Items ({getTotalItems()}):</span>
                <span className="font-semibold">Rs. {getTotalPrice().toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Shipping:</span>
                <span className="font-semibold">Free</span>
              </div>
              <div className="border-t pt-3 flex justify-between text-xl">
                <span className="font-bold">Total:</span>
                <span className="font-bold text-green-600">
                  Rs. {getTotalPrice().toFixed(2)}
                </span>
              </div>
            </div>

            <button className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 font-semibold">
              Proceed to Checkout
            </button>
            
            <Link 
              href="/products" 
              className="block text-center mt-4 text-blue-600 hover:underline"
            >
              Continue Shopping
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}