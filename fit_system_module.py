# ============================================================================
# FILE: fit_system_module.py
# PURPOSE: Collects fit preferences with state serialization (REFINED)
# ============================================================================

from typing import Dict, Any, List

def generate_custom_fit_questions(master_plan: Dict[str, Any], vision_analysis: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Generates customized fit questions based on garment features.
    Fallback when LLM doesn't generate proper dynamic_fit_questions.
    """
    questions = []
    
    # Extract features from vision analysis if available
    features = []
    if vision_analysis:
        features = vision_analysis.get("design_features", [])
    
    # Convert features to lowercase for easier checking
    features_lower = [str(f).lower() for f in features]
    
    # Detect garment characteristics
    has_sleeves = any(keyword in ' '.join(features_lower) for keyword in 
                     ['sleeve', 'long sleeve', 'short sleeve', 'puff sleeve', 'bishop sleeve'])
    has_waist = any(keyword in ' '.join(features_lower) for keyword in 
                   ['waist', 'fitted waist', 'belted', 'empire'])
    has_skirt = any(keyword in ' '.join(features_lower) for keyword in 
                   ['skirt', 'a-line', 'flared', 'tiered', 'maxi'])
    has_neckline = any(keyword in ' '.join(features_lower) for keyword in 
                      ['v-neck', 'v neck', 'scoop', 'sweetheart', 'neckline'])
    
    # Generate questions based on features
    if has_sleeves:
        questions.append({
            "key": "sleeve_fit",
            "q": "How should the sleeves fit?",
            "options": ["Fitted", "Regular", "Relaxed"]
        })
    
    if has_waist:
        questions.append({
            "key": "waist_fit",
            "q": "How should the waist fit?",
            "options": ["Cinched", "Fitted", "Relaxed"]
        })
    
    if has_skirt:
        questions.append({
            "key": "skirt_fullness",
            "q": "How full should the skirt be?",
            "options": ["Close", "Moderate", "Full"]
        })
    
    if has_neckline:
        questions.append({
            "key": "neckline_depth",
            "q": "How deep should the neckline be?",
            "options": ["Modest", "Standard", "Deep"]
        })
    
    # Always include overall ease preference
    questions.append({
        "key": "overall_ease",
        "q": "Overall, how should the garment fit?",
        "options": ["Close-fitting", "Standard", "Loose/Relaxed"]
    })
    
    print(f"🎯 Generated {len(questions)} custom fit questions based on garment features")
    return questions

class FitPreferencesCollector:
    def __init__(self, master_plan: Dict[str, Any], vision_analysis: Dict[str, Any] = None):
        # Get questions from master plan, or generate custom ones
        self.questions: List[Dict[str, Any]] = master_plan.get("dynamic_fit_questions", [])
        self.current_question_index: int = 0
        self.preferences: Dict[str, Any] = {}
        
        # If no questions generated or only has generic fallback, generate smart questions
        if not self.questions or (len(self.questions) == 1 and self.questions[0].get("key") == "ease_preference"):
            print("📋 Generating smart fit questions based on garment features...")
            self.questions = generate_custom_fit_questions(master_plan, vision_analysis)
        else:
            print(f"📋 Using {len(self.questions)} fit questions from master plan")

    def get_current_question(self) -> Dict[str, Any]:
        """Returns the current question data or None if complete."""
        if self.has_more_questions():
            return self.questions[self.current_question_index]
        return None

    def format_current_question(self) -> str:
        """Formats the current question for the chat interface."""
        q_data = self.get_current_question()
        if q_data:
            options_str = "\n".join([f"• {opt}" for opt in q_data['options']])
            return f"🎯 {q_data['q']}\n\nOptions:\n{options_str}"
        return "No more questions."


    def process_answer(self, raw_message: str) -> bool:
        """
        Processes a user's answer, validating it against options.
        Stores preference and advances index ONLY if valid. (REFINEMENT APPLIED)
        """
        current_q = self.get_current_question()
        if not current_q:
            return False

        q_data = current_q
        answer_lower = raw_message.strip().lower()

        # Check if the user's message contains any of the valid options
        matched_option = next(
            (opt for opt in q_data['options'] if opt.lower() in answer_lower), 
            None
        )
        
        if matched_option:
            self.preferences[q_data['key']] = matched_option
            self.current_question_index += 1
            return True
            
        return False # Invalid answer, do not advance state

    def has_more_questions(self) -> bool:
        return self.current_question_index < len(self.questions)

    def get_all_preferences(self) -> Dict[str, Any]:
        return self.preferences

    def serialize(self) -> Dict[str, Any]:
        """Converts the object state to a storable dictionary."""
        return {
            "questions": self.questions,
            "current_index": self.current_question_index,
            "preferences": self.preferences
        }

    @classmethod
    def deserialize(cls, data: Dict[str, Any], master_plan: Dict[str, Any], vision_analysis: Dict[str, Any] = None):
        """Reconstructs the object from a stored dictionary."""
        # Note: We must pass master_plan only to satisfy the __init__ signature,
        # but immediately override questions with serialized data to maintain history.
        collector = cls(master_plan, vision_analysis)
        collector.questions = data["questions"]
        collector.current_question_index = data["current_index"]
        collector.preferences = data["preferences"]
        return collector