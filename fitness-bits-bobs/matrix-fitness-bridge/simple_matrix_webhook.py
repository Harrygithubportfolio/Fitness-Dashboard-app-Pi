#!/usr/bin/env python3
import requests
import json
import time
from matrix_client.client import MatrixClient
from matrix_client.api import MatrixRequestError

# Configuration - UPDATED with new room ID
MATRIX_URL = "http://localhost:8008"
MATRIX_USERNAME = "@fitness-admin:pi-fitness.local"
MATRIX_PASSWORD = "Ahoithereshipmaet1996!!"
ROOM_ID = "!GQJkRdAVRdMEONAepv:matrix.org"  # NEW unencrypted room
BRIDGE_URL = "http://localhost:5000/matrix-hook"
API_KEY = "fitness-bridge-secret-2025"

def main():
    print("🔗 Connecting to Matrix...")
    
    try:
        client = MatrixClient(MATRIX_URL)
        token = client.login(MATRIX_USERNAME, MATRIX_PASSWORD)
        print(f"✅ Logged in to Matrix")
        
        room = client.join_room(ROOM_ID)
        print(f"✅ Joined room: {ROOM_ID}")
        
        def on_message(room, event):
            print(f"🎯 Event received: {event['type']}")  # Debug
            
            if event['type'] == "m.room.message":
                sender = event['sender']
                body = event['content'].get('body', '')
                
                print(f"📧 Message event - Sender: {sender}, Body: {body}")
                
                # Don't process our own messages
                if sender == MATRIX_USERNAME:
                    print("🚫 Ignoring own message")
                    return
                
                print(f"📨 Processing message from {sender}: {body}")
                
                # Forward to bridge
                try:
                    payload = {
                        "body": body,
                        "key": API_KEY,
                        "sender": sender
                    }
                    
                    print(f"🔄 Sending to bridge: {BRIDGE_URL}/{ROOM_ID}")
                    response = requests.post(
                        f"{BRIDGE_URL}/{ROOM_ID}",
                        json=payload,
                        timeout=5
                    )
                    
                    print(f"✅ Bridge response: {response.status_code} - {response.text}")
                    
                except Exception as e:
                    print(f"❌ Failed to forward message: {e}")
            else:
                print(f"ℹ️ Non-message event: {event['type']}")
        
        room.add_listener(on_message)
        
        print("👂 Listening for messages... Press Ctrl+C to stop")
        client.listen_forever()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
