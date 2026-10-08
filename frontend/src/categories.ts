/**
 * Normalizes the catalogue's raw, inconsistent garment_type strings (e.g. "hoodie",
 * "pullover hoodie", "hooded sweatshirt", "full-zip hooded sweatshirt" are all the same
 * thing to a shopper) into four clean, high-level shopping categories.
 *
 * Kept in sync by hand with backend/categories.py's `categorize()` — same rules, same
 * labels — since the frontend and backend don't share code. If you change one, change
 * the other.
 */

export const SHOP_CATEGORIES = ["Hoodie", "T-Shirt", "Crewneck & Sweatshirt", "Jackets & Outerwear"] as const;

export type ShopCategory = (typeof SHOP_CATEGORIES)[number];

interface CategorizableFields {
  name: string;
  description: string;
  garment_type: string;
}

const HOOD_RE = /\bhood(ie|ed)?\b/;
const JACKET_RE = /\bjacket\b/;
const SWEATSHIRT_RE = /\b(crewneck|crew-neck|sweatshirt|sweater|mockneck|quarter-zip|pullover)\b/;
const TSHIRT_HINT_RE = /\b(t-shirt|tshirt)\b/;

export function categorize(product: CategorizableFields): ShopCategory {
  const text = `${product.name} ${product.description} ${product.garment_type}`.toLowerCase();

  if (HOOD_RE.test(text)) return "Hoodie";
  if (JACKET_RE.test(text)) return "Jackets & Outerwear";
  // "sweatshirt" itself contains the substring "tshirt" ("swea" + "tshirt"), so this
  // exclusion check must use a word-bounded pattern, not a plain substring check.
  if (SWEATSHIRT_RE.test(text) && !TSHIRT_HINT_RE.test(text)) return "Crewneck & Sweatshirt";
  return "T-Shirt";
}
