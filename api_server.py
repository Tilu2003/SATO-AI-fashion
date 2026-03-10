# ============================================================================
# FILE: api_server.py
# PURPOSE: Main Flask application — 5-stage conversational pattern flow.
# ============================================================================

from flask import Flask, request, jsonify, send_from_directory
import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from vision_module import analyze_garment
from master_tailor_module import get_master_plan, assess_complexity
from nlp_module import parse_user_intent
from measurement_form_generator import get_measurements_for_garment, validate_measurements
from fit_system_module import FitPreferencesCollector
from hybrid_engine_module import generate_pattern_hybrid
from validation_module import run_3d_validation
from tutorial_module import find_youtube_tutorials       # split out from validation_module
from upload_handler import handle_upload                 # split out from validation_module
from llm_provider import validate_hybrid_setup, LLMConfig
from garment_extraction import GarmentProportionExtractor, match_proportions_to_formulas
from proportion_pattern_generator import ProportionBasedPatternGenerator
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder="static")
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
if not app.secret_key:
    raise RuntimeError("FLASK_SECRET_KEY environment variable is not set. Aborting.")

SESSION_DB_FILE = "sessions.json"


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

def load_sessions() -> Dict[str, Any]:
    if os.path.exists(SESSION_DB_FILE):
        try:
            with open(SESSION_DB_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("WARNING: Corrupt sessions.json — starting fresh.")
    return {}


def save_sessions(sessions: Dict[str, Any]) -> None:
    with open(SESSION_DB_FILE, "w") as f:
        json.dump(sessions, f, indent=4)


SESSIONS: Dict[str, Any] = load_sessions()


def create_session() -> Dict[str, Any]:
    return {
        "stage": "UPLOAD",
        "image_path": None,
        "analysis": None,
        "master_plan": None,
        "complexity": None,
        "proportions": None,
        "formula_adjustments": None,
        "technical_drawing": None,
        "questionnaire": None,
        "user_preferences": {},
        "measurement_form_config": None,
        "measurements": {},
        "fit_collector_state": None,
        "created_at": str(datetime.now()),
    }


# ============================================================================
# CORE LOGIC — 5-STAGE FLOW
# ============================================================================

def process_stage(
    message, image_path_input, session: Dict[str, Any]
):
    output_link = None
    bot_response = ""
    form_data = None

    image_path = image_path_input if image_path_input else session.get("image_path")

    # Rehydrate fit-collector if state exists
    collector = None
    if session.get("fit_collector_state") and session.get("master_plan"):
        try:
            collector = FitPreferencesCollector.deserialize(
                session["fit_collector_state"],
                session["master_plan"],
                session.get("vision_analysis"),
            )
        except Exception as e:
            print(f"Error deserialising FitPreferencesCollector: {e}")
            session["fit_collector_state"] = None

    try:
        # =================================================================
        # STAGE 1: UPLOAD
        # =================================================================
        if session["stage"] == "UPLOAD":
            if not image_path:
                bot_response = (
                    "👋 **Welcome to SATO Interactive Pattern Generator!**\n\n"
                    "Upload an image of the garment you want to recreate.\n"
                    "I'll analyse it with Gemini AI and ask you detailed questions "
                    "to create the perfect pattern."
                )
                return bot_response, output_link, form_data, session

            session["image_path"] = image_path

            user_description = (
                message
                if message and len(message.strip()) >= 3
                else (
                    "Analyse this garment in detail: identify the type, all visible "
                    "features (sleeves, neckline, closures, pockets, fit), fabric drape, "
                    "construction details, and any special design elements."
                )
            )

            print("🤖 [1/3] Running Gemini Vision Analysis…")
            analysis = analyze_garment(image_path, user_description)

            has_gemini_error = "error" in analysis and analysis.get("garment_type") == "dress"
            if "error" in analysis and not has_gemini_error:
                raise Exception(f"Vision failed: {analysis['error']}")

            print("🤖 [2/3] Extracting garment proportions with computer vision…")
            try:
                extractor = GarmentProportionExtractor(image_path, analysis)
                extractor.extract_garment_outline()
                key_points = extractor.detect_key_points()
                proportions = extractor.calculate_proportions(key_points, {"chest": 90})

                tech_drawing_path = (
                    f"static/downloads/technical_drawing_{uuid.uuid4().hex[:8]}.png"
                )
                extractor.generate_2d_technical_drawing(tech_drawing_path)

                formula_adjustments = match_proportions_to_formulas(
                    proportions, analysis.get("garment_type", "dress")
                )

                print("✅ CV extraction successful!")
                if "chest_to_waist_ratio" in proportions:
                    print(f"   Chest-to-waist ratio: {proportions['chest_to_waist_ratio']:.2f}")
                if "bodice_length_cm" in proportions:
                    print(f"   Bodice length: {proportions['bodice_length_cm']:.1f} cm")

            except Exception as cv_error:
                print(f"⚠️  CV extraction failed: {cv_error}")
                proportions = {}
                formula_adjustments = {}
                tech_drawing_path = None

            print("🤖 [3/3] Generating measurement form…")

            session.update(
                {
                    "analysis": analysis,
                    "vision_analysis": analysis,
                    "proportions": proportions,
                    "formula_adjustments": formula_adjustments,
                    "technical_drawing": tech_drawing_path,
                    "master_plan": get_master_plan(analysis),
                }
            )

            response = "✅ **AI Analysis Complete!**\n\n"

            if proportions:
                response += "📐 **Extracted Proportions:**\n"
                if "chest_to_waist_ratio" in proportions:
                    ratio = proportions["chest_to_waist_ratio"]
                    fit_desc = (
                        "Very fitted" if ratio > 1.25
                        else "Fitted" if ratio > 1.1
                        else "Relaxed"
                    )
                    response += f"- Fit: {fit_desc} (ratio: {ratio:.2f})\n"
                if "bodice_length_cm" in proportions:
                    response += f"- Bodice length: {proportions['bodice_length_cm']:.1f} cm\n"
                if "skirt_length_cm" in proportions:
                    response += f"- Skirt length: {proportions['skirt_length_cm']:.1f} cm\n"
                if tech_drawing_path:
                    response += (
                        f"\n[View Technical Drawing]"
                        f"({tech_drawing_path.replace('static/', '')})\n"
                    )
                response += "\n"

            if has_gemini_error:
                response += "⚠️  **Note:** Using basic analysis (Gemini API timeout)\n\n"

            response += f"**Detected:** {analysis.get('garment_type', 'garment').title()}\n"
            response += f"**Features Found:** {', '.join(analysis.get('style_features', ['basic']))}\n"
            if analysis.get("description"):
                response += f"**Details:** {analysis['description'][:150]}…\n"

            garment_type   = session["analysis"].get("garment_type", "dress")
            style_features = session["analysis"].get("style_features", [])
            form_config    = get_measurements_for_garment(garment_type, style_features)

            session["measurement_form_config"] = form_config
            session["stage"] = "MEASUREMENTS"

            form_data = {
                "form_fields": form_config["form_fields"],
                "total_count": form_config["total_count"],
                "garment_info": form_config.get("garment_info", {}),
            }

            response += (
                f"\n\n📏 **Please provide your measurements in CM:**\n"
                f"I need {form_config['total_count']} measurements to generate your pattern.\n"
                "Send them as JSON or via the measurement form."
            )

            bot_response = response
            return bot_response, output_link, form_data, session

        # =================================================================
        # STAGE 2: MEASUREMENTS
        # =================================================================
        elif session["stage"] == "MEASUREMENTS":
            if isinstance(message, str):
                try:
                    measurements_data = json.loads(message)
                except json.JSONDecodeError:
                    bot_response = (
                        "⚠️  Please submit measurements as a JSON object or via the form."
                    )
                    return bot_response, output_link, form_data, session
            else:
                measurements_data = message

            validation_result = validate_measurements(
                measurements_data, session["measurement_form_config"]
            )

            if not validation_result["valid"]:
                bot_response = "❌ **Validation Errors:**\n\n"
                for error in validation_result["errors"]:
                    bot_response += f"• {error}\n"
                bot_response += "\nPlease correct and resubmit."

                form_data = {
                    "form_fields": session["measurement_form_config"]["form_fields"],
                    "errors": validation_result["errors"],
                    "warnings": validation_result["warnings"],
                    "submitted_values": measurements_data,
                }
                return bot_response, output_link, form_data, session

            session["measurements"] = validation_result["validated_measurements"]

            warnings_text = ""
            if validation_result["warnings"]:
                warnings_text = "\n⚠️  **Please verify:**\n"
                for w in validation_result["warnings"]:
                    warnings_text += f"• {w}\n"

            new_collector = FitPreferencesCollector(
                session["master_plan"], session.get("vision_analysis")
            )
            session["fit_collector_state"] = new_collector.serialize()
            session["stage"] = "FIT_QUESTIONS"

            bot_response = (
                f"✅ **All {len(validation_result['validated_measurements'])} "
                f"measurements received!**{warnings_text}\n\n"
                f"📋 **Next: {len(new_collector.questions)} fit questions.**\n"
                "Say **ok** to start."
            )
            return bot_response, output_link, form_data, session

        # =================================================================
        # STAGE 3: FIT_QUESTIONS
        # =================================================================
        elif session["stage"] == "FIT_QUESTIONS":
            if not collector:
                # Collector state was lost — recover gracefully
                print("⚠️  Fit collector state missing — reinitialising.")
                collector = FitPreferencesCollector(
                    session["master_plan"], session.get("vision_analysis")
                )
                session["fit_collector_state"] = collector.serialize()

            if (
                collector.current_question_index == 0
                and isinstance(message, str)
                and message.lower().strip() in {"yes", "ok", "ready", "start"}
            ):
                question_text = collector.format_current_question()
                bot_response = f"🎯 Starting fit interview…\n\n{question_text}"
                return bot_response, output_link, form_data, session

            if collector.process_answer(str(message)):
                session["fit_collector_state"] = collector.serialize()

                if collector.has_more_questions():
                    bot_response = f"✅ Got it!\n\n{collector.format_current_question()}"
                    return bot_response, output_link, form_data, session

                # All questions answered — generate pattern
                session["stage"] = "GENERATING"
                session["fit_preferences"] = collector.get_all_preferences()

                bot_response = "✅ **All preferences collected!**\n\n🎨 Generating your pattern…"

                if session.get("proportions") and session.get("formula_adjustments"):
                    print("🎨 Using proportion-based pattern generation (CV-enhanced)")
                    prop_gen = ProportionBasedPatternGenerator(
                        measurements=session["measurements"],
                        proportions=session["proportions"],
                        formula_adjustments=session["formula_adjustments"],
                    )
                    preferences   = session.get("user_preferences", {})
                    sleeve_type   = preferences.get("sleeve_style", "long")
                    neckline      = preferences.get("neckline_style", "round")
                    include_skirt = "skirt" in session["analysis"].get("garment_type", "").lower()

                    svg_content     = prop_gen.generate_pattern_from_proportions(
                        sleeve_type=sleeve_type,
                        neckline=neckline,
                        include_skirt=include_skirt,
                    )
                    output_filename = f"pattern_{uuid.uuid4().hex}.svg"
                    output_filepath = os.path.join("static", "downloads", output_filename)
                    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
                    with open(output_filepath, "w") as f:
                        f.write(svg_content)

                    tech_spec = prop_gen.generate_technical_spec_sheet()
                    result = {
                        "pattern_file": output_filename,
                        "method_used": "Proportion-Based (CV-Enhanced FreeSewing)",
                        "translation_confidence": 0.95,
                        "technical_spec": tech_spec,
                    }
                else:
                    print("🎨 Using standard pattern generation")
                    result = generate_pattern_hybrid(
                        session["master_plan"],
                        session["measurements"],
                        session["fit_preferences"],
                        session.get("complexity", {}),
                    )

                validation   = run_3d_validation(result, session["measurements"])
                tutorials    = find_youtube_tutorials(
                    session["master_plan"].get("key_sewing_techniques", [])
                )

                response  = "🎉 **Your Custom Pattern is Ready!**\n\n"
                response += f"**Quality Score:** {validation['score']}/100\n"
                response += f"**Method:** {result.get('method_used')}\n"
                response += f"**Confidence:** {int(result.get('translation_confidence', 0.85) * 100)}%\n\n"

                if "technical_spec" in result:
                    notes = result["technical_spec"].get("pattern_notes", [])
                    if notes:
                        response += "**Pattern Features:**\n"
                        for note in notes:
                            response += f"  • {note}\n"
                        response += "\n"

                if result.get("unsupported_features"):
                    response += "⚠️  **Manual adjustment needed:**\n"
                    for feat in result["unsupported_features"]:
                        response += f"  • {feat}\n"
                    response += "\n"

                response += "**Tutorials:**\n"
                for t in tutorials[:3]:
                    response += f"* {t['title']}: <{t['link']}>\n"

                output_link = f"/downloads/{result.get('pattern_file')}"
                session["stage"] = "COMPLETE"
                session["fit_collector_state"] = None

                bot_response = response + "\n📥 **Download your pattern via the link!**"
                return bot_response, output_link, form_data, session

            else:
                question_text = collector.format_current_question()
                bot_response = (
                    "❌ **Invalid selection.** Please choose one of the options.\n\n"
                    + question_text
                )
                return bot_response, output_link, form_data, session

        # =================================================================
        # STAGE 4: COMPLETE
        # =================================================================
        elif session["stage"] == "COMPLETE":
            intent = parse_user_intent(message, {"stage": "COMPLETE"})

            if intent.get("intent") == "iteration_request":
                bot_response = (
                    "🔄 Re-generating with modifications is coming soon. "
                    "Please start a new project for now."
                )
                return bot_response, output_link, form_data, session

            bot_response = "Thank you! Starting a new project."
            return bot_response, output_link, form_data, create_session()

        return "System error: unknown stage.", output_link, form_data, create_session()

    except Exception as e:
        import traceback
        print(f"CRITICAL ERROR in process_stage: {e}")
        traceback.print_exc()
        bot_response = f"🚨 A critical error occurred. Please restart the session.\nError: {e}"
        return bot_response, output_link, form_data, create_session()


# ============================================================================
# FLASK ENDPOINTS
# ============================================================================

@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify(
        {
            "status": "healthy",
            "gemini_configured": bool(LLMConfig.GEMINI_API_KEY),
            "version": "1.0.0",
        }
    )


@app.route("/upload", methods=["POST"])
def upload_endpoint():
    return handle_upload()


@app.route("/chat", methods=["POST"])
def chat_endpoint():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        session_id   = data.get("session_id")
        user_message = data.get("message", "").strip()
        image_path   = data.get("image_path")

        # Measurements submitted via the form take priority over plain text
        if data.get("measurements") and isinstance(data.get("measurements"), dict):
            user_message = data["measurements"]

        if not session_id or session_id not in SESSIONS:
            session_id          = str(uuid.uuid4())
            SESSIONS[session_id] = create_session()
            print(f"✅ Created new session: {session_id}")
        else:
            print(f"✅ Retrieved session: {session_id}")

        session = SESSIONS[session_id]

        bot_response, output_link, form_data, updated_session = process_stage(
            user_message, image_path, session
        )

        SESSIONS[session_id] = updated_session
        save_sessions(SESSIONS)

        response_data: Dict[str, Any] = {
            "session_id": session_id,
            "message": bot_response,
            "stage": updated_session["stage"],
            "file_link": output_link,
            "success": True,
        }
        if form_data:
            response_data["form"] = form_data

        return jsonify(response_data)

    except Exception as e:
        import traceback
        print(f"❌ Chat endpoint error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e), "message": f"An error occurred: {e}", "success": False}), 500


@app.route("/downloads/<path:filename>")
def download_file(filename: str):
    """Serve pattern files. Flask's send_from_directory prevents path traversal."""
    downloads_dir = os.path.join("static", "downloads")
    file_path     = os.path.join(downloads_dir, filename)

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    return send_from_directory(downloads_dir, filename, as_attachment=False)


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error.", "success": False}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found.", "success": False}), 404


# ============================================================================
# STARTUP
# ============================================================================

if __name__ == "__main__":
    if not os.environ.get("GEMINI_API_KEY"):
        print("!!! ERROR: GEMINI_API_KEY must be set in your .env file !!!")
        raise SystemExit(1)

    print("✅ Gemini API key found.")
    print("✅ Ollama will connect on first use.")
    os.makedirs("uploads", exist_ok=True)
    os.makedirs(os.path.join("static", "downloads"), exist_ok=True)
    print("🚀 SATO API starting on http://localhost:5000")
    app.run(debug=False, host="127.0.0.1", port=5000, use_reloader=False)
