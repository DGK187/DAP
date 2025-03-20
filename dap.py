import re
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from textblob import TextBlob
from collections import Counter
import string
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Download necessary resources
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

# Load dataset (replace with actual file path)
df = pd.read_csv('chat_data.csv')  # Ensure the dataset has 'message' and 'label' columns

# Preprocessing function
def clean_text(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'http\S+|www.\S+', '', text)  # Remove URLs
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove special characters
    tokens = word_tokenize(text)  # Tokenize text
    tokens = [word for word in tokens if word not in stopwords.words('english')]  # Remove stopwords
    return ' '.join(tokens)

# Extract additional features
def extract_features(text):
    tokens = word_tokenize(text)
    num_words = len(tokens)  # Word count
    num_chars = len(text)  # Character count
    num_sentences = text.count('.') + text.count('!') + text.count('?')  # Sentence count
    avg_word_length = num_chars / num_words if num_words > 0 else 0  # Average word length
    sentiment = TextBlob(text).sentiment.polarity  # Sentiment score (-1 to 1)
    pos_tags = nltk.pos_tag(tokens)  # Part-of-speech tagging
    noun_count = sum(1 for word, tag in pos_tags if tag.startswith('N'))  # Count nouns
    verb_count = sum(1 for word, tag in pos_tags if tag.startswith('V'))  # Count verbs
    punctuation_count = sum(1 for char in text if char in string.punctuation)  # Count punctuation
    return pd.Series([num_words, num_chars, num_sentences, avg_word_length, sentiment, noun_count, verb_count, punctuation_count])

# Apply preprocessing and feature extraction
df['cleaned_message'] = df['message'].apply(clean_text)
df[['num_words', 'num_chars', 'num_sentences', 'avg_word_length', 'sentiment', 'noun_count', 'verb_count', 'punctuation_count']] = df['cleaned_message'].apply(extract_features)

# Convert text into numerical representation using TF-IDF
vectorizer = TfidfVectorizer()
X_text_features = vectorizer.fit_transform(df['cleaned_message'])

# Combine TF-IDF features with extracted features
X_combined = pd.concat([pd.DataFrame(X_text_features.toarray()), df[['num_words', 'num_chars', 'num_sentences', 'avg_word_length', 'sentiment', 'noun_count', 'verb_count', 'punctuation_count']]], axis=1)

# Define labels
y = df['label']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_combined, y, test_size=0.2, random_state=42)

# Train a Random Forest Classifier
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Make predictions
y_pred = clf.predict(X_test)

# Evaluate the model
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Classification Report:\n", classification_report(y_test, y_pred))

# Save the model and vectorizer
joblib.dump(clf, 'grooming_detection_model.pkl')
joblib.dump(vectorizer, 'tfidf_vectorizer.pkl')

print("Model training complete. Saved as 'grooming_detection_model.pkl'.")
