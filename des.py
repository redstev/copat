import tkinter as tk
from tkinter import ttk, scrolledtext
import re
from typing import List, Tuple, Dict
from dataclasses import dataclass
import time
import os
import json
from PIL import Image, ImageTk
from ttkthemes import ThemedTk # Import ThemedTk

# --- Pirate Theme Configuration ---
# Using hex codes for better color control
# Light Mode Colors (Inspired by parchment, sea foam, wood)
LIGHT_BG = "#F5F5DC"  # Beige (Parchment)
LIGHT_TEXT = "#3B3131"  # Dark Brown (Wood/Ink)
LIGHT_ACCENT = "#87CEEB" # Sky Blue (Sea Foam/Sky)
LIGHT_TEXT_AREA_BG = "#FFFFFF" # White
LIGHT_BUTTON_BG = "#D2B48C" # Tan (Wood)
LIGHT_BUTTON_FG = "#3B3131" # Dark Brown

# Dark Mode Colors (Inspired by deep sea, night sky, treasure)
DARK_BG = "#1E2A3A"   # Deep Blue/Grey (Deep Sea)
DARK_TEXT = "#E0E0E0"   # Light Grey (Moonlight)
DARK_ACCENT = "#FFD700" # Gold (Treasure)
DARK_TEXT_AREA_BG = "#2C3E50" # Darker Blue/Grey
DARK_BUTTON_BG = "#4A6B8A" # Medium Blue/Grey
DARK_BUTTON_FG = "#E0E0E0" # Light Grey

# Font configuration
FONT_FAMILY_MAIN = "Segoe UI" # Modern, clean font
FONT_FAMILY_TITLE = "Segoe UI Semibold" # Slightly bolder for title
FONT_SIZE_NORMAL = 10
FONT_SIZE_HEADER = 11
FONT_SIZE_TITLE = 14

# Symbol for Success Checkmark (Pirate themed?)
SUCCESS_SYMBOL = "✔" # Could be "⚓" or "★" but ✔ is clearer

@dataclass
class CodeBlock:
    code: str
    indent_level: int
    leading_spaces: int

