# -*- coding: utf-8 -*-
"""
test/ollama_client.py - Appel au modèle Ollama / Séquence en deux passes FOR-054
"""

import re
import json
import io
import base64
import os
from PIL import Image
import requests
import time
import datetime

import config
from config.prompts import PASS1_AGGREGATION_PROMPT, PASS2_FOR054_PROMPT
from .text_processing import (
    enforce_infinitive_in_description,
    simplify_description,
)

OLLAMA_API_URL = "http://localhost:11434/api/chat"
MODEL_NAME = getattr(config, "OLLAMA_MODEL", "gemma4:31b")

def get_active_model_name():
    """Récupère le modèle Ollama configuré dynamiquement."""
    return getattr(config, "OLLAMA_MODEL", "gemma4:31b")

def _log(msg):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

def safe_parse_json(content):
    if not content or not content.strip():
        return {}

    cleaned = content.strip()
    
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

    parsed = {}
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*?\}", cleaned)
        if match:
            try:
                parsed = json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

    if isinstance(parsed, list):
        if len(parsed) > 0 and isinstance(parsed[0], dict):
            return parsed[0]
        return {}
    
    return parsed if isinstance(parsed, dict) else {}

def optimize_base64_image(base64_str, max_size=(384, 384)):
    try:
        if isinstance(base64_str, str) and os.path.isfile(base64_str):
            with Image.open(base64_str) as img:
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=60, optimize=True)
                return base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        if "," in base64_str:
            base64_str = base64_str.split(",", 1)[1]

        image_data = base64.b64decode(base64_str)
        img = Image.open(io.BytesIO(image_data))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=60, optimize=True)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception:
        return base64_str


def _post_with_retry(payload, max_retries=3, timeout=(10, 500)):
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=timeout)
            if response.status_code in (502, 503) and attempt < max_retries:
                time.sleep(2 * attempt)
                continue
            return response
        except requests.exceptions.RequestException:
            if attempt == max_retries:
                raise
            time.sleep(2 * attempt)
    return None


def analyze_sequence_two_pass(images_base64, previous_action, workflow_context, forced_step_label=None):
    optimized_images = [optimize_base64_image(img) for img in images_base64]
    active_model = get_active_model_name()

    # --- PASSE 1 ---
    prompt_p1 = PASS1_AGGREGATION_PROMPT.format(
        previous_action=previous_action,
        workflow_context=workflow_context
    )
    
    payload_p1 = {
        "model": active_model,
        "messages": [{"role": "user", "content": prompt_p1, "images": optimized_images}],
        "format": "json",
        "stream": False
    }
    
    resp_p1 = _post_with_retry(payload_p1)

    raw_content_p1 = ""
    if resp_p1 and resp_p1.ok:
        try:
            raw_content_p1 = resp_p1.json().get("message", {}).get("content", "")
        except Exception:
            raw_content_p1 = ""

    res_p1 = safe_parse_json(raw_content_p1)

    etape_macro = forced_step_label or res_p1.get("etape_macro", "Opération assemblée")
    gestes = res_p1.get("gestes_observes", "Manipulation continue de la pièce")
    duree = res_p1.get("duree_cumulee_secondes", 5)
    
    duree_str = str(duree).strip().rstrip('s')

    # --- PASSE 2 ---
    prompt_p2 = PASS2_FOR054_PROMPT.format(
        etape_macro=etape_macro,
        gestes_observes=gestes,
        duree_cumulee=duree_str
    )
    
    payload_p2 = {
        "model": active_model,
        "messages": [{"role": "user", "content": prompt_p2}],
        "format": "json",
        "stream": False
    }

    resp_p2 = _post_with_retry(payload_p2)

    raw_content_p2 = ""
    if resp_p2 and resp_p2.ok:
        try:
            raw_content_p2 = resp_p2.json().get("message", {}).get("content", "")
        except Exception:
            raw_content_p2 = ""

    parsed_json = safe_parse_json(raw_content_p2)

    desc = parsed_json.get("description_complete", "")

    if isinstance(desc, list):
        desc = " ".join([str(item) for item in desc if item])

    if desc and isinstance(desc, str):
        parsed_json["description_complete"] = enforce_infinitive_in_description(simplify_description(desc))

    return parsed_json


def analyze_sequence_with_ollama(images_base64, previous_action, used_verbs=None,
                                  workflow_type="auto", custom_steps=None,
                                  conditioning_mode="conditionner",
                                  forced_step_label=None, step_index=None, total_steps=None,
                                  progress_callback=None, cancellation_event=None):
    
    if getattr(config, "USE_CUSTOM_LORA_MODEL", False):
        try:
            from custom_model_client import analyze_sequence_with_custom_model
            return analyze_sequence_with_custom_model(
                images_base64, previous_action,
                forced_step_label=forced_step_label,
                progress_callback=progress_callback,
                cancellation_event=cancellation_event
            )
        except Exception as e:
            _log(f"⚠️ Erreur modèle sur-mesure, repli sur Ollama : {e}")

    if cancellation_event and cancellation_event.is_set():
        _log("Interruption détectée avant envoi Ollama.")
        return {}

    workflow_ctx = f"Étape {step_index}/{total_steps} : {forced_step_label}" if forced_step_label else "Analyse automatique du poste"
    
    if progress_callback:
        progress_callback(f"Analyse avec {get_active_model_name()}...")

    try:
        t0 = time.time()
        _log(f"→ Lancement de l'analyse deux passes ({get_active_model_name()}) vers {OLLAMA_API_URL}")
        
        result = analyze_sequence_two_pass(
            images_base64=images_base64,
            previous_action=previous_action,
            workflow_context=workflow_ctx,
            forced_step_label=forced_step_label
        )
        
        _log(f"← Analyse deux passes terminée en {time.time() - t0:.1f}s")
        return result

    except requests.exceptions.RequestException as e:
        if cancellation_event and cancellation_event.is_set():
            return {}
        err_msg = f"Erreur réseau : {e}"
        if progress_callback:
            progress_callback(err_msg)
        else:
            _log(err_msg)
        return {
            "action_principale": "Erreur Réseau",
            "mouvement_observe": str(e),
            "outils_fixations": "Aucun",
            "description_complete": str(e),
            "points_cles": "",
            "raison_point_cle": "Perte du temps",
            "temps_cycle_estime": "3s",
            "cp_cs": "Non",
            "etape_principale_resume": "Erreur"
        }
    except Exception as e:
        if cancellation_event and cancellation_event.is_set():
            return {}
        err_msg = f"Erreur d'analyse : {e}"
        if progress_callback:
            progress_callback(err_msg)
        else:
            _log(err_msg)
        return {
            "action_principale": "Erreur de Format",
            "mouvement_observe": str(e),
            "outils_fixations": "Aucun",
            "description_complete": str(e),
            "points_cles": "",
            "raison_point_cle": "Perte du temps",
            "temps_cycle_estime": "3s",
            "cp_cs": "Non",
            "etape_principale_resume": "Erreur format"
        }