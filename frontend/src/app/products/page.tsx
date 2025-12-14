'use client';

import { useEffect, useState } from 'react';
import { getAllProducts } from '@/services/productService';
import { Product } from '@/types/product';
import { useCart } from '@/context/CartContext';
import Link from 'next/link';


export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const { addToCart, getTotalItems } = useCart();

  useEffect(() => {
    async function fetchProducts() {
      try {
        const data = await getAllProducts();
        setProducts(data);
      } catch (error) {
        console.error('Failed to fetch products:', error);
      } finally {
        setLoading(false);
      }
    }
    fetchProducts();
  }, []);

  const handleAddToCart = (product: Product) => {
    addToCart(product);
    alert(`${product.name} added to cart!`);
  };

  if (loading) {
    return <div className="container mx-auto p-8">Loading products...</div>;
  }

  return (
    <div className="container mx-auto p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Our Products</h1>
        <Link 
          href="/cart"
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
  >
    Cart: {getTotalItems()} items
  </Link>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {products.map((product) => (
          <Link 
  key={product.id} 
  href={`/products/${product.id}`}
  className="border rounded-lg p-4 shadow hover:shadow-lg block cursor-pointer"
>
  <h2 className="text-xl font-semibold">{product.name}</h2>
  <p className="text-gray-600 mt-2">{product.description}</p>
  <p className="text-2xl font-bold text-green-600 mt-4">
    Rs. {product.price}
  </p>
  <p className="text-sm text-gray-500 mt-2">
    Stock: {product.stock_quantity}
  </p>
  <button 
    onClick={(e) => {
      e.preventDefault(); // Prevent navigation when clicking button
      handleAddToCart(product);
    }}
    className="w-full bg-blue-600 text-white py-2 rounded mt-4 hover:bg-blue-700"
  >
    Add to Cart
  </button>
</Link>
          
        ))}
      </div>
    </div>
  );
}