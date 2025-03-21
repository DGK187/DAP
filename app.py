#!/usr/bin/env python3
"""
Child Safety Monitoring Application
Main application entry point
"""
import logging
import os
import sys
from datetime import datetime

from database import Database
from model import GroomingDetector
from utils import setup_logging, load_config
from alert_manager import AlertManager

# Setup logging
logger = setup_logging()

def main():
    """Main application entry point"""
    try:
        logger.info("Starting Child Safety Monitoring Application")
        
        # Load configuration
        config = load_config()
        logger.info(f"Configuration loaded from {config['config_path']}")
        
        # Initialize database connection
        db = Database(config['database']['path'])
        logger.info("Database connection established")
        
        # Initialize ML model
        model = GroomingDetector(config['model']['path'])
        logger.info(f"Grooming detection model loaded: {model.info()}")
        
        # Initialize alert manager
        alert_manager = AlertManager(db, config['alerts'])
        
        # Process new messages
        process_new_messages(db, model, alert_manager, config)
        
        # Close database connection
        db.close()
        logger.info("Application completed successfully")
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)

def process_new_messages(db, model, alert_manager, config):
    """Process new messages and generate alerts"""
    logger.info("Processing new messages")
    
    # Get unprocessed messages
    messages = db.get_unprocessed_messages()
    logger.info(f"Found {len(messages)} unprocessed messages")
    
    alerts_generated = 0
    
    for message in messages:
        # Analyze message for risk
        risk_score = model.predict_risk(message['content'])
        
        # Update message with risk score
        db.update_message_risk(message['id'], risk_score)
        
        # Update contact risk score
        db.update_contact_risk(message['contact_id'])
        
        # Generate alert if needed
        if risk_score >= config['alerts']['min_risk_threshold']:
            alert_manager.create_alert(
                child_id=message['child_id'],
                contact_id=message['contact_id'],
                message_id=message['id'],
                risk_score=risk_score,
                alert_type="high_risk_message"
            )
            alerts_generated += 1
    
    # Generate contact-based alerts
    high_risk_contacts = db.get_contacts_by_risk(
        min_risk=config['alerts']['contact_risk_threshold']
    )
    
    for contact in high_risk_contacts:
        if not alert_manager.has_recent_alert(contact['id'], "high_risk_contact"):
            alert_manager.create_alert(
                child_id=contact['child_id'],
                contact_id=contact['id'],
                risk_score=contact['risk_score'],
                alert_type="high_risk_contact"
            )
            alerts_generated += 1
    
    logger.info(f"Processing complete. Generated {alerts_generated} alerts")

if __name__ == "__main__":
    main()