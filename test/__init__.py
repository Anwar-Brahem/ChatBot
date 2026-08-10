# -*- coding: utf-8 -*-
"""
test/__init__.py - Point d'entree du package test.

Ce package remplace l'ancien test.py monolithique (analyseur video),
decoupe en plusieurs petits fichiers par responsabilite : verbes
(verb_utils.py), nettoyage de texte (text_processing.py), extraction
video (video_extraction.py), appel Ollama (ollama_client.py), et
orchestration (pipeline.py). Tout est reexporte ici, donc partout
ailleurs dans le projet, `import test` continue de fonctionner
exactement comme avant (ex: test.run_pipeline(...)), sans aucun
changement de logique.
"""

from .verb_utils import normalize_verb, extract_verbs_from_text, VERB_NORMALIZATION, BASE_VERBS
from .text_processing import (
    simplify_description,
    enforce_simple_description,
    enforce_infinitive_in_description,
    clean_points_cles,
    INFINITIVE_MAP,
)
from .video_extraction import encode_image_to_base64, extract_frames_smart
from .ollama_client import analyze_sequence_with_ollama, OLLAMA_API_URL, MODEL_NAME
from .pipeline import run_pipeline
