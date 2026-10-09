[🇺🇸 English](README.md) | [🇹🇷 Türkçe](README_TR.md)

# 🪰 FlyBrainGame: 166,700-Neuron Biological Connectome Simulation

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Connectome](https://img.shields.io/badge/Connectome-Janelia%20MaleCNS%20v1.0-green.svg)](https://janelia.org)
[![Engine](https://img.shields.io/badge/3D%20Engine-Panda3D-orange.svg)](https://www.panda3d.org)
[![Control](https://img.shields.io/badge/Neural%20Control-100%25%20Pure%20Connectome-brightgreen.svg)](#-100-pure-connectome-control)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**FlyBrainGame** is a living 3D ecosystem simulation driven by the complete central nervous system connectome of an adult male fruit fly (*Drosophila melanogaster*) from Janelia Research Campus (**MaleCNS v1.0**).

In this simulation, the fly's locomotion, foraging, landing, and survival behaviors are **not** scripted by artificial heuristics or reinforcement learning shortcuts. Every wingbeat, turn, landing, takeoff, proboscis extension, and predator evasion response is generated in real time by an active **Leaky Integrate-and-Fire (LIF) spiking neural network comprising 166,700 biologically reconstructed neurons and 25.58 million synapses**.

---

## 📑 Table of Contents

- [Key Highlights](#-key-highlights)
- [100% Pure Connectome Control](#-100-pure-connectome-control)
- [Biological Architecture & Circuits](#-biological-architecture--circuits)
  - [1. Visual System (Looming & Optic Flow)](#1-visual-system-looming--optic-flow)
  - [2. 3D Olfactory System & Plume Dynamics](#2-3d-olfactory-system--plume-dynamics)
  - [3. Gustation & Proboscis Extension Reflex (PER)](#3-gustation--proboscis-extension-reflex-per)
  - [4. Mushroom Body Associative Learning & Memory](#4-mushroom-body-associative-learning--memory)
  - [5. Physiological Internal State](#5-physiological-internal-state)
  - [6. Frog Predator AI & Ballistic Tongue Strike](#6-frog-predator-ai--ballistic-tongue-strike)
- [Installation](#-installation)
- [Quick Start & Controls](#-quick-start--controls)
- [HUD Telemetry Guide](#-hud-telemetry-guide)
- [Scientific Testing & Benchmarks](#-scientific-testing--benchmarks)
- [MaleCNS 166,700-Neuron Interface Audit](#-malecns-166700-neuron-interface-audit)
- [Citation & Acknowledgments](#-citation--acknowledgments)

---

## 🌟 Key Highlights

- 🧠 **Full Janelia MaleCNS v1.0 Graph**: 166,700 neurons and 25,582,938 weighted synapses evaluated simultaneously using Numba JIT multi-core parallelism at ~25–50 Hz brain steps.
- 🎯 **Strictly Zero Heuristic Creep**: Zero neural firing produces exactly zero forward velocity ($0\text{ spikes} \implies 0.0\text{ m/s}$). No background cruising speed, no hidden `if obstacle: turn()` logic.
- 👁️ **Biophysical Vision**: Visual looming detected via `LC4` (rapid escape) and `LPLC2` (expanding optic flow); small target pursuit driven by `LC10a/b/c`.
- 👃 **3D Atmospheric Odor Dispersion**: Physical turbulent plume model with wind advection; bilateral antenna concentration gradients drive biological tropotaxis via `ORN_DM1` through `ORN_DM5`.
- 👅 **Contact Chemosensation & PER**: Tarsal (leg) sugar detection triggers immediate walking arrest; labellar (mouthpart) contact triggers `MN_Proboscis` motor activation.
- 🍔 **Collision-Verified Feeding**: No arbitrary feed radius. Ingestion requires physical overlap between the 3D proboscis collider and the fruit mesh.
- 🍄 **Mushroom Body Synaptic Plasticity**: Three-factor learning ($KC \to MBON$) modulated by dopaminergic reward (`PAM`) and punishment (`PPL1`); learned associations persist across deaths and reincarnations (`fly_memory_mb.npz`).
- 🐸 **Dynamic Frog Predators**: Multi-stage hunting cycle (`WATCH` $\to$ `AIM` $\to$ `TONGUE_STRIKE` at 14 m/s $\to$ `CATCH_PULL` $\to$ `FLY EATEN`) with physical 3D tongue segment collision.
- 🎮 **Spectator & Chase Cameras**: Seamless toggle between third-person chase mode and a 6-DOF free-flight spectator drone camera.

---

## 🔬 100% Pure Connectome Control

The core philosophy of FlyBrainGame is **uncompromising biological causality**:

```
[Physical Environment] 
         │  (Light, Odor Plume, Taste, Surface Collision)
         ▼
[Sensory Receptor Neurons] 
         │  (LC4, LPLC2, LC10, ORN, BM_Taste, Halteres)
         ▼
[166,700-Neuron MaleCNS Graph] 
         │  (Numba JIT Leaky Integrate-and-Fire Network)
         ▼
[Descending & Motor Neurons] 
         │  (DNp01, DNa02, DNg100, MDN, DNp09, MN_Proboscis)
         ▼
[Body Physics Actuation]
```

1. **No Artificial Steering**: If visual looming excites right `LC4`, lateral excitation triggers left `DNa02`, mechanically rotating the body away from the predator.
2. **True Takeoff Causality**: Walking does not automatically trigger flight when a speed threshold is crossed. Takeoff requires tergotrochanteral motor neuron (`MN_Takeoff` / Giant Fiber circuit) activation.
3. **Causality Proven by Automated Tests**: In `tests/test_neural_control.py`, disabling the connectome instantly brings all physical movement to a dead halt ($0.0\text{ m/s}$).

---

## 🧬 Biological Architecture & Circuits

### 1. Visual System (Looming & Optic Flow)
- **LC4 (Lobula Columna 4)**: Sensitive to rapidly expanding dark edges. Mediates fast looming escape responses.
- **LPLC2 (Lobula Plate / Lobula Columnar 2)**: Detects expanding optical flow across the compound eye visual field.
- **LC10a / LC10b / LC10c**: Small-object motion detectors crucial for tracking food patches, conspecifics, and orientation cues.

### 2. 3D Olfactory System & Plume Dynamics
- **Atmospheric Plume Physics**: Fruit items emit volatile organic compounds modeled as a 3D Gaussian plume advected by real-time ambient wind vectors with turbulent dispersion.
- **Bilateral Antennal Coding**: Separate left and right antennal sensors measure concentration differentials, driving antennal lobe projection neurons (`ORN_DM1` to `ORN_DM5`) for natural chemotaxis / tropotaxis.

### 3. Gustation & Proboscis Extension Reflex (PER)
- **Tarsal (Leg) Chemosensation**: When landing on fruit surfaces, contact chemoreceptors on the legs evaluate sucrose (sweet) vs. bitter compounds (`BM_Taste`).
- **Walking Arrest**: High sweet receptor activation inhibits forward walking descending neurons (`DNp09`), halting the fly over the food source.
- **Proboscis Motor Drive**: Motor neurons (`MN_Proboscis`) extend the proboscis until the physical 3D labellum collider contacts the fruit mesh, initiating nutrient uptake.

### 4. Mushroom Body Associative Learning & Memory
- **Kenyon Cells (KCs)**: ~2,000 cells provide sparse representations of complex olfactory blends.
- **MBONs (Mushroom Body Output Neurons)**: Output channels driving approach or avoidance behaviors.
- **Dopaminergic Modulation**:
  - `PAM` cluster: Activated by sugar reward, inducing long-term synaptic depression (LTD) on avoidance MBONs.
  - `PPL1` cluster: Activated by predator strikes and bitter tastes, reinforcing avoidance pathways.
- **Persistent Synaptic Storage**: Plastic weights are saved to `fly_memory_mb.npz`, ensuring learned memories survive fly reincarnation.

### 5. Physiological Internal State
- Dynamic homeostatic state variables: `hunger`, `energy`, and `hydration`.
- **Sensory Gain Modulation**: Elevated hunger upregulates olfactory and gustatory receptor gains via simulated octopaminergic/dopaminergic tone, prioritizing foraging drive over quiescent resting.
- **Metabolic Fatigue**: Depleted energy attenuates wing motor output, forcing the fly to land and rest.

### 6. Frog Predator AI & Ballistic Tongue Strike
- Three autonomous predator frogs patrol the wetland and marsh biomes with a realistic physiological hunting state machine:
  1. `IDLE` $\to$ `WATCH` (Smooth head orientation toward fly position).
  2. `AIM` (Kinematic range and elevation alignment).
  3. `TONGUE_STRIKE` (Ballistic tongue extension at 14 m/s).
  4. `CATCH_PULL` (Physical 3D bounding box collision pulls fly to mouth).
  5. `FLY EATEN` (Game Over summary).
- The fly can actively evade if its `LC4 / DNp01` Giant Fiber pathway fires before physical tongue impact.

---

## 💻 Installation

### Prerequisites
- **Operating System**: Windows 10/11, Linux, or macOS.
- **Python Version**: Python 3.12 recommended.
- **Hardware**: Dedicated GPU optional. Runs smoothly at 60 FPS 3D rendering with ~25–50 Hz brain steps on modern multi-core CPUs (e.g., Intel Iris Xe / Core i5 or AMD Ryzen).

### 1. Clone the Repository
```bash
git clone https://github.com/asiluzunoglu1216-gif/FlyBrainGame.git
cd FlyBrainGame
```

### 2. Set Up Virtual Environment
```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

```bash
# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
pip install panda3d numba numpy scipy
```

*Note: On first startup, the ~260 MB compiled Janelia MaleCNS connectome (`brain.npz` and `weights.npz`) will be loaded and cached automatically.*

---

## 🎮 Quick Start & Controls

Launch the simulation:

```powershell
.\.venv\Scripts\python.exe run_game.py
```

### Keybindings

| Key | Mode | Description |
|:---:|:---|:---|
| **F** | Camera | **Toggle Camera**: 3rd-Person Chase $\leftrightarrow$ 6-DOF Free Spectator Drone |
| **W, A, S, D** | Spectator | Move camera Forward, Left, Backward, Right |
| **Space** | Mixed | *Chase:* Reset fly to safety. *Spectator:* Elevate camera upward. |
| **Shift / Ctrl** | Spectator | Lower camera downward |
| **Mouse Move** | Spectator | Free-look camera orientation (Pitch & Yaw) |
| **Mouse Wheel** | Spectator | Adjust camera movement speed (5 – 70 units/s) |
| **F1** | Brain | **Connectome Control (Default)**: 166,700-neuron MaleCNS in direct control |
| **F2** | Brain | **Scripted Baseline Bot**: Heuristic rule-based bot for comparison |
| **F3** | Sensory | Toggle between `FEATURE_MODE` and experimental `EYE_MODE` |
| **R** | Life | **Reincarnation**: Rebirth fly with a new seed while preserving MB memories |
| **Esc** | System | Clean shutdown and telemetry dump |

---

## 📊 HUD Telemetry Guide

- **Render FPS**: Graphics rendering frame rate (~60 FPS).
- **Brain Step Hz**: Real-time connectome solver frequency.
- **Latency (ms)**: Wall-clock duration required to compute one 166.7k-neuron graph step (~25–38 ms).
- **Life Stats**:
  - `ALIVE`: Elapsed lifespan in seconds.
  - `FOOD`: Total fruit items successfully ingested.
  - `DIST`: Cumulative travel distance.
  - `LANDINGS`: Total successful surface perch events.
  - `THREATS / ESCAPES`: Frog attacks survived vs. near-misses.
- **Physiology Status**:
  - `HUNGER`: Metabolic nutritional deficit percentage.
  - `ENERGY`: Available flight motor reserve.
  - `PROBOSCIS`: Labellum extension percentage (0% to 100%).
- **Key Motor Firing Rates (Hz)**:
  - `DNp01 (L/R)`: Giant Fiber emergency escape circuit.
  - `DNa02 (L/R)`: Steering and yaw motor command.
  - `DNg100`: Forward propulsion motor drive.
  - `MDN`: Moonwalker backward / braking motor drive.

---

## 🧪 Scientific Testing & Benchmarks

The repository includes a suite of automated verification suites to validate neural circuits, causality, and biomechanics:

```powershell
# 1. Biological Circuit Verification (LC4/LPLC2 -> DNp01, LC10a -> DNa02)
.\.venv\Scripts\python.exe -m unittest tests/test_circuits.py -v

# 2. Strict Neural Causality & Anti-Cheat Invariant (0 spikes -> 0 speed)
.\.venv\Scripts\python.exe -m unittest tests/test_neural_control.py -v

# 3. Proboscis Contact Verification & Takeoff Purity
.\.venv\Scripts\python.exe -m unittest tests/test_feeding_takeoff_purity.py -v

# 4. Frog Predator Fair Live Hunt & Physical Tongue Strike Collision
.\.venv\Scripts\python.exe -m unittest tests/test_frog_fair_live.py -v

# 5. Mushroom Body Associative Learning & Synaptic Persistence
.\.venv\Scripts\python.exe -m unittest tests/test_memory_plasticity.py -v

# 6. Multi-Seed 10-Run Ecological Benchmark
.\.venv\Scripts\python.exe tests/run_10_seed_foraging_benchmark.py
```

---

## 📋 MaleCNS 166,700-Neuron Interface Audit

All **166,700 neurons** from the Janelia MaleCNS v1.0 dataset remain fully simulated inside the active graph:

- **Total Cell Types**: 11,863
- **Sensory Boundary Interfaces**: Optic lobe projections (`LC4`, `LPLC2`, `LC9`, `LC10a-c`), Antennal receptor neurons (`ORN_DM1-5`), Gustatory receptor neurons (`BM_Taste`), Mechanosensory halteres, and Johnston's organ airflow sensors.
- **Motor Boundary Interfaces**: Giant Fiber escape (`DNp01`), Yaw steering (`DNa02`), Forward flight drive (`DNg100`), Backward brake (`MDN`), Walking initiation (`DNp09`), Proboscis extension (`MN_Proboscis`), Jumping takeoff (`MN_Takeoff`).
- **Complete Audit Records**: Detailed in [`reports/full_166700_neuron_interface_audit.json`](reports/full_166700_neuron_interface_audit.json) and [`reports/biological_evidence.md`](reports/biological_evidence.md).

---

## 📄 Citation & Acknowledgments

- **Connectome Dataset**: [Janelia Research Campus](https://www.janelia.org) - FlyEM Project (MaleCNS v1.0).
- **Simulation Engine Foundations**: Built upon concepts from `alextitonis/fly.ai` and Ornata Fly64 LIF architectures.
- **Author & Maintainer**: [asiluzunoglu1216-gif](https://github.com/asiluzunoglu1216-gif)

Licensed under the [MIT License](LICENSE).
