# -*- coding: utf-8 -*-
"""
test/pipeline.py - Orchestration complète avec agrégation des étapes, pipeline deux passes, 
détection de netteté et exportation Excel FOR-054 (avec Rich Text XlsxWriter)
"""

import json
import re
import time
import datetime
import threading
from pathlib import Path
import cv2

import xlsxwriter

import config
from .text_processing import sanitize_analysis_step
from .video_extraction import extract_frames_smart
from .ollama_client import analyze_sequence_two_pass


def _log(msg):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


MAX_IMAGES_PER_REQUEST = 4


def calculate_sharpness(image_path) -> float:
    """
    Calculates image sharpness using Variance of Laplacian.
    Higher variance indicates sharper, focused images with well-defined edges (less motion blur).
    """
    try:
        img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
        if img is None:
            return 0.0
        return float(cv2.Laplacian(img, cv2.CV_64F).var())
    except Exception:
        return 0.0


def select_clearest_frame(paths: list) -> tuple:
    """
    Selects the frame path with the highest sharpness score from a list of paths
    to eliminate motion blur and mid-action moving hands.
    Returns (best_path, best_score).
    """
    if not paths:
        return "", 0.0
    
    scored_paths = [(p, calculate_sharpness(p)) for p in paths]
    scored_paths.sort(key=lambda x: x[1], reverse=True)
    return scored_paths[0]


def generate_excel_report(chronological_logs: list, output_excel_path: str):
    """
    Builds the formatted Excel report according to standard FOR-054 using XlsxWriter.
    Highlights key points in RED BOLD inside the description cell.
    """
    workbook = xlsxwriter.Workbook(output_excel_path)
    worksheet = workbook.add_worksheet("Mode Operatoire")

    fmt_normal = workbook.add_format({'font_name': 'Calibri', 'font_size': 11, 'font_color': '#000000'})
    fmt_red_bold = workbook.add_format({'font_name': 'Calibri', 'font_size': 11, 'bold': True, 'font_color': '#FF0000'})
    
    fmt_header = workbook.add_format({
        'font_name': 'Calibri', 'font_size': 10, 'bold': True, 
        'bg_color': '#D9D9D9', 'border': 1, 'text_wrap': True, 
        'align': 'center', 'valign': 'vcenter'
    })
    
    fmt_cell = workbook.add_format({
        'font_name': 'Calibri', 'font_size': 11, 'valign': 'vcenter', 
        'text_wrap': True, 'border': 1
    })

    worksheet.set_column('A:A', 8)   # N° Etape
    worksheet.set_column('B:B', 8)   # CP/CS
    worksheet.set_column('C:C', 35)  # Description
    worksheet.set_column('D:D', 22)  # Photo
    worksheet.set_column('E:E', 25)  # Etape principale
    worksheet.set_column('F:F', 8)   # T/C
    worksheet.set_column('G:G', 28)  # Points cles
    worksheet.set_column('H:H', 32)  # Raison

    headers = [
        "N° Etape Principale", 
        "CP/CS", 
        "Description du mode opératoire:\navec détails écrit", 
        "Complément du mode opératoire:\navec photos si besoin", 
        "Étapes principales", 
        "T/C", 
        "Points clés (Comment ?)", 
        "Raison du point clé (Pourquoi ?)"
    ]

    worksheet.set_row(0, 35)
    for col_idx, h in enumerate(headers):
        worksheet.write(0, col_idx, h, fmt_header)

    stopwords = {"le", "la", "les", "un", "une", "des", "du", "de", "d", "sur", "dans", "avec", "en", "et", "ou", "a", "à", "pour", "par"}

    for idx, step in enumerate(chronological_logs, start=1):
        row = idx
        worksheet.set_row(row, 75)
        
        worksheet.write(row, 0, idx, fmt_cell)
        worksheet.write(row, 1, step.get("cp_cs", "Non"), fmt_cell)

        desc = str(step.get("description_complete", ""))
        pts = str(step.get("points_cles", ""))

        raw_segments = [s.strip() for s in re.split(r'[/,]', pts) if s.strip()]
        search_terms = []

        for seg in raw_segments:
            if seg.lower() in desc.lower():
                search_terms.append(seg)
            else:
                for w in seg.split():
                    clean_w = re.sub(r'[^\w]', '', w)
                    if len(clean_w) >= 3 and clean_w.lower() not in stopwords:
                        search_terms.append(clean_w)

        intervals = []
        if search_terms:
            for term in search_terms:
                pattern = r'\b' + re.escape(term) + r'\b'
                matches = list(re.finditer(pattern, desc, flags=re.IGNORECASE))
                if not matches:
                    matches = list(re.finditer(re.escape(term), desc, flags=re.IGNORECASE))
                for m in matches:
                    intervals.append((m.start(), m.end()))

        if intervals:
            intervals.sort(key=lambda x: x[0])
            merged = []
            for s, e in intervals:
                if not merged:
                    merged.append([s, e])
                else:
                    if s <= merged[-1][1]:
                        merged[-1][1] = max(merged[-1][1], e)
                    else:
                        merged.append([s, e])

            rich_tokens = []
            curr = 0
            for s, e in merged:
                if s > curr:
                    rich_tokens.extend([fmt_normal, desc[curr:s]])
                rich_tokens.extend([fmt_red_bold, desc[s:e]])
                curr = e
            if curr < len(desc):
                rich_tokens.extend([fmt_normal, desc[curr:]])

            try:
                worksheet.write_rich_string(row, 2, *rich_tokens, fmt_cell)
            except Exception:
                worksheet.write(row, 2, desc, fmt_cell)
        else:
            worksheet.write(row, 2, desc, fmt_cell)

        img_path = step.get("frame_image_path")
        worksheet.write(row, 3, "", fmt_cell)
        if img_path and Path(img_path).exists():
            try:
                worksheet.insert_image(
                    row, 3, img_path, 
                    {'x_scale': 0.22, 'y_scale': 0.22, 'x_offset': 5, 'y_offset': 5, 'object_position': 1}
                )
            except Exception:
                pass

        worksheet.write(row, 4, step.get("etape_principale_resume", ""), fmt_cell)
        worksheet.write(row, 5, step.get("temps_cycle_estime", ""), fmt_cell)
        worksheet.write(row, 6, pts, fmt_cell)
        worksheet.write(row, 7, step.get("raison_point_cle", ""), fmt_cell)

    workbook.close()


