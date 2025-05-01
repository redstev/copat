import tkinter as tk
from tkinter import ttk, scrolledtext
import re
from typing import List, Tuple, Dict
from dataclasses import dataclass
import time
import os
import json
from PIL import Image, ImageTk  # For logo image handling

@dataclass
class CodeBlock:
    code: str
    indent_level: int
    leading_spaces: int

class SmartCodePatcher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Co-Patcher")
        self.dark_mode = False  # Track dark mode state
        
        # Configuration
        self.config_file = os.path.join(os.path.expanduser("~"), ".copatcher_config.json")
        
        # Set application icon
        self.set_app_icon()
        
        self.setup_ui()
        self.setup_styles()

        # Load and apply previous position, or use default right position
        self.load_and_apply_position()

        # Bind window close event to save position
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Enable dark mode at startup
        self.toggle_dark_mode()
    
    def set_app_icon(self):
        """Set the application icon using the ICO file directly."""
        ico_path = r"C:\Users\279sd\OneDrive\Desktop\p4tch4r\favicon.ico"
        
        try:
            if os.path.exists(ico_path):
                # Set ico file directly as window icon
                self.root.iconbitmap(ico_path)
                print(f"Icon set successfully from {ico_path}")
            else:
                print(f"Icon file not found at {ico_path}")
        except Exception as e:
            print(f"Error setting application icon: {e}")
    
    def save_position(self):
        """Save the current window position to a configuration file."""
        try:
            # Get current geometry
            geometry = self.root.geometry()
            
            # Extract position information
            position = geometry.split('+', 1)[1]  # Get the +x+y part
            
            # Save to config file
            config = {"position": position}
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
                
            print(f"Window position saved: {position}")
        except Exception as e:
            print(f"Error saving window position: {e}")
    
    def load_and_apply_position(self):
        """Load the saved position or use default right position."""
        try:
            # Check if config file exists
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                if "position" in config:
                    width = 600
                    height = 600
                    position = config["position"]
                    self.root.geometry(f"{width}x{height}+{position}")
                    print(f"Restored position from config: {position}")
                    return
            
            # If no config or position, default to right side
            self.position_window_right()
            
        except Exception as e:
            print(f"Error loading window position: {e}")
            # Fall back to default right position
            self.position_window_right()
    
    def on_closing(self):
        """Handle window close event - save position before closing."""
        self.save_position()
        self.root.destroy()
    
    def position_window_right(self):
        """Position the window on the right side of the screen."""
        # Set window size
        width = 600
        height = 600
        
        # Get screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate position for right side
        x = screen_width - width - 20  # 20 pixels from right edge
        y = (screen_height - height) // 2  # Center vertically
        
        # Set window geometry
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        print("Window positioned to right side")
        
    def setup_styles(self):
        self.style = ttk.Style()
        self.style.configure("Success.TLabel", foreground="green")
        self.style.configure("DarkMode.TFrame", background="#2d2d2d")
        self.style.configure("DarkMode.TButton", background="#2d2d2d", foreground="white")
        self.style.configure("DarkMode.TLabel", background="#2d2d2d", foreground="white")
        
    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        bg_color = "#2d2d2d" if self.dark_mode else "white"
        fg_color = "white" if self.dark_mode else "black"
        text_bg = "#363636" if self.dark_mode else "white"
        
        # Update frames
        for frame in [self.code_frame, self.changes_frame, self.bottom_frame,
                     self.code_header, self.changes_header, self.preview_header,
                     self.button_frame, self.inject_frame, self.logo_frame]:
            frame.configure(style="DarkMode.TFrame" if self.dark_mode else "")
            
        # Update text areas
        for text_widget in [self.code_text, self.changes_text, self.preview_text]:
            text_widget.configure(
                bg=text_bg,
                fg=fg_color,
                insertbackground=fg_color  # Cursor color
            )
            
        # Update labels
        self.dark_mode_text.configure(
            text="🌞 Light Mode" if self.dark_mode else "🌙 Dark Mode"
        )
        
        # Update app name label color
        self.logo_name_label.configure(
            style="DarkMode.TLabel" if self.dark_mode else ""
        )
        
        # Update main window
        self.root.configure(bg=bg_color)
        
    def setup_ui(self):
        # Main split container
        self.paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)
        
        # Original code section
        self.code_frame = ttk.Frame(self.paned)
        self.paned.add(self.code_frame, weight=1)
        
        self.code_header = ttk.Frame(self.code_frame)
        self.code_header.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(self.code_header, text="Original Code").pack(side=tk.LEFT)
        ttk.Label(self.code_header, text="✓", style="Success.TLabel", 
                 name="code_check").pack(side=tk.RIGHT)
        self.code_check = self.code_header.children["code_check"]
        self.code_check.pack_forget()  # Hide initially
        
        self.code_text = scrolledtext.ScrolledText(self.code_frame, wrap=tk.NONE)
        self.code_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.code_text.bind("<FocusIn>", self.select_all_text)
        
        # Inject button frame
        self.inject_frame = ttk.Frame(self.paned)
        self.paned.add(self.inject_frame, weight=0)
        
        # Add logo in the middle of inject frame
        self.logo_frame = ttk.Frame(self.inject_frame)
        self.logo_frame.pack(pady=10)
        
        # Load and display logo
        logo_path = r"C:\Users\279sd\OneDrive\Desktop\p4tch4r\favicon.ico"
        if os.path.exists(logo_path):
            try:
                # Load and resize the logo image
                original_logo = Image.open(logo_path)
                logo_size = 64  # Larger logo size
                resized_logo = original_logo.resize((logo_size, logo_size), Image.LANCZOS)
                self.logo_image = ImageTk.PhotoImage(resized_logo)
                
                # Create and pack logo label
                self.logo_label = ttk.Label(self.logo_frame, image=self.logo_image)
                self.logo_label.pack(pady=5)
                
                # Add program name under logo
                self.logo_name_label = ttk.Label(self.logo_frame, text="Co-Patcher", font=("Helvetica", 12, "bold"))
                self.logo_name_label.pack(pady=5)
            except Exception as e:
                print(f"Error loading logo image: {e}")
        
        # Add inject button at the bottom of the frame
        self.inject_button = ttk.Button(
            self.inject_frame,
            text="← Inject Code",
            command=self.inject_code
        )
        self.inject_button.pack(expand=True, padx=5, pady=10)
        
        # Changes section
        self.changes_frame = ttk.Frame(self.paned)
        self.paned.add(self.changes_frame, weight=1)
        
        self.changes_header = ttk.Frame(self.changes_frame)
        self.changes_header.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(self.changes_header, text="Changes").pack(side=tk.LEFT)
        ttk.Label(self.changes_header, text="✓", style="Success.TLabel",
                 name="changes_check").pack(side=tk.RIGHT)
        self.changes_check = self.changes_header.children["changes_check"]
        self.changes_check.pack_forget()  # Hide initially
        
        self.changes_text = scrolledtext.ScrolledText(self.changes_frame, wrap=tk.NONE)
        self.changes_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.changes_text.bind("<FocusIn>", self.select_all_text)
        
        # Bottom section
        self.bottom_frame = ttk.Frame(self.root)
        self.bottom_frame.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        self.button_frame = ttk.Frame(self.bottom_frame)
        self.button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(self.button_frame, text="Process Changes", 
                  command=self.process_changes).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(self.button_frame, text="Copy Result",
                  command=self.copy_result).pack(side=tk.LEFT, padx=5)
        
        # Dark mode toggle button
        self.dark_mode_text = ttk.Button(
            self.button_frame,
            text="🌙 Dark Mode",
            command=self.toggle_dark_mode
        )
        self.dark_mode_text.pack(side=tk.RIGHT, padx=5)
        
        # Result preview
        self.preview_header = ttk.Frame(self.bottom_frame)
        self.preview_header.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(self.preview_header, text="Result").pack(side=tk.LEFT)
        ttk.Label(self.preview_header, text="✓", style="Success.TLabel",
                 name="result_check").pack(side=tk.RIGHT)
        self.result_check = self.preview_header.children["result_check"]
        self.result_check.pack_forget()  # Hide initially
        
        self.preview_text = scrolledtext.ScrolledText(self.bottom_frame, wrap=tk.NONE)
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def select_all_text(self, event):
        event.widget.tag_add('sel', '1.0', 'end')
        event.widget.mark_set('insert', 'end')
        return 'break'

    def analyze_indentation(self, code: str) -> List[CodeBlock]:
        blocks = []
        lines = code.splitlines()
        
        for line in lines:
            if not line.strip():
                blocks.append(CodeBlock(line, 0, 0))
                continue
                
            leading_spaces = len(line) - len(line.lstrip())
            stripped = line.strip()
            
            # Calculate indent level based on leading spaces
            indent_level = leading_spaces // 4  # Assuming 4 spaces per level
            
            blocks.append(CodeBlock(stripped, indent_level, leading_spaces))
            
        return blocks

    def process_changes(self):
        original_code = self.code_text.get("1.0", tk.END)
        changes_text = self.changes_text.get("1.0", tk.END)
        
        if not original_code.strip() or not changes_text.strip():
            return
        
        # Show checkmarks
        self.code_check.pack(side=tk.RIGHT)
        self.changes_check.pack(side=tk.RIGHT)
        
        # Parse changes
        modified_code = original_code
        changes = changes_text.split('FIND:')[1:]  # Skip first empty part
        
        for change in changes:
            try:
                parts = change.split('REPLACE:', 1)
                if len(parts) != 2:
                    continue
                    
                find_part = parts[0]
                
                rest_parts = parts[1].split('END', 1)
                if len(rest_parts) != 2:
                    continue
                    
                replace_part = rest_parts[0]
                
                # Clean up the parts
                find_code = find_part.strip()
                replace_code = replace_part.strip()
                
                # Analyze indentation of find_code
                find_blocks = self.analyze_indentation(find_code)
                base_indent = find_blocks[0].leading_spaces if find_blocks else 0
                
                # Apply same indentation to replace_code
                replace_blocks = self.analyze_indentation(replace_code)
                indented_replace_lines = []
                
                for block in replace_blocks:
                    if block.code.strip():
                        spaces = base_indent + (block.indent_level * 4)
                        indented_replace_lines.append(' ' * spaces + block.code)
                    else:
                        indented_replace_lines.append('')
                        
                indented_replace = '\n'.join(indented_replace_lines)
                
                # Apply the change
                modified_code = modified_code.replace(find_code, indented_replace)
                
            except (ValueError, IndexError):
                continue
        
        # Update preview
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert("1.0", modified_code)

    def copy_result(self):
        result = self.preview_text.get("1.0", tk.END)
        if not result.strip():
            return
            
        self.root.clipboard_clear()
        self.root.clipboard_append(result)
        
        # Show success checkmark
        self.result_check.pack(side=tk.RIGHT)
        
        # Hide checkmark after 2 seconds
        self.root.after(2000, lambda: self.result_check.pack_forget())
    
    def inject_code(self):
        """
        Apply the changes from the Changes section to the Original Code section.
        This allows for chaining multiple changes without manual copying.
        Also automatically copies the resulting code to clipboard.
        """
        original_code = self.code_text.get("1.0", tk.END)
        changes_text = self.changes_text.get("1.0", tk.END)
        
        if not original_code.strip() or not changes_text.strip():
            return
        
        # Parse changes
        modified_code = original_code
        changes = changes_text.split('FIND:')[1:]  # Skip first empty part
        
        for change in changes:
            try:
                parts = change.split('REPLACE:', 1)
                if len(parts) != 2:
                    continue
                    
                find_part = parts[0]
                
                rest_parts = parts[1].split('END', 1)
                if len(rest_parts) != 2:
                    continue
                    
                replace_part = rest_parts[0]
                
                # Clean up the parts
                find_code = find_part.strip()
                replace_code = replace_part.strip()
                
                # Analyze indentation of find_code
                find_blocks = self.analyze_indentation(find_code)
                base_indent = find_blocks[0].leading_spaces if find_blocks else 0
                
                # Apply same indentation to replace_code
                replace_blocks = self.analyze_indentation(replace_code)
                indented_replace_lines = []
                
                for block in replace_blocks:
                    if block.code.strip():
                        spaces = base_indent + (block.indent_level * 4)
                        indented_replace_lines.append(' ' * spaces + block.code)
                    else:
                        indented_replace_lines.append('')
                        
                indented_replace = '\n'.join(indented_replace_lines)
                
                # Apply the change
                modified_code = modified_code.replace(find_code, indented_replace)
                
            except (ValueError, IndexError):
                continue
        
        # Update original code
        self.code_text.delete("1.0", tk.END)
        self.code_text.insert("1.0", modified_code)
        
        # Copy to clipboard automatically
        self.root.clipboard_clear()
        self.root.clipboard_append(modified_code)
        
        # Show success checkmark
        self.code_check.pack(side=tk.RIGHT)
        
        # Hide checkmark after 2 seconds
        self.root.after(2000, lambda: self.code_check.pack_forget())
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SmartCodePatcher()
    app.run()