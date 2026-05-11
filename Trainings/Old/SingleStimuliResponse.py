import os
import csv
import time

from SingleLeverTraining import SingleLeverTraining
from LeverBase import LeverBase
from datetime import datetime
from ADU200 import ADU200

from Events.LeverStateChangedEvent import LeverStateChangedEvent

class SingleStimuliResponse(SingleLeverTraining):
    def __init__(self, lever1: LeverBase, params_yaml_path: str, global_params_yaml_path: str) -> None:
        super().__init__(lever1, params_yaml_path, global_params_yaml_path)

        self.output_data_file: str = (
            f"OutputData/{self.get_global_param('Subject')}_SingleStimuliResponse_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        self.relay_output_type: str = self.get_param("RelayOutputType", "Unknown")
        self.relay_output_pin: int = self.get_param("RelayOutputPin", -1)

        # switching behavior: "step" (default) | "pulse" | "toggle"
        self.switch_type: str = str(self.get_param("SwitchType", "step")).lower()
        # pulse duration in seconds (used for pulse mode and fallback toggles)
        try:
            self.pulse_duration: float = float(self.get_param("PulseDuration", 0.1))
        except Exception:
            self.pulse_duration = 0.1
        
        self.toggle_state: bool = False  # for toggle mode

    def start_event(self):
        """Enable lever, create csv and attach event to control relay on press/release."""
        # enable lever and register event
        self.lever1.set_is_active(True)
        self.lever1.add_event(LeverStateChangedEvent(
            "stimulus_on_press", self.lever1, self._on_lever_state_changed
        ))
        self.start_time = time.time()

    def stop_event(self):
        """Clear lever events."""
        self.lever1.events.clear()

    def _on_lever_state_changed(self, lever: LeverBase, new_state: int, time_since_last_change: float):
        """Called when lever state changes. Control relay according to SwitchType and log on press."""
        if not lever.active:
            return

        # safe check for relay pin
        has_valid_pin = (self.relay_output_pin is not None and isinstance(self.relay_output_pin, int) and self.relay_output_pin >= 0)

        # run hardware action only if pin valid, otherwise skip but still log
        if has_valid_pin:
            try:
                adu = ADU200.get_instance()
                mode = (self.switch_type or "step").lower()

                if mode == "pulse":
                    # pulse on press only
                    if new_state == 0:
                        adu.set_relay(self.relay_output_pin, set_open=False)
                        time.sleep(self.pulse_duration)
                        adu.set_relay(self.relay_output_pin, set_open=True)

                elif mode == "toggle":
                    # toggle on press only
                    if new_state == 0:
                        try:
                            cur = adu.get_port_status(self.relay_output_pin)
                        except Exception:
                            cur = None
                        if cur is None:
                            # fallback: pulse if we can't read current state
                            adu.set_relay(self.relay_output_pin, set_open=False)
                            time.sleep(self.pulse_duration)
                            adu.set_relay(self.relay_output_pin, set_open=True)
                        else:
                            # invert current state (coerce to bool)
                            adu.set_relay(self.relay_output_pin, set_open=not bool(cur))

                else:  # default "step"
                    if new_state == 0:   # pressed -> activate relay (closed)
                        adu.set_relay(self.relay_output_pin, set_open=False)
                    elif new_state == 0: # released -> deactivate relay (open)
                        adu.set_relay(self.relay_output_pin, set_open=True)

            except Exception as e:
                print(f"Error controlling relay pin {self.relay_output_pin}: {e}")
        else:
            # no valid pin configured
            pass

        # Logging: keep existing behavior, log only on press (new_state == 1)
        if new_state != 1:
            return
