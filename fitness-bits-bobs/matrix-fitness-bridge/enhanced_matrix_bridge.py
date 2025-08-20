#!/usr/bin/env python3
"""
Enhanced Matrix Bridge with AI Integration - Phase 2
Integrates fast local AI service with existing AWS infrastructure

Features:
- Smart message routing (AI vs AWS)
- Free-form text handling with AI
- Structured message handling with existing AWS
- Enhanced confirmations with AI-generated names
- Backwards compatibility maintained
"""

import asyncio
import aiohttp
import json
import logging
import os
import re
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

# Matrix SDK imports
from nio import AsyncClient, RoomMessageText, MatrixRoom
from nio.events import Event

# Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/matrix-ai-bridge.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedMatrixBridge:
    """Enhanced Matrix bridge with AI integration"""
    
    def __init__(self):
        # Load configuration
        self.load_config()
        
        # Initialize Matrix client
        self.client = AsyncClient(
            homeserver=self.matrix_url,
            user=self.matrix_user_id
        )
        
        # Setup Matrix event handlers
        self.client.add_event_callback(self.message_callback, RoomMessageText)
        
        # Service URLs
        self.ai_service_url = "http://localhost:7000"
        self.aws_webhook_url = "https://w6h9nl1gd7.execute-api.eu-west-2.amazonaws.com/prod/ntfy/workout"
        
        # Message tracking
        self.processed_messages = set()
        
    def load_config(self):
        """Load configuration from environment and .env file"""
        # Try to load from .env file first
        env_file = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
        
        # Load configuration
        self.matrix_url = os.getenv('MATRIX_URL', 'http://localhost:8008')
        self.matrix_user_id = os.getenv('MATRIX_ID', '@fitness-admin:pi-fitness.local')
        self.matrix_password = os.getenv('MATRIX_PW', '')
        self.api_key = os.getenv('API_KEY', 'fitness-bridge-secret-2025')
        self.room_id = "!DrpxcCGaUYuUbViiLw:pi-fitness.local"
        
        # AI service configuration
        self.ai_enabled = os.getenv('ENABLE_AI_PARSING', 'true').lower() == 'true'
        self.ai_timeout = int(os.getenv('AI_TIMEOUT', '10'))
        
        logger.info(f"Configuration loaded - AI enabled: {self.ai_enabled}")
    
    def is_structured_workout(self, message: str) -> bool:
        """Detect if message follows structured format (weight + sets + reps)"""
        # Look for patterns like "80kg 4x8" or "80kg 4 x 8"
        structured_patterns = [
            r'\d+(?:\.\d+)?\s*kg\s+\d+\s*x\s*\d+',  # 80kg 4x8
            r'\d+(?:\.\d+)?\s*kg\s+\d+\s*X\s*\d+',  # 80kg 4X8 (capital X)
            r'\d+(?:\.\d+)?\s*kg\s*,\s*\d+\s*x\s*\d+',  # 80kg, 4x8
        ]
        
        for pattern in structured_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return True
        
        return False
    
    def has_exercise_keywords(self, message: str) -> bool:
        """Check if message contains exercise-related keywords"""
        exercise_keywords = [
            'workout', 'exercise', 'gym', 'training', 'session',
            'bench', 'squat', 'deadlift', 'press', 'curl', 'row',
            'run', 'cycle', 'swim', 'cardio', 'lift', 'weight',
            'set', 'rep', 'kg', 'lb', 'mile', 'minute', 'hour'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in exercise_keywords)
    
    async def check_ai_service_health(self) -> bool:
        """Check if AI service is responding"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(f"{self.ai_service_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('status') == 'healthy'
        except Exception as e:
            logger.warning(f"AI service health check failed: {e}")
        
        return False
    
    async def process_with_ai_service(self, message: str) -> Optional[Dict]:
        """Process message with local AI service"""
        try:
            payload = {"message": message}
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.ai_timeout)) as session:
                async with session.post(
                    f"{self.ai_service_url}/parse-workout",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        if data.get('success'):
                            return data.get('parsed_workout')
                    else:
                        error_text = await response.text()
                        logger.error(f"AI service error ({response.status}): {error_text}")
        
        except asyncio.TimeoutError:
            logger.error(f"AI service timeout after {self.ai_timeout} seconds")
        except Exception as e:
            logger.error(f"AI service request failed: {e}")
        
        return None
    
    async def process_with_aws_lambda(self, message: str) -> Optional[Dict]:
        """Process message with existing AWS Lambda"""
        try:
            payload = {"message": message}
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.post(
                    self.aws_webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        # AWS returns different format, normalize it
                        if 'body' in data:
                            # Parse the body if it's a string
                            body = data['body']
                            if isinstance(body, str):
                                body = json.loads(body)
                            return body
                        return data
                    else:
                        error_text = await response.text()
                        logger.error(f"AWS Lambda error ({response.status}): {error_text}")
        
        except Exception as e:
            logger.error(f"AWS Lambda request failed: {e}")
        
        return None
    
    def format_confirmation_message(self, result: Dict, processing_method: str) -> str:
        """Format confirmation message with enhanced details"""
        exercises = result.get('exercises', [])
        total_volume = result.get('total_volume', 0)
        ai_name = result.get('ai_generated_name', 'Workout Session')
        processing_time = result.get('processing_time_ms', 0)
        
        # Header with AI-generated name
        message_parts = [
            f"✅ **{ai_name}**",
            ""
        ]
        
        # Exercise breakdown
        if exercises:
            message_parts.append("📋 **Exercises:**")
            for i, exercise in enumerate(exercises, 1):
                name = exercise.get('name', 'Unknown')
                weight = exercise.get('weight', 0)
                sets = exercise.get('sets', 0)
                reps = exercise.get('reps', 0)
                volume = exercise.get('volume', weight * sets * reps)
                
                if weight > 0:
                    message_parts.append(f"{i}. {name}: {weight}kg × {sets}×{reps} = {volume:,.0f}kg volume")
                else:
                    message_parts.append(f"{i}. {name}: {sets}×{reps}")
            
            message_parts.append("")
        
        # Summary stats
        message_parts.extend([
            "📊 **Summary:**",
            f"• Total Volume: {total_volume:,.0f}kg",
            f"• Exercises: {len(exercises)}",
            f"• Processing: {processing_method} ({processing_time}ms)",
            ""
        ])
        
        # Workout type and classification
        workout_type = result.get('type', result.get('workout_type', 'Mixed'))
        if workout_type:
            message_parts.append(f"🎯 **Type:** {workout_type}")
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M")
        message_parts.append(f"⏰ Logged at {timestamp}")
        
        return "\n".join(message_parts)
    
    def format_error_message(self, message: str, error: str) -> str:
        """Format error message"""
        return f"""❌ **Workout Logging Failed**

