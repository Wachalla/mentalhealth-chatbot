"""
Conversation History Management Service
Handles retrieval and management of conversation history for context-aware AI responses
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import sqlite3
import os

@dataclass
class ConversationMessage:
    """Represents a single message in conversation history"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    user_id: str
    session_id: Optional[str] = None
    message_type: str = "chat"  # "chat", "activity_start", "activity_complete", etc.
    metadata: Optional[Dict] = None

class ConversationHistoryManager:
    """Manages conversation history storage and retrieval"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Default to database directory
            db_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, 'conversation_history.db')
        
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize SQLite database for conversation history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS conversation_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        session_id TEXT,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        timestamp DATETIME NOT NULL,
                        message_type TEXT DEFAULT 'chat',
                        metadata TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes for better performance
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_user_id ON conversation_messages(user_id)
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_timestamp ON conversation_messages(timestamp)
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_user_timestamp ON conversation_messages(user_id, timestamp)
                ''')
                
                conn.commit()
        except Exception as e:
            print(f"Warning: Could not initialize conversation history database: {e}")
    
    def add_message(self, message: ConversationMessage) -> bool:
        """
        Add a message to conversation history
        
        Args:
            message: ConversationMessage to add
            
        Returns:
            True if successfully added
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                metadata_json = json.dumps(message.metadata) if message.metadata else None
                
                conn.execute('''
                    INSERT INTO conversation_messages 
                    (user_id, session_id, role, content, timestamp, message_type, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    message.user_id,
                    message.session_id,
                    message.role,
                    message.content,
                    message.timestamp.isoformat(),
                    message.message_type,
                    metadata_json
                ))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding message to history: {e}")
            return False
    
    def get_recent_messages(self, user_id: str, limit: int = 5, session_id: Optional[str] = None) -> List[Dict]:
        """
        Get recent messages for a user
        
        Args:
            user_id: User identifier
            limit: Maximum number of messages to retrieve
            session_id: Optional session ID to filter by
            
        Returns:
            List of message dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                if session_id:
                    cursor = conn.execute('''
                        SELECT role, content, timestamp, message_type, metadata
                        FROM conversation_messages
                        WHERE user_id = ? AND session_id = ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                    ''', (user_id, session_id, limit))
                else:
                    cursor = conn.execute('''
                        SELECT role, content, timestamp, message_type, metadata
                        FROM conversation_messages
                        WHERE user_id = ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                    ''', (user_id, limit))
                
                messages = []
                for row in cursor.fetchall():
                    message_dict = {
                        'role': row['role'],
                        'content': row['content'],
                        'timestamp': row['timestamp'],
                        'message_type': row['message_type']
                    }
                    
                    # Parse metadata if present
                    if row['metadata']:
                        try:
                            message_dict['metadata'] = json.loads(row['metadata'])
                        except:
                            pass
                    
                    messages.append(message_dict)
                
                # Return in chronological order (oldest first)
                return list(reversed(messages))
                
        except Exception as e:
            print(f"Error retrieving conversation history: {e}")
            return []
    
    def get_conversation_summary(self, user_id: str, hours: int = 24) -> Dict:
        """
        Get summary of recent conversation activity
        
        Args:
            user_id: User identifier
            hours: Number of hours to look back
            
        Returns:
            Dictionary with conversation statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT 
                        COUNT(*) as total_messages,
                        COUNT(CASE WHEN role = 'user' THEN 1 END) as user_messages,
                        COUNT(CASE WHEN role = 'assistant' THEN 1 END) as assistant_messages,
                        MIN(timestamp) as first_message,
                        MAX(timestamp) as last_message
                    FROM conversation_messages
                    WHERE user_id = ? 
                    AND timestamp >= datetime('now', '-{} hours')
                '''.format(hours), (user_id,))
                
                row = cursor.fetchone()
                
                if row and row[0] > 0:
                    return {
                        'total_messages': row[0],
                        'user_messages': row[1],
                        'assistant_messages': row[2],
                        'first_message': row[3],
                        'last_message': row[4],
                        'hours_covered': hours
                    }
                else:
                    return {
                        'total_messages': 0,
                        'user_messages': 0,
                        'assistant_messages': 0,
                        'hours_covered': hours
                    }
                    
        except Exception as e:
            print(f"Error getting conversation summary: {e}")
            return {'total_messages': 0, 'hours_covered': hours}
    
    def clear_old_messages(self, days: int = 30) -> int:
        """
        Clear old messages from database
        
        Args:
            days: Number of days to keep messages
            
        Returns:
            Number of messages deleted
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    DELETE FROM conversation_messages
                    WHERE timestamp < datetime('now', '-{} days')
                '''.format(days))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                return deleted_count
                
        except Exception as e:
            print(f"Error clearing old messages: {e}")
            return 0
    
    def get_user_sessions(self, user_id: str, days: int = 7) -> List[str]:
        """
        Get list of session IDs for a user
        
        Args:
            user_id: User identifier
            days: Number of days to look back
            
        Returns:
            List of session IDs
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT DISTINCT session_id
                    FROM conversation_messages
                    WHERE user_id = ? 
                    AND session_id IS NOT NULL
                    AND timestamp >= datetime('now', '-{} days')
                    ORDER BY MAX(timestamp) DESC
                '''.format(days), (user_id,))
                
                sessions = [row[0] for row in cursor.fetchall()]
                return sessions
                
        except Exception as e:
            print(f"Error getting user sessions: {e}")
            return []

# Singleton instance for easy import
conversation_history_manager = ConversationHistoryManager()

# Helper functions for integration with AIProcessor
def add_user_message(user_id: str, content: str, session_id: Optional[str] = None) -> bool:
    """Add a user message to conversation history"""
    message = ConversationMessage(
        role="user",
        content=content,
        timestamp=datetime.now(),
        user_id=user_id,
        session_id=session_id
    )
    return conversation_history_manager.add_message(message)

def add_assistant_message(user_id: str, content: str, session_id: Optional[str] = None, metadata: Optional[Dict] = None) -> bool:
    """Add an assistant message to conversation history"""
    message = ConversationMessage(
        role="assistant",
        content=content,
        timestamp=datetime.now(),
        user_id=user_id,
        session_id=session_id,
        metadata=metadata
    )
    return conversation_history_manager.add_message(message)

def get_conversation_history(user_id: str, limit: int = 5, session_id: Optional[str] = None) -> List[Dict]:
    """Get recent conversation history for a user"""
    return conversation_history_manager.get_recent_messages(user_id, limit, session_id)

def format_history_for_prompt(history: List[Dict]) -> List[Dict]:
    """
    Format conversation history for prompt builder
    
    Args:
        history: List of message dictionaries
        
    Returns:
        Formatted history suitable for PromptComponents
    """
    formatted_history = []
    
    for msg in history:
        formatted_msg = {
            'role': msg['role'],
            'content': msg['content'],
            'timestamp': msg['timestamp']
        }
        
        # Add metadata if present
        if 'metadata' in msg:
            formatted_msg['metadata'] = msg['metadata']
        
        formatted_history.append(formatted_msg)
    
    return formatted_history
