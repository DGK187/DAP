# Guardian Pro - Comprehensive Child Protection System
# Core backend system architecture

import os
import re
import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob
import spacy
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model, Model
from tensorflow.keras.layers import Dense, LSTM, Embedding, Input, Dropout, Bidirectional, Concatenate
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import torch
import torch.nn as nn
from transformers import BertTokenizer, BertModel, BertForSequenceClassification
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score, precision_recall_curve
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, LabelEncoder
import pickle
import json
import logging
import time
import datetime
from datetime import timedelta
import sqlite3
import hashlib
import requests
import asyncio
import concurrent.futures
import queue
import threading
import argparse
import configparser
import uuid
import base64
import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import getpass
import signal
import sys
import io
import cv2
import PIL
from PIL import Image
import imagehash
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter, defaultdict, deque
import string
import calendar
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import joblib
import warnings
from typing import Dict, List, Tuple, Optional, Union, Any, Callable, Iterator, Set

# Suppress warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("guardian.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("GuardianPro")

# Constants
VERSION = "1.0.0"
CONFIG_FILE = "guardian_config.ini"
DEFAULT_RISK_THRESHOLD = 0.65
ENCRYPTION_KEY_FILE = ".guardian_key"
DATABASE_FILE = "guardian.db"
MODEL_DIRECTORY = "models/"
DATA_DIRECTORY = "data/"
LOG_DIRECTORY = "logs/"
CACHE_DIRECTORY = "cache/"
REPORT_DIRECTORY = "reports/"

# Ensure directories exist
for directory in [MODEL_DIRECTORY, DATA_DIRECTORY, LOG_DIRECTORY, CACHE_DIRECTORY, REPORT_DIRECTORY]:
    os.makedirs(directory, exist_ok=True)

# ------------------------------
# Core NLP Utility Functions
# ------------------------------

