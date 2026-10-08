import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { fetchProducts, imageUrl } from "../api";
import { SHOP_CATEGORIES, categorize } from "../categories";
import type { Product } from "../types";
import "./Products.css";

function totalStockOf(product: Product): number {
  return product.inventory.reduce((sum, i) => sum + i.quantity, 0);
}

export default function Products() {
  const [products, setProducts] = useState<Product[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("");
  const [inStockOnly, setInStockOnly] = useState(false);

  useEffect(() => {
    let cancelled = false;

    fetchProducts()
      .then((data) => {
        if (!cancelled) setProducts(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load products");
      });

    return () => {
      cancelled = true;
    };
  }, []);

  // Fixed, display-order list of the categories actually present in the catalogue — using
  // SHOP_CATEGORIES' own order (not alphabetical) keeps the dropdown in a sensible shopping
  // order (Hoodie, T-Shirt, ...) instead of whatever order the raw data happens to produce.
  const availableCategories = useMemo(() => {
    if (!products) return [];
    const present = new Set(products.map((p) => categorize(p)));
    return SHOP_CATEGORIES.filter((c) => present.has(c));
  }, [products]);

  const filtered = useMemo(() => {
    if (!products) return null;
    const q = query.trim().toLowerCase();
    return products.filter((p) => {
      if (category && categorize(p) !== category) return false;
      if (inStockOnly && totalStockOf(p) === 0) return false;
      if (q && !(p.name.toLowerCase().includes(q) || p.description.toLowerCase().includes(q))) return false;
      return true;
    });
  }, [products, query, category, inStockOnly]);

  const hasActiveFilters = query.trim() !== "" || category !== "" || inStockOnly;

  function clearFilters() {
    setQuery("");
    setCategory("");
    setInStockOnly(false);
  }

  return (
    <div className="products container">
      <h1>Products</h1>
      <p className="products-sub">The full Campus Customs catalogue, pulled straight from inventory.</p>

      {error && <p className="products-error">{error}</p>}
      {!products && !error && <p className="products-loading">Loading catalogue…</p>}

      {products && (
        <div className="products-toolbar">
          <input
            type="search"
            className="products-search"
            placeholder="Search by name or description…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <select className="products-type-select" value={category} onChange={(e) => setCategory(e.target.value)}>
            <option value="">All categories</option>
            {availableCategories.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
          <label className="products-stock-toggle">
            <input type="checkbox" checked={inStockOnly} onChange={(e) => setInStockOnly(e.target.checked)} />
            In stock only
          </label>
          <span className="products-count">
            {filtered?.length ?? 0} of {products.length}
          </span>
          {hasActiveFilters && (
            <button type="button" className="products-clear" onClick={clearFilters}>
              Clear filters
            </button>
          )}
        </div>
      )}

      {filtered && filtered.length === 0 && (
        <p className="products-empty">No products match those filters. Try broadening your search.</p>
      )}

      <div className="product-grid">
        {filtered?.map((product) => {
          const totalStock = totalStockOf(product);
          return (
            <Link to={`/products/${product.product_id}`} key={product.product_id} className="product-card">
              <div className="product-thumb">
                <img src={imageUrl(product.image_url)} alt={product.name} loading="lazy" />
                <span className="price-tag product-thumb-price">${product.price.toFixed(2)}</span>
              </div>
              <div className="product-info">
                <h3>{product.name}</h3>
                <p className="product-desc">{product.description}</p>
                <div className="product-meta">
                  <span className={"stock-pill" + (totalStock === 0 ? " out" : "")}>
                    {totalStock === 0 ? "Out of stock" : `${totalStock} in stock`}
                  </span>
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
