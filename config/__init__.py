# -*- coding: utf-8 -*-
"""
config/__init__.py - Point d'entree du package config.

Ce package remplace l'ancien config.py monolithique, decoupe en
plusieurs petits fichiers par theme (chemins, valeurs par defaut,
workflows, prompts, risques, theme GUI). Tout le contenu est
reexporte ici, donc partout ailleurs dans le projet,
`import config` puis `config.NOM_DE_LA_CONSTANTE` continue de
fonctionner exactement comme avant, sans aucun changement de logique.
"""

# ── Chemins et disposition Excel (config/paths.py) ────────────────
from .paths import (
    OUTPUT_DIR,
    make_session_dir,
    PAGE1_OP_START,
    PAGE1_OP_END,
    FIRST_REPEAT_HEADER_ROW,
    HEADER_BLOCK_LEN,
    OP_ROWS_PER_REPEAT_PAGE,
    PAGE_BLOCK_LEN,
    TEMPLATE_NAME,
    TEMPLATE_SHEET,
    START_ROW_OPERATIONS,
    COL_STEP_NUM,
    COL_CP_CS,
    COL_DESCRIPTION,
    COL_DESCRIPTION_END_COL,
    COL_PHOTO,
    COL_MAIN_STEP,
    COL_CYCLE_TIME,
    COL_KEY_POINTS,
    COL_REASON,
    COL_STEP_NUM_END,
    COL_CP_CS_END,
    COL_PHOTO_END,
    COL_MAIN_STEP_END,
    COL_KEY_POINTS_END,
    COL_REASON_END,
)

# ── Valeurs par defaut d'extraction (config/defaults.py) ───────────
from .defaults import (
    DEFAULT_INTERVAL_S,
    DEFAULT_WINDOW_SIZE,
    DEFAULT_FRAME_STEP,
    DEFAULT_SMART_DENSE_INTERVAL_S,
    DEFAULT_MOTION_THRESHOLD,
    DEFAULT_STATIC_SKIP_S,
    DEFAULT_RESIZE_FACTOR,
    DEFAULT_OLLAMA_TIMEOUT,
    DEFAULT_SKIP_SIMILAR,
    DEFAULT_SIMILARITY_THRESHOLD,
    OLLAMA_MODEL,
)

# ── Workflows (config/workflows.py) ────────────────────────────────
from .workflows import WORKFLOW_TYPES, parse_custom_steps

# ── Prompt Ollama (config/prompts.py) ──────────────────────────────
from .prompts import SOS_ANALYSIS_PROMPT

# ── Mapping des risques (config/risk_mapping.py) ───────────────────
from .risk_mapping import RISK_MAPPINGS

# ── Theme GUI (config/theme.py) ────────────────────────────────────
from .theme import (
    BG_COLOR,
    CARD_BG,
    CARD_BG_HOVER,
    FG_COLOR,
    FG_SECONDARY,
    ACCENT_COLOR,
    ACCENT_HOVER,
    SUCCESS_COLOR,
    SUCCESS_BG,
    WARNING_COLOR,
    WARNING_BG,
    ERROR_COLOR,
    ERROR_BG,
    INFO_COLOR,
    INFO_BG,
    BORDER_COLOR,
    BORDER_LIGHT,
    FONT_FAMILY,
    FONT_TITLE,
    FONT_SUBTITLE,
    FONT_BODY,
    FONT_SMALL,
    FONT_MONO,
)

# config/__init__.py

from .prompts import (
    PASS1_AGGREGATION_PROMPT,
    PASS2_FOR054_PROMPT,
    SOS_ANALYSIS_PROMPT,
)
