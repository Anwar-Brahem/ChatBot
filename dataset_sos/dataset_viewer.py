# -*- coding: utf-8 -*-
"""
dataset_viewer.py - Inspector, Cleaner & Editor (Same Folder Edition)
Place this script directly inside the folder containing dataset.jsonl.
"""

import os
import json
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# Base directory is the directory containing this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_FILE = os.path.join(BASE_DIR, "dataset.jsonl")

# Theme Palette
DARK_BG = "#121212"
DARK_CARD = "#1E1E1E"
DARK_BORDER = "#2C2C2C"
TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "#A0A0A0"
ACCENT_BLUE = "#3B82F6"
ACCENT_RED = "#EF4444"
ACCENT_GREEN = "#10B981"
ACCENT_AMBER = "#F59E0B"


class DatasetViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dataset Inspector & Editor - Local Folder")
        self.geometry("1100x750")
        self.minsize(900, 650)
        self.configure(bg=DARK_BG)

        self.records = []
        self.current_index = 0
        self.is_editing = False

        self._build_ui()
        self.load_dataset()

    def _build_ui(self):
        # Top Header
        header = tk.Frame(self, bg=DARK_BG, padx=20, pady=15)
        header.pack(fill="x")

        self.lbl_counter = tk.Label(
            header, text="Échantillon : 0 / 0", font=("Segoe UI", 14, "bold"),
            fg=TEXT_PRIMARY, bg=DARK_BG
        )
        self.lbl_counter.pack(side="left")

        self.lbl_workflow = tk.Label(
            header, text="Workflow: N/A", font=("Segoe UI", 11, "bold"),
            fg=ACCENT_BLUE, bg=DARK_BG
        )
        self.lbl_workflow.pack(side="right")

        # Main Side-by-Side Content Area
        content = tk.Frame(self, bg=DARK_BG, padx=20, pady=10)
        content.pack(fill="both", expand=True)

        # Left Column: Image Preview
        self.img_frame = tk.Frame(content, bg=DARK_CARD, highlightbackground=DARK_BORDER, highlightthickness=1)
        self.img_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.lbl_image = tk.Label(self.img_frame, text="Aucune Image", bg=DARK_CARD, fg=TEXT_SECONDARY)
        self.lbl_image.pack(fill="both", expand=True)

        # Right Column: Ground Truth Details & Form Fields
        self.details_frame = tk.Frame(content, bg=DARK_CARD, highlightbackground=DARK_BORDER, highlightthickness=1, padx=15, pady=15)
        self.details_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # Form Scrollable Canvas Container
        canvas = tk.Canvas(self.details_frame, bg=DARK_CARD, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.details_frame, orient="vertical", command=canvas.yview)
        self.form_container = tk.Frame(canvas, bg=DARK_CARD)

        self.form_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.form_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Input Form Elements
        self.entries = {}
        fields = [
            ("etape_principale_resume", "Étape Résumé :", "entry"),
            ("action_principale", "Action Principale :", "entry"),
            ("mouvement_observe", "Mouvement Observé :", "entry"),
            ("outils_fixations", "Outils / Fixations :", "entry"),
            ("temps_cycle_estime", "Temps Estimé :", "entry"),
            ("cp_cs", "CP / CS (Oui/Non) :", "entry"),
            ("description_complete", "Description Complète :", "text"),
            ("points_cles", "Points Clés (HOW) :", "text"),
            ("raison_point_cle", "Raison (WHY) :", "text"),
        ]

        for key, label_text, field_type in fields:
            lbl = tk.Label(self.form_container, text=label_text, font=("Segoe UI", 10, "bold"), fg=TEXT_SECONDARY, bg=DARK_CARD, anchor="w")
            lbl.pack(fill="x", pady=(8, 2))

            if field_type == "entry":
                ent = tk.Entry(self.form_container, font=("Segoe UI", 10), bg="#252525", fg=TEXT_PRIMARY, insertbackground="white", relief="flat")
                ent.pack(fill="x", ipady=4)
                self.entries[key] = ent
            else:
                txt = tk.Text(self.form_container, font=("Segoe UI", 10), bg="#252525", fg=TEXT_PRIMARY, insertbackground="white", relief="flat", height=3, wrap="word")
                txt.pack(fill="x")
                self.entries[key] = txt

        # Bottom Bar: Navigation & Action Controls
        bottom_bar = tk.Frame(self, bg=DARK_BG, padx=20, pady=15)
        bottom_bar.pack(fill="x")

        self.btn_prev = tk.Button(
            bottom_bar, text="◀ Précédent", font=("Segoe UI", 10, "bold"),
            bg=DARK_BORDER, fg=TEXT_PRIMARY, activebackground="#3A3A3A", activeforeground=TEXT_PRIMARY,
            relief="flat", padx=12, pady=8, command=self.show_prev
        )
        self.btn_prev.pack(side="left")

        self.btn_delete = tk.Button(
            bottom_bar, text="🗑️ Supprimer", font=("Segoe UI", 10, "bold"),
            bg=ACCENT_RED, fg=TEXT_PRIMARY, activebackground="#B91C1C", activeforeground=TEXT_PRIMARY,
            relief="flat", padx=12, pady=8, command=self.delete_current_sample
        )
        self.btn_delete.pack(side="left", padx=10)

        self.btn_edit = tk.Button(
            bottom_bar, text="✏️ Modifier", font=("Segoe UI", 10, "bold"),
            bg=ACCENT_AMBER, fg=TEXT_PRIMARY, activebackground="#D97706", activeforeground=TEXT_PRIMARY,
            relief="flat", padx=12, pady=8, command=self.toggle_edit
        )
        self.btn_edit.pack(side="left")

        self.btn_save = tk.Button(
            bottom_bar, text="💾 Enregistrer", font=("Segoe UI", 10, "bold"),
            bg=ACCENT_GREEN, fg=TEXT_PRIMARY, activebackground="#059669", activeforeground=TEXT_PRIMARY,
            relief="flat", padx=12, pady=8, command=self.save_modifications
        )
        self.btn_save.pack(side="left", padx=10)

        self.btn_next = tk.Button(
            bottom_bar, text="Suivant ▶", font=("Segoe UI", 10, "bold"),
            bg=ACCENT_BLUE, fg=TEXT_PRIMARY, activebackground="#2563EB", activeforeground=TEXT_PRIMARY,
            relief="flat", padx=12, pady=8, command=self.show_next
        )
        self.btn_next.pack(side="right")

        self.set_fields_state("disabled")

    def _resolve_image_path(self, raw_path):
        if not raw_path:
            return None
        if os.path.exists(raw_path):
            return raw_path
        rel_path = os.path.join(BASE_DIR, raw_path)
        if os.path.exists(rel_path):
            return rel_path
        filename = os.path.basename(raw_path)
        fallback_path = os.path.join(BASE_DIR, "images", filename)
        if os.path.exists(fallback_path):
            return fallback_path
        return None

    def load_dataset(self):
        self.records = []
        if os.path.exists(DATASET_FILE):
            with open(DATASET_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        try:
                            self.records.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue

        if self.records:
            self.current_index = 0
            self.display_current()
        else:
            self.show_empty_state()

    def set_fields_state(self, state):
        for widget in self.entries.values():
            if isinstance(widget, tk.Entry):
                widget.config(state=state, bg="#252525" if state == "normal" else "#1E1E1E")
            elif isinstance(widget, tk.Text):
                widget.config(state=state, bg="#252525" if state == "normal" else "#1E1E1E")

    def display_current(self):
        if not self.records or self.current_index >= len(self.records):
            self.show_empty_state()
            return

        self.is_editing = False
        self.set_fields_state("disabled")
        self.btn_save.config(state="disabled")

        record = self.records[self.current_index]
        gt = record.get("ground_truth", {})

        self.lbl_counter.config(text=f"Échantillon : {self.current_index + 1} / {len(self.records)}")
        self.lbl_workflow.config(text=f"Workflow: {record.get('workflow_type', 'auto')}")

        # Image Handling
        images = record.get("images", [])
        raw_img_path = images[0] if images else None
        resolved_img_path = self._resolve_image_path(raw_img_path)

        if resolved_img_path:
            try:
                img = Image.open(resolved_img_path)
                img.thumbnail((480, 480), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.lbl_image.config(image=photo, text="")
                self.lbl_image.image = photo
            except Exception as e:
                self.lbl_image.config(image="", text=f"Erreur d'affichage image\n{e}", fg=ACCENT_RED)
        else:
            self.lbl_image.config(image="", text=f"Image introuvable :\n{raw_img_path}", fg=TEXT_SECONDARY)

        # Populate Form Fields
        for key, widget in self.entries.items():
            val = str(gt.get(key, "N/A"))
            if isinstance(widget, tk.Entry):
                widget.config(state="normal")
                widget.delete(0, "end")
                widget.insert(0, val)
                widget.config(state="disabled")
            elif isinstance(widget, tk.Text):
                widget.config(state="normal")
                widget.delete("1.0", "end")
                widget.insert("1.0", val)
                widget.config(state="disabled")

        self.btn_prev.config(state="normal" if self.current_index > 0 else "disabled")
        self.btn_next.config(state="normal" if self.current_index < len(self.records) - 1 else "disabled")
        self.btn_delete.config(state="normal")
        self.btn_edit.config(state="normal", text="✏️ Modifier")

    def toggle_edit(self):
        if not self.records:
            return
        self.is_editing = not self.is_editing
        if self.is_editing:
            self.set_fields_state("normal")
            self.btn_save.config(state="normal")
            self.btn_edit.config(text="❌ Annuler")
        else:
            self.display_current()

    def save_modifications(self):
        if not self.records or not self.is_editing:
            return

        gt = self.records[self.current_index].setdefault("ground_truth", {})

        for key, widget in self.entries.items():
            if isinstance(widget, tk.Entry):
                gt[key] = widget.get().strip()
            elif isinstance(widget, tk.Text):
                gt[key] = widget.get("1.0", "end-1c").strip()

        # Save back to file
        try:
            with open(DATASET_FILE, "w", encoding="utf-8") as f:
                for rec in self.records:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            messagebox.showinfo("Succès", "L'échantillon a été modifié avec succès.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de mettre à jour dataset.jsonl : {e}")
            return

        self.is_editing = False
        self.display_current()

    def show_empty_state(self):
        self.lbl_counter.config(text="Échantillon : 0 / 0")
        self.lbl_workflow.config(text="")
        self.lbl_image.config(image="", text="Le dataset est vide.", fg=TEXT_SECONDARY)
        self.set_fields_state("disabled")
        self.btn_prev.config(state="disabled")
        self.btn_next.config(state="disabled")
        self.btn_delete.config(state="disabled")
        self.btn_edit.config(state="disabled")
        self.btn_save.config(state="disabled")

    def show_prev(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.display_current()

    def show_next(self):
        if self.current_index < len(self.records) - 1:
            self.current_index += 1
            self.display_current()

    def delete_current_sample(self):
        if not self.records or self.current_index >= len(self.records):
            return

        if not messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer cet échantillon ?"):
            return

        target_record = self.records.pop(self.current_index)

        for raw_img_path in target_record.get("images", []):
            resolved = self._resolve_image_path(raw_img_path)
            if resolved and os.path.exists(resolved):
                try:
                    os.remove(resolved)
                except Exception as e:
                    print(f"[VIEWER] Erreur suppression image {resolved}: {e}")

        try:
            with open(DATASET_FILE, "w", encoding="utf-8") as f:
                for rec in self.records:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de mettre à jour dataset.jsonl : {e}")
            return

        if self.current_index >= len(self.records) and self.current_index > 0:
            self.current_index -= 1

        self.display_current()


if __name__ == "__main__":
    app = DatasetViewer()
    app.mainloop()
