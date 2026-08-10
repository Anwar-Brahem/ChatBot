# -*- coding: utf-8 -*-
"""
test/text_processing.py - Normalisation de la syntaxe des descriptions SOS et filtres de cohérence
"""

import re

INFINITIVE_MAP = {
    # Présent de l'indicatif -> Infinitif
    "prend": "Prendre", "prends": "Prendre", "prennent": "Prendre",
    "déplace": "Déplacer", "déplaces": "Déplacer", "déplacent": "Déplacer",
    "tourne": "Tourner", "tournes": "Tourner", "tournent": "Tourner",
    "contrôle": "Contrôler", "contrôles": "Contrôler", "contrôlent": "Contrôler",
    "controle": "Contrôler", "controles": "Contrôler", "controlent": "Contrôler",
    "vérifie": "Vérifier", "vérifies": "Vérifier", "vérifient": "Vérifier",
    "verifie": "Vérifier", "verifies": "Vérifier", "verifient": "Vérifier",
    "coupe": "Couper", "coupes": "Couper", "coupent": "Couper",
    "lisse": "Lisser", "lisses": "Lisser", "lissent": "Lisser",
    "aligne": "Aligner", "alignes": "Aligner", "alignent": "Aligner",
    "oriente": "Orienter", "orientes": "Orienter", "orientent": "Orienter",
    "pousse": "Pousser", "pousses": "Pousser", "poussent": "Pousser",
    "tire": "Tirer", "tires": "Tirer", "tirent": "Tirer",
    "glisse": "Glisser", "glisses": "Glisser", "glissent": "Glisser",
    "introduis": "Introduire", "introduit": "Introduire", "introduisent": "Introduire",
    "inspecte": "Inspecter", "inspectes": "Inspecter", "inspectent": "Inspecter",
    "assure": "Assurer", "assures": "Assurer", "assurent": "Assurer",
    "maintiens": "Maintenir", "maintient": "Maintenir", "maintiennent": "Maintenir",
    "tiens": "Tenir", "tient": "Tenir", "tiennent": "Tenir",
    "mets": "Mettre", "met": "Mettre", "mettent": "Mettre",
    "souleve": "Soulever", "souleves": "Soulever", "soulevent": "Soulever",
    "assemble": "Assembler", "assembles": "Assembler", "assemblent": "Assembler",
    "conditionne": "Conditionner", "conditionnes": "Conditionner", "conditionnent": "Conditionner",
    "insère": "Insérer", "insères": "Insérer", "insèrent": "Insérer",
    "actionne": "Actionner", "actionnes": "Actionner", "actionnent": "Actionner",
}


def sanitize_analysis_step(step_dict: dict) -> dict:
    """
    Post-processing rule engine that eliminates common industrial VLM hallucinations.
    Corrects false bimanual/press predictions and fixes inverted supply/packaging actions.
    """
    if not isinstance(step_dict, dict):
        return step_dict

    desc = str(step_dict.get("description_complete", "")).strip()
    mouvement = str(step_dict.get("mouvement_observe", "")).strip().lower()
    points_cles = str(step_dict.get("points_cles", "")).strip()

    # 1. Correct false "Commande bimanuelle" / "Presse" when physical clamps or manual levers are used
    if "commande bimanuelle" in desc.lower() or "presse" in desc.lower() or "commande bimanuelle" in points_cles.lower():
        if any(kw in mouvement for kw in ["levier", "verrou", "pression", "serrage", "fermeture", "pousser"]):
            step_dict["action_principale"] = "Actionner"
            desc_clean = re.sub(r"la commande bimanuelle", "le levier du posage", desc, flags=re.IGNORECASE)
            desc_clean = re.sub(r"depuis la presse", "depuis le posage", desc_clean, flags=re.IGNORECASE)
            step_dict["description_complete"] = desc_clean
            step_dict["outils_fixations"] = "Posage à levier"
            step_dict["points_cles"] = re.sub(r"commande bimanuelle", "levier / posage", points_cles, flags=re.IGNORECASE)

    # 2. Correct false 'Conditionner' when pulling raw components from supply cardboard boxes
    if step_dict.get("action_principale") == "Conditionner":
        if any(kw in mouvement for kw in ["saisir", "extraire", "retirer", "bac en carton", "vrac", "agripper"]):
            step_dict["action_principale"] = "Prendre"
            step_dict["etape_principale_resume"] = "Prise de composant"
            step_dict["description_complete"] = re.sub(r"^Conditionner", "Prendre", desc, flags=re.IGNORECASE)

    return step_dict


def simplify_description(description):
    """Garde la description fluide tout en nettoyant les espaces superflus."""
    if not description:
        return description
    return description.strip()


def enforce_simple_description(description, step_type=None):
    """Fonction conservée pour compatibilité sans altérer la phrase originale."""
    return description


def enforce_infinitive_in_description(description):
    """S'assure que le premier mot de la description est au verbe infinitif."""
    if not description:
        return description

    words = description.strip().split()
    if not words:
        return description

    first_word = words[0]
    first_word_clean = re.sub(r'[^a-zA-ZàâäéèêëïîôùûüÀÂÄÉÈÊËÎÏÔÙÛÜ]', '', first_word).lower()

    if first_word_clean in INFINITIVE_MAP:
        words[0] = INFINITIVE_MAP[first_word_clean]
        return " ".join(words)

    # Majuscule sur la première lettre du premier mot si déjà à l'infinitif
    words[0] = words[0].capitalize()
    return " ".join(words)


def clean_points_cles(points_cles, description):
    """Nettoie les points clés en retirant la répétition du premier verbe."""
    if not points_cles or not description:
        return points_cles

    desc_words = description.split()
    if not desc_words:
        return points_cles

    first_verb = desc_words[0].lower()
    first_verb_variants = {first_verb, "contrôler", "controler", "vérifier", "verifier"}

    cleaned = points_cles
    for variant in first_verb_variants:
        cleaned = re.sub(r'\b' + re.escape(variant) + r'[,;\s]*', '', cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r',\s*,', ',', cleaned)
    cleaned = re.sub(r'^\s*,\s*', '', cleaned)
    cleaned = re.sub(r'\s*,\s*$', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    return cleaned.capitalize() if cleaned else points_cles