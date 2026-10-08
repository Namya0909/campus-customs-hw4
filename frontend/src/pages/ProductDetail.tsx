import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { fetchProduct, imageUrl } from "../api";
import { usePageContext } from "../context/PageContextProvider";
import type { Product } from "../types";
import "./ProductDetail.css";

export default function ProductDetail() {
  const { productId } = useParams<{ productId: string }>();
  const [product, setProduct] = useState<Product | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { setActiveProduct } = usePageContext();

  useEffect(() => {
    if (!productId) return;
    let cancelled = false;
    setProduct(null);
    setError(null);

    fetchProduct(productId)
      .then((data) => {
        if (!cancelled) setProduct(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load product");
      });

    return () => {
      cancelled = true;
    };
  }, [productId]);

  // Lets the chat widget tell the agent which product page is open, so pronouns like
  // "this"/"it" resolve correctly. Cleared on unmount/navigation so stale context doesn't linger.
  useEffect(() => {
    if (product) {
      setActiveProduct({ product_id: product.product_id, product_title: product.name });
    }
    return () => setActiveProduct(null);
  }, [product, setActiveProduct]);

  if (error) {
    return (
      <div className="product-detail container">
        <p className="product-detail-error">{error}</p>
        <Link to="/products" className="back-link">
          ← Back to products
        </Link>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="product-detail container">
        <p>Loading…</p>
      </div>
    );
  }

  return (
    <div className="product-detail container">
      <Link to="/products" className="back-link">
        ← Back to products
      </Link>

      <div className="product-detail-split">
        <div className="product-detail-image">
          <img src={imageUrl(product.image_url)} alt={product.name} />
        </div>

        <div className="product-detail-info">
          <h1>{product.name}</h1>
          <p className="product-detail-type">{product.garment_type}</p>
          <span className="price-tag price-tag-large">${product.price.toFixed(2)}</span>
          <p className="product-detail-desc">{product.description}</p>

          <div className="product-detail-colors">
            {product.colors.map((color) => (
              <span key={color} className="color-pill">
                {color}
              </span>
            ))}
          </div>

          <h2>Sizes &amp; availability</h2>
          <table className="size-table">
            <thead>
              <tr>
                <th>Size</th>
                <th>In stock</th>
              </tr>
            </thead>
            <tbody>
              {product.inventory.map((item) => (
                <tr key={item.size}>
                  <td>{item.size}</td>
                  <td>
                    <span className={"stock-pill" + (item.quantity === 0 ? " out" : "")}>
                      {item.quantity === 0 ? "Out of stock" : `${item.quantity} in stock`}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
