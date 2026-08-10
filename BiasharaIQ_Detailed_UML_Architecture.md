# BiasharaIQ --- Detailed UML & System Architecture Documentation

## 1. Document Purpose

This document defines the UML, database, system architecture, sequence
flows, mobile architecture, and deployment architecture for the
**BiasharaIQ Financial Intelligence Platform**.

BiasharaIQ is a financial intelligence platform designed for Kenyan
SMEs. It combines:

-   Business transaction tracking
-   Income and expense management
-   AI-assisted transaction categorization
-   Financial analytics and insights
-   M-Pesa payment integration
-   Subscription management
-   Financial document imports
-   AI-assisted financial chat/analysis
-   Web access through Next.js
-   Android packaging through Capacitor
-   PostgreSQL persistence
-   Docker-based development and AWS deployment

This document is based on the supplied project README, SQLAlchemy
models, and PostgreSQL schema.

------------------------------------------------------------------------

# 2. System Overview

BiasharaIQ follows a decoupled client-server architecture.

``` text
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
│                                                                 │
│       Next.js Web Application       Capacitor Android App       │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTPS / REST
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                       APPLICATION LAYER                         │
│                                                                 │
│                         FastAPI API                             │
│                              │                                  │
│      ┌─────────────┬─────────┼─────────┬──────────────┐         │
│      │             │         │         │              │         │
│ Authentication  Transactions Payments  AI          Imports      │
│      │             │         │         │              │         │
└──────┼─────────────┼─────────┼─────────┼──────────────┼─────────┘
       │             │         │         │              │
       └─────────────┴────┬────┴─────────┴──────────────┘
                          ▼
                 ┌─────────────────┐
                 │   PostgreSQL    │
                 └─────────────────┘

External integrations:

FastAPI ───────────────► M-Pesa API
FastAPI ───────────────► Google Gemini / GenAI
Import Service ────────► S3 / Cloudinary
```

------------------------------------------------------------------------

# 3. Technology Stack

## Frontend

-   Next.js 14
-   React 18
-   Tailwind CSS
-   Recharts
-   Capacitor for Android packaging

## Backend

-   Python
-   FastAPI
-   SQLAlchemy ORM
-   Authentication middleware
-   Subscription guards
-   Business services

## Database

-   PostgreSQL

## AI

-   Google GenAI / Gemini
-   Rule-based fallback for categorization

## Payments

-   M-Pesa API
-   STK Push
-   Callback handling

## Infrastructure

-   Docker
-   Docker Compose
-   Terraform
-   AWS ECS
-   AWS RDS

## Storage

-   Cloudinary and/or Amazon S3

------------------------------------------------------------------------

# 4. Main System Actors

## SME Business User

The primary user of BiasharaIQ.

The user can:

-   Register
-   Log in
-   Verify an account
-   Manage business information
-   Record transactions
-   Import transactions
-   View dashboards
-   View reports
-   View financial insights
-   Use AI functionality
-   Manage categories
-   Subscribe to a paid plan
-   Make M-Pesa payments
-   Upload financial documents
-   Access the application from Android

## Administrator

An administrative actor may have access to system-level management and
reporting capabilities depending on the implemented authorization model.

------------------------------------------------------------------------

# 5. UML Use Case Diagram

``` mermaid
flowchart LR
    User["SME Business User"]
    Admin["Administrator"]

    subgraph BI["BiasharaIQ Financial Intelligence Platform"]

        UC1(("Register Account"))
        UC2(("Login"))
        UC3(("Verify Email"))

        UC4(("View Dashboard"))
        UC5(("Record Transaction"))
        UC6(("Import Transactions"))
        UC7(("Categorize Transaction"))
        UC8(("View Reports"))
        UC9(("View Financial Insights"))

        UC10(("Manage Subscription"))
        UC11(("Make M-Pesa Payment"))

        UC12(("Upload Financial Data"))
        UC13(("Manage Account Settings"))
        UC14(("Access Mobile App"))
        UC15(("Use AI Chat"))
    end

    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    User --> UC5
    User --> UC6
    User --> UC8
    User --> UC9
    User --> UC10
    User --> UC11
    User --> UC12
    User --> UC13
    User --> UC14
    User --> UC15

    UC5 -.->|uses| UC7
    UC6 -.->|uses| UC7
    UC9 -.->|uses| UC7

    Admin --> UC4
    Admin --> UC8
```

------------------------------------------------------------------------

