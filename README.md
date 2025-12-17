# OT-2 Electrochemistry Workflow

Python tools for controlling **Opentrons OT-2** via HTTP API and orchestrating **electrochemistry experiments** (BioLogic potentiostat) from scripts or Jupyter notebooks.

---

## Overview

This repository automates solution handling, deposition, characterization, and data logging for high-throughput electrochemistry workflows.

* `alan_workflow.ipynb` — single-run notebook showing the full sequence: load labware/pipettes → transfer solutions → execute electrochemistry → log data & images.
* `alan_workflow_host.ipynb` — **host-mode runner** that adds a BioLogic channel server so multiple devices/clients can share the BioLogic potentiostat concurrently. It brokers channel reservations and dispatches techniques so OT-2 runs don’t block each other.
* `opentronsClient` handles robotics control (labware, movement, pipetting).
* BioLogic helpers provide electrochemical methods (PEIS/OCV/CA/etc.).

---

## Running the Notebook

1. **Create/activate a Python environment** and install the required packages: `paho-mqtt`, `paramiko`, `opencv-python`, `Pillow`, `pandas`, plus the BioLogic SDK (copy the `biologic` and `kbio` into this env’s `site-packages`). Make sure your Jupyter kernel is using this environment.  
   - **conda example**:  
     ```bash
     conda create -n ot2_workflow python=3.10
     conda activate ot2_workflow
     pip install paho-mqtt paramiko opencv-python pillow pandas
     ```  
   - **venv example** (pure Python):  
     ```bash
     python -m venv .venv
     .venv\Scripts\activate  # Windows
     pip install paho-mqtt paramiko opencv-python pillow pandas
     ```

2. **Open the notebook**: use `alan_workflow.ipynb` for a single OT‑2 run, or `alan_workflow_host.ipynb` to run the full workflow and host the BioLogic channel server.

   > if use `alan_workflow_host.ipynb`, run `run_biologic_host.bat` first to start the server

3. **Cell 0 – Imports**: run to import dependencies and helper functions (from `workflow_helpers.py`, `iot_mqtt.py`, etc.). Install any missing packages if imports fail.

4. **Cell 1 – Experiment folder + logging**: creates a new run folder under `data/DATE_RUNID`, sets up `workflowLog.log`, and configures logging to file + stdout; no user input.

5. **Cell 2 – Experiment parameters CSV**:
   - Creates `experiment_params.csv` with a header and template row if it does not exist, and prompt for user input to comfirm CSV file.
   - Edit this CSV to define one row per reactor well with:
     - **wellName**: reactor well to run on (e.g. `A1`, `B2`).
     - **well ID**: any numeric ID for your own reference (code uses `wellName` for motion).
     - **temperature_C**: target temperature (currently logged).
     - **depositionCurrent_mA**, **depositionTime_s**: both filled → deposition run; both empty → skip deposition and go straight to characterization.
     - **solution A–D name**: solution names; must match the vial‑rack entries you define later.
     - **solution A–D volume_mL**: volume of each solution (mL) to add to that well.
   - When the CSV is ready, press **Enter**.
   - Prompt for **Pipette Tip ID**: starting tip index in the 96‑tip rack (press Enter for 1 if unsure).
   - Load and print a summary of wells/solutions. 

6. **Cell 3 – OT‑2 + labware setup**:
   - Set `robotIP` to your OT‑2’s IP address.
   - The cell:
     - Instantiates `opentronsClient`.
     - Loads: 1000 µL tip rack (slot 1), sonicator bath (slot 3), 25 mL vial racks (slots 4 & 7), 15‑well reactor (slot 9), electrode tip rack (slot 10), pH probe rack (slot 11).
     - Loads a `p1000_single_gen2` pipette on the right mount.
   - Physically arrange the deck to match this configuration.

7. **Cell 4 – Solution layout (`sources_by_plate`)**:
   - Map each vial‑rack well (e.g. `A1`, `A2` on `strID_vialRack_4`) to a solution name and starting volume (in µL).
   - Ensure solution names here match the `solution A–D name` entries in `experiment_params.csv`.

