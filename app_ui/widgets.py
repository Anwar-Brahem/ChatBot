# -*- coding: utf-8 -*-
"""
app_ui/widgets.py - Widgets tkinter customises et reutilisables.

Contient les briques visuelles "modernes" utilisees partout dans l'app :
- RoundedButton   : bouton a coins arrondis avec effet hover
- RoundedCard     : conteneur a coins arrondis (remplace tk.LabelFrame)
- StatusPill      : pastille arrondie coloree pour afficher un statut
- ScrollableArea  : zone scrollable (molette + scrollbar) reutilisable
- StyledEntry / StyledSpinbox / StyledScrolledText : champs de saisie
"""

import tkinter as tk
from tkinter import scrolledtext

from .theme import (
    DARK_BG, DARK_CARD, DARK_CARD_HOVER, DARK_CARD_ALT, DARK_BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ACCENT_BLUE, ACCENT_BLUE_HOVER, ACCENT_BLUE_SOFT,
    ACCENT_GREEN, ACCENT_GREEN_HOVER, ACCENT_GREEN_SOFT,
    ACCENT_RED, ACCENT_RED_HOVER, ACCENT_RED_SOFT,
    ACCENT_AMBER, ACCENT_AMBER_SOFT,
    FONT_FAMILY, FONT_MONO, FONT_BODY, FONT_BODY_BOLD, FONT_SMALL, FONT_H3,
    RADIUS_MD, RADIUS_SM, SPACE_SM, SPACE_LG,
)


def _round_rect(canvas, x1, y1, x2, y2, radius=12, **kwargs):
    """Dessine un rectangle a coins arrondis sur un Canvas et retourne son id."""
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


# ═══════════════════════════════════════════════════════════════════
# BOUTON ARRONDI
# ═══════════════════════════════════════════════════════════════════
_VARIANT_COLORS = {
    "primary": (ACCENT_BLUE, ACCENT_BLUE_HOVER, TEXT_PRIMARY),
    "success": (ACCENT_GREEN, ACCENT_GREEN_HOVER, TEXT_PRIMARY),
    "danger": (ACCENT_RED, ACCENT_RED_HOVER, TEXT_PRIMARY),
    "ghost": (DARK_CARD, DARK_CARD_HOVER, TEXT_SECONDARY),
    "outline": (DARK_BG, DARK_CARD_HOVER, ACCENT_BLUE),
}


class RoundedButton(tk.Canvas):
    """Bouton a coins arrondis, avec etats hover / disabled, dessine sur un Canvas
    (tkinter ne supporte pas les coins arrondis nativement sur tk.Button)."""

    def __init__(self, master, text="", command=None, variant="primary",
                 width=180, height=42, radius=RADIUS_MD, font=None, icon="",
                 bg=None, **kwargs):
        parent_bg = bg or (master.cget("bg") if "bg" in master.keys() else DARK_BG)
        super().__init__(master, width=width, height=height, bg=parent_bg,
                          highlightthickness=0, **kwargs)
        self.command = command
        self.variant = variant
        self.text = f"{icon}  {text}".strip() if icon else text
        self.font = font or FONT_BODY_BOLD
        self.radius = radius
        self.width = width
        self.height = height
        self._disabled = False

        base, hover, fg = _VARIANT_COLORS.get(variant, _VARIANT_COLORS["primary"])
        self._base, self._hover, self._fg = base, hover, fg
        self._outline = ACCENT_BLUE if variant == "outline" else ""

        self.bind("<Enter>", lambda e: self._render(hover=True))
        self.bind("<Leave>", lambda e: self._render(hover=False))
        self.bind("<Button-1>", self._on_click)

        self._render(hover=False)

    def set_text(self, text, icon=""):
        """Met a jour le texte du bouton et re-rend la zone Canvas."""
        self.text = f"{icon}  {text}".strip() if icon else text
        self._render(hover=False)

    def _render(self, hover):
        self.delete("all")
        if self._disabled:
            fill, fg = DARK_CARD_ALT, TEXT_MUTED
        else:
            fill = self._hover if hover else self._base
            fg = self._fg
        _round_rect(self, 1, 1, self.width - 1, self.height - 1,
                    radius=self.radius, fill=fill, outline=self._outline, width=1.4)
        self.create_text(self.width / 2, self.height / 2, text=self.text,
                          fill=fg, font=self.font)
        self.configure(cursor="hand2" if not self._disabled else "arrow")

    def _on_click(self, _event):
        if not self._disabled and self.command:
            self.command()

    def config_state(self, state):
        """state: 'normal' ou 'disabled' (imite l'API des widgets tk classiques)."""
        self._disabled = (state == "disabled")
        self._render(hover=False)

    def config(self, **kwargs):
        if "state" in kwargs:
            self.config_state(kwargs.pop("state"))
        if "text" in kwargs:
            self.set_text(kwargs.pop("text"))
        if kwargs:
            super().config(**kwargs)

    def configure(self, **kwargs):
        self.config(**kwargs)