# 6. Use Case Descriptions

## 6.1 Register Account

**Actor:** SME Business User

**Purpose:** Create a BiasharaIQ account.

**Main flow:**

1.  User opens the registration page.
2.  User enters business and account details.
3.  Backend validates the information.
4.  User account is created.
5.  Default categories can be initialized.
6.  Verification information is generated.
7.  User verifies their account.

------------------------------------------------------------------------

## 6.2 Login

**Actor:** SME Business User

**Purpose:** Authenticate an existing user.

**Main flow:**

1.  User submits email and password.
2.  Backend validates credentials.
3.  Authentication succeeds.
4.  User receives an authenticated session/token.
5.  User accesses the dashboard.

------------------------------------------------------------------------

## 6.3 Record Transaction

**Actor:** SME Business User

**Purpose:** Record income or expense.

A transaction contains:

-   Amount
-   Type
-   Category
-   Date
-   Description
-   Source
-   Status

Supported transaction types:

``` text
income
expense
```

Supported sources include:

``` text
manual
mpesa
bank
csv
invoice
```

------------------------------------------------------------------------

## 6.4 Import Transactions

**Actor:** SME Business User

The user uploads a financial document such as:

-   M-Pesa statement
-   Bank statement
-   CSV
-   Invoice

The system stores the document, parses it, creates transactions,
categorizes them, and tracks the import batch.

------------------------------------------------------------------------

## 6.5 Generate Financial Insights

The system analyzes transaction data and produces insights such as:

-   Warnings
-   Tips
-   Trends
-   Alerts

Insight severity:

``` text
info
warning
critical
```

------------------------------------------------------------------------

## 6.6 Manage Subscription

The user can manage their subscription plan.

Current user plans:

``` text
FREE
PRO
```

Subscription states:

``` text
active
expired
pending
```

------------------------------------------------------------------------

## 6.7 Make M-Pesa Payment

The user can pay for a subscription through M-Pesa.

The payment process uses:

-   Phone number
-   Amount
-   Checkout request ID
-   Merchant request ID
-   M-Pesa receipt
-   Payment status

------------------------------------------------------------------------

# 7. UML Component / System Architecture Diagram

``` mermaid
flowchart TB

    User["SME Business User"]

    subgraph Client["Client Layer"]

        Web["Next.js 14<br/>React 18<br/>Tailwind CSS"]

        Android["Android App<br/>Capacitor"]

        Charts["Recharts<br/>Analytics Visualization"]
    end

    subgraph API["Application Layer"]

        FastAPI["FastAPI REST API"]

        Auth["Authentication"]

        Middleware["Middleware<br/>Auth / Subscription Guards"]

        Routes["API Routes"]

        subgraph Services["Business Services"]

            TransactionService["Transaction Service"]
            CategoryService["Category Service"]
            AIService["AI Categorization / Chat"]
            PaymentService["M-Pesa Payment Service"]
            SubscriptionService["Subscription Service"]
            InsightService["Financial Insights Service"]
            ParsingService["Data Parsing / Import Service"]
        end

        ORM["SQLAlchemy ORM"]
    end

    subgraph External["External Services"]

        Gemini["Google GenAI / Gemini"]
        MPESA["M-Pesa API"]
        Storage["Cloudinary / Amazon S3"]
    end

    DB[("PostgreSQL Database")]

    User --> Web
    User --> Android

    Web --> Charts
    Web -->|REST / HTTPS| FastAPI
    Android -->|REST / HTTPS| FastAPI

    FastAPI --> Middleware
    Middleware --> Auth
    FastAPI --> Routes

    Routes --> TransactionService
    Routes --> CategoryService
    Routes --> AIService
    Routes --> PaymentService
    Routes --> SubscriptionService
    Routes --> InsightService
    Routes --> ParsingService

    TransactionService --> ORM
    CategoryService --> ORM
    AIService --> ORM
    PaymentService --> ORM
    SubscriptionService --> ORM
    InsightService --> ORM
    ParsingService --> ORM

    ORM --> DB

    AIService -->|AI Requests| Gemini
    PaymentService -->|STK Push / Callbacks| MPESA
    ParsingService -->|File Storage| Storage
```

------------------------------------------------------------------------

# 8. Application Layer Responsibilities

## Authentication

Responsible for:

-   Registration
-   Login
-   Password handling
-   Email verification
-   User authentication
-   Account status

## Transaction Service

Responsible for:

