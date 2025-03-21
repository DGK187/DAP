"""
Machine learning model for detecting grooming and risky conversations
"""
import logging
import os
import pickle
import pandas as pd
import numpy as np
from datetime import datetime

# ML components
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

logger = logging.getLogger(__name__)

class GroomingDetector:
    """Grooming detection model using NLP and machine learning"""
    
    def __init__(self, model_path=None):
        """Initialize the model, loading from path if provided"""
        self.model = None
        self.model_info = {
            'version': '0.1',
            'created_at': datetime.now().isoformat(),
            'accuracy': 0.0,
            'training_size': 0
        }
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            logger.warning(f"No model found at {model_path}, initializing new model")
            self._initialize_model()
    
    def _initialize_model(self):
        """Create a new model pipeline"""
        self.model = Pipeline([
            ('vectorizer', TfidfVectorizer(
                max_features=10000,
                ngram_range=(1, 3),
                stop_words='english'
            )),
            ('classifier', RandomForestClassifier(
                n_estimators=100,
                random_state=42
            ))
        ])
    
    def train(self, data_path, test_size=0.2):
        """Train the model on data from CSV file"""
        logger.info(f"Training model with data from {data_path}")
        
        try:
            # Load data
            df = pd.read_csv(data_path)
            logger.info(f"Loaded {len(df)} messages from {data_path}")
            
            # Prepare data
            X = df['message']
            y = df['label'].apply(lambda x: 1 if x == 'grooming' else 0)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42, stratify=y
            )
            
            # Initialize model if needed
            if self.model is None:
                self._initialize_model()
            
            # Train model
            self.model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Update model info
            self.model_info.update({
                'created_at': datetime.now().isoformat(),
                'accuracy': accuracy,
                'training_size': len(X_train)
            })
            
            logger.info(f"Model trained with accuracy: {accuracy:.4f}")
            logger.info(f"Classification report:\n{classification_report(y_test, y_pred)}")
            
            return accuracy
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            raise
    
    def predict_risk(self, message):
        """Predict risk score for a message"""
        if self.model is None:
            logger.error("No model loaded, cannot predict")
            return 0.0
        
        try:
            # Get probability of class 1 (grooming)
            probabilities = self.model.predict_proba([message])
            risk_score = probabilities[0][1]  # Probability of grooming class
            
            return float(risk_score)
            
        except Exception as e:
            logger.error(f"Error predicting risk: {e}")
            return 0.0
    
    def save_model(self, model_path):
        """Save model to file"""
        if self.model is None:
            logger.error("No model to save")
            return False
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            
            # Save model and info
            with open(model_path, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'info': self.model_info
                }, f)
            
            logger.info(f"Model saved to {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False
    
    def load_model(self, model_path):
        """Load model from file"""
        try:
            with open(model_path, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.model_info = data.get('info', self.model_info)
            
            logger.info(f"Model loaded from {model_path}")
            logger.info(f"Model info: {self.model_info}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def info(self):
        """Get model information"""
        return self.model_info

# Usage example
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    model = GroomingDetector()
    model.train("chat_data.csv")
    
    # Example prediction
    risk = model.predict_risk("Hey, how old are you? Where do you live?")
    print(f"Risk score: {risk:.4f}")
    
    # Save model
    model.save_model("models/grooming_detector.pkl")