# ═══════════════════════════════════════════════════════════════════
# SECTION / CARTE (remplace tk.LabelFrame / StyledFrame)
# ═══════════════════════════════════════════════════════════════════
# NOTE: la premiere version dessinait le fond arrondi sur un Canvas dont la
# hauteur se recalculait a chaque <Configure> du contenu. Nichee dans une
# ScrollableArea (qui recalcule aussi sa scrollregion a chaque <Configure>),
# la boucle de recalcul produisait parfois un rendu intermediaire avant que
# le titre soit repositionne -> le texte semblait "coupe/duplique" (le bug
# visible en capture d'ecran). Cette version utilise un Frame borde classique
# (highlightthickness) : aucun recalcul recursif, donc aucun rendu
# intermediaire possible. Coin "releve" visuellement par une bordure fine
# plutot qu'un vrai rayon -> reste sobre, et surtout fiable.
class Section(tk.Frame):
    """Conteneur "carte" avec titre optionnel en en-tete accentue.
    Le contenu se place dans `self.content` (un tk.Frame classique)."""

    def __init__(self, master, title=None, accent=ACCENT_BLUE, padding=SPACE_LG,
                 bg_parent=None, **kwargs):
        bg_parent = bg_parent or (master.cget("bg") if "bg" in master.keys() else DARK_BG)
        super().__init__(master, bg=DARK_CARD, highlightthickness=1,
                          highlightbackground=DARK_BORDER, bd=0, **kwargs)

        if title:
            header = tk.Frame(self, bg=DARK_CARD)
            header.pack(fill="x", padx=padding, pady=(padding, SPACE_SM))
            bar = tk.Frame(header, bg=accent, width=4)
            bar.pack(side="left", fill="y", padx=(0, 10))
            tk.Label(header, text=title, font=FONT_H3, fg=accent, bg=DARK_CARD).pack(side="left")

        self.content = tk.Frame(self, bg=DARK_CARD)
        self.content.pack(fill="both", expand=True, padx=padding, pady=(0, padding))


# Alias retro-compatible : main_window.py importe encore "RoundedCard".
RoundedCard = Section


