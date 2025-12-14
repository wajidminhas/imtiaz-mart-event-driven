import { Product } from '@/types/product';

const BASE_URL = 'http://localhost:8001';

export async function getAllProducts(): Promise<Product[]> {
  const response = await fetch(`${BASE_URL}/products/`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch products');
  }
  
  return response.json();
}
export async function getProductById(id: number): Promise<Product> {
  const response = await fetch(`${BASE_URL}/products/${id}`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch product');
  }
  
  return response.json();
}