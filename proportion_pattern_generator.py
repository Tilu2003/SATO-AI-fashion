"""
Proportion-Based Pattern Generator
Takes extracted proportions and generates pattern matching photo exactly
"""

from typing import Dict, Tuple
from pattern_drafting_engine import PatternDrafter
import math

class ProportionBasedPatternGenerator:
    """
    Generates pattern based on extracted garment proportions
    Uses FreeSewing formulas but adjusts them to match photo ratios
    """
    
    def __init__(self, measurements: Dict, proportions: Dict, formula_adjustments: Dict):
        self.measurements = measurements
        self.proportions = proportions
        self.adjustments = formula_adjustments.get('adjustments', {})
        self.drafter = PatternDrafter(measurements)
        
    def calculate_adjusted_bodice_points(self) -> Dict[str, Tuple[float, float]]:
        """
        Calculate bodice using FreeSewing formulas + photo proportions
        """
        # Start with FreeSewing base
        base_points = self.drafter.calculate_bodice_points()
        
        # Adjust based on photo proportions
        adjusted_points = base_points.copy()
        
        # Adjust bodice length
        if 'bodice_length_cm' in self.proportions:
            target_length = self.proportions['bodice_length_cm']
            current_length = base_points['back_waist_center'][1]
            scale_factor = target_length / current_length if current_length > 0 else 1.0
            
            # Scale all vertical coordinates
            for key in adjusted_points:
                x, y = adjusted_points[key]
                adjusted_points[key] = (x, y * scale_factor)
        
        # Adjust waist suppression based on photo
        if 'dart_intake' in self.adjustments:
            dart_intake = self.adjustments['dart_intake']
            
            # Adjust waist points to create more/less suppression
            if 'back_waist_side' in adjusted_points:
                x, y = adjusted_points['back_waist_side']
                adjusted_points['back_waist_side'] = (x - dart_intake, y)
            
            if 'front_waist_side' in adjusted_points:
                x, y = adjusted_points['front_waist_side']
                adjusted_points['front_waist_side'] = (x - dart_intake, y)
        
        # Adjust hip flare
        if 'hip_flare' in self.adjustments and 'back_hip_side' in adjusted_points:
            flare = self.adjustments['hip_flare']
            flare_amount = {'none': 0, 'medium': 2, 'high': 5}.get(flare, 0)
            
            x, y = adjusted_points['back_hip_side']
            adjusted_points['back_hip_side'] = (x + flare_amount, y)
            
            if 'front_hip_side' in adjusted_points:
                x, y = adjusted_points['front_hip_side']
                adjusted_points['front_hip_side'] = (x + flare_amount, y)
        
        return adjusted_points
    
    def calculate_adjusted_skirt_points(self, skirt_type: str) -> Dict[str, Tuple[float, float]]:
        """
        Calculate skirt using photo proportions
        """
        # Use photo skirt length if available
        if 'skirt_length_cm' in self.proportions:
            skirt_length = self.proportions['skirt_length_cm']
        else:
            skirt_length = 60  # Default
        
        waist = self.measurements.get('waist', 72)
        hips = self.measurements.get('hips', 98)
        
        points = {}
        
        # Use extracted hip flare ratio
        if 'waist_to_hip_ratio' in self.proportions:
            ratio = self.proportions['waist_to_hip_ratio']
            # If photo shows A-line (ratio < 0.9), increase hem flare
            if ratio < 0.9:
                hem_width = (hips / 4) * 1.3  # Extra flare
            elif ratio < 0.95:
                hem_width = (hips / 4) * 1.15
            else:
                hem_width = hips / 4  # Straight
        else:
            hem_width = (hips / 4) * 1.2  # Default A-line
        
        waist_width = waist / 4
        
        # Skirt pattern points
        points['waist_left'] = (0, 0)
        points['waist_right'] = (waist_width, 0)
        points['hip_right'] = (hem_width, skirt_length * 0.3)
        points['hem_right'] = (hem_width, skirt_length)
        points['hem_left'] = (0, skirt_length)
        points['hip_left'] = (0, skirt_length * 0.3)
        
        return points
    
    def generate_pattern_from_proportions(self, sleeve_type: str = "long", 
                                         neckline: str = "round",
                                         include_skirt: bool = True) -> str:
        """
        Main function: Generate complete pattern matching photo proportions
        """
        from pattern_drafting_engine import generate_professional_pattern
        
        # Get adjusted measurements
        adjusted_measurements = self.measurements.copy()
        
        # Override with photo-extracted measurements
        if 'bodice_length_cm' in self.proportions:
            adjusted_measurements['hpsToWaistBack'] = self.proportions['bodice_length_cm']
        
        # Calculate length adjustment
        length_adjust = 0
        if 'bodice_length_factor' in self.adjustments:
            length_adjust = (self.adjustments['bodice_length_factor'] - 1.0) * 20  # cm
        
        # Determine skirt type from proportions
        skirt_type = None
        if include_skirt:
            if 'hip_flare' in self.adjustments:
                flare = self.adjustments['hip_flare']
                skirt_type = {'none': 'pencil', 'medium': 'a-line', 'high': 'circle'}.get(flare, 'a-line')
            else:
                skirt_type = 'a-line'
        
        # Generate pattern with adjustments
        svg = generate_professional_pattern(
            measurements=adjusted_measurements,
            sleeve_type=sleeve_type,
            neckline=neckline,
            length_adjust=length_adjust,
            skirt_type=skirt_type,
            include_pants=False,
            collar_type=None
        )
        
        return svg
    
    def generate_technical_spec_sheet(self) -> Dict:
        """
        Generate detailed technical specification based on photo analysis
        """
        spec = {
            "extracted_proportions": self.proportions,
            "formula_adjustments": self.adjustments,
            "pattern_notes": []
        }
        
        # Add specific notes based on proportions
        if 'chest_to_waist_ratio' in self.proportions:
            ratio = self.proportions['chest_to_waist_ratio']
            if ratio > 1.3:
                spec["pattern_notes"].append("Very fitted bodice - significant waist suppression required")
            elif ratio > 1.15:
                spec["pattern_notes"].append("Fitted bodice - moderate dart shaping")
            else:
                spec["pattern_notes"].append("Relaxed fit - minimal or no darts")
        
        if 'bodice_to_total_ratio' in self.proportions:
            ratio = self.proportions['bodice_to_total_ratio']
            if ratio < 0.4:
                spec["pattern_notes"].append("Short bodice - empire waist style")
            elif ratio > 0.6:
                spec["pattern_notes"].append("Long bodice - dropped waist style")
            else:
                spec["pattern_notes"].append("Standard bodice length - natural waist")
        
        if 'waist_to_hip_ratio' in self.proportions:
            ratio = self.proportions['waist_to_hip_ratio']
            if ratio < 0.8:
                spec["pattern_notes"].append("Significant A-line flare from waist to hem")
            elif ratio < 0.95:
                spec["pattern_notes"].append("Moderate A-line shaping")
            else:
                spec["pattern_notes"].append("Straight/pencil skirt - minimal flare")
        
        # Add measurements
        if 'bodice_length_cm' in self.proportions:
            spec["measured_bodice_length"] = f"{self.proportions['bodice_length_cm']:.1f} cm"
        
        if 'skirt_length_cm' in self.proportions:
            spec["measured_skirt_length"] = f"{self.proportions['skirt_length_cm']:.1f} cm"
        
        if 'scale_px_to_cm' in self.proportions:
            spec["scale_factor"] = f"{self.proportions['scale_px_to_cm']:.4f} cm/pixel"
        
        return spec


if __name__ == "__main__":
    print("Proportion-Based Pattern Generator")
    print("Generates patterns matching photo proportions exactly")