# ═══════════════════════════════════════════════════════════════════
# LISTE A SELECTION MODERNE (remplace les tk.Radiobutton "puce")
# ═══════════════════════════════════════════════════════════════════
class OptionRow(tk.Frame):
    """Une ligne cliquable pleine largeur (cible bien plus grande qu'un radio
    bouton natif), avec bandeau et fond qui s'accentuent quand selectionnee."""

    def __init__(self, master, key, label, subtitle="", accent=ACCENT_BLUE,
                 on_select=None, **kwargs):
        super().__init__(master, bg=DARK_CARD_ALT, highlightthickness=1,
                          highlightbackground=DARK_BORDER, cursor="hand2", **kwargs)
        self.key = key
        self.accent = accent
        self.on_select = on_select
        self._selected = False

        self.indicator = tk.Frame(self, bg=DARK_BORDER, width=5)
        self.indicator.pack(side="left", fill="y")

        inner = tk.Frame(self, bg=DARK_CARD_ALT)
        inner.pack(side="left", fill="both", expand=True, padx=(16, 16), pady=13)
        self._inner = inner

        self.lbl_title = tk.Label(inner, text=label, font=FONT_BODY_BOLD,
                                   fg=TEXT_PRIMARY, bg=DARK_CARD_ALT, anchor="w")
        self.lbl_title.pack(fill="x")

        self.lbl_sub = None
        if subtitle:
            self.lbl_sub = tk.Label(inner, text=subtitle, font=FONT_SMALL,
                                     fg=TEXT_SECONDARY, bg=DARK_CARD_ALT, anchor="w",
                                     justify="left")
            self.lbl_sub.pack(fill="x", pady=(3, 0))

        for widget in (self, self.indicator, inner, self.lbl_title):
            widget.bind("<Button-1>", self._handle_click)
        if self.lbl_sub is not None:
            self.lbl_sub.bind("<Button-1>", self._handle_click)

    def _handle_click(self, _event=None):
        if self.on_select:
            self.on_select(self.key)

    def set_selected(self, selected):
        self._selected = selected
        bg = ACCENT_BLUE_SOFT if selected else DARK_CARD_ALT
        self.indicator.config(bg=self.accent if selected else DARK_BORDER)
        self.config(highlightbackground=self.accent if selected else DARK_BORDER,
                    highlightthickness=2 if selected else 1)
        self._inner.config(bg=bg)
        self.lbl_title.config(bg=bg)
        if self.lbl_sub is not None:
            self.lbl_sub.config(bg=bg)


class OptionGroup:
    """Gere la selection unique entre plusieurs OptionRow (equivalent d'un
    groupe de Radiobutton mais avec des lignes pleine largeur modernes)."""

    def __init__(self, on_change=None):
        self.rows = {}
        self.selected_key = None
        self.on_change = on_change

    def add(self, row):
        self.rows[row.key] = row
        row.on_select = self.select

    def select(self, key):
        self.selected_key = key
        for row_key, row in self.rows.items():
            row.set_selected(row_key == key)
        if self.on_change:
            self.on_change(key)


# ═══════════════════════════════════════════════════════════════════
# UTILITAIRE : suppression des emojis dans du texte externe (config.py)
# ═══════════════════════════════════════════════════════════════════
import re as _re

_EMOJI_PATTERN = _re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U00002600-\U000026FF"
    "\U00002700-\U000027BF"
    "\U0001F1E6-\U0001F1FF"
    "\uFE0F"
    "]+",
    flags=_re.UNICODE,
)


def strip_emoji(text):
    """Retire les emojis d'un texte (les labels de workflow viennent de
    config.py et peuvent en contenir) et nettoie les espaces restants."""
    if not text:
        return text
    return _re.sub(r"\s{2,}", " ", _EMOJI_PATTERN.sub("", text)).strip()


# ═══════════════════════════════════════════════════════════════════
# PASTILLE DE STATUT
# ═══════════════════════════════════════════════════════════════════
_PILL_COLORS = {
    "idle": (DARK_CARD_ALT, TEXT_SECONDARY),
    "info": (ACCENT_BLUE_SOFT, ACCENT_BLUE),
    "success": (ACCENT_GREEN_SOFT, ACCENT_GREEN),
    "warning": (ACCENT_AMBER_SOFT, ACCENT_AMBER),
    "error": (ACCENT_RED_SOFT, ACCENT_RED),
}


