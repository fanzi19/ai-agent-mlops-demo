import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os
import re

class EnhancedModelTrainer:
    def __init__(self):
        # Better feature extraction with more sophisticated patterns
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),  # Include bigrams
            stop_words='english',
            lowercase=True,
            min_df=2  # Ignore rare words
        )
        
        # Use Random Forest for better accuracy
        self.issue_classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        self.sentiment_classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        self.satisfaction_regressor = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
    def add_features(self, df):
        """Add engineered features for better accuracy"""
        # Add text length features
        df['message_length'] = df['message'].str.len()
        df['word_count'] = df['message'].str.split().str.len()
        
        # Add negative sentiment indicators
        negative_patterns = [
            r'\b(bad|terrible|awful|horrible|worst|hate|angry|frustrated|disappointed)\b',
            r'\b(can\'t|cannot|won\'t|don\'t|never|no|not)\b',
            r'\b(lost|missing|broken|damaged|wrong|error|fail|problem)\b',
            r'[!]{2,}',  # Multiple exclamation marks
            r'[?]{2,}'   # Multiple question marks
        ]
        
        df['negative_indicators'] = 0
        for pattern in negative_patterns:
            df['negative_indicators'] += df['message'].str.count(pattern, flags=re.IGNORECASE)
        
        # Add positive sentiment indicators
        positive_patterns = [
            r'\b(great|excellent|amazing|wonderful|fantastic|perfect|love|thank|good)\b',
            r'\b(yes|absolutely|definitely|sure|of course)\b'
        ]
        
        df['positive_indicators'] = 0
        for pattern in positive_patterns:
            df['positive_indicators'] += df['message'].str.count(pattern, flags=re.IGNORECASE)
        
        # Add urgency indicators
        urgency_patterns = [
            r'\b(urgent|emergency|immediately|asap|now|quick|fast)\b',
            r'[!]{1,}'
        ]
        
        df['urgency_indicators'] = 0
        for pattern in urgency_patterns:
            df['urgency_indicators'] += df['message'].str.count(pattern, flags=re.IGNORECASE)
            
        return df
    
    def train_models(self, data_path='data/training_data.csv'):
        """Train all models with enhanced features"""
        print("📚 Loading training data...")
        df = pd.read_csv(data_path)
        
        # Add engineered features
        df = self.add_features(df)
        
        print(f"📊 Training on {len(df)} examples")
        
        # Prepare text features
        X_text = self.tfidf_vectorizer.fit_transform(df['message'])
        
        # Combine text features with engineered features
        feature_cols = ['message_length', 'word_count', 'negative_indicators', 
                       'positive_indicators', 'urgency_indicators']
        X_features = df[feature_cols].values
        
        # Combine all features
        from scipy.sparse import hstack
        X_combined = hstack([X_text, X_features])
        
        # Train issue classifier
        print("🎯 Training issue classifier...")
        y_issue = df['issue_type']
        X_train, X_test, y_train, y_test = train_test_split(
            X_combined, y_issue, test_size=0.2, random_state=42
        )
        
        self.issue_classifier.fit(X_train, y_train)
        y_pred = self.issue_classifier.predict(X_test)
        print(f"Issue Classification Accuracy: {accuracy_score(y_test, y_pred):.3f}")
        
        # Train sentiment classifier
        print("😊 Training sentiment classifier...")
        y_sentiment = df['sentiment']
        X_train, X_test, y_train, y_test = train_test_split(
            X_combined, y_sentiment, test_size=0.2, random_state=42
        )
        
        self.sentiment_classifier.fit(X_train, y_train)
        y_pred = self.sentiment_classifier.predict(X_test)
        print(f"Sentiment Classification Accuracy: {accuracy_score(y_test, y_pred):.3f}")
        
        # Train satisfaction regressor (convert to classification for better accuracy)
        print("📈 Training satisfaction predictor...")
        # Convert satisfaction scores to categories
        df['satisfaction_category'] = pd.cut(df['satisfaction_score'], 
                                           bins=[0, 0.3, 0.7, 1.0], 
                                           labels=['low', 'medium', 'high'])
        
        y_satisfaction = df['satisfaction_category']
        X_train, X_test, y_train, y_test = train_test_split(
            X_combined, y_satisfaction, test_size=0.2, random_state=42
        )
        
        self.satisfaction_regressor.fit(X_train, y_train)
        y_pred = self.satisfaction_regressor.predict(X_test)
        print(f"Satisfaction Prediction Accuracy: {accuracy_score(y_test, y_pred):.3f}")
        
        # Save models
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.tfidf_vectorizer, 'models/tfidf_vectorizer.pkl')
        joblib.dump(self.issue_classifier, 'models/issue_classifier.pkl')
        joblib.dump(self.sentiment_classifier, 'models/sentiment_classifier.pkl')
        joblib.dump(self.satisfaction_regressor, 'models/satisfaction_regressor.pkl')
        
        print("✅ Enhanced models trained and saved!")
        
        return {
            'issue_accuracy': accuracy_score(y_test, y_pred),
            'models_saved': True
        }

if __name__ == "__main__":
    trainer = EnhancedModelTrainer()
    trainer.train_models()
