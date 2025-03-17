from flask import Flask, request, jsonify, render_template
from analyze import get_sentiment, compute_embeddings, classify_email, load_classes, save_class

app = Flask(__name__, template_folder='templates')

@app.route("/")
def home():
    print("Home page")
    return render_template('index.html')


@app.route("/api/v1/sentiment-analysis/", methods=['POST'])
def analysis():
    if request.is_json:
        data = request.get_json()
        sentiment = get_sentiment(data['text'])
        return jsonify({"message": "Data received", "data": data, "sentiment": sentiment}), 200
    else:
        return jsonify({"error": "Invalid Content-Type"}), 400


@app.route("/api/v1/valid-embeddings/", methods=['GET'])
def valid_embeddings():
    embeddings = compute_embeddings()
    formatted_embeddings = []
    for text, vector in embeddings:
        formatted_embeddings.append({
            "text": text,
            "vector": vector.tolist() if hasattr(vector, 'tolist') else vector
        })
    embeddings = formatted_embeddings
    return jsonify({"message": "Valid embeddings fetched", "embeddings": embeddings}), 200


@app.route("/api/v1/classify/", methods=['POST'])
def classify():
    if request.is_json:
        data = request.get_json()
        text = data['text']
        classifications = classify_email(text)
        return jsonify({"message": "Email classified", "classifications": classifications}), 200
    else:
        return jsonify({"error": "Invalid Content-Type"}), 400


@app.route("/api/v1/classify-email/", methods=['GET'])
def classify_with_get():
    text = request.args.get('text')
    classifications = classify_email(text)
    return jsonify({"message": "Email classified", "classifications": classifications}), 200


@app.route("/api/v1/add-class/", methods=['POST'])
def add_class():
    if request.is_json:
        data = request.get_json()
        new_class = data.get("class_name", "").strip()

        if not new_class:
            return jsonify({"error": "Class name cannot be empty"}), 400

        # Load existing classes to prevent duplicates
        existing_classes = load_classes()
        if new_class in existing_classes:
            return jsonify({"message": "Class already exists"}), 400

        # Save the new class
        save_class(new_class)
        return jsonify({"message": f"Class '{new_class}' added successfully"}), 201
    else:
        return jsonify({"error": "Invalid Content-Type"}), 400
        
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=True)