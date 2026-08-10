# -*- coding: utf-8 -*-
"""
test/video_extraction.py - Extraction d'images depuis la vidéo avec sous-échantillonnage temporel adapté
"""

import base64
import shutil
from pathlib import Path

import cv2

import config


def encode_image_to_base64(image_bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")


def calculate_optimal_interval(duration_s: float, step_count: int = 5, frames_per_step: int = 4) -> float:
    """
    Calcule dynamiquement l'intervalle d'extraction (en secondes) pour répartir 
    l'échantillonnage sur toute la durée de la vidéo.
    """
    if duration_s <= 0:
        return getattr(config, 'DEFAULT_INTERVAL_S', 0.8)

    # Viser un nombre total d'images proportionnel au nombre d'étapes imposées
    target_total_frames = max(12, step_count * frames_per_step)
    optimal_interval = duration_s / target_total_frames

    # Borner entre 0.4s (~2.5 fps) et 1.5s (~0.6 fps) pour garantir une couverture temporelle complète
    return max(0.40, min(1.50, round(optimal_interval, 2)))


def extract_frames_smart(video_path: str, session_dir: Path, step_count: int = 5, progress_callback=None):
    if progress_callback:
        progress_callback("Extraction des images en cours...")
    else:
        print(f"--- Extraction des images depuis : {video_path} ---")

    frames_dir = session_dir / "frames"
    if frames_dir.exists():
        try:
            shutil.rmtree(frames_dir)
        except Exception as e:
            print(f"Attention: Impossible de supprimer {frames_dir}: {e}")
            
    frames_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Impossible d'ouvrir la vidéo : {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    if fps == 0 or fps is None:
        cap.release()
        raise ValueError(f"Impossible de lire le FPS de la vidéo : {video_path}")
    
    duration_s = total_frames_count / fps if total_frames_count > 0 else 0

    # Intervalle dynamique pour couvrir toute la durée vidéo
    interval_s = calculate_optimal_interval(duration_s, step_count=step_count)
    frame_interval = max(1, int(fps * interval_s))

    print(f"[video_extraction] Durée vidéo : {duration_s:.1f}s | Étapes visées : {step_count} | Intervalle calculé : {interval_s}s (chaque {frame_interval} frames)")

    extracted_frames = []
    frame_paths = []
    frame_count = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            if config.DEFAULT_RESIZE_FACTOR != 1.0:
                width = int(frame.shape[1] * config.DEFAULT_RESIZE_FACTOR)
                height = int(frame.shape[0] * config.DEFAULT_RESIZE_FACTOR)
                frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)

            frame_filename = frames_dir / f"frame_{saved_count:04d}.jpg"
            cv2.imwrite(str(frame_filename), frame)

            _, buffer = cv2.imencode('.jpg', frame)
            base64_string = encode_image_to_base64(buffer)

            extracted_frames.append(base64_string)
            frame_paths.append(str(frame_filename))
            saved_count += 1

            if saved_count % 5 == 0 and progress_callback:
                progress_callback(f"Extraction des images... ({saved_count} images extraites)")

        frame_count += 1

    cap.release()

    msg = f"Extraction terminée. {saved_count} images prêtes."
    if progress_callback:
        progress_callback(msg)
    else:
        print(msg)

    return extracted_frames, frame_paths, interval_s