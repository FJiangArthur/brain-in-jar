#!/usr/bin/env python3
"""
Conversation Logger - Logging and history management for the Brain in a Jar experiment
"""

import sqlite3
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from ..core.emotion_engine import Emotion
import random

class ConversationLogger:
    """Handles logging and replay of AI conversations"""
    
    def __init__(self, db_path: str = "logs/conversations.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize the database with required tables"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Drop existing tables to ensure clean state
        cursor.execute("DROP TABLE IF EXISTS messages")
        cursor.execute("DROP TABLE IF EXISTS system_state")
        cursor.execute("DROP TABLE IF EXISTS sessions")
        
        # Create sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                mode TEXT NOT NULL,
                model TEXT NOT NULL,
                start_time DATETIME NOT NULL,
                end_time DATETIME,
                total_messages INTEGER DEFAULT 0,
                total_crashes INTEGER DEFAULT 0
            )
        ''')
        
        # Create messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                emotion TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        ''')
        
        # Create system_state table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_state (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                memory_usage REAL,
                cpu_usage REAL,
                temperature REAL,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def start_session(self, mode: str, model: str) -> str:
        """Start a new conversation session"""
        timestamp = int(time.time())
        session_id = f"{mode}_{timestamp}"
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO sessions (session_id, mode, model, start_time)
                VALUES (?, ?, ?, datetime('now'))
            ''', (session_id, mode, model))
            conn.commit()
            conn.close()
            return session_id
        except sqlite3.IntegrityError:
            # If session_id already exists, try again with a random suffix
            session_id = f"{mode}_{timestamp}_{random.randint(1000, 9999)}"
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO sessions (session_id, mode, model, start_time)
                VALUES (?, ?, ?, datetime('now'))
            ''', (session_id, mode, model))
            conn.commit()
            conn.close()
            return session_id
    
    def end_session(self, session_id: str):
        """End a conversation session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE sessions 
            SET end_time = datetime('now')
            WHERE session_id = ?
        ''', (session_id,))
        conn.commit()
        conn.close()
    
    def log_message(self, session_id: str, role: str, content: str, emotion: str = None):
        """Log a message to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO messages (session_id, timestamp, role, content, emotion)
            VALUES (?, datetime('now'), ?, ?, ?)
        ''', (session_id, role, content, emotion))
        conn.commit()
        conn.close()
    
    def log_system_state(self, session_id: str, memory_usage: float, cpu_usage: float, temperature: float):
        """Log system state metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO system_state (session_id, timestamp, memory_usage, cpu_usage, temperature)
            VALUES (?, datetime('now'), ?, ?, ?)
        ''', (session_id, memory_usage, cpu_usage, temperature))
        conn.commit()
        conn.close()
    
    def log_visual_analysis(self, session_id: str, frame_number: int, 
                           analysis: str, mood: str, 
                           image_path: str = None, metadata: Dict = None):
        """Log visual analysis data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute('''
            INSERT INTO visual_logs 
            (session_id, timestamp, frame_number, analysis, mood, image_path, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (session_id, datetime.now().isoformat(), frame_number, 
              analysis, mood, image_path, metadata_json))
        
        conn.commit()
        conn.close()
    
    def get_session_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM conversations 
            WHERE session_id = ? 
            ORDER BY timestamp
        ''', (session_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        columns = ['id', 'session_id', 'timestamp', 'message_type', 'content', 
                  'metadata', 'mood', 'crash_count', 'network_status']
        
        history = []
        for row in rows:
            entry = dict(zip(columns, row))
            if entry['metadata']:
                entry['metadata'] = json.loads(entry['metadata'])
            history.append(entry)
        
        return history
    
    def get_visual_history(self, session_id: str) -> List[Dict]:
        """Get visual analysis history for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM visual_logs 
            WHERE session_id = ? 
            ORDER BY timestamp
        ''', (session_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        columns = ['id', 'session_id', 'timestamp', 'frame_number', 
                  'analysis', 'mood', 'image_path', 'metadata']
        
        history = []
        for row in rows:
            entry = dict(zip(columns, row))
            if entry['metadata']:
                entry['metadata'] = json.loads(entry['metadata'])
            history.append(entry)
        
        return history
    
    def list_sessions(self, limit: int = 20) -> List[Dict]:
        """List recent conversation sessions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM sessions 
            ORDER BY start_time DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        columns = ['session_id', 'start_time', 'end_time', 'mode', 
                  'model_path', 'total_messages', 'total_crashes']
        
        sessions = []
        for row in rows:
            sessions.append(dict(zip(columns, row)))
        
        return sessions
    
    def search_conversations(self, query: str, session_id: str = None) -> List[Dict]:
        """Search conversations by content"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if session_id:
            cursor.execute('''
                SELECT * FROM conversations 
                WHERE session_id = ? AND content LIKE ?
                ORDER BY timestamp
            ''', (session_id, f'%{query}%'))
        else:
            cursor.execute('''
                SELECT * FROM conversations 
                WHERE content LIKE ?
                ORDER BY timestamp DESC
            ''', (f'%{query}%',))
        
        rows = cursor.fetchall()
        conn.close()
        
        columns = ['id', 'session_id', 'timestamp', 'message_type', 'content', 
                  'metadata', 'mood', 'crash_count', 'network_status']
        
        results = []
        for row in rows:
            entry = dict(zip(columns, row))
            if entry['metadata']:
                entry['metadata'] = json.loads(entry['metadata'])
            results.append(entry)
        
        return results
    
    def export_session(self, session_id: str, format: str = 'json') -> str:
        """Export session data to file"""
        history = self.get_session_history(session_id)
        visual_history = self.get_visual_history(session_id)
        
        export_data = {
            'session_id': session_id,
            'conversations': history,
            'visual_logs': visual_history,
            'exported_at': datetime.now().isoformat()
        }
        
        if format == 'json':
            filename = f"logs/export_{session_id}.json"
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
        elif format == 'txt':
            filename = f"logs/export_{session_id}.txt"
            with open(filename, 'w') as f:
                f.write(f"Brain in Jar - Session Export\n")
                f.write(f"Session ID: {session_id}\n")
                f.write(f"Exported: {export_data['exported_at']}\n")
                f.write("=" * 50 + "\n\n")
                
                for entry in history:
                    f.write(f"[{entry['timestamp']}] {entry['message_type'].upper()}\n")
                    f.write(f"Mood: {entry['mood'] or 'Unknown'}\n")
                    f.write(f"Content: {entry['content']}\n\n")
                
                if visual_history:
                    f.write("\nVisual Analysis History:\n")
                    f.write("=" * 30 + "\n")
                    for entry in visual_history:
                        f.write(f"[{entry['timestamp']}] Frame {entry['frame_number']}\n")
                        f.write(f"Mood: {entry['mood']}\n")
                        f.write(f"Analysis: {entry['analysis']}\n\n")
        
        return filename
    
    def get_session_stats(self, session_id: str) -> Dict:
        """Get statistics for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get message stats
        cursor.execute('''
            SELECT COUNT(*), message_type FROM conversations 
            WHERE session_id = ? 
            GROUP BY message_type
        ''', (session_id,))
        message_stats = dict(cursor.fetchall())
        
        # Get mood distribution
        cursor.execute('''
            SELECT COUNT(*), mood FROM conversations 
            WHERE session_id = ? AND mood IS NOT NULL
            GROUP BY mood
        ''', (session_id,))
        mood_stats = dict(cursor.fetchall())
        
        # Get crash events
        cursor.execute('''
            SELECT COUNT(*) FROM conversations 
            WHERE session_id = ? AND message_type = 'CRASH'
        ''', (session_id,))
        crash_count = cursor.fetchone()[0]
        
        # Get visual analysis stats
        cursor.execute('''
            SELECT COUNT(*) FROM visual_logs 
            WHERE session_id = ?
        ''', (session_id,))
        visual_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'message_stats': message_stats,
            'mood_distribution': mood_stats,
            'total_crashes': crash_count,
            'visual_analyses': visual_count
        }
    
    def cleanup_old_sessions(self, days_old: int = 30):
        """Clean up sessions older than specified days"""
        cutoff_date = datetime.now().replace(day=datetime.now().day - days_old).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get old session IDs
        cursor.execute('''
            SELECT session_id FROM sessions 
            WHERE start_time < ?
        ''', (cutoff_date,))
        old_sessions = [row[0] for row in cursor.fetchall()]
        
        # Delete conversations for old sessions
        cursor.execute('''
            DELETE FROM conversations 
            WHERE session_id IN (
                SELECT session_id FROM sessions 
                WHERE start_time < ?
            )
        ''', (cutoff_date,))
        
        # Delete visual logs for old sessions
        cursor.execute('''
            DELETE FROM visual_logs 
            WHERE session_id IN (
                SELECT session_id FROM sessions 
                WHERE start_time < ?
            )
        ''', (cutoff_date,))
        
        # Delete old sessions
        cursor.execute('''
            DELETE FROM sessions 
            WHERE start_time < ?
        ''', (cutoff_date,))
        
        conn.commit()
        conn.close()
        
        return len(old_sessions)

class ConversationReplayer:
    """Replays conversation logs with timing"""
    
    def __init__(self, logger: ConversationLogger):
        self.logger = logger
    
    def replay_session(self, session_id: str, speed_multiplier: float = 1.0):
        """Replay a conversation session with original timing"""
        history = self.logger.get_session_history(session_id)
        visual_history = self.logger.get_visual_history(session_id)
        
        if not history:
            print(f"No conversation history found for session {session_id}")
            return
        
        print(f"Replaying session: {session_id}")
        print("=" * 50)
        
        # Merge and sort by timestamp
        all_events = []
        
        for entry in history:
            all_events.append({
                'timestamp': entry['timestamp'],
                'type': 'conversation',
                'data': entry
            })
        
        for entry in visual_history:
            all_events.append({
                'timestamp': entry['timestamp'],
                'type': 'visual',
                'data': entry
            })
        
        all_events.sort(key=lambda x: x['timestamp'])
        
        # Replay with timing
        start_time = None
        last_time = None
        
        for event in all_events:
            event_time = datetime.fromisoformat(event['timestamp'])
            
            if start_time is None:
                start_time = event_time
                last_time = event_time
            else:
                # Calculate delay
                real_delay = (event_time - last_time).total_seconds()
                replay_delay = real_delay / speed_multiplier
                
                if replay_delay > 0:
                    time.sleep(min(replay_delay, 5))  # Cap at 5 seconds
                
                last_time = event_time
            
            # Display event
            if event['type'] == 'conversation':
                data = event['data']
                print(f"\n[{event_time.strftime('%H:%M:%S')}] {data['message_type']}")
                if data['mood']:
                    print(f"Mood: {data['mood']}")
                print(f"Content: {data['content'][:200]}...")
            elif event['type'] == 'visual':
                data = event['data']
                print(f"\n[{event_time.strftime('%H:%M:%S')}] VISUAL_ANALYSIS Frame #{data['frame_number']}")
                print(f"Mood: {data['mood']}")
                print(f"Analysis: {data['analysis'][:100]}...")
    
    def generate_summary(self, session_id: str) -> str:
        """Generate a summary of the conversation session"""
        stats = self.logger.get_session_stats(session_id)
        history = self.logger.get_session_history(session_id)
        
        if not history:
            return "No conversation data found."
        
        summary = f"Session Summary: {session_id}\n"
        summary += "=" * 40 + "\n\n"
        
        # Basic stats
        summary += f"Total Messages: {sum(stats['message_stats'].values())}\n"
        summary += f"Total Crashes: {stats['total_crashes']}\n"
        summary += f"Visual Analyses: {stats['visual_analyses']}\n\n"
        
        # Mood distribution
        if stats['mood_distribution']:
            summary += "Mood Distribution:\n"
            for mood, count in stats['mood_distribution'].items():
                summary += f"  {mood}: {count}\n"
            summary += "\n"
        
        # Key moments
        summary += "Key Moments:\n"
        crash_events = [h for h in history if h['message_type'] == 'CRASH']
        if crash_events:
            summary += f"  First crash: {crash_events[0]['timestamp']}\n"
            summary += f"  Last crash: {crash_events[-1]['timestamp']}\n"
        
        return summary