# -*- coding: utf-8 -*-
"""
test/verb_utils.py - Normalisation et extraction de verbes francais
(extrait de l'ancien test.py, aucune logique modifiee)
"""

import re

VERB_NORMALIZATION = {
    # Prendre
    "prend": "prendre", "prends": "prendre", "prennent": "prendre",
    "prenait": "prendre", "prenais": "prendre", "pris": "prendre",
    # Déplacer
    "deplace": "deplacer", "deplaces": "deplacer", "deplacent": "deplacer",
    "deplacait": "deplacer", "deplacais": "deplacer",
    # Tourner
    "tourne": "tourner", "tournes": "tourner", "tournent": "tourner",
    "tournait": "tourner", "tournais": "tourner",
    # Contrôler
    "controle": "controler", "controles": "controler", "controlent": "controler",
    "controlait": "controler", "controlais": "controler",
    # Vérifier
    "verifie": "verifier", "verifies": "verifier", "verifient": "verifier",
    "verifiait": "verifier", "verifiais": "verifier",
    # Couper
    "coupe": "couper", "coupes": "couper", "coupent": "couper",
    "coupait": "couper", "coupais": "couper",
    # Lisser
    "lisse": "lisser", "lisses": "lisser", "lissent": "lisser",
    # Aligner
    "aligne": "aligner", "alignes": "aligner", "alignent": "aligner",
    # Orienter
    "oriente": "orienter", "orientes": "orienter", "orientent": "orienter",
    # Pousser
    "pousse": "pousser", "pousses": "pousser", "poussent": "pousser",
    # Tirer
    "tire": "tirer", "tires": "tirer", "tirent": "tirer",
    # Glisser
    "glisse": "glisser", "glisses": "glisser", "glissent": "glisser",
    # Introduire
    "introduis": "introduire", "introduit": "introduire", "introduisent": "introduire",
    # Inspecter
    "inspecte": "inspecter", "inspectes": "inspecter", "inspectent": "inspecter",
    # Assurer
    "assure": "assurer", "assures": "assurer", "assurent": "assurer",
    # Maintenir
    "maintiens": "maintenir", "maintient": "maintenir", "maintiennent": "maintenir",
    # Tenir
    "tiens": "tenir", "tient": "tenir", "tiennent": "tenir",
    # Mettre
    "mets": "mettre", "met": "mettre", "mettent": "mettre",
    # Attendre
    "attends": "attendre", "attend": "attendre", "attendent": "attendre",
    # Rester
    "reste": "rester", "restes": "rester", "restent": "rester",
    # Soulever
    "souleve": "soulever", "souleves": "soulever", "soulevent": "soulever",
    # Hisser
    "hisse": "hisser", "hisses": "hisser", "hissent": "hisser",
    # Pliage
    "plie": "plier", "plies": "plier", "plient": "plier",
    # Replier
    "replie": "replier", "replies": "replier", "replient": "replier",
    # Courber
    "courbe": "courber", "courbes": "courber", "courbent": "courber",
    # Envelopper
    "enveloppe": "envelopper", "enveloppes": "envelopper", "enveloppent": "envelopper",
    # Canaliser
    "canalise": "canaliser", "canalises": "canaliser", "canalisent": "canaliser",
    # Piloter
    "pilote": "piloter", "pilotes": "piloter", "pilotent": "piloter",
    # Mener
    "mene": "mener", "menes": "mener", "menent": "mener",
    # Calibrer
    "calibre": "calibrer", "calibres": "calibrer", "calibrent": "calibrer",
    # Niveler
    "nivele": "niveler", "niveles": "niveler", "nivelent": "niveler",
    # Centrer
    "centre": "centrer", "centres": "centrer", "centrent": "centrer",
    # Régler
    "regle": "regler", "regles": "regler", "reglent": "regler",
    # Diviser
    "divise": "diviser", "divises": "diviser", "divisent": "diviser",
    # Séparer
    "separe": "separer", "separes": "separer", "separent": "separer",
    # Fendre
    "fends": "fendre", "fend": "fendre", "fendent": "fendre",
    # Installer
    "installe": "installer", "installes": "installer", "installent": "installer",
    # Coller
    "colle": "coller", "colles": "coller", "collent": "coller",
    # Écraser
    "ecrase": "ecraser", "ecrases": "ecraser", "ecrasent": "ecraser",
    # Passer
    "passe": "passer", "passes": "passer", "passent": "passer",
    # Aplatir
    "aplatis": "aplatir", "aplatit": "aplatir", "aplatissent": "aplatir",
    # Remonter
    "remonte": "remonter", "remontes": "remonter", "remontent": "remonter",
    # Monter
    "monte": "monter", "montes": "monter", "montent": "monter",
    # Inverser
    "inverse": "inverser", "inverses": "inverser", "inversent": "inverser",
    # Renverser
    "renverse": "renverser", "renverses": "renverser", "renversent": "renverser",
    # Marquer
    "marque": "marquer", "marques": "marquer", "marquent": "marquer",
    # Confirmer
    "confirme": "confirmer", "confirmes": "confirmer", "confirment": "confirmer",
    # Ajouter (déjà dans common_verbs mais pas normalisé)
    "ajoute": "ajouter", "ajoutes": "ajouter", "ajoutent": "ajouter",
    # Enfiler
    "enfile": "enfiler", "enfiles": "enfiler", "enfilent": "enfiler",
    # Insérer
    "insere": "inserer", "inseres": "inserer", "inserent": "inserer",
    # Garder
    "garde": "garder", "gardes": "garder", "gardent": "garder",
    # Supporter
    "supporte": "supporter", "supportes": "supporter", "supportent": "supporter",
    # Retenir
    "retiens": "retenir", "retient": "retenir", "retiennent": "retenir",
    # Fixer
    "fixe": "fixer", "fixes": "fixer", "fixent": "fixer",
    # Transporter
    "transporte": "transporter", "transportes": "transporter", "transportent": "transporter",
    # Bouger
    "bouge": "bouger", "bouges": "bouger", "bougent": "bouger",
    # Guider
    "guide": "guider", "guides": "guider", "guident": "guider",
    # Diriger
    "dirige": "diriger", "diriges": "diriger", "dirigent": "diriger",
    # Appuyer
    "appuie": "appuyer", "appuies": "appuyer", "appuient": "appuyer",
    # Frotter
    "frotte": "frotter", "frottes": "frotter", "frottent": "frotter",
    # Agripper
    "agrippe": "agripper", "agrippes": "agripper", "agrippent": "agripper",
    # Attraper
    "attrape": "attraper", "attrapes": "attraper", "attrapent": "attraper",
    # Ramasser
    "ramasse": "ramasser", "ramasses": "ramasser", "ramassent": "ramasser",
    # Emporter
    "empoi": "emporter", "emporte": "emporter", "emportes": "emporter", "emportent": "emporter",
    # Reprendre
    "reprend": "reprendre", "reprends": "reprendre", "reprennent": "reprendre",
    # Assembler
    "assemble": "assembler", "assembles": "assembler", "assemblent": "assembler",
    # Conditionner
    "conditionne": "conditionner", "conditionnes": "conditionner", "conditionnent": "conditionner",
    # Stocker
    "stocke": "stocker", "stockes": "stocker", "stockent": "stocker",
}


