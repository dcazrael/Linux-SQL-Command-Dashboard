import tkinter as tk
from tkinter import ttk
import sv_ttk
from commands import COMMANDS


class App(tk.Tk):
    def __init__(self, title, size):
        # main setup
        super().__init__()

        self.title(title)
        self.geometry(f'{size[0]}x{size[1]}')
        self.minsize(size[0], size[1])
        self.attributes('-alpha', 0.8)

        # styles
        style = ttk.Style()
        style.layout('Hidden.TScrollbar', [])  # Versteckte Scrollbar
        sv_ttk.set_theme("dark")
        style.configure('Transparent.TFrame', background=self['bg'])
        style.configure('Card.TFrame', borderwidth=2, relief='raised', padding=10)
        style.configure('Inverse.TLabel', foreground='white', font=('Segoe UI', 11, 'bold'))
        style.configure('Menu.TButton', font=('Segoe UI', 12), anchor='w', padding=5)
        style.configure('Accent.TButton', font=('Segoe UI', 13, 'bold'), padding=6)

        # widgets
        self.main = Main(self)
        self.menu = Menu(self, self.main)

    @staticmethod
    def ttk_label(frame, text_str, anchor='w', font_size=12):
        ttk.Label(frame, text=text_str, font=('Segoe UI', font_size, 'bold'), style='Inverse.TLabel').pack(
            pady=(20, 10), padx=10, anchor=anchor)


class Menu(ttk.Frame):
    def __init__(self, parent, main):
        super().__init__(parent, style='Card.TFrame')
        self.main = main
        self.show = None
        self.configure(padding=10)
        self.place(x=0, y=0, relwidth=2 / 6, relheight=4 / 6)

        # Interner Container mit .pack()
        inner = ttk.Frame(self)
        inner.pack(fill=tk.BOTH, expand=True)

        App.ttk_label(inner, 'MENU', 'center')

        self.scroll_frame = ScrollableFrame(inner)
        self.scroll_frame.pack(fill=tk.BOTH, expand=True)

        self.create_widgets()

    def create_widgets(self):
        menu_buttons = [("LINUX COMMANDS", 'linux'), ("SQL COMMANDS", 'sql'), ("DATENTYPEN", 'datentypen'),
                        ("Exit", '')]

        for text, category in menu_buttons:
            if text == 'Exit':
                self.add_button(self.scroll_frame.scrollable_frame, text, self.quit)
            else:
                self.add_button(self.scroll_frame.scrollable_frame, text, lambda cat=category: self.open_show(cat))

    @staticmethod
    def add_button(frame, text, command, is_accent=False):
        style = 'Menu.TButton'
        if is_accent:
            style = 'Accent.TButton'
        btn = ttk.Button(frame, text=text, style=style, command=command)
        btn._is_dynamic = True
        btn.pack(fill=tk.X, pady=2, padx=10)

    def remove_buttons(self):
        for widget in self.scroll_frame.scrollable_frame.winfo_children():
            if getattr(widget, "_is_dynamic", False):
                widget.destroy()

    def open_show(self, category):
        self.show = Show(self.main, self)
        self.show.categories(category)

    def add_return_button(self):
        self.add_button(self.scroll_frame.scrollable_frame, "RETURN", self.show.return_to_main_menu)


class Main(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style='Card.TFrame')
        self.parent = parent
        self.place(relx=1 / 6, y=0, relwidth=1, relheight=1)

        self.content_frame = ttk.Frame(self)
        self.content_frame.place(relx=1 / 6, y=0, relwidth=4 / 6, relheight=4 / 6)
        output_frame = ttk.Frame(parent)
        output_frame.place(relx=0, rely=4 / 6, relwidth=1, relheight=2 / 6)

        self.command_display = TextOutput(output_frame, {'height': 10, 'width': 40, 'side': tk.LEFT})
        self.explanation_display = TextOutput(output_frame, {'height': 10, 'width': 60, 'side': tk.RIGHT})

        self.show_welcome_message(self.content_frame)

    def show_welcome_message(self, frame):
        self.clear_content_frame()
        App.ttk_label(frame, "Willkommen im Command Dashboard von xqi", 'w', 18)
        App.ttk_label(frame, "Wählen Sie eine Kategorie aus dem Menü links")

    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def clear_frames(self):
        self.clear_content_frame()
        self.clear_output_frame([self.command_display, self.explanation_display])

    @staticmethod
    def clear_output_frame(displays):
        for display in displays:
            display.config(state=tk.NORMAL)
            display.delete(1.0, tk.END)


class ScrollableFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Canvas & Scrollbar
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Inner Frame
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Layout
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Bindings
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", lambda e: self.after_idle(self._resize_inner_frame))

    def _on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        content_h = self.scrollable_frame.winfo_height()
        visible_h = self.canvas.winfo_height()

        if content_h > visible_h:
            self._bind_mousewheel()
        else:
            self._unbind_mousewheel()

    def _resize_inner_frame(self):
        self.canvas.update_idletasks()
        self.scrollbar.update_idletasks()

        canvas_w = self.canvas.winfo_width()
        scrollbar_w = self.scrollbar.winfo_width()
        if scrollbar_w < 10:
            scrollbar_w = 16  # fallback for early Wayland/Floating

        self.canvas.itemconfig(self.window_id, width=canvas_w - scrollbar_w)

    def _bind_mousewheel(self):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def _unbind_mousewheel(self):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


class TextOutput:
    def __init__(self, parent, dimensions):
        self.widget = tk.Text(parent, wrap=tk.WORD, font=('Consolas', 12), bg='#3d3d3d', fg='white',
                              insertbackground='white', height=dimensions['height'], width=dimensions['width'])
        self.widget.pack(side=dimensions['side'], fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.widget.config(padx=10, pady=10)
        self.widget.config(state=tk.DISABLED)
        self.widget.bind("<Button-1>", self.copy_to_clipboard)

    def insert(self, *args, **kwargs):
        self.widget.insert(*args, **kwargs)

    def config(self, *args, **kwargs):
        self.widget.config(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.widget.delete(*args, **kwargs)

    def copy_to_clipboard(self, event=None):
        self.widget.config(state=tk.NORMAL)
        content = self.widget.get("1.0", "end-1c")
        self.widget.clipboard_clear()
        self.widget.clipboard_append(content)
        self.widget.config(state=tk.DISABLED)
        # Optionales Feedback
        orig_bg = self.widget['bg']
        self.widget.config(bg='#145a32')
        self.widget.after(100, lambda: self.widget.config(bg=orig_bg))


class Show:
    def __init__(self, main, menu):
        self.main = main
        self.menu = menu

    def return_to_main_menu(self):
        self.main.clear_frames()
        self.menu.remove_buttons()
        self.menu.create_widgets()

    def commands(self, text, subcategory):
        self.clear_frames(False)
        App.ttk_label(self.main.content_frame, f'{text}')

        for btn_text, command in subcategory.items():
            command_function = lambda c=command['command'], e=command['explanation']: self.display_command(c, e)
            self.menu.add_button(self.main.content_frame, btn_text, command_function, True)

    def categories(self, category):
        self.clear_frames()
        for key, subcategory in COMMANDS[category].items():
            command_function = lambda k=key, s=subcategory: self.commands(k, s)
            self.menu.add_button(self.menu.scroll_frame.scrollable_frame, key, command_function)

        App.ttk_label(self.main.content_frame, "Wählen Sie eine Befehlskategorie aus dem Menü links")

    def display_command(self, command, explanation):
        displays = [self.main.command_display, self.main.explanation_display]
        self.main.clear_output_frame(displays)

        self.main.command_display.insert(tk.END, command)
        self.main.command_display.config(state=tk.DISABLED)
        self.main.explanation_display.insert(tk.END, explanation)
        self.main.explanation_display.config(state=tk.DISABLED)

    def clear_frames(self, clear_menu=True):
        self.main.clear_frames()
        if clear_menu != False:
            self.menu.remove_buttons()
            self.menu.add_return_button()


if __name__ == "__main__":
    app = App('Command Dashboard', (1200, 700))
    app.mainloop()
