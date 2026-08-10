# -*- coding: utf-8 -*-
"""
config/paths.py - Chemins de sortie et disposition du template Excel
(extrait de l'ancien config.py, aucune logique modifiee)
"""

from datetime import datetime
from pathlib import Path

# ── Chemins ─────────────────────────────────────────────────────────
OUTPUT_DIR = Path("outputs")


def make_session_dir(video_path: str, project_name: str = None) -> Path:
    """Crée un dossier unique par session d'analyse, nommé par projet ou par défaut."""
    if project_name:
        session_name = project_name.strip().replace(" ", "_")
    else:
        video_name = Path(video_path).stem
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        session_name = f"{video_name}_{timestamp}"
    session_dir = OUTPUT_DIR / session_name
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / "frames").mkdir(exist_ok=True)
    return session_dir


PAGE1_OP_START = 17
PAGE1_OP_END = 32
FIRST_REPEAT_HEADER_ROW = 33
HEADER_BLOCK_LEN = 7      # rows 33-39 style block
OP_ROWS_PER_REPEAT_PAGE = 26
PAGE_BLOCK_LEN = 33

# ── Template Excel ────────────────────────────────────────────────
TEMPLATE_NAME = "FOR-054-Multi-J-SOS Analysis.xlsx"
TEMPLATE_SHEET = "Template"
START_ROW_OPERATIONS = 40

# Column mapping for FOR-054-Multi-J template (operations table)
# Row 39 = headers, Row 40+ = data
# Merged ranges per row:
#   A:C = N° Etape Principale
#   D:E = CP/CS
#   F:N = Description du mode opératoire
#   O:W = Complément du mode opératoire (photos)
#   X:AF = Étapes principales
#   AG = T/C (single column, width 13)
#   AH:AP = Points clés (Comment ?)
#   AQ:AY = Raison du point clé (Pourquoi ?)
COL_STEP_NUM = 1       # A (merged A:C)
COL_CP_CS = 4          # D (merged D:E)
COL_DESCRIPTION = 6    # F (merged F:N)
COL_DESCRIPTION_END_COL = 14  # N — dernière colonne de la plage fusionnée F:N
COL_PHOTO = 15         # O (merged O:W)
COL_MAIN_STEP = 24     # X (merged X:AF)
COL_CYCLE_TIME = 33    # AG (single column)
COL_KEY_POINTS = 34    # AH (merged AH:AP)
COL_REASON = 43        # AQ (merged AQ:AY)
COL_STEP_NUM_END = 3      # C
COL_CP_CS_END = 5         # E
COL_PHOTO_END = 23        # W
COL_MAIN_STEP_END = 32    # AF
COL_KEY_POINTS_END = 42   # AP
COL_REASON_END = 51       # AY
