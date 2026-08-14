# -*- coding: utf-8 -*-
"""
app_ui/step_builder.py - Palette d'actions rapides dynamiques (Ajouter, Éditer, Supprimer, Réinitialiser)
"""

import tkinter as tk
from tkinter import simpledialog, messagebox
import re
from .theme import (
    DARK_CARD, DARK_CARD_ALT, DARK_BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY, ACCENT_BLUE,
    FONT_SMALL, FONT_BODY_BOLD
)

DEFAULT_COMMON_ACTIONS = [
    # Prise & Positionnement
    "Prendre une pièce",
    "Prise d'un composant",
    "Prise des corps avec outil",
    "Mise en place sur posage",
    "Positionnement dans logement",

    # Assemblage
    "Assembler composant sur pièce",
    "Assemblage des corps avec outil",

    # Presse & Actionnement
    "Translation du posage",
    "Actionnement du levier",

    # Contrôle
    "Contrôle visuel",
    "Contrôle traçabilité",
    "Contrôle assemblage",
    "Contrôle Tampographie",
    "Contrôle dimensionnel",

    # Finition
    "Retouche de pièce",

    # Lancement & Sécurité
    "Lancement cycle (Pédale)",
    "Lancement cycle (Bimanuelle)",
    "Recul de sécurité",

    # Evacuation & Conditionnement
    "Évacuation pièce",
    "Conditionnement",
    "Nettoyage par air",
    "Nettoyage zone tampographie",
]


