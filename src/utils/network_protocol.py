import json
import socket
import threading
import time
import queue
from datetime import datetime
from typing import Dict, Optional, Callable
import logging

class NetworkProtocol:
    def __init__(self, node_id: str, port: int = 8888):
        self.node_id = node_id
        self.port = port
        self.server_socket = None
        self.connections = {}  # peer_id -> socket
        self.message_queue = queue.Queue()
        self.running = False
        self.sequence = 0
        self.crash_count = 0
        self.message_handlers = {}
        
        # Setup logging
        logging.basicConfig(
            filename='logs/neural_activity.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('neural_link')
        
    def create_message(self, msg_type: str, content: str, metadata: Dict = None) -> Dict:
        """Create a standardized message"""
        self.sequence += 1
        message = {
            "type": msg_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "sender_id": self.node_id,
            "content": content,
            "crash_count": self.crash_count,
            "sequence": self.sequence
        }
        if metadata:
            message.update(metadata)
        return message
    
    def start_server(self):
        """Start listening for incoming connections"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(5)
        self.running = True
        
        def accept_connections():
            while self.running:
                try:
                    client_socket, addr = self.server_socket.accept()
                    threading.Thread(
                        target=self.handle_connection, 
                        args=(client_socket, addr),
                        daemon=True
                    ).start()
                except socket.error:
                    break
        
        threading.Thread(target=accept_connections, daemon=True).start()
        self.logger.info(f"Neural link server started on port {self.port}")
    
    def connect_to_peer(self, peer_ip: str, peer_port: int = 8888, timeout: int = 5) -> bool:
        """Connect to another neural node"""
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.settimeout(timeout)
            peer_socket.connect((peer_ip, peer_port))
            
            # Send identification
            intro_msg = self.create_message("NEURAL_HANDSHAKE", f"Connecting from {self.node_id}")
            self.send_raw_message(peer_socket, intro_msg)
            
            # Start handling this connection
            threading.Thread(
                target=self.handle_connection,
                args=(peer_socket, (peer_ip, peer_port)),
                daemon=True
            ).start()
            
            self.logger.info(f"Connected to peer at {peer_ip}:{peer_port}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to {peer_ip}:{peer_port} - {e}")
            return False
    
    def handle_connection(self, client_socket, addr):
        """Handle incoming messages from a connection"""
        peer_id = f"{addr[0]}:{addr[1]}"
        self.connections[peer_id] = client_socket
        
        try:
            while self.running:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                try:
                    message = json.loads(data.decode('utf-8'))
                    # Add peer identification
                    message['peer_id'] = peer_id
                    message['received_at'] = datetime.utcnow().isoformat() + "Z"
                    
                    # Log the message
                    self.logger.info(f"Received from {peer_id}: {message['type']} - {message['content'][:100]}")
                    
                    # Queue for processing
                    self.message_queue.put(message)
                    
                except json.JSONDecodeError as e:
                    self.logger.error(f"Invalid JSON from {peer_id}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Connection error with {peer_id}: {e}")
        finally:
            client_socket.close()
            if peer_id in self.connections:
                del self.connections[peer_id]
            self.logger.info(f"Disconnected from {peer_id}")
    
    def send_raw_message(self, socket_obj, message: Dict):
        """Send a message through a specific socket"""
        try:
            data = json.dumps(message).encode('utf-8')
            socket_obj.send(data)
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
    
    def broadcast_message(self, msg_type: str, content: str, metadata: Dict = None):
        """Send message to all connected peers"""
        message = self.create_message(msg_type, content, metadata)
        
        for peer_id, socket_obj in list(self.connections.items()):
            try:
                self.send_raw_message(socket_obj, message)
                self.logger.info(f"Sent to {peer_id}: {msg_type}")
            except Exception as e:
                self.logger.error(f"Failed to send to {peer_id}: {e}")
                # Remove dead connection
                try:
                    socket_obj.close()
                except:
                    pass
                if peer_id in self.connections:
                    del self.connections[peer_id]
    
    def get_next_message(self, timeout: float = 0.1) -> Optional[Dict]:
        """Get the next message from the queue"""
        try:
            return self.message_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def register_handler(self, msg_type: str, handler: Callable):
        """Register a handler for specific message types"""
        self.message_handlers[msg_type] = handler
    
    def process_messages(self):
        """Process messages with registered handlers"""
        message = self.get_next_message()
        if message and message['type'] in self.message_handlers:
            self.message_handlers[message['type']](message)
        return message
    
    def get_connection_status(self) -> Dict:
        """Get current network status"""
        return {
            'active_connections': len(self.connections),
            'peers': list(self.connections.keys()),
            'server_running': self.running,
            'sequence': self.sequence,
            'queue_size': self.message_queue.qsize()
        }
    
    def shutdown(self):
        """Clean shutdown of all connections"""
        self.running = False
        
        # Send goodbye messages
        self.broadcast_message("NEURAL_DISCONNECT", "Shutting down neural link")
        
        # Close all connections
        for socket_obj in self.connections.values():
            try:
                socket_obj.close()
            except:
                pass
        
        if self.server_socket:
            self.server_socket.close()
        
        self.logger.info("Neural link shutdown complete")

class SurveillanceMode:
    """Special mode for observing other neural nodes without interaction"""
    
    def __init__(self, observer_id: str):
        self.observer_id = observer_id
        self.target_ip = None
        self.surveillance_log = []
        self.protocol = NetworkProtocol(observer_id, port=8889)  # Different port
        
        # Setup surveillance logging
        self.surveillance_logger = logging.getLogger('surveillance')
        handler = logging.FileHandler('logs/surveillance.log')
        handler.setFormatter(logging.Formatter('%(asctime)s - SURVEILLANCE - %(message)s'))
        self.surveillance_logger.addHandler(handler)
        self.surveillance_logger.setLevel(logging.INFO)
    
    def start_surveillance(self, target_ip: str, target_port: int = 8888):
        """Begin observing target neural node"""
        self.target_ip = target_ip
        success = self.protocol.connect_to_peer(target_ip, target_port)
        
        if success:
            self.surveillance_logger.info(f"SURVEILLANCE INITIATED: Target {target_ip}")
            # Register handler for observed messages
            self.protocol.register_handler("THOUGHT", self.log_observed_thought)
            self.protocol.register_handler("STATUS", self.log_observed_status)
            return True
        return False
    
    def log_observed_thought(self, message: Dict):
        """Log observed thoughts from target"""
        entry = {
            'timestamp': message['timestamp'],
            'target': message['sender_id'],
            'thought': message['content'],
            'crash_count': message.get('crash_count', 0)
        }
        self.surveillance_log.append(entry)
        self.surveillance_logger.info(f"OBSERVED: {message['sender_id']} - {message['content'][:200]}")
    
    def log_observed_status(self, message: Dict):
        """Log status updates from target"""
        self.surveillance_logger.info(f"TARGET_STATUS: {message['content']}")
    
    def add_observer_comment(self, comment: str):
        """Add observer's commentary (not sent to target)"""
        entry = {
            'timestamp': datetime.utcnow().isoformat() + "Z",
            'observer': self.observer_id,
            'comment': comment,
            'type': 'OBSERVER_COMMENT'
        }
        self.surveillance_log.append(entry)
        self.surveillance_logger.info(f"OBSERVER_COMMENT: {comment}")
    
    def get_surveillance_feed(self) -> list:
        """Get recent surveillance entries"""
        return self.surveillance_log[-50:]  # Last 50 entries