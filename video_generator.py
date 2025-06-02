import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
import time

class VideoGenerator:
    def __init__(self, output_dir="demonstration_output"):
        """Initialize video generator"""
        self.output_dir = output_dir
        self.font = ImageFont.truetype("arial.ttf", 24)
        self.fps = 24
        self.width = 1920
        self.height = 1080
        
        # Initialize explanations
        self.explanations = {
            "Scenario1_ConflictFree": "Demonstrating a conflict-free mission where drones maintain safe distances in both space and time.",
            "Scenario2_SpatialConflict": "Showing spatial conflicts where drones' paths come too close in 3D space, despite different timing.",
            "Scenario3_TemporalConflict": "Illustrating temporal conflicts where drones occupy the same space at different times.",
            "Scenario4_FullConflict": "Demonstrating combined spatial and temporal conflicts, showing how the system identifies and explains both types of conflicts.",
            "Scenario5_EmergencyLanding": "Showing how the system handles emergency landing scenarios while maintaining safe distances from other drones.",
            "Scenario6_CircularFlight": "Demonstrating circular flight patterns and how the system detects conflicts in repetitive trajectories.",
            "Scenario7_VerticalStacking": "Showing vertical stacking scenarios where drones operate at different altitudes in the same area.",
            "Scenario8_Complex3DManeuvers": "Demonstrating complex 3D maneuvers and how the system handles intricate flight patterns."
        }
    
    def add_text_overlay(self, image, text, position=(50, 50), color=(255, 255, 255)):
        """Add text overlay to an image"""
        img_pil = Image.fromarray(image)
        draw = ImageDraw.Draw(img_pil)
        draw.text(position, text, font=self.font, fill=color)
        return np.array(img_pil)
    
    def create_intro(self, duration=5):
        """Create introduction sequence"""
        frames = []
        intro_text = [
            "UAV Strategic Deconfliction System Demonstration",
            "Demonstrating 4D Conflict Detection and Resolution",
            "Created by: Your Name"
        ]
        
        for i in range(int(duration * self.fps)):
            frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            for j, text in enumerate(intro_text):
                frame = self.add_text_overlay(frame, text, (50, 200 + j*100), (255, 255, 255))
            frames.append(frame)
        return frames
    
    def create_scenario_section(self, scenario_name, duration=60):
        """Create section for each scenario"""
        frames = []
        
        # Load static visualization
        static_img_path = os.path.join(self.output_dir, f"{scenario_name}_trajectories.png")
        static_img = cv2.imread(static_img_path)
        
        # Add explanation text
        explanation = self.get_explanation_text(scenario_name)
        
        # Add static visualization with explanation
        for i in range(int(duration * self.fps * 0.3)):
            frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            frame[:static_img.shape[0], :static_img.shape[1]] = static_img
            frame = self.add_text_overlay(frame, explanation, (50, 900), (255, 255, 255))
            frames.append(frame)
        
        # Add animation
        animation_path = os.path.join(self.output_dir, f"{scenario_name}_animation.gif")
        animation = cv2.VideoCapture(animation_path)
        
        while True:
            ret, frame = animation.read()
            if not ret:
                break
            frame = cv2.resize(frame, (self.width, self.height))
            frames.append(frame)
        
        animation.release()
        return frames
    
    def get_explanation_text(self, scenario_name):
        """Get explanation text for each scenario"""
        return self.explanations.get(scenario_name, "")
    
    def create_video(self):
        """Create the complete demonstration video with enhanced effects"""
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        output_path = os.path.join(self.output_dir, "uav_deconfliction_demo.mp4")
        out = cv2.VideoWriter(output_path, fourcc, self.fps, (self.width, self.height))
        
        # Add intro with enhanced effects
        intro_frames = self.create_intro()
        for frame in intro_frames:
            out.write(frame)
        
        # Add each scenario with enhanced effects
        scenarios = [
            "Scenario1_ConflictFree",
            "Scenario2_SpatialConflict",
            "Scenario3_TemporalConflict",
            "Scenario4_FullConflict"
        ]
        
        for scenario in scenarios:
            scenario_frames = self.create_scenario_section(scenario)
            for frame in scenario_frames:
                out.write(frame)
        
        # Add outro with enhanced effects
        outro_text = [
            "Thank you for watching!",
            "This demonstration showcases our UAV deconfliction system's",
            "ability to detect and resolve conflicts in 4D space.",
            "Created by: Chetan Tangale"
        ]
        outro_frames = []
        
        # Enhanced outro with zoom and fade effects
        for i in range(int(5 * self.fps * 0.3)):
            frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            alpha = i / (5 * self.fps * 0.3)
            scale = 1.0 + (i / (5 * self.fps * 0.3)) * 0.2
            
            for j, text in enumerate(outro_text):
                text_frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
                text_frame = self.add_text_overlay(text_frame, text, (50, 300 + j*50), (255, 255, 255))
                frame = cv2.addWeighted(frame, 1, text_frame, alpha, 0)
                
                # Add zoom effect
                frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
                frame = cv2.resize(frame, (self.width, self.height))
            outro_frames.append(frame)
        
        # Hold outro with slight pan
        for i in range(int(5 * self.fps * 0.4)):
            frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            pan_offset = int((i / (5 * self.fps * 0.4)) * 30)  # 30 pixels max pan
            
            for j, text in enumerate(outro_text):
                frame = self.add_text_overlay(frame, text, (50 + pan_offset, 300 + j*50), (255, 255, 255))
            outro_frames.append(frame)
        
        # Fade out outro with zoom out
        for i in range(int(5 * self.fps * 0.3)):
            frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            alpha = 1 - i / (5 * self.fps * 0.3)
            scale = 1.2 - (i / (5 * self.fps * 0.3)) * 0.2
            
            for j, text in enumerate(outro_text):
                text_frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
                text_frame = self.add_text_overlay(text_frame, text, (50, 300 + j*50), (255, 255, 255))
                frame = cv2.addWeighted(frame, 1, text_frame, alpha, 0)
                
                # Add zoom out effect
                frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
                frame = cv2.resize(frame, (self.width, self.height))
            outro_frames.append(frame)
        
        for frame in outro_frames:
            out.write(frame)
        
        out.release()
        print(f"Video created successfully at: {output_path}")

if __name__ == "__main__":
    generator = VideoGenerator()
    generator.create_video()