8. **Cell 5–6 – MQTT broker and devices**:
   - Cell 5 starts or reuses the MQTT broker via `start_broker_if_needed`, starts a controller beacon, and connects `PumpMQTT`, `UltraMQTT`, `HeatMQTT`, `PhMQTT`, and `BioMQTT` clients (set `broker` to your MQTT host IP).
   - Cell 6 prints ONLINE/OFFLINE and per‑channel states for each device; verify all are ONLINE before continuing.

9. **Cell 7–8 – OT‑2 readiness**:
   - Turn OT‑2 lights on and run `homeRobot()` (Cell 7).
   - Optionally use the camera‑focus/test‑well snippet (Cell 8) to confirm focus and Z‑heights.

10. **Cell 10 – Main workflow**:
    - Loops over all wells loaded from `experiment_params.csv`.
    - For each well: creates folders, metadata JSON, and a video recorder; washes the reactor; takes start images.
    - Fills the reactor well with the specified solutions via `fillWell_autoSource`, tracking remaining volumes.
    - Handles pH probe pickup/wash/measurement, runs Biologic deposition + characterization sequences (via `biologic_stream`), and performs all required washes and imaging.
    - Stops recording and marks the well as completed in the log/metadata.
    
11. **Final cell – Shutdown**:
    - Calls `_best_effort_all_off` to turn off pumps/ultra/heat/pH/BioLogic, stops the controller beacon, disconnects all MQTT clients, stops the broker (`stop_broker(proc)`), and homes the OT‑2 one last time.

### Host mode (BioLogic server)
- Clients/notebooks request channels; the server serializes technique execution so multiple devices can share BioLogic hardware without conflicts.  
- Keep the host notebook running while client workflows execute.

---

## Main API Surface (`opentronsClient`)

```python
opentronsClient(strRobotIP, headers={"opentrons-version": "*"}, strRobot="ot2")
```

Functions include:

| Category               | Key Methods                                                            |
| ---------------------- | ---------------------------------------------------------------------- |
| **Labware & Pipettes** | `loadLabware`, `loadCustomLabware`, `loadPipette`, `addLabwareOffsets` |
| **Motion & Tips**      | `homeRobot`, `moveToWell`, `pickUpTip`, `dropTip`, `pipetteHasTip`     |
| **Liquid Handling**    | `aspirate`, `dispense`, `blowout`, `liquidProbe`                       |
| **Robot Control**      | `controlAction`, `lights`, `getRunInfo`                                |

---

## Workflow Structure

1. **Initialization**

   * connect to OT-2
   * start MQTT + logging
   * load experiment parameters
   * `homeRobot()`

2. **Experiment Loop — for each well**
   **Pre-experiment**

   * create metadata file
   * rinse (if storage solution present)
   * capture pre-experiment image
   * start recording

   **Deposition stage**

   * dispense solutions according to plan
   * read pH (probe wash before/after)
   * run BioLogic deposition technique
   * rinse + image

   **Characterization stage**

   * dispense new solutions
   * run BioLogic characterization
   * rinse + image 
   * stop recording 

3. **End of Run**

   * stop all MQTT clients and brokerS
   * `homeRobot()`

---

## OT-2 Deck Layout

| Slot | Item                         |
| ---- | ---------------------------- |
| 1    | 1000 µL tip rack             |
| 3    | Ultrasonic wash tank (A1–A2) |
| 4    | Reservoir rack (25 mL ×8)    |
| 7    | Reservoir rack (25 mL ×8)    |
| 9    | 15-well reactor (A1–C5)      |
| 10   | Electrode tip rack           |
| 11   | pH probe tip rack            |
| 12   | Waste disposal               |

---

## Common Issues

### `has attribute {dict}` error

→ Run `homeRobot()` to reset internal state.

### Incorrect pipette height

→ Usually caused by missed homing or motor obstruction.
**Fix:** `homeRobot()` and restart the run.

