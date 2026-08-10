# -*- coding: utf-8 -*-
"""
config/workflows.py - Définitions des 5 types de workflows industriels et options associées
"""

import re
from typing import Dict, List, Any

# ═══════════════════════════════════════════════════════════════════
# DÉFAUTS DE CONTRÔLE PRÉDÉFINIS (FACE ASPECT / FACE TECHNIQUE)
# ═══════════════════════════════════════════════════════════════════
DEFAULT_DEFECT_OPTIONS = [
    "Pas de traces",
    "Point noir (si pièce blanche)",
    "Givrage",
    "Manque",
    "Cassé",
    "Déformation"
]

# ═══════════════════════════════════════════════════════════════════
# WORKFLOW DEFINITIONS — Standard Industrie PVL
# ═══════════════════════════════════════════════════════════════════

WORKFLOW_TYPES: Dict[str, Dict[str, Any]] = {
    "injection": {
        "label": "💉 Type 1 : Injection",
        "desc": "Flux standard injection plastique (4 étapes)",
        "has_control_choice": True,
        "steps": [
            "Prendre une pièce",
            "Contrôle traçabilité",
            "Contrôle face aspect ou face technique",
            "Conditionnement"
        ],
        "max_steps": 4,
        "prompt_addendum": (
            "Cette vidéo montre un procédé d'INJECTION. "
            "Le flux attendu est STRICTEMENT : 1) Prendre une pièce, 2) Contrôle traçabilité, "
            "3) Contrôle face d'aspect ou contrôle face technique, 4) Conditionnement."
        ),
    },
    "injection_assemblage": {
        "label": "🧩 Type 2 : Injection Assemblage",
        "desc": "Flux injection avec assemblage sur posage (8 étapes)",
        "has_control_choice": True,
        "steps": [
            "Prendre une pièce",
            "Contrôle traçabilité",
            "Contrôle face aspect ou face technique",
            "Mise en place sur posage",
            "Prise autre composant",
            "Assembler composant sur pièce",
            "Contrôle assemblage",
            "Conditionnement"
        ],
        "max_steps": 8,
        "prompt_addendum": (
            "Cette vidéo montre un procédé d'INJECTION ASSEMBLAGE. "
            "Le flux attendu est STRICTEMENT : 1) Prendre une pièce, 2) Contrôle traçabilité, "
            "3) Contrôle face d'aspect ou contrôle face technique, 4) Mise en place sur posage, "
            "5) Prise autre composant, 6) Assembler composant sur pièce, "
            "7) Contrôle assemblage, 8) Conditionnement."
        ),
    },
        "assemblage normal": {
            "label": "🧩 Type 3 : Assemblage Normal",
            "desc": "Flux assemblage (7 étapes)",
            "has_control_choice": True,
            "steps": [
                "Prendre une pièce",
                "Contrôle traçabilité",
                "Contrôle face aspect ou face technique",
                "Prise autre composant",
                "Assembler composant sur pièce",
                "Contrôle assemblage",
                "Conditionnement"
            ],
            "max_steps": 7,
            "prompt_addendum": (
                "Cette vidéo montre un procédé d'ASSEMBLAGE. "
                "Le flux attendu est STRICTEMENT : 1) Prendre une pièce, 2) Contrôle traçabilité, "
                "3) Contrôle face d'aspect ou contrôle face technique, "
                "4) Prise autre composant, 5) Assembler composant sur pièce, "
                "6) Contrôle assemblage, 7) Conditionnement."
            ),
    },
    "tampographie": {
        "label": "🖼️ Type 4 : Tampographie",
        "desc": "Procédé de tampographie avec pédale (5 étapes)",
        "has_control_choice": False,
        "steps": [
            "Prendre une pièce",
            "Mettre la pièce sur le posage",
            "Lancement cycle (Appuyer avec le pied sur la pédale)",
            "Contrôle Tampographie",
            "Conditionnement"
        ],
        "max_steps": 5,
        "prompt_addendum": (
            "Cette vidéo montre un procédé de TAMPOGRAPHIE. "
            "Le flux attendu est STRICTEMENT : 1) Prendre une pièce, 2) Mettre la pièce sur le posage, "
            "3) Lancement cycle (Appuyer avec le pied sur la pédale), 4) Contrôle Tampographie, "
            "5) Conditionnement."
        ),
    },
    "marquage_chaud": {
        "label": "🔥 Type 5 : Marquage à chaud",
        "desc": "Procédé de marquage à chaud avec commande bimanuelle (5 étapes)",
        "has_control_choice": False,
        "steps": [
            "Prendre une pièce",
            "Mettre la pièce sur le posage",
            "Lancement cycle (Appuyer avec les deux mains sur la bimanuelle)",
            "Contrôle Tampographie",
            "Conditionnement"
        ],
        "max_steps": 5,
        "prompt_addendum": (
            "Cette vidéo montre un procédé de MARQUAGE À CHAUD. "
            "Le flux attendu est STRICTEMENT : 1) Prendre une pièce, 2) Mettre la pièce sur le posage, "
            "3) Lancement cycle (Appuyer avec les deux mains sur la bimanuelle), "
            "4) Contrôle Tampographie, 5) Conditionnement."
        ),
    },
    "soudure_boutrollage": {
        "label": "⚡ Type 6 : Soudure ou Boutrollage",
        "desc": "Procédé de soudure/boutrollage bimanuel avec composant (7 étapes)",
        "has_control_choice": False,
        "steps": [
            "Prendre une pièce",
            "Positionnement sur posage",
            "Prise composant",
            "Positionnement dans logement",
            "Lancement de cycle (Appuyer avec les deux mains sur la bimanuelle)",
            "Contrôle assemblage",
            "Conditionnement"
        ],
        "max_steps": 7,
        "prompt_addendum": (
            "Cette vidéo montre un procédé de SOUDURE OU BOUTROLLAGE. "
            "Le flux attendu est STRICTEMENT : 1) Prendre une pièce, 2) Positionnement sur posage, "
            "3) Prise composant, 4) Positionnement dans logement, "
            "5) Lancement de cycle (Appuyer avec les deux mains sur la bimanuelle), "
            "6) Contrôle assemblage, 7) Conditionnement."
        ),
    },
    "retouche_finition": {
        "label": "⚡ Type 7 : Retouche & Finition",
        "desc": "Procédé de Finition ou Ébavurage manuelle (7 étapes)",
        "has_control_choice": True,
        "steps": [
            "Prendre une pièce",
            "Contrôle traçabilité et état de pièce",
            "Retouche de piece",
            "Contrôle face d'aspect ou contrôle face technique",
            "Conditionnement"
        ],
        "max_steps": 5,
            "prompt_addendum": (
            "Cette vidéo montre un procédé de SOUDURE OU BOUTROLLAGE. "
            "Le flux attendu est STRICTEMENT : 1) Prendre une pièce, 2) Contrôle traçabilité et état de pièce, "
            "3) Retouche de piece, 4) Contrôle face d'aspect ou contrôle face technique, "
            "5) Conditionnement."
        ),
    },
    "assemblage_avec_outil": {
        "label": "⚡ Type 8 : Assemblage manuelle avec outil",
        "desc": "Procédé d'assemblage manuelle à l'outil (5 étapes)",
        "has_control_choice": True,
        "steps": [
            "prise de la pièce",
            "prise des composants avec outil",
            "assemblage",
            "Contrôle visuel de la pièce",
            "Conditionnement",
        ],
        "max_steps": 5,
        "prompt_addendum": (
            "Cette vidéo montre un procédé d'assemblage manuel avec outil. "
            "L'opérateur utilise un outil à main pour assembler les éléments sur la pièce plastique. "
            "Le flux attendu est STRICTEMENT : 1) Prise de la pièce, "
            "2) prise des composants avec outil, 3) assemblage, "
            "4) Contrôle visuel de la pièce, 5) Conditionnement. "
            "Ignorer les équipements personnels de confort (ventilateur, bouteille) sur le poste."
        ),
    },
    "tampographie_sans_recuperation": {
        "label": "🖼️ Type 10 : Tampographie sans récupération",
        "desc": "Procédé de tampographie automatique sans dépose/évacuation manuelle (4 étapes)",
        "has_control_choice": True,
        "steps": [
            "Prendre une pièce",
            "Mettre la pièce sur le posage",
            "Lancement cycle",
            "Recul de sécurité",
        ],
        "max_steps": 4,
        "prompt_addendum": (
            "Cette vidéo montre un procédé de TAMPOGRAPHIE SANS RÉCUPÉRATION MANUELLE. "
            "L'opérateur dépose la pièce sur le posage, lance le cycle, puis s'éloigne pendant l'impression. "
            "Le flux attendu est STRICTEMENT : 1) Prendre une pièce, "
            "2) Mettre la pièce sur le posage, 3) Lancement cycle, "
            "4) Recul de sécurité."
        ),
    },
    "custom": {
        "label": "✏️ Personnalisé",
        "desc": "Définissez vous-même la liste exacte des étapes dans le champ texte.",
        "has_control_choice": False,
        "steps": [],
        "max_steps": None,
        "prompt_addendum": "",
    },
}


# ═══════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def get_workflow_config(workflow_type: str) -> Dict[str, Any]:
    """Récupère la configuration d'un workflow de manière sécurisée."""
    default_config = {
        "label": workflow_type.capitalize(),
        "desc": "",
        "has_control_choice": False,
        "steps": [],
        "max_steps": None,
        "prompt_addendum": "",
    }
    return WORKFLOW_TYPES.get(workflow_type, default_config)


def parse_custom_steps(custom_steps_text: str) -> List[str]:
    """Transforme le texte libre 'une étape par ligne' en liste propre de libellés."""
    if not custom_steps_text:
        return []

    steps = []
    for line in custom_steps_text.splitlines():
        line = line.strip()
        if not line:
            continue
        line = re.sub(r"^\s*(\d+[\.\)/]|[-•])\s*", "", line).strip()
        if line:
            steps.append(line[0].upper() + line[1:])

    return steps