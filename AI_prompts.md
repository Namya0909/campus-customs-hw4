# Homework 4 — AI Prompt Log

Prompt log for the "vibe coding" portions of Homework 4. For each problem, record the initial prompt, and (if needed) a follow-up prompt along with what was missing from the first attempt.

---

## Problem 1: [Problem Title]

### Initial Prompt
```
[Paste your initial prompt here]
```

### Follow-up Prompt (if needed)
```
[Paste your follow-up prompt here]
```

### What was lacking
[One sentence explaining what was missing/wrong after the first prompt that led to the follow-up]

---

## Problem 2: [Problem Title]

### Initial Prompt
```
[Paste your initial prompt here]
```

### Follow-up Prompt (if needed)
```
[Paste your follow-up prompt here]
```

### What was lacking
[One sentence explaining what was missing/wrong after the first prompt that led to the follow-up]

---

## Problem 3: [Problem Title]

### Initial Prompt
```
[Paste your initial prompt here]
```

### Follow-up Prompt (if needed)
```
[Paste your follow-up prompt here]
```

### What was lacking
[One sentence explaining what was missing/wrong after the first prompt that led to the follow-up]

---

## Problem 9: Usability Improvements

### Initial Prompt
```
Now for Problem 9, we need to implement usability improvements across the site and chatbot
with exactly two for the front end and two for the agent or backend. Before coding, please
provide me with three strong options for the front end and three options for the backend,
explaining what each does and how it benefits either the customer or the business, so I can
review them and choose which specific features to implement. Once I select the final four,
help me write up output/usability.md with what was added and why it helps a Campus Customs
shopper or the store, and then guide me through implementing them cleanly into the running
application.
```

### Follow-up Prompt
```
So, right now, the garment type dropdown pulls raw, unnormalized strings from the database.
This leads to entries like "Hoodie", "Pullover Hoodie", "Hooded Sweatshirt", "Full-Zip Hooded
Sweatshirt", and "Hooded Pullover Sweatshirt", along with similar duplicates for t-shirts,
crewnecks, and jackets. Because of this, choosing "Hoodie" only shows the 5 items labeled
exactly as "Hoodie" instead of all 26 hooded garments. It also makes it hard for the agent to
count categories accurately.

To fix this, add a category normalization layer on both the frontend (Products.tsx) and
backend (backend/tools.py). This layer should map each product's title, description, and raw
type to clear, high-level shopping categories. For example, 'Hoodie' should match any product
with 'hoodie', 'hooded', or 'hood' in its details, so all 26 hooded items are grouped
together. Other products should be sorted into standard categories like 'T-Shirt', 'Crewneck
& Sweatshirt', and 'Jackets & Outerwear'.

Next, update the dropdown menu in Products.tsx to show only these cleaned-up categories. When
someone selects "Hoodie", the counter should update to "26 of 102" and display all 26 matching
products. In backend/tools.py and prompt.md, make sure search_products uses the same keyword
matching for titles, descriptions, and categories, and does not limit results to just 10
items. This way, the chatbot can always find and show all 26 hoodies when customers ask.
```

### What was lacking
The first pass at the search/filter bar (Problem 9's original two frontend picks) filtered the dropdown on the catalogue's raw `garment_type` string with exact equality and capped `search_products` at 10 results, so near-duplicate labels for the same real-world category (e.g. "hoodie" vs. "pullover hoodie" vs. "hooded sweatshirt") were never grouped together — selecting "Hoodie" or asking the chatbot for hoodies only ever surfaced a fraction of what the store actually carried (5–10 of the true 27).

---
