#!/usr/bin/env python3
"""
Matrix to AWS Lambda Bridge for Fitness Logging
Receives Matrix messages and forwards workout data to AWS Lambda
"""

import requests
import json
import re
from flask import Flask, request
import os

app = Flask(__name__)

# Configuration
AWS_WEBHOOK_URL = "https://w6h9nl1gd7.execute-api.eu-west-2.amazonaws.com/prod/ntfy/workout"
MATRIX_URL = "http://localhost:8008"
MATRIX_TOKEN = None  # We'll get this when needed
API_KEY = "fitness-bridge-secret-2025"

def get_matrix_token():
    """Get Matrix access token for sending messages"""
    global MATRIX_TOKEN
    if MATRIX_TOKEN:
        return MATRIX_TOKEN
        
    try:
        response = requests.post(f"{MATRIX_URL}/_matrix/client/r0/login", json={
            "type": "m.login.password",
            "user": "fitness-admin",
            "password": "Ahoithereshipmaet1996!!"
        })
        
        if response.status_code == 200:
            MATRIX_TOKEN = response.json()["access_token"]
            return MATRIX_TOKEN
    except Exception as e:
        print(f"Failed to get Matrix token: {e}")
    
    return None

def send_matrix_message(room_id, message):
    """Send message directly to Matrix room"""
    try:
        token = get_matrix_token()
        if not token:
            print("No Matrix token available")
            return False
            
        url = f"{MATRIX_URL}/_matrix/client/r0/rooms/{room_id}/send/m.room.message"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "msgtype": "m.text",
            "body": message
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            print(f"✅ Sent Matrix message: {message}")
            return True
        else:
            print(f"❌ Failed to send Matrix message: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Matrix message error: {e}")
        return False

def is_workout_message(text):
    """Check if message looks like a workout"""
    workout_pattern = r'\b\w+\s+\d+kg\s+\d+x\d+\b'
    return re.search(workout_pattern, text, re.IGNORECASE) is not None

def send_to_aws_lambda(workout_text):
    """Forward workout to AWS Lambda and get response"""
    try:
        payload = {
            "message": workout_text,
            "source": "matrix"
        }
        
        response = requests.post(
            AWS_WEBHOOK_URL, 
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            return {"error": f"AWS Lambda returned {response.status_code}"}
            
    except Exception as e:
        return {"error": str(e)}

@app.route('/matrix-hook/<room_id>', methods=['POST'])
def handle_matrix_message(room_id):
    """Handle incoming Matrix webhook messages"""
    try:
        data = request.get_json()
        
        # Verify API key
        if data.get('key') != API_KEY:
            return {"error": "Unauthorized"}, 401
        
        message_body = data.get('body', '')
        
        print(f"Matrix message: {message_body}")
        
        # Check if it's a workout message
        if is_workout_message(message_body):
            print(f"Detected workout: {message_body}")
            
            # Send to AWS Lambda
            result = send_to_aws_lambda(message_body)
            
            # Create confirmation message
            if result.get('error'):
                confirmation = f"❌ Error logging workout: {result['error']}"
            else:
                # Get the formatted message from AWS Lambda
                aws_message = result.get('message', '')
                if aws_message:
                    confirmation = aws_message
                else:
                    total_volume = result.get('total_volume', 'Unknown')
                    confirmation = f"✅ Workout logged! Total volume: {total_volume}kg"
            
            # Send confirmation back to Matrix room
            send_matrix_message(room_id, confirmation)
            
            return {
                "status": "processed", 
                "result": result
            }
        else:
            print(f"Not a workout message, ignoring: {message_body}")
            return {"status": "ignored", "reason": "Not a workout message"}
            
    except Exception as e:
        print(f"Error processing Matrix message: {e}")
        return {"error": str(e)}, 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "matrix-aws-bridge"}

if __name__ == '__main__':
    print("Starting Matrix-AWS Bridge...")
    app.run(host='0.0.0.0', port=5000, debug=False)
