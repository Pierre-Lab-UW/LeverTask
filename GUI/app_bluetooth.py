import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yaml
import glob
import os
import subprocess
import threading
from pathlib import Path
from queue import Queue
import sys

# Add Bluetooth module to path
BLUETOOTH_DIR = Path(__file__).resolve().parents[1] / 'Bluetooth'
if str(BLUETOOTH_DIR) not in sys.path:
    sys.path.insert(0, str(BLUETOOTH_DIR))

from Bluetooth.client import BluetoothClient

ROOT = Path(__file__).resolve().parents[1]
TRAININGS_DIR = ROOT / 'Trainings'
PYGAME_SCRIPT = ROOT / 'pygame_simulation.py'
MAIN_SCRIPT = ROOT / 'main.py'

# Predefined list of Bluetooth MAC addresses
BLUETOOTH_DEVICES = [
    "00:1A:7D:DA:71:13",
    "5C:F3:70:8C:4D:AA",
    "94:B8:6D:52:F4:D1",
    "AC:DE:48:00:11:22",
]

class BluetoothManager:
    """Manages Bluetooth connection and communication."""
    def __init__(self, log_queue):
        self.client = None
        self.log_queue = log_queue
        self.mac = None

    def connect(self, mac):
        """Connect to Bluetooth device."""
        try:
            self.client = BluetoothClient(mac, channel=1, timeout=10)
            self.client.connect()
            self.mac = mac
            self.log_queue.put(f"Connected to {mac}")
            return True
        except Exception as e:
            self.log_queue.put(f"Connection failed: {str(e)}")
            self.client = None
            return False

    def disconnect(self):
        """Disconnect from Bluetooth device."""
        if self.client:
            self.client.disconnect()
            self.log_queue.put("Disconnected from device")
            self.client = None

    @property
    def connected(self):
        """Check if connected."""
        return self.client is not None and self.client.connected

    def send_file(self, training_id, path):
        """Send file to device."""
        if not self.connected:
            self.log_queue.put("Error: Not connected to device")
            return False
        try:
            response = self.client.send_file(training_id, path)
            self.log_queue.put(f"File sent: {response}")
            return True
        except Exception as e:
            self.log_queue.put(f"Send failed: {str(e)}")
            return False

    def start_training(self, training_id):
        """Start training on device."""
        if not self.connected:
            self.log_queue.put("Error: Not connected to device")
            return False
        try:
            response = self.client.start_training(training_id)
            self.log_queue.put(f"Start training: {response}")
            return True
        except Exception as e:
            self.log_queue.put(f"Start failed: {str(e)}")
            return False

