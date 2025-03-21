"""
Alert management for the Child Safety Monitoring Application
"""
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AlertManager:
    """Manages alert generation and resolution"""
    
    def __init__(self, database, alert_config=None):
        """Initialize with database connection and configuration"""
        self.db = database
        self.config = alert_config or {
            'min_risk_threshold': 0.7,
            'contact_risk_threshold': 0.6,
            'alert_cooldown_hours': 24
        }
    
    def create_alert(self, child_id, risk_score, alert_type, contact_id=None, message_id=None, details=None):
        """Create a new alert in the database"""
        try:
            cursor = self.db.conn.cursor()
            
            # Insert alert
            cursor.execute('''
            INSERT INTO alerts (
                child_id, contact_id, message_id, alert_type, 
                risk_score, details, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                child_id, contact_id, message_id, alert_type,
                risk_score, details, datetime.now().isoformat()
            ))
            
            self.db.conn.commit()
            alert_id = cursor.lastrowid
            
            logger.info(f"Created alert ID {alert_id} for child {child_id}, type: {alert_type}, risk: {risk_score:.2f}")
            return alert_id
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            self.db.conn.rollback()
            return None
    
    def resolve_alert(self, alert_id, resolved_by, notes=None):
        """Mark an alert as resolved"""
        try:
            cursor = self.db.conn.cursor()
            
            # Update alert
            cursor.execute('''
            UPDATE alerts
            SET resolved = 1, 
                resolved_at = ?,
                resolved_by = ?,
                resolution_notes = ?
            WHERE id = ?
            ''', (
                datetime.now().isoformat(),
                resolved_by,
                notes,
                alert_id
            ))
            
            self.db.conn.commit()
            
            logger.info(f"Resolved alert ID {alert_id} by {resolved_by}")
            return True
            
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
            self.db.conn.rollback()
            return False
    
    def has_recent_alert(self, contact_id, alert_type=None):
        """Check if there's a recent alert for this contact to avoid duplicates"""
        try:
            cursor = self.db.conn.cursor()
            
            # Calculate cutoff time
            cooldown_hours = self.config.get('alert_cooldown_hours', 24)
            cutoff = (datetime.now() - timedelta(hours=cooldown_hours)).isoformat()
            
            query = '''
            SELECT COUNT(*) as count
            FROM alerts
            WHERE contact_id = ? AND created_at >= ?
            '''
            
            params = [contact_id, cutoff]
            
            if alert_type:
                query += " AND alert_type = ?"
                params.append(alert_type)
            
            cursor.execute(query, tuple(params))
            
            result = cursor.fetchone()
            count = result[0] if result else 0
            
            return count > 0
            
        except Exception as e:
            logger.error(f"Error checking for recent alerts: {e}")
            return False
    
    def get_unresolved_alerts(self, child_id=None, days=7):
        """Get unresolved alerts for a child"""
        return self.db.get_alerts(
            child_id=child_id,
            days=days,
            resolved=False
        )
    
    def get_alert_count(self, child_id=None, days=7, resolved=None):
        """Get count of alerts matching criteria"""
        try:
            alerts = self.db.get_alerts(
                child_id=child_id,
                days=days,
                resolved=resolved
            )
            
            return len(alerts)
            
        except Exception as e:
            logger.error(f"Error getting alert count: {e}")
            return 0