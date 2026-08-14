# -*- coding: utf-8 -*-
"""
config/defaults.py - Valeurs par défaut pour l'extraction video
"""

# ── Valeurs par défaut ─────────────────────────────────────────────
# Set to 1.0s interval to avoid extracting hundreds of redundant frames
DEFAULT_INTERVAL_S = 0.13
DEFAULT_WINDOW_SIZE = 2
DEFAULT_FRAME_STEP = 2

# ── Smart sampling ───────────────────────────────────────────────
DEFAULT_SMART_DENSE_INTERVAL_S = 1.0
DEFAULT_MOTION_THRESHOLD = 0.08
DEFAULT_STATIC_SKIP_S = 2.0
DEFAULT_RESIZE_FACTOR = 0.75
DEFAULT_OLLAMA_TIMEOUT = 500

# ── Skip similar frames ───────────────────────────────────────────
DEFAULT_SKIP_SIMILAR = True
DEFAULT_SIMILARITY_THRESHOLD = 0.88

# ── Modèle Ollama ────────────────────────────────────────────────
OLLAMA_MODEL = "gemma4:31b-cloud"# -*- coding: utf-8 -*-
"""
config/defaults.py - Valeurs par défaut pour l'extraction video
"""

# ── Valeurs par défaut ─────────────────────────────────────────────
# Set to 1.0s interval to avoid extracting hundreds of redundant frames
DEFAULT_INTERVAL_S = 0.13
DEFAULT_WINDOW_SIZE = 2
DEFAULT_FRAME_STEP = 2

# ── Smart sampling ───────────────────────────────────────────────
DEFAULT_SMART_DENSE_INTERVAL_S = 1.0
DEFAULT_MOTION_THRESHOLD = 0.08
DEFAULT_STATIC_SKIP_S = 2.0
DEFAULT_RESIZE_FACTOR = 0.75
DEFAULT_OLLAMA_TIMEOUT = 500

# ── Skip similar frames ───────────────────────────────────────────
DEFAULT_SKIP_SIMILAR = True
DEFAULT_SIMILARITY_THRESHOLD = 0.88

# ── Modèle Ollama ────────────────────────────────────────────────
OLLAMA_MODEL = "gemma4:31b-cloud"
