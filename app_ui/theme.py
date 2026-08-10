# -*- coding: utf-8 -*-
"""
app_ui/theme.py - Design tokens du theme sombre "moderne" de l'interface.

Toutes les couleurs, espacements, rayons et tailles de police de l'app
sont centralises ici. Changer une valeur ici la propage partout
(boutons, cartes, dialogue) sans toucher au reste du code.
"""

# ═══════════════════════════════════════════════════════════════════
# COULEURS - fond / cartes / bordures
# ═══════════════════════════════════════════════════════════════════
DARK_BG = "#0B0F19"          # fond general de la fenetre
DARK_CARD = "#151B2B"        # fond des "cartes" (sections)
DARK_CARD_HOVER = "#1E2740"  # survol des cartes / boutons ghost
DARK_CARD_ALT = "#111726"    # variante legerement plus sombre (zones internes)
DARK_BORDER = "#2A3447"      # bordure standard
DARK_BORDER_ACTIVE = "#3B82F6"

# ═══════════════════════════════════════════════════════════════════
# TEXTE
# ═══════════════════════════════════════════════════════════════════
TEXT_PRIMARY = "#F0F4F8"
TEXT_SECONDARY = "#94A3B8"
TEXT_MUTED = "#64748B"

# ═══════════════════════════════════════════════════════════════════
# ACCENTS
# ═══════════════════════════════════════════════════════════════════
ACCENT_BLUE = "#3B82F6"
ACCENT_BLUE_HOVER = "#2563EB"
ACCENT_BLUE_GLOW = "#1D4ED8"
ACCENT_BLUE_SOFT = "#1E3A5F"   # fond pale pour badges/pills bleus

ACCENT_GREEN = "#10B981"
ACCENT_GREEN_HOVER = "#059669"
ACCENT_GREEN_SOFT = "#0F2E28"

ACCENT_RED = "#EF4444"
ACCENT_RED_HOVER = "#DC2626"
ACCENT_RED_SOFT = "#3A1B1E"

ACCENT_AMBER = "#F59E0B"
ACCENT_AMBER_HOVER = "#D97706"
ACCENT_AMBER_SOFT = "#3A2E10"

ACCENT_PURPLE = "#8B5CF6"

# ═══════════════════════════════════════════════════════════════════
# TYPOGRAPHIE
# ═══════════════════════════════════════════════════════════════════
FONT_FAMILY = "Segoe UI"
FONT_MONO = "Consolas"

FONT_H1 = (FONT_FAMILY, 22, "bold")
FONT_H2 = (FONT_FAMILY, 15, "bold")
FONT_H3 = (FONT_FAMILY, 11, "bold")
FONT_BODY = (FONT_FAMILY, 11)
FONT_BODY_BOLD = (FONT_FAMILY, 11, "bold")
FONT_SMALL = (FONT_FAMILY, 9)
FONT_SMALL_ITALIC = (FONT_FAMILY, 9, "italic")
FONT_CAPTION = (FONT_FAMILY, 10)

# ═══════════════════════════════════════════════════════════════════
# ESPACEMENT / RAYONS - pour garder une grille visuelle coherente
# ═══════════════════════════════════════════════════════════════════
SPACE_XS = 4
SPACE_SM = 8
SPACE_MD = 12
SPACE_LG = 18
SPACE_XL = 24

RADIUS_SM = 8
RADIUS_MD = 12
RADIUS_LG = 16
