# -*- coding: utf-8 -*-
"""
app_ui/__init__.py - Point d'entree du package app_ui.

Regroupe l'interface graphique (auparavant tout dans app.py) :
theme.py (couleurs), widgets.py (composants tkinter reutilisables),
dialog.py (fenetre des parametres), analysis.py (wrapper pipeline),
main_window.py (fenetre principale DescriptionApp).
"""

from .main_window import DescriptionApp
from .analysis import analyze_video

__all__ = ["DescriptionApp"]