#!/usr/bin/env python3
import requests
import json
import time

# Configuration
MATRIX_URL = "http://localhost:8008"
ROOM_ID = "!MEoQAcdsRWNXPFPOZp:pi-fitness.local"
ACCESS_TOKEN = "syt_Zml0bmVzcy1hZG1pbg_wkEqMTpaLIfSmnEINOPL_3hNpBv"
BRIDGE_URL = "http://localhost:5000/matrix-hook"
API_KEY = "fitness-bridge-secret-2025"

# Sync with Matrix server
def sync_matrix(since_token=None):
    params = {
        "access_token": ACCESS_TOKEN,
        "timeout": 30000,
        "filter": json.dumps({
            "room": {
                "timeline": {
                    "types": ["m.room.message"]
                }
            }
        })
    }
    
    if since_token:
        params["since"] = since_token
    
    try:
        response = requests.get(
            f"{MATRIX_URL}/_matrix/client/r0/sync",
            params=params,
            timeout=35
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Sync failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Sync error: {e}")
        return None

# Main loop
def main():
    print("🚀 Starting Matrix Fitness Listener (Sync Mode)...")
    
    next_batch = None
    processed_events = set()
    
    print("👂 Listening for messages... Press Ctrl+C to stop")
    
    while True:
        try:
            data = sync_matrix(next_batch)
            
            if data:
                next_batch = data.get('next_batch')
                
                # Check for messages in our room
                rooms = data.get('rooms', {}).get('join', {})
                
                if ROOM_ID in rooms:
                    room_data = rooms[ROOM_ID]
                    timeline = room_data.get('timeline', {})
                    events = timeline.get('events', [])
                    
                    for event in events:
                        event_id = event.get('event_id', '')
                        
                        if event_id in processed_events:
                            continue
                        
                        if event['type'] == 'm.room.message':
                            sender = event['sender']
                            body = event['content'].get('body', '')
                            
                            print(f"📧 New message from {sender}: {body}")
                            
                            # Don't process our own messages
                            if sender == "@fitness-admin:pi-fitness.local":
                                print("🚫 Ignoring own message")
                                processed_events.add(event_id)
                                continue
                            
                            # Forward to bridge
                            try:
                                payload = {
                                    "body": body,
                                    "key": API_KEY,
                                    "sender": sender
                                }
                                
                                print(f"🔄 Sending to bridge...")
                                response = requests.post(
                                    f"{BRIDGE_URL}/{ROOM_ID}",
                                    json=payload,
                                    timeout=5
                                )
                                
                                if response.status_code == 200:
                                    result = response.json()
                                    print(f"✅ Workout logged: {result.get('result', {}).get('message', 'Success')}")
                                else:
                                    print(f"❌ Bridge error: {response.status_code}")
                                
                            except Exception as e:
                                print(f"❌ Failed to forward message: {e}")
                            
                            processed_events.add(event_id)
            
        except KeyboardInterrupt:
            print("\n👋 Stopping listener")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
