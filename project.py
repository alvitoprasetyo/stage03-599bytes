import streamlit as st
import requests
import numpy as np
import cv2
from PIL import Image
import time
import tensorflow as tf
import os

# Ubidots Config
UBIDOTS_TOKEN = "BBUS-jsfxoukARnkvGzSfmBBAdtzV60TQF3"
DEVICE_LABEL = "demo-machine"
VARIABLE_LABEL = "led_status"  # Will send numbers 1, 2, or 3

# Load TFLite model
interpreter = tf.lite.Interpreter(model_path="./model/disability_detection.tflite")
interpreter.allocate_tensors()

def predict_image(image):
    try:
        # Convert image to OpenCV format
        img_array = np.array(image.convert('L'))  # Convert to grayscale
        
        # Calculate sharpness
        sharpness = cv2.Laplacian(img_array, cv2.CV_64F).var()
        
        if sharpness < 15:  # Threshold for blur detection
            return np.nan  # Use numpy's nan instead of float('nan')
            
        # Normal preprocessing for valid images
        img_array = np.array(image.resize((224, 224))) / 255.0
        img_array = np.expand_dims(img_array, axis=0).astype(np.float32)
        
        # Run inference
        interpreter.set_tensor(interpreter.get_input_details()[0]['index'], img_array)
        interpreter.invoke()
        return interpreter.get_tensor(interpreter.get_output_details()[0]['index'])[0][0]
        
    except Exception as e:
        print(f"Prediction error: {str(e)}")
        return np.nan

def send_to_ubidots(status_code, status_message):
    """Send status code and status message with timestamp to Ubidots"""
    url = f"https://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}"
    headers = {"X-Auth-Token": UBIDOTS_TOKEN}
    payload = {
        "led_status": status_code,
        "status_info": {
            "value": status_code,
            "context": {
                "message": status_message
            }
        },
        "timestamp": int(time.time() * 1000)
    }
    response = requests.post(url, headers=headers, json=payload)
    print(f"Ubidots Response: {response.json()}")
    return response.json()


# Streamlit UI
st.title("Disability Detection IoT System")
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", width=300)
    
    try:
        prediction = predict_image(image)
        if np.isnan(prediction):
            raise ValueError("Image too blurry or invalid")
            
        confidence_threshold = 0.9  # 90% confidence threshold
        disability_threshold = 0.5  # Original threshold for disability classification
        
        # Get the confidence (higher of prediction or 1-prediction)
        confidence = max(prediction, 1 - prediction)
        
        if confidence < confidence_threshold:
            st.error(f"Low confidence prediction ({confidence:.2%})")
            send_to_ubidots(3, "Gagal memindai")  # Red LED + Message
        elif prediction > disability_threshold:
            st.success(f"Person with disability (Confidence: {prediction:.2%})")
            send_to_ubidots(1, "Pintu dibuka")  # Green LED + Message
        else:
            st.warning(f"Person without disability (Confidence: {1 - prediction:.2%})")
            send_to_ubidots(2, "Silakan gunakan tangga yang tersedia")  # Yellow LED + Message

            
    except Exception as e:
        st.error(f"Error: {str(e)}")
        send_to_ubidots(3, "Gagal memindai")  # Red LED for errors