def download_nlp_resources():
    """Download and initialize all required NLP resources."""
    try:
        nltk.download('stopwords', quiet=True)
        nltk.download('punkt', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        nltk.download('wordnet', quiet=True)
        nltk.download('vader_lexicon', quiet=True)
        
        # Load spaCy model
        try:
            nlp = spacy.load('en_core_web_sm')
            logger.info("Loaded spaCy model successfully")
            return nlp
        except:
            logger.warning("Could not load spaCy model. Downloading...")
            spacy.cli.download('en_core_web_sm')
            nlp = spacy.load('en_core_web_sm')
            logger.info("Downloaded and loaded spaCy model successfully")
            return nlp
    
    except Exception as e:
        logger.error(f"Failed to download NLP resources: {e}")
        return None

# ------------------------------
# Encryption and Security Module
# ------------------------------

class SecurityManager:
    """Handles encryption, authentication, and security features."""
    
    def __init__(self, key_file=ENCRYPTION_KEY_FILE):
        """Initialize the security manager with encryption key."""
        self.key_file = key_file
        self.key = self._load_or_generate_key()
        self.cipher_suite = Fernet(self.key)
        
    def _load_or_generate_key(self):
        """Load existing key or generate a new one."""
        if os.path.exists(self.key_file):
            with open(self.key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(key)
            return key
    
    def encrypt_data(self, data: str) -> bytes:
        """Encrypt string data."""
        return self.cipher_suite.encrypt(data.encode())
    
    def decrypt_data(self, encrypted_data: bytes) -> str:
        """Decrypt data to string."""
        return self.cipher_suite.decrypt(encrypted_data).decode()
    
    def hash_password(self, password: str, salt=None) -> Tuple[bytes, bytes]:
        """Hash a password with a salt."""
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        password_hash = kdf.derive(password.encode())
        return password_hash, salt
    
    def verify_password(self, password: str, stored_hash: bytes, salt: bytes) -> bool:
        """Verify a password against a stored hash."""
        password_hash, _ = self.hash_password(password, salt)
        return password_hash == stored_hash
    
    def generate_token(self) -> str:
        """Generate a secure authentication token."""
        return base64.urlsafe_b64encode(os.urandom(32)).decode()

# ------------------------------
# Database Manager
# ------------------------------

class DatabaseManager:
    """Manages database operations and schema."""
    
    def __init__(self, db_file=DATABASE_FILE, security_manager=None):
        """Initialize database connection and setup schema."""
        self.db_file = db_file
        self.security = security_manager
        self.conn = self._initialize_database()
        
    def _initialize_database(self):
        """Set up database and tables."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash BLOB,
            salt BLOB,
            email TEXT,
            phone TEXT,
            role TEXT,
            created_at TEXT,
            last_login TEXT,
            settings_json TEXT
        )
        ''')
        
        # Children profiles
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS children (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id INTEGER,
            name TEXT,
            age INTEGER,
            device_ids TEXT,
            risk_profile TEXT,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY (parent_id) REFERENCES users (id)
        )
        ''')
        
        # Devices
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_uuid TEXT UNIQUE,
            device_name TEXT,
            device_type TEXT,
            os_type TEXT,
            os_version TEXT, 
            child_id INTEGER,
            last_active TEXT,
            status TEXT,
            FOREIGN KEY (child_id) REFERENCES children (id)
        )
        ''')
        
        # Messages table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            sender TEXT,
            sender_id TEXT,
            receiver TEXT,
            receiver_id TEXT,
            app_source TEXT,
            message_text TEXT,
            message_hash TEXT UNIQUE,
            risk_score REAL,
            flagged INTEGER,
            reviewed INTEGER DEFAULT 0,
            device_id INTEGER,
            FOREIGN KEY (device_id) REFERENCES devices (id)
        )
        ''')
        
        # Alerts table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            message_id INTEGER,
            alert_type TEXT,
            severity TEXT,
            description TEXT,
            action_taken TEXT,
            status TEXT,
            resolved_at TEXT,
            resolved_by INTEGER,
            FOREIGN KEY (message_id) REFERENCES messages (id),
            FOREIGN KEY (resolved_by) REFERENCES users (id)
        )
        ''')
        
        # Contact analysis
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id TEXT,
            name TEXT,
            phone TEXT,
            platform TEXT,
            first_contact TEXT,
            last_contact TEXT,
            interaction_count INTEGER,
            risk_score REAL,
            device_id INTEGER,
            child_id INTEGER,
            FOREIGN KEY (device_id) REFERENCES devices (id),
            FOREIGN KEY (child_id) REFERENCES children (id)
        )
        ''')
        
        # Images analysis
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            device_id INTEGER,
            image_hash TEXT UNIQUE,
            source_app TEXT,
            risk_score REAL,
            flagged INTEGER,
            reviewed INTEGER DEFAULT 0,
            FOREIGN KEY (device_id) REFERENCES devices (id)
        )
        ''')
        
        # App usage stats
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS app_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER,
            app_name TEXT,
            start_time TEXT,
            end_time TEXT,
            duration_seconds INTEGER,
            date TEXT,
            FOREIGN KEY (device_id) REFERENCES devices (id)
        )
        ''')
        
        # Safety reports
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            report_type TEXT,
            generated_at TEXT,
            timeframe TEXT,
            content_json TEXT,
            format TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Settings and configurations
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            setting_key TEXT,
            setting_value TEXT,
            updated_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages (timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages (sender)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_receiver ON messages (receiver)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts (timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_risk ON contacts (risk_score)')
        
        conn.commit()
        return conn
    
    def add_user(self, username, password, email=None, phone=None, role="parent"):
        """Add a new user with securely hashed password."""
        try:
            if not self.security:
                raise ValueError("Security manager not initialized")
                
            # Hash the password
            password_hash, salt = self.security.hash_password(password)
            
            # Prepare default settings
            default_settings = {
                "risk_threshold": DEFAULT_RISK_THRESHOLD,
                "alert_notifications": True,
                "report_frequency": "weekly",
                "monitored_apps": ["SMS", "WhatsApp", "Instagram", "Snapchat", "TikTok"],
                "notification_channels": ["app", "email"]
            }
            
            now = datetime.datetime.now().isoformat()
            
            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT INTO users (username, password_hash, salt, email, phone, role, created_at, settings_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, password_hash, salt, email, phone, role, now, json.dumps(default_settings)))
            
            self.conn.commit()
            return cursor.lastrowid
            
        except sqlite3.IntegrityError:
            logger.error(f"Username {username} already exists")
            return None
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            return None
    
    def verify_user(self, username, password):
        """Verify user credentials."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            SELECT id, password_hash, salt FROM users WHERE username = ?
            ''', (username,))
            
            result = cursor.fetchone()
            if not result:
                return None
                
            user_id, password_hash, salt = result
            
            if self.security.verify_password(password, password_hash, salt):
                # Update last login time
                now = datetime.datetime.now().isoformat()
                cursor.execute('''
                UPDATE users SET last_login = ? WHERE id = ?
                ''', (now, user_id))
                self.conn.commit()
                return user_id
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error verifying user: {e}")
            return None
    
    def get_user_settings(self, user_id):
        """Get user settings."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            SELECT settings_json FROM users WHERE id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            if result and result[0]:
                return json.loads(result[0])
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error getting user settings: {e}")
            return {}
    
    def update_user_settings(self, user_id, settings):
        """Update user settings."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            UPDATE users SET settings_json = ? WHERE id = ?
            ''', (json.dumps(settings), user_id))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error updating user settings: {e}")
            return False
    
    def add_child_profile(self, parent_id, name, age, device_ids=None):
        """Add a child profile."""
        try:
            now = datetime.datetime.now().isoformat()
            device_ids_str = json.dumps(device_ids or [])
            
            # Default risk profile
            risk_profile = {
                "overall_risk_level": "low",
                "age_appropriate_threshold": 0.6 if age < 13 else 0.7,
                "custom_alerts": [],
                "restricted_contacts": []
            }
            
            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT INTO children (parent_id, name, age, device_ids, risk_profile, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (parent_id, name, age, device_ids_str, json.dumps(risk_profile), now, now))
            
            self.conn.commit()
            return cursor.lastrowid
            
        except Exception as e:
            logger.error(f"Error adding child profile: {e}")
            return None
    
    def get_child_profiles(self, parent_id):
        """Get all child profiles for a parent."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            SELECT id, name, age, device_ids, risk_profile, created_at, updated_at
            FROM children
            WHERE parent_id = ?
            ''', (parent_id,))
            
            profiles = []
            for row in cursor.fetchall():
                child_id, name, age, device_ids_str, risk_profile_str, created_at, updated_at = row
                
                # Parse JSON fields
                try:
                    device_ids = json.loads(device_ids_str)
                except:
                    device_ids = []
                    
                try:
                    risk_profile = json.loads(risk_profile_str)
                except:
                    risk_profile = {}
                
                profiles.append({
                    "id": child_id,
                    "name": name,
                    "age": age,
                    "device_ids": device_ids,
                    "risk_profile": risk_profile,
                    "created_at": created_at,
                    "updated_at": updated_at
                })
                
            return profiles
            
        except Exception as e:
            logger.error(f"Error getting child profiles: {e}")
            return []
    
    def register_device(self, device_uuid, device_name, device_type, os_type, os_version, child_id=None):
        """Register a new device."""
        try:
            now = datetime.datetime.now().isoformat()
            
            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT INTO devices (device_uuid, device_name, device_type, os_type, os_version, child_id, last_active, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (device_uuid, device_name, device_type, os_type, os_version, child_id, now, "active"))
            
            device_id = cursor.lastrowid
            
            # If child_id provided, update the child's device_ids list
            if child_id:
                cursor.execute('''
                SELECT device_ids FROM children WHERE id = ?
                ''', (child_id,))
                
                result = cursor.fetchone()
                if result:
                    try:
                        device_ids = json.loads(result[0])
                    except:
                        device_ids = []
                        
                    device_ids.append(device_id)
                    
                    cursor.execute('''
                    UPDATE children SET device_ids = ?, updated_at = ? WHERE id = ?
                    ''', (json.dumps(device_ids), now, child_id))
            
            self.conn.commit()
            return device_id
            
        except sqlite3.IntegrityError:
            logger.error(f"Device UUID {device_uuid} already exists")
            
            # Return existing device id
            cursor = self.conn.cursor()
            cursor.execute('''
            SELECT id FROM devices WHERE device_uuid = ?
            ''', (device_uuid,))
            
            result = cursor.fetchone()
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"Error registering device: {e}")
            return None
    
    def log_message(self, timestamp, sender, sender_id, receiver, receiver_id, app_source, 
                   message_text, risk_score, flagged, device_id):
        """Log a message with analysis results."""
        try:
            # Create message hash to prevent duplicates
            message_hash = hashlib.md5(f"{timestamp}:{sender}:{receiver}:{message_text}".encode()).hexdigest()
            
            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT INTO messages (timestamp, sender, sender_id, receiver, receiver_id, app_source, 
                                 message_text, message_hash, risk_score, flagged, device_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (timestamp, sender, sender_id, receiver, receiver_id, app_source, 
                 message_text, message_hash, risk_score, int(flagged), device_id))
            
            self.conn.commit()
            return cursor.lastrowid
            
        except sqlite3.IntegrityError:
            # Message already exists
            return None
            
        except Exception as e:
            logger.error(f"Error logging message: {e}")
            return None
    
    def create_alert(self, message_id, alert_type, severity, description, action_taken="Alert generated"):
        """Create an alert for a flagged message or event."""
        try:
            timestamp = datetime.datetime.now().isoformat()
            
            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT INTO alerts (timestamp, message_id, alert_type, severity, description, action_taken, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (timestamp, message_id, alert_type, severity, description, action_taken, "open"))
            
            self.conn.commit()
            return cursor.lastrowid
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            return None
    
    def update_contact_profile(self, contact_id, name, phone, platform, device_id, child_id, 
                              risk_score=0.0, interaction_count=1, first_contact=None, last_contact=None):
        """Update or create a contact profile."""
        try:
            now = datetime.datetime.now().isoformat()
            first_contact = first_contact or now
            last_contact = last_contact or now
            
            cursor = self.conn.cursor()
            
            # Check if contact exists
            cursor.execute('''
            SELECT id, interaction_count FROM contacts 
            WHERE contact_id = ? AND device_id = ? AND child_id = ?
            ''', (contact_id, device_id, child_id))
            
            result = cursor.fetchone()
            
            if result:
                # Update existing contact
                contact_id_db, current_count = result
                interaction_count = current_count + 1
                
                cursor.execute('''
                UPDATE contacts SET 
                    name = ?, 
                    phone = ?, 
                    platform = ?, 
                    last_contact = ?, 
                    interaction_count = ?,
                    risk_score = ?
                WHERE id = ?
                ''', (name, phone, platform, last_contact, interaction_count, risk_score, contact_id_db))
                
                self.conn.commit()
                return contact_id_db
                
            else:
                # Create new contact
                cursor.execute('''
                INSERT INTO contacts (contact_id, name, phone, platform, first_contact, last_contact, 
                                     interaction_count, risk_score, device_id, child_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (contact_id, name, phone, platform, first_contact, last_contact, 
                     interaction_count, risk_score, device_id, child_id))
                
                self.conn.commit()
                return cursor.lastrowid
                
        except Exception as e:
            logger.error(f"Error updating contact profile: {e}")
            return None
    
    def log_image(self, timestamp, device_id, image_hash, source_app, risk_score, flagged):
        """Log an image that has been analyzed."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT INTO images (timestamp, device_id, image_hash, source_app, risk_score, flagged)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (timestamp, device_id, image_hash, source_app, risk_score, int(flagged)))
            
            self.conn.commit()
            return cursor.lastrowid
            
        except sqlite3.IntegrityError:
            # Image already exists
            return None
            
        except Exception as e:
            logger.error(f"Error logging image: {e}")
            return None
    
    def log_app_usage(self, device_id, app_name, start_time, end_time, duration_seconds, date):
        """Log app usage statistics."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT INTO app_usage (device_id, app_name, start_time, end_time, duration_seconds, date)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (device_id, app_name, start_time, end_time, duration_seconds, date))
            
            self.conn.commit()
            return cursor.lastrowid
            
        except Exception as e:
            logger.error(f"Error logging app usage: {e}")
            return None
    
    def save_report(self, user_id, report_type, timeframe, content, format="json"):
        """Save a generated safety report."""
        try:
            generated_at = datetime.datetime.now().isoformat()
            
            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT INTO reports (user_id, report_type, generated_at, timeframe, content_json, format)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, report_type, generated_at, timeframe, json.dumps(content), format))
            
            self.conn.commit()
            return cursor.lastrowid
            
        except Exception as e:
            logger.error(f"Error saving report: {e}")
            return None
    
    def get_messages(self, filters=None, limit=100, offset=0):
        """Get messages with optional filtering."""
        try:
            query = '''
            SELECT id, timestamp, sender, receiver, app_source, message_text, risk_score, flagged, device_id 
            FROM messages
            '''
            
            params = []
            
            # Apply filters
            if filters:
                where_clauses = []
                
                if 'device_id' in filters:
                    where_clauses.append("device_id = ?")
                    params.append(filters['device_id'])
                
                if 'sender' in filters:
                    where_clauses.append("sender LIKE ?")
                    params.append(f"%{filters['sender']}%")
                
                if 'receiver' in filters:
                    where_clauses.append("receiver LIKE ?")
                    params.append(f"%{filters['receiver']}%")
                
                if 'app_source' in filters:
                    where_clauses.append("app_source = ?")
                    params.append(filters['app_source'])
                
                if 'min_risk' in filters:
                    where_clauses.append("risk_score >= ?")
                    params.append(filters['min_risk'])
                
                if 'flagged' in filters:
                    where_clauses.append("flagged = ?")
                    params.append(int(filters['flagged']))
                
                if 'start_date' in filters:
                    where_clauses.append("timestamp >= ?")
                    params.append(filters['start_date'])
                
                if 'end_date' in filters:
                    where_clauses.append("timestamp <= ?")
                    params.append(filters['end_date'])
                
                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)
            
            # Add ordering
            query += " ORDER BY timestamp DESC"
            
            # Add limit and offset
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            
            messages = []
            for row in cursor.fetchall():
                id, timestamp, sender, receiver, app_source, message_text, risk_score, flagged, device_id = row
                
                messages.append({
                    "id": id,
                    "timestamp": timestamp,
                    "sender": sender,
                    "receiver": receiver,
                    "app_source": app_source,
                    "message_text": message_text,
                    "risk_score": risk_score,
                    "flagged": bool(flagged),
                    "device_id": device_id
                })
                
            return messages
            
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            return []
    
    def get_alerts(self, user_id=None, status=None, severity=None, limit=20):
        """Get recent alerts with optional filtering."""
        try:
            query = '''
            SELECT a.id, a.timestamp, a.message_id, a.alert_type, a.severity, 
                  a.description, a.action_taken, a.status, m.message_text, m.sender, m.receiver,
                  d.device_name, c.name as child_name, c.id as child_id
            FROM alerts a
            JOIN messages m ON a.message_id = m.id
            JOIN devices d ON m.device_id = d.id
            LEFT JOIN children c ON d.child_id = c.id
            '''
            
            params = []
            where_clauses = []
            
            # Apply filters
            if user_id:
                where_clauses.append("c.parent_id = ?")
                params.append(user_id)
            
            if status:
                where_clauses.append("a.status = ?")
                params.append(status)
            
            if severity:
                where_clauses.append("a.severity = ?")
                params.append(severity)
            
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
            
            # Add ordering and limit
            query += " ORDER BY a.timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            
            alerts = []
            for row in cursor.fetchall():
                (id, timestamp, message_id, alert_type, severity, description, 
                 action_taken, status, message_text, sender, receiver, device_name, child_name, child_id) = row
                
                alerts.append({
                    "id": id,
                    "timestamp": timestamp,
                    "message_id": message_id,
                    "alert_type": alert_type,
                    "severity": severity,
                    "description": description,
                    "action_taken": action_taken,
                    "status": status,
                    "message_text": message_text,
                    "sender": sender,
                    "receiver": receiver,
                    "device_name": device_name,
                    "child_name": child_name,
                    "child_id": child_id
                })
                
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return []
    
    def get_contacts_by_risk(self, child_id, min_risk=0.5, limit=10):
        """Get high-risk contacts for a child."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            SELECT id, contact_id, name, phone, platform, first_contact, last_contact, 
                  interaction_count, risk_score
            FROM contacts
            WHERE child_id = ? AND risk_score >= ?
            ORDER BY risk_score DESC
            LIMIT ?
            ''', (child_id, min_risk, limit))
            
            contacts = []
            for row in cursor.fetchall():
                contacts.append({
                    'id': row[0],
                    'contact_id': row[1],
                    'name': row[2],
                    'phone': row[3],
                    'platform': row[4],
                    'first_contact': row[5],
                    'last_contact': row[6],
                    'interaction_count': row[7],
                    'risk_score': row[8]
                })
            
            return contacts
            
        except Exception as e:
            logger.error(f"Error getting high-risk contacts: {e}")
            return []