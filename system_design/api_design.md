# Food Nutrition Application API: Ranking System Design

## 1. Objective

The goal of this project is to create an API that estimates the calories of a food item based on an image. This API will either return a single prediction if the model is confident or multiple (top 5) predictions if the confidence is low. The API will serve as the backend for a mobile application.

**Key functionalities of the API:**
- **Single Prediction**: If the model is confident enough, it returns the estimated calories of the food item.
- **Top 5 Predictions**: If the model’s confidence is low, it returns the top 5 most likely food items, with their respective calorie estimates.

---

## 2. Assumptions

- **Annotated Image Dataset**: Pre-annotated food images are available, and annotators are available to assist with maintaining the quality of this data.
- **External AI Model**: The AI team has already developed a machine learning model capable of recognizing food items in images and returning predictions with confidence scores.
- **Image Quality**: The incoming images are of sufficient quality for the model to make reliable predictions.
- **Mobile App Integration**: The mobile app will send images and display the results from the API.

---

## 3. System Design Components

Here’s a breakdown of the core components:

### 1. API Gateway
- **Responsibility**: It handles incoming requests from the mobile app, specifically receiving the image and forwarding the request to the prediction services.

### 2. Image Preprocessing
- **Responsibility**: Standardizes and normalizes the incoming images for the model.
    - **Functions**: Resize, crop, normalize, and apply any necessary transformations.
    - **Tools**: TensorFlow etc.

### 3. Food Classification Model
- **Responsibility**: This machine learning model is responsible for classifying the food item from the image.
    - **Input**: The preprocessed image.
    - **Output**: A food label and its associated confidence score.

### 4. Confidence Scoring & Threshold
- **Responsibility**: Evaluates the confidence score returned by the model.
    - **If confidence > threshold**: Return the predicted food item with estimated calories.
    - **If confidence < threshold**: Return the top 5 predictions sorted by confidence.

### 5. Ranking / Recommendation Engine
- **Responsibility**: If the model is uncertain, this engine generates the top 5 most likely predictions based on the likelihoods provided by the model.
    - **Output**: A ranked list of food items with calorie estimates.

### 6. Database
- **Responsibility**: Stores food item data, calorie information, and historical predictions.
    - **Uses**: Data logging, model retraining, and tracking predictions.
    - **Technology**: PostgreSQL, MongoDB, or other databases as needed.

### 7. Batch Processing System
- **Responsibility**: Manages tasks such as model retraining, augmenting datasets, and handling large-scale predictions.
    - **Tools**: Apache Kafka, or similar job queues for background processing.

---

## 4. System Flow

1. **Client Sends Request**: The mobile app sends a food image to the API via the API Gateway.
2. **Image Preprocessing**: The image is passed through the preprocessing pipeline to standardize and prepare it for the model.
3. **Model Inference**: The preprocessed image is passed to the food classification model, which generates a prediction with a confidence score.
4. **Confidence Evaluation**: The confidence score is checked. If it's high enough, the model returns the predicted food item and calories.
5. **Top 5 Predictions**: If the confidence score is low, the recommendation engine generates and returns the top 5 predictions based on the model's output.
6. **Database Logging**: The predictions are logged for analytics and model retraining purposes.
7. **Background Processing**: The batch processing system periodically retrains the model using new data.

---

## 5. Diagram

Below is the diagram illustrating the system architecture. It includes components like the **API Gateway**, **Image Preprocessing**, **Food Classification Model**, **Ranking Engine**, **Database**, and **Batch Processing** system.

```plaintext
+-------------------+        +----------------+        +-------------------+
|   Mobile Client   | ---->  |   API Gateway  | ---->  | Image Preprocessing |
+-------------------+        +----------------+        +-------------------+
                                       |
                                       v
                              +--------------------+    
                              | Food Classification |
                              |        Model         |
                              +--------------------+
                                       |
                                       v
                           +------------------------+    +----------------------+
                           | Confidence Scoring &    |<---|   Recommendation     |
                           | Thresholding            |    |     Engine           |
                           +------------------------+    +----------------------+
                                       |
                                       v
                                +-------------+
                                | Database    |
                                | (Logging)   |
                                +-------------+
                                       |
                                       v
                         +----------------------------+
                         | Batch Processing System    |
                         +----------------------------+
``` 

## 6. Edge Case Handling

- **Low Confidence**: If the model's confidence is low (e.g., due to poor image quality or ambiguous food items), the system will return the top 5 predictions.
- **Unclear or Distorted Images**: Implement fallback solutions that handle unclear or non-recognizable food items. For example, if the system cannot identify the food item, it will return a message like "Unable to recognize food item."
- **Multiple Food Items in One Image**: The system can identify individual food components and return multiple predictions.
- **Bad Data**: Implement data validation checks to ensure that the incoming images are of acceptable quality and format.

## 7. Technologies

- **API Gateway**: AWS API Gateway, Nginx, or FastAPI (for Python-based systems).
- **Image Preprocessing**: TensorFlow, or PyTorch for preprocessing and transformations.
- **Machine Learning Model**: Pre-trained CNN models like ResNet or MobileNet.
- **Database**: PostgreSQL, MySQL, MongoDB for data storage.
- **Batch Processing**: Kafka for job scheduling and model retraining.
- **Containerization**: Docker for deploying API services.