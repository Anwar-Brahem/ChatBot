# -*- coding: utf-8 -*-
"""
app_ui/step_builder.py - Palette d'actions rapides dynamiques (Ajouter, Éditer, Supprimer, Réinitialiser)
"""

import os
import sys
import re
import importlib
from pathlib import Path
import tkinter as tk
from tkinter import simpledialog, messagebox
from .theme import (
    DARK_BG, DARK_CARD, DARK_CARD_HOVER, DARK_CARD_ALT, DARK_BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ACCENT_BLUE, ACCENT_BLUE_HOVER, ACCENT_GREEN, ACCENT_RED,
    FONT_FAMILY, FONT_H2, FONT_H3, FONT_BODY, FONT_BODY_BOLD,
    FONT_SMALL, FONT_CAPTION, RADIUS_SM, SPACE_SM, SPACE_MD, SPACE_LG
)
from .widgets import RoundedButton, StyledEntry

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


def _update_prompts_file(step_name: str, step_pattern: str) -> bool:
    """Ajoute la nouvelle règle/patron dans config/prompts.py sous la section 2."""
    try:
        current_dir = Path(__file__).resolve().parent
        project_root = current_dir.parent
        prompts_file = project_root / "config" / "prompts.py"

        if not prompts_file.exists():
            return False

        content = prompts_file.read_text(encoding="utf-8")

        # Vérifier si l'étape existe déjà dans prompts.py
        if f'"{step_name}"' in content:
            return True

        # Trouver la séparation vers la section 3
        sec3_match = re.search(r"(\n*═{40,}\n3\.\s*RÈGLE D'OR DE GÉNÉRATION DU TITRE)", content)
        if not sec3_match:
            sec3_match = re.search(r"(\n*3\.\s*RÈGLE D'OR)", content)

        if not sec3_match:
            return False

        sec3_start = sec3_match.start()
        sec2_text = content[:sec3_start]

        # Extraire les numéros existants dans la section 2
        numbers = [int(n) for n in re.findall(r"\n\s*(\d+)\.\s+\"", sec2_text)]
        next_num = max(numbers) + 1 if numbers else 23

        new_entry = f'\n{next_num}. "{step_name}" :\n   "{step_pattern}"\n'

        before = content[:sec3_start].rstrip()
        after = content[sec3_start:].lstrip("\r\n")

        updated_content = f"{before}\n{new_entry}\n{after}"
        prompts_file.write_text(updated_content, encoding="utf-8")

        # Mettre à jour en mémoire pour la session en cours
        try:
            import config.prompts
            importlib.reload(config.prompts)
            import config
            config.PASS2_FOR054_PROMPT = config.prompts.PASS2_FOR054_PROMPT
            config.SOS_ANALYSIS_PROMPT = config.prompts.SOS_ANALYSIS_PROMPT
            if "test.ollama_client" in sys.modules:
                import test.ollama_client
                test.ollama_client.PASS2_FOR054_PROMPT = config.prompts.PASS2_FOR054_PROMPT
        except Exception as e:
            print(f"[StepBuilder] Avertissement rechargement runtime config.prompts: {e}")

        return True
    except Exception as e:
        print(f"[StepBuilder] Erreur écriture prompts.py : {e}")
        return False


def _update_step_builder_file(step_name: str) -> bool:
    """Ajoute l'action dans DEFAULT_COMMON_ACTIONS du fichier step_builder.py."""
    try:
        current_file = Path(__file__).resolve()
        content = current_file.read_text(encoding="utf-8")

        if f'"{step_name}"' in content:
            return True

        match = re.search(r"(DEFAULT_COMMON_ACTIONS\s*=\s*\[[\s\S]*?)(\n\])", content)
        if match:
            prefix = match.group(1).rstrip()
            new_item = f'\n    "{step_name}",'
            updated_content = content[:match.start()] + prefix + new_item + "\n]" + content[match.end():]
            current_file.write_text(updated_content, encoding="utf-8")
            return True
        return False
    except Exception as e:
        print(f"[StepBuilder] Erreur écriture step_builder.py : {e}")
        return False