def _subsample_evenly_pair(frames, paths, max_count):
    n = len(frames)
    if n <= max_count or max_count <= 0:
        return frames, paths
    if max_count == 1:
        return [frames[n // 2]], [paths[n // 2]]

    indices = [round(i * (n - 1) / (max_count - 1)) for i in range(max_count)]
    seen = set()
    deduped_indices = []
    for idx in indices:
        if idx not in seen:
            seen.add(idx)
            deduped_indices.append(idx)

    return [frames[i] for i in deduped_indices], [paths[i] for i in deduped_indices]


def reconcile_step_consistency(data: dict, fallback_step_label: str = "") -> dict:
    title = str(data.get("etape_principale_resume", "")).strip()
    desc = str(data.get("description_complete", "")).strip()
    fallback = str(fallback_step_label).strip()

    # --- 1. RÈGLE : Recul / Sécurité ---
    recoil_keywords = ["reculer", "sécurité", "securite", "retirer", "mains hors", "dégager", "degager", "attente"]
    title_has_recoil = any(kw in title.lower() for kw in recoil_keywords)
    desc_has_recoil = any(kw in desc.lower() for kw in recoil_keywords)

    if title_has_recoil and not desc_has_recoil:
        data["action_principale"] = "Reculer"
        data["description_complete"] = "Reculer les mains et le buste hors de la zone de travail pendant le fonctionnement de la machine."
        data["points_cles"] = "Maintenir les mains hors de la zone de danger pendant le cycle"
        data["raison_point_cle"] = "Sécurité opérateur / Éviter tout risque d'écrasement ou de pincement"
    elif desc_has_recoil and not title_has_recoil:
        data["action_principale"] = "Reculer"
        data["etape_principale_resume"] = "Reculer pendant le cycle de la machine"

    # --- 2. RÈGLE : Retouche / Ébavurage / Finition ---
    retouche_keywords = ["retouche", "ébavurage", "ebavurage", "finition", "grattage", "bistouri", "cutter"]
    is_retouche_step = any(kw in fallback.lower() for kw in retouche_keywords) or any(kw in title.lower() for kw in retouche_keywords)

    if is_retouche_step:
        # Si le VLM a produit une simple "Prise" ou "Manipulation" au lieu d'une retouche
        if "prise" in title.lower() or data.get("action_principale") in ["Prendre", "Prise", "Manipuler", "Manipulation"]:
            data["etape_principale_resume"] = "Retouche de pièce"
            data["action_principale"] = "Retoucher"
            
            if "posage" in desc.lower() or "prendre" in desc.lower() or "bac" in desc.lower() or "saisie" in desc.lower():
                data["description_complete"] = "Retoucher avec l'outil de finition la pièce pour éliminer les bavures."
                data["points_cles"] = "outil de finition / éliminer les bavures"
                data["raison_point_cle"] = "Garantir la conformité géométrique et l'absence de bavures"

    if data.get("action_principale") in ["Erreur Format", "", None]:
        if title_has_recoil or desc_has_recoil:
            data["action_principale"] = "Reculer"
        elif is_retouche_step:
            data["action_principale"] = "Retoucher"
        else:
            data["action_principale"] = "Manipuler"

    return data


def ensure_clean_dict(data, fallback_step_label="Étape"):
    default_structure = {
        "action_principale": "Manipulation",
        "mouvement_observe": "",
        "outils_fixations": "Rien",
        "description_complete": "Effectuer l'opération.",
        "points_cles": "Suivre le mode opératoire.",
        "raison_point_cle": "Assurer la qualité.",
        "temps_cycle_estime": "2s",
        "cp_cs": "Non",
        "etape_principale_resume": fallback_step_label,
        "best_frame_index": 1
    }

    if isinstance(data, str):
        cleaned_str = data.strip()
        if cleaned_str.startswith("```"):
            cleaned_str = re.sub(r"^```(?:json)?\s*", "", cleaned_str, flags=re.IGNORECASE)
            cleaned_str = re.sub(r"\s*```$", "", cleaned_str)

        try:
            data = json.loads(cleaned_str)
        except json.JSONDecodeError:
            match = re.search(r"\{[\s\S]*?\}", cleaned_str)
            if match:
                try:
                    data = json.loads(match.group(0))
                except json.JSONDecodeError:
                    data = default_structure
                    data["description_complete"] = cleaned_str[:150]
            else:
                data = default_structure
                data["description_complete"] = cleaned_str[:150]

    if isinstance(data, dict):
        desc = str(data.get("description_complete", "")).strip()
        if desc.startswith("{") and desc.endswith("}"):
            try:
                nested_dict = json.loads(desc)
                if isinstance(nested_dict, dict):
                    data.update(nested_dict)
            except json.JSONDecodeError:
                pass

        for key, val in default_structure.items():
            if key not in data or data[key] is None or data[key] == "":
                data[key] = val

        if data.get("etape_principale_resume") in ["Erreur Format", "Erreur format", "Erreur"]:
            data["etape_principale_resume"] = fallback_step_label

        data = reconcile_step_consistency(data, fallback_step_label=fallback_step_label)
        data = sanitize_analysis_step(data)
        return data

    return default_structure


def run_pipeline(video_file_path: str, custom_project_name: str = None,
                 workflow_type="auto", custom_steps=None, expected_step_count=None,
                 progress_callback=None, cancellation_event: threading.Event = None):
    if not custom_project_name:
        custom_project_name = Path(video_file_path).stem

    session_dir = config.make_session_dir(video_file_path, project_name=custom_project_name)

    msg = f"Dossier de session opérationnel : {session_dir}"
    if progress_callback:
        progress_callback(msg)
    else:
        print(msg)

    if cancellation_event and cancellation_event.is_set():
        _log("Analyse interrompue par l'utilisateur.")
        if progress_callback:
            progress_callback("Analyse annulée.")
        return None, []

    wf = config.WORKFLOW_TYPES.get(workflow_type, config.WORKFLOW_TYPES.get("injection", {}))
    step_labels = []
    if workflow_type == "custom":
        step_labels = config.parse_custom_steps(custom_steps)
    elif wf.get("steps"):
        step_labels = wf["steps"]

    target_step_count = len(step_labels) if step_labels else (expected_step_count or 4)

    frames, frame_paths, calculated_interval_s = extract_frames_smart(
        video_file_path,
        session_dir,
        step_count=target_step_count,
        progress_callback=progress_callback
    )

    if cancellation_event and cancellation_event.is_set():
        _log("Analyse interrompue par l'utilisateur.")
        if progress_callback:
            progress_callback("Analyse annulée.")
        return None, []

    if not frames:
        if progress_callback:
            progress_callback("Aucune image extraite.")
        return None, []

    last_known_action = "Début du poste"
    chronological_logs = []
    n_steps = target_step_count
    total_frames = len(frames)
    frames_per_macro_step = max(1, total_frames // n_steps)

    for idx in range(n_steps):
        if cancellation_event and cancellation_event.is_set():
            _log("Analyse interrompue par l'utilisateur.")
            if progress_callback:
                progress_callback("Analyse annulée.")
            return None, []

        start = idx * frames_per_macro_step
        end = total_frames if idx == n_steps - 1 else (idx + 1) * frames_per_macro_step
        
        window_frames = frames[start:end] if end > start else [frames[-1]]
        window_paths = frame_paths[start:end] if end > start else [frame_paths[-1]]
        
        timestamp_approx = start * calculated_interval_s
        label = step_labels[idx] if step_labels and idx < len(step_labels) else f"Étape {idx + 1}"

        target_max_images = getattr(config, 'DEFAULT_WINDOW_SIZE', MAX_IMAGES_PER_REQUEST)
        sub_frames, sub_paths = _subsample_evenly_pair(window_frames, window_paths, target_max_images)

        if progress_callback:
            progress_callback(f"Analyse de l'étape consolidée {idx + 1}/{n_steps} : {label}...")

        try:
            raw_json_data = analyze_sequence_two_pass(
                images_base64=sub_frames,
                previous_action=last_known_action,
                workflow_context=f"Étape {idx + 1}/{n_steps} : {label}",
                forced_step_label=label
            )
        except Exception as e:
            _log(f"Erreur durant la passe d'analyse ({label}): {e}")
            raw_json_data = {"description_complete": str(e), "etape_principale_resume": label}

        if cancellation_event and cancellation_event.is_set():
            _log("Analyse interrompue par l'utilisateur.")
            if progress_callback:
                progress_callback("Analyse annulée.")
            return None, []

        json_data = ensure_clean_dict(raw_json_data, fallback_step_label=label)
        json_data["timestamp_debut"] = f"{timestamp_approx:.1f}s"
        
        if window_paths:
            best_sharp_path, sharpness_score = select_clearest_frame(window_paths)
            json_data["frame_image_path"] = str(best_sharp_path)
            _log(f"[Étape {idx + 1}] Photo nette sélectionnée (score: {sharpness_score:.1f}) -> {best_sharp_path}")

        chronological_logs.append(json_data)
        last_known_action = json_data.get("description_complete", label)

    if cancellation_event and cancellation_event.is_set():
        _log("Analyse interrompue par l'utilisateur.")
        if progress_callback:
            progress_callback("Analyse annulée.")
        return None, []

    if progress_callback:
        progress_callback("Génération des rapports (JSON + Excel)...")

    final_report_path = session_dir / "rapport_analyse.json"
    with open(final_report_path, "w", encoding="utf-8") as f:
        json.dump(chronological_logs, f, indent=4, ensure_ascii=False)

    final_excel_path = session_dir / "mode_operatoire.xlsx"
    try:
        generate_excel_report(chronological_logs, str(final_excel_path))
        _log(f"Rapport Excel généré : {final_excel_path}")
    except Exception as e:
        _log(f"Erreur lors de la génération de l'Excel : {e}")

    msg = f"Rapports sauvegardés dans : {session_dir}"
    if progress_callback:
        progress_callback(msg)
    else:
        print(msg)

    return final_report_path, chronological_logs