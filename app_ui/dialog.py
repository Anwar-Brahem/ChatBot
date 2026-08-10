# -*- coding: utf-8 -*-
"""
app_ui/dialog.py - Dynamic Workflow Configuration Dialog (Tkinter)
"""

import tkinter as tk
import config
from .theme import (
    DARK_BG, DARK_CARD, DARK_CARD_ALT, DARK_BORDER, TEXT_PRIMARY, TEXT_SECONDARY,
    TEXT_MUTED, ACCENT_BLUE, ACCENT_GREEN, FONT_H1, FONT_H3, FONT_BODY,
    FONT_BODY_BOLD, FONT_CAPTION, SPACE_SM, SPACE_MD, SPACE_LG, SPACE_XL,
)
from .widgets import (
    RoundedButton, Section, ScrollableArea, StyledSpinbox,
    OptionRow, OptionGroup, strip_emoji,
)
from .step_builder import StepBuilderFrame


class ModernDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Configuration de l'Analyse")
        self.geometry("840x940")
        self.minsize(640, 700)
        self.resizable(True, True)
        self.configure(bg=DARK_BG)
        self.transient(parent)

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

        self.result = None
        self._user_action = None
        self._option_group = OptionGroup(on_change=self._on_workflow_change)
        self._cond_option_group = OptionGroup()

        # Variables dynamiques pour les sous-options
        self.var_control_type = tk.StringVar(value="face_aspect")
        self.checkbox_vars = {}

        self._build_ui()
        self.center_window(parent)

        self.grab_set()
        self.wait_window(self)

    def center_window(self, parent):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        px, py = parent.winfo_x(), parent.winfo_y()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ═══════════════════════════════════════════════════════════
    # UI BUILD
    # ═══════════════════════════════════════════════════════════
    def _build_ui(self):
        # --- HEADER fixe ---
        header = tk.Frame(self, bg=DARK_BG, padx=SPACE_XL, pady=SPACE_XL)
        header.pack(fill="x")
        tk.Label(header, text="Configuration du Workflow", font=FONT_H1,
                 fg=TEXT_PRIMARY, bg=DARK_BG).pack(anchor="w")
        tk.Label(header, text="Choisissez le procédé, paramétrez les contrôles de qualité et l'échantillonnage.",
                 font=FONT_CAPTION, fg=TEXT_SECONDARY, bg=DARK_BG).pack(anchor="w", pady=(6, 0))

        # --- ZONE SCROLLABLE ---
        scroll = ScrollableArea(self, bg=DARK_BG)
        scroll.pack(fill="both", expand=True, padx=SPACE_XL, pady=(0, SPACE_MD))
        content = scroll.body

        # --- SECTION 1 : TYPE DE WORKFLOW ---
        wf_section = Section(content, title="Type de workflow", accent=ACCENT_BLUE)
        wf_section.pack(fill="x", pady=(0, SPACE_LG))
        wf_box = wf_section.content

        workflows = getattr(config, 'WORKFLOW_TYPES', {})
        rows_container = tk.Frame(wf_box, bg=DARK_CARD)
        rows_container.pack(fill="x")

        for key, info in workflows.items():
            label_text = strip_emoji(info.get('label', key.capitalize()))
            steps_list = info.get('steps', [])
            subtitle = f"{len(steps_list)} étapes" if steps_list else ("Saisie libre" if key == "custom" else "Auto")

            row = OptionRow(rows_container, key=key, label=label_text,
                             subtitle=subtitle, accent=ACCENT_BLUE)
            row.pack(fill="x", pady=(0, SPACE_SM))
            self._option_group.add(row)

        # --- Sub-options: Choix du type de contrôle ---
        self.sub_control_frame = tk.Frame(wf_box, bg=DARK_CARD_ALT, padx=SPACE_MD, pady=SPACE_MD,
                                          highlightthickness=1, highlightbackground=DARK_BORDER)
        
        tk.Label(self.sub_control_frame, text="Type de contrôle de surface :", font=FONT_BODY_BOLD,
                 fg=TEXT_PRIMARY, bg=DARK_CARD_ALT).pack(anchor="w", pady=(0, SPACE_SM))
        
        rb_aspect = tk.Radiobutton(
            self.sub_control_frame, text="Contrôle Face d'Aspect", variable=self.var_control_type,
            value="face_aspect", bg=DARK_CARD_ALT, fg=TEXT_PRIMARY, selectcolor=DARK_BG,
            activebackground=DARK_CARD_ALT, activeforeground=TEXT_PRIMARY, font=FONT_BODY
        )
        rb_aspect.pack(anchor="w")

        rb_tech = tk.Radiobutton(
            self.sub_control_frame, text="Contrôle Face Technique", variable=self.var_control_type,
            value="face_technique", bg=DARK_CARD_ALT, fg=TEXT_PRIMARY, selectcolor=DARK_BG,
            activebackground=DARK_CARD_ALT, activeforeground=TEXT_PRIMARY, font=FONT_BODY
        )
        rb_tech.pack(anchor="w", pady=(2, 0))

        # --- Sub-options: Checkboxes Défauts ---
        self.defects_frame = tk.Frame(wf_box, bg=DARK_CARD_ALT, padx=SPACE_MD, pady=SPACE_MD,
                                      highlightthickness=1, highlightbackground=DARK_BORDER)
        
        tk.Label(self.defects_frame, text="Points clés de contrôle (Raison / Défauts à vérifier) :",
                 font=FONT_BODY_BOLD, fg=TEXT_PRIMARY, bg=DARK_CARD_ALT).pack(anchor="w", pady=(0, SPACE_SM))

        defects_list = getattr(config, 'DEFAULT_DEFECT_OPTIONS', [
            "Pas de traces", "Point noir (si pièce blanche)", "Givrage", "Manque", "Cassé", "Déformation"
        ])

        for defect in defects_list:
            var = tk.BooleanVar(value=True)
            self.checkbox_vars[defect] = var
            cb = tk.Checkbutton(
                self.defects_frame, text=defect, variable=var, bg=DARK_CARD_ALT, fg=TEXT_PRIMARY,
                selectcolor=DARK_BG, activebackground=DARK_CARD_ALT, activeforeground=TEXT_PRIMARY,
                font=FONT_BODY, anchor="w"
            )
            cb.pack(fill="x", anchor="w", pady=2)

        # --- Details Card ---
        self.detail_section = tk.Frame(wf_box, bg=DARK_CARD_ALT, highlightthickness=1,
                                        highlightbackground=DARK_BORDER)
        self.detail_section.pack(fill="x", pady=(SPACE_MD, 0))
        detail_inner = tk.Frame(self.detail_section, bg=DARK_CARD_ALT, padx=SPACE_MD, pady=SPACE_MD)
        detail_inner.pack(fill="both", expand=True)

        self.lbl_card_title = tk.Label(detail_inner, text="", font=FONT_H3,
                                        fg=ACCENT_BLUE, bg=DARK_CARD_ALT, anchor="w")
        self.lbl_card_title.pack(fill="x")

        self.lbl_card_desc = tk.Label(detail_inner, text="", font=FONT_CAPTION,
                                       fg=TEXT_SECONDARY, bg=DARK_CARD_ALT, justify="left")
        self.lbl_card_desc.pack(fill="x", pady=(SPACE_SM, 4))

        self.lbl_card_meta = tk.Label(detail_inner, text="", font=FONT_CAPTION,
                                       fg=TEXT_MUTED, bg=DARK_CARD_ALT, anchor="w", justify="left")
        self.lbl_card_meta.pack(fill="x")

        # --- Custom Mode UI Components ---
        self.custom_label = tk.Label(wf_box, text="Étapes personnalisées (une par ligne) :",
                                      font=FONT_CAPTION, fg=TEXT_SECONDARY, bg=DARK_CARD)
        
        self.custom_text = tk.Text(wf_box, height=5, font=FONT_BODY, bg=DARK_BG, fg=TEXT_PRIMARY,
                                    insertbackground=TEXT_PRIMARY, bd=0, relief="flat",
                                    highlightthickness=1, highlightbackground=DARK_BORDER,
                                    highlightcolor=ACCENT_BLUE, padx=12, pady=10)
        self.custom_text.insert("1.0", "1/ Prendre une pièce\n2/ Assembler composant\n3/ Contrôle final")

        # Integrated Step Builder Frame (Palette d'actions)
        self.step_builder = StepBuilderFrame(wf_box, text_widget=self.custom_text)

        # --- SECTION 2 : FORMAT DE CONDITIONNEMENT ---
        cond_section = Section(content, title="Format de conditionnement", accent=ACCENT_BLUE)
        cond_section.pack(fill="x", pady=(0, SPACE_LG))
        cond_container = tk.Frame(cond_section.content, bg=DARK_CARD)
        cond_container.pack(fill="x")

        row_conditionner = OptionRow(
            cond_container, key="conditionner", label="Conditionner la pièce",
            subtitle="Conditionner la pièce selon la gamme de conditionnement.", accent=ACCENT_BLUE
        )
        row_conditionner.pack(fill="x", pady=(0, SPACE_SM))
        self._cond_option_group.add(row_conditionner)

        row_passer = OptionRow(
            cond_container, key="passer", label="Passer au poste suivant",
            subtitle="Passer la pièce au poste suivant.", accent=ACCENT_BLUE
        )
        row_passer.pack(fill="x")
        self._cond_option_group.add(row_passer)
        self._cond_option_group.select("conditionner")

        # --- SECTION 3 : PARAMÈTRES DE CAPTURE VIDÉO ---
        cap_section = Section(content, title="Paramètres de capture vidéo", accent=ACCENT_GREEN)
        cap_section.pack(fill="x")
        grid = tk.Frame(cap_section.content, bg=DARK_CARD)
        grid.pack(fill="x")
        grid.columnconfigure(1, weight=1)

        def _param_row(row_idx, label_text, help_text, widget_factory):
            top_pad = 0 if row_idx == 0 else SPACE_LG
            tk.Label(grid, text=label_text, font=FONT_BODY_BOLD, fg=TEXT_PRIMARY,
                     bg=DARK_CARD, anchor="w").grid(row=row_idx, column=0, sticky="w", pady=(top_pad, 0))
            widget = widget_factory()
            widget.grid(row=row_idx, column=1, sticky="e", pady=(top_pad, 0))
            tk.Label(grid, text=help_text, font=FONT_CAPTION, fg=TEXT_MUTED,
                     bg=DARK_CARD, anchor="w").grid(row=row_idx + 1, column=0, columnspan=2, sticky="w", pady=(2, 0))
            return widget

        self.spin_interval = _param_row(0, "Intervalle d'analyse (secondes)", "Fréquence d'échantillonnage.",
                                        lambda: StyledSpinbox(grid, from_=0.05, to=5.0, increment=0.05, width=8, font=FONT_BODY_BOLD))
        self.spin_interval.delete(0, "end")
        self.spin_interval.insert(0, "0.18")

        self.spin_window = _param_row(2, "Taille de fenêtre", "Nombre d'images regroupées.",
                                      lambda: StyledSpinbox(grid, from_=1, to=10, width=8, font=FONT_BODY_BOLD))
        self.spin_window.delete(0, "end")
        self.spin_window.insert(0, "3")

        self.spin_scale = _param_row(4, "Facteur d'échelle", "Redimensionnement avant analyse.",
                                     lambda: StyledSpinbox(grid, from_=0.1, to=1.0, increment=0.05, width=8, font=FONT_BODY_BOLD))
        self.spin_scale.delete(0, "end")
        self.spin_scale.insert(0, "0.75")

        # --- FOOTER ---
        btn_row = tk.Frame(self, bg=DARK_BG, padx=SPACE_XL, pady=SPACE_LG)
        btn_row.pack(fill="x", side="bottom")

        RoundedButton(btn_row, text="Annuler", variant="ghost", width=140, height=46,
                      command=self._on_cancel).pack(side="right", padx=(SPACE_MD, 0))
        RoundedButton(btn_row, text="Confirmer", variant="primary", width=160, height=46,
                      command=self._on_confirm).pack(side="right")

        default_key = "injection" if "injection" in workflows else next(iter(workflows), None)
        if default_key:
            self._option_group.select(default_key)

    # ═══════════════════════════════════════════════════════════
    # LOGIQUE & EVENTS
    # ═══════════════════════════════════════════════════════════
    def _on_workflow_change(self, wf_key):
        workflows = getattr(config, 'WORKFLOW_TYPES', {})
        details = workflows.get(wf_key, {})

        title = strip_emoji(details.get("label", wf_key.capitalize()))
        description = details.get("desc", "Aucune description.")
        steps_list = details.get("steps", [])

        # Reconstruct the detailed step list preview
        if steps_list:
            steps_text = "Étapes prévues :\n" + "\n".join([f"  • {step}" for step in steps_list])
        elif wf_key == "custom":
            steps_text = "Étapes : Saisie libre par l'utilisateur"
        else:
            steps_text = "Étapes : Variable"

        self.lbl_card_title.config(text=title)
        self.lbl_card_desc.config(text=description)
        self.lbl_card_meta.config(text=steps_text)

        # Manage dynamic frames
        has_control_choice = details.get("has_control_choice", False)
        if has_control_choice:
            self.sub_control_frame.pack(fill="x", pady=(SPACE_MD, 0))
        else:
            self.sub_control_frame.pack_forget()

        if wf_key != "custom":
            self.defects_frame.pack(fill="x", pady=(SPACE_MD, 0))
            self.custom_label.pack_forget()
            self.step_builder.pack_forget()
            self.custom_text.pack_forget()
        else:
            self.defects_frame.pack_forget()
            self.custom_label.pack(anchor="w", pady=(SPACE_LG, SPACE_SM))
            self.step_builder.pack(fill="x", pady=(0, SPACE_SM))
            self.custom_text.pack(fill="x")

    def _on_confirm(self):
        wf_type = self._option_group.selected_key
        custom = self.custom_text.get("1.0", "end").strip() if wf_type == "custom" else None
        cond_mode = self._cond_option_group.selected_key

        selected_defects = [defect for defect, var in self.checkbox_vars.items() if var.get()]
        control_type = self.var_control_type.get() if getattr(config, 'WORKFLOW_TYPES', {}).get(wf_type, {}).get("has_control_choice") else None

        workflows = getattr(config, 'WORKFLOW_TYPES', {})
        expected_steps = len(workflows[wf_type]["steps"]) if wf_type in workflows and workflows[wf_type].get("steps") else None

        self.result = {
            "workflow_type": wf_type,
            "control_type": control_type,
            "selected_defects": selected_defects,
            "custom_steps": custom,
            "conditioning_mode": cond_mode,
            "expected_step_count": expected_steps,
            "frame_interval_sec": float(self.spin_interval.get()),
            "window_size": int(self.spin_window.get()),
            "resize_factor": float(self.spin_scale.get())
        }
        self._user_action = "confirm"
        self.destroy()

    def _on_cancel(self):
        self.result = None
        self._user_action = "cancel"
        self.destroy()