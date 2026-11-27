# Dynamic Left Sidebar Menu with Live Search/Filter Option
import customtkinter as ctk
from tkinter import messagebox

# Shared references injected from main_screen.py
root = None
CARD_BG = "#1E293B"
app_state = {}
status_badge = None
start_pattern = None
open_wifi_tool_popup = None

_sidebar_ref = None
_scroll_area_ref = None
_search_entry_ref = None
_search_var = None
_nav_label_ref = None
_clear_btn_ref = None

_sidebar_expanded = True
_EXPANDED_WIDTH = 235
_COLLAPSED_WIDTH = 56
_section_widgets = []
_active_menu_config = None


def get_menu_config():
    """Returns dynamic menu sections and items. Modify here to add/remove menus dynamically."""
    return [
        {
            "title": "File",
            "icon": "📁",
            "items": [
                ("Restart Workspace", restart_patterns),
                ("Logout to Login Screen", handle_logout),
                "---",
                ("Exit Application", lambda: root.destroy() if root else None),
            ],
        },
        {
            "title": "Patterns",
            "icon": "🎨",
            "items": [
                ("Play / Pause Animations", toggle_pause),
                ("Replay Spiral (Block 1)", restart_patterns),
                "---",
                ("Clear All Screens", clear_all_canvases),
            ],
        },
        {
            "title": "Tools",
            "icon": "🛠️",
            "items": [
                (
                    "Saved Wi-Fi Passwords",
                    lambda: open_wifi_tool_popup(root) if open_wifi_tool_popup else None,
                ),
                (
                    "System Status Info",
                    lambda: messagebox.showinfo("Status", "All 4 Render Engines Online."),
                ),
            ],
        },
        {
            "title": "View",
            "icon": "👁️",
            "items": [
                ("Dark Theme (Default)", lambda: set_theme("dark")),
                ("Light Theme", lambda: set_theme("light")),
            ],
        },
        {
            "title": "Help",
            "icon": "❓",
            "items": [
                (
                    "About NEXUS HUB",
                    lambda: messagebox.showinfo(
                        "About", "NEXUS HUB v1.0\n4-Block Python Control Center"
                    ),
                ),
            ],
        },
    ]


def create_left_sidebar_menu(sidebar_container, menu_config=None):
    """Builds a dynamic, collapsible left-side accordion navigation menu with a live filter bar."""
    global _sidebar_ref, _scroll_area_ref, _search_entry_ref, _search_var
    global _nav_label_ref, _clear_btn_ref, _active_menu_config

    _sidebar_ref = sidebar_container
    _active_menu_config = menu_config if menu_config is not None else get_menu_config()

    for child in sidebar_container.winfo_children():
        child.destroy()

    # Sidebar Header
    header_frame = ctk.CTkFrame(sidebar_container, fg_color="transparent", height=34)
    header_frame.pack(fill="x", padx=10, pady=(10, 4))
    header_frame.pack_propagate(False)

    _nav_label_ref = ctk.CTkLabel(
        header_frame,
        text="NAVIGATION",
        font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
        text_color="#94A3B8",
    )
    _nav_label_ref.pack(side="left", padx=4)

    # Filter / Search Box Container
    filter_frame = ctk.CTkFrame(sidebar_container, fg_color="transparent", height=34)
    filter_frame.pack(fill="x", padx=8, pady=(2, 6))
    filter_frame.pack_propagate(False)

    _search_var = ctk.StringVar(value="")

    _search_entry_ref = ctk.CTkEntry(
        filter_frame,
        textvariable=_search_var,
        placeholder_text="🔍 Filter menu...",
        height=30,
        corner_radius=8,
        fg_color="#0F172A",
        border_color="#334155",
        border_width=1,
        text_color="#F8FAFC",
        placeholder_text_color="#64748B",
        font=ctk.CTkFont(family="Segoe UI", size=12),
    )
    _search_entry_ref.pack(side="left", fill="x", expand=True)

    _clear_btn_ref = ctk.CTkButton(
        filter_frame,
        text="✕",
        width=26,
        height=28,
        corner_radius=6,
        fg_color="transparent",
        hover_color="#334155",
        text_color="#94A3B8",
        font=ctk.CTkFont(size=11, weight="bold"),
        command=clear_filter,
    )

    # Scrollable container for dynamic menu sections
    _scroll_area_ref = ctk.CTkScrollableFrame(
        sidebar_container,
        fg_color="transparent",
        scrollbar_button_color="#334155",
        scrollbar_button_hover_color="#475569",
    )
    _scroll_area_ref.pack(fill="both", expand=True, padx=4, pady=4)

    # Bind live filtering on text change
    _search_var.trace_add("write", lambda *_: _on_filter_change())

    # Initial render
    _render_menu_sections(filter_query="")


