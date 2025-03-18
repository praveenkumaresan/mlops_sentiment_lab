# MLOps Homework 2: Email Classification Solution

### Overview

This document describes the modifications made to the email classification system to support dynamic class updates and provides a demonstration with screenshots.

### Solution Implementation

#### 1. Removing Hardcoded Classification Labels

Previously, classification labels were hardcoded in analyze.py:

```
EMAIL_CLASSES = ["Work", "Sports", "Food"]
```

Modification:

Classification labels are now stored in a file (classes.txt), allowing dynamic updates.

#### 2. Loading Classification Labels Dynamically from a File

Implemented a function to read classification labels from classes.txt:

```python
import os

CLASS_FILE = "classes.txt"

def load_classes():
    """Load classification labels from a file."""
    if not os.path.exists(CLASS_FILE):
        return ["Work", "Sports", "Food"]  # Default classes if file doesn't exist
    
    with open(CLASS_FILE, "r") as f:
        classes = [line.strip() for line in f.readlines()]
    return classes
```

#### 3. Enabling Class Updates via API

A new API endpoint allows users to add classifications dynamically.

API Endpoint:

```python
@app.route("/api/v1/add-class/", methods=['POST'])
def add_class():
    if request.is_json:
        data = request.get_json()
        new_class = data.get("class_name", "").strip()

        if not new_class:
            return jsonify({"error": "Class name cannot be empty"}), 400

        existing_classes = load_classes()
        if new_class in existing_classes:
            return jsonify({"message": "Class already exists"}), 400

        save_class(new_class)
        return jsonify({"message": f"Class '{new_class}' added successfully"}), 201
    else:
        return jsonify({"error": "Invalid Content-Type"}), 400
```

#### 4. Updating Classification Logic

The compute_embeddings() function now loads classifications dynamically:

```
def compute_embeddings():
    """Compute embeddings for all loaded classes."""
    classes = load_classes()
    embeddings = model.encode(classes)
    return zip(classes, embeddings)
```

#### 5. End-to-End Testing and Demonstration

##### Step 1: Add a New Classification Label

Request:

```
curl -X POST "http://localhost:3000/api/v1/add-class/" \
     -H "Content-Type: application/json" \
     -d '{"class_name": "Finance"}'
```
Response:
```json
{
  "message": "Class 'Finance' added successfully"
}
```


##### Step 2: Verify Classification with New Label

Request:
```
curl -X POST "http://localhost:3000/api/v1/classify/" \
     -H "Content-Type: application/json" \
     -d '{"text": "This is an investment report about stocks"}'
```

Response:

```json 
{
  "message": "Email classified",
  "classifications": [
    {"class": "Finance", "similarity": 0.89},
    {"class": "Work", "similarity": 0.75}
  ]
}
```

### Screenshots

![Response.png](Response.png)

### Conclusion

This implementation allows users to dynamically update classification labels without modifying the code. The modifications improve flexibility and scalability, making the email classification system more adaptable for real-world applications.
