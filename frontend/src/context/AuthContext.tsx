import { createContext, useContext, useEffect, useState } from "react";
import type { ReactNode } from "react";
import {
  type LoginPayload,
  type RegisterPayload,
  fetchCurrentUser,
  loginUser,
  logoutUser,
  registerUser,
} from "../api";
import type { User } from "../types";

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchCurrentUser()
      .then(setUser)
      .finally(() => setIsLoading(false));
  }, []);

  async function login(payload: LoginPayload) {
    const loggedInUser = await loginUser(payload);
    setUser(loggedInUser);
  }

  async function register(payload: RegisterPayload) {
    const newUser = await registerUser(payload);
    setUser(newUser);
  }

  async function logout() {
    await logoutUser();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
}
