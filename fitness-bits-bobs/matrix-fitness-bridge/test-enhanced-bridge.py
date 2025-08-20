#!/usr/bin/env python3
"""
Test the enhanced Matrix bridge with various message types
"""

import asyncio
import sys
from nio import AsyncClient

async def send_test_messages():
    """Send test workout messages"""
    client = AsyncClient("http://localhost:8008", "@pi-user:pi-fitness.local")
    
    # Login (you'll need to enter password)
    password = input("Enter pi-user password: ")
    await client.login(password)
    
    room_id = "!DrpxcCGaUYuUbViiLw:pi-fitness.local"
    
    test_messages = [
        "Bench press 80kg 4x8",  # Structured - should use AI or AWS
        "Had a great workout today! Managed to bench 80kg for 4 sets of 8 reps, then did some squats at 100kg for 3 sets of 10",  # Free-form - should use AI
        "Quick run this morning, 5km in about 25 minutes, felt good!",  # Cardio free-form - should use AI
        "BP 80kg 4x8, SQ 100kg 3x10, DL 120kg 1x5",  # Multiple structured exercises
    ]
    
    print("Sending test messages...")
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. Sending: {message}")
        await client.room_send(
            room_id=room_id,
            message_type="m.room.message",
            content={"msgtype": "m.text", "body": message}
        )
        await asyncio.sleep(3)  # Wait between messages
    
    await client.close()
    print("\nTest messages sent! Check Matrix room for responses.")

if __name__ == "__main__":
    asyncio.run(send_test_messages())
