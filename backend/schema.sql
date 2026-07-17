-- BiasharaIQ Database Schema

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    business_name VARCHAR(255) NOT NULL,
    owner_name VARCHAR(255),
    phone VARCHAR(20),
    business_type VARCHAR(100),
    currency VARCHAR(10) DEFAULT 'KES',
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    plan VARCHAR(50) DEFAULT 'FREE',
    subscription_status VARCHAR(50) DEFAULT 'active',
    subscription_start TIMESTAMP,
    subscription_end TIMESTAMP,
    monthly_transaction_count INTEGER DEFAULT 0,
    ai_queries_count INTEGER DEFAULT 0,
    ai_queries_reset_date TIMESTAMP,
    verification_code VARCHAR(10),
    verification_expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Categories table
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
    icon VARCHAR(50),
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    amount DECIMAL(15, 2) NOT NULL,
    type VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
    category VARCHAR(100) NOT NULL,
    date TIMESTAMP NOT NULL DEFAULT NOW(),
    description TEXT,
    source VARCHAR(50) DEFAULT 'manual',
    import_batch_id VARCHAR(100),
    status VARCHAR(50) DEFAULT 'confirmed',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Insights table (cached AI/rule-based insights)
CREATE TABLE IF NOT EXISTS insights (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    severity VARCHAR(20) DEFAULT 'info' CHECK (severity IN ('info', 'warning', 'critical')),
    timestamp TIMESTAMP DEFAULT NOW(),
    is_read BOOLEAN DEFAULT FALSE
);

-- AI Chat history
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);
CREATE INDEX IF NOT EXISTS idx_transactions_user_date ON transactions(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_categories_user_id ON categories(user_id);
CREATE INDEX IF NOT EXISTS idx_insights_user_id ON insights(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_user_id ON chat_messages(user_id);

-- Default categories seed data (inserted per user on registration - handled in app)
-- These are the template categories
CREATE TABLE IF NOT EXISTS default_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(10) NOT NULL,
    color VARCHAR(7) DEFAULT '#6366f1',
    icon VARCHAR(50) DEFAULT 'tag'
);

INSERT INTO default_categories (name, type, color, icon) VALUES
-- Income categories
('Sales', 'income', '#2E7D32', 'trending-up'),
('Services', 'income', '#1A1F71', 'briefcase'),
('Loans Received', 'income', '#0A2540', 'credit-card'),
('Other Income', 'income', '#F9A825', 'plus-circle'),
-- Expense categories
('Stock / Inventory', 'expense', '#F9A825', 'package'),
('Rent', 'expense', '#D32F2F', 'home'),
('Salaries', 'expense', '#0A2540', 'users'),
('Transport', 'expense', '#1A1F71', 'truck'),
('Utilities', 'expense', '#2E7D32', 'zap'),
('Marketing', 'expense', '#F9A825', 'megaphone'),
('Loan Repayment', 'expense', '#D32F2F', 'credit-card'),
('Equipment', 'expense', '#0A2540', 'tool'),
('Other Expenses', 'expense', '#1E1E1E', 'more-horizontal')
ON CONFLICT DO NOTHING;
