# Gyro Conflict Demo

This demo shows why Gyro Logic is different from a normal fixed-model system.

## What it demonstrates

- one behavior state
- two competing frames
- a joint optimization process
- conflict that bends the trajectory
- stabilization under tension rather than under a single objective

## Run

```bash
python gyro_conflict_demo.py
```

## Expected output

The demo opens three plots:

1. **Inference Trajectory**  
   The state moves through 2D space under the pull of two competing targets.

2. **Stability Under Competing Frames**  
   Each frame produces its own stability score.  
   The total score shows the actual inference objective.

3. **Frame Conflict Over Time**  
   Conflict is explicitly measured as the distance between the two frames.

## Why this matters

Traditional systems usually assume one model, one objective, one fixed interpretation.

Gyro Logic instead treats:

- behavior as dynamic,
- frame as dynamic,
- conflict as internal to reasoning,
- inference as a trajectory toward stable resolution.

This is one of the first practical demonstrations of the Gyro claim:

> Intelligence is motion in frame space.

## Suggested repository placement

```text
repo/
├─ README.md
├─ gyro_demo_v2.py
├─ gyro_conflict_demo.py
└─ docs/
   ├─ gyro_hero.png
   ├─ gyro_figure1_paper.png
   ├─ gyro_figure2_paper.png
   └─ gyro_figure3_paper.png
```
