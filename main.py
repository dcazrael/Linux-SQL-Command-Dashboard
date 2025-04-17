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
        sv_ttk.set_theme("dark")
        style.configure('Transparent.TFrame', background=self['bg'])
        style.configure('Card.TFrame', borderwidth=2, relief='raised', padding=10)
        style.configure('Inverse.TLabel', foreground='white', font=('Segoe UI', 11, 'bold'))
        style.configure('Menu.TButton', font=('Segoe UI', 12), anchor='w', padding=5)
        style.configure('Accent.TButton', font=('Segoe UI', 13, 'bold'), padding=6)

        # widgets
        self.main = Main(self)
        self.menu = Menu(self, self.main)

        # run
        self.mainloop()

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
        App.ttk_label(self, 'MENU', 'center')

        self.create_widgets()

    def create_widgets(self):
        menu_buttons = [("LINUX COMMANDS", 'linux'), ("SQL COMMANDS", 'sql'), ("DATENTYPEN", 'datentypen'),
                        ("Exit", '')]

        for text, category in menu_buttons:
            if text == 'Exit':
                btn = ttk.Button(self, text=text, style='Menu.TButton', command=self.quit)
            else:
                btn = ttk.Button(self, text=text, style='Menu.TButton',
                                 command=lambda cat=category: self.open_show(cat))

            btn.pack(fill=tk.X, pady=3, padx=10)

    @staticmethod
    def remove_buttons(frame):
        for widget in frame.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.destroy()

    def open_show(self, category):
        self.show = Show(self.main, self)
        self.show.categories(category)

    def add_return_button(self, frame):
        ttk.Button(frame, text="RETURN", style='Menu.TButton', command=self.show.return_to_main_menu).pack(fill=tk.X,
                                                                                                           pady=2,
                                                                                                           padx=10)


class Main(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style='Card.TFrame')
        self.parent = parent
        self.place(relx=1 / 6, y=0, relwidth=1, relheight=1)

        self.content_frame = SubFrame(self, 'place', relx=1 / 6, y=0, relwidth=4 / 6, relheight=4 / 6)
        output_frame = SubFrame(parent, 'place', relx=0, rely=4 / 6, relwidth=1, relheight=2 / 6)

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


class SubFrame(ttk.Frame):
    def __init__(self, parent, position='pack', **kwargs):
        super().__init__(parent, style='Card.TFrame')
        self.configure(padding=10)
        if position == 'pack':
            self.pack(**kwargs)
        if position == 'place':
            self.place(**kwargs)


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
        self.widget.after(300, lambda: self.widget.config(bg=orig_bg))


class Show:
    def __init__(self, main, menu):
        self.main = main
        self.menu = menu

    def return_to_main_menu(self):
        self.main.clear_frames()

        Menu.remove_buttons(self.menu)
        self.menu.create_widgets()

    def commands(self, text, subcategory):
        self.main.clear_content_frame()

        App.ttk_label(self.main.content_frame, text)

        for btn_text, command in subcategory.items():
            btn = ttk.Button(self.main.content_frame, text=btn_text, style='Accent.TButton',
                             command=lambda c=command['command'], e=command['explanation']: self.display_command(c, e))
            btn.pack(fill=tk.X, padx=50, pady=5)

    def categories(self, category):
        self.main.clear_frames()
        Menu.remove_buttons(self.menu)
        self.menu.add_return_button(self.menu)

        for key, subcategory in COMMANDS[category].items():
            btn = ttk.Button(self.menu, text=key, style='Menu.TButton',
                             command=lambda k=key, s=subcategory: self.commands(k, s))
            btn.pack(fill=tk.X, pady=2, padx=10)

        App.ttk_label(self.main.content_frame, "Wählen Sie eine Befehlskategorie aus dem Menü links")

    def display_command(self, command, explanation):
        displays = [self.main.command_display, self.main.explanation_display]
        self.main.clear_output_frame(displays)

        self.main.command_display.insert(tk.END, command)
        self.main.command_display.config(state=tk.DISABLED)
        self.main.explanation_display.insert(tk.END, explanation)
        self.main.explanation_display.config(state=tk.DISABLED)


if __name__ == "__main__":
    App('Command Dashboard', (1200, 700))