def normalize_verb(verb):
    """Normalise un verbe conjugué vers sa forme de base pour le matching anti-répétition."""
    verb = verb.lower().strip()
    return VERB_NORMALIZATION.get(verb, verb)


BASE_VERBS = {
    "prendre", "attraper", "ramasser", "agripper", "empoigner",
    "couper", "trancher", "sectionner", "diviser", "separer", "fendre",
    "deposer", "placer", "installer", "ajouter", "coller",
    "lisser", "aplatir", "ecraser", "frotter", "passer", "aplanir",
    "tirer", "hisser", "soulever", "remonter", "monter",
    "tourner", "pivoter", "retourner", "inverser", "renverser",
    "attendre", "rester", "patienter", "marquer",
    "verifier", "inspecter", "confirmer", "controler", "assurer",
    "mettre", "introduire", "enfiler", "glisser", "inserer",
    "tenir", "maintenir", "garder", "supporter", "retenir", "fixer",
    "deplacer", "transferer", "transporter", "shift", "bouger",
    "plier", "replier", "courber", "envelopper",
    "guider", "diriger", "orienter", "canaliser", "piloter", "mener",
    "aligner", "ajuster", "calibrer", "niveler", "centrer", "regler",
    "assembler", "conditionner", "stocker", "emporter", "reprendre",
    "pousser", "appuyer",
}


def extract_verbs_from_text(text):
    """Extrait les verbes à l'infinitif ou conjugués du début de texte et les normalise."""
    if not text:
        return []

    words = text.strip().lower().split()

    found_verbs = []
    for word in words[:15]:  # Check first 15 words (augmenté pour plus de couverture)
        clean_word = re.sub(r'[^a-zàâäéèêëïîôùûü]', '', word)
        normalized = normalize_verb(clean_word)
        if normalized in BASE_VERBS and normalized not in found_verbs:
            found_verbs.append(normalized)

    return found_verbs