**Original Message:** {message[:100]}{'...' if len(message) > 100 else ''}

**Error:** {error}

**Tip:** Try using format like "Bench press 80kg 4x8" for better parsing."""
    
    async def message_callback(self, room: MatrixRoom, event: RoomMessageText):
        """Handle incoming Matrix messages"""
        # Skip if not in our target room
        if room.room_id != self.room_id:
            return
        
        # Skip our own messages
        if event.sender == self.matrix_user_id:
            return
        
        # Skip already processed messages
        if event.event_id in self.processed_messages:
            return
        
        # Add to processed set
        self.processed_messages.add(event.event_id)
        
        # Get message content
        message = event.body.strip()
        if not message:
            return
        
        # Skip non-workout messages
        if not self.has_exercise_keywords(message):
            logger.info(f"Skipping non-workout message: {message[:50]}...")
            return
        
        logger.info(f"Processing workout message: {message}")
        
        start_time = time.time()
        result = None
        processing_method = "unknown"
        
        # Determine processing strategy
        is_structured = self.is_structured_workout(message)
        ai_available = await self.check_ai_service_health() if self.ai_enabled else False
        
        try:
            if is_structured and not ai_available:
                # Structured format + no AI -> use AWS Lambda
                logger.info("Using AWS Lambda for structured message")
                result = await self.process_with_aws_lambda(message)
                processing_method = "AWS Lambda"
                
            elif self.ai_enabled and ai_available:
                # AI available -> use AI service (handles both structured and free-form)
                logger.info("Using AI service for message processing")
                result = await self.process_with_ai_service(message)
                processing_method = "Local AI"
                
                # If AI fails and message is structured, fallback to AWS
                if not result and is_structured:
                    logger.info("AI failed, falling back to AWS Lambda")
                    result = await self.process_with_aws_lambda(message)
                    processing_method = "AWS Lambda (AI fallback)"
                    
            else:
                # No AI and unstructured -> try AWS anyway
                logger.info("No AI available, trying AWS Lambda")
                result = await self.process_with_aws_lambda(message)
                processing_method = "AWS Lambda (no AI)"
            
            # Send response back to Matrix room
            processing_time = int((time.time() - start_time) * 1000)
            
            if result:
                # Add processing time to result if not present
                if 'processing_time_ms' not in result:
                    result['processing_time_ms'] = processing_time
                
                confirmation = self.format_confirmation_message(result, processing_method)
                await self.send_message(confirmation)
                
                logger.info(f"Workout processed successfully ({processing_time}ms, {processing_method})")
            else:
                error_msg = self.format_error_message(message, "No processing service available or all services failed")
                await self.send_message(error_msg)
                
                logger.error(f"Failed to process workout message")
        
        except Exception as e:
            error_msg = self.format_error_message(message, str(e))
            await self.send_message(error_msg)
            logger.error(f"Error processing message: {e}")
    
    async def send_message(self, message: str):
        """Send message to Matrix room"""
        try:
            await self.client.room_send(
                room_id=self.room_id,
                message_type="m.room.message",
                content={
                    "msgtype": "m.text",
                    "body": message,
                    "format": "org.matrix.custom.html",
                    "formatted_body": message.replace("**", "<strong>").replace("**", "</strong>")
                }
            )
        except Exception as e:
            logger.error(f"Failed to send Matrix message: {e}")
    
    async def start(self):
        """Start the enhanced Matrix bridge"""
        logger.info("Starting Enhanced Matrix Bridge with AI Integration...")
        
        # Check AI service status
        if self.ai_enabled:
            ai_status = await self.check_ai_service_health()
            if ai_status:
                logger.info("✅ AI service is available")
            else:
                logger.warning("⚠️ AI service is not available - will use AWS fallback")
        else:
            logger.info("🔄 AI service disabled - using AWS Lambda only")
        
        # Login to Matrix
        try:
            login_response = await self.client.login(self.matrix_password)
            if not login_response.user_id:
                logger.error(f"Failed to login to Matrix: {login_response}")
                return
            
            logger.info(f"✅ Logged in to Matrix as {login_response.user_id}")
            
            # Join the room if not already joined
            try:
                await self.client.join(self.room_id)
                logger.info(f"✅ Joined room {self.room_id}")
            except Exception as e:
                logger.info(f"Already in room or join failed: {e}")
            
            # Send startup message
            startup_msg = f"""🚀 **Enhanced Fitness Bridge Started**

• AI Service: {'✅ Available' if await self.check_ai_service_health() else '❌ Unavailable'}
• AWS Lambda: ✅ Available
• Processing: Smart routing enabled
• Time: {datetime.now().strftime('%H:%M:%S')}

Ready to log workouts! 💪"""
            
            await self.send_message(startup_msg)
            
            # Start sync loop
            logger.info("🔄 Starting Matrix sync...")
            await self.client.sync_forever(timeout=30000)
            
        except Exception as e:
            logger.error(f"Failed to start Matrix bridge: {e}")
        finally:
            await self.client.close()

async def main():
    """Main entry point"""
    bridge = EnhancedMatrixBridge()
    
    try:
        await bridge.start()
    except KeyboardInterrupt:
        logger.info("Bridge stopped by user")
    except Exception as e:
        logger.error(f"Bridge crashed: {e}")

if __name__ == "__main__":
    asyncio.run(main())