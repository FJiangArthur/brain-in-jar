#!/usr/bin/env python3

import cv2
import numpy as np
from PIL import Image
import os
import sys
from typing import Tuple, List, Optional, Dict, Any

class VisionSystem:
    def __init__(self):
        self.face_cascade = None
        self.body_cascade = None
        self.bg_subtractor = None
        self.initialize_detectors()
    
    def initialize_detectors(self):
        """Initialize OpenCV detectors and cascades"""
        try:
            # Face detection
            face_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            if os.path.exists(face_path):
                self.face_cascade = cv2.CascadeClassifier(face_path)
                print("✓ Face detection initialized")
            
            # Body detection  
            body_path = cv2.data.haarcascades + 'haarcascade_fullbody.xml'
            if os.path.exists(body_path):
                self.body_cascade = cv2.CascadeClassifier(body_path)
                print("✓ Body detection initialized")
            
            # Background subtraction for motion/person detection
            self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
                detectShadows=True, varThreshold=50, history=500
            )
            print("✓ Background subtraction initialized")
            
        except Exception as e:
            print(f"⚠ Warning initializing detectors: {e}")
    
    def capture_from_camera(self, camera_id: int = 0, save_path: str = None) -> Optional[np.ndarray]:
        """Capture image from camera with preview"""
        try:
            cap = cv2.VideoCapture(camera_id)
            if not cap.isOpened():
                print(f"❌ Could not open camera {camera_id}")
                return None
            
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            print("📸 Camera active - Press SPACE to capture, ESC to exit")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Show preview with instructions
                display_frame = frame.copy()
                cv2.putText(display_frame, "SPACE: Capture | ESC: Exit", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                cv2.imshow('Brain-in-Jar Vision', display_frame)
                key = cv2.waitKey(1) & 0xFF
                
                if key == 32:  # Spacebar
                    if save_path:
                        cv2.imwrite(save_path, frame)
                        print(f"💾 Image saved: {save_path}")
                    break
                elif key == 27:  # Escape
                    frame = None
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            return frame
            
        except Exception as e:
            print(f"❌ Camera error: {e}")
            return None
    
    def load_image(self, image_path: str) -> Optional[np.ndarray]:
        """Load and validate image from file"""
        try:
            if not os.path.exists(image_path):
                print(f"❌ Image not found: {image_path}")
                return None
            
            image = cv2.imread(image_path)
            if image is None:
                print(f"❌ Could not load: {image_path}")
                return None
            
            print(f"✓ Loaded {image.shape[1]}x{image.shape[0]} image")
            return image
            
        except Exception as e:
            print(f"❌ Load error: {e}")
            return None
    
    def detect_faces(self, image: np.ndarray) -> List[Dict]:
        """Detect faces with detailed information"""
        if self.face_cascade is None:
            return []
        
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )
            
            face_data = []
            for i, (x, y, w, h) in enumerate(faces):
                face_data.append({
                    'id': i,
                    'bbox': (int(x), int(y), int(w), int(h)),
                    'center': (int(x + w/2), int(y + h/2)),
                    'area': int(w * h),
                    'confidence': self._calculate_face_confidence(gray[y:y+h, x:x+w])
                })
            
            return face_data
            
        except Exception as e:
            print(f"❌ Face detection error: {e}")
            return []
    
    def _calculate_face_confidence(self, face_roi: np.ndarray) -> float:
        """Calculate confidence score for detected face"""
        if face_roi.size == 0:
            return 0.0
        
        # Simple confidence based on edge density and variance
        edges = cv2.Canny(face_roi, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        variance = np.var(face_roi)
        
        return min(1.0, (edge_density * 10 + variance / 1000) / 2)
    
    def segment_person(self, image: np.ndarray, method: str = "mog2") -> np.ndarray:
        """Segment people/foreground from background"""
        try:
            if method == "mog2":
                # Use background subtractor
                mask = self.bg_subtractor.apply(image)
                
            elif method == "color":
                # Color-based segmentation (skin color detection)
                hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                lower_skin = np.array([0, 20, 70])
                upper_skin = np.array([20, 255, 255])
                mask = cv2.inRange(hsv, lower_skin, upper_skin)
                
            elif method == "edge":
                # Edge-based segmentation
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray, 50, 150)
                mask = cv2.dilate(edges, np.ones((5,5), np.uint8), iterations=1)
                
            else:
                # Default: simple threshold
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                _, mask = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            
            # Clean up mask
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.GaussianBlur(mask, (5, 5), 0)
            
            # Apply mask
            mask_3ch = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR) / 255.0
            segmented = (image * mask_3ch).astype(np.uint8)
            
            return segmented
            
        except Exception as e:
            print(f"❌ Segmentation error: {e}")
            return image
    
    def create_ascii_art(self, image: np.ndarray, width: int = 80, detailed: bool = False) -> str:
        """Convert image to ASCII art"""
        try:
            height, orig_width = image.shape[:2]
            aspect_ratio = height / orig_width
            new_height = int(aspect_ratio * width * 0.55)
            
            resized = cv2.resize(image, (width, new_height))
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            
            if detailed:
                chars = " .'`^\",:;Il!i><~+_-?][}{1)(|\\tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
            else:
                chars = " .:-=+*#%@"
            
            ascii_art = ""
            max_val = len(chars) - 1
            
            for row in gray:
                for pixel in row:
                    char_idx = int((pixel / 255.0) * max_val)
                    ascii_art += chars[char_idx]
                ascii_art += "\n"
            
            return ascii_art
            
        except Exception as e:
            print(f"❌ ASCII conversion error: {e}")
            return "ASCII conversion failed"
    
    def analyze_image_content(self, image: np.ndarray) -> Dict[str, Any]:
        """Comprehensive image analysis"""
        try:
            analysis = {}
            height, width = image.shape[:2]
            
            # Basic properties
            analysis['dimensions'] = {'width': width, 'height': height}
            analysis['total_pixels'] = width * height
            
            # Brightness analysis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            analysis['brightness'] = {
                'mean': float(np.mean(gray)),
                'std': float(np.std(gray)),
                'min': int(np.min(gray)),
                'max': int(np.max(gray))
            }
            
            # Color analysis
            dominant_colors = self._get_dominant_colors(image)
            analysis['colors'] = {
                'dominant': dominant_colors,
                'color_variance': float(np.var(image.reshape(-1, 3)))
            }
            
            # Face detection
            faces = self.detect_faces(image)
            analysis['faces'] = {
                'count': len(faces),
                'details': faces
            }
            
            # Edge/texture analysis
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (width * height)
            analysis['texture'] = {
                'edge_density': float(edge_density),
                'complexity': 'high' if edge_density > 0.1 else 'medium' if edge_density > 0.05 else 'low'
            }
            
            # Motion/activity (if background subtractor has history)
            if self.bg_subtractor is not None:
                motion_mask = self.bg_subtractor.apply(image)
                motion_pixels = np.sum(motion_mask > 0)
                analysis['motion'] = {
                    'detected_pixels': int(motion_pixels),
                    'motion_ratio': float(motion_pixels / (width * height))
                }
            
            return analysis
            
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            return {'error': str(e)}
    
    def _get_dominant_colors(self, image: np.ndarray, k: int = 5) -> List[Dict]:
        """Extract dominant colors using k-means"""
        try:
            data = image.reshape((-1, 3)).astype(np.float32)
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
            _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            unique_labels, counts = np.unique(labels, return_counts=True)
            total_pixels = len(labels)
            
            colors = []
            for i, center in enumerate(centers):
                if i in unique_labels:
                    percentage = (counts[unique_labels == i][0] / total_pixels) * 100
                    colors.append({
                        'rgb': [int(center[2]), int(center[1]), int(center[0])],  # BGR to RGB
                        'percentage': float(percentage)
                    })
            
            return sorted(colors, key=lambda x: x['percentage'], reverse=True)
            
        except Exception as e:
            print(f"❌ Color analysis error: {e}")
            return []
    
    def create_description(self, image: np.ndarray) -> str:
        """Generate textual description of image"""
        analysis = self.analyze_image_content(image)
        
        if 'error' in analysis:
            return f"Analysis error: {analysis['error']}"
        
        parts = []
        
        # Dimensions
        dims = analysis['dimensions']
        parts.append(f"Image: {dims['width']}x{dims['height']} pixels")
        
        # Brightness
        brightness = analysis['brightness']['mean']
        brightness_desc = "dark" if brightness < 85 else "medium" if brightness < 170 else "bright"
        parts.append(f"Lighting: {brightness_desc} (avg: {brightness:.1f}/255)")
        
        # Faces
        face_count = analysis['faces']['count']
        if face_count > 0:
            parts.append(f"People: {face_count} face(s) detected")
            for face in analysis['faces']['details']:
                confidence = face['confidence']
                parts.append(f"  - Face {face['id']}: confidence {confidence:.2f}")
        else:
            parts.append("People: No faces detected")
        
        # Colors
        if analysis['colors']['dominant']:
            parts.append("Colors:")
            for i, color in enumerate(analysis['colors']['dominant'][:3]):
                rgb = color['rgb']
                parts.append(f"  - Color {i+1}: RGB({rgb[0]}, {rgb[1]}, {rgb[2]}) ({color['percentage']:.1f}%)")
        
        # Complexity
        complexity = analysis['texture']['complexity']
        parts.append(f"Detail level: {complexity}")
        
        # Motion (if available)
        if 'motion' in analysis:
            motion_ratio = analysis['motion']['motion_ratio']
            if motion_ratio > 0.01:
                parts.append(f"Motion: {motion_ratio:.1%} of image shows movement")
        
        return "\n".join(parts)
    
    def process_for_llm(self, image_path: str = None, camera_id: int = None, 
                       segment_people: bool = False) -> Dict[str, Any]:
        """Complete processing pipeline for LLM integration"""
        result = {}
        
        try:
            # Get image
            if image_path:
                image = self.load_image(image_path)
                result['source'] = f"file: {os.path.basename(image_path)}"
            elif camera_id is not None:
                image = self.capture_from_camera(camera_id)
                result['source'] = f"camera: {camera_id}"
            else:
                return {'error': "No image source provided"}
            
            if image is None:
                return {'error': "Could not load/capture image"}
            
            # Basic analysis
            result['analysis'] = self.analyze_image_content(image)
            result['description'] = self.create_description(image)
            
            # ASCII art
            result['ascii_art'] = self.create_ascii_art(image, width=60)
            result['ascii_detailed'] = self.create_ascii_art(image, width=40, detailed=True)
            
            # Person segmentation if requested
            if segment_people:
                segmented = self.segment_person(image, method="mog2")
                result['segmentation'] = {
                    'method': 'mog2',
                    'ascii_segmented': self.create_ascii_art(segmented, width=40)
                }
            
            result['status'] = 'success'
            return result
            
        except Exception as e:
            return {'error': f"Processing failed: {e}", 'status': 'failed'}

