# -*- coding: utf-8 -*-
"""
data_collector.py - Archivage automatique des données pour le Fine-Tuning LoRA
"""

import os
import json
import io
import base64
import time
from PIL import Image

DATASET_DIR = "dataset_sos"
IMAGES_DIR = os.path.join(DATASET_DIR, "images")
ANNOTATIONS_FILE = os.path.join(DATASET_DIR, "dataset.jsonl")


def init_dataset_structure():
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR, exist_ok=True)


def save_training_sample(base64_images, final_json, workflow_type="auto", step_label=""):
    try:
        init_dataset_structure()
        timestamp = int(time.time() * 1000)
        saved_image_paths = []

        if isinstance(base64_images, list):
            for idx, img_item in enumerate(base64_images):
                if not img_item:
                    continue
                image_filename = f"step_{timestamp}_{idx}.jpg"
                image_path = os.path.join(IMAGES_DIR, image_filename)
                
                if isinstance(img_item, str) and os.path.exists(img_item):
                    with Image.open(img_item) as img:
                        img.convert("RGB").save(image_path, "JPEG", quality=90)
                else:
                    b64_str = str(img_item)
                    if "," in b64_str:
                        b64_str = b64_str.split(",")[1]
                    image_data = base64.b64decode(b64_str)
                    img = Image.open(io.BytesIO(image_data))
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    img.save(image_path, "JPEG", quality=90)
                
                saved_image_paths.append(image_path)

        dataset_entry = {
            "timestamp": timestamp,
            "workflow_type": workflow_type,
            "step_label": step_label,
            "images": saved_image_paths,
            "ground_truth": {
                "action_principale": final_json.get("action_principale", ""),
                "mouvement_observe": final_json.get("mouvement_observe", ""),
                "outils_fixations": final_json.get("outils_fixations", "Rien"),
                "description_complete": final_json.get("description_complete", ""),
                "points_cles": final_json.get("points_cles", ""),
                "raison_point_cle": final_json.get("raison_point_cle", ""),
                "temps_cycle_estime": final_json.get("temps_cycle_estime", "3s"),
                "cp_cs": final_json.get("cp_cs", "Non"),
                "etape_principale_resume": final_json.get("etape_principale_resume", "")
            }
        }

        with open(ANNOTATIONS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(dataset_entry, ensure_ascii=False) + "\n")

        print(f"[DATA COLLECTOR] Sample archivé dans '{ANNOTATIONS_FILE}'")
        return True

    except Exception as e:
        print(f"[DATA COLLECTOR ERROR] Erreur : {e}")
        return False