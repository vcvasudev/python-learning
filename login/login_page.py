import math
import tkinter as tk
import customtkinter as ctk
from login import sso_auth
import main_screen as ms

# Configure global modern theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ModernLoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Modern Login Portal")
        self.geometry("850x520")
        self.resizable(False, False)

        # Configure 2-column split layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ================= LEFT PANEL (Branding & Animated Welcome) =================
        self.left_frame = ctk.CTkFrame(
            self, fg_color="#1E3A8A", corner_radius=0
        )
        self.left_frame.grid(row=0, column=0, sticky="nsew")

        # Animated canvas graphic with Welcome sign
        self.art_canvas = tk.Canvas(
            self.left_frame, width=300, height=230, bg="#1E3A8A", highlightthickness=0
        )
        self.art_canvas.pack(pady=(45, 10))

        # Animation state variables
        self.angle_offset = 0.0
        self.pulse_phase = 0.0
        self.welcome_full_text = "WELCOME"
        self.welcome_char_index = 0
        self.animate_welcome_emblem()

        self.brand_title = ctk.CTkLabel(
            self.left_frame,
            text="NEXUS HUB",
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color="#FFFFFF",
        )
        self.brand_title.pack(pady=(5, 5))

        self.brand_subtitle = ctk.CTkLabel(
            self.left_frame,
            text="Secure Workspace & Analytics Dashboard\nSign in to launch your 4-block control center.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#BFDBFE",
            justify="center",
        )
        self.brand_subtitle.pack(pady=(0, 20), padx=20)

        # ================= RIGHT PANEL (Login Form Card) =================
        self.right_frame = ctk.CTkFrame(
            self, fg_color="#0F172A", corner_radius=0
        )
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        self.form_card = ctk.CTkFrame(
            self.right_frame,
            fg_color="#1E293B",
            corner_radius=18,
            border_width=1,
            border_color="#334155",
        )
        self.form_card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.82, relheight=0.84)

        self.welcome_label = ctk.CTkLabel(
            self.form_card,
            text="Welcome Back",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color="#F8FAFC",
        )
        self.welcome_label.pack(pady=(30, 2))

        self.sub_label = ctk.CTkLabel(
            self.form_card,
            text="Enter your credentials to continue",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#94A3B8",
        )
        self.sub_label.pack(pady=(0, 22))

        # Username Field
        self.username_entry = ctk.CTkEntry(
            self.form_card,
            placeholder_text="Username or Email",
            width=260,
            height=42,
            corner_radius=10,
            border_width=1,
            fg_color="#0F172A",
            border_color="#334155",
            font=ctk.CTkFont(size=13),
        )
        self.username_entry.pack(pady=(0, 14))

        # Password Field
        self.password_entry = ctk.CTkEntry(
            self.form_card,
            placeholder_text="Password",
            show="•",
            width=260,
            height=42,
            corner_radius=10,
            border_width=1,
            fg_color="#0F172A",
            border_color="#334155",
            font=ctk.CTkFont(size=13),
        )
        self.password_entry.pack(pady=(0, 10))

        # Options Row (Show Password)
        self.options_frame = ctk.CTkFrame(self.form_card, fg_color="transparent", width=260)
        self.options_frame.pack(pady=(0, 18))

        self.show_pass_var = ctk.BooleanVar(value=False)
        self.show_pass_cb = ctk.CTkCheckBox(
            self.options_frame,
            text="Show Password",
            variable=self.show_pass_var,
            command=self.toggle_password,
            font=ctk.CTkFont(size=12),
            checkbox_width=18,
            checkbox_height=18,
            corner_radius=5,
        )
        self.show_pass_cb.pack(side="left")

        # Status / Error Message Label
        self.status_label = ctk.CTkLabel(
            self.form_card,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#F87171",
            wraplength=260,
        )
        self.status_label.pack(pady=(0, 8))

        # Login Button
        self.login_btn = ctk.CTkButton(
            self.form_card,
            text="SIGN IN",
            width=260,
            height=44,
            corner_radius=10,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.handle_login,
        )
        self.login_btn.pack(pady=(0, 15))
        # --- SSO Divider ---

        self.sso_divider = ctk.CTkLabel(
            self.form_card,
            text="────────  OR CONTINUE WITH  ────────",
            font=ctk.CTkFont(size=11),
            text_color="#64748B",
        )
        self.sso_divider.pack(pady=(0, 12))

        # SSO Buttons Frame
        self.sso_frame = ctk.CTkFrame(self.form_card, fg_color="transparent", width=260)
        self.sso_frame.pack(pady=(0, 10))

        # Google Button
        ctk.CTkButton(
            self.sso_frame,
            text="G",
            width=36,
            height=36,
            corner_radius=8,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self.handle_sso_login("google"),
        ).pack(side="left", padx=4)

        # Facebook Button
        ctk.CTkButton(
            self.sso_frame,
            text="F",
            width=36,
            height=36,
            corner_radius=8,
            fg_color="#1D4ED8",
            hover_color="#1E40AF",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self.handle_sso_login("facebook"),
        ).pack(side="left", padx=4)

        # X / Twitter Button
        ctk.CTkButton(
            self.sso_frame,
            text="X",
            width=36,
            height=36,
            corner_radius=8,
            fg_color="#0F172A",
            hover_color="#334155",
            border_width=1,
            border_color="#475569",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self.handle_sso_login("twitter"),
        ).pack(side="left", padx=4)

        # Allow pressing Enter key to submit
        self.bind("<Return>", lambda event: self.handle_login())

    def animate_welcome_emblem(self):
        """Animates rotating rays, a pulsing glow ring, and typing WELCOME text."""
        if not self.winfo_exists():
            return

        self.art_canvas.delete("all")
        cx, cy = 150, 115

        # 1. Smoothly rotating outer starburst pattern
        for base_deg in range(0, 360, 15):
            rad = math.radians(base_deg + self.angle_offset)
            is_major = (base_deg % 30 == 0)
            inner_r = 70 if is_major else 78
            outer_r = 98 if is_major else 88
            color = "#60A5FA" if is_major else "#3B82F6"

            x1 = cx + math.cos(rad) * inner_r
            y1 = cy + math.sin(rad) * inner_r
            x2 = cx + math.cos(rad) * outer_r
            y2 = cy + math.sin(rad) * outer_r
            self.art_canvas.create_line(x1, y1, x2, y2, fill=color, width=2, capstyle="round")

        # 2. Pulsing outer halo ring
        pulse_r = 65 + math.sin(self.pulse_phase) * 3
        self.art_canvas.create_oval(
            cx - pulse_r, cy - pulse_r, cx + pulse_r, cy + pulse_r,
            fill="#172554", outline="#60A5FA", width=2
        )

        # 3. Counter-rotating inner dashed ring
        inner_ring_r = 56
        self.art_canvas.create_oval(
            cx - inner_ring_r, cy - inner_ring_r, cx + inner_ring_r, cy + inner_ring_r,
            outline="#93C5FD", width=1, dash=(4, 4)
        )

        # 4. Typewriter reveal + gentle floating bounce for "WELCOME"
        visible_chars = int(self.welcome_char_index)
        shown_text = self.welcome_full_text[:visible_chars]
        float_y = cy - 8 + math.sin(self.pulse_phase * 1.5) * 2.5

        self.art_canvas.create_text(
            cx, float_y,
            text=shown_text,
            fill="#FFFFFF",
            font=("Segoe UI", 15, "bold"),
        )

        # Animated twinkling stars below WELCOME
        star_colors = ["#60A5FA", "#93C5FD", "#FFFFFF"]
        shift = int(self.pulse_phase * 2) % 3
        for idx, offset_x in enumerate([-24, 0, 24]):
            c = star_colors[(idx + shift) % 3]
            self.art_canvas.create_text(
                cx + offset_x, cy + 16,
                text="★",
                fill=c,
                font=("Segoe UI", 11),
            )

        # Advance animation counters
        self.angle_offset = (self.angle_offset + 1.2) % 360
        self.pulse_phase += 0.12
        if self.welcome_char_index < len(self.welcome_full_text):
            self.welcome_char_index += 0.25  # Types one letter every ~4 frames

        # Refresh at ~30 FPS
        self.after(33, self.animate_welcome_emblem)

    def toggle_password(self):
        if self.show_pass_var.get():
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="•")

    def handle_sso_login(self, provider_name):
        user_info =sso_auth.start_sso_login(provider_name)
        print(user_info)
        if user_info:
            self.status_label.configure(
                text="Login Successful! Opening dashboard...", text_color="#4ADE80"
            )
            self.after(800, self.open_main_dashboard)

    def handle_login(self):
        user = self.username_entry.get().strip()
        pwd = self.password_entry.get().strip()

        if user == "admin" and pwd == "1234":
            self.status_label.configure(
                text="Login Successful! Opening dashboard...", text_color="#4ADE80"
            )
            self.after(800, self.open_main_dashboard)
        else:
            self.status_label.configure(
                text="Invalid username or password (try admin / 1234)",
                text_color="#F87171",
            )

    def open_main_dashboard(self):
        self.destroy()
        ms.create_four_block_ui()

if __name__ == "__main__":
    app = ModernLoginApp()
    app.mainloop()
