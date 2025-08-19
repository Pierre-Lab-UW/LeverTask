Simple GUI to run trainings and edit YAML parameters.

Usage:
- Run the app: python GUI/app.py
- Select a training YAML from the dropdown.
- Edit parameter values and click Save.
- Click Start Training to launch the training in a separate process (calls pygame_simulation.py).

Notes:
- Requires Python and PyYAML installed.
- The GUI edits the `actual` field in the selected YAML.
