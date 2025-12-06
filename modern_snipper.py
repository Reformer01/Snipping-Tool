import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageGrab, ImageDraw, ImageFont
import io
from datetime import datetime
import time

# Import win32clipboard with error handling
try:
    import win32clipboard  # type: ignore[import-untyped]  # Part of pywin32, installed via pip
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    print("Warning: pywin32 not installed. Clipboard functionality will be disabled.")
    print("Install with: pip install pywin32")

# Import pygetwindow for window capture
try:
    import pygetwindow as gw  # type: ignore[import-untyped]
    PYGETWINDOW_AVAILABLE = True
except ImportError:
    PYGETWINDOW_AVAILABLE = False
    print("Warning: pygetwindow not installed. Window Snip will be disabled.")
    print("Install with: pip install pygetwindow")

# Import pytesseract for OCR text extraction
try:
    import pytesseract  # type: ignore[import-untyped]
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False
    print("Warning: pytesseract not installed. OCR text extraction will be disabled.")
    print("Install with: pip install pytesseract")
    print("Also install Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki")

# Configuration for the Modern UI
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class SnippingTool(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Main Window Setup ---
        self.title("Clippr")
        self.geometry("380x380")
        self.resizable(False, False)
        self.attributes('-topmost', True)  # Keep the tool floating above others

        # --- UI Components ---
        self.grid_columnconfigure(0, weight=1)
        
        # Header Section
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        
        self.lbl_title = ctk.CTkLabel(
            header_frame,
            text="Clippr",
            font=("Roboto Medium", 28),
            text_color="#E63946"
        )
        self.lbl_title.grid(row=0, column=0)
        
        subtitle = ctk.CTkLabel(
            header_frame,
            text="Professional Snipping Tool",
            font=("Roboto", 10),
            text_color="gray"
        )
        subtitle.grid(row=1, column=0, pady=(5, 0))

        # Settings Section
        settings_frame = ctk.CTkFrame(self)
        settings_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        settings_frame.grid_columnconfigure(1, weight=1)

        # Snip Type Selection
        snip_label = ctk.CTkLabel(settings_frame, text="Snip Type:", font=("Roboto", 11, "bold"))
        snip_label.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))
        
        self.snip_type_var = ctk.StringVar(value="Rectangular")
        self.snip_type_menu = ctk.CTkOptionMenu(
            settings_frame,
            values=["Rectangular", "Window", "Fullscreen"],
            variable=self.snip_type_var,
            width=200,
            font=("Roboto", 11)
        )
        self.snip_type_menu.grid(row=0, column=1, sticky="ew", padx=(0, 15), pady=(15, 5))
        
        # Window snip availability indicator
        if not PYGETWINDOW_AVAILABLE:
            window_status = ctk.CTkLabel(
                settings_frame,
                text="⚠ Window Snip unavailable",
                font=("Roboto", 8),
                text_color="#FCBF49"
            )
            window_status.grid(row=0, column=2, padx=(5, 15), pady=(15, 5))

        # Timer Dropdown
        timer_label = ctk.CTkLabel(settings_frame, text="Delay Timer:", font=("Roboto", 11, "bold"))
        timer_label.grid(row=1, column=0, sticky="w", padx=15, pady=5)
        
        self.timer_var = ctk.StringVar(value="No Delay")
        self.timer_menu = ctk.CTkOptionMenu(
            settings_frame,
            values=["No Delay", "3 Seconds", "5 Seconds", "10 Seconds"],
            variable=self.timer_var,
            width=200,
            font=("Roboto", 11)
        )
        self.timer_menu.grid(row=1, column=1, sticky="ew", padx=(0, 15), pady=5)

        # Auto-Copy Checkbox
        self.auto_copy_var = ctk.BooleanVar(value=True)
        self.auto_copy_cb = ctk.CTkCheckBox(
            settings_frame,
            text="Auto-Copy to Clipboard",
            variable=self.auto_copy_var,
            font=("Roboto", 11)
        )
        self.auto_copy_cb.grid(row=2, column=0, columnspan=2, sticky="w", padx=15, pady=(5, 15))

        # Main Action Button
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        action_frame.grid_columnconfigure(0, weight=1)
        
        self.btn_snip = ctk.CTkButton(
            action_frame,
            text="🖼️ NEW SNIP",
            height=45,
            fg_color="#E63946",
            hover_color="#D62828",
            font=("Roboto", 15, "bold"),
            command=self.start_snip,
            corner_radius=10
        )
        self.btn_snip.grid(row=0, column=0, sticky="ew")
        
        # Bind Enter key for quick snip
        self.bind("<Return>", lambda e: self.start_snip())
        self.btn_snip.bind("<Return>", lambda e: self.start_snip())

        # Status Section
        status_frame = ctk.CTkFrame(self, fg_color="transparent")
        status_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 10))
        status_frame.grid_columnconfigure(0, weight=1)
        
        self.lbl_status = ctk.CTkLabel(
            status_frame,
            text="Ready",
            text_color="#2a9d8f",
            font=("Roboto", 10, "bold")
        )
        self.lbl_status.grid(row=0, column=0)
        
        # Feature Status Indicators
        features_frame = ctk.CTkFrame(self, fg_color="transparent")
        features_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 15))
        
        feature_statuses = []
        if WIN32_AVAILABLE:
            feature_statuses.append("✓ Clipboard")
        else:
            feature_statuses.append("✗ Clipboard")
            
        if PYGETWINDOW_AVAILABLE:
            feature_statuses.append("✓ Window Snip")
        else:
            feature_statuses.append("✗ Window Snip")
            
        if PYTESSERACT_AVAILABLE:
            feature_statuses.append("✓ OCR")
        else:
            feature_statuses.append("✗ OCR")
        
        status_text = " | ".join(feature_statuses)
        features_label = ctk.CTkLabel(
            features_frame,
            text=status_text,
            font=("Roboto", 8),
            text_color="gray"
        )
        features_label.pack()

        # --- State Variables ---
        self.start_x = 0
        self.start_y = 0
        self.rect = None
        self.snip_surface = None
        self.original_image = None
        self.snip_mode = "rectangular"
        self.timer_countdown_id = None
        self.current_image = None

    def start_snip(self):
        """Starts the snipping process with optional delay."""
        snip_type = self.snip_type_var.get()
        timer_value = self.timer_var.get()
        
        # Map timer values to milliseconds
        delay_map = {"No Delay": 0, "3 Seconds": 3000, "5 Seconds": 5000, "10 Seconds": 10000}
        delay_ms = delay_map[timer_value]
        
        self.snip_mode = snip_type.lower()
        
        if delay_ms > 0:
            self.lbl_status.configure(
                text=f"Snipping in {delay_ms//1000} seconds...",
                text_color="#E9C46A"
            )
            self.withdraw()
            self.countdown_timer(delay_ms // 1000)
        else:
            self.withdraw()
            self.after(200, self.execute_snip)

    def countdown_timer(self, seconds):
        """Shows countdown in status before snipping."""
        if seconds > 0:
            # Create a temporary visible window for countdown
            countdown_window = ctk.CTkToplevel(self)
            countdown_window.title("Snip Countdown")
            countdown_window.geometry("300x150")
            countdown_window.attributes('-topmost', True)
            countdown_window.resizable(False, False)
            
            countdown_label = ctk.CTkLabel(
                countdown_window,
                text=f"Snipping in {seconds}...",
                font=("Roboto", 24, "bold"),
                text_color="#E9C46A"
            )
            countdown_label.pack(expand=True)
            
            def update_countdown():
                nonlocal seconds
                seconds -= 1
                if seconds > 0:
                    countdown_label.configure(text=f"Snipping in {seconds}...")
                    countdown_window.after(1000, update_countdown)
                else:
                    countdown_window.destroy()
                    self.after(200, self.execute_snip)
            
            countdown_window.after(1000, update_countdown)
        else:
            self.after(200, self.execute_snip)

    def execute_snip(self):
        """Executes the appropriate snip type."""
        if self.snip_mode == "fullscreen":
            self.take_fullscreen_snip()
        elif self.snip_mode == "window":
            self.take_window_snip()
        else:  # rectangular
            self.take_rectangular_snip()

    def take_fullscreen_snip(self):
        """Captures the entire screen instantly."""
        self.original_image = ImageGrab.grab()
        self.process_snapped_image(self.original_image)

    def take_window_snip(self):
        """Captures the active window."""
        if not PYGETWINDOW_AVAILABLE:
            messagebox.showerror(
                "Error",
                "pygetwindow is not installed.\n\n"
                "Install it with: pip install pygetwindow\n"
                "Then restart the application."
            )
            self.deiconify()
            return
        
        try:
            # Get the active window
            time.sleep(0.3)  # Small delay to ensure window focus
            active_window = gw.getActiveWindow()
            
            if active_window is None:
                messagebox.showwarning("Warning", "No active window found.")
                self.deiconify()
                return
            
            # Get window coordinates
            left, top, width, height = active_window.left, active_window.top, active_window.width, active_window.height
            
            # Capture the window region
            self.original_image = ImageGrab.grab(bbox=(left, top, left + width, top + height))
            self.process_snapped_image(self.original_image)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to capture window:\n{str(e)}")
            self.deiconify()

    def take_rectangular_snip(self):
        """Captures the screen and opens the selection overlay."""
        # 1. Grab the whole screen
        self.original_image = ImageGrab.grab()
        
        # 2. Create the overlay window
        self.snip_surface = tk.Toplevel(self)
        self.snip_surface.attributes("-fullscreen", True)
        self.snip_surface.attributes("-topmost", True)
        
        # 3. Put the screenshot on a canvas
        self.canvas = tk.Canvas(self.snip_surface, cursor="cross", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Convert PIL image to Tkinter format to display on canvas
        self.tk_image = ImageTk.PhotoImage(self.original_image)
        self.canvas.create_image(0, 0, image=self.tk_image, anchor="nw")
        
        # 4. Bind events
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)
        self.canvas.bind("<Escape>", lambda e: [self.snip_surface.destroy(), self.deiconify()])

    def on_mouse_down(self, event):
        """Handles mouse button press for rectangular selection."""
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        # Create a selection rectangle (Red outline)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="#E63946", width=3
        )

    def on_mouse_drag(self, event):
        """Handles mouse drag for rectangular selection."""
        cur_x, cur_y = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_mouse_release(self, event):
        """Handles mouse release for rectangular selection."""
        cur_x, cur_y = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        
        # Calculate coordinates ensuring x1 < x2
        x1, x2 = sorted([self.start_x, cur_x])
        y1, y2 = sorted([self.start_y, cur_y])

        # Destroy overlay
        self.snip_surface.destroy()
        
        # Crop logic
        if x2 - x1 > 5 and y2 - y1 > 5:  # Avoid accidental tiny clicks
            cropped = self.original_image.crop((x1, y1, x2, y2))
            self.process_snapped_image(cropped)
        else:
            self.deiconify()  # Just bring back main window if cancelled

    def process_snapped_image(self, image):
        """Processes the captured image - auto-copy if enabled, then show editor."""
        self.current_image = image.copy()
        
        # Auto-copy if enabled
        if self.auto_copy_var.get():
            self.copy_to_clipboard(image, silent=True)
        
        # Show editor window
        self.show_editor_window(image)

    def show_editor_window(self, image):
        """Opens the editor window with drawing tools, shapes, and crop."""
        editor = ctk.CTkToplevel(self)
        editor.title("Snip Editor - Clippr")
        editor.geometry("1000x750")
        editor.attributes('-topmost', True)
        
        # Store image reference
        editor.original_image = image.copy()
        editor.current_image = image.copy()
        editor.draw_image = image.copy()
        editor.tool = "pen"
        editor.pen_color = "#E63946"
        editor.pen_width = 3
        editor.drawing = False
        editor.start_x = 0
        editor.start_y = 0
        editor.shapes = []
        editor.current_shape = None
        editor.tool_buttons = {}  # Store tool buttons for highlighting
        
        # Calculate display size
        max_width, max_height = 800, 500
        img_width, img_height = image.size
        
        if img_width > max_width or img_height > max_height:
            ratio = min(max_width / img_width, max_height / img_height)
            display_size = (int(img_width * ratio), int(img_height * ratio))
            display_image = image.resize(display_size, Image.Resampling.LANCZOS)
        else:
            display_image = image
            display_size = (img_width, img_height)
        
        editor.display_size = display_size
        editor.scale_x = img_width / display_size[0]
        editor.scale_y = img_height / display_size[1]
        
        # Toolbar Frame
        toolbar = ctk.CTkFrame(editor)
        toolbar.pack(fill="x", padx=15, pady=(15, 10))
        toolbar.grid_columnconfigure(1, weight=1)
        
        # Left side - Drawing Tools Section
        drawing_section = ctk.CTkFrame(toolbar, fg_color="transparent")
        drawing_section.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        
        tools_label = ctk.CTkLabel(
            drawing_section,
            text="Drawing Tools:",
            font=("Roboto", 11, "bold")
        )
        tools_label.grid(row=0, column=0, columnspan=6, sticky="w", pady=(0, 8))
        
        def create_tool_button(parent, tool_name, text, row, col):
            """Helper to create tool buttons with proper highlighting."""
            btn = ctk.CTkButton(
                parent,
                text=text,
                width=75,
                height=32,
                font=("Roboto", 10),
                command=lambda: self.set_tool(editor, tool_name),
                fg_color=("#E63946" if editor.tool == tool_name else "#2b2b2b"),
                hover_color=("#D62828" if editor.tool == tool_name else "#3a3a3a")
            )
            btn.grid(row=row, column=col, padx=3, pady=2)
            editor.tool_buttons[tool_name] = btn
            return btn
        
        # Drawing tools row
        create_tool_button(drawing_section, "pen", "✏️ Pen", 1, 0)
        create_tool_button(drawing_section, "highlighter", "🖍️ Highlighter", 1, 1)
        
        # Shape tools row
        create_tool_button(drawing_section, "arrow", "➡️ Arrow", 1, 2)
        create_tool_button(drawing_section, "rectangle", "▭ Rectangle", 1, 3)
        create_tool_button(drawing_section, "circle", "○ Circle", 1, 4)
        create_tool_button(drawing_section, "crop", "✂️ Crop", 1, 5)
        
        # Right side - Color Selection
        color_section = ctk.CTkFrame(toolbar, fg_color="transparent")
        color_section.grid(row=0, column=1, sticky="e", padx=10, pady=10)
        
        color_label = ctk.CTkLabel(
            color_section,
            text="Color:",
            font=("Roboto", 11, "bold")
        )
        color_label.pack(side="left", padx=(0, 8))
        
        colors = ["#E63946", "#F77F00", "#FCBF49", "#2a9d8f", "#264653", "#000000", "#FFFFFF"]
        editor.color_buttons = []
        editor.color_list = colors  # Store for later use
        for color in colors:
            btn_color = ctk.CTkButton(
                color_section,
                text="",
                width=28,
                height=28,
                fg_color=color,
                hover_color=color,
                command=lambda c=color: self.set_color(editor, c),
                corner_radius=14,
                border_width=2 if color == editor.pen_color else 0,
                border_color="#FFFFFF" if color in ["#000000", "#264653"] else "#000000"
            )
            btn_color.pack(side="left", padx=3)
            editor.color_buttons.append(btn_color)
        
        # Update color indicators
        self.update_color_indicator(editor)
        
        # Canvas for drawing with status bar
        canvas_container = ctk.CTkFrame(editor)
        canvas_container.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        canvas_frame = ctk.CTkFrame(canvas_container)
        canvas_frame.pack(fill="both", expand=True)
        
        editor.canvas = tk.Canvas(
            canvas_frame,
            width=display_size[0],
            height=display_size[1],
            bg="#1a1a1a",
            highlightthickness=0
        )
        editor.canvas.pack(expand=True, fill="both")
        
        # Status bar showing tool and dimensions
        status_bar = ctk.CTkFrame(canvas_container, height=25, fg_color="#2b2b2b")
        status_bar.pack(fill="x", pady=(5, 0))
        status_bar.pack_propagate(False)
        
        editor.status_label = ctk.CTkLabel(
            status_bar,
            text=f"Tool: {editor.tool.title()} | Color: {editor.pen_color} | Size: {image.size[0]}x{image.size[1]}",
            font=("Roboto", 9),
            text_color="gray"
        )
        editor.status_label.pack(side="left", padx=10)
        
        # Display image on canvas
        editor.tk_image = ImageTk.PhotoImage(display_image)
        editor.canvas.create_image(0, 0, image=editor.tk_image, anchor="nw")
        editor.canvas.image_ref = editor.tk_image
        
        # Bind canvas events
        editor.canvas.bind("<ButtonPress-1>", lambda e: self.on_editor_mouse_down(e, editor))
        editor.canvas.bind("<B1-Motion>", lambda e: self.on_editor_mouse_drag(e, editor))
        editor.canvas.bind("<ButtonRelease-1>", lambda e: self.on_editor_mouse_up(e, editor))
        
        # Action Buttons Frame
        btn_frame = ctk.CTkFrame(editor)
        btn_frame.pack(fill="x", padx=15, pady=10)
        btn_frame.grid_columnconfigure(0, weight=1)
        
        # Left side - Advanced Actions
        left_actions = ctk.CTkFrame(btn_frame, fg_color="transparent")
        left_actions.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        
        if PYTESSERACT_AVAILABLE:
            btn_extract_text = ctk.CTkButton(
                left_actions,
                text="🔍 Extract Text (OCR)",
                command=lambda: self.extract_text_from_image(editor.draw_image, editor=editor),
                fg_color="#2a9d8f",
                hover_color="#1e7d72",
                font=("Roboto", 11),
                width=160,
                height=35
            )
            btn_extract_text.pack(side="left", padx=(0, 8))
        else:
            btn_extract_text_disabled = ctk.CTkButton(
                left_actions,
                text="🔍 Extract Text (OCR) - Unavailable",
                fg_color="gray",
                state="disabled",
                font=("Roboto", 11),
                width=240,
                height=35
            )
            btn_extract_text_disabled.pack(side="left", padx=(0, 8))
        
        btn_copy = ctk.CTkButton(
            left_actions,
            text="📋 Copy Image",
            command=lambda: self.copy_to_clipboard(editor.draw_image, editor=editor),
            font=("Roboto", 11),
            width=120,
            height=35
        )
        btn_copy.pack(side="left", padx=(0, 8))
        
        btn_save = ctk.CTkButton(
            left_actions,
            text="💾 Save to File",
            command=lambda: self.save_to_file(editor.draw_image, editor=editor),
            font=("Roboto", 11),
            width=120,
            height=35
        )
        btn_save.pack(side="left")
        
        # Right side - Close button
        right_actions = ctk.CTkFrame(btn_frame, fg_color="transparent")
        right_actions.grid(row=0, column=1, sticky="e", padx=10, pady=10)
        
        btn_close = ctk.CTkButton(
            right_actions,
            text="✖ Close",
            fg_color="gray",
            hover_color="#5a5a5a",
            command=lambda: [editor.destroy(), self.deiconify()],
            font=("Roboto", 11),
            width=100,
            height=35
        )
        btn_close.pack(side="right")
        
        # Bind keyboard shortcuts
        editor.bind("<Control-s>", lambda e: self.save_to_file(editor.draw_image, editor=editor))
        editor.bind("<Control-c>", lambda e: self.copy_to_clipboard(editor.draw_image, editor=editor))
        editor.bind("<Escape>", lambda e: [editor.destroy(), self.deiconify()])

    def set_tool(self, editor, tool_name):
        """Sets the active tool and updates button highlighting."""
        editor.tool = tool_name
        # Update all tool button colors
        for tool, btn in editor.tool_buttons.items():
            if tool == tool_name:
                btn.configure(fg_color="#E63946", hover_color="#D62828")
            else:
                btn.configure(fg_color="#2b2b2b", hover_color="#3a3a3a")
        # Update status bar
        if hasattr(editor, 'status_label'):
            img_size = editor.draw_image.size
            editor.status_label.configure(
                text=f"Tool: {tool_name.title()} | Color: {editor.pen_color} | Size: {img_size[0]}x{img_size[1]}"
            )
    
    def set_color(self, editor, color):
        """Sets the pen color and updates indicator."""
        editor.pen_color = color
        self.update_color_indicator(editor)
        # Update status bar
        if hasattr(editor, 'status_label'):
            img_size = editor.draw_image.size
            editor.status_label.configure(
                text=f"Tool: {editor.tool.title()} | Color: {color} | Size: {img_size[0]}x{img_size[1]}"
            )
    
    def update_color_indicator(self, editor):
        """Updates visual indicator for selected color."""
        if hasattr(editor, 'color_buttons') and editor.color_buttons:
            colors = getattr(editor, 'color_list', ["#E63946", "#F77F00", "#FCBF49", "#2a9d8f", "#264653", "#000000", "#FFFFFF"])
            for btn, color in zip(editor.color_buttons, colors):
                if color == editor.pen_color:
                    # Highlight selected color with border
                    border_color = "#FFFFFF" if color in ["#000000", "#264653"] else "#000000"
                    btn.configure(border_width=2, border_color=border_color)
                else:
                    btn.configure(border_width=0)

    def on_editor_mouse_down(self, event, editor):
        """Handles mouse down in editor."""
        editor.drawing = True
        editor.start_x = event.x
        editor.start_y = event.y
        
        if editor.tool == "pen" or editor.tool == "highlighter":
            # Start drawing path
            editor.last_x = event.x
            editor.last_y = event.y
        elif editor.tool in ["arrow", "rectangle", "circle", "crop"]:
            # Start shape selection
            pass

    def on_editor_mouse_drag(self, event, editor):
        """Handles mouse drag in editor."""
        if not editor.drawing:
            return
        
        if editor.tool == "pen" or editor.tool == "highlighter":
            # Draw line segment
            width = editor.pen_width if editor.tool == "pen" else 20
            opacity = 255 if editor.tool == "pen" else 128
            
            # Convert hex to RGB
            color_hex = editor.pen_color.lstrip('#')
            color_rgb = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
            
            # Draw on PIL image
            draw = ImageDraw.Draw(editor.draw_image, 'RGBA')
            start_coords = (
                int(editor.last_x * editor.scale_x),
                int(editor.last_y * editor.scale_y)
            )
            end_coords = (
                int(event.x * editor.scale_x),
                int(event.y * editor.scale_y)
            )
            
            if editor.tool == "highlighter":
                draw.line(
                    [start_coords, end_coords],
                    fill=(*color_rgb, opacity),
                    width=int(width * editor.scale_x)
                )
            else:
                draw.line(
                    [start_coords, end_coords],
                    fill=(*color_rgb, 255),
                    width=int(width * editor.scale_x)
                )
            
            # Update canvas display
            display_img = editor.draw_image.resize(editor.display_size, Image.Resampling.LANCZOS)
            editor.tk_image = ImageTk.PhotoImage(display_img)
            editor.canvas.create_image(0, 0, image=editor.tk_image, anchor="nw")
            editor.canvas.image_ref = editor.tk_image
            
            editor.last_x = event.x
            editor.last_y = event.y
            
        elif editor.tool in ["arrow", "rectangle", "circle", "crop"]:
            # Update shape preview
            if editor.current_shape:
                editor.canvas.delete(editor.current_shape)
            
            color = editor.pen_color if editor.tool != "crop" else "#E63946"
            
            if editor.tool == "arrow":
                # Simple arrow as line with arrowhead
                editor.current_shape = editor.canvas.create_line(
                    editor.start_x, editor.start_y, event.x, event.y,
                    fill=color, width=3, arrow=tk.LAST
                )
            elif editor.tool == "rectangle":
                editor.current_shape = editor.canvas.create_rectangle(
                    editor.start_x, editor.start_y, event.x, event.y,
                    outline=color, width=3
                )
            elif editor.tool == "circle":
                editor.current_shape = editor.canvas.create_oval(
                    editor.start_x, editor.start_y, event.x, event.y,
                    outline=color, width=3
                )
            elif editor.tool == "crop":
                editor.current_shape = editor.canvas.create_rectangle(
                    editor.start_x, editor.start_y, event.x, event.y,
                    outline=color, width=2, dash=(5, 5)
                )

    def on_editor_mouse_up(self, event, editor):
        """Handles mouse up in editor."""
        if not editor.drawing:
            return
        
        editor.drawing = False
        
        if editor.tool in ["arrow", "rectangle", "circle"]:
            # Draw shape on PIL image
            draw = ImageDraw.Draw(editor.draw_image, 'RGBA')
            color_hex = editor.pen_color.lstrip('#')
            color_rgb = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
            
            x1 = int(editor.start_x * editor.scale_x)
            y1 = int(editor.start_y * editor.scale_y)
            x2 = int(event.x * editor.scale_x)
            y2 = int(event.y * editor.scale_y)
            
            if editor.tool == "arrow":
                # Draw arrow line
                draw.line([(x1, y1), (x2, y2)], fill=(*color_rgb, 255), width=int(3 * editor.scale_x))
                # Simple arrowhead
                arrow_size = 10
                import math
                angle = math.atan2(y2 - y1, x2 - x1)
                arrow_x1 = x2 - arrow_size * math.cos(angle - math.pi/6)
                arrow_y1 = y2 - arrow_size * math.sin(angle - math.pi/6)
                arrow_x2 = x2 - arrow_size * math.cos(angle + math.pi/6)
                arrow_y2 = y2 - arrow_size * math.sin(angle + math.pi/6)
                draw.polygon([(x2, y2), (int(arrow_x1), int(arrow_y1)), (int(arrow_x2), int(arrow_y2))],
                            fill=(*color_rgb, 255))
            elif editor.tool == "rectangle":
                draw.rectangle([x1, y1, x2, y2], outline=(*color_rgb, 255), width=int(3 * editor.scale_x))
            elif editor.tool == "circle":
                draw.ellipse([x1, y1, x2, y2], outline=(*color_rgb, 255), width=int(3 * editor.scale_x))
            
            # Update canvas
            display_img = editor.draw_image.resize(editor.display_size, Image.Resampling.LANCZOS)
            editor.tk_image = ImageTk.PhotoImage(display_img)
            editor.canvas.create_image(0, 0, image=editor.tk_image, anchor="nw")
            editor.canvas.image_ref = editor.tk_image
            
            if editor.current_shape:
                editor.canvas.delete(editor.current_shape)
                editor.current_shape = None
                
        elif editor.tool == "crop":
            # Crop the image
            x1, x2 = sorted([editor.start_x, event.x])
            y1, y2 = sorted([editor.start_y, event.y])
            
            if x2 - x1 > 5 and y2 - y1 > 5:
                # Scale coordinates back to original image size
                orig_x1 = int(x1 * editor.scale_x)
                orig_y1 = int(y1 * editor.scale_y)
                orig_x2 = int(x2 * editor.scale_x)
                orig_y2 = int(y2 * editor.scale_y)
                
                editor.draw_image = editor.draw_image.crop((orig_x1, orig_y1, orig_x2, orig_y2))
                editor.original_image = editor.draw_image.copy()
                
                # Recalculate display size
                img_width, img_height = editor.draw_image.size
                max_width, max_height = 800, 500
                if img_width > max_width or img_height > max_height:
                    ratio = min(max_width / img_width, max_height / img_height)
                    editor.display_size = (int(img_width * ratio), int(img_height * ratio))
                else:
                    editor.display_size = (img_width, img_height)
                
                editor.scale_x = img_width / editor.display_size[0]
                editor.scale_y = img_height / editor.display_size[1]
                
                # Update canvas
                editor.canvas.config(width=editor.display_size[0], height=editor.display_size[1])
                display_img = editor.draw_image.resize(editor.display_size, Image.Resampling.LANCZOS)
                editor.tk_image = ImageTk.PhotoImage(display_img)
                editor.canvas.create_image(0, 0, image=editor.tk_image, anchor="nw")
                editor.canvas.image_ref = editor.tk_image
                
                messagebox.showinfo("Crop", "Image cropped successfully!")
            
            if editor.current_shape:
                editor.canvas.delete(editor.current_shape)
                editor.current_shape = None

    def copy_to_clipboard(self, image, silent=False, editor=None):
        """Detailed logic to copy image to Windows Clipboard."""
        if not WIN32_AVAILABLE:
            if not silent:
                messagebox.showerror(
                    "Error",
                    "pywin32 is not installed.\n\n"
                    "Install it with: pip install pywin32\n"
                    "Then restart the application."
                )
            if editor:
                pass  # Could set status in editor
            else:
                self.lbl_status.configure(text="Error: pywin32 not installed", text_color="#E63946")
            return
        
        try:
            output = io.BytesIO()
            image.convert("RGB").save(output, "BMP")
            data = output.getvalue()[14:]  # Remove BMP header (14 bytes)
            output.close()

            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()
            
            if not silent:
                if editor:
                    messagebox.showinfo("Success", "Copied to Clipboard!")
                else:
                    self.lbl_status.configure(text="Copied to Clipboard!", text_color="#2a9d8f")
        except Exception as e:
            if not silent:
                messagebox.showerror("Error", f"Failed to copy to clipboard:\n{str(e)}")
            if editor:
                pass
            else:
                self.lbl_status.configure(text="Copy failed", text_color="#E63946")

    def extract_text_from_image(self, image, editor=None):
        """Extracts text from image using OCR (Optical Character Recognition)."""
        if not PYTESSERACT_AVAILABLE:
            messagebox.showerror(
                "Error",
                "pytesseract is not installed.\n\n"
                "Install it with: pip install pytesseract\n\n"
                "Also install Tesseract OCR executable from:\n"
                "https://github.com/UB-Mannheim/tesseract/wiki\n\n"
                "After installation, you may need to set the Tesseract path:\n"
                "pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'"
            )
            return
        
        try:
            # Show progress
            progress_window = ctk.CTkToplevel(self)
            progress_window.title("OCR Processing")
            progress_window.geometry("400x150")
            progress_window.attributes('-topmost', True)
            progress_window.resizable(False, False)
            
            progress_label = ctk.CTkLabel(
                progress_window,
                text="Extracting text from image...",
                font=("Roboto", 12)
            )
            progress_label.pack(expand=True, pady=20)
            
            def process_ocr():
                try:
                    # Convert image to RGB if needed
                    if image.mode != 'RGB':
                        ocr_image = image.convert('RGB')
                    else:
                        ocr_image = image.copy()
                    
                    # Perform OCR
                    extracted_text = pytesseract.image_to_string(ocr_image)
                    progress_window.destroy()
                    
                    # Display results in a new window
                    self.show_text_results(extracted_text)
                    
                except Exception as e:
                    progress_window.destroy()
                    error_msg = str(e)
                    if "tesseract" in error_msg.lower() or "not found" in error_msg.lower():
                        messagebox.showerror(
                            "Tesseract Not Found",
                            "Tesseract OCR executable not found.\n\n"
                            "Please install Tesseract OCR from:\n"
                            "https://github.com/UB-Mannheim/tesseract/wiki\n\n"
                            "Or set the path manually:\n"
                            "pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'"
                        )
                    else:
                        messagebox.showerror("OCR Error", f"Failed to extract text:\n{error_msg}")
            
            progress_window.after(100, process_ocr)
            
        except Exception as e:
            messagebox.showerror("Error", f"OCR processing failed:\n{str(e)}")

    def show_text_results(self, text):
        """Displays extracted text in a window with copy functionality."""
        text_window = ctk.CTkToplevel(self)
        text_window.title("Extracted Text - Clippr")
        text_window.geometry("700x500")
        text_window.attributes('-topmost', True)
        
        # Title
        title_label = ctk.CTkLabel(
            text_window,
            text="Extracted Text",
            font=("Roboto", 16, "bold")
        )
        title_label.pack(pady=10)
        
        # Text display (scrollable)
        text_frame = ctk.CTkScrollableFrame(text_window)
        text_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Display text
        if text.strip():
            text_display = ctk.CTkTextbox(text_frame, width=650, height=350, wrap="word")
            text_display.pack(fill="both", expand=True)
            text_display.insert("1.0", text)
            text_display.configure(state="disabled")
            text_window.extracted_text = text
        else:
            no_text_label = ctk.CTkLabel(
                text_frame,
                text="No text found in the image.",
                font=("Roboto", 12),
                text_color="gray"
            )
            no_text_label.pack(expand=True)
            text_window.extracted_text = ""
        
        # Action buttons
        btn_frame = ctk.CTkFrame(text_window)
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        if text.strip():
            btn_copy_text = ctk.CTkButton(
                btn_frame,
                text="Copy Text to Clipboard",
                command=lambda: self.copy_text_to_clipboard(text, text_window),
                fg_color="#2a9d8f"
            )
            btn_copy_text.pack(side="left", padx=10)
        
        btn_close = ctk.CTkButton(
            btn_frame,
            text="Close",
            fg_color="gray",
            command=text_window.destroy
        )
        btn_close.pack(side="right", padx=10)

    def copy_text_to_clipboard(self, text, window=None):
        """Copies text to clipboard."""
        try:
            if WIN32_AVAILABLE:
                # Use win32clipboard for text
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, text)
                win32clipboard.CloseClipboard()
            else:
                # Fallback to tkinter clipboard
                self.clipboard_clear()
                self.clipboard_append(text)
                self.update()
            
            messagebox.showinfo("Success", "Text copied to clipboard!")
            if window:
                window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy text:\n{str(e)}")

    def save_to_file(self, image, editor=None):
        """Saves the image to a file."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPG", "*.jpg")],
            initialfile=f"Snip_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        if filename:
            image.save(filename)
            if editor:
                messagebox.showinfo("Success", f"Saved to {filename}")
            else:
                self.lbl_status.configure(text=f"Saved to {filename}", text_color="#2a9d8f")


if __name__ == "__main__":
    app = SnippingTool()
    app.mainloop()