class StepBuilderFrame(tk.Frame):
    """
    Palette de boutons dynamiques permettant d'ajouter, éditer, supprimer
    et réinitialiser les actions rapides pour le mode personnalisé.
    """
    def __init__(self, master, text_widget, **kwargs):
        super().__init__(master, bg=DARK_CARD, highlightthickness=1,
                         highlightbackground=DARK_BORDER, bd=0, **kwargs)
        self.text_widget = text_widget
        self.actions_list = list(DEFAULT_COMMON_ACTIONS)
        self._build_ui()

    def _build_ui(self):
        # Effacer le contenu existant si reconstruction
        for widget in self.winfo_children():
            widget.destroy()

        # Header / Title Bar
        header = tk.Frame(self, bg=DARK_CARD)
        header.pack(fill="x", padx=10, pady=(8, 4))
        
        bar = tk.Frame(header, bg=ACCENT_BLUE, width=3)
        bar.pack(side="left", fill="y", padx=(0, 6))
        
        tk.Label(
            header, 
            text="🛠️ Palette d'actions rapides", 
            font=FONT_BODY_BOLD, 
            fg=ACCENT_BLUE, 
            bg=DARK_CARD
        ).pack(side="left")

        # Top Control Bar (Palette Operations: Add & Reset)
        palette_ops_bar = tk.Frame(self, bg=DARK_CARD)
        palette_ops_bar.pack(fill="x", padx=10, pady=(0, 4))

        btn_add = tk.Button(
            palette_ops_bar,
            text="➕ Ajouter une action",
            font=FONT_SMALL,
            fg=TEXT_PRIMARY,
            bg=DARK_CARD_ALT,
            activebackground=ACCENT_BLUE,
            activeforeground=TEXT_PRIMARY,
            relief="flat",
            cursor="hand2",
            padx=5,
            pady=2,
            command=self.add_custom_action
        )
        btn_add.pack(side="left", padx=(0, 4))

        btn_reset = tk.Button(
            palette_ops_bar,
            text="🔄 Réinitialiser la liste",
            font=FONT_SMALL,
            fg=TEXT_SECONDARY,
            bg=DARK_CARD_ALT,
            relief="flat",
            cursor="hand2",
            padx=5,
            pady=2,
            command=self.reset_to_default
        )
        btn_reset.pack(side="left")

        # Scrollable / Grid Frame for Action Buttons
        self.grid_frame = tk.Frame(self, bg=DARK_CARD)
        self.grid_frame.pack(fill="x", padx=8, pady=4)

        self._render_action_buttons()

        # Bottom Control Bar (Text Area Operations: Renumber & Clear)
        btn_bar = tk.Frame(self, bg=DARK_CARD)
        btn_bar.pack(fill="x", padx=10, pady=(4, 8))

        btn_renumber = tk.Button(
            btn_bar,
            text="🔢 Ré-numéroter texte",
            font=FONT_SMALL,
            fg=TEXT_SECONDARY,
            bg=DARK_CARD_ALT,
            relief="flat",
            cursor="hand2",
            padx=6,
            pady=2,
            command=self.renumber_steps
        )
        btn_renumber.pack(side="left")

        btn_clear = tk.Button(
            btn_bar,
            text="🗑️ Effacer tout le texte",
            font=FONT_SMALL,
            fg=TEXT_SECONDARY,
            bg=DARK_CARD_ALT,
            relief="flat",
            cursor="hand2",
            padx=6,
            pady=2,
            command=self.clear_all
        )
        btn_clear.pack(side="right")

    def _render_action_buttons(self):
        """Rendu visuel dynamique des boutons d'action."""
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        cols = 2
        for idx, action in enumerate(self.actions_list):
            r = idx // cols
            c = idx % cols

            btn_container = tk.Frame(self.grid_frame, bg=DARK_CARD_ALT, highlightthickness=1,
                                     highlightbackground=DARK_BORDER)
            btn_container.grid(row=r, column=c, padx=2, pady=2, sticky="ew")

            # Bouton principal pour insérer l'action
            btn_action = tk.Button(
                btn_container,
                text=f"+ {action}",
                font=FONT_SMALL,
                fg=TEXT_PRIMARY,
                bg=DARK_CARD_ALT,
                activebackground=ACCENT_BLUE,
                activeforeground=TEXT_PRIMARY,
                bd=0,
                relief="flat",
                cursor="hand2",
                anchor="w",
                padx=4,
                pady=2,
                command=lambda act=action: self.add_step(act)
            )
            btn_action.pack(side="left", fill="x", expand=True)

            # Bouton Éditer (✏️)
            btn_edit = tk.Label(
                btn_container,
                text="✏️",
                font=FONT_SMALL,
                fg=TEXT_SECONDARY,
                bg=DARK_CARD_ALT,
                cursor="hand2",
                padx=2
            )
            btn_edit.pack(side="right")
            btn_edit.bind("<Button-1>", lambda e, idx_act=idx: self.edit_action(idx_act))

            # Bouton Supprimer (❌)
            btn_del = tk.Label(
                btn_container,
                text="❌",
                font=FONT_SMALL,
                fg=TEXT_SECONDARY,
                bg=DARK_CARD_ALT,
                cursor="hand2",
                padx=2
            )
            btn_del.pack(side="right")
            btn_del.bind("<Button-1>", lambda e, idx_act=idx: self.delete_action(idx_act))

            self.grid_frame.columnconfigure(c, weight=1)

    # --- Palette Operations ---

    def add_custom_action(self):
        """Ajoute une nouvelle action personnalisée à la liste."""
        new_action = simpledialog.askstring("Nouvelle Action", "Nom de la nouvelle action :", parent=self)
        if new_action and new_action.strip():
            cleaned = new_action.strip()
            if cleaned not in self.actions_list:
                self.actions_list.append(cleaned)
                self._render_action_buttons()

    def edit_action(self, index: int):
        """Édite l'intitulé d'une action de la palette."""
        current_val = self.actions_list[index]
        updated_val = simpledialog.askstring("Modifier l'action", "Nouveau nom de l'action :",
                                             initialvalue=current_val, parent=self)
        if updated_val and updated_val.strip():
            self.actions_list[index] = updated_val.strip()
            self._render_action_buttons()

    def delete_action(self, index: int):
        """Supprime une action de la palette après confirmation."""
        action_name = self.actions_list[index]
        if messagebox.askyesno("Confirmation", f"Supprimer '{action_name}' de la palette ?", parent=self):
            del self.actions_list[index]
            self._render_action_buttons()

    def reset_to_default(self):
        """Réinitialise la palette d'actions avec la liste COMMON_ACTIONS par défaut."""
        if messagebox.askyesno("Réinitialiser", "Restaurer la liste d'actions par défaut ?", parent=self):
            self.actions_list = list(DEFAULT_COMMON_ACTIONS)
            self._render_action_buttons()

    # --- Text Area Operations ---

    def add_step(self, action_text: str):
        """Ajoute l'étape sélectionnée avec numérotation séquentielle dans la zone de texte."""
        current_content = self.text_widget.get("1.0", tk.END).strip()
        lines = [line for line in current_content.splitlines() if line.strip()]
        
        next_num = len(lines) + 1

        if current_content:
            self.text_widget.insert(tk.END, f"\n{next_num}/ {action_text}")
        else:
            self.text_widget.insert(tk.END, f"{next_num}/ {action_text}")

    def renumber_steps(self):
        """Ré-indexe proprement les lignes du zone de texte en 1/, 2/, 3/..."""
        raw_text = self.text_widget.get("1.0", tk.END).strip()
        if not raw_text:
            return

        lines = raw_text.splitlines()
        renumbered = []
        count = 1

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
            clean_text = re.sub(r"^\s*(\d+[\.\)/]|[-•])\s*", "", line_str).strip()
            if clean_text:
                renumbered.append(f"{count}/ {clean_text}")
                count += 1

        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", "\n".join(renumbered))

    def clear_all(self):
        """Efface l'intégralité de la zone de texte."""
        self.text_widget.delete("1.0", tk.END)
