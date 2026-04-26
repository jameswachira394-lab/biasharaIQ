# BiasharaIQ API Reference

Base URL: `http://localhost:8000`
Interactive docs: `http://localhost:8000/docs`

All protected endpoints require:
```
Authorization: Bearer <JWT_TOKEN>
```

---

## Authentication

### POST `/auth/register`
Register a new user and business.

**Body:**
```json
{
  "email": "jane@shop.co.ke",
  "password": "mypassword",
  "business_name": "Jane's Shop",
  "owner_name": "Jane Wanjiku",
  "phone": "+254712345678",
  "business_type": "Retail"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": { "id": 1, "email": "...", "business_name": "..." }
}
```

---

### POST `/auth/login`
Login with email and password.

**Body:**
```json
{ "email": "jane@shop.co.ke", "password": "mypassword" }
```

---

## Dashboard

### GET `/dashboard/` 🔒
Returns the full financial snapshot for the dashboard.

**Response:**
```json
{
  "business_name": "Jane's Shop",
  "metrics": {
    "all_time": { "income": 0, "expenses": 0, "profit": 0 },
    "this_month": { "income": 0, "expenses": 0, "profit": 0, "profit_margin": 0 },
    "cash_flow": {
      "daily_spending_rate": 0,
      "survival_days": null,
      "risk_level": "safe",
      "message": "..."
    },
    "expense_breakdown": [{ "category": "Rent", "amount": 15000, "percentage": 35.0 }],
    "income_breakdown": [...]
  },
  "insights": [{ "type": "...", "severity": "warning", "message": "...", "icon": "⚠️" }],
  "weekly_trend": [{ "week": "Apr 01", "income": 0, "expenses": 0, "profit": 0 }]
}
```

---

## Transactions

### GET `/transactions/` 🔒
List transactions with optional filters.

| Query Param | Type | Description |
|-------------|------|-------------|
| `type` | string | `income` or `expense` |
| `category` | string | Filter by category name |
| `start_date` | datetime | ISO 8601 start date |
| `end_date` | datetime | ISO 8601 end date |
| `limit` | int | Max results (default 50, max 200) |
| `offset` | int | Pagination offset |

**Response:**
```json
{ "total": 142, "items": [...] }
```

---

### POST `/transactions/` 🔒
Create a new transaction.

```json
{
  "amount": 5000,
  "type": "income",
  "category": "Product Sales",
  "date": "2026-04-25T10:00:00",
  "description": "Morning sales"
}
```

---

### PUT `/transactions/{id}` 🔒
Update a transaction.

### DELETE `/transactions/{id}` 🔒
Delete a transaction.

---

## Insights

### GET `/insights/` 🔒
Returns current rule-based financial insights.

### GET `/insights/history?limit=20` 🔒
Returns previously saved insights from the database.

---

## AI Agent

### POST `/ai/chat` 🔒
Chat with the BiasharaIQ AI Advisor.

```json
{
  "message": "Why am I losing money?",
  "history": [
    { "role": "user", "content": "Hello" },
    { "role": "assistant", "content": "Hi! How can I help?" }
  ]
}
```

**Response:**
```json
{ "response": "Based on your data, your expenses exceeded income by KES 12,400 this month..." }
```

---

## Reports

### GET `/reports/monthly` 🔒
Current month summary with breakdowns.

### GET `/reports/weekly-trend?weeks=8` 🔒
Week-by-week income/expense/profit data.

---

## Categories

### GET `/categories/?type=expense` 🔒
List all categories. Optionally filter by type (`income` or `expense`).

### POST `/categories/` 🔒
Create a custom category.
```json
{ "name": "MPESA Charges", "type": "expense" }
```

### DELETE `/categories/{id}` 🔒
Delete a custom category (default categories cannot be deleted).

---

## Profile

### GET `/profile/` 🔒
Get the current user's profile.

### PUT `/profile/` 🔒
Update business profile.
```json
{ "business_name": "New Name", "phone": "+254..." }
```

---

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad request / validation error |
| 401 | Unauthorized – invalid or expired token |
| 404 | Resource not found |
| 422 | Unprocessable entity – schema mismatch |
| 500 | Internal server error |
