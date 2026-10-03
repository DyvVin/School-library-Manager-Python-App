import tkinter as tk
from tkinter import ttk

FONT = ('Bahnschrift SemiLight', 11)

BG_ROOT = '#f5e2d8'
BG_PANEL = '#ebd8c2'
BG_FIELD = '#fff5eb'
BG_BUTTON = '#d6b89a'
BG_BUTTON_HOVER = '#c79f72'
BG_BUTTON_ACTIVE = '#b98560'
BG_TREE = '#f5ead8'
BG_TREE_ALT = '#efe0cf'
BG_HEADER = '#d4ad86'
TEXT_COLOR = '#4b3725'
SCROLL_BG = '#e6c8a7'
SELECT_BG = '#c79f72'
SELECT_FG = '#2f1f12'


def apply_design(root):
    root.configure(bg=BG_ROOT)
    root.option_add('*Font', FONT)

    style = ttk.Style(root)
    try:
        style.theme_use('clam')
    except tk.TclError:
        pass

    style.configure('App.TFrame', background=BG_PANEL)
    style.configure('App.TLabel', background=BG_PANEL, foreground=TEXT_COLOR, font=FONT)
    style.configure('App.TEntry', fieldbackground=BG_FIELD, background=BG_FIELD, foreground=TEXT_COLOR, font=FONT)
    style.configure('App.TCombobox', fieldbackground=BG_FIELD, background=BG_FIELD, foreground=TEXT_COLOR, font=FONT)
    style.configure('App.Treeview', background=BG_TREE, fieldbackground=BG_TREE, foreground=TEXT_COLOR, font=FONT, rowheight=26)
    style.configure('App.Treeview.Heading', background=BG_HEADER, foreground=TEXT_COLOR, font=FONT)
    style.map('App.Treeview', background=[('selected', SELECT_BG)], foreground=[('selected', SELECT_FG)])
    style.configure('App.TScrollbar', background=SCROLL_BG, troughcolor=BG_PANEL, arrowcolor=TEXT_COLOR)
    try:
        style.layout('Vertical.App.TScrollbar', style.layout('Vertical.TScrollbar'))
        style.layout('Horizontal.App.TScrollbar', style.layout('Horizontal.TScrollbar'))
    except tk.TclError:
        pass
    style.configure('App.TNotebook', background=BG_ROOT, borderwidth=0)
    style.configure('App.TNotebook.Tab', background=BG_PANEL, foreground=TEXT_COLOR, font=FONT, padding=[10, 6])
    style.map('App.TNotebook.Tab', background=[('selected', BG_BUTTON)], foreground=[('selected', TEXT_COLOR)])


def add_button_hover(button):
    original_bg = button.cget('bg')

    def on_enter(_event):
        button.configure(bg=BG_BUTTON_HOVER)

    def on_leave(_event):
        button.configure(bg=original_bg)

    button.bind('<Enter>', on_enter)
    button.bind('<Leave>', on_leave)
    return button


def create_button(parent, text, command=None, **kwargs):
    button = tk.Button(
        parent,
        text=text,
        command=command,
        bg=BG_BUTTON,
        fg=TEXT_COLOR,
        activebackground=BG_BUTTON_ACTIVE,
        activeforeground=TEXT_COLOR,
        font=FONT,
        bd=0,
        relief='flat',
        cursor='hand2',
        highlightthickness=0,
        **kwargs
    )
    return add_button_hover(button)


def default_combobox_match(item, search):
    item_text = item.lower()
    query_tokens = [token for token in search.lower().split() if token]
    return all(token in item_text for token in query_tokens)


class SearchableCombobox(ttk.Combobox):
    def __init__(self, parent, values=None, match_fn=None, **kwargs):
        self._all_values = list(values) if values is not None else []
        self._match_fn = match_fn or default_combobox_match
        super().__init__(parent, values=self._all_values, state='normal', **kwargs)
        self.bind('<KeyRelease>', self._on_keyrelease)
        self.bind('<<ComboboxSelected>>', self._on_selection)

    def set_completion_list(self, values):
        self._all_values = list(values)
        self['values'] = self._all_values

    def __setitem__(self, key, value):
        if key == 'values':
            self._all_values = list(value)
        super().__setitem__(key, value)

    def _on_keyrelease(self, event):
        if event.keysym in ('Left', 'Right', 'Home', 'End', 'Tab', 'Shift_L', 'Shift_R', 'Control_L', 'Control_R', 'Alt_L', 'Alt_R'):
            return
        current_text = self.get()
        self._filter_values(current_text)
        self.icursor(tk.END)
        self.focus_set()

    def _on_selection(self, _event):
        self._filter_values(self.get())

    def _filter_values(self, text):
        if not text:
            self['values'] = self._all_values
            return
        matched = [value for value in self._all_values if self._match_fn(value, text)]
        self['values'] = matched
        if matched:
            self.event_generate('<Down>')