-   Creating transactions
-   Updating transactions
-   Deleting transactions
-   Listing transactions
-   Filtering transactions
-   Tracking transaction sources
-   Tracking transaction status

## Category Service

Responsible for:

-   User categories
-   Global/default categories
-   Income categories
-   Expense categories

## Payment Service

Responsible for:

-   Creating payment records
-   Initiating M-Pesa STK Push
-   Handling M-Pesa callbacks
-   Updating payment status
-   Storing M-Pesa receipts

## Subscription Service

Responsible for:

-   FREE and PRO plans
-   Subscription activation
-   Subscription expiry
-   Subscription status
-   Transaction and AI usage limits

## Insight Service

Responsible for:

-   Reading transaction data
-   Generating financial insights
-   Storing insights
-   Tracking whether insights have been read

## Import / Parsing Service

Responsible for:

-   Uploading financial documents
-   Storing documents
-   Parsing documents
-   Creating transaction records
-   Grouping imported transactions into batches

## AI Service

Responsible for:

-   Transaction categorization
-   Financial analysis
-   AI-generated insights
-   AI chat
-   Rule-based fallback when AI is unavailable

------------------------------------------------------------------------

# 9. UML Class Diagram

The following class diagram represents the domain model from the
supplied SQLAlchemy implementation.

``` mermaid
classDiagram

    class User {
        +Integer id
        +String email
        +String password_hash
        +String business_name
        +String owner_name
        +String phone
        +String business_type
        +String currency
        +UserPlan plan
        +SubscriptionStatus subscription_status
        +DateTime subscription_start
        +DateTime subscription_end
        +Integer monthly_transaction_count
        +Integer ai_queries_count
        +DateTime ai_queries_reset_date
        +DateTime created_at
        +Boolean is_active
        +Boolean is_verified
        +String verification_code
        +DateTime verification_expires_at
    }

    class Transaction {
        +Integer id
        +Integer user_id
        +Float amount
        +TransactionType type
        +String category
        +DateTime date
        +Text description
        +String source
        +String import_batch_id
        +String status
        +DateTime created_at
        +DateTime updated_at
    }

    class Category {
        +Integer id
        +Integer user_id
        +String name
        +TransactionType type
        +String icon
        +Boolean is_default
    }

    class Subscription {
        +Integer id
        +Integer user_id
        +String plan
        +Float amount
        +String status
        +DateTime started_at
        +DateTime expires_at
    }

    class Payment {
        +Integer id
        +Integer user_id
        +String phone_number
        +Float amount
        +String status
        +String mpesa_receipt
        +String checkout_request_id
        +String merchant_request_id
        +DateTime created_at
    }

    class UploadedDocument {
        +Integer id
        +Integer user_id
        +String filename
        +String file_type
        +String storage_url
        +DateTime parsed_at
        +Integer transaction_count
        +String batch_id
        +String status
        +Text summary
        +DateTime created_at
    }

    class Insight {
        +Integer id
        +Integer user_id
        +String type
        +Text message
        +String severity
        +DateTime timestamp
        +Boolean is_read
    }

    class ChatMessage {
        +Integer id
        +Integer user_id
        +String role
        +Text content
        +DateTime created_at
    }

    class DefaultCategory {
        +Integer id
        +String name
        +String type
        +String color
        +String icon
    }

    class UserPlan {
        <<enumeration>>
        FREE
        PRO
    }

    class SubscriptionStatus {
        <<enumeration>>
        active
        expired
        pending
    }

    class TransactionType {
        <<enumeration>>
        income
        expense
    }

    User "1" --> "0..*" Transaction : owns
    User "1" --> "0..*" Category : creates
    User "1" --> "0..*" Subscription : has
    User "1" --> "0..*" Payment : makes
    User "1" --> "0..*" UploadedDocument : uploads
    User "1" --> "0..*" Insight : receives
    User "1" --> "0..*" ChatMessage : sends

    Category "1" --> "0..*" Transaction : categorizes
    UploadedDocument "1" --> "0..*" Transaction : imports

    User --> UserPlan : has
    User --> SubscriptionStatus : has
    Transaction --> TransactionType : uses
    Category --> TransactionType : uses
```

------------------------------------------------------------------------

# 10. Important Class Diagram Accuracy Notes

The diagram contains two relationships that are currently **logical
rather than physical database foreign-key relationships**.

## 10.1 Transaction → Category

Current implementation:

``` python
category = Column(String, nullable=False)
```

