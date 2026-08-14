# -*- coding: utf-8 -*-
"""
app_ui/main_window.py - Fenêtre principale de l'application (DescriptionApp)
"""

import os
import json
import threading
import platform
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import config
from excel_generator import generate_sos_excel
from .theme import (
    DARK_BG, DARK_CARD, DARK_BORDER, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ACCENT_BLUE, ACCENT_GREEN, ACCENT_RED, ACCENT_AMBER, FONT_FAMILY,
    FONT_H1, FONT_H2, FONT_CAPTION, FONT_BODY, SPACE_MD, SPACE_LG,
)
from .widgets import RoundedButton, RoundedCard, StatusPill, StyledScrolledText, ScrollableArea
from .dialog import ModernDialog
from .analysis import analyze_video
import re


def format_text_for_qt(text):
    if not text:
        return ""
    return re.sub(
        r'\*\*(.*?)\*\*',
        r'<span style="color: red; font-weight: bold;">\1</span>',
        text
    )


class DescriptionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PVL Operator Analyzer")
        self.geometry("1080x920")
        self.minsize(760, 600)
        self.configure(bg=DARK_BG)
        self.video_path = None
        self.report_path = None
        self.workflow_config = None
        self.last_report_path = None

        # Interrupt Event
        self.cancellation_event = threading.Event()

        self._build_ui()

    def _build_ui(self):
        # FOOTER CREDITS (Ancré en bas de la fenêtre, toujours visible et discret)
        lbl_footer = tk.Label(
            self,
            text="Developed by Anwar Brahem",
            font=(FONT_FAMILY, 8),
            fg=TEXT_MUTED,
            bg=DARK_BG,
            anchor="center"
        )
        lbl_footer.pack(side="bottom", fill="x", pady=(2, 6))

        scroll = ScrollableArea(self, bg=DARK_BG)
        scroll.pack(fill="both", expand=True)
        container = tk.Frame(scroll.body, bg=DARK_BG, padx=SPACE_LG, pady=SPACE_LG)
        container.pack(fill="both", expand=True)

        # HEADER
        header = tk.Frame(container, bg=DARK_BG)
        header.pack(fill="x", pady=(0, SPACE_LG))

        title_row = tk.Frame(header, bg=DARK_BG)
        title_row.pack(fill="x")
        tk.Label(title_row, text="SOS Generator", font=FONT_H1,
                 fg=TEXT_PRIMARY, bg=DARK_BG).pack(side="left")

        self.status_pill = StatusPill(title_row, text="En attente d'une vidéo", state="idle", width=250)
        self.status_pill.pack(side="right")

        tk.Label(header, text="Operation Analyzer - Génération de rapports industriels",
                 font=FONT_CAPTION, fg=TEXT_SECONDARY, bg=DARK_BG).pack(anchor="w", pady=(4, 0))

        # --- CARTE 1 : SELECTION VIDEO ---
        video_card = RoundedCard(container, title="1. VIDÉO À ANALYSER", accent=ACCENT_BLUE)
        video_card.pack(fill="x", pady=(0, SPACE_MD))
        vbox = video_card.content

        row1 = tk.Frame(vbox, bg=DARK_CARD)
        row1.pack(fill="x")
        self.btn_choose = RoundedButton(row1, text="Choisir une vidéo...", icon="📁",
                                         variant="ghost", width=220, height=40, command=self.choose_video)
        self.btn_choose.pack(side="left")

        self.lbl_path = tk.Label(row1, text="Aucune vidéo sélectionnée.",
                                  font=FONT_BODY, fg=TEXT_MUTED, bg=DARK_CARD)
        self.lbl_path.pack(side="left", padx=(SPACE_MD, 0))

        self.lbl_workflow = tk.Label(row1, text="", font=(FONT_FAMILY, 10, "bold"),
                                      fg=ACCENT_BLUE, bg=DARK_CARD)
        self.lbl_workflow.pack(side="right")

        # --- CARTE 2 : ANALYSE ---
        action_card = RoundedCard(container, title="2. ANALYSE", accent=ACCENT_AMBER)
        action_card.pack(fill="x", pady=(0, SPACE_MD))
        abox = action_card.content

        self.btn_analyze = RoundedButton(abox, text="Analyser la vidéo", icon="▶",
                                          variant="primary", width=220, height=44,
                                          command=self.start_analysis)
        self.btn_analyze.pack(side="left")
        self.btn_analyze.config_state("disabled")

        self.btn_stop = RoundedButton(abox, text="Arrêter l'analyse", icon="■",
                                       variant="ghost", width=200, height=44,
                                       command=self.stop_analysis)
        self.btn_stop.pack(side="left", padx=(SPACE_MD, 0))
        self.btn_stop.config_state("disabled")

        # --- CARTE 3 : SÉLECTION DU MODÈLE & ENTRAÎNEMENT ---
        train_card = RoundedCard(container, title="3. CHOIX DU MODÈLE IA & ENTRAÎNEMENT", accent=ACCENT_AMBER)
        train_card.pack(fill="x", pady=(0, SPACE_MD))
        tbox = train_card.content

        t_row = tk.Frame(tbox, bg=DARK_CARD)
        t_row.pack(fill="x")

        # Sélecteur de modèle Ollama
        tk.Label(t_row, text="Modèle Ollama :", font=FONT_BODY, fg=TEXT_PRIMARY, bg=DARK_CARD).pack(side="left", padx=(0, 6))
        
        current_model = getattr(config, "OLLAMA_MODEL", "gemma4:31b-cloud")
        self.combo_model = ttk.Combobox(
            t_row, 
            values=["gemma4:31b-cloud"], 
            state="readonly",
            width=18
        )
        self.combo_model.set(current_model)
        self.combo_model.pack(side="left", padx=(0, SPACE_MD))
        self.combo_model.bind("<<ComboboxSelected>>", self.on_model_selected)

        self.lbl_samples = tk.Label(t_row, text="Échantillons : 0", font=FONT_BODY, fg=TEXT_SECONDARY, bg=DARK_CARD)
        self.lbl_samples.pack(side="left", padx=(SPACE_MD, 0))

        # Bouton d'entraînement
        self.btn_train = RoundedButton(t_row, text="Entraîner le Modèle", icon="🏋️",
                                        variant="warning", width=180, height=36,
                                        command=self.start_training_thread)
        self.btn_train.pack(side="right")

        # Bouton de bascule vers le modèle LoRA entraîné
        is_custom = getattr(config, "USE_CUSTOM_LORA_MODEL", False)
        mode_str = "Mode : LoRA Local" if is_custom else "Mode : Ollama Standard"
        self.btn_toggle_model = RoundedButton(t_row, text=mode_str, icon="⚙️",
                                               variant="ghost", width=200, height=36,
                                               command=self.toggle_custom_model)
        self.btn_toggle_model.pack(side="right", padx=(0, SPACE_MD))

        self.update_sample_count()

        # --- CARTE 4 : RAPPORT D'ANALYSE ---
        output_card = RoundedCard(container, title="4. RAPPORT D'ANALYSE", accent=ACCENT_GREEN)
        output_card.pack(fill="both", expand=True, pady=(0, SPACE_MD))
        obox = output_card.content
        obox.pack_configure(fill="both", expand=True)

        self.text_output = StyledScrolledText(obox, height=18)
        self.text_output.pack(fill="both", expand=True)

        # --- CARTE 5 : EXPORT ---
        export_card = RoundedCard(container, title="5. EXPORT", accent=ACCENT_BLUE)
        export_card.pack(fill="x")
        ebox = export_card.content

        self.btn_save = RoundedButton(ebox, text="Enregistrer (.txt)", icon="💾",
                                       variant="ghost", width=190, height=40,
                                       command=self.save_description)
        self.btn_save.pack(side="left", padx=(0, SPACE_MD))
        self.btn_save.config_state("disabled")

        self.btn_open_json = RoundedButton(ebox, text="Ouvrir JSON", icon="📂",
                                            variant="ghost", width=170, height=40,
                                            command=self.open_json_report)
        self.btn_open_json.pack(side="left", padx=(0, SPACE_MD))
        self.btn_open_json.config_state("disabled")

        self.btn_generate_excel = RoundedButton(ebox, text="Générer Excel SOS", icon="📊",
                                                 variant="success", width=210, height=40,
                                                 command=self.start_excel_generation)
        self.btn_generate_excel.pack(side="right")
        self.btn_generate_excel.config_state("disabled")

    def on_model_selected(self, event=None):
        selected_model = self.combo_model.get()
        config.OLLAMA_MODEL = selected_model
        self._update_config_file_var("OLLAMA_MODEL", f'"{selected_model}"')
        self.status_pill.set_status(f"Modèle actif : {selected_model}", "success")

    def toggle_custom_model(self):
        """ Bascule entre le modèle Ollama standard et le modèle LoRA entraîné localement """
        current_state = getattr(config, "USE_CUSTOM_LORA_MODEL", False)
        new_state = not current_state
        config.USE_CUSTOM_LORA_MODEL = new_state

        if new_state:
            lora_dir = "my_sos_lora_weights"
            if not os.path.exists(lora_dir):
                messagebox.showwarning(
                    "Modèle Non Entraîné",
                    f"Aucun dossier '{lora_dir}' trouvé.\n"
                    "Veuillez d'abord lancer un entraînement avec le bouton 'Entraîner le Modèle'."
                )
                config.USE_CUSTOM_LORA_MODEL = False
                return

            self.btn_toggle_model.set_text("Mode : LoRA Local")
            self.status_pill.set_status("Mode : Modèle Local (LoRA)", "success")
        else:
            self.btn_toggle_model.set_text("Mode : Ollama Standard")
            self.status_pill.set_status(f"Mode : Ollama ({getattr(config, 'OLLAMA_MODEL', 'gemma4:31b-cloud')})", "idle")

        self._update_config_file_var("USE_CUSTOM_LORA_MODEL", str(config.USE_CUSTOM_LORA_MODEL))

    def _update_config_file_var(self, var_name: str, var_value: str):
        """ Met à jour une variable dans config/defaults.py ou config.py pour conserver l'état au redémarrage """
        try:
            target_files = [os.path.join("config", "defaults.py"), "config.py"]
            for config_path in target_files:
                if not os.path.exists(config_path):
                    continue
                with open(config_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                found = False
                with open(config_path, "w", encoding="utf-8") as f:
                    for line in lines:
                        if line.startswith(var_name):
                            f.write(f"{var_name} = {var_value}\n")
                            found = True
                        else:
                            f.write(line)
                    if not found:
                        f.write(f"\n{var_name} = {var_value}\n")
        except Exception as e:
            print(f"[CONFIG ERROR] Impossible de modifier la configuration : {e}")

    def update_sample_count(self):
        dataset_file = os.path.join("dataset_sos", "dataset.jsonl")
        count = 0
        if os.path.exists(dataset_file):
            with open(dataset_file, "r", encoding="utf-8") as f:
                count = sum(1 for line in f if line.strip())
        self.lbl_samples.config(text=f"Échantillons : {count}")

    def start_training_thread(self):
        dataset_file = os.path.join("dataset_sos", "dataset.jsonl")
        if not os.path.exists(dataset_file):
            messagebox.showwarning("Données insuffisantes", "Aucun échantillon collecté. Effectuez d'abord quelques analyses d'exemples.")
            return

        if not messagebox.askyesno("Lancer l'entraînement", "L'entraînement du modèle peut prendre plusieurs minutes. Souhaitez-vous continuer ?"):
            return

        self.btn_train.config_state("disabled")
        self.status_pill.set_status("Entraînement du modèle LoRA...", "warning")
        threading.Thread(target=self._run_training_process, daemon=True).start()

    def _run_training_process(self):
        try:
            import train_lora
            train_lora.main()
            self.after(0, self._on_training_success)
        except Exception as e:
            err_msg = str(e)
            self.after(0, lambda msg=err_msg: self._on_training_failure(msg))

    def _on_training_success(self):
        self.btn_train.config_state("normal")
        config.USE_CUSTOM_LORA_MODEL = True
        self._update_config_file_var("USE_CUSTOM_LORA_MODEL", "True")
        self.btn_toggle_model.set_text("Mode : LoRA Local")
        self.status_pill.set_status("Modèle entraîné et activé avec succès !", "success")
        messagebox.showinfo("Succès", "L'entraînement est terminé !\nLe modèle personnalisé a été activé automatiquement.")

    def _on_training_failure(self, error_msg):
        self.btn_train.config_state("normal")
        self.status_pill.set_status("Échec de l'entraînement.", "error")
        messagebox.showerror("Erreur d'entraînement", f"Une erreur s'est produite :\n{error_msg}")

    # ═══════════════════════════════════════════════════════════
    # ACTIONS D'ANALYSE & FICHIERS
    # ═══════════════════════════════════════════════════════════
    def choose_video(self):
        path = filedialog.askopenfilename(
            title="Sélectionner une vidéo",
            filetypes=[("Fichiers vidéo", "*.mp4 *.avi *.mov *.mkv")],
        )
        if path:
            self.video_path = path
            self.lbl_path.config(text=Path(path).name, fg=TEXT_PRIMARY)
            self.btn_analyze.config_state("normal")
            self.btn_stop.config_state("disabled")
            self.btn_save.config_state("disabled")
            self.btn_open_json.config_state("disabled")
            self.btn_generate_excel.config_state("disabled")
            self.text_output.delete("1.0", "end")
            self.workflow_config = None
            self.lbl_workflow.config(text="")
            self.status_pill.set_status("Vidéo chargée. Prêt à analyser.", "success")

    def start_analysis(self):
        dialog = ModernDialog(self)
        if dialog.result is None:
            self.status_pill.set_status("Analyse annulée.", "idle")
            return

        self.workflow_config = dialog.result
        wf_type = self.workflow_config["workflow_type"]
        wf_label = config.WORKFLOW_TYPES[wf_type]["label"]
        self.lbl_workflow.config(text=f"Workflow: {wf_label}")

        self.cancellation_event.clear()

        self.btn_analyze.config_state("disabled")
        self.btn_stop.config_state("normal")
        self.btn_choose.config_state("disabled")
        self.btn_save.config_state("disabled")
        self.btn_open_json.config_state("disabled")
        self.btn_generate_excel.config_state("disabled")
        self.text_output.delete("1.0", "end")
        self.status_pill.set_status("Analyse en cours...", "warning")
        threading.Thread(target=self.run_analysis, daemon=True).start()

    def stop_analysis(self):
        if messagebox.askyesno("Arrêter l'analyse", "Voulez-vous vraiment interrompre l'analyse ?"):
            self.cancellation_event.set()
            self.status_pill.set_status("Interruption en cours...", "warning")
            self.btn_stop.config_state("disabled")

    def run_analysis(self):
        try:
            result = analyze_video(
                self.video_path,
                progress_callback=self._report_status,
                workflow_type=self.workflow_config["workflow_type"],
                custom_steps=self.workflow_config.get("custom_steps"),
                expected_step_count=self.workflow_config.get("expected_step_count"),
                frame_interval=self.workflow_config.get("frame_interval"),
                window_size=self.workflow_config.get("window_size"),
                resize_factor=self.workflow_config.get("resize_factor"),
                cancellation_event=self.cancellation_event,
                control_type=self.workflow_config.get("control_type")
            )
            self.after(0, self._on_success, result)
        except Exception as e:
            import traceback
            error_detail = f"{str(e)}\n\n{traceback.format_exc()}"
            self.after(0, self._on_failure, error_detail)

    def _report_status(self, text):
        self.after(0, lambda: self.status_pill.set_status(text, "warning"))

    def _on_success(self, result):
        description, report_path = result if isinstance(result, tuple) else (result, None)

        if self.cancellation_event.is_set():
            self.status_pill.set_status("Analyse interrompue.", "error")
            self.text_output.insert("end", "\n[Analyse interrompue par l'utilisateur]")
        else:
            self.text_output.insert("end", description or "(Aucune description générée.)")
            self.status_pill.set_status("Terminé.", "success")
            if report_path:
                self.last_report_path = Path(report_path)
                self.btn_open_json.config_state("normal")
                self.btn_generate_excel.config_state("normal")
                self.btn_save.config_state("normal")

        self.btn_analyze.config_state("normal")
        self.btn_stop.config_state("disabled")
        self.btn_choose.config_state("normal")
        self.update_sample_count()

    def _on_failure(self, error_msg):
        messagebox.showerror("Erreur", error_msg)
        self.status_pill.set_status("Erreur pendant l'analyse.", "error")
        self.btn_analyze.config_state("normal")
        self.btn_stop.config_state("disabled")
        self.btn_choose.config_state("normal")
        self.btn_generate_excel.config_state("disabled")

    def save_description(self):
        content = self.text_output.get("1.0", "end").strip()
        if not content:
            return
        default_name = Path(self.video_path).stem + "_description.txt"
        save_path = filedialog.asksaveasfilename(
            initialfile=default_name,
            defaultextension=".txt",
            filetypes=[("Fichier texte", "*.txt")],
        )
        if save_path:
            Path(save_path).write_text(content, encoding="utf-8")
            messagebox.showinfo("Enregistré", f"Description enregistrée :\n{save_path}")

    def _open_file(self, filepath):
        system = platform.system()
        try:
            if system == "Windows":
                os.startfile(str(filepath))
            elif system == "Darwin":
                subprocess.run(["open", str(filepath)], check=True)
            else:
                subprocess.run(["xdg-open", str(filepath)], check=True)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier : {e}")

    def open_json_report(self):
        if self.last_report_path and self.last_report_path.exists():
            import webbrowser
            webbrowser.open(str(self.last_report_path.resolve()))
            return

        if self.video_path:
            video_stem = Path(self.video_path).stem
            outputs_dir = Path("outputs")
            if outputs_dir.exists():
                candidates = sorted(
                    [d for d in outputs_dir.iterdir() if d.is_dir() and video_stem in d.name],
                    key=lambda x: x.stat().st_mtime,
                    reverse=True
                )
                if candidates:
                    json_path = candidates[0] / "rapport_analyse.json"
                    if json_path.exists():
                        import webbrowser
                        webbrowser.open(str(json_path.resolve()))
                        return

        messagebox.showinfo("Info", "Rapport JSON non trouvé.")

    def start_excel_generation(self):
        if not self.last_report_path or not self.last_report_path.exists():
            messagebox.showerror("Erreur", "Aucun rapport trouvé. Analysez d'abord une vidéo.")
            return
        self.btn_generate_excel.config_state("disabled")
        self.status_pill.set_status("Génération du fichier Excel SOS...", "warning")
        threading.Thread(target=self.generate_excel, daemon=True).start()

    def generate_excel(self):
        try:
            output_path = generate_sos_excel(
                str(self.last_report_path),
                project_name=Path(self.video_path).stem
            )
            self.after(0, self._on_excel_success, output_path)
        except Exception as e:
            self.after(0, self._on_excel_failure, str(e))

    def _on_excel_success(self, output_path):
        self.status_pill.set_status("Fichier Excel SOS généré !", "success")
        self.btn_generate_excel.config_state("normal")
        if messagebox.askyesno("Succès", f"Fichier généré :\n{output_path}\n\nOuvrir ?"):
            self._open_file(output_path)

    def _on_excel_failure(self, error_msg):
        messagebox.showerror("Erreur Excel", f"Erreur :\n{error_msg}")
        self.status_pill.set_status("Erreur génération Excel.", "error")
        self.btn_generate_excel.config_state("normal")
