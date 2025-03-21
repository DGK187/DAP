"""
Database operations for the Child Safety Monitoring Application
"""
import logging
import sqlite3
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class Database:
    """Database operations handler"""
    
    def __init__(self, db_path):
        """Initialize database connection"""
        self.db_path = db_path
        self.conn = None
        self._connect()
        
    def _connect(self):
        """Establish database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def get_unprocessed_messages(self, limit=100):
        """Get unprocessed messages from the database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            SELECT m.id, m.child_id, m.contact_id, m.content, m.timestamp, 
                   c.name as contact_name, c.platform
            FROM messages m
            JOIN contacts c ON m.contact_id = c.id
            WHERE m.processed = 0
            ORDER BY m.timestamp ASC
            LIMIT ?
            ''', (limit,))
            
            messages = []
            for row in cursor.fetchall():
                messages.append(dict(row))
            
            return messages
        
        except Exception as e:
            logger.error(f"Error getting unprocessed messages: {e}")
            return []
    
    def update_message_risk(self, message_id, risk_score):
        """Update message with risk score and mark as processed"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            UPDATE messages
            SET risk_score = ?, processed = 1, processed_at = ?
            WHERE id = ?
            ''', (risk_score, datetime.now().isoformat(), message_id))
            
            self.conn.commit()
            logger.debug(f"Updated message {message_id} with risk score {risk_score}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating message risk: {e}")
            self.conn.rollback()
            return False
    
    def update_contact_risk(self, contact_id):
        """Update contact risk score based on message history"""
        try:
            cursor = self.conn.cursor()
            
            # Calculate average risk from recent messages
            cursor.execute('''
            SELECT AVG(risk_score) as avg_risk
            FROM (
                SELECT risk_score
                FROM messages
                WHERE contact_id = ? AND processed = 1
                ORDER BY timestamp DESC
                LIMIT 50
            )
            ''', (contact_id,))
            
            result = cursor.fetchone()
            avg_risk = result['avg_risk'] if result['avg_risk'] is not None else 0
            
            # Get current interaction count
            cursor.execute('''
            SELECT interaction_count
            FROM contacts
            WHERE id = ?
            ''', (contact_id,))
            
            result = cursor.fetchone()
            current_count = result['interaction_count'] if result else 0
            
            # Update contact with new risk score and increment interaction count
            cursor.execute('''
            UPDATE contacts
            SET risk_score = ?, 
                interaction_count = ?,
                last_contact = ?
            WHERE id = ?
            ''', (avg_risk, current_count + 1, datetime.now().isoformat(), contact_id))
            
            self.conn.commit()
            logger.debug(f"Updated contact {contact_id} with risk score {avg_risk}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating contact risk: {e}")
            self.conn.rollback()
            return False
    
    def get_contacts_by_risk(self, child_id=None, min_risk=0.5, limit=10):
        """Get high-risk contacts for a child."""
        try:
            cursor = self.conn.cursor()
            
            query = '''
            SELECT id, child_id, contact_id, name, phone, platform, first_contact, last_contact, 
                  interaction_count, risk_score
            FROM contacts
            WHERE risk_score >= ?
            '''
            
            params = [min_risk]
            
            if child_id:
                query += " AND child_id = ?"
                params.append(child_id)
                
            query += '''
            ORDER BY risk_score DESC
            LIMIT ?
            '''
            params.append(limit)
            
            cursor.execute(query, tuple(params))
            
            contacts = []
            for row in cursor.fetchall():
                contacts.append(dict(row))
            
            return contacts
            
        except Exception as e:
            logger.error(f"Error getting high-risk contacts: {e}")
            return []
    
    def get_alerts(self, child_id=None, days=7, resolved=False, limit=50):
        """Get recent alerts"""
        try:
            cursor = self.conn.cursor()
            
            query = '''
            SELECT a.id, a.child_id, a.contact_id, a.message_id, a.alert_type, 
                   a.risk_score, a.created_at, a.resolved, a.resolved_at,
                   c.name as contact_name, c.platform
            FROM alerts a
            LEFT JOIN contacts c ON a.contact_id = c.id
            WHERE a.created_at >= ?
            '''
            
            since_date = (datetime.now() - timedelta(days=days)).isoformat()
            params = [since_date]
            
            if child_id:
                query += " AND a.child_id = ?"
                params.append(child_id)
                
            if resolved is not None:
                query += " AND a.resolved = ?"
                params.append(1 if resolved else 0)
                
            query += '''
            ORDER BY a.created_at DESC
            LIMIT ?
            '''
            params.append(limit)
            
            cursor.execute(query, tuple(params))
            
            alerts = []
            for row in cursor.fetchall():
                alerts.append(dict(row))
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return []