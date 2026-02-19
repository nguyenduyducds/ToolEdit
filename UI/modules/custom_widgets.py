import tkinter as tk
import customtkinter as ctk

COLOR_ACCENT = "#00BFA5"
COLOR_HOVER = "#3A3A3A"

class DraggableValueLabel(ctk.CTkLabel):
    """
    A label that acts like a numeric input (CustomTkinter version).
    - Click and drag left/right to change value (Scrubby).
    - Double click to type value manually.
    """
    def __init__(self, parent, variable, min_val, max_val, step=0.1, fmt="%.2f", **kwargs):
        # Handle colors manually to support hover/active states
        self.default_fg_color = kwargs.pop("fg_color", "#2B2B2B") 
        self.default_text_color = kwargs.pop("text_color", COLOR_ACCENT)
        
        # Override cursor if possible (CTK might not support cursor config on Label directly in all versions, but let's try)
        if "cursor" not in kwargs:
            kwargs["cursor"] = "size_we"
            
        super().__init__(parent, **kwargs, fg_color=self.default_fg_color, text_color=self.default_text_color)
        
        self.variable = variable
        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        self.fmt = fmt
        
        # State
        self.start_x = 0
        self.start_val = 0
        self.dragging = False
        
        # Initial text
        self.update_text()
        
        # Trace variable changes
        self.trace_id = self.variable.trace_add("write", lambda *args: self.update_text())
        
        # Bindings
        self.bind("<Button-1>", self.on_press)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Double-Button-1>", self.on_double_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def update_text(self):
        try:
            val = self.variable.get()
            if isinstance(val, (int, float)):
                if "d" in self.fmt:
                    self.configure(text=self.fmt % int(val))
                else:
                    self.configure(text=self.fmt % float(val))
        except:
            pass

    def on_enter(self, event):
        self.configure(fg_color=COLOR_HOVER, text_color="#FFFFFF")

    def on_leave(self, event):
        if not self.dragging:
            self.configure(fg_color=self.default_fg_color, text_color=self.default_text_color)

    def on_press(self, event):
        self.start_x = event.x_root
        try:
            self.start_val = self.variable.get()
        except:
            self.start_val = self.min_val
        self.dragging = True
        self.configure(fg_color=COLOR_ACCENT, text_color="#000000") # Active state

    def on_drag(self, event):
        if not self.dragging: return
        
        delta = event.x_root - self.start_x
        
        change = delta * self.step
        new_val = self.start_val + change
        
        # Clamp
        new_val = max(self.min_val, min(self.max_val, new_val))
        
        # Rounding
        if isinstance(self.variable, tk.IntVar) or "d" in self.fmt:
            self.variable.set(int(new_val))
        else:
            self.variable.set(round(new_val, 2))

    def on_release(self, event):
        self.dragging = False
        self.configure(fg_color=self.default_fg_color, text_color=self.default_text_color)
        self.update_text()

    def on_double_click(self, event):
        # Switch to Entry mode (CTK Entry)
        self.entry_var = tk.StringVar(value=str(self.variable.get()))
        
        self.entry = ctk.CTkEntry(self.master, textvariable=self.entry_var, 
                                 width=self.winfo_width(), height=self.winfo_height(),
                                 fg_color="#333333", text_color="white", border_width=0)
        
        # Place entry exactly over label
        self.entry.place(in_=self, x=0, y=0)
        self.entry.focus_set()
        # Select all is trickier in CTK, let's just focus
        
        # Bindings to finish edit
        self.entry.bind("<Return>", self.finish_edit)
        self.entry.bind("<FocusOut>", self.finish_edit)
        self.entry.bind("<Escape>", self.cancel_edit)

    def finish_edit(self, event=None):
        if not hasattr(self, 'entry'): return
        try:
            val = float(self.entry_var.get())
            val = max(self.min_val, min(self.max_val, val))
            
            if isinstance(self.variable, tk.IntVar) or "d" in self.fmt:
                self.variable.set(int(val))
            else:
                self.variable.set(val)
        except:
            pass # Invalid input, ignore
        finally:
            self.entry.destroy()
            del self.entry

    def cancel_edit(self, event=None):
        if hasattr(self, 'entry'):
            self.entry.destroy()
            del self.entry
