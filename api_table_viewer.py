import threading
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import requests

# Theme matching NEXUS HUB
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG_MAIN = "#0F172A"
CARD_BG = "#1E293B"
CARD_BORDER = "#334155"
HEADER_BAR = "#1E3A8A"


class APITableViewer(ctk.CTkFrame):
    """
    Reusable CustomTkinter component that fetches JSON records from an API,
    displays them in a styled ttk.Treeview table, and provides:
      1. Global search across all columns
      2. Column-specific filter dropdown + filter input
      3. Click-to-sort on any table column header
    """

    def __init__(self, master, api_url="https://jsonplaceholder.typicode.com/users", **kwargs):
        super().__init__(master, fg_color=BG_MAIN, **kwargs)
        self.api_url = api_url
        self.all_records = []
        self.filtered_records = []
        self.columns = []
        self.sort_reverse = {}

        self._build_ui()
        self.fetch_api_data()

    def _build_ui(self):
        # ================= 1. TOP TOOLBAR & API URL BAR =================
        top_bar = ctk.CTkFrame(
            self, fg_color=CARD_BG, corner_radius=12, border_width=1, border_color=CARD_BORDER
        )
        top_bar.pack(fill="x", padx=12, pady=(12, 6))

        ctk.CTkLabel(
            top_bar,
            text="API Endpoint:",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#94A3B8",
        ).pack(side="left", padx=(14, 6), pady=10)

        self.url_entry = ctk.CTkEntry(
            top_bar,
            height=32,
            fg_color=BG_MAIN,
            border_color=CARD_BORDER,
            text_color="#F8FAFC",
            font=ctk.CTkFont(family="Consolas", size=12),
        )
        self.url_entry.insert(0, self.api_url)
        self.url_entry.pack(side="left", fill="x", expand=True, padx=6, pady=10)

        self.fetch_btn = ctk.CTkButton(
            top_bar,
            text="⟳ Fetch Records",
            width=125,
            height=32,
            corner_radius=8,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self.fetch_api_data,
        )
        self.fetch_btn.pack(side="right", padx=(6, 14), pady=10)

        # ================= 2. COLUMN FILTER CONTROLS BAR =================
        filter_bar = ctk.CTkFrame(
            self, fg_color=CARD_BG, corner_radius=12, border_width=1, border_color=CARD_BORDER
        )
        filter_bar.pack(fill="x", padx=12, pady=6)

        # Column selector dropdown
        ctk.CTkLabel(
            filter_bar,
            text="Filter Column:",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#E2E8F0",
        ).pack(side="left", padx=(14, 6), pady=10)

        self.col_var = ctk.StringVar(value="All Columns")
        self.col_dropdown = ctk.CTkOptionMenu(
            filter_bar,
            variable=self.col_var,
            values=["All Columns"],
            width=165,
            height=32,
            corner_radius=8,
            fg_color=BG_MAIN,
            button_color="#2563EB",
            button_hover_color="#1D4ED8",
            dropdown_fg_color=CARD_BG,
            command=lambda _: self.apply_filters(),
        )
        self.col_dropdown.pack(side="left", padx=6, pady=10)

        # Filter match mode dropdown
        self.mode_var = ctk.StringVar(value="Contains")
        self.mode_dropdown = ctk.CTkOptionMenu(
            filter_bar,
            variable=self.mode_var,
            values=["Contains", "Equals", "Starts With", "Ends With"],
            width=130,
            height=32,
            corner_radius=8,
            fg_color=BG_MAIN,
            button_color="#334155",
            button_hover_color="#475569",
            dropdown_fg_color=CARD_BG,
            command=lambda _: self.apply_filters(),
        )
        self.mode_dropdown.pack(side="left", padx=6, pady=10)

        # Filter search input
        self.filter_var = ctk.StringVar()
        self.filter_var.trace_add("write", lambda *_: self.apply_filters())

        self.filter_entry = ctk.CTkEntry(
            filter_bar,
            textvariable=self.filter_var,
            placeholder_text="🔍 Type value to filter table...",
            height=32,
            corner_radius=8,
            fg_color=BG_MAIN,
            border_color=CARD_BORDER,
            text_color="#F8FAFC",
            font=ctk.CTkFont(family="Segoe UI", size=12),
        )
        self.filter_entry.pack(side="left", fill="x", expand=True, padx=6, pady=10)

        self.clear_btn = ctk.CTkButton(
            filter_bar,
            text="Clear Filter",
            width=95,
            height=32,
            corner_radius=8,
            fg_color="#334155",
            hover_color="#475569",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self.clear_filters,
        )
        self.clear_btn.pack(side="left", padx=(4, 10), pady=10)

        # Record counter badge
        self.count_label = ctk.CTkLabel(
            filter_bar,
            text="0 / 0 records",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#4ADE80",
        )
        self.count_label.pack(side="right", padx=(6, 14), pady=10)

        # ================= 3. STYLED DATA TABLE (TREEVIEW) =================
        table_card = ctk.CTkFrame(
            self, fg_color=CARD_BG, corner_radius=12, border_width=1, border_color=CARD_BORDER
        )
        table_card.pack(fill="both", expand=True, padx=12, pady=(6, 12))

        self._configure_treeview_style()

        tree_container = tk.Frame(table_card, bg=CARD_BG)
        tree_container.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(tree_container, show="headings", selectmode="browse")

        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        # Alternating row tags
        self.tree.tag_configure("oddrow", background="#0F172A", foreground="#F8FAFC")
        self.tree.tag_configure("evenrow", background="#1E293B", foreground="#F8FAFC")

        # Double-click row to inspect full JSON record
        self.tree.bind("<Double-1>", self._on_row_double_click)

    def _configure_treeview_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background="#0F172A",
            foreground="#F8FAFC",
            fieldbackground="#0F172A",
            rowheight=32,
            borderwidth=0,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Treeview.Heading",
            background="#1E3A8A",
            foreground="#FFFFFF",
            relief="flat",
            padding=(8, 6),
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "Treeview.Heading",
            background=[("active", "#2563EB")],
        )
        style.map(
            "Treeview",
            background=[("selected", "#2563EB")],
            foreground=[("selected", "#FFFFFF")],
        )

    # ================= API FETCHING & FLATTENING =================
    def fetch_api_data(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Missing URL", "Please enter a valid API endpoint URL.")
            return

        self.fetch_btn.configure(state="disabled", text="Loading...")
        self.count_label.configure(text="Fetching API...", text_color="#FACC15")

        def worker():
            try:
                resp = requests.get(url, timeout=12)
                resp.raise_for_status()
                payload = resp.json()

                # Support both top-level list [...] and wrapped list {"data": [...]} / {"items": [...]}
                if isinstance(payload, list):
                    raw_list = payload
                elif isinstance(payload, dict):
                    raw_list = next(
                        (v for v in payload.values() if isinstance(v, list)),
                        [payload],
                    )
                else:
                    raw_list = [{"value": str(payload)}]

                flat_records = [self._flatten_dict(item) for item in raw_list if isinstance(item, dict)]
                self.after(0, lambda: self._load_records(flat_records))
            except Exception as exc:
                self.after(0, lambda: self._on_fetch_error(str(exc)))

        threading.Thread(target=worker, daemon=True).start()

    @staticmethod
    def _flatten_dict(d, parent_key="", sep="."):
        """Flattens nested JSON objects (e.g., address.city) so every field gets a clean column."""
        items = {}
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else str(k)
            if isinstance(v, dict):
                items.update(APITableViewer._flatten_dict(v, new_key, sep=sep))
            elif isinstance(v, list):
                items[new_key] = ", ".join(str(x) for x in v)
            else:
                items[new_key] = "" if v is None else str(v)
        return items

    def _on_fetch_error(self, error_msg):
        self.fetch_btn.configure(state="normal", text="⟳ Fetch Records")
        self.count_label.configure(text="API Error", text_color="#F87171")
        messagebox.showerror("API Request Failed", f"Could not fetch records:\n{error_msg}")

    def _load_records(self, records):
        self.fetch_btn.configure(state="normal", text="⟳ Fetch Records")
        self.all_records = records

        # Extract unique column names preserving order
        cols = []
        for rec in records:
            for k in rec.keys():
                if k not in cols:
                    cols.append(k)
        self.columns = cols

        # Update column filter dropdown
        dropdown_values = ["All Columns"] + self.columns
        self.col_dropdown.configure(values=dropdown_values)
        if self.col_var.get() not in dropdown_values:
            self.col_var.set("All Columns")

        # Configure Treeview columns
        self.tree["columns"] = self.columns
        for col in self.columns:
            self.sort_reverse[col] = False
            self.tree.heading(
                col,
                text=f"{col} ⇅",
                anchor="w",
                command=lambda c=col: self.sort_by_column(c),
            )
            self.tree.column(col, width=150, minwidth=90, anchor="w", stretch=True)

        self.apply_filters()

    # ================= COLUMN FILTERING & SORTING =================
    def apply_filters(self):
        query = self.filter_var.get().strip().lower()
        selected_col = self.col_var.get()
        match_mode = self.mode_var.get()

        if not query:
            self.filtered_records = list(self.all_records)
        else:
            results = []
            for rec in self.all_records:
                if selected_col == "All Columns":
                    values_to_check = [str(v).lower() for v in rec.values()]
                else:
                    values_to_check = [str(rec.get(selected_col, "")).lower()]

                if any(self._matches(val, query, match_mode) for val in values_to_check):
                    results.append(rec)
            self.filtered_records = results

        self._render_rows(self.filtered_records)

    @staticmethod
    def _matches(value, query, mode):
        if mode == "Equals":
            return value == query
        if mode == "Starts With":
            return value.startswith(query)
        if mode == "Ends With":
            return value.endswith(query)
        return query in value  # Default: Contains

    def clear_filters(self):
        self.col_var.set("All Columns")
        self.mode_var.set("Contains")
        self.filter_var.set("")
        self.filter_entry.focus_set()

    def sort_by_column(self, col):
        reverse = self.sort_reverse.get(col, False)

        def sort_key(rec):
            val = rec.get(col, "")
            try:
                return (0, float(val))
            except ValueError:
                return (1, str(val).lower())

        self.filtered_records.sort(key=sort_key, reverse=reverse)
        self.sort_reverse[col] = not reverse

        # Update heading arrows
        for c in self.columns:
            arrow = (" ▼" if reverse else " ▲") if c == col else " ⇅"
            self.tree.heading(c, text=f"{c}{arrow}")

        self._render_rows(self.filtered_records)

    def _render_rows(self, records):
        self.tree.delete(*self.tree.get_children())
        for idx, rec in enumerate(records):
            row_vals = [rec.get(col, "") for col in self.columns]
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert("", "end", values=row_vals, tags=(tag,))

        total = len(self.all_records)
        shown = len(records)
        self.count_label.configure(
            text=f"Showing {shown} / {total} records",
            text_color="#4ADE80" if shown > 0 else "#F87171",
        )

    def _on_row_double_click(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        detail_lines = [f"{col}: {val}" for col, val in zip(self.columns, values)]
        messagebox.showinfo("Record Details", "\n".join(detail_lines))


# Standalone launch for testing
if __name__ == "__main__":
    app = ctk.CTk()
    app.title("NEXUS HUB — API Data Table & Column Filter")
    app.geometry("1150x650")
    app.configure(fg_color=BG_MAIN)

    viewer = APITableViewer(app, api_url="https://jsonplaceholder.typicode.com/users")
    viewer.pack(fill="both", expand=True)

    app.mainloop()
