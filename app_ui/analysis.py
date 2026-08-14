# -*- coding: utf-8 -*-
"""
app_ui/analysis.py - Wrapper haut niveau autour du pipeline test.run_pipeline
"""

import test
import config
from data_collector import save_training_sample


def analyze_video(video_path, progress_callback=None, workflow_type="auto",
                  custom_steps=None, expected_step_count=None, frame_interval=None,
                  window_size=None, resize_factor=None, cancellation_event=None,
                  control_type=None, **kwargs):
    
    if cancellation_event and cancellation_event.is_set():
        return "Analyse interrompue par l'utilisateur.", None
    
    if progress_callback:
        progress_callback("Démarrage de l'analyse...")

    if frame_interval is not None:
        config.DEFAULT_INTERVAL_S = frame_interval
    if window_size is not None:
        config.DEFAULT_WINDOW_SIZE = window_size
    if resize_factor is not None:
        config.DEFAULT_RESIZE_FACTOR = resize_factor

    report_path, chronological_logs = test.run_pipeline(
        video_file_path=video_path,
        progress_callback=progress_callback,
        workflow_type=workflow_type,
        custom_steps=custom_steps,
        expected_step_count=expected_step_count,
        cancellation_event=cancellation_event,
        control_type=control_type
    )

    if cancellation_event and cancellation_event.is_set():
        return "Analyse interrompue par l'utilisateur.", None

    if not chronological_logs:
        return "Aucune étape analysée ou analyse annulée.", None

    if progress_callback:
        progress_callback("Génération du rapport et archivage du dataset...")

    lines = []
    lines.append("=" * 70)
    lines.append("RAPPORT D'ANALYSE SOS - PVL Operator Analyzer")
    lines.append(f"Workflow utilisé : {workflow_type}")
    lines.append("=" * 70)
    lines.append("")

    for i, step in enumerate(chronological_logs, 1):
        lines.append(f"--- Étape {i} ---")
        lines.append(f"Action principale      : {step.get('action_principale', 'N/A')}")
        lines.append(f"Résumé de l'étape      : {step.get('etape_principale_resume', 'N/A')}")
        lines.append(f"Mouvement observé      : {step.get('mouvement_observe', 'N/A')}")
        lines.append(f"Outils / Fixations     : {step.get('outils_fixations', 'N/A')}")
        lines.append(f"Points clés (HOW)      : {step.get('points_cles', 'N/A')}")
        lines.append(f"Raison (WHY)           : {step.get('raison_point_cle', 'N/A')}")
        lines.append(f"Temps de cycle estimé  : {step.get('temps_cycle_estime', 'N/A')}")
        lines.append(f"CP/CS                  : {step.get('cp_cs', 'N/A')}")
        lines.append(f"Timestamp début        : {step.get('timestamp_debut', 'N/A')}")
        lines.append(f"Description complète   : {step.get('description_complete', 'N/A')}")
        
        image_path = step.get('frame_image_path')
        if image_path:
            lines.append(f"Image associée         : {image_path}")
        lines.append("")

        images_to_save = [image_path] if image_path else []
        save_training_sample(
            base64_images=images_to_save,
            final_json=step,
            workflow_type=workflow_type,
            step_label=step.get('etape_principale_resume', f"Etape {i}")
        )

    lines.append("=" * 70)
    lines.append(f"Total : {len(chronological_logs)} étapes analysées")
    lines.append(f"Workflow : {workflow_type}")
    lines.append(f"Rapport JSON sauvegardé : {report_path}")
    lines.append("=" * 70)

    return "\n".join(lines), report_path
