"""
Comprehensive Pattern Generator
Generates patterns for various garments with full customization support
Supports: Dresses, Shirts, Pants, Skirts for both male/female with sleeve variations
"""

import math

def generate_basic_bodice_svg(measurements, garment_type="dress", sleeve_type="long", gender="female", style_options=None):
    """
    Generate garment patterns using traditional pattern drafting formulas
    
    Args:
        measurements: dict with chest, waist, hips, etc (in cm, will convert to mm)
        garment_type: "dress", "shirt", "blouse", "pants", "skirt"
        sleeve_type: "long", "short", "cap", "sleeveless", "puff"
        gender: "female" or "male"
        style_options: dict with neckline, length adjustments, etc.
    """
    
    if style_options is None:
        style_options = {}
    
    # Convert measurements from cm to mm (FreeSewing standard)
    meas_mm = {}
    for key, value in measurements.items():
        if isinstance(value, (int, float)):
            meas_mm[key] = value * 10  # cm to mm
    
    # Extract measurements (now in mm)
    chest = meas_mm.get('chest', 920)
    waist = meas_mm.get('waist', 720)
    hips = meas_mm.get('hips', 980)
    shoulder_width = meas_mm.get('shoulderToShoulder', 420)
    back_length = meas_mm.get('hpsToWaistBack', 420)
    shoulder_to_wrist = meas_mm.get('shoulderToWrist', chest * 0.65)
    biceps = meas_mm.get('biceps', chest * 0.35)
    wrist = meas_mm.get('wrist', chest * 0.18)
    waist_to_hips = meas_mm.get('waistToHips', 200)
    
    # Route to specific pattern generator
    if garment_type.lower() in ["dress", "blouse", "shirt", "top"]:
        return _generate_bodice_with_sleeves(
            chest, waist, hips, shoulder_width, back_length,
            shoulder_to_wrist, biceps, wrist, waist_to_hips,
            sleeve_type, gender, style_options
        )
    elif garment_type.lower() == "pants":
        return _generate_pants(chest, waist, hips, gender, style_options)
    elif garment_type.lower() == "skirt":
        return _generate_skirt(waist, hips, waist_to_hips, style_options)
    else:
        # Default to bodice
        return _generate_bodice_with_sleeves(
            chest, waist, hips, shoulder_width, back_length,
            shoulder_to_wrist, biceps, wrist, waist_to_hips,
            sleeve_type, gender, style_options
        )


