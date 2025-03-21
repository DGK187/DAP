"""
Utility functions for the Child Safety Monitoring Application
"""
import logging
import logging.handlers
import json
import os
import sys
from datetime import datetime

def setup_logging(log_level=logging.INFO, log_file=None):
    """Set up application logging"""
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if log file specified)
    if log_file:
        # Create log directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # Rotating file handler (10 MB max, keep 5 backups)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def load_config(config_path='config.json'):
    """Load application configuration from JSON file"""
    # Default configuration
    default_config = {
        'database': {
            'path': 'data/monitoring.db'
        },
        'model': {
            'path': 'models/grooming_detector.pkl'
        },
        'alerts': {
            'min_risk_threshold': 0.7,
            'contact_risk_threshold': 0.6,
            'alert_cooldown_hours': 24
        },
        'logging': {
            'level': 'INFO',
            'file': 'logs/app.log'
        }
    }
    
    # Load configuration from file if exists
    config = default_config.copy()
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                # Update default config with file config
                deep_update(config, file_config)
    except Exception as e:
        logging.error(f"Error loading configuration: {e}")
        logging.warning(f"Using default configuration")
    
    # Add config path to config
    config['config_path'] = config_path
    
    return config

def deep_update(d, u):
    """Recursively update nested dictionary"""
    for k, v in u.items():
        if isinstance(v, dict) and k in d and isinstance(d[k], dict):
            deep_update(d[k], v)
        else:
            d[k] = v
    return d

def initialize_database(db_path, schema_path='schema.sql'):
    """Initialize database with schema"""
    import sqlite3
    
    # Create directory if it doesn't exist
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    
    # Execute schema SQL
    try:
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        conn.executescript(schema_sql)
        conn.commit()
        
        # Add timestamp fields
        now = datetime.now().isoformat()
        
        # Add initial test child if database is empty
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM children")
        count = cursor.fetchone()[0]
        
        if count == 0:
            cursor.execute(
                "INSERT INTO children (name, age, created_at, updated_at) VALUES (?, ?, ?, ?)",
                ("Test Child", 12, now, now)
            )
            conn.commit()
        
        logging.info(f"Database initialized at {db_path}")
        
    except Exception as e:
        logging.error(f"Error initializing database: {e}")
        raise
    finally:
        conn.close()