class StatusPill(tk.Canvas):
    """Petite pastille arrondie type 'badge' pour afficher un statut clairement
    (remplace un simple tk.Label de couleur pour plus de lisibilite)."""

    def __init__(self, master, text="", state="idle", width=220, height=30, **kwargs):
        parent_bg = master.cget("bg") if "bg" in master.keys() else DARK_BG
        super().__init__(master, width=width, height=height, bg=parent_bg,
                          highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.set_status(text, state)

    def set_status(self, text, state="idle"):
        fill, fg = _PILL_COLORS.get(state, _PILL_COLORS["idle"])
        self.delete("all")
        _round_rect(self, 0, 0, self.width, self.height, radius=self.height / 2,
                    fill=fill, outline="")
        self.create_oval(10, self.height / 2 - 4, 18, self.height / 2 + 4, fill=fg, outline="")
        self.create_text(self.width / 2 + 6, self.height / 2, text=text,
                          fill=fg, font=FONT_SMALL)


# ═══════════════════════════════════════════════════════════════════
# ZONE SCROLLABLE (molette + scrollbar) - reutilisable partout
# ═══════════════════════════════════════════════════════════════════
class ScrollableArea(tk.Frame):
    """Frame scrollable verticalement, avec support de la molette de souris
    (Windows/Mac: <MouseWheel>, Linux: <Button-4>/<Button-5>).
    Le contenu se place dans `self.body`."""

    def __init__(self, master, bg=DARK_BG, **kwargs):
        super().__init__(master, bg=bg, **kwargs)

        self._canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        self._scrollbar = tk.Scrollbar(self, orient="vertical", command=self._canvas.yview)
        self.body = tk.Frame(self._canvas, bg=bg)

        self.body.bind("<Configure>", lambda e: self._canvas.configure(
            scrollregion=self._canvas.bbox("all")))
        self._window = self._canvas.create_window((0, 0), window=self.body, anchor="nw")
        self._canvas.configure(yscrollcommand=self._scrollbar.set)

        self._canvas.pack(side="left", fill="both", expand=True)
        self._scrollbar.pack(side="right", fill="y")

        self._canvas.bind("<Configure>", lambda e: self._canvas.itemconfig(self._window, width=e.width))

        for widget in (self._canvas, self.body):
            widget.bind("<Enter>", self._bind_wheel)
            widget.bind("<Leave>", self._unbind_wheel)

    def _bind_wheel(self, _e):
        self._canvas.bind_all("<MouseWheel>", self._on_wheel)
        self._canvas.bind_all("<Button-4>", self._on_wheel)
        self._canvas.bind_all("<Button-5>", self._on_wheel)

    def _unbind_wheel(self, _e):
        self._canvas.unbind_all("<MouseWheel>")
        self._canvas.unbind_all("<Button-4>")
        self._canvas.unbind_all("<Button-5>")

    def _on_wheel(self, event):
        if event.num == 4:
            self._canvas.yview_scroll(-3, "units")
        elif event.num == 5:
            self._canvas.yview_scroll(3, "units")
        else:
            self._canvas.yview_scroll(int(-1 * (event.delta / 120) * 3), "units")


# ═══════════════════════════════════════════════════════════════════
# CHAMPS DE SAISIE
# ═══════════════════════════════════════════════════════════════════
class StyledEntry(tk.Entry):
    def __init__(self, master=None, **kwargs):
        defaults = {
            "bg": DARK_BG, "fg": TEXT_PRIMARY, "insertbackground": ACCENT_BLUE,
            "font": FONT_BODY, "bd": 0, "highlightthickness": 1,
            "highlightbackground": DARK_BORDER, "highlightcolor": ACCENT_BLUE,
            "relief": "flat",
        }
        defaults.update(kwargs)
        super().__init__(master, **defaults)


class StyledSpinbox(tk.Spinbox):
    def __init__(self, master=None, **kwargs):
        defaults = {
            "bg": DARK_BG, "fg": TEXT_PRIMARY, "font": FONT_BODY,
            "bd": 0, "highlightthickness": 1, "highlightbackground": DARK_BORDER,
            "highlightcolor": ACCENT_BLUE, "buttonbackground": DARK_CARD,
            "buttoncursor": "hand2", "relief": "flat", "justify": "center",
        }
        defaults.update(kwargs)
        super().__init__(master, **defaults)


class StyledScrolledText(scrolledtext.ScrolledText):
    def __init__(self, master=None, **kwargs):
        defaults = {
            "bg": DARK_BG, "fg": TEXT_PRIMARY, "insertbackground": ACCENT_BLUE,
            "font": (FONT_MONO, 11), "wrap": "word", "bd": 0,
            "highlightthickness": 1, "highlightbackground": DARK_BORDER,
            "relief": "flat", "padx": 12, "pady": 12,
        }
        defaults.update(kwargs)
        super().__init__(master, **defaults)


# ─── Retro-compatibilite avec l'ancien nom StyledButton / StyledFrame ────────
StyledButton = RoundedButton
StyledFrame = RoundedCard