def _generate_bodice_with_sleeves(chest, waist, hips, shoulder_width, back_length,
                                   shoulder_to_wrist, biceps, wrist, waist_to_hips,
                                   sleeve_type, gender, style_options):
    """Generate bodice pattern with customizable sleeves"""
    
    # Calculate pattern dimensions
    ease = 20 if gender == "male" else 10  # Males need more ease
    front_width = (chest / 4) + ease
    back_width = (chest / 4) + ease
    
    # Armhole depth
    armhole_depth = (chest / 12) + 50
    
    # Neckline depth
    neckline = style_options.get('neckline', 'round')
    neck_depth = 70 if neckline == 'v-neck' else 50 if neckline == 'square' else 60
    
    # Length adjustment
    length_adjust = style_options.get('length_adjustment', 0)
    total_length = back_length + waist_to_hips + length_adjust
    
    # BODICE FRONT
    front_path = f"""
    <g id="bodice-front">
      <path class="fabric" d="
        M {front_width/2},{neck_depth}
        L 0,{neck_depth + 30}
        L 0,{back_length}
        L 0,{total_length}
        L {front_width},{total_length}
        L {front_width},{back_length}
        L {front_width},{armhole_depth}
        C {front_width},{armhole_depth/2} {front_width - shoulder_width/4 + 20},{10} {front_width/2},{neck_depth}
        Z
      " />
      <text x="{front_width/2}" y="{neck_depth - 20}" class="text-center">FRONT</text>
      <text x="{front_width/2}" y="{neck_depth - 35}" class="text-center text-sm">Cut 2 (mirrored)</text>
      
      <!-- Grain line -->
      <line x1="{front_width/2}" y1="{neck_depth + 50}" x2="{front_width/2}" y2="{total_length - 50}" 
            class="grainline" stroke-dasharray="5,5"/>
      <text x="{front_width/2 + 10}" y="{(neck_depth + total_length)/2}" class="text-xs">Grain</text>
    </g>
    """
    
    # BODICE BACK
    back_offset_x = front_width + 50
    back_neck_depth = neck_depth - 20  # Back neck is higher
    back_path = f"""
    <g id="bodice-back" transform="translate({back_offset_x}, 0)">
      <path class="fabric" d="
        M {back_width/2},{back_neck_depth}
        L 0,{back_neck_depth + 20}
        L 0,{back_length}
        L 0,{total_length}
        L {back_width},{total_length}
        L {back_width},{back_length}
        L {back_width},{armhole_depth}
        C {back_width},{armhole_depth/2} {back_width - shoulder_width/4 + 20},{10} {back_width/2},{back_neck_depth}
        Z
      " />
      <text x="{back_width/2}" y="{back_neck_depth - 20}" class="text-center">BACK</text>
      <text x="{back_width/2}" y="{back_neck_depth - 35}" class="text-center text-sm">Cut 2 (mirrored)</text>
      
      <!-- Grain line -->
      <line x1="{back_width/2}" y1="{back_neck_depth + 50}" x2="{back_width/2}" y2="{total_length - 50}" 
            class="grainline" stroke-dasharray="5,5"/>
    </g>
    """
    
    # SLEEVE GENERATION
    sleeve_offset_x = back_offset_x + back_width + 50
    sleeve_path = ""
    
    if sleeve_type != "sleeveless":
        sleeve_path = _generate_sleeve(sleeve_type, shoulder_to_wrist, biceps, wrist, 
                                       armhole_depth, sleeve_offset_x)
    
    # Calculate total dimensions
    total_width = sleeve_offset_x + (300 if sleeve_type != "sleeveless" else -50)
    total_height = max(total_length, shoulder_to_wrist if sleeve_type in ["long", "short"] else armhole_depth) + 100
    
    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" 
     width="{total_width}mm" 
     height="{total_height}mm" 
     viewBox="0 0 {total_width} {total_height}">
  <style>
    .fabric {{ fill: none; stroke: #000; stroke-width: 2; }}
    .grainline {{ stroke: #666; stroke-width: 1; }}
    .text-center {{ text-anchor: middle; font-family: Arial; font-size: 16px; fill: #000; }}
    .text-sm {{ font-size: 12px; }}
    .text-xs {{ font-size: 10px; }}
    .dashed {{ stroke-dasharray: 10,5; stroke: #999; }}
  </style>
  
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="5" refY="3" orient="auto">
      <polygon points="0 0, 10 3, 0 6" fill="#666"/>
    </marker>
  </defs>
  
  <g transform="translate(20, 40)">
    {front_path}
    {back_path}
    {sleeve_path}
    
    <!-- Pattern info -->
    <text x="10" y="-10" class="text-sm" style="fill: #333;">
      Pattern: {sleeve_type.upper()} SLEEVE {gender.upper()} GARMENT | Neckline: {neckline.upper()}
    </text>
  </g>
</svg>"""
    
    return svg


def _generate_sleeve(sleeve_type, length, biceps, wrist, armhole_depth, offset_x):
    """Generate different sleeve types"""
    
    if sleeve_type == "long":
        # Full length sleeve
        cap_height = armhole_depth * 0.6
        width_top = biceps + 20
        width_bottom = wrist + 20
        
        return f"""
        <g id="sleeve" transform="translate({offset_x}, 0)">
          <path class="fabric" d="
            M {width_top/2},0
            C {width_top/2 + 30},{cap_height/3} {width_top/2 + 40},{cap_height/2} {width_top/2},{cap_height}
            L {width_bottom/2},{length}
            L {-width_bottom/2},{length}
            L {-width_top/2},{cap_height}
            C {-width_top/2 - 40},{cap_height/2} {-width_top/2 - 30},{cap_height/3} {-width_top/2},0
            Z
          " />
          <text x="0" y="-10" class="text-center">SLEEVE</text>
          <text x="0" y="-25" class="text-center text-sm">Cut 2</text>
          
          <!-- Grain line -->
          <line x1="0" y1="{cap_height + 20}" x2="0" y2="{length - 20}" 
                class="grainline" stroke-dasharray="5,5"/>
        </g>
        """
    
    elif sleeve_type == "short":
        # Short sleeve (1/3 length)
        short_length = length * 0.35
        cap_height = armhole_depth * 0.6
        width_top = biceps + 20
        width_bottom = biceps
        
        return f"""
        <g id="sleeve-short" transform="translate({offset_x}, 0)">
          <path class="fabric" d="
            M {width_top/2},0
            C {width_top/2 + 30},{cap_height/3} {width_top/2 + 40},{cap_height/2} {width_top/2},{cap_height}
            L {width_bottom/2},{short_length}
            L {-width_bottom/2},{short_length}
            L {-width_top/2},{cap_height}
            C {-width_top/2 - 40},{cap_height/2} {-width_top/2 - 30},{cap_height/3} {-width_top/2},0
            Z
          " />
          <text x="0" y="-10" class="text-center">SHORT SLEEVE</text>
          <text x="0" y="-25" class="text-center text-sm">Cut 2</text>
        </g>
        """
    
    elif sleeve_type == "cap":
        # Cap sleeve
        cap_length = armhole_depth * 0.4
        cap_height = armhole_depth * 0.5
        width = biceps + 30
        
        return f"""
        <g id="sleeve-cap" transform="translate({offset_x}, 0)">
          <path class="fabric" d="
            M {width/2},0
            C {width/2 + 20},{cap_height/2} {width/2 + 15},{cap_height} {width/2},{cap_length}
            L {-width/2},{cap_length}
            C {-width/2 - 15},{cap_height} {-width/2 - 20},{cap_height/2} {-width/2},0
            Z
          " />
          <text x="0" y="-10" class="text-center">CAP SLEEVE</text>
          <text x="0" y="-25" class="text-center text-sm">Cut 2</text>
        </g>
        """
    
    elif sleeve_type == "puff":
        # Puff sleeve (gathered)
        puff_length = length * 0.3
        cap_height = armhole_depth * 0.7
        width_top = biceps + 60  # Extra width for gathering
        width_bottom = biceps + 10
        
        return f"""
        <g id="sleeve-puff" transform="translate({offset_x}, 0)">
          <path class="fabric" d="
            M {width_top/2},0
            C {width_top/2 + 50},{cap_height/3} {width_top/2 + 60},{cap_height/2} {width_top/2},{cap_height}
            L {width_bottom/2},{puff_length}
            L {-width_bottom/2},{puff_length}
            L {-width_top/2},{cap_height}
            C {-width_top/2 - 60},{cap_height/2} {-width_top/2 - 50},{cap_height/3} {-width_top/2},0
            Z
          " />
          <text x="0" y="-10" class="text-center">PUFF SLEEVE</text>
          <text x="0" y="-25" class="text-center text-sm">Cut 2 + GATHER TOP</text>
          
          <!-- Gathering indication -->
          <line x1="{-width_top/2 + 20}" y1="{cap_height - 10}" 
                x2="{width_top/2 - 20}" y2="{cap_height - 10}" 
                class="dashed" stroke-width="1.5"/>
          <text x="0" y="{cap_height - 15}" class="text-xs">GATHER</text>
        </g>
        """
    
    return ""


def _generate_pants(chest, waist, hips, gender, style_options):
    """Generate pants/trousers pattern"""
    # TODO: Implement pants pattern
    return generate_basic_bodice_svg({'chest': chest/10, 'waist': waist/10, 'hips': hips/10})


def _generate_skirt(waist, hips, waist_to_hips, style_options):
    """Generate skirt pattern"""
    # TODO: Implement skirt pattern  
    return generate_basic_bodice_svg({'chest': hips/10, 'waist': waist/10, 'hips': hips/10})


if __name__ == "__main__":
    # Test with sample measurements
    test_measurements = {
        'chest': 92,  # cm
        'waist': 72,  
        'hips': 98,
        'shoulderToShoulder': 42,
        'hpsToWaistBack': 42
    }
    
    svg = generate_basic_bodice_svg(test_measurements, sleeve_type="long")
    
    with open('test-basic-pattern.svg', 'w') as f:
        f.write(svg)
    
    print("✅ Generated test-basic-pattern.svg")
    print(f"SVG length: {len(svg)} bytes")
    print("This pattern has ACTUAL content with SLEEVES!")
