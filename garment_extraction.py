"""
garment_extraction.py
---------------------
Extracts 2D garment outlines from photos using OpenCV and calculates
proportions that are later used to adjust pattern-drafting formulas.
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import os


class GarmentProportionExtractor:
    """
    Extracts a garment outline from a photo and measures its proportions.
    Uses only open-source libraries: OpenCV and NumPy.
    """

    def __init__(self, image_path: str, gemini_analysis: Dict):
        self.image_path = image_path
        self.analysis   = gemini_analysis
        self.image: Optional[np.ndarray] = None
        self.garment_mask: Optional[np.ndarray] = None
        self.contours: List[np.ndarray] = []
        self.proportions: Dict = {}

    # ------------------------------------------------------------------
    # Step 1: Extract garment outline
    # ------------------------------------------------------------------

    def extract_garment_outline(self) -> np.ndarray:
        """
        Segments the garment from the background using GrabCut + edge detection.
        Returns a 2-D binary mask of the garment.
        """
        img = cv2.imread(self.image_path)
        if img is None:
            raise ValueError(f"Cannot load image: {self.image_path}")

        self.image = img
        height, width = img.shape[:2]

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # GrabCut — assume garment occupies the central 60 % of the frame
        mask      = np.zeros(img.shape[:2], np.uint8)
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)
        rect = (
            int(width * 0.2),
            int(height * 0.1),
            int(width * 0.6),
            int(height * 0.8),
        )
        cv2.grabCut(img, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")

        # Edge detection
        edges = cv2.Canny(gray, 50, 150)

        # Combine and clean up
        combined = cv2.bitwise_and(mask2, mask2, mask=edges)
        kernel   = np.ones((5, 5), np.uint8)
        cleaned  = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel)
        cleaned  = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN,  kernel)

        contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest = max(contours, key=cv2.contourArea)
            final_mask = np.zeros(img.shape[:2], np.uint8)
            cv2.drawContours(final_mask, [largest], -1, 255, -1)
            self.garment_mask = final_mask
            self.contours     = [largest]
            return final_mask

        self.garment_mask = mask2
        return mask2

    # ------------------------------------------------------------------
    # Step 2: Detect key points
    # ------------------------------------------------------------------

    def detect_key_points(self) -> Dict[str, Tuple[int, int]]:
        """
        Identifies key garment landmarks (shoulders, waist, hem, neckline).
        Returns a dict mapping landmark name → (x, y) pixel coordinates.
        """
        if self.garment_mask is None:
            self.extract_garment_outline()

        if not self.contours:
            return {}

        contour = self.contours[0]
        x, y, w, h = cv2.boundingRect(contour)
        points: Dict[str, Tuple[int, int]] = {}

        # Neckline — topmost point
        top_region = contour[contour[:, 0, 1] < y + h * 0.2]
        if len(top_region):
            top = top_region[np.argmin(top_region[:, 0, 1])]
            points["neck_center"] = tuple(top[0])

        # Shoulders — leftmost / rightmost in top 25 %
        shoulder_region = contour[contour[:, 0, 1] < y + h * 0.25]
        if len(shoulder_region):
            points["left_shoulder"]  = tuple(shoulder_region[np.argmin(shoulder_region[:, 0, 0])][0])
            points["right_shoulder"] = tuple(shoulder_region[np.argmax(shoulder_region[:, 0, 0])][0])

        # Chest — widest span in top 20–50 %
        chest_region = contour[
            (contour[:, 0, 1] > y + h * 0.2) & (contour[:, 0, 1] < y + h * 0.5)
        ]
        if len(chest_region):
            points["left_chest"]  = tuple(chest_region[np.argmin(chest_region[:, 0, 0])][0])
            points["right_chest"] = tuple(chest_region[np.argmax(chest_region[:, 0, 0])][0])

        # Waist — narrowest horizontal span in middle 40–65 %
        waist_region = contour[
            (contour[:, 0, 1] > y + h * 0.4) & (contour[:, 0, 1] < y + h * 0.65)
        ]
        if len(waist_region):
            waist_widths = []
            for py in range(int(y + h * 0.4), int(y + h * 0.65), 2):
                row = waist_region[waist_region[:, 0, 1] == py]
                if len(row) >= 2:
                    waist_widths.append((np.max(row[:, 0, 0]) - np.min(row[:, 0, 0]), py))
            if waist_widths:
                _, waist_y = min(waist_widths, key=lambda item: item[0])
                waist_pts  = waist_region[waist_region[:, 0, 1] == waist_y]
                if len(waist_pts):
                    points["left_waist"]  = tuple(waist_pts[np.argmin(waist_pts[:, 0, 0])][0])
                    points["right_waist"] = tuple(waist_pts[np.argmax(waist_pts[:, 0, 0])][0])

        # Hip — widest span in bottom 60 %
        hip_region = contour[contour[:, 0, 1] > y + h * 0.6]
        if len(hip_region):
            points["left_hip"]  = tuple(hip_region[np.argmin(hip_region[:, 0, 0])][0])
            points["right_hip"] = tuple(hip_region[np.argmax(hip_region[:, 0, 0])][0])

        # Hem — bottommost point
        bottom_region = contour[contour[:, 0, 1] > y + h * 0.9]
        if len(bottom_region):
            points["hem_center"] = tuple(bottom_region[np.argmax(bottom_region[:, 0, 1])][0])

        # Armholes — innermost side points in top 15–40 %
        armhole_region = contour[
            (contour[:, 0, 1] > y + h * 0.15) & (contour[:, 0, 1] < y + h * 0.4)
        ]
        if len(armhole_region) > 4:
            center_x = x + w / 2
            left_side  = armhole_region[armhole_region[:, 0, 0] < center_x]
            right_side = armhole_region[armhole_region[:, 0, 0] > center_x]
            if len(left_side):
                points["left_armhole"]  = tuple(left_side[np.argmax(left_side[:, 0, 0])][0])
            if len(right_side):
                points["right_armhole"] = tuple(right_side[np.argmin(right_side[:, 0, 0])][0])

        return points

    # ------------------------------------------------------------------
    # Step 3: Calculate proportions
    # ------------------------------------------------------------------

    def calculate_proportions(
        self,
        key_points: Dict[str, Tuple[int, int]],
        user_measurements: Dict,
    ) -> Dict:
        """
        Converts pixel distances to centimetres and computes aspect ratios.
        `user_measurements` must contain at least {"chest": <cm>} for scaling.
        """
        if not key_points:
            key_points = self.detect_key_points()
        if not key_points or self.garment_mask is None:
            return {}

        p = {}

        def width_px(left_key: str, right_key: str) -> Optional[float]:
            if left_key in key_points and right_key in key_points:
                return float(key_points[right_key][0] - key_points[left_key][0])
            return None

        def height_px(top_key: str, bottom_key: str) -> Optional[float]:
            if top_key in key_points and bottom_key in key_points:
                return float(key_points[bottom_key][1] - key_points[top_key][1])
            return None

        # Raw pixel measurements
        for label, lk, rk in [
            ("shoulder", "left_shoulder",  "right_shoulder"),
            ("chest",    "left_chest",     "right_chest"),
            ("waist",    "left_waist",     "right_waist"),
            ("hip",      "left_hip",       "right_hip"),
        ]:
            val = width_px(lk, rk)
            if val is not None:
                p[f"{label}_width_px"] = val

        total_len  = height_px("neck_center", "hem_center")
        bodice_len = height_px("neck_center", "left_waist")
        skirt_len  = height_px("left_waist",  "hem_center")

        if total_len  is not None: p["total_length_px"]  = total_len
        if bodice_len is not None: p["bodice_length_px"] = bodice_len
        if skirt_len  is not None: p["skirt_length_px"]  = skirt_len

        # Dimensionless ratios (scale-independent)
        if "chest_width_px" in p and "waist_width_px" in p and p["waist_width_px"] > 0:
            p["chest_to_waist_ratio"] = p["chest_width_px"] / p["waist_width_px"]

        if "waist_width_px" in p and "hip_width_px" in p and p["hip_width_px"] > 0:
            p["waist_to_hip_ratio"] = p["waist_width_px"] / p["hip_width_px"]

        if "bodice_length_px" in p and "total_length_px" in p and p["total_length_px"] > 0:
            p["bodice_to_total_ratio"] = p["bodice_length_px"] / p["total_length_px"]

        if "skirt_length_px" in p and "total_length_px" in p and p["total_length_px"] > 0:
            p["skirt_to_total_ratio"] = p["skirt_length_px"] / p["total_length_px"]

        # Scale pixels → cm using chest as reference
        if "chest_width_px" in p and "chest" in user_measurements and p["chest_width_px"] > 0:
            user_chest_panel_cm = user_measurements["chest"] / 4.0
            px_to_cm = user_chest_panel_cm / p["chest_width_px"]
            p["scale_px_to_cm"] = px_to_cm

            for key in list(p.keys()):
                if key.endswith("_px"):
                    p[key.replace("_px", "_cm")] = p[key] * px_to_cm

        self.proportions = p
        return p

    # ------------------------------------------------------------------
    # Step 4: Generate 2-D technical drawing
    # ------------------------------------------------------------------

    def generate_2d_technical_drawing(self, output_path: str) -> str:
        """
        Produces a clean flat-sketch PNG with the garment outline and
        key measurement lines annotated.
        """
        if self.image is None or self.garment_mask is None:
            self.extract_garment_outline()

        key_points = self.detect_key_points()

        drawing = np.ones_like(self.image) * 255  # White background

        if self.contours:
            cv2.drawContours(drawing, self.contours, -1, (0, 0, 0), 2)

        colour_map = {"left": (255, 0, 0), "right": (0, 0, 255)}
        for name, (px, py) in key_points.items():
            colour = colour_map.get(name.split("_")[0], (0, 180, 0))
            cv2.circle(drawing, (px, py), 5, colour, -1)
            cv2.putText(
                drawing,
                name.split("_")[0],
                (px + 8, py),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.38,
                colour,
                1,
            )

        grey = (160, 160, 160)
        for lk, rk in [
            ("left_shoulder", "right_shoulder"),
            ("left_chest",    "right_chest"),
            ("left_waist",    "right_waist"),
            ("left_hip",      "right_hip"),
        ]:
            if lk in key_points and rk in key_points:
                cv2.line(drawing, key_points[lk], key_points[rk], grey, 1)

        os.makedirs(os.path.dirname(output_path), exist_ok=True) if os.path.dirname(output_path) else None
        cv2.imwrite(output_path, drawing)
        return output_path


# ---------------------------------------------------------------------------
# Step 5: Map proportions → pattern-formula adjustments
# ---------------------------------------------------------------------------

def match_proportions_to_formulas(proportions: Dict, garment_type: str) -> Dict:
    """
    Translates extracted photo proportions into adjustment parameters
    that override the default FreeSewing / Aldrich formula values.
    """
    adjustments: Dict = {}

    # Bodice length
    if "bodice_to_total_ratio" in proportions:
        ratio = proportions["bodice_to_total_ratio"]
        adjustments["bodice_length_factor"] = (
            0.9 if ratio < 0.4 else 1.1 if ratio > 0.6 else 1.0
        )

    # Waist suppression
    if "chest_to_waist_ratio" in proportions:
        ratio = proportions["chest_to_waist_ratio"]
        if ratio > 1.3:
            adjustments["waist_suppression"] = "high"
            adjustments["dart_intake"]        = ratio - 1.0
        elif ratio > 1.15:
            adjustments["waist_suppression"] = "medium"
            adjustments["dart_intake"]        = (ratio - 1.0) * 0.8
        else:
            adjustments["waist_suppression"] = "low"
            adjustments["dart_intake"]        = 0

    # Hip flare
    if "waist_to_hip_ratio" in proportions:
        ratio = proportions["waist_to_hip_ratio"]
        adjustments["hip_flare"] = (
            "high" if ratio < 0.8 else "medium" if ratio < 0.95 else "none"
        )

    # Pass through absolute measurements when available
    for key in ("bodice_length_cm", "skirt_length_cm"):
        if key in proportions:
            adjustments[key] = proportions[key]

    return {
        "base_formulas": "freesewing",
        "adjustments":   adjustments,
    }


if __name__ == "__main__":
    print("Garment-to-Pattern Extraction System")
    print("Dependencies: OpenCV, NumPy (open-source)")
