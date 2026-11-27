import colorsys as cs
import math
import subprocess as sp
import tkinter as tk
import turtle
from tkinter import messagebox
import customtkinter as ctk
from menu import main_page_menu as menu

# Match the login page theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Color Palette matching ModernLoginApp
BG_MAIN = "#0F172A"
CARD_BG = "#1E293B"
CARD_BORDER = "#334155"
HEADER_BAR = "#1E3A8A"
MENU_BAR_BG = "#172554"
CANVAS_DARK = "#0B1120"


def center_turtle_canvas(canvas, screen):
    w = canvas.winfo_width()
    h = canvas.winfo_height()
    if w > 1 and h > 1:
        screen.screensize(w, h)
        canvas.config(scrollregion=(-w // 2, -h // 2, w // 2, h // 2))


def start_pattern(screen, pen, state):
    screen.bgcolor(CANVAS_DARK)
    pen.clear()
    pen.pensize(2)
    pen.speed(0)
    pen.penup()
    pen.goto(0, 0)
    pen.setheading(0)
    pen.pendown()

    n = 100

    def step(i=0, h=0.0):
        if i >= n or not state["running"]:
            return
        try:
            c = cs.hsv_to_rgb(h, 1, 1)
            pen.pencolor(c)
            pen.forward(i * 2)
            pen.right(59)
            screen.ontimer(lambda: step(i + 1, h + 1 / n), 20)
        except tk.TclError:
            pass

    step()


def start_followers_pattern(screen, pen, state, radius=150, phase_offset=0.0):
    screen.bgcolor(CANVAS_DARK)
    screen.tracer(0)

    pen.turtlesize(2)
    pen.pensize(1)
    pen.speed(0)
    pen.hideturtle()

    local_state = {"h": phase_offset, "a": phase_offset * 5}

    def animate():
        try:
            if state["running"]:
                local_state["a"] += 0.1
                pen.clear()

                for i in range(100):
                    c = cs.hsv_to_rgb(local_state["h"] % 1.0, 1, 1)
                    pen.color(c)
                    pen.penup()
                    pen.goto(0, 0)
                    pen.pendown()
                    x = math.sin(local_state["a"] + i) * radius
                    y = math.cos(local_state["a"] + i * 2) * radius
                    pen.goto(x, y)
                    pen.dot(14)
                    local_state["h"] += 0.001

                screen.update()
                local_state["a"] += 0.05

            screen.ontimer(animate, 50)
        except tk.TclError:
            pass

    animate()


def open_wifi_tool_popup(parent):
    """Opens a sleek popup window showing saved Wi-Fi profiles & passwords."""
    win = ctk.CTkToplevel(parent)
    win.title("Saved Wi-Fi Password Viewer")
    win.geometry("460x380")
    win.configure(fg_color=BG_MAIN)
    win.grab_set()
    win.resizable(False, False)

    ctk.CTkLabel(
        win,
        text="Saved Wi-Fi Profiles",
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color="#F8FAFC",
    ).pack(pady=(15, 10))

    textbox = ctk.CTkTextbox(
        win,
        width=410,
        height=250,
        fg_color=CARD_BG,
        border_color=CARD_BORDER,
        border_width=1,
        font=ctk.CTkFont(family="Consolas", size=12),
    )
    textbox.pack(pady=5, padx=20)

    try:
        profiles = sp.check_output("netsh wlan show profiles", shell=True).decode(
            "utf-8", errors="ignore"
        )
        names = [
            line.split(":", 1)[1].strip()
            for line in profiles.splitlines()
            if "All User Profile" in line
        ]
        if not names:
            textbox.insert("end", "No saved Wi-Fi profiles found.\n")
        else:
            for name in names:
                details = sp.check_output(
                    f'netsh wlan show profile name="{name}" key=clear', shell=True
                ).decode("utf-8", errors="ignore")
                pwd = "<Open / No Password>"
                for line in details.splitlines():
                    if "Key Content" in line:
                        pwd = line.split(":", 1)[1].strip()
                        break
                textbox.insert("end", f"{name:<24} : {pwd}\n")
    except Exception as exc:
        textbox.insert("end", f"Error reading Wi-Fi profiles: {exc}\n")

    textbox.configure(state="disabled")

    ctk.CTkButton(
        win, text="Close", width=110, fg_color="#2563EB", command=win.destroy
    ).pack(pady=12)


def create_four_block_ui():
    root = ctk.CTk()
    root.title("NEXUS HUB — 4-Block Control Center")
    root.configure(fg_color=BG_MAIN)

    try:
        root.state("zoomed")
    except tk.TclError:
        root.attributes("-zoomed", True)

    app_state = {"running": True, "screens": [], "pens": [], "radius": 150}

    # ================= 1. TOP BRAND HEADER BAR =================
    top_bar = ctk.CTkFrame(root, height=48, fg_color=HEADER_BAR, corner_radius=0)
    top_bar.pack(fill="x", side="top")
    top_bar.pack_propagate(False)

    # Toggle button in top header to collapse/expand the left sidebar
    toggle_sidebar_btn = ctk.CTkButton(
        top_bar,
        text="☰",
        width=36,
        height=30,
        corner_radius=6,
        fg_color="#172554",
        hover_color="#2563EB",
        font=ctk.CTkFont(size=15, weight="bold"),
        command=menu.toggle_sidebar,
    )
    toggle_sidebar_btn.pack(side="left", padx=(12, 8))

    ctk.CTkLabel(
        top_bar,
        text="◈  NEXUS HUB  |  VISUAL ANALYTICS WORKSPACE",
        font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
        text_color="#FFFFFF",
    ).pack(side="left", padx=8)

    ctk.CTkButton(
        top_bar,
        text="Logout",
        width=90,
        height=30,
        corner_radius=8,
        fg_color="#172554",
        hover_color="#DC2626",
        border_width=1,
        border_color="#60A5FA",
        font=ctk.CTkFont(size=12, weight="bold"),
        command=menu.handle_logout,
    ).pack(side="right", padx=18)

    status_badge = ctk.CTkLabel(
        top_bar,
        text="●  LIVE ENGINE ACTIVE",
        font=ctk.CTkFont(size=12, weight="bold"),
        text_color="#4ADE80",
    )
    status_badge.pack(side="right", padx=15)

    # ================= 2. BODY CONTAINER (LEFT SIDEBAR + RIGHT GRID) =================
    body_container = ctk.CTkFrame(root, fg_color=BG_MAIN, corner_radius=0)
    body_container.pack(fill="both", expand=True)

    # Left Dynamic Menu Container (replaces top menu strip)
    left_sidebar = ctk.CTkFrame(
        body_container,
        width=220,
        fg_color=MENU_BAR_BG,
        corner_radius=0,
        border_width=1,
        border_color=CARD_BORDER,
    )
    left_sidebar.pack(side="left", fill="y")
    left_sidebar.pack_propagate(False)

    # Wire dependencies to menu module before building the sidebar
    menu.root = root
    menu.CARD_BG = CARD_BG
    menu.status_badge = status_badge
    menu.app_state = app_state
    menu.start_pattern = start_pattern
    menu.open_wifi_tool_popup = open_wifi_tool_popup
    menu.create_left_sidebar_menu(sidebar_container=left_sidebar)

    # ================= 3. MAIN 2x2 GRID CONTAINER =================
    grid_container = ctk.CTkFrame(body_container, fg_color=BG_MAIN, corner_radius=0)
    grid_container.pack(side="left", fill="both", expand=True, padx=12, pady=12)

    grid_container.grid_rowconfigure(0, weight=1)
    grid_container.grid_rowconfigure(1, weight=1)
    grid_container.grid_columnconfigure(0, weight=1)
    grid_container.grid_columnconfigure(1, weight=1)

    def make_modern_block(row, col, title_text, badge_text, badge_color):
        card = ctk.CTkFrame(
            grid_container,
            fg_color=CARD_BG,
            corner_radius=16,
            border_width=1,
            border_color=CARD_BORDER,
        )
        card.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)

        card_header = ctk.CTkFrame(card, fg_color="transparent", height=34)
        card_header.pack(fill="x", padx=14, pady=(8, 4))

        ctk.CTkLabel(
            card_header,
            text=title_text,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#F8FAFC",
        ).pack(side="left")

        ctk.CTkLabel(
            card_header,
            text=badge_text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=badge_color,
        ).pack(side="right")

        canvas_holder = tk.Frame(card, bg=CANVAS_DARK, bd=0)
        canvas_holder.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        c = tk.Canvas(canvas_holder, bg=CANVAS_DARK, highlightthickness=0)
        c.pack(fill="both", expand=True)
        return c

    canvas1 = make_modern_block(0, 0, "01 // SPIRAL GEOMETRY", "● STATIC RENDER", "#60A5FA")
    canvas2 = make_modern_block(0, 1, "02 // HARMONIC ORBIT A", "● LIVE 20 FPS", "#4ADE80")
    canvas3 = make_modern_block(1, 0, "03 // HARMONIC ORBIT B", "● PHASE +0.33", "#C084FC")
    canvas4 = make_modern_block(1, 1, "04 // HARMONIC ORBIT C", "● PHASE +0.66", "#F472B6")

    def init_and_draw():
        root.update()

        canvases = [canvas1, canvas2, canvas3, canvas4]
        screens = []
        pens = []

        for c in canvases:
            s = turtle.TurtleScreen(c)
            center_turtle_canvas(c, s)
            c.bind("<Configure>", lambda e, cv=c, sc=s: center_turtle_canvas(cv, sc))
            p = turtle.RawTurtle(s)
            screens.append(s)
            pens.append(p)

        block_radius = min(canvas2.winfo_width(), canvas2.winfo_height()) * 0.38
        app_state["screens"] = screens
        app_state["pens"] = pens
        app_state["radius"] = block_radius

        start_pattern(screens[0], pens[0], app_state)
        start_followers_pattern(screens[1], pens[1], app_state, radius=block_radius, phase_offset=0.0)
        start_followers_pattern(screens[2], pens[2], app_state, radius=block_radius, phase_offset=0.33)
        start_followers_pattern(screens[3], pens[3], app_state, radius=block_radius, phase_offset=0.66)

    root.after(150, init_and_draw)
    root.mainloop()

