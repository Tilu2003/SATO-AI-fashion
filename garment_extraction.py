"""
Garment-to-Pattern Extraction System
Uses open-source CV to extract 2D garment outline and calculate proportions
Then generates pattern matching those exact proportions
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import json
from PIL import Image
import os

class GarmentProportionExtractor:
    """
    Extracts 2D garment outline from photo and measures proportions
    Uses: OpenCV, NumPy (all open-source)
    """
    
    def __init__(self, image_path: str, gemini_analysis: Dict):
        self.image_path = image_path
        self.analysis = gemini_analysis
        self.image = None
        self.garment_mask = None
        self.contours = []
        self.proportions = {}
        
    def extract_garment_outline(self) -> np.ndarray:
        """
        Step 1: Extract garment from background using edge detection
        Returns: 2D binary mask of garment
        """
        # Load image
        img = cv2.imread(self.image_path)
        if img is None:
            raise ValueError(f"Cannot load image: {self.image_path}")
        
        self.image = img
        height, width = img.shape[:2]
        
        # Convert to different color spaces for better segmentation
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Method 1: GrabCut (automatic foreground extraction)
        mask = np.zeros(img.shape[:2], np.uint8)
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)
        
        # Assume garment is in center 60% of image
        rect = (
            int(width * 0.2), 
            int(height * 0.1), 
            int(width * 0.6), 
            int(height * 0.8)
        )
        
        cv2.grabCut(img, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        
        # Method 2: Edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Combine methods
        combined = cv2.bitwise_and(mask2, mask2, mask=edges)
        
        # Morphological operations to clean up
        kernel = np.ones((5, 5), np.uint8)
        cleaned = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel)
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Get largest contour (should be the garment)
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Create final mask
            final_mask = np.zeros(img.shape[:2], np.uint8)
            cv2.drawContours(final_mask, [largest_contour], -1, 255, -1)
            
            self.garment_mask = final_mask
            self.contours = [largest_contour]
            
            return final_mask
        
        return mask2
    
    def detect_key_points(self) -> Dict[str, Tuple[int, int]]:
        """
        Step 2: Detect key garment points (shoulders, waist, hem, neckline)
        Returns: Dictionary of point names to (x, y) coordinates
        """
        if self.garment_mask is None:
            self.extract_garment_outline()
        
        if not self.contours:
            return {}
        
        contour = self.contours[0]
        height, width = self.garment_mask.shape
        
        # Get bounding box
        x, y, w, h = cv2.boundingRect(contour)
        
        points = {}
        
        # Top center (neckline/shoulder area)
        top_region = contour[contour[:, 0, 1] < y + h * 0.2]
        if len(top_region) > 0:
            top_center = top_region[np.argmin(top_region[:, 0, 1])]
            points['neck_center'] = tuple(top_center[0])
        
        # Shoulders (leftmost and rightmost points in top 20%)
        shoulder_region = contour[contour[:, 0, 1] < y + h * 0.25]
        if len(shoulder_region) > 0:
            left_shoulder = shoulder_region[np.argmin(shoulder_region[:, 0, 0])]
            right_shoulder = shoulder_region[np.argmax(shoulder_region[:, 0, 0])]
            points['left_shoulder'] = tuple(left_shoulder[0])
            points['right_shoulder'] = tuple(right_shoulder[0])
        
        # Bust/chest (widest point in top 40%)
        chest_region = contour[(contour[:, 0, 1] > y + h * 0.2) & (contour[:, 0, 1] < y + h * 0.5)]
        if len(chest_region) > 0:
            left_chest = chest_region[np.argmin(chest_region[:, 0, 0])]
            right_chest = chest_region[np.argmax(chest_region[:, 0, 0])]
            points['left_chest'] = tuple(left_chest[0])
            points['right_chest'] = tuple(right_chest[0])
        
        # Waist (narrowest point in middle 40-60%)
        waist_region = contour[(contour[:, 0, 1] > y + h * 0.4) & (contour[:, 0, 1] < y + h * 0.65)]
        if len(waist_region) > 0:
            # Find narrowest horizontal span
            waist_widths = []
            for py in range(int(y + h * 0.4), int(y + h * 0.65), 2):
                row_points = waist_region[waist_region[:, 0, 1] == py]
                if len(row_points) >= 2:
                    width_at_row = np.max(row_points[:, 0, 0]) - np.min(row_points[:, 0, 0])
                    waist_widths.append((width_at_row, py))
            
            if waist_widths:
                _, waist_y = min(waist_widths, key=lambda x: x[0])
                waist_pts = waist_region[waist_region[:, 0, 1] == waist_y]
                points['left_waist'] = tuple(waist_pts[np.argmin(waist_pts[:, 0, 0])][0])
                points['right_waist'] = tuple(waist_pts[np.argmax(waist_pts[:, 0, 0])][0])
        
        # Hip (widest point in bottom 40%)
        hip_region = contour[contour[:, 0, 1] > y + h * 0.6]
        if len(hip_region) > 0:
            left_hip = hip_region[np.argmin(hip_region[:, 0, 0])]
            right_hip = hip_region[np.argmax(hip_region[:, 0, 0])]
            points['left_hip'] = tuple(left_hip[0])
            points['right_hip'] = tuple(right_hip[0])
        
        # Hem (bottom)
        bottom_region = contour[contour[:, 0, 1] > y + h * 0.9]
        if len(bottom_region) > 0:
            bottom_center = bottom_region[np.argmax(bottom_region[:, 0, 1])]
            points['hem_center'] = tuple(bottom_center[0])
        
        # Armholes (indentations on sides in top 30%)
        armhole_region = contour[(contour[:, 0, 1] > y + h * 0.15) & (contour[:, 0, 1] < y + h * 0.4)]
        if len(armhole_region) > 4:
            # Find points closest to center (armhole curves inward)
            center_x = x + w / 2
            left_armhole_pts = armhole_region[armhole_region[:, 0, 0] < center_x]
            right_armhole_pts = armhole_region[armhole_region[:, 0, 0] > center_x]
            
            if len(left_armhole_pts) > 0:
                left_armhole = left_armhole_pts[np.argmax(left_armhole_pts[:, 0, 0])]  # Rightmost of left side
                points['left_armhole'] = tuple(left_armhole[0])
            
            if len(right_armhole_pts) > 0:
                right_armhole = right_armhole_pts[np.argmin(right_armhole_pts[:, 0, 0])]  # Leftmost of right side
                points['right_armhole'] = tuple(right_armhole[0])
        
        return points
    
    def calculate_proportions(self, key_points: Dict, user_measurements: Dict) -> Dict:
        """
        Step 3: Calculate garment proportions and scale to user measurements
        Returns: Pattern adjustments based on photo proportions
        """
        if not key_points:
            key_points = self.detect_key_points()
        
        if not key_points:
            return {}
        
        height, width = self.garment_mask.shape
        
        proportions = {}
        
        # Calculate widths (in pixels)
        if 'left_shoulder' in key_points and 'right_shoulder' in key_points:
            shoulder_width_px = key_points['right_shoulder'][0] - key_points['left_shoulder'][0]
            proportions['shoulder_width_px'] = shoulder_width_px
        
        if 'left_chest' in key_points and 'right_chest' in key_points:
            chest_width_px = key_points['right_chest'][0] - key_points['left_chest'][0]
            proportions['chest_width_px'] = chest_width_px
        
        if 'left_waist' in key_points and 'right_waist' in key_points:
            waist_width_px = key_points['right_waist'][0] - key_points['left_waist'][0]
            proportions['waist_width_px'] = waist_width_px
        
        if 'left_hip' in key_points and 'right_hip' in key_points:
            hip_width_px = key_points['right_hip'][0] - key_points['left_hip'][0]
            proportions['hip_width_px'] = hip_width_px
        
        # Calculate lengths (in pixels)
        if 'neck_center' in key_points and 'hem_center' in key_points:
            total_length_px = key_points['hem_center'][1] - key_points['neck_center'][1]
            proportions['total_length_px'] = total_length_px
        
        if 'neck_center' in key_points and 'left_waist' in key_points:
            bodice_length_px = key_points['left_waist'][1] - key_points['neck_center'][1]
            proportions['bodice_length_px'] = bodice_length_px
        
        if 'left_waist' in key_points and 'hem_center' in key_points:
            skirt_length_px = key_points['hem_center'][1] - key_points['left_waist'][1]
            proportions['skirt_length_px'] = skirt_length_px
        
        # Calculate RATIOS (these are independent of scale)
        if 'chest_width_px' in proportions and 'waist_width_px' in proportions:
            proportions['chest_to_waist_ratio'] = proportions['chest_width_px'] / proportions['waist_width_px']
        
        if 'waist_width_px' in proportions and 'hip_width_px' in proportions:
            proportions['waist_to_hip_ratio'] = proportions['waist_width_px'] / proportions['hip_width_px']
        
        if 'bodice_length_px' in proportions and 'total_length_px' in proportions:
            proportions['bodice_to_total_ratio'] = proportions['bodice_length_px'] / proportions['total_length_px']
        
        if 'skirt_length_px' in proportions and 'total_length_px' in proportions:
            proportions['skirt_to_total_ratio'] = proportions['skirt_length_px'] / proportions['total_length_px']
        
        # Calculate scale factor (pixels to cm) using user measurements
        # Use chest as reference since it's most reliable
        if 'chest_width_px' in proportions and 'chest' in user_measurements:
            # Chest circumference / 4 = front panel width
            user_chest_width_cm = user_measurements['chest'] / 4
            px_to_cm = user_chest_width_cm / proportions['chest_width_px']
            proportions['scale_px_to_cm'] = px_to_cm
            
            # Convert all measurements to cm
            for key in list(proportions.keys()):
                if key.endswith('_px'):
                    cm_key = key.replace('_px', '_cm')
                    proportions[cm_key] = proportions[key] * px_to_cm
        
        self.proportions = proportions
        return proportions
    
    def generate_2d_technical_drawing(self, output_path: str) -> str:
        """
        Step 4: Generate clean 2D technical flat sketch
        """
        if self.image is None or self.garment_mask is None:
            self.extract_garment_outline()
        
        key_points = self.detect_key_points()
        
        # Create white background
        drawing = np.ones_like(self.image) * 255
        
        # Draw garment outline in black
        if self.contours:
            cv2.drawContours(drawing, self.contours, -1, (0, 0, 0), 2)
        
        # Draw key points
        for name, (x, y) in key_points.items():
            color = (255, 0, 0) if 'left' in name else (0, 0, 255) if 'right' in name else (0, 255, 0)
            cv2.circle(drawing, (x, y), 5, color, -1)
            cv2.putText(drawing, name.split('_')[0], (x + 10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        # Draw measurement lines
        if 'left_shoulder' in key_points and 'right_shoulder' in key_points:
            cv2.line(drawing, key_points['left_shoulder'], key_points['right_shoulder'], (128, 128, 128), 1)
        
        if 'left_chest' in key_points and 'right_chest' in key_points:
            cv2.line(drawing, key_points['left_chest'], key_points['right_chest'], (128, 128, 128), 1)
        
        if 'left_waist' in key_points and 'right_waist' in key_points:
            cv2.line(drawing, key_points['left_waist'], key_points['right_waist'], (128, 128, 128), 1)
        
        # Save
        cv2.imwrite(output_path, drawing)
        return output_path


def match_proportions_to_formulas(proportions: Dict, garment_type: str) -> Dict:
    """
    Step 5: Map extracted proportions to pattern formulas
    Adjusts FreeSewing formulas to match photo proportions
    """
    formula_adjustments = {
        "base_formulas": "freesewing",
        "adjustments": {}
    }
    
    # Adjust bodice length
    if 'bodice_to_total_ratio' in proportions:
        ratio = proportions['bodice_to_total_ratio']
        if ratio < 0.4:  # Short bodice
            formula_adjustments['adjustments']['bodice_length_factor'] = 0.9
        elif ratio > 0.6:  # Long bodice
            formula_adjustments['adjustments']['bodice_length_factor'] = 1.1
        else:
            formula_adjustments['adjustments']['bodice_length_factor'] = 1.0
    
    # Adjust waist shaping
    if 'chest_to_waist_ratio' in proportions:
        ratio = proportions['chest_to_waist_ratio']
        if ratio > 1.3:  # Very fitted
            formula_adjustments['adjustments']['waist_suppression'] = 'high'
            formula_adjustments['adjustments']['dart_intake'] = ratio - 1.0
        elif ratio > 1.15:  # Fitted
            formula_adjustments['adjustments']['waist_suppression'] = 'medium'
            formula_adjustments['adjustments']['dart_intake'] = (ratio - 1.0) * 0.8
        else:  # Loose/straight
            formula_adjustments['adjustments']['waist_suppression'] = 'low'
            formula_adjustments['adjustments']['dart_intake'] = 0
    
    # Adjust hip shaping
    if 'waist_to_hip_ratio' in proportions:
        ratio = proportions['waist_to_hip_ratio']
        if ratio < 0.8:  # A-line/flared
            formula_adjustments['adjustments']['hip_flare'] = 'high'
        elif ratio < 0.95:  # Slight flare
            formula_adjustments['adjustments']['hip_flare'] = 'medium'
        else:  # Straight
            formula_adjustments['adjustments']['hip_flare'] = 'none'
    
    # Use actual measurements if available
    if 'bodice_length_cm' in proportions:
        formula_adjustments['adjustments']['bodice_length_cm'] = proportions['bodice_length_cm']
    
    if 'skirt_length_cm' in proportions:
        formula_adjustments['adjustments']['skirt_length_cm'] = proportions['skirt_length_cm']
    
    return formula_adjustments


if __name__ == "__main__":
    # Test with sample
    print("Garment-to-Pattern Extraction System")
    print("Using: OpenCV, NumPy (all open-source)")
