-- Child Safety Monitoring Application Database Schema

-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- Children table
CREATE TABLE IF NOT EXISTS children (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    device_id TEXT,
    parent_id INTEGER,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Contacts table
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id INTEGER NOT NULL,
    contact_id TEXT NOT NULL,  -- External identifier (phone number, username, etc.)
    name TEXT,
    phone TEXT,
    platform TEXT NOT NULL,    -- Social media platform or messaging app
    first_contact TEXT NOT NULL,  -- Timestamp of first interaction
    last_contact TEXT NOT NULL,   -- Timestamp of last interaction
    interaction_count INTEGER DEFAULT 0,
    risk_score REAL DEFAULT 0.0,  -- 0.0 to 1.0 risk score
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
    UNIQUE (child_id, contact_id, platform)
);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id INTEGER NOT NULL,
    contact_id INTEGER NOT NULL,
    direction TEXT NOT NULL,    -- 'incoming' or 'outgoing'
    content TEXT NOT NULL,
    media_url TEXT,            -- URL to any media content in the message
    timestamp TEXT NOT NULL,   -- When the message was sent/received
    processed BOOLEAN DEFAULT 0,
    processed_at TEXT,         -- When message was analyzed
    risk_score REAL DEFAULT 0.0,
    created_at TEXT NOT NULL,
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
);

-- Alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id INTEGER NOT NULL,
    contact_id INTEGER,
    message_id INTEGER,
    alert_type TEXT NOT NULL,  -- 'high_risk_message', 'high_risk_contact', etc.
    risk_score REAL NOT NULL,
    details TEXT,
    resolved BOOLEAN DEFAULT 0,
    resolved_at TEXT,
    resolved_by TEXT,
    resolution_notes TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE SET NULL,
    FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE SET NULL
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_messages_processed ON messages(processed, timestamp);
CREATE INDEX IF NOT EXISTS idx_messages_contact ON messages(contact_id);
CREATE INDEX IF NOT EXISTS idx_contacts_risk ON contacts(risk_score);
CREATE INDEX IF NOT EXISTS idx_alerts_created ON alerts(created_at);
CREATE INDEX IF NOT EXISTS idx_alerts_child ON alerts(child_id);