class AddActionDialog(tk.Toplevel):
    """Dialogue modal moderne pour ajouter une action et son patron strict."""
    def __init__(self, parent):
        toplevel = parent.winfo_toplevel()
        super().__init__(toplevel)
        self.title("Ajouter une action")
        self.geometry("560x430")
        self.minsize(500, 390)
        self.configure(bg=DARK_BG)
        self.transient(toplevel)
        self.resizable(False, False)

        self.result = None  # (step_name, step_pattern)

        self._build_ui()
        self.center_window(toplevel)

        self.lift()
        self.focus_force()
        self.grab_set()
        self.entry_name.focus_set()
        self.wait_window(self)

    def center_window(self, toplevel):
        self.update_idletasks()
        w, h = 560, 430
        toplevel.update_idletasks()
        rx = toplevel.winfo_rootx()
        ry = toplevel.winfo_rooty()
        rw = toplevel.winfo_width()
        rh = toplevel.winfo_height()
        x = rx + max(0, (rw - w) // 2)
        y = ry + max(0, (rh - h) // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        container = tk.Frame(self, bg=DARK_BG, padx=20, pady=20)
        container.pack(fill="both", expand=True)

        # Title
        tk.Label(
            container,
            text="➕ Ajouter une nouvelle action",
            font=FONT_H2,
            fg=TEXT_PRIMARY,
            bg=DARK_BG
        ).pack(anchor="w", pady=(0, 4))

        tk.Label(
            container,
            text="Cette action sera ajoutée à la palette et injectée dans prompts.py.",
            font=FONT_CAPTION,
            fg=TEXT_SECONDARY,
            bg=DARK_BG
        ).pack(anchor="w", pady=(0, 14))

        # Field 1: Step Name
        tk.Label(
            container,
            text="Nom de l'étape (ex: Vissage du capot, Soudure ultrason) :",
            font=FONT_BODY_BOLD,
            fg=TEXT_PRIMARY,
            bg=DARK_BG
        ).pack(anchor="w", pady=(0, 4))

        self.entry_name = StyledEntry(container)
        self.entry_name.pack(fill="x", pady=(0, 12), ipady=4)

        # Field 2: Pattern / Format
        tk.Label(
            container,
            text="Patron / Structure de description (pour prompts.py) :",
            font=FONT_BODY_BOLD,
            fg=TEXT_PRIMARY,
            bg=DARK_BG
        ).pack(anchor="w", pady=(0, 4))

        self.entry_pattern = StyledEntry(container)
        self.entry_pattern.pack(fill="x", pady=(0, 8), ipady=4)

        # Syntax hint box
        hint_frame = tk.Frame(container, bg=DARK_CARD, highlightthickness=1,
                              highlightbackground=DARK_BORDER, padx=10, pady=8)
        hint_frame.pack(fill="x", pady=(0, 16))

        tk.Label(
            hint_frame,
            text="💡 Format standard FOR-054 :",
            font=FONT_SMALL,
            fg=ACCENT_BLUE,
            bg=DARK_CARD,
            anchor="w"
        ).pack(fill="x")

        tk.Label(
            hint_frame,
            text="[Verbe infinitif] + [Mains / Outil] + [Pièce / Composant] + [Lieu / Complément]\n"
                 "Ex: Visser avec [la visseuse] les 4 vis sur le boîtier.",
            font=FONT_SMALL,
            fg=TEXT_SECONDARY,
            bg=DARK_CARD,
            justify="left",
            anchor="w"
        ).pack(fill="x", pady=(2, 0))

        # Buttons bar
        btn_box = tk.Frame(container, bg=DARK_BG)
        btn_box.pack(fill="x", side="bottom")

        btn_cancel = RoundedButton(
            btn_box,
            text="Annuler",
            variant="ghost",
            width=120,
            height=36,
            command=self._on_cancel
        )
        btn_cancel.pack(side="right", padx=(8, 0))

        btn_confirm = RoundedButton(
            btn_box,
            text="Ajouter l'action",
            variant="primary",
            width=150,
            height=36,
            command=self._on_confirm
        )
        btn_confirm.pack(side="right")

        self.bind("<Return>", lambda e: self._on_confirm())
        self.bind("<Escape>", lambda e: self._on_cancel())

    def _on_confirm(self):
        name = self.entry_name.get().strip()
        pattern = self.entry_pattern.get().strip()

        if not name:
            messagebox.showwarning("Champs requis", "Veuillez renseigner le nom de l'étape.", parent=self)
            self.entry_name.focus_set()
            return

        if not pattern:
            # Patron par défaut si non renseigné
            pattern = f"{name} avec [la main droite / les deux mains] la pièce."

        self.result = (name, pattern)
        self.destroy()

    def _on_cancel(self):
        self.result = None
        self.destroy()


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
        """Ouvre un dialogue pour saisir le nom et le patron strict, puis met à jour l'UI et prompts.py."""
        dialog = AddActionDialog(self)
        if dialog.result:
            step_name, step_pattern = dialog.result

            # Ajouter à la liste en mémoire si pas déjà présent
            if step_name not in self.actions_list:
                self.actions_list.append(step_name)
            if step_name not in DEFAULT_COMMON_ACTIONS:
                DEFAULT_COMMON_ACTIONS.append(step_name)

            # Mettre à jour la palette UI
            self._render_action_buttons()

            # Mettre à jour prompts.py et step_builder.py
            prompts_ok = _update_prompts_file(step_name, step_pattern)
            builder_ok = _update_step_builder_file(step_name)

            if prompts_ok:
                messagebox.showinfo(
                    "Action ajoutée",
                    f"L'action '{step_name}' a été ajoutée avec succès :\n\n"
                    f"• À la palette d'actions rapides\n"
                    f"• Dans config/prompts.py (Section 2 - Patrons stricts)",
                    parent=self
                )
            else:
                messagebox.showwarning(
                    "Avertissement",
                    f"L'action '{step_name}' a été ajoutée à la palette mais n'a pas pu être écrite dans config/prompts.py.",
                    parent=self
                )

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
