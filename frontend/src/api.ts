import type { ChatHistoryEntry, ChatMessage, ChatReply, PageContext, Product, User } from "./types";

export const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8010";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function parseErrorDetail(res: Response, fallback: string): Promise<string> {
  try {
    const body = await res.json();
    return typeof body?.detail === "string" ? body.detail : fallback;
  } catch {
    return fallback;
  }
}

export interface RegisterPayload {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export async function registerUser(payload: RegisterPayload): Promise<User> {
  const res = await fetch(`${API_BASE_URL}/api/auth/register`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new ApiError(await parseErrorDetail(res, "Could not create account."), res.status);
  }
  return res.json();
}

export async function loginUser(payload: LoginPayload): Promise<User> {
  const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new ApiError(await parseErrorDetail(res, "Could not log in."), res.status);
  }
  return res.json();
}

export async function logoutUser(): Promise<void> {
  await fetch(`${API_BASE_URL}/api/auth/logout`, {
    method: "POST",
    credentials: "include",
  });
}

export async function fetchCurrentUser(): Promise<User | null> {
  const res = await fetch(`${API_BASE_URL}/api/auth/me`, {
    credentials: "include",
  });
  if (!res.ok) return null;
  return res.json();
}

export async function sendChatMessage(
  message: string,
  history: ChatMessage[],
  pageContext: PageContext | null,
): Promise<ChatReply> {
  const res = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    credentials: "include", // so a logged-in session is recognized and this turn gets saved
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, history, page_context: pageContext }),
  });
  if (!res.ok) {
    throw new ApiError(await parseErrorDetail(res, "The assistant couldn't respond. Please try again."), res.status);
  }
  return res.json();
}

export async function fetchChatHistory(): Promise<ChatHistoryEntry[]> {
  const res = await fetch(`${API_BASE_URL}/api/chat/history`, {
    credentials: "include",
  });
  if (!res.ok) return [];
  return res.json();
}

export async function fetchProducts(): Promise<Product[]> {
  const res = await fetch(`${API_BASE_URL}/api/products`);
  if (!res.ok) {
    throw new Error(`Failed to load products (${res.status})`);
  }
  return res.json();
}

export async function fetchProduct(productId: string): Promise<Product> {
  const res = await fetch(`${API_BASE_URL}/api/products/${productId}`);
  if (!res.ok) {
    throw new Error(`Failed to load product ${productId} (${res.status})`);
  }
  return res.json();
}

export function imageUrl(path: string): string {
  return `${API_BASE_URL}${path}`;
}
