# BiasharaIQ Project URL Diagrams

This document maps the key project URLs, route structure, and deployment flow for BiasharaIQ.

---

## 1. Local Development URLs

- Frontend web app: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- FastAPI docs: `http://localhost:8000/docs`
- Swagger/OpenAPI: `http://localhost:8000/docs`
- Redoc API docs: `http://localhost:8000/redoc`

---
ss
## 2. Architecturesddd URL Flowddss

```mermaid
flowchart LR
  User["User / Browser / Mobile App"] -->|HTTP/HTTPS| Frontend["Frontend (Next.js)"]
  Frontend -->|REST API| Backend["Backend (FastAPI)"]
  Backend -->|SQL| Database["PostgreSQL"]
  Backend -->|M-Pesa integration| MPESA["M-Pesa API"]
  Backend -->|AI calls| AI["Google GenAI / Gemini"]
  Frontend -->|Assets / Static| CDN["Static assets + images"]
``` 

---

## 3. Frontend Route Diagram

The frontend serves the application pages and mobile wrapper logic.

```mermaid
flowchart TD
  A["/ (Home / Login)"] --> B["/dashboard"]
  B --> C["/transactions"]
  B --> D["/reports"]
  B --> E["/insights"]
  B --> F["/settings"]
  A --> G["/register"]
  A --> H["/verify-email"]
  B --> I["/pricing"]
  B --> J["/subscription"]
  C --> K["/transactions/import"]
``` 

---

## 4. Backend API URL Diagram

The backend exposes REST endpoints under the main API surface.

```mermaid
flowchart LR
  UI["UI / Frontend"] -->|POST / GET| Auth["/api/auth/*"]
  UI -->|GET| Subscription["/api/subscriptions/*"]
  UI -->|POST / GET| Transactions["/api/transactions/*"]
  UI -->|POST / GET| Payments["/api/payments/*"]
  UI -->|POST| Uploads["/api/uploads/*"]
  UI -->|POST| EmailVerification["/api/email-verification/*"]
  UI -->|POST| Insights["/api/insights/*"]
  UI -->|GET| Health["/api/health-check"]
```

---

## 5. Deployment URL Patterns

When deployed, the app is typically hosted at a public domain such as:

- `https://app.example.com` for the frontend
- `https://api.example.com` for the backend
- `https://app.example.com/docs` for API documentation if served through the backend domain

For Docker / ECS deployments, the runtime URLs are driven by the load balancer, ingress, and DNS records.

---

## 6. Mobile Build URL Flow

For Android mobile packaging, the frontend bundles into a Capacitor app.

```mermaid
flowchart TD
  UserDevice["Android Device"] -->|WebView| Capacitor["Capacitor Android Wrapper"]
  Capacitor -->|HTTP/HTTPS| Frontend["Next.js Web App / Built Output"]
  Frontend -->|REST API| Backend["FastAPI API"]
```

---

## Notes

- Update this file whenever new route groups or deployment domains are added.
- Use the backend `/docs` endpoint to verify generated API routes against the implemented FastAPI routes.
- If the app is served from a monorepo deployment, replace the frontend and backend domains with the correct application hostnames.