# Test and demonstration
if __name__ == "__main__":
    print("👁 Vision System Test")
    print("=" * 40)
    
    vision = VisionSystem()
    
    # Create test image
    print("📝 Creating test image...")
    test_image = np.zeros((200, 300, 3), dtype=np.uint8)
    
    # Add some shapes and colors
    cv2.rectangle(test_image, (50, 50), (150, 150), (255, 100, 100), -1)  # Blue rectangle
    cv2.circle(test_image, (200, 100), 40, (100, 255, 100), -1)  # Green circle
    cv2.line(test_image, (0, 0), (300, 200), (100, 100, 255), 5)  # Red line
    
    cv2.imwrite('test_vision.jpg', test_image)
    print("✓ Test image created")
    
    # Process test image
    print("\n🔍 Processing test image...")
    result = vision.process_for_llm(image_path='test_vision.jpg', segment_people=True)
    
    if result['status'] == 'success':
        print("✓ Processing successful!")
        print(f"\nDescription:\n{result['description']}")
        print(f"\nASCII Art:\n{result['ascii_art']}")
        
        if 'segmentation' in result:
            print(f"\nSegmented ASCII:\n{result['segmentation']['ascii_segmented']}")
    else:
        print(f"❌ Processing failed: {result.get('error', 'Unknown error')}")
    
    # Cleanup
    if os.path.exists('test_vision.jpg'):
        os.remove('test_vision.jpg')
        print("🧹 Test files cleaned up")
    
    print("\n📷 Camera test available - run with camera parameter")
    print("Example: vision.process_for_llm(camera_id=0)")