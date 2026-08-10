# -*- coding: utf-8 -*-
"""
config/risk_mapping.py - Mapping des risques pour "Raison du point clé"
(extrait de l'ancien config.py, aucune logique modifiee)
"""

# ── Risk mapping for auto-generated "Raison du point clé" ─────────
# Cles en minuscules pour matching partiel
RISK_MAPPINGS = {
    "assemblage": ["Mauvais montage", "Perte du temps"],
    "assemblage des deux composants": ["Mauvais montage", "Jeu fonctionnel", "Perte du temps"],
    "vissage": ["Mauvais montage", "Perte du temps"],
    "controle": ["Pièce à rebuter", "Perte du temps"],
    "controle composant": ["Composant défectueux", "Mauvais montage", "Perte du temps"],
    "controle assemblage": ["Assemblage non conforme", "Pièce à rebuter", "Perte du temps"],
    "stockage": ["Mélange références", "Réclamation client"],
    "prise": ["Perte du temps", "Pièce à terre"],
    "prise d'autre composant": ["Mauvais composant", "Perte du temps", "Mélange références"],
    "depose": ["Perte du temps", "Mauvais montage"],
    "manipulation": ["Perte du temps"],
    "attente": ["Perte du temps"],
    "depliage": ["Pli incorrect", "Protection insuffisante"],
    "alignement": ["Mauvais positionnement", "Defaut d'aspect"],
    "guidage": ["Mauvais alignement", "Bourrage"],
    "decoupe": ["Dimension incorrecte", "Chute de production"],
    "lissage": ["Pli ou bulle", "Defaut d'aspect"],
    "positionnement": ["Mauvais montage", "Perte du temps"],
    "prendre": ["Perte du temps", "Chute de piece"],
    "preparation": ["Perte du temps", "Materiau incorrect"],
    "orientation": ["Mauvais positionnement", "Perte du temps"],
    "conditionnement": ["Chute de piece", "Rayure", "Perte du temps"],
}