class SmartCodePatcher:
    def __init__(self):
        # Use ThemedTk for better styling foundation
        self.root = ThemedTk(theme="arc") # Using 'arc' theme as a base, can change to others like 'equilux', 'breeze'
        self.root.title("Co-Patcher - The Code Buccaneer")
        self.dark_mode = False  # Start in light mode

        # Configuration
        self.config_file = os.path.join(os.path.expanduser("~"), ".copatcher_config.json")

        # --- Icon Handling ---
        # IMPORTANT: Ensure this path is correct for your system!
        # Using a relative path is generally better if the icon is in the same folder:
        # self.icon_path = "favicon.ico"
        self.icon_path = r"C:\Users\279sd\OneDrive\Desktop\p4tch4r\favicon.ico" # Keep your original path for now
        self.logo_image_tk = None # To store the PhotoImage object

        self.set_app_icon() # Set icon early

        self.setup_styles() # Setup base styles first
        self.setup_ui()     # Then create UI elements

        # Load and apply previous position or default
        self.load_and_apply_position()

        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Apply initial theme (light mode by default now)
        self.apply_theme()

    def set_app_icon(self):
        """Set the application icon using the ICO file directly."""
        try:
            if os.path.exists(self.icon_path):
                # For Tkinter's iconbitmap, the .ico format is usually best on Windows.
                self.root.iconbitmap(self.icon_path)
                print(f"Taskbar icon set successfully from {self.icon_path}")

                # Also load for use within the app (logo display)
                logo_img = Image.open(self.icon_path)
                # Resize for the GUI logo display (keep original for taskbar)
                logo_size = 48 # Slightly smaller logo for UI balance
                resized_logo = logo_img.resize((logo_size, logo_size), Image.LANCZOS)
                self.logo_image_tk = ImageTk.PhotoImage(resized_logo)

            else:
                print(f"Icon file not found at {self.icon_path}")
                self.logo_image_tk = None # Ensure it's None if load fails
        except Exception as e:
            # tk.TclError might occur if the .ico is invalid for iconbitmap
            print(f"Error setting application icon: {e}")
            self.logo_image_tk = None

    def save_position(self):
        """Save the current window position and dark mode state."""
        try:
            geometry = self.root.geometry()
            position = geometry.split('+', 1)[1]
            config = {"position": position, "dark_mode": self.dark_mode}
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
            print(f"Window state saved: Position={position}, DarkMode={self.dark_mode}")
        except Exception as e:
            print(f"Error saving window state: {e}")

    def load_and_apply_position(self):
        """Load saved position and dark mode state or use defaults."""
        width = 750 # Slightly wider default
        height = 650 # Slightly taller default
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)

                # Restore dark mode state FIRST
                self.dark_mode = config.get("dark_mode", False) # Default to light if not found

                # Restore position
                position = config.get("position")
                if position:
                    self.root.geometry(f"{width}x{height}+{position}")
                    print(f"Restored state: Position={position}, DarkMode={self.dark_mode}")
                    return # Success

            # If no config or position, default to right side
            self.position_window_right(width, height)
            self.dark_mode = False # Ensure default is light mode if no config

        except Exception as e:
            print(f"Error loading window state: {e}")
            self.position_window_right(width, height)
            self.dark_mode = False # Fallback to light mode

    def on_closing(self):
        """Handle window close event."""
        self.save_position()
        self.root.destroy()

    def position_window_right(self, width, height):
        """Position the window on the right side of the screen."""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = screen_width - width - 30  # A bit more margin
        y = (screen_height - height) // 2 - 30 # Slightly higher than center
        y = max(y, 30) # Ensure it's not too high
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        print(f"Window positioned to right side ({width}x{height}+{x}+{y})")

    def setup_styles(self):
        """Configure ttk styles."""
        self.style = ttk.Style()
        # Ensure the theme engine is aware (needed after creating ThemedTk)
        self.style.theme_use(self.root.get_themes()[0]) # Get the current theme name used by ThemedTk

        # General Style Configurations (will be overridden by apply_theme)
        self.style.configure("TFrame", padding=5)
        self.style.configure("TButton", padding=5, font=(FONT_FAMILY_MAIN, FONT_SIZE_NORMAL))
        self.style.configure("TLabel", padding=2, font=(FONT_FAMILY_MAIN, FONT_SIZE_NORMAL))
        self.style.configure("Header.TLabel", font=(FONT_FAMILY_MAIN, FONT_SIZE_HEADER, "bold"))
        self.style.configure("AppName.TLabel", font=(FONT_FAMILY_TITLE, FONT_SIZE_TITLE, "bold"))
        self.style.configure("Success.TLabel", font=(FONT_FAMILY_MAIN, FONT_SIZE_NORMAL)) # Color set in apply_theme
        self.style.configure("BW.TButton", # Style for inject button (stands out)
                             font=(FONT_FAMILY_MAIN, FONT_SIZE_NORMAL, "bold"))

        # Style the PanedWindow sash (the divider)
        self.style.configure("TPanedwindow", background=LIGHT_BG) # Initial color
        self.style.map("TPanedwindow.Sash", background=[("active", LIGHT_ACCENT)])

    def apply_theme(self):
        """Apply colors and styles based on dark_mode state."""
        bg_color = DARK_BG if self.dark_mode else LIGHT_BG
        fg_color = DARK_TEXT if self.dark_mode else LIGHT_TEXT
        accent_color = DARK_ACCENT if self.dark_mode else LIGHT_ACCENT
        text_bg = DARK_TEXT_AREA_BG if self.dark_mode else LIGHT_TEXT_AREA_BG
        btn_bg = DARK_BUTTON_BG if self.dark_mode else LIGHT_BUTTON_BG
        btn_fg = DARK_BUTTON_FG if self.dark_mode else LIGHT_BUTTON_FG
        inject_btn_bg = DARK_ACCENT if self.dark_mode else LIGHT_ACCENT # Make inject button use accent
        inject_btn_fg = DARK_BG if self.dark_mode else LIGHT_BG # Contrast for inject button

        self.root.configure(bg=bg_color)

        # Update Style configurations
        self.style.configure("TFrame", background=bg_color)
        self.style.configure("TLabel", background=bg_color, foreground=fg_color)
        self.style.configure("Header.TLabel", background=bg_color, foreground=fg_color)
        self.style.configure("AppName.TLabel", background=bg_color, foreground=accent_color) # Title uses accent
        self.style.configure("Success.TLabel", background=bg_color, foreground=accent_color) # Success uses accent

        # Buttons need specific background/foreground in configure for reliability
        self.style.configure("TButton", background=btn_bg, foreground=btn_fg,
                             font=(FONT_FAMILY_MAIN, FONT_SIZE_NORMAL), borderwidth=1)
        self.style.map("TButton",
                       background=[('active', accent_color), ('pressed', accent_color)],
                       foreground=[('active', fg_color), ('pressed', fg_color)])

        # Inject button style
        self.style.configure("BW.TButton", background=inject_btn_bg, foreground=inject_btn_fg,
                              font=(FONT_FAMILY_MAIN, FONT_SIZE_NORMAL, "bold"))
        self.style.map("BW.TButton",
                       background=[('active', btn_bg), ('pressed', btn_bg)], # Swap on hover/press
                       foreground=[('active', btn_fg), ('pressed', btn_fg)])

        # Update PanedWindow and Sash
        self.style.configure("TPanedwindow", background=bg_color)
        self.style.map("TPanedwindow.Sash", background=[("active", accent_color)]) # Sash hover color

        # Update Text Areas (need direct configuration)
        text_widgets = [self.code_text, self.changes_text, self.preview_text]
        for widget in text_widgets:
            widget.configure(
                bg=text_bg,
                fg=fg_color,
                insertbackground=accent_color, # Cursor color uses accent
                font=(FONT_FAMILY_MAIN, FONT_SIZE_NORMAL),
                borderwidth=0, # Remove border for flatter look
                relief=tk.FLAT, # Flat relief
                selectbackground=accent_color, # Selection uses accent
                selectforeground=text_bg # Text color during selection
            )

        # Update Dark Mode Toggle Button Text/Symbol
        # Using Unicode symbols for a bit of flair
        toggle_text = "☀️ Light Mode" if self.dark_mode else "🌙 Dark Mode"
        self.dark_mode_button.configure(text=toggle_text)

        # Update Logo Label Background (if it exists)
        if hasattr(self, 'logo_label'):
             self.logo_label.configure(background=bg_color)

        # Update Checkmark Labels (already styled, colors applied via style update)
        # Update App Name Label Style
        self.logo_name_label.configure(style="AppName.TLabel")


    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme() # Re-apply styles

    def setup_ui(self):
        # Main frame to hold everything, allows root background color to show
        main_frame = ttk.Frame(self.root, style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Top part with Code | Inject | Changes
        top_pane = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        top_pane.pack(fill=tk.BOTH, expand=True, side=tk.TOP, pady=(0, 5))

        # --- Original Code Section ---
        code_frame = ttk.Frame(top_pane, padding=5)
        top_pane.add(code_frame, weight=2) # Give more weight

        code_header_frame = ttk.Frame(code_frame)
        code_header_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(code_header_frame, text="Original Code", style="Header.TLabel").pack(side=tk.LEFT)
        self.code_check = ttk.Label(code_header_frame, text=SUCCESS_SYMBOL, style="Success.TLabel")
        # self.code_check pack/pack_forget managed later

        self.code_text = scrolledtext.ScrolledText(code_frame, wrap=tk.NONE, height=10)
        self.code_text.pack(fill=tk.BOTH, expand=True)
        self.code_text.bind("<FocusIn>", self.select_all_text)

        # --- Inject/Logo Section (Middle) ---
        inject_frame = ttk.Frame(top_pane, style="TFrame", width=150) # Fixed width might be needed
        inject_frame.pack_propagate(False) # Prevent frame from shrinking to content
        top_pane.add(inject_frame, weight=0) # No weight, fixed size

        logo_area = ttk.Frame(inject_frame)
        logo_area.pack(pady=20, anchor=tk.CENTER) # Center the logo area

        if self.logo_image_tk:
            self.logo_label = ttk.Label(logo_area, image=self.logo_image_tk)
            self.logo_label.pack()
        else:
             # Placeholder if image failed to load
             self.logo_label = ttk.Label(logo_area, text="[Logo]")
             self.logo_label.pack()

        self.logo_name_label = ttk.Label(logo_area, text="Co-Patcher", style="AppName.TLabel", anchor=tk.CENTER)
        self.logo_name_label.pack(pady=(5, 20)) # Space below name

        self.inject_button = ttk.Button(
            inject_frame,
            text="Inject Changes", # Clearer text
            command=self.inject_code,
            style="BW.TButton" # Apply the special style
        )
        # Use pack to center the button at the bottom of its area
        self.inject_button.pack(side=tk.BOTTOM, pady=20, padx=10, fill=tk.X)


        # --- Changes Section ---
        changes_frame = ttk.Frame(top_pane, padding=5)
        top_pane.add(changes_frame, weight=2) # Give more weight

        changes_header_frame = ttk.Frame(changes_frame)
        changes_header_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(changes_header_frame, text="Changes", style="Header.TLabel").pack(side=tk.LEFT)
        self.changes_check = ttk.Label(changes_header_frame, text=SUCCESS_SYMBOL, style="Success.TLabel")
        # self.changes_check pack/pack_forget managed later

        self.changes_text = scrolledtext.ScrolledText(changes_frame, wrap=tk.NONE, height=10)
        self.changes_text.pack(fill=tk.BOTH, expand=True)
        self.changes_text.bind("<FocusIn>", self.select_all_text)

        # --- Bottom Section (Buttons and Preview) ---
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True, side=tk.BOTTOM)

        # Buttons Frame
        button_frame = ttk.Frame(bottom_frame)
        button_frame.pack(fill=tk.X, pady=5)

        self.process_button = ttk.Button(button_frame, text="Process Changes", command=self.process_changes)
        self.process_button.pack(side=tk.LEFT, padx=(0, 5))

        self.copy_button = ttk.Button(button_frame, text="Copy Result", command=self.copy_result)
        self.copy_button.pack(side=tk.LEFT, padx=5)

        self.dark_mode_button = ttk.Button(button_frame, text="🌙 Dark Mode", command=self.toggle_dark_mode)
        self.dark_mode_button.pack(side=tk.RIGHT, padx=5)

        # Result Preview Frame
        preview_frame = ttk.Frame(bottom_frame)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(5,0))

        preview_header_frame = ttk.Frame(preview_frame)
        preview_header_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(preview_header_frame, text="Result Preview", style="Header.TLabel").pack(side=tk.LEFT)
        self.result_check = ttk.Label(preview_header_frame, text=SUCCESS_SYMBOL, style="Success.TLabel")
        # self.result_check pack/pack_forget managed later

        self.preview_text = scrolledtext.ScrolledText(preview_frame, wrap=tk.NONE, height=10)
        self.preview_text.pack(fill=tk.BOTH, expand=True)


    def select_all_text(self, event):
        # Schedule the select_all to run after the focus event is fully processed
        event.widget.after_idle(lambda: event.widget.tag_add('sel', '1.0', 'end'))
        # Don't return 'break', allow default focus behavior
        # return 'break'


    def analyze_indentation(self, code: str) -> List[CodeBlock]:
        # This function seems fine, no changes needed for styling
        blocks = []
        lines = code.splitlines()
        for line in lines:
            leading_spaces = len(line) - len(line.lstrip())
            stripped = line.lstrip() # Use lstrip here for block code
            
            # Treat empty or whitespace-only lines correctly
            if not stripped:
                 blocks.append(CodeBlock(line.strip(), 0, leading_spaces)) # Keep original spacing info if needed, but indent 0
                 continue

            # Calculate indent level based on leading spaces (assuming 4 spaces)
            # Use actual leading spaces for reconstruction, indent_level for logic if needed
            indent_level = leading_spaces // 4

            blocks.append(CodeBlock(stripped, indent_level, leading_spaces))
        return blocks

    def _apply_changes_logic(self, original_code: str, changes_text: str) -> str:
        """Internal logic for applying changes, returns the modified code."""
        modified_code = original_code
        if not original_code.strip() or not changes_text.strip():
            return original_code # Return original if nothing to process

        # Simple parsing, assuming FIND:, REPLACE:, END structure
        # More robust parsing might be needed for complex cases
        changes = re.split(r'(FIND:)', changes_text)[1:] # Split and keep FIND:

        i = 0
        while i < len(changes):
            if changes[i] == 'FIND:' and i + 1 < len(changes):
                # Extract find/replace blocks
                content = changes[i+1]
                parts = re.split(r'(REPLACE:)', content, 1)
                find_part = parts[0]
                
                if len(parts) > 1 and parts[1] == 'REPLACE:' and len(parts) > 2:
                    replace_content = parts[2]
                    replace_parts = re.split(r'(END)', replace_content, 1)
                    replace_part = replace_parts[0]
                    # end_part is replace_parts[1] + replace_parts[2] if needed

                    # Clean up leading/trailing whitespace BUT preserve internal structure
                    find_code_raw = find_part.strip()
                    replace_code_raw = replace_part.strip() # Strip outer whitespace only

                    if not find_code_raw:
                        i += 2
                        continue # Skip if find block is empty

                    # Analyze base indentation of the *first line* of the find block in the *original* code
                    try:
                        # Find the start index of the raw find_code block
                        start_index = modified_code.index(find_code_raw)
                        # Find the beginning of that line
                        line_start_index = modified_code.rfind('\n', 0, start_index) + 1
                        # Get the leading whitespace
                        leading_whitespace = modified_code[line_start_index:start_index]
                        
                        # Reconstruct replace_code with the found leading whitespace applied to each line
                        replace_lines = replace_code_raw.splitlines()
                        indented_replace_lines = []
                        for line in replace_lines:
                             # Add the original leading whitespace + any *relative* indent within the replace block
                             # This simple version just adds the base indent to all non-empty lines
                             if line.strip():
                                 indented_replace_lines.append(leading_whitespace + line)
                             else:
                                 indented_replace_lines.append("") # Keep empty lines

                        indented_replace = "\n".join(indented_replace_lines)

                        # Perform the replacement
                        # Use count=1 to replace only the first occurrence if desired,
                        # otherwise replaces all occurrences. Replacing all is likely intended.
                        modified_code = modified_code.replace(find_code_raw, indented_replace)

                    except ValueError:
                        # find_code_raw not found in modified_code, skip this change
                        print(f"Warning: Block starting with '{find_code_raw[:50]}...' not found.")
                        pass

                i += 2 # Move past FIND: and its content block
            else:
                 i += 1 # Should not happen with correct split, but prevents infinite loop

        return modified_code

    def _flash_checkmark(self, check_label: ttk.Label):
        """Show and then hide a checkmark label."""
        check_label.pack(side=tk.RIGHT, padx=5)
        self.root.after(2000, lambda: check_label.pack_forget())

    def process_changes(self):
        original_code = self.code_text.get("1.0", tk.END).strip()
        changes_text = self.changes_text.get("1.0", tk.END).strip()

        if not original_code or not changes_text:
            print("Both Original Code and Changes must be provided.")
            return

        # Show processing indicators (optional)
        # ...

        modified_code = self._apply_changes_logic(original_code + "\n", changes_text + "\n") # Add newline robustness

        # Update preview
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert("1.0", modified_code.strip()) # Strip trailing newline added

        # Flash checkmarks for visual feedback
        self._flash_checkmark(self.code_check)
        self._flash_checkmark(self.changes_check)
        print("Changes processed.")


    def copy_result(self):
        result = self.preview_text.get("1.0", tk.END).strip()
        if not result:
            return

        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(result)
            print("Result copied to clipboard.")
            self._flash_checkmark(self.result_check)
        except tk.TclError:
             print("Error: Could not access clipboard.")


    def inject_code(self):
        """
        Apply changes from 'Changes' to 'Original Code' and copy result.
        """
        original_code = self.code_text.get("1.0", tk.END).strip()
        changes_text = self.changes_text.get("1.0", tk.END).strip()

        if not original_code or not changes_text:
            print("Both Original Code and Changes must be provided for injection.")
            return

        modified_code = self._apply_changes_logic(original_code + "\n", changes_text + "\n") # Add newline robustness

        # Update original code text area
        self.code_text.delete("1.0", tk.END)
        self.code_text.insert("1.0", modified_code.strip()) # Strip trailing newline added

        # Clear changes and preview text areas after injection? Optional.
        # self.changes_text.delete("1.0", tk.END)
        # self.preview_text.delete("1.0", tk.END)

        # Copy the new original code to clipboard automatically
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(modified_code.strip())
            print("Injected changes applied to Original Code and copied to clipboard.")
            self._flash_checkmark(self.code_check) # Flash checkmark on the original code section
        except tk.TclError:
             print("Error: Could not access clipboard after injection.")


    def run(self):
        # Ensure the UI is fully drawn before starting the main loop
        # This *might* help with the taskbar icon showing up immediately,
        # although iconbitmap() called early should be sufficient.
        self.root.update_idletasks()
        self.root.mainloop()

if __name__ == "__main__":
    # Ensures Pillow finds Tk PhotoImage format (sometimes needed)
    # from PIL import Image, ImageTk
    # Image.init() # Not usually necessary, but can try if images fail

    app = SmartCodePatcher()
    app.run()