There is no:

``` python
category_id = Column(Integer, ForeignKey("categories.id"))
```

Therefore:

``` text
Category ───── categorizes ───── Transaction
```

is a logical relationship.

If you want a strict relational implementation, a future design could
use:

``` text
transactions.category_id
        ↓
categories.id
```

------------------------------------------------------------------------

## 10.2 UploadedDocument → Transaction

The current implementation uses:

``` text
UploadedDocument.batch_id
Transaction.import_batch_id
```

The two fields logically associate imported transactions with their
source upload.

There is currently no direct foreign key.

------------------------------------------------------------------------

# 11. Database / ER Diagram

``` mermaid
erDiagram

    USERS ||--o{ TRANSACTIONS : owns
    USERS ||--o{ CATEGORIES : creates
    USERS ||--o{ SUBSCRIPTIONS : has
    USERS ||--o{ PAYMENTS : makes
    USERS ||--o{ UPLOADED_DOCUMENTS : uploads
    USERS ||--o{ INSIGHTS : receives
    USERS ||--o{ CHAT_MESSAGES : sends

    USERS {
        int id PK
        varchar email UK
        varchar password_hash
        varchar business_name
        varchar owner_name
        varchar phone
        varchar business_type
        varchar currency
        varchar plan
        varchar subscription_status
        timestamp subscription_start
        timestamp subscription_end
        int monthly_transaction_count
        int ai_queries_count
        timestamp ai_queries_reset_date
        boolean is_active
        boolean is_verified
        varchar verification_code
        timestamp verification_expires_at
        timestamp created_at
    }

    TRANSACTIONS {
        int id PK
        int user_id FK
        decimal amount
        varchar type
        varchar category
        timestamp date
        text description
        varchar source
        varchar import_batch_id
        varchar status
        timestamp created_at
        timestamp updated_at
    }

    CATEGORIES {
        int id PK
        int user_id FK
        varchar name
        varchar type
        varchar icon
        boolean is_default
    }

    SUBSCRIPTIONS {
        int id PK
        int user_id FK
        varchar plan
        decimal amount
        varchar status
        timestamp started_at
        timestamp expires_at
    }

    PAYMENTS {
        int id PK
        int user_id FK
        varchar phone_number
        decimal amount
        varchar status
        varchar mpesa_receipt
        varchar checkout_request_id UK
        varchar merchant_request_id
        timestamp created_at
    }

    UPLOADED_DOCUMENTS {
        int id PK
        int user_id FK
        varchar filename
        varchar file_type
        varchar storage_url
        timestamp parsed_at
        int transaction_count
        varchar batch_id UK
        varchar status
        text summary
        timestamp created_at
    }

    INSIGHTS {
        int id PK
        int user_id FK
        varchar type
        text message
        varchar severity
        timestamp timestamp
        boolean is_read
    }

    CHAT_MESSAGES {
        int id PK
        int user_id FK
        varchar role
        text content
        timestamp created_at
    }
```

------------------------------------------------------------------------

# 12. Entity Relationship Summary

## User

The `User` is the central entity.

A single user can have:

``` text
User
 ├── many Transactions
 ├── many Categories
 ├── many Subscriptions
 ├── many Payments
 ├── many UploadedDocuments
 ├── many Insights
 └── many ChatMessages
```

## Transaction

A transaction belongs to one user.

It records:

-   Income or expense
-   Amount
-   Category
-   Date
-   Description
-   Source
-   Import batch
-   Status

## Category

Categories distinguish income and expense classifications.

Examples:

``` text
Income:
- Sales
- Services
- Loans Received
- Other Income

Expenses:
- Stock / Inventory
- Rent
- Salaries
- Transport
- Utilities
- Marketing
- Loan Repayment
- Equipment
- Other Expenses
```

## Subscription

A subscription belongs to a user and records:

-   Plan
-   Amount
-   Status
-   Start date
-   Expiry date

## Payment

A payment belongs to a user and records M-Pesa payment information.

## UploadedDocument

An uploaded document represents imported financial data.

Supported types include:

``` text
mpesa
bank
csv
invoice
```

## Insight

An insight is a financial recommendation, warning, trend, or alert
generated for a user.

## ChatMessage

The SQL schema contains an AI chat history table.

It stores:

``` text
user
role
content
created_at
```

The role is either:

``` text
user
assistant
```

------------------------------------------------------------------------

# 13. Transaction + AI Categorization Sequence Diagram

