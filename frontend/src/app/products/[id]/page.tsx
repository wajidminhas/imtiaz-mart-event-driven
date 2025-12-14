

'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { getProductById } from '@/services/productService';
import { Product } from '@/types/product';
import { useCart } from '@/context/CartContext';
import Link from 'next/link';

export default function ProductDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const { addToCart } = useCart();
  
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchProduct() {
      try {
        const id = Number(params.id);
        const data = await getProductById(id);
        setProduct(data);
      } catch (err) {
        setError('Failed to load product');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchProduct();
  }, [params.id]);

  const handleAddToCart = () => {
    if (product) {
      addToCart(product);
      alert(`${product.name} added to cart!`);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto p-8">
        <p className="text-xl">Loading product...</p>
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="container mx-auto p-8">
        <p className="text-xl text-red-600">Product not found</p>
        <Link href="/products" className="text-blue-600 hover:underline mt-4 inline-block">
          Back to Products
        </Link>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-8">
      <Link href="/products" className="text-blue-600 hover:underline mb-4 inline-block">
        ← Back to Products
      </Link>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-4">
        {/* Product Image Placeholder */}
        <div className="bg-gray-200 rounded-lg flex items-center justify-center h-96">
          <span className="text-gray-500 text-xl">Product Image</span>
        </div>

        {/* Product Details */}
        <div>
          <h1 className="text-4xl font-bold mb-4">{product.name}</h1>
          
          <div className="mb-6">
            <span className={`inline-block px-3 py-1 rounded text-sm ${
              product.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {product.is_active ? 'In Stock' : 'Out of Stock'}
            </span>
          </div>

          <p className="text-gray-700 text-lg mb-6">{product.description}</p>

          <div className="mb-6">
            <p className="text-4xl font-bold text-green-600">
              Rs. {product.price}
            </p>
          </div>

          <div className="mb-6">
            <p className="text-gray-600">
              Available Stock: <span className="font-semibold">{product.stock_quantity}</span>
            </p>
          </div>

          <button
            onClick={handleAddToCart}
            disabled={!product.is_active || product.stock_quantity === 0}
            className={`w-full py-3 rounded-lg font-semibold text-lg ${
              product.is_active && product.stock_quantity > 0
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            {product.is_active && product.stock_quantity > 0 
              ? 'Add to Cart' 
              : 'Out of Stock'}
          </button>

          <div className="mt-8 pt-8 border-t">
            <h3 className="font-semibold mb-2">Product Information</h3>
            <div className="text-sm text-gray-600 space-y-1">
              <p>Product ID: {product.id}</p>
              <p>Added: {new Date(product.created_at).toLocaleDateString()}</p>
              <p>Last Updated: {new Date(product.updated_at).toLocaleDateString()}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}