# ...existing code...
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yaml
import glob
import os
import subprocess
from pathlib import Path

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

        # Training selection
        ttk.Label(container, text='Select Training:').grid(row=0, column=0, sticky='w')
        self.training_var = tk.StringVar()
        self.training_combo = ttk.Combobox(container, textvariable=self.training_var, state='readonly', width=40)
        self.training_combo.grid(row=0, column=1, sticky='w', padx=8, pady=6)
        self.training_combo.bind('<<ComboboxSelected>>', self.on_select_training)

        self.load_training_list()

        # Params frame
        self.params_frame = ttk.Frame(container, padding=10, borderwidth=1, relief='groove')
        self.params_frame.grid(row=1, column=0, columnspan=2, pady=10)

        # Lever name inputs
        ttk.Label(container, text='Lever 1 Name:').grid(row=2, column=0, sticky='e')
        self.lever1_var = tk.StringVar(value='Lever1')
        self.lever1_entry = ttk.Entry(container, textvariable=self.lever1_var, width=30)
        self.lever1_entry.grid(row=2, column=1, sticky='w', padx=8, pady=4)

        ttk.Label(container, text='Lever 2 Name:').grid(row=3, column=0, sticky='e')
        self.lever2_var = tk.StringVar(value='Lever2')
        self.lever2_entry = ttk.Entry(container, textvariable=self.lever2_var, width=30)
        self.lever2_entry.grid(row=3, column=1, sticky='w', padx=8, pady=4)

        # GlobalParameter File row (store label so we can hide/show)
        self.globalparam_label = ttk.Label(container, text='GlobalParameter File:')
        self.globalparam_label.grid(row=4, column=0, sticky='e')
        self.globalparam_var = tk.StringVar()
        self.gp_frame = ttk.Frame(container)
        self.gp_frame.grid(row=4, column=1, sticky='w', padx=8, pady=4)
        self.globalparam_entry = ttk.Entry(self.gp_frame, textvariable=self.globalparam_var, width=30)
        self.globalparam_entry.pack(side='left')
        ttk.Button(self.gp_frame, text="Browse", command=self.browse_globalparam).pack(side='left', padx=4)

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

        # status
        self.status_var = tk.StringVar(value='Ready')
        ttk.Label(container, textvariable=self.status_var).grid(row=7, column=0, columnspan=2)

        self.param_widgets = {}
        if self.training_combo['values']:
            self.training_combo.current(0)
            self.on_select_training()

    def load_training_list(self):
        files = sorted(glob.glob(str(TRAININGS_DIR / '*.yaml')))
        self.yaml_files = files
        names = [os.path.basename(f) for f in files]
        self.training_combo['values'] = names

    def on_select_training(self, event=None):
        sel = self.training_combo.get()
        if not sel:
            return
        path = TRAININGS_DIR / sel
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
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

            # render dropdown
            if ptype == 'dropdown':
                ttk.Label(self.params_frame, text=key+':').grid(row=row, column=0, sticky='e', padx=6, pady=4)
                opts = meta.get('options', [])
                var = tk.StringVar(value=str(actual))
                cmb = ttk.Combobox(self.params_frame, textvariable=var, values=opts, state='readonly')
                cmb.grid(row=row, column=1, sticky='w', padx=6, pady=4)
                self.param_widgets[key] = (ptype, var)
                row += 1
                continue

            # render boolean
            elif ptype == 'bool':
                var = tk.BooleanVar(value=bool(actual))
                chk = ttk.Checkbutton(self.params_frame, text=key, variable=var)
                chk.grid(row=row, column=0, columnspan=2, sticky='w', padx=6, pady=4)
                self.param_widgets[key] = (ptype, var)
                row += 1
                continue

            # lists and plain text
            elif ptype.startswith('list'):
                ttk.Label(self.params_frame, text=key+':').grid(row=row, column=0, sticky='e', padx=6, pady=4)
                var = tk.StringVar(value=str(actual))
                ent = ttk.Entry(self.params_frame, textvariable=var, width=40)
                ent.grid(row=row, column=1, sticky='w', padx=6, pady=4)
                self.param_widgets[key] = (ptype, var)
                row += 1
                continue

            # file / filepath parameter -> entry + Browse button
            # also treat parameters whose key suggests a path/file (e.g. contains 'path', 'file', 'params', 'param')
            elif ptype in ('file', 'filepath', 'path') or any(substr in key.lower() for substr in ('path', 'file', 'params', 'param')):
                ttk.Label(self.params_frame, text=key+':').grid(row=row, column=0, sticky='e', padx=6, pady=4)
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
                ttk.Button(frame, text='Browse', command=_browse).pack(side='left', padx=6)
                self.param_widgets[key] = (ptype, var)
                row += 1
                continue

            # default string/int/float entry
            else:
                ttk.Label(self.params_frame, text=key+':').grid(row=row, column=0, sticky='e', padx=6, pady=4)
                var = tk.StringVar(value=str(actual))
                ent = ttk.Entry(self.params_frame, textvariable=var, width=40)
                ent.grid(row=row, column=1, sticky='w', padx=6, pady=4)
                self.param_widgets[key] = (ptype, var)
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
            self.globalparam_label.grid()
            self.gp_frame.grid()
            self.runner_label.grid()
            self.runner_frame.grid()
            self.start_btn.grid()
        else:
            self.globalparam_label.grid_remove()
            self.gp_frame.grid_remove()
            self.runner_label.grid_remove()
            self.runner_frame.grid_remove()
            self.start_btn.grid_remove()

    def save_params(self):
        sel = self.training_combo.get()
        if not sel:
            return
        path = TRAININGS_DIR / sel
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
        path = TRAININGS_DIR / sel
        # read TaskName to get class name
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        task_meta = data.get('parameters', {}).get('TaskName', {})
        task_name = task_meta.get('actual') or task_meta.get('default') or Path(sel).stem
        # launch subprocess
        lever1 = self.lever1_var.get() or 'Lever1'
        lever2 = self.lever2_var.get() or 'Lever2'
        globalparam = self.globalparam_var.get() or ''
        runner = self.runner_var.get()
        if runner == 'main':
            cmd = ["python", str(MAIN_SCRIPT), task_name, str(path), lever1, lever2, globalparam]
        else:
            cmd = ["python", str(PYGAME_SCRIPT), task_name, str(path), lever1, lever2, globalparam]
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

if __name__ == '__main__':
    app = TrainingGUI()
    app.mainloop()
