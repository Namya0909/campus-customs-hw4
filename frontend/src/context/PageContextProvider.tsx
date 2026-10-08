import { createContext, useContext, useMemo, useState } from "react";
import type { ReactNode } from "react";
import type { PageContext as PageContextValue } from "../types";

interface PageContextApi {
  activeProduct: PageContextValue | null;
  setActiveProduct: (value: PageContextValue | null) => void;
}

const PageContext = createContext<PageContextApi | undefined>(undefined);

export function PageContextProvider({ children }: { children: ReactNode }) {
  const [activeProduct, setActiveProduct] = useState<PageContextValue | null>(null);
  const value = useMemo(() => ({ activeProduct, setActiveProduct }), [activeProduct]);
  return <PageContext.Provider value={value}>{children}</PageContext.Provider>;
}

export function usePageContext(): PageContextApi {
  const ctx = useContext(PageContext);
  if (!ctx) {
    throw new Error("usePageContext must be used within a PageContextProvider");
  }
  return ctx;
}
