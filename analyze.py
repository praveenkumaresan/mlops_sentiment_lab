import os 
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import numpy as np

sentiment_pipeline = pipeline("sentiment-analysis")
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')


CLASS_FILE = "classes.txt"

def load_classes():
    """Load classification labels from a file."""
    if not os.path.exists(CLASS_FILE):
        return ["Work", "Sports", "Food"]  # Default classes if file doesn't exist

    with open(CLASS_FILE, "r") as f:
        classes = [line.strip() for line in f.readlines()]
    return classes
    
def save_class(new_class):
    """Append a new class to the file if it does not already exist."""
    existing_classes = load_classes()
    if new_class not in existing_classes:
        with open(CLASS_FILE, "a") as f:
            f.write(new_class + "\n")
            
def get_sentiment(text):
    response = sentiment_pipeline(text)
    return response

def compute_embeddings():
    """Compute embeddings for all loaded classes."""
    classes = load_classes()
    embeddings = model.encode(classes)
    return zip(classes, embeddings)

def classify_email(text):
    """Classify email based on similarity to class embeddings."""
    text_embedding = model.encode([text])[0]  # Encode input text
    class_embeddings = compute_embeddings()   # Get class embeddings

    results = []
    for class_name, class_embedding in class_embeddings:
        # Compute cosine similarity between input text and class embedding
        similarity = np.dot(text_embedding, class_embedding) / (np.linalg.norm(text_embedding) * np.linalg.norm(class_embedding))
        results.append({
            "class": class_name,
            "similarity": float(similarity)  # Convert tensor to float for JSON serialization
        })

    # Sort by similarity score in descending order
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results