class TrainingGUIBluetooth(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Training Runner with Bluetooth')
        self.geometry('900x900')
        self.resizable(False, False)
        self.eval('tk::PlaceWindow . center')

        self.current_file_path = ''
        
        # Queue for thread-safe logging
        self.log_queue = Queue()
        self.bluetooth = BluetoothManager(self.log_queue)
        
        # Create main container
        main_container = ttk.Frame(self)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)

        # ===== BLUETOOTH SECTION =====
        bt_frame = ttk.LabelFrame(main_container, text='Bluetooth Connection', padding=10)
        bt_frame.pack(fill='x', pady=10)

        ttk.Label(bt_frame, text='Device MAC:').grid(row=0, column=0, sticky='w')
        self.bt_var = tk.StringVar()
        self.bt_combo = ttk.Combobox(bt_frame, textvariable=self.bt_var, values=BLUETOOTH_DEVICES, state='readonly', width=25)
        self.bt_combo.grid(row=0, column=1, sticky='w', padx=8, pady=4)

        self.bt_connect_btn = ttk.Button(bt_frame, text='Connect', command=self.connect_bluetooth)
        self.bt_connect_btn.grid(row=0, column=2, padx=6)

        self.bt_disconnect_btn = ttk.Button(bt_frame, text='Disconnect', command=self.disconnect_bluetooth, state='disabled')
        self.bt_disconnect_btn.grid(row=0, column=3, padx=6)

        self.bt_status_var = tk.StringVar(value='Not connected')
        ttk.Label(bt_frame, textvariable=self.bt_status_var, foreground='red').grid(row=1, column=0, columnspan=4, sticky='w', pady=4)

        # ===== TRAINING SECTION =====
        training_frame = ttk.LabelFrame(main_container, text='Training Configuration', padding=10)
        training_frame.pack(fill='x', pady=10)

        ttk.Label(training_frame, text='Select Training:').grid(row=0, column=0, sticky='w')
        self.training_var = tk.StringVar()
        self.training_combo = ttk.Combobox(training_frame, textvariable=self.training_var, state='readonly', width=40)
        self.training_combo.grid(row=0, column=1, sticky='w', padx=8, pady=6)
        self.training_combo.bind('<<ComboboxSelected>>', self.on_select_training)

        self.load_training_list()

        # Params frame
        self.params_frame = ttk.Frame(training_frame, padding=10, borderwidth=1, relief='groove')
        self.params_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky='nsew')

        # Runner selection
        self.runner_label = ttk.Label(training_frame, text='Runner:')
        self.runner_label.grid(row=5, column=0, sticky='e')
        self.runner_var = tk.StringVar(value='pygame')
        self.runner_frame = ttk.Frame(training_frame)
        self.runner_frame.grid(row=5, column=1, sticky='w', padx=8, pady=4)
        ttk.Radiobutton(self.runner_frame, text='Pygame', value='pygame', variable=self.runner_var).pack(side='left')
        ttk.Radiobutton(self.runner_frame, text='Main', value='main', variable=self.runner_var).pack(side='left')

        # Action Buttons
        btn_frame = ttk.Frame(training_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=8)
        self.save_btn = ttk.Button(btn_frame, text='Save Params', command=self.save_params)
        self.save_btn.grid(row=0, column=0, padx=6)
        self.start_btn = ttk.Button(btn_frame, text='Start Training (Local)', command=self.start_training)
        self.start_btn.grid(row=0, column=1, padx=6)
        self.send_config_btn = ttk.Button(btn_frame, text='Send Config to Device', command=self.send_config_to_device, state='disabled')
        self.send_config_btn.grid(row=0, column=2, padx=6)

        # Status
        self.status_var = tk.StringVar(value='Ready')
        ttk.Label(training_frame, textvariable=self.status_var).grid(row=7, column=0, columnspan=2)

        # ===== LOG SECTION =====
        log_frame = ttk.LabelFrame(main_container, text='Device Logs', padding=10)
        log_frame.pack(fill='both', expand=True, pady=10)

        # Text widget for logs with scrollbar
        scrollbar = ttk.Scrollbar(log_frame)
        scrollbar.pack(side='right', fill='y')

        self.log_text = tk.Text(log_frame, height=15, width=100, yscrollcommand=scrollbar.set, state='disabled')
        self.log_text.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.log_text.yview)

        # Clear logs button
        ttk.Button(log_frame, text='Clear Logs', command=self.clear_logs).pack(pady=4)

        self.param_widgets = {}
        
        # Start log polling
        self.poll_logs()

        if self.training_combo['values']:
            self.training_combo.current(0)
            self.on_select_training()

    def load_training_list(self):
        files = sorted(glob.glob(str(TRAININGS_DIR / '*.yaml')))
        self.yaml_files = files
        names = [os.path.basename(f) for f in files]
        self.training_combo['values'] = names

    class Tooltip:
        """Simple tooltip for Tk widgets."""
        def __init__(self, widget, text: str, delay: int = 500):
            self.widget = widget
            self.text = text
            self.delay = delay
            self.tipwindow = None
            self._after_id = None
            widget.bind("<Enter>", self._on_enter, add="+")
            widget.bind("<Leave>", self._on_leave, add="+")
            widget.bind("<ButtonPress>", self._on_leave, add="+")

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

    def connect_bluetooth(self):
        """Connect to Bluetooth device."""
        mac = self.bt_var.get()
        if not mac:
            messagebox.showerror('Error', 'Please select a MAC address')
            return

        self.bt_status_var.set('Connecting...')
        self.bt_status_var.set('Connecting...')
        
        # Connect in a thread to avoid blocking UI
        def connect_thread():
            success = self.bluetooth.connect(mac)
            if success:
                self.bt_status_var.set(f'Connected to {mac}')
                self.bt_status_var.set(f'Connected: {mac}')
                self.bt_connect_btn.config(state='disabled')
                self.bt_disconnect_btn.config(state='normal')
                self.send_config_btn.config(state='normal')
            else:
                self.bt_status_var.set('Connection failed')
                self.bt_status_var.set('Connection failed (check logs)')

        thread = threading.Thread(target=connect_thread, daemon=True)
        thread.start()

    def disconnect_bluetooth(self):
        """Disconnect from Bluetooth device."""
        self.bluetooth.disconnect()
        self.bt_status_var.set('Not connected')
        self.bt_connect_btn.config(state='normal')
        self.bt_disconnect_btn.config(state='disabled')
        self.send_config_btn.config(state='disabled')

    def send_config_to_device(self):
        """Send training config YAML file to device."""
        if not self.bluetooth.connected:
            messagebox.showerror('Error', 'Not connected to device')
            return

        sel = self.training_combo.get()
        if not sel:
            messagebox.showerror('Error', 'No training selected')
            return

        path = TRAININGS_DIR / sel
        training_id = Path(sel).stem

        def send_thread():
            success = self.bluetooth.send_file(training_id, str(path))
            if success:
                self.status_var.set(f'Sent {sel} to device')
            else:
                self.status_var.set('Failed to send file')

        thread = threading.Thread(target=send_thread, daemon=True)
        thread.start()

    def poll_logs(self):
        """Poll log queue and update GUI."""
        while not self.log_queue.empty():
            try:
                msg = self.log_queue.get_nowait()
                self.log_text.config(state='normal')
                self.log_text.insert('end', msg + '\n')
                self.log_text.see('end')
                self.log_text.config(state='disabled')
            except:
                break

        self.after(500, self.poll_logs)

    def clear_logs(self):
        """Clear log display."""
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', 'end')
        self.log_text.config(state='disabled')

    def on_select_training(self, event=None):
        sel = self.training_combo.get()
        if not sel:
            return
        path = TRAININGS_DIR / sel
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

            # file / filepath parameter
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
                ttk.Button(frame, text='Browse', command=_browse).pack(side='left', padx=6)
                self.param_widgets[key] = (ptype, var)
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

        # determine runnable flag
        runnable_meta = params.get('runnable', {})
        runnable_actual = runnable_meta.get('actual', runnable_meta.get('default', False))
        if isinstance(runnable_actual, str):
            runnable_bool = runnable_actual.lower() in ('true', '1', 'yes')
        else:
            runnable_bool = bool(runnable_actual)

        self.set_run_controls_visible(runnable_bool)

    def set_run_controls_visible(self, visible: bool):
        """Toggle visibility of run-related widgets."""
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
                data['parameters'][key]['actual'] = bool(val)
            elif ptype.startswith('list'):
                try:
                    parsed = eval(val)
                    data['parameters'][key]['actual'] = parsed
                except Exception:
                    data['parameters'][key]['actual'] = val
            else:
                data['parameters'][key]['actual'] = val
        
        with open(path, 'w') as f:
            yaml.safe_dump(data, f)
        self.status_var.set('Saved parameters')

    def start_training(self):
        sel = self.training_combo.get()
        if not sel:
            return
        path = TRAININGS_DIR / sel
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        task_meta = data.get('parameters', {}).get('TaskName', {})
        task_name = task_meta.get('actual') or task_meta.get('default') or Path(sel).stem
        runner = self.runner_var.get()
        
        if runner == 'main':
            cmd = ["python", str(MAIN_SCRIPT), str(self.current_file_path)]
        else:
            cmd = ["python", str(PYGAME_SCRIPT), str(self.current_file_path)]
        
        try:
            subprocess.Popen(cmd)
            self.status_var.set(f'Launched {task_name}')
        except Exception as e:
            messagebox.showerror('Error', str(e))

if __name__ == '__main__':
    app = TrainingGUIBluetooth()
    app.mainloop()
