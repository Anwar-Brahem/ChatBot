# -*- coding: utf-8 -*-
"""
custom_model_client.py - Inférence directe sur le modèle LoRA Fine-Tuné
"""

import os
import re
import json
import torch
from PIL import Image
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
from peft import PeftModel

MODEL_BASE = "Qwen/Qwen2-VL-2B-Instruct"
LORA_PATH = "my_sos_lora_weights"

_model = None
_processor = None

def load_custom_model():
    global _model, _processor
    if _model is None:
        if not os.path.exists(LORA_PATH):
            raise FileNotFoundError(f"Dossier de poids '{LORA_PATH}' introuvable. Exécutez train_lora.py d'abord.")
        
        print("[CUSTOM MODEL] Chargement du modèle entraîné...")
        base = Qwen2VLForConditionalGeneration.from_pretrained(
            MODEL_BASE,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        _model = PeftModel.from_pretrained(base, LORA_PATH)
        _processor = AutoProcessor.from_pretrained(LORA_PATH)
    return _model, _processor

def clean_json_string(text):
    """Extrait le JSON si le modèle le renvoie dans un bloc Markdown ```json ... ```"""
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        return match.group(1)
    match_raw = re.search(r'\{.*\}', text, re.DOTALL)
    if match_raw:
        return match_raw.group(0)
    return text

def analyze_sequence_with_custom_model(images_base64, previous_action, **kwargs):
    model, processor = load_custom_model()
    image_path = images_base64[0] if images_base64 else None
    
    if not image_path or not os.path.exists(image_path):
        return {}

    image = Image.open(image_path).convert("RGB")
    forced_step = kwargs.get("forced_step_label", "")

    # Prompt structuré exigeant un format JSON valide
    prompt = (
        f"<|im_start|>system\n"
        f"Tu es un expert en analyse de postes de travail industriels. "
        f"Réponds UNIQUEMENT sous forme d'un objet JSON valide sans texte avant ni après.<|im_end|>\n"
        f"<|im_start|>user\n"
        f"Étape visée : {forced_step}\n"
        f"Action précédente : {previous_action}\n\n"
        f"Fournis l'analyse au format JSON strict avec les clés suivantes :\n"
        f"{{\n"
        f'  "action_principale": "...",\n'
        f'  "etape_principale_resume": "...",\n'
        f'  "mouvement_observe": "...",\n'
        f'  "outils_fixations": "...",\n'
        f'  "points_cles_how": "...",\n'
        f'  "raison_why": "...",\n'
        f'  "description_complete": "...",\n'
        f'  "cp_cs": "Oui" ou "Non"\n'
        f"}}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )

    inputs = processor(images=image, text=prompt, return_tensors="pt").to("cuda")
    
    with torch.no_grad():
        output = model.generate(
            **inputs, 
            max_new_tokens=256,
            do_sample=False,
            temperature=0.1
        )

    # Récupérer uniquement les tokens générés par l'assistant
    generated_tokens = output[0][inputs.input_ids.shape[1]:]
    text_resp = processor.decode(generated_tokens, skip_special_tokens=True).strip()

    try:
        cleaned_resp = clean_json_string(text_resp)
        data = json.loads(cleaned_resp)
        return data
    except Exception as e:
        print(f"[CUSTOM MODEL WARNING] Échec parsing JSON: {e} | Réponse brute: {text_resp[:100]}...")
        return {
            "action_principale": "Manipulation",
            "etape_principale_resume": forced_step or "Étape",
            "mouvement_observe": text_resp if text_resp else "Observation non structurée",
            "outils_fixations": "Sans outil",
            "points_cles_how": "Suivre la consigne",
            "raison_why": "Assurer l'exécution correcte",
            "description_complete": text_resp if text_resp else "Détails non générés",
            "cp_cs": "Non"
        }