``` mermaid
sequenceDiagram

    actor User
    participant UI as Next.js Frontend
    participant API as FastAPI
    participant TS as Transaction Service
    participant AI as Gemini / AI Service
    participant DB as PostgreSQL

    User->>UI: Enter transaction
    UI->>API: POST /api/transactions
    API->>TS: Create transaction

    TS->>AI: Request categorization
    AI->>AI: Analyze transaction

    AI-->>TS: Category + confidence

    TS->>DB: Save transaction + category
    DB-->>TS: Transaction saved

    TS-->>API: Transaction result
    API-->>UI: Return transaction
    UI-->>User: Display categorized transaction
```

------------------------------------------------------------------------

# 14. AI Categorization Fallback

BiasharaIQ supports a rule-based fallback.

``` mermaid
flowchart LR

    Transaction["New Transaction"]

    Decision{"AI Available?"}

    AI["Google Gemini"]

    Rules["Rule-Based<br/>Categorization"]

    Category["Transaction Category"]

    Transaction --> Decision

    Decision -->|Yes| AI
    Decision -->|No| Rules

    AI --> Category
    Rules --> Category
```

This allows transaction categorization to continue when the external AI
service is unavailable.

------------------------------------------------------------------------

# 15. Transaction Import Sequence Diagram

``` mermaid
sequenceDiagram

    actor User
    participant Frontend as Next.js
    participant API as FastAPI
    participant Import as Import Service
    participant Storage as S3 / Cloudinary
    participant DB as PostgreSQL
    participant AI as Gemini

    User->>Frontend: Upload financial document

    Frontend->>API: POST upload
    API->>Import: Process document

    Import->>Storage: Store uploaded file
    Storage-->>Import: storage_url

    Import->>Import: Parse document

    Import->>DB: Create UploadedDocument
    DB-->>Import: Document saved

    loop For each transaction
        Import->>AI: Categorize transaction
        AI-->>Import: Category
        Import->>DB: Create Transaction
    end

    Import->>DB: Update transaction_count
    Import->>DB: Update document status

    API-->>Frontend: Import result
    Frontend-->>User: Display imported transactions
```

------------------------------------------------------------------------

# 16. AI Financial Insight Sequence Diagram

``` mermaid
sequenceDiagram

    actor User
    participant UI as Next.js
    participant API as FastAPI
    participant Insight as Insight Service
    participant AI as Gemini
    participant DB as PostgreSQL

    User->>UI: Request financial insights

    UI->>API: GET insights
    API->>Insight: Generate / retrieve insights

    Insight->>DB: Read user transactions
    DB-->>Insight: Transaction data

    Insight->>AI: Analyze financial data
    AI-->>Insight: Financial recommendations

    Insight->>DB: Save Insight
    DB-->>Insight: Insight stored

    Insight-->>API: Return insights
    API-->>UI: Insights
    UI-->>User: Display financial insights
```

------------------------------------------------------------------------

# 17. M-Pesa Subscription Payment Sequence

``` mermaid
sequenceDiagram

    actor User
    participant UI as Next.js
    participant API as FastAPI
    participant Payment as Payment Service
    participant MPESA as M-Pesa API
    participant DB as PostgreSQL

    User->>UI: Select PRO subscription

    UI->>API: Initiate payment
    API->>Payment: Create payment

    Payment->>DB: Save pending Payment

    Payment->>MPESA: STK Push
    MPESA-->>User: Payment prompt

    User->>MPESA: Confirm payment

    MPESA->>API: Payment callback

    API->>Payment: Process callback

    Payment->>DB: Update Payment = completed

    Payment->>DB: Create / activate Subscription

    API-->>UI: Payment successful
    UI-->>User: PRO activated
```

------------------------------------------------------------------------

# 18. Mobile Application Architecture

BiasharaIQ uses Capacitor to package the frontend for Android.

``` mermaid
flowchart TB

    User["Business User"]

    Android["Android Device"]

    Capacitor["Capacitor Android Wrapper"]

    Next["Next.js Application"]

    API["FastAPI REST API"]

    DB[("PostgreSQL")]

    User --> Android
    Android --> Capacitor
    Capacitor --> Next

    Next -->|HTTPS REST API| API
    API --> DB
```

The Android application uses the same backend API as the web
application.

This means:

``` text
Web App ────────┐
                ├──► FastAPI ───► PostgreSQL
Android App ────┘
```

There is no requirement for a separate Android backend.

------------------------------------------------------------------------

# 19. AWS Deployment Architecture

The README specifies Docker, Terraform, ECS, and RDS.

``` mermaid
flowchart TB

    Developer["Developer"]

    Terraform["Terraform"]

    subgraph AWS["AWS Cloud"]

        subgraph ECS["Amazon ECS"]

            Frontend["Frontend Container<br/>Next.js"]

            Backend["Backend Container<br/>FastAPI"]
        end

        RDS[("Amazon RDS<br/>PostgreSQL")]

        LB["Load Balancer"]

        Secrets["Environment Variables<br/>/ Secrets"]
    end

    MPESA["M-Pesa API"]
    Gemini["Google Gemini API"]

    Developer --> Terraform

    Terraform --> ECS
    Terraform --> RDS
    Terraform --> LB

    LB --> Frontend
    LB --> Backend

    Frontend --> Backend
    Backend --> RDS

    Backend --> MPESA
    Backend --> Gemini

    Secrets --> Backend
```

------------------------------------------------------------------------

# 20. Complete BiasharaIQ Architecture

This is the high-level architecture suitable for a project presentation.

``` mermaid
flowchart TB

    User["SME Business User"]

    subgraph Clients["Client Applications"]

        Web["Web Application<br/>Next.js + React"]

        Mobile["Android Application<br/>Capacitor"]
    end

    subgraph AWS["AWS Cloud"]

        subgraph ECS["Amazon ECS"]

            API["FastAPI Backend"]

            Auth["Authentication"]

            Transaction["Transaction Management"]

            Category["Category Management"]

            Payment["Payment Service"]

            Subscription["Subscription Service"]

            AIService["AI Categorization / Chat"]

            Insight["Financial Insights"]

            Import["Transaction Import"]

        end

        DB[("Amazon RDS<br/>PostgreSQL")]
    end

    Gemini["Google GenAI / Gemini"]
    MPESA["Safaricom M-Pesa API"]
    Storage["Cloudinary / Amazon S3"]

    User --> Web
    User --> Mobile

    Web -->|HTTPS / REST| API
    Mobile -->|HTTPS / REST| API

    API --> Auth
    API --> Transaction
    API --> Category
    API --> Payment
    API --> Subscription
    API --> AIService
    API --> Insight
    API --> Import

    Transaction --> DB
    Category --> DB
    Payment --> DB
    Subscription --> DB
    AIService --> DB
    Insight --> DB
    Import --> DB
    Auth --> DB

    AIService --> Gemini
    Payment --> MPESA
    Import --> Storage
```

------------------------------------------------------------------------

# 21. Project URL Architecture

## Local Development

Frontend:

``` text
http://localhost:3000
```

Backend:

``` text
http://localhost:8000
```

FastAPI documentation:

``` text
http://localhost:8000/docs
```

Swagger/OpenAPI:

``` text
http://localhost:8000/docs
```

ReDoc:

``` text
http://localhost:8000/redoc
```

------------------------------------------------------------------------

# 22. Frontend Route Structure

The frontend route structure supplied for BiasharaIQ is:

``` mermaid
flowchart TD

    A["/ Home / Login"]

    A --> B["/dashboard"]

    B --> C["/transactions"]
    B --> D["/reports"]
    B --> E["/insights"]
    B --> F["/settings"]
    B --> I["/pricing"]
    B --> J["/subscription"]

    A --> G["/register"]
    A --> H["/verify-email"]

    C --> K["/transactions/import"]
```

------------------------------------------------------------------------

# 23. Backend API Structure

The backend exposes REST API groups.

``` mermaid
flowchart LR

    UI["Frontend / Mobile UI"]

    UI --> Auth["/api/auth/*"]
    UI --> Subscription["/api/subscriptions/*"]
    UI --> Transactions["/api/transactions/*"]
    UI --> Payments["/api/payments/*"]
    UI --> Uploads["/api/uploads/*"]
    UI --> EmailVerification["/api/email-verification/*"]
    UI --> Insights["/api/insights/*"]
    UI --> Health["/api/health-check"]
```

------------------------------------------------------------------------

# 24. Recommended Backend API Responsibilities

  API Group                     Responsibility
  ----------------------------- -------------------------------------
  `/api/auth/*`                 Registration, login, authentication
  `/api/subscriptions/*`        Subscription management
  `/api/transactions/*`         Transaction CRUD and querying
  `/api/payments/*`             M-Pesa and payment processing
  `/api/uploads/*`              Financial document uploads
  `/api/email-verification/*`   Account verification
  `/api/insights/*`             Financial insights
  `/api/health-check`           Backend health monitoring

The exact implemented routes should always be verified against FastAPI
`/docs` and the `backend/routes/` implementation.

------------------------------------------------------------------------

# 25. Logical Data Flow

The primary financial data flow is:

``` text
                 ┌──────────────┐
                 │     User     │
                 └──────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │ Next.js / App │
                └───────┬───────┘
                        │
                        ▼
                 ┌────────────┐
                 │  FastAPI   │
                 └─────┬──────┘
                       │
          ┌────────────┼─────────────┐
          │            │             │
          ▼            ▼             ▼
    Transactions     AI Service   Payment
          │            │             │
          │            ▼             ▼
          │         Gemini         M-Pesa
          │
          ▼
     PostgreSQL
          │
          ├── Transactions
          ├── Categories
          ├── Insights
          ├── Users
          ├── Payments
          └── Subscriptions
```

------------------------------------------------------------------------

# 26. Data Flow for Uploaded Financial Statements

``` text
User
 │
 ▼
Upload financial document
 │
 ▼
FastAPI
 │
 ▼
Import / Parsing Service
 │
 ├────────────► S3 / Cloudinary
 │
 ▼
Parse transactions
 │
 ▼
AI Categorization
 │
 ▼
PostgreSQL
 │
 ├── UploadedDocument
 │
 └── Transactions
       │
       ▼
   Dashboard / Reports / Insights
```

------------------------------------------------------------------------

# 27. Subscription and Payment Data Flow

``` text
User
 │
 ▼
Select PRO
 │
 ▼
Frontend
 │
 ▼
FastAPI
 │
 ▼
Payment Service
 │
 ├──► PostgreSQL
 │      Payment = pending
 │
 └──► M-Pesa
         │
         ▼
      STK Push
         │
         ▼
       User
         │
         ▼
    M-Pesa PIN
         │
         ▼
      Callback
         │
         ▼
     FastAPI
         │
         ▼
   Payment Service
         │
         ├── Payment = completed
         │
         └── Subscription = active
```

------------------------------------------------------------------------

# 28. Database Design Observations

There are currently discrepancies between `backend/models/models.py` and
the supplied `schema.sql`.

## Entity comparison

  Entity               SQLAlchemy Models   schema.sql
  ------------------ ------------------- ------------
  User                               Yes          Yes
  Transaction                        Yes          Yes
  Category                           Yes          Yes
  Subscription                       Yes           No
  Payment                            Yes           No
  UploadedDocument                   Yes           No
  Insight                            Yes          Yes
  ChatMessage                         No          Yes
  DefaultCategory                     No          Yes

This should be resolved before treating `schema.sql` as the definitive
production schema.

------------------------------------------------------------------------

# 29. Schema Synchronization Issues

## 29.1 User updated_at

The SQL schema contains:

``` sql
updated_at TIMESTAMP DEFAULT NOW()
```

but the SQLAlchemy `User` model does not currently define this field.

## 29.2 Subscription

`Subscription` exists in the SQLAlchemy models but does not exist in the
supplied `schema.sql`.

## 29.3 Payment

`Payment` exists in the SQLAlchemy models but does not exist in the
supplied `schema.sql`.

## 29.4 UploadedDocument

`UploadedDocument` exists in the SQLAlchemy models but does not exist in
the supplied `schema.sql`.

## 29.5 ChatMessage

`chat_messages` exists in the SQL schema but does not have a
corresponding SQLAlchemy model in the supplied `models.py`.

## 29.6 DefaultCategory

`default_categories` exists in SQL but does not have a corresponding
SQLAlchemy model.

------------------------------------------------------------------------

# 30. Recommended Database Improvements

If the goal is to make the database design more relational and
maintainable, consider introducing an explicit category foreign key.

Current:

``` text
transactions
    category VARCHAR
```

Potential improved design:

``` text
transactions
    category_id INTEGER FK
            │
            ▼
categories
    id INTEGER PK
```

This prevents category names from becoming inconsistent.

For imported transactions, the current logical relationship is:

``` text
uploaded_documents.batch_id
             │
             │ logical match
             ▼
transactions.import_batch_id
```

A future design could introduce a direct foreign key if the application
requires strict referential integrity.

------------------------------------------------------------------------

# 31. Recommended UML Documentation Set

For the complete project documentation, use these diagrams:

``` text
BiasharaIQ UML Documentation
│
├── 01 Use Case Diagram
│
├── 02 System Architecture / Component Diagram
│
├── 03 UML Class Diagram
│
├── 04 Database / ER Diagram
│
├── 05 Transaction Sequence Diagram
│
├── 06 Transaction Import Sequence Diagram
│
├── 07 AI Insight Sequence Diagram
│
├── 08 M-Pesa Payment Sequence Diagram
│
├── 09 Mobile Application Architecture
│
├── 10 AWS Deployment Diagram
│
└── 11 URL / API Route Architecture
```

------------------------------------------------------------------------

# 32. POS Extension --- Future Architecture

The current BiasharaIQ model does **not** contain a POS subsystem.

If an online POS is added, it should be integrated with the existing
financial system instead of becoming a completely separate application.

A future POS model could introduce:

``` text
Product
 ├── ProductCategory
 ├── Stock
 └── SaleItem

Sale
 ├── SaleItem
 ├── Payment
 └── Transaction
```

A conceptual flow would be:

``` text
POS
 │
 ▼
Sale
 │
 ├── Sale Items
 │       │
 │       └── Products
 │
 ▼
Payment
 │
 ▼
Transaction
 │
 ▼
BiasharaIQ Financial Analytics
```

This would allow POS sales to automatically become financial
transactions and appear in:

-   Dashboard
-   Reports
-   Revenue analytics
-   Financial insights
-   Transaction history

The POS should therefore be treated as a future module of BiasharaIQ.

------------------------------------------------------------------------

# 33. Final High-Level System Model

The complete conceptual architecture can be summarized as:

``` text
                           BIASHARAIQ
                               │
             ┌─────────────────┼──────────────────┐
             │                 │                  │
             ▼                 ▼                  ▼
          WEB APP          ANDROID APP          FUTURE POS
          Next.js          Capacitor             Module
             │                 │                  │
             └─────────────────┼──────────────────┘
                               │
                         REST / HTTPS
                               │
                               ▼
                         FASTAPI BACKEND
                               │
        ┌──────────────┬───────┼────────┬──────────────┐
        │              │       │        │              │
        ▼              ▼       ▼        ▼              ▼
   Transactions    Payments   AI    Insights       Imports
        │              │       │        │              │
        │              ▼       ▼        │              ▼
        │            M-Pesa  Gemini     │        S3/Cloudinary
        │                              │
        └───────────────┬──────────────┘
                        ▼
                   PostgreSQL
                        │
       ┌────────────────┼────────────────────┐
       │                │                    │
       ▼                ▼                    ▼
     Users         Transactions          Categories
       │
       ├── Subscriptions
       ├── Payments
       ├── UploadedDocuments
       ├── Insights
       └── ChatMessages
```

------------------------------------------------------------------------

# 34. Conclusion

BiasharaIQ is structured as a decoupled financial intelligence platform
with:

1.  A Next.js web client.
2.  A Capacitor-based Android client.
3.  A FastAPI REST backend.
4.  SQLAlchemy-based data access.
5.  PostgreSQL as the primary relational database.
6.  Google Gemini for AI-assisted categorization and analysis.
7.  M-Pesa for payment processing.
8.  Cloudinary/S3 for uploaded document storage.
9.  Docker for containerization.
10. Terraform for infrastructure automation.
11. AWS ECS for application deployment.
12. AWS RDS for PostgreSQL.

The central domain entity is the `User`, which owns transactions,
categories, subscriptions, payments, uploaded documents, insights, and
AI chat history.

The most important financial workflow is:

``` text
Transaction Input
      │
      ▼
Transaction Processing
      │
      ▼
AI / Rule-Based Categorization
      │
      ▼
PostgreSQL
      │
      ├── Dashboard
      ├── Reports
      └── Financial Insights
```

The most important payment workflow is:

``` text
Subscription
      │
      ▼
Payment Request
      │
      ▼
M-Pesa STK Push
      │
      ▼
Callback
      │
      ▼
Payment Confirmation
      │
      ▼
Subscription Activation
```

The most important deployment workflow is:

``` text
Developer
    │
    ▼
Terraform
    │
    ▼
AWS Infrastructure
    │
    ├── ECS → Next.js / FastAPI
    │
    └── RDS → PostgreSQL
```

This document should be updated whenever the database models, API
routes, system integrations, or deployment architecture changes.
