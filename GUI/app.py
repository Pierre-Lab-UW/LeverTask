# ...existing code...
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yaml
import glob
import os
import subprocess
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[1]
TRAININGS_DIR = ROOT / 'Trainings'
PYGAME_SCRIPT = ROOT / 'pygame_simulation.py'
MAIN_SCRIPT = ROOT / 'main.py'

class TrainingGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Training Runner')
        self.geometry('700x700')
        self.resizable(False, False)
        # center window
        self.eval('tk::PlaceWindow . center')

        container = ttk.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor='center')

        #current file path
        self.current_file_path = ''
        self.names_to_paths: dict[str, str] = {}

        # Training selection
        ttk.Label(container, text='Select Training:').grid(row=0, column=0, sticky='w')
        self.training_var = tk.StringVar()
        self.training_combo = ttk.Combobox(container, textvariable=self.training_var, state='readonly', width=40)
        self.training_combo.grid(row=0, column=1, sticky='w', padx=8, pady=6)
        self.training_combo.bind('<<ComboboxSelected>>', self.on_select_training)

        # Params frame with scrolling
        params_wrapper = ttk.Frame(container)
        params_wrapper.grid(row=1, column=0, columnspan=2, pady=10, sticky='nsew')
        
        # Create canvas and scrollbar
        self.params_canvas = tk.Canvas(params_wrapper, height=250, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(params_wrapper, orient='vertical', command=self.params_canvas.yview)
        self.params_frame = ttk.Frame(self.params_canvas, padding=10)
        
        self.params_canvas.configure(yscrollcommand=scrollbar.set)
        self.params_canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Create window in canvas
        self.params_window_id = self.params_canvas.create_window((0, 0), window=self.params_frame, anchor='nw')
        
        # Bind mousewheel for scrolling
        def _on_mousewheel(event):
            self.params_canvas.yview_scroll(int(-1*(event.delta/120)), 'units')
        self.params_canvas.bind_all('<MouseWheel>', _on_mousewheel)
        
        # Update scroll region when frame is configured
        def _update_scroll_region(event=None):
            self.params_canvas.configure(scrollregion=self.params_canvas.bbox('all'))
        self.params_frame.bind('<Configure>', _update_scroll_region)

        # Runner selection (store label so we can hide/show)
        self.runner_label = ttk.Label(container, text='Runner:')
        self.runner_label.grid(row=5, column=0, sticky='e')
        self.runner_var = tk.StringVar(value='pygame')
        self.runner_frame = ttk.Frame(container)
        self.runner_frame.grid(row=5, column=1, sticky='w', padx=8, pady=4)
        ttk.Radiobutton(self.runner_frame, text='Pygame', value='pygame', variable=self.runner_var).pack(side='left')
        ttk.Radiobutton(self.runner_frame, text='Main', value='main', variable=self.runner_var).pack(side='left')

        # Buttons
        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=8)
        self.save_btn = ttk.Button(btn_frame, text='Save Params', command=self.save_params)
        self.save_btn.grid(row=0, column=0, padx=6)
        self.start_btn = ttk.Button(btn_frame, text='Start Training', command=self.start_training)
        self.start_btn.grid(row=0, column=1, padx=6)

        
        self.load_file_btn = ttk.Button(btn_frame, text='Load File', command=self.browse_param_file)
        self.load_file_btn.grid(row=0, column=2, padx=6)


        # status
        self.status_var = tk.StringVar(value='Ready')
        ttk.Label(container, textvariable=self.status_var).grid(row=7, column=0, columnspan=2)

        self.param_widgets = {}
        if self.training_combo['values']:
            self.training_combo.current(0)
            self.on_select_training()

    # --- Tooltip helper ---
    class Tooltip:
        """Simple tooltip for Tk widgets. Shows small window with text on hover."""
        def __init__(self, widget, text: str, delay: int = 500):
            self.widget = widget
            self.text = text
            self.delay = delay
            self.tipwindow = None
            self._after_id = None
            widget.bind("<Enter>", self._on_enter, add="+")
            widget.bind("<Leave>", self._on_leave, add="+")
            widget.bind("<ButtonPress>", self._on_leave, add="+")  # hide on click

        def _on_enter(self, _ev=None):
            self._schedule()

        def _on_leave(self, _ev=None):
            self._unschedule()
            self._hide()

        def _schedule(self):
            self._unschedule()
            try:
                self._after_id = self.widget.after(self.delay, self._show)
            except Exception:
                self._after_id = None

        def _unschedule(self):
            if self._after_id:
                try:
                    self.widget.after_cancel(self._after_id)
                except Exception:
                    pass
                self._after_id = None

        def _show(self):
            if self.tipwindow or not self.text:
                return
            x = self.widget.winfo_rootx() + 20
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
            self.tipwindow = tw = tk.Toplevel(self.widget)
            tw.wm_overrideredirect(True)
            tw.wm_geometry(f"+{x}+{y}")
            label = tk.Label(tw, text=self.text, justify='left', background='#ffffe0', relief='solid', borderwidth=1,
                             font=("tahoma", "8"), wraplength=300)
            label.pack(ipadx=4, ipady=2)

        def _hide(self):
            if self.tipwindow:
                try:
                    self.tipwindow.destroy()
                except Exception:
                    pass
                self.tipwindow = None

    def on_select_training(self, event=None):
        sel = self.training_combo.get()
        if not sel:
            return
        path = self.names_to_paths[sel]
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        self.current_file_path = path
        params = data.get('parameters', {})
        # clear frame
        for w in self.params_frame.winfo_children():
            w.destroy()
        self.param_widgets = {}
        row = 0
        for key, meta in params.items():
            # skip hidden parameters (default: not hidden)
            if meta.get('hidden', False):
                continue

            ptype = meta.get('type', 'str')
            actual = meta.get('actual', meta.get('default', ''))
            description = meta.get('description', '')

            # render dropdown
            if ptype == 'dropdown':
                label = ttk.Label(self.params_frame, text=key+':')
                label.grid(row=row, column=0, sticky='e', padx=6, pady=4)
                opts = meta.get('options', [])
                var = tk.StringVar(value=str(actual))
                cmb = ttk.Combobox(self.params_frame, textvariable=var, values=opts, state='readonly')
                cmb.grid(row=row, column=1, sticky='w', padx=6, pady=4)
                self.param_widgets[key] = (ptype, var)
                # attach tooltip (prefer label, else combobox)
                if description:
                    self.Tooltip(label, description)
                row += 1
                continue

            # render boolean
            elif ptype == 'bool':
                var = tk.BooleanVar(value=bool(actual))
                chk = ttk.Checkbutton(self.params_frame, text=key, variable=var)
                chk.grid(row=row, column=0, columnspan=2, sticky='w', padx=6, pady=4)
                self.param_widgets[key] = (ptype, var)
                if description:
                    self.Tooltip(chk, description)
                row += 1
                continue

            # lists and plain text
            elif ptype.startswith('list'):
                label = ttk.Label(self.params_frame, text=key+':')
                label.grid(row=row, column=0, sticky='e', padx=6, pady=4)
                var = tk.StringVar(value=str(actual))
                ent = ttk.Entry(self.params_frame, textvariable=var, width=40)
                ent.grid(row=row, column=1, sticky='w', padx=6, pady=4)
                self.param_widgets[key] = (ptype, var)
                if description:
                    self.Tooltip(ent, description)
                row += 1
                continue

            # file / filepath parameter -> entry + Browse button
            elif ptype in ('file', 'filepath', 'path'):
                label = ttk.Label(self.params_frame, text=key+':')
                label.grid(row=row, column=0, sticky='e', padx=6, pady=4)
                var = tk.StringVar(value=str(actual))
                frame = ttk.Frame(self.params_frame)
                frame.grid(row=row, column=1, sticky='w', padx=6, pady=4)
                ent = ttk.Entry(frame, textvariable=var, width=30)
                ent.pack(side='left', fill='x', expand=True)
                def _browse(v=var, k=key):
                    file_path = filedialog.askopenfilename(
                        title=f"Select file for {k}",
                        filetypes=[("YAML files", "*.yaml *.yml"), ("All files", "*.*")]
                    )
                    if file_path:
                        v.set(file_path)
                        # list_values = list(self.training_combo['values'])
                        # list_values.append(file_path)
                        # self.training_combo['values'] = tuple(list_values)

                ttk.Button(frame, text='Browse', command=_browse).pack(side='left', padx=6)
                self.param_widgets[key] = (ptype, var)
                # tooltip attached to entry
                if description:
                    self.Tooltip(ent, description)
                row += 1
                continue

            # default string/int/float entry
            else:
                label = ttk.Label(self.params_frame, text=key+':')
                label.grid(row=row, column=0, sticky='e', padx=6, pady=4)
                var = tk.StringVar(value=str(actual))
                ent = ttk.Entry(self.params_frame, textvariable=var, width=40)
                ent.grid(row=row, column=1, sticky='w', padx=6, pady=4)
                self.param_widgets[key] = (ptype, var)
                if description:
                    self.Tooltip(ent, description)
                row += 1
                continue

        self.status_var.set(f'Loaded {sel}')

        # determine runnable flag from YAML metadata (default False)
        runnable_meta = params.get('runnable', {})
        runnable_actual = runnable_meta.get('actual', runnable_meta.get('default', False))
        # coerce common string forms if necessary
        if isinstance(runnable_actual, str):
            runnable_bool = runnable_actual.lower() in ('true', '1', 'yes')
        else:
            runnable_bool = bool(runnable_actual)

        # show/hide run-related controls
        self.set_run_controls_visible(runnable_bool)

    def set_run_controls_visible(self, visible: bool):
        """Toggle visibility of run-related widgets (global params row, runner, start)."""
        if visible:
            self.runner_label.grid()
            self.runner_frame.grid()
            self.start_btn.grid()
        else:
            self.runner_label.grid_remove()
            self.runner_frame.grid_remove()
            self.start_btn.grid_remove()

    def save_params(self):
        sel = self.training_combo.get()
        if not sel:
            return
        path = self.names_to_paths[sel]
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        for key, (ptype, var) in self.param_widgets.items():
            val = var.get()
            if ptype == 'int':
                try:
                    data['parameters'][key]['actual'] = int(val)
                except ValueError:
                    messagebox.showerror('Invalid', f'Parameter {key} expects int')
                    return
            elif ptype == 'float':
                try:
                    data['parameters'][key]['actual'] = float(val)
                except ValueError:
                    messagebox.showerror('Invalid', f'Parameter {key} expects float')
                    return
            elif ptype == 'bool':
                # BooleanVar.get() already returns bool
                data['parameters'][key]['actual'] = bool(val)
            elif ptype.startswith('list'):
                try:
                    parsed = eval(val)
                    data['parameters'][key]['actual'] = parsed
                except Exception:
                    data['parameters'][key]['actual'] = val
            else:
                # includes 'str', 'file', 'filepath', 'path', etc.
                data['parameters'][key]['actual'] = val
        with open(path, 'w') as f:
            yaml.safe_dump(data, f)
        self.status_var.set('Saved parameters')

    def start_training(self):
        sel = self.training_combo.get()
        if not sel:
            return
        path = self.names_to_paths[sel]
        # read TaskName to get class name
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        task_meta = data.get('parameters', {}).get('TaskName', {})
        task_name = task_meta.get('actual') or task_meta.get('default') or Path(sel).stem
        runner = self.runner_var.get()
        if runner == 'main':
            cmd = ["python", str(MAIN_SCRIPT), self.current_file_path]
        else:
            cmd = ["python", str(PYGAME_SCRIPT), self.current_file_path]
        try:
            subprocess.Popen(cmd)
            self.status_var.set(f'Launched {task_name}')
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def browse_globalparam(self):
        file_path = filedialog.askopenfilename(
            title="Select GlobalParameter File",
            filetypes=[("YAML files", "*.yaml *.yml"), ("All files", "*.*")]
        )
        if file_path:
            self.globalparam_var.set(file_path)
            if file_path not in self.training_combo['values']:
                self.training_combo['values'].append(file_path)

    
    def browse_param_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Parameter File to Open",
            filetypes=[("YAML files", "*.yaml *.yml"), ("All files", "*.*")]
        )
        if not file_path:
            return
        
        file_name = Path(file_path).stem
        if file_name in self.names_to_paths:
            if not self.names_to_paths[file_name] == file_path:
                while True:
                    file_name = file_name + str(random.randint(1,10))
                    if file_name not in self.names_to_paths:
                        break
            else:
                self.training_combo.set(file_name)
                self.training_combo.event_generate('<<ComboboxSelected>>')
                return
        
        self.names_to_paths[file_name] = file_path
        list_values = list(self.training_combo['values'])
        list_values.append(file_name)
        self.training_combo['values'] = tuple(list_values)
        self.training_combo.set(file_name)
        self.training_combo.event_generate('<<ComboboxSelected>>')

                
                
            

if __name__ == '__main__':
    app = TrainingGUI()
    app.mainloop()
