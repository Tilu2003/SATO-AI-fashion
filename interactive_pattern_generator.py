"""
Interactive Pattern Generator with User Preferences
Uses Gemini vision analysis to ask relevant questions and collect all needed data
"""

from typing import Dict, List, Any, Optional
import json

class PatternQuestionnaire:
    """
    Generates dynamic questions based on Gemini's vision analysis
    and collects ALL information needed for accurate pattern generation
    """
    
    def __init__(self, gemini_analysis: Dict[str, Any]):
        self.analysis = gemini_analysis
        self.garment_type = gemini_analysis.get('garment_type', 'dress')
        self.features = gemini_analysis.get('style_features', [])
        self.answers = {}
        self.current_step = 0
        self.questions = self._generate_questions()
        
    def _generate_questions(self) -> List[Dict]:
        """Generate questions based on what Gemini detected"""
        questions = []
        
        # Always ask for basic preferences first
        questions.append({
            "id": "garment_confirmation",
            "question": f"I detected a **{self.garment_type}**. Is this correct?",
            "type": "yes_no",
            "options": ["yes", "no"],
            "follow_up": "If no, what type of garment is it?"
        })
        
        # Closure type questions
        if self.garment_type in ['dress', 'top', 'shirt', 'blouse']:
            questions.append({
                "id": "closure_type",
                "question": "What type of closure would you like?",
                "type": "choice",
                "options": [
                    "Invisible zipper (side)",
                    "Exposed zipper (back)",
                    "Buttons (front)",
                    "Buttons (back)",
                    "No closure (pullover)",
                    "Hook and eye"
                ],
                "required": True
            })
            
            # If zipper, ask position
            questions.append({
                "id": "zipper_position",
                "question": "Where should the zipper be placed?",
                "type": "choice",
                "depends_on": {"closure_type": ["zipper"]},
                "options": [
                    "Left side seam",
                    "Right side seam",
                    "Center back",
                    "Invisible in seam"
                ]
            })
        
        # Sleeve questions based on detection
        has_sleeves = any(s in str(self.features).lower() for s in ['sleeve', 'arm'])
        questions.append({
            "id": "sleeve_type",
            "question": f"What sleeve style? (Detected: {self.analysis.get('sleeve_type', 'unknown')})",
            "type": "choice",
            "options": [
                "Long fitted sleeve",
                "Long loose sleeve",
                "3/4 length sleeve",
                "Short sleeve (just past shoulder)",
                "Cap sleeve (covers shoulder)",
                "Sleeveless",
                "Straps"
            ],
            "required": True
        })
        
        # Neckline questions
        questions.append({
            "id": "neckline_type",
            "question": f"Neckline style? (Detected: {self.analysis.get('neckline', 'unknown')})",
            "type": "choice",
            "options": [
                "Round crew neck",
                "V-neck (shallow)",
                "V-neck (deep)",
                "Square neckline",
                "Scoop neck",
                "Boat neck",
                "High neck/mock turtleneck",
                "Halter neck",
                "Off-shoulder"
            ],
            "required": True
        })
        
        # Collar questions if needed
        if 'collar' in str(self.features).lower():
            questions.append({
                "id": "collar_type",
                "question": "What collar style would you like?",
                "type": "choice",
                "options": [
                    "No collar",
                    "Standard shirt collar",
                    "Peter Pan collar",
                    "Mandarin collar",
                    "Shawl collar",
                    "Notched collar"
                ]
            })
        
        # Pocket questions
        questions.append({
            "id": "pockets",
            "question": "Do you want pockets?",
            "type": "choice",
            "options": [
                "No pockets",
                "Patch pockets (sewn on surface)",
                "In-seam pockets (hidden in seam)",
                "Welt pockets (formal, with flap)",
                "Kangaroo pocket (front)",
                "Both patch and in-seam"
            ]
        })
        
        # For dresses/skirts
        if self.garment_type in ['dress', 'skirt']:
            questions.append({
                "id": "skirt_type",
                "question": "What skirt style?",
                "type": "choice",
                "options": [
                    "A-line (fitted waist, flares out)",
                    "Pencil (straight, fitted)",
                    "Circle skirt (very full)",
                    "Pleated",
                    "Gathered/Full",
                    "Tiered"
                ],
                "required": True
            })
            
            questions.append({
                "id": "skirt_length",
                "question": "Desired length?",
                "type": "choice",
                "options": [
                    "Mini (above knee)",
                    "Knee length",
                    "Midi (mid-calf)",
                    "Maxi (ankle length)",
                    "Custom length"
                ],
                "required": True
            })
        
        # Waist fit
        questions.append({
            "id": "waist_fit",
            "question": "How should it fit at the waist?",
            "type": "choice",
            "options": [
                "Fitted (no ease)",
                "Slightly relaxed (+2cm ease)",
                "Loose (+5cm ease)",
                "Very loose (+10cm ease)"
            ],
            "required": True
        })
        
        # Bust fit for women's garments
        if self.garment_type in ['dress', 'top', 'blouse']:
            questions.append({
                "id": "bust_fit",
                "question": "Bust fit preference?",
                "type": "choice",
                "options": [
                    "Very fitted (no ease)",
                    "Fitted (+2cm ease)",
                    "Relaxed (+5cm ease)",
                    "Loose (+8cm ease)"
                ],
                "required": True
            })
            
            questions.append({
                "id": "bust_darts",
                "question": "Bust dart style?",
                "type": "choice",
                "options": [
                    "Standard dart from side",
                    "Princess seams",
                    "No darts (loose fit)",
                    "Gather instead of darts"
                ]
            })
        
        # Hem finish
        questions.append({
            "id": "hem_style",
            "question": "Hem finish preference?",
            "type": "choice",
            "options": [
                "Simple fold (2cm)",
                "Narrow roll hem",
                "Faced hem",
                "Binding/trim",
                "Curved/hi-lo hem"
            ]
        })
        
        # Lining
        questions.append({
            "id": "lining",
            "question": "Do you want lining?",
            "type": "choice",
            "options": [
                "No lining",
                "Full lining",
                "Half lining (bodice only)",
                "Facing only (neck and armholes)"
            ]
        })
        
        # Special features detected by Gemini
        if 'belt' in str(self.features).lower():
            questions.append({
                "id": "belt_loops",
                "question": "Belt loops or sewn-in belt?",
                "type": "choice",
                "options": ["Belt loops", "Sewn-in belt", "No belt"]
            })
        
        if 'ruffle' in str(self.features).lower() or 'gather' in str(self.features).lower():
            questions.append({
                "id": "gathering",
                "question": "Where should gathering/ruffles be?",
                "type": "multi_choice",
                "options": ["Shoulders", "Waist", "Cuffs", "Hem", "Neckline"]
            })
        
        # Measurement-related questions
        questions.append({
            "id": "measurement_unit",
            "question": "What unit for measurements?",
            "type": "choice",
            "options": ["Centimeters (cm)", "Inches (in)"],
            "required": True
        })
        
        # Final customization
        questions.append({
            "id": "special_requests",
            "question": "Any special requests or modifications?",
            "type": "text",
            "optional": True,
            "placeholder": "E.g., 'Add contrast piping', 'Extra long torso', 'Maternity panel'"
        })
        
        return questions
    
    def get_current_question(self) -> Optional[Dict]:
        """Get current question, respecting dependencies"""
        while self.current_step < len(self.questions):
            question = self.questions[self.current_step]
            
            # Check if question has dependencies
            if "depends_on" in question:
                deps = question["depends_on"]
                should_skip = True
                
                for answer_id, required_values in deps.items():
                    user_answer = self.answers.get(answer_id, "")
                    if any(val.lower() in user_answer.lower() for val in required_values):
                        should_skip = False
                        break
                
                if should_skip:
                    self.current_step += 1
                    continue
            
            return question
        
        return None
    
    def answer_question(self, answer: str) -> bool:
        """Record answer and move to next question"""
        if self.current_step >= len(self.questions):
            return False
        
        current_q = self.questions[self.current_step]
        self.answers[current_q["id"]] = answer
        self.current_step += 1
        return True
    
    def is_complete(self) -> bool:
        """Check if all required questions answered"""
        return self.current_step >= len(self.questions)
    
    def get_all_answers(self) -> Dict:
        """Get all collected answers"""
        return self.answers
    
    def get_required_measurements(self) -> List[Dict]:
        """Generate list of measurements needed based on answers"""
        measurements = []
        
        # Standard measurements everyone needs
        measurements.append({
            "name": "chest",
            "description": "Full chest/bust circumference at fullest part",
            "unit": self.answers.get("measurement_unit", "cm"),
            "required": True
        })
        
        measurements.append({
            "name": "waist",
            "description": "Natural waist circumference (narrowest part)",
            "unit": self.answers.get("measurement_unit", "cm"),
            "required": True
        })
        
        measurements.append({
            "name": "hips",
            "description": "Full hip circumference at widest part",
            "unit": self.answers.get("measurement_unit", "cm"),
            "required": True
        })
        
        # Garment-specific measurements
        if self.garment_type in ['dress', 'top', 'shirt']:
            measurements.extend([
                {
                    "name": "neck",
                    "description": "Neck circumference at base",
                    "required": True
                },
                {
                    "name": "shoulder_width",
                    "description": "Across shoulders (from shoulder point to shoulder point)",
                    "required": True
                },
                {
                    "name": "back_length",
                    "description": "From nape of neck to waist (back)",
                    "required": True
                },
                {
                    "name": "front_length",
                    "description": "From shoulder over bust to waist (front)",
                    "required": True
                }
            ])
        
        # Sleeve measurements
        sleeve_type = self.answers.get("sleeve_type", "")
        if "long" in sleeve_type.lower() or "3/4" in sleeve_type.lower():
            measurements.extend([
                {
                    "name": "arm_length",
                    "description": "Shoulder to wrist (arm slightly bent)",
                    "required": True
                },
                {
                    "name": "bicep",
                    "description": "Upper arm circumference at fullest part",
                    "required": True
                },
                {
                    "name": "wrist",
                    "description": "Wrist circumference",
                    "required": True
                }
            ])
        elif "short" in sleeve_type.lower() or "cap" in sleeve_type.lower():
            measurements.append({
                "name": "bicep",
                "description": "Upper arm circumference",
                "required": True
            })
        
        # Skirt measurements
        if self.garment_type in ['dress', 'skirt']:
            measurements.append({
                "name": "skirt_length",
                "description": "From waist to desired hem",
                "required": True
            })
        
        # Additional measurements based on fit preference
        bust_fit = self.answers.get("bust_fit", "")
        if "fitted" in bust_fit.lower():
            measurements.extend([
                {
                    "name": "bust_point_separation",
                    "description": "Distance between bust points",
                    "required": False
                },
                {
                    "name": "bust_height",
                    "description": "From shoulder to bust point",
                    "required": False
                }
            ])
        
        return measurements
    
    def format_question_for_display(self) -> str:
        """Format current question with options for display"""
        question = self.get_current_question()
        if not question:
            return "All questions completed!"
        
        output = f"**Question {self.current_step + 1}/{len(self.questions)}**\n\n"
        output += f"{question['question']}\n\n"
        
        if question["type"] == "choice":
            output += "**Options:**\n"
            for i, option in enumerate(question["options"], 1):
                output += f"{i}. {option}\n"
            output += "\nReply with the number or full text of your choice."
        
        elif question["type"] == "yes_no":
            output += "Reply: **yes** or **no**"
        
        elif question["type"] == "multi_choice":
            output += "**Select all that apply:**\n"
            for i, option in enumerate(question["options"], 1):
                output += f"{i}. {option}\n"
            output += "\nReply with numbers separated by commas (e.g., '1, 3, 5')"
        
        elif question["type"] == "text":
            output += f"*{question.get('placeholder', 'Type your answer here...')}*"
        
        return output