def _on_filter_change():
    query = _search_var.get().strip() if _search_var else ""
    if _clear_btn_ref:
        if query:
            _clear_btn_ref.pack(side="right", padx=(4, 0))
        else:
            _clear_btn_ref.pack_forget()
    _render_menu_sections(filter_query=query)


def clear_filter():
    if _search_var:
        _search_var.set("")
    if _search_entry_ref:
        _search_entry_ref.focus_set()


def _render_menu_sections(filter_query=""):
    """Renders menu sections dynamically filtered by the search query."""
    global _section_widgets
    if _scroll_area_ref is None:
        return

    for child in _scroll_area_ref.winfo_children():
        child.destroy()
    _section_widgets = []

    q = filter_query.lower().strip()
    total_matches = 0

    for idx, section in enumerate(_active_menu_config):
        sec_title = section["title"]
        sec_icon = section["icon"]
        section_matches = q in sec_title.lower() if q else False

        # Filter sub-items
        filtered_items = []
        for item in section["items"]:
            if item == "---":
                if not q:
                    filtered_items.append(item)
            else:
                label, cmd = item
                if not q or section_matches or (q in label.lower()):
                    filtered_items.append(item)

        if q and not filtered_items and not section_matches:
            continue

        total_matches += 1

        sec_frame = ctk.CTkFrame(_scroll_area_ref, fg_color="transparent")
        sec_frame.pack(fill="x", pady=(2, 4))

        sub_frame = ctk.CTkFrame(sec_frame, fg_color="#0F172A", corner_radius=8)
        # Auto-expand matching sections when filtering; otherwise default first section open
        is_open = {"value": True if q else (idx == 0)}

        btn_text = (
            f"{sec_icon}  {sec_title}  ▾"
            if _sidebar_expanded
            else sec_icon
        )
        header_btn = ctk.CTkButton(
            sec_frame,
            text=btn_text,
            anchor="w" if _sidebar_expanded else "center",
            height=34,
            corner_radius=8,
            fg_color="transparent",
            hover_color="#1E3A8A",
            text_color="#F8FAFC",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
        )
        header_btn.pack(fill="x", padx=2)

        def make_toggle(btn, sub, state_dict, title, icon):
            def _toggle():
                global _sidebar_expanded
                if not _sidebar_expanded:
                    toggle_sidebar()
                state_dict["value"] = not state_dict["value"]
                if state_dict["value"]:
                    btn.configure(text=f"{icon}  {title}  ▾")
                    sub.pack(fill="x", padx=6, pady=(4, 2))
                else:
                    btn.configure(text=f"{icon}  {title}  ▸")
                    sub.pack_forget()

            return _toggle

        header_btn.configure(
            command=make_toggle(header_btn, sub_frame, is_open, sec_title, sec_icon)
        )

        # Populate sub-items inside the accordion drawer
        for item in filtered_items:
            if item == "---":
                sep = ctk.CTkFrame(sub_frame, height=1, fg_color="#334155")
                sep.pack(fill="x", padx=8, pady=4)
            else:
                label, cmd = item
                item_btn = ctk.CTkButton(
                    sub_frame,
                    text=f"•  {label}",
                    anchor="w",
                    height=28,
                    corner_radius=6,
                    fg_color="transparent",
                    hover_color="#2563EB",
                    text_color="#CBD5E1",
                    font=ctk.CTkFont(family="Segoe UI", size=12),
                    command=cmd,
                )
                item_btn.pack(fill="x", padx=4, pady=2)

        if _sidebar_expanded and is_open["value"] and filtered_items:
            sub_frame.pack(fill="x", padx=6, pady=(4, 2))
        elif _sidebar_expanded:
            header_btn.configure(text=f"{sec_icon}  {sec_title}  ▸")

        _section_widgets.append(
            {
                "btn": header_btn,
                "sub": sub_frame,
                "state": is_open,
                "title": sec_title,
                "icon": sec_icon,
            }
        )

    if q and total_matches == 0 and _sidebar_expanded:
        empty_lbl = ctk.CTkLabel(
            _scroll_area_ref,
            text=f'No menu items match\n"{filter_query}"',
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#64748B",
            justify="center",
        )
        empty_lbl.pack(pady=24, padx=8)


