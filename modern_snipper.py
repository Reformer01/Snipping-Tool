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

# Configuration for the Modern UI
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class SnippingTool(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Main Window Setup ---
        self.title("PySnip Pro")
        self.geometry("350x280")
        self.resizable(False, False)
        self.attributes('-topmost', True)  # Keep the tool floating above others

        # --- UI Components ---
        self.grid_columnconfigure(0, weight=1)
        
        self.lbl_title = ctk.CTkLabel(self, text="PySnip Pro", font=("Roboto Medium", 22))
        self.lbl_title.grid(row=0, column=0, pady=(15, 10))

        # Snip Type Selection
        self.snip_type_var = ctk.StringVar(value="Rectangular")
        self.snip_type_label = ctk.CTkLabel(self, text="Snip Type:", font=("Roboto", 12))
        self.snip_type_label.grid(row=1, column=0, sticky="w", padx=20)
        
        self.snip_type_menu = ctk.CTkOptionMenu(
            self,
            values=["Rectangular", "Window", "Fullscreen"],
            variable=self.snip_type_var,
            width=250
        )
        self.snip_type_menu.grid(row=2, column=0, pady=(5, 10), padx=20, sticky="ew")

        # Timer Dropdown
        self.timer_var = ctk.StringVar(value="No Delay")
        self.timer_label = ctk.CTkLabel(self, text="Delay Timer:", font=("Roboto", 12))
        self.timer_label.grid(row=3, column=0, sticky="w", padx=20)
        
        self.timer_menu = ctk.CTkOptionMenu(
            self,
            values=["No Delay", "3 Seconds", "5 Seconds", "10 Seconds"],
            variable=self.timer_var,
            width=250
        )
        self.timer_menu.grid(row=4, column=0, pady=(5, 10), padx=20, sticky="ew")

        # Auto-Copy Checkbox
        self.auto_copy_var = ctk.BooleanVar(value=True)
        self.auto_copy_cb = ctk.CTkCheckBox(
            self,
            text="Auto-Copy to Clipboard",
            variable=self.auto_copy_var,
            font=("Roboto", 11)
        )
        self.auto_copy_cb.grid(row=5, column=0, pady=(5, 10))

        # New Snip Button
        self.btn_snip = ctk.CTkButton(
            self,
            text="NEW SNIP",
            height=40,
            fg_color="#E63946",
            hover_color="#D62828",
            font=("Roboto", 14, "bold"),
            command=self.start_snip
        )
        self.btn_snip.grid(row=6, column=0, pady=10, padx=20, sticky="ew")

        self.lbl_status = ctk.CTkLabel(self, text="Ready", text_color="gray", font=("Roboto", 10))
        self.lbl_status.grid(row=7, column=0, pady=(5, 10))

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
        editor.title("Snip Editor - PySnip Pro")
        editor.geometry("900x700")
        
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
        toolbar.pack(fill="x", padx=10, pady=10)
        
        # Drawing Tools
        tools_label = ctk.CTkLabel(toolbar, text="Tools:", font=("Roboto", 12, "bold"))
        tools_label.pack(side="left", padx=10)
        
        btn_pen = ctk.CTkButton(
            toolbar, text="Pen", width=80, height=30,
            command=lambda: setattr(editor, 'tool', 'pen'),
            fg_color=("#E63946" if editor.tool == "pen" else "#2b2b2b")
        )
        btn_pen.pack(side="left", padx=5)
        
        btn_highlighter = ctk.CTkButton(
            toolbar, text="Highlighter", width=80, height=30,
            command=lambda: setattr(editor, 'tool', 'highlighter'),
            fg_color=("#E63946" if editor.tool == "highlighter" else "#2b2b2b")
        )
        btn_highlighter.pack(side="left", padx=5)
        
        # Shape Tools
        btn_arrow = ctk.CTkButton(
            toolbar, text="Arrow", width=80, height=30,
            command=lambda: setattr(editor, 'tool', 'arrow'),
            fg_color=("#E63946" if editor.tool == "arrow" else "#2b2b2b")
        )
        btn_arrow.pack(side="left", padx=5)
        
        btn_rect = ctk.CTkButton(
            toolbar, text="Rectangle", width=80, height=30,
            command=lambda: setattr(editor, 'tool', 'rectangle'),
            fg_color=("#E63946" if editor.tool == "rectangle" else "#2b2b2b")
        )
        btn_rect.pack(side="left", padx=5)
        
        btn_circle = ctk.CTkButton(
            toolbar, text="Circle", width=80, height=30,
            command=lambda: setattr(editor, 'tool', 'circle'),
            fg_color=("#E63946" if editor.tool == "circle" else "#2b2b2b")
        )
        btn_circle.pack(side="left", padx=5)
        
        btn_crop = ctk.CTkButton(
            toolbar, text="Crop", width=80, height=30,
            command=lambda: setattr(editor, 'tool', 'crop'),
            fg_color=("#E63946" if editor.tool == "crop" else "#2b2b2b")
        )
        btn_crop.pack(side="left", padx=5)
        
        # Color selection
        color_frame = ctk.CTkFrame(toolbar)
        color_frame.pack(side="right", padx=10)
        
        color_label = ctk.CTkLabel(color_frame, text="Color:", font=("Roboto", 10))
        color_label.pack(side="left", padx=5)
        
        colors = ["#E63946", "#F77F00", "#FCBF49", "#2a9d8f", "#264653", "#000000", "#FFFFFF"]
        for color in colors:
            btn_color = ctk.CTkButton(
                color_frame, text="", width=25, height=25,
                fg_color=color, hover_color=color,
                command=lambda c=color: setattr(editor, 'pen_color', c)
            )
            btn_color.pack(side="left", padx=2)
        
        # Canvas for drawing
        canvas_frame = ctk.CTkFrame(editor)
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        editor.canvas = tk.Canvas(
            canvas_frame,
            width=display_size[0],
            height=display_size[1],
            bg="#1a1a1a",
            highlightthickness=0
        )
        editor.canvas.pack(expand=True)
        
        # Display image on canvas
        editor.tk_image = ImageTk.PhotoImage(display_image)
        editor.canvas.create_image(0, 0, image=editor.tk_image, anchor="nw")
        editor.canvas.image_ref = editor.tk_image
        
        # Bind canvas events
        editor.canvas.bind("<ButtonPress-1>", lambda e: self.on_editor_mouse_down(e, editor))
        editor.canvas.bind("<B1-Motion>", lambda e: self.on_editor_mouse_drag(e, editor))
        editor.canvas.bind("<ButtonRelease-1>", lambda e: self.on_editor_mouse_up(e, editor))
        
        # Action Buttons
        btn_frame = ctk.CTkFrame(editor)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        btn_copy = ctk.CTkButton(
            btn_frame, text="Copy to Clipboard",
            command=lambda: self.copy_to_clipboard(editor.draw_image, editor=editor)
        )
        btn_copy.pack(side="left", padx=10)
        
        btn_save = ctk.CTkButton(
            btn_frame, text="Save to File",
            command=lambda: self.save_to_file(editor.draw_image, editor=editor)
        )
        btn_save.pack(side="left", padx=10)
        
        btn_close = ctk.CTkButton(
            btn_frame, text="Close", fg_color="gray",
            command=lambda: [editor.destroy(), self.deiconify()]
        )
        btn_close.pack(side="right", padx=10)

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
