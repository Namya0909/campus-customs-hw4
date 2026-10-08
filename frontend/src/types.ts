export interface User {
  id: number;
  first_name: string | null;
  last_name: string | null;
  name: string;
  email: string;
}

export interface InventorySize {
  size: string;
  quantity: number;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ProductCard {
  product_id: string;
  name: string;
  price: number;
  image_url: string;
  garment_type: string;
  in_stock: boolean;
}

export interface ChatReply {
  message: string;
  products: ProductCard[];
}

export interface PageContext {
  product_id: string;
  product_title: string;
}

export interface ChatHistoryEntry {
  role: "user" | "assistant";
  content: string;
  products: ProductCard[];
}

export interface Product {
  product_id: string;
  name: string;
  garment_type: string;
  description: string;
  colors: string[];
  search_tags: string[];
  image_url: string;
  price: number;
  inventory: InventorySize[];
}