def toggle_sidebar():
    """Dynamically collapses or expands the left sidebar between icon-only and full width."""
    global _sidebar_expanded
    if _sidebar_ref is None:
        return

    _sidebar_expanded = not _sidebar_expanded

    if _sidebar_expanded:
        _sidebar_ref.configure(width=_EXPANDED_WIDTH)
        if _nav_label_ref:
            _nav_label_ref.configure(text="NAVIGATION")
        if _search_entry_ref:
            _search_entry_ref.pack(side="left", fill="x", expand=True)
            if _search_var and _search_var.get().strip() and _clear_btn_ref:
                _clear_btn_ref.pack(side="right", padx=(4, 0))
        for sec in _section_widgets:
            arrow = "▾" if sec["state"]["value"] else "▸"
            sec["btn"].configure(
                text=f"{sec['icon']}  {sec['title']}  {arrow}", anchor="w"
            )
            if sec["state"]["value"]:
                sec["sub"].pack(fill="x", padx=6, pady=(4, 2))
    else:
        _sidebar_ref.configure(width=_COLLAPSED_WIDTH)
        if _nav_label_ref:
            _nav_label_ref.configure(text="NAV")
        if _search_entry_ref:
            _search_entry_ref.pack_forget()
        if _clear_btn_ref:
            _clear_btn_ref.pack_forget()
        for sec in _section_widgets:
            sec["btn"].configure(text=sec["icon"], anchor="center")
            sec["sub"].pack_forget()


# ================= MENU ACTIONS =================
def toggle_pause():
    app_state["running"] = not app_state.get("running", True)
    if status_badge:
        if app_state["running"]:
            status_badge.configure(text="●  LIVE ENGINE ACTIVE", text_color="#4ADE80")
        else:
            status_badge.configure(text="❚❚  ENGINE PAUSED", text_color="#FACC15")


def restart_patterns():
    app_state["running"] = True
    if status_badge:
        status_badge.configure(text="●  LIVE ENGINE ACTIVE", text_color="#4ADE80")
    if app_state.get("screens") and start_pattern:
        start_pattern(app_state["screens"][0], app_state["pens"][0], app_state)


def clear_all_canvases():
    app_state["running"] = False
    if status_badge:
        status_badge.configure(text="■  CANVASES CLEARED", text_color="#94A3B8")
    for p in app_state.get("pens", []):
        p.clear()


def set_theme(mode):
    ctk.set_appearance_mode(mode)


def handle_logout():
    app_state["running"] = False
    if root:
        root.destroy()
    try:
        from login.login_page import ModernLoginApp
        ModernLoginApp().mainloop()
    except ImportError:
        pass
