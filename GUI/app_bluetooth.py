import sys
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from pathlib import Path

try:
    from Bluetooth.client import *
except Exception:
    # If running the script directly (sys.path[0]==GUI/), the top-level
    # package folder may not be on sys.path. Add the project root so
    # imports like `Bluetooth.client` resolve when launched as a script.
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))
    from Bluetooth.client import *

try:
    from GUI.app import TrainingGUI
except Exception:
    # fallback if module import path differs
    from app import TrainingGUI

class TrainingBluetoothGUI(TrainingGUI):
    """Extends existing TrainingGUI with Bluetooth controls for sending
    training files and starting sessions remotely.
    """
    def __init__(self):
        super().__init__()

        # Bluetooth client instance
        self.bt_client = None
        # monitor thread controls
        self.bt_monitor_stop = None
        self.bt_monitor_thread = None

        # Bluetooth controls frame at bottom of window
        self.bt_frame = ttk.LabelFrame(self, text='Bluetooth', padding=8)
        self.bt_frame.place(relx=0.5, rely=0.88, anchor='center')

        ttk.Label(self.bt_frame, text='MAC:').grid(row=0, column=0, sticky='e')
        self.mac_var = tk.StringVar(value='')
        ttk.Entry(self.bt_frame, textvariable=self.mac_var, width=20).grid(row=0, column=1, padx=4)

        ttk.Label(self.bt_frame, text='Channel:').grid(row=0, column=2, sticky='e')
        self.chan_var = tk.IntVar(value=1)
        ttk.Entry(self.bt_frame, textvariable=self.chan_var, width=6).grid(row=0, column=3, padx=4)

        self.connect_btn = ttk.Button(self.bt_frame, text='Connect', command=self._connect_bt)
        self.connect_btn.grid(row=0, column=4, padx=6)

        self.disconnect_btn = ttk.Button(self.bt_frame, text='Disconnect', command=self._disconnect_bt, state='disabled')
        self.disconnect_btn.grid(row=0, column=5, padx=6)

        # actions
        self.send_btn = ttk.Button(self.bt_frame, text='Send Training', command=self._send_training_to_device, state='disabled')
        self.send_btn.grid(row=1, column=0, columnspan=2, pady=6, sticky='w')

        self.start_remote_btn = ttk.Button(self.bt_frame, text='Start Remote', command=self._start_remote_training, state='disabled')
        self.start_remote_btn.grid(row=1, column=2, columnspan=2, pady=6)

        self.stop_btn = ttk.Button(self.bt_frame, text='Stop Training', command=self._stop_training, state='disabled')
        self.stop_btn.grid(row=1, column=4, padx=6)

        self.request_btn = ttk.Button(self.bt_frame, text='Request File', command=self._request_file, state='disabled')
        self.request_btn.grid(row=1, column=5, columnspan=2, pady=6)

        self.bt_status_var = tk.StringVar(value='Bluetooth: disconnected')
        ttk.Label(self.bt_frame, textvariable=self.bt_status_var).grid(row=2, column=0, columnspan=6, pady=(6,0), sticky='w')

        self.set_run_controls_visible(False)
    # --- Bluetooth helper wrappers (run in threads) ---
    def _connect_bt(self):
        if TrainingBluetoothClient is None:
            messagebox.showerror('Bluetooth', 'Bluetooth client not available (missing import).')
            return

        mac = self.mac_var.get().strip()
        chan = int(self.chan_var.get())
        if not mac:
            messagebox.showwarning('Bluetooth', 'Enter a MAC address')
            return

        def do_connect():
            try:
                self.status_var.set(f'Connecting to {mac}:{chan}...')
                self.bt_client = TrainingBluetoothClient(mac, chan)
                self.bt_client.connect()
                self.connect_btn.config(state='disabled')
                self.disconnect_btn.config(state='normal')
                self.send_btn.config(state='normal')
                self.start_remote_btn.config(state='normal')
                self.stop_btn.config(state='normal')
                self.request_btn.config(state='normal')
                self._set_bt_status('connected')
                # start background monitor to detect dropped connections
                self._start_bt_monitor()
                messagebox.showinfo('Bluetooth', f'Connected to {mac}')
            except Exception as e:
                self.status_var.set('Bluetooth connect failed')
                self._set_bt_status('disconnected')
                messagebox.showerror('Bluetooth Connect', str(e))

        threading.Thread(target=do_connect, daemon=True).start()

    def _disconnect_bt(self):
        if not self.bt_client:
            return
        try:
            self.bt_client.disconnect()
        finally:
            self.bt_client = None
            # stop monitor if running
            self._stop_bt_monitor()
            self.status_var.set('Bluetooth disconnected')
            self._set_bt_status('disconnected')
            self.connect_btn.config(state='normal')
            self.disconnect_btn.config(state='disabled')
            self.send_btn.config(state='disabled')
            self.start_remote_btn.config(state='disabled')
            self.stop_btn.config(state='disabled')
            self.request_btn.config(state='disabled')

    def _send_training_to_device(self):
        if not self.bt_client:
            messagebox.showwarning('Bluetooth', 'Not connected')
            return
        initfile = str(getattr(self, 'current_file_path', ''))
        training_path = filedialog.askopenfilename(
            title='Select merged training YAML to send',
            initialfile=initfile,
            filetypes=[('YAML','*.yaml;*.yml'),('All','*.*')]
        )
        if not training_path:
            return

        default_id = Path(training_path).stem
        training_id = simpledialog.askstring('Training ID', 'Training ID to use on device:', initialvalue=default_id)
        if not training_id:
            return

        def do_send():
            try:
                self.status_var.set('Sending merged training file...')
                resp = self.bt_client.send_file(training_id, training_path)
                self.status_var.set('Send complete')
                messagebox.showinfo('Send', f'Server response: {resp}')
            except Exception as e:
                self.status_var.set('Send failed')
                messagebox.showerror('Send', str(e))

        threading.Thread(target=do_send, daemon=True).start()

    # --- Bluetooth monitor helpers ---
    def _set_bt_status(self, status: str) -> None:
        self.bt_status_var.set(f'Bluetooth: {status}')

    def _start_bt_monitor(self):
        self._stop_bt_monitor()
        self.bt_monitor_stop = threading.Event()

        def _loop():
            while not self.bt_monitor_stop.is_set():
                if self.bt_client is None or not self.bt_client.connected:
                    self.after(0, lambda: self._set_bt_status('disconnected'))
                    break
                try:
                    status = self.bt_client.get_status()
                    self.after(0, lambda status=status: self._set_bt_status(status))
                except Exception:
                    self.after(0, lambda: self.status_var.set('Bluetooth connection lost'))
                    self.after(0, self._disconnect_bt)
                    break
                self.bt_monitor_stop.wait(2.0)

        self.bt_monitor_thread = threading.Thread(target=_loop, daemon=True)
        self.bt_monitor_thread.start()

    def _stop_bt_monitor(self):
        try:
            if self.bt_monitor_stop:
                self.bt_monitor_stop.set()
            self.bt_monitor_stop = None
        except Exception:
            pass
        try:
            self.bt_monitor_thread = None
        except Exception:
            pass

    def _start_remote_training(self):
        if not self.bt_client:
            messagebox.showwarning('Bluetooth', 'Not connected')
            return
        default_id = Path(str(self.current_file_path)).stem if getattr(self, 'current_file_path', None) else ''
        training_id = simpledialog.askstring('Training ID', 'Training ID to start on device:', initialvalue=default_id)
        if not training_id:
            return

        def do_start():
            try:
                self.status_var.set('Starting remote training...')
                resp = self.bt_client.start_training(training_id)
                self.status_var.set('Remote start response')
                self._set_bt_status('running training')
                messagebox.showinfo('Start', f'Server: {resp}')
            except Exception as e:
                self.status_var.set('Remote start failed')
                messagebox.showerror('Start', str(e))

        threading.Thread(target=do_start, daemon=True).start()

    def _stop_training(self):
        if not self.bt_client:
            messagebox.showwarning('Bluetooth', 'Not connected')
            return

        def do_stop():
            try:
                self.status_var.set('Stopping training...')
                resp = self.bt_client.stop_training()
                self.status_var.set('Training stopped')
                self._set_bt_status('idle')
                messagebox.showinfo('Stop', f'Server: {resp}')
            except Exception as e:
                self.status_var.set('Stop failed')
                messagebox.showerror('Stop', str(e))

        threading.Thread(target=do_stop, daemon=True).start()

    def _request_file(self):
        if not self.bt_client:
            messagebox.showwarning('Bluetooth', 'Not connected')
            return

        filename = simpledialog.askstring('Request file', 'Filename on device to request (e.g. output.csv):')
        if not filename:
            return
        save_path = filedialog.asksaveasfilename(title='Save received file as', initialfile=filename)
        if not save_path:
            return

        def do_req():
            try:
                self.status_var.set('Requesting file...')
                self.bt_client.request_file(filename, save_path)
                self.status_var.set('File received')
                messagebox.showinfo('Request', f'File saved to {save_path}')
            except Exception as e:
                self.status_var.set('Request failed')
                messagebox.showerror('Request', str(e))

        threading.Thread(target=do_req, daemon=True).start()


if __name__ == '__main__':
    app = TrainingBluetoothGUI()
    app.mainloop()
