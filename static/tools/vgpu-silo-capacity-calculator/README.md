# Mixed Mode vGPU Profile Placement Silo Simulator

A browser-based tool to visualize how **NVIDIA vGPU mixed-size mode** placement creates **siloed** (unreachable) GPU capacity when different profile sizes share the same GPU. Uses placement-boundary alignment and FCFS allocation to show silos in real time and to recommend profiles by silo impact.

## What it does

- **Step 1 — Profile mix:** Choose which vGPU profile types you plan to offer (e.g. 8 GB, 16 GB, 24 GB).
- **Step 2 — Allocate instances:** Simulate FCFS placement; the memory map shows allocated, free, and **siloed** (unreachable by any selected profile) capacity. Includes:
  - **Randomize until first failed placement** — one random FCFS run to the first failure.
  - **Monte Carlo (10.000 runs)** — worst/median/average siloed GB; optional **Visualize worst-case run** to load that layout into the map.
- **Step 3 — Profile recommender:** Enter a workload size (GB); profiles in your mix that fit are ranked by siloed capacity impact, placement density, and headroom. “Tighter” profiles outside your mix are suggested when they reduce headroom vs your best fit.

Profile data and placement IDs follow **NVIDIA vGPU Software** (e.g. 19.x) mixed-size mode behaviour.

## Repo contents

| File | Purpose |
|------|--------|
| `index.html` | Single-page app (HTML, CSS, JS). Includes an inline catalog fallback if `vgpu-catalog.json` is not available. |
| `vgpu-catalog.json` | GPU and profile catalog (memory, profiles, placement IDs). Loaded when the app is served over HTTP. |
| `vgpu-catalog.csv` | Source data for (re)building the catalog. |
| `build-vgpu-catalog.py` | Script to regenerate `vgpu-catalog.json` from the CSV. |

## How to run

- **Local:** Open `index.html` in a browser (file protocol). The app uses the **inline** catalog in that case.
- **Web:** Serve the folder (e.g. GitHub Pages, any static host). The app will load `vgpu-catalog.json` from the same directory when possible.

### GitHub Pages

1. Push this folder as the root of a repo (or the `docs` folder).
2. In the repo **Settings → Pages**, set source to the branch and folder containing `index.html`.
3. The app will be at `https://<username>.github.io/<repo>/` (or `.../docs/`).

## References

- [NVIDIA vGPU Software User Guide](https://docs.nvidia.com/vgpu/latest/pdf/grid-vgpu-user-guide.pdf) — Mixed-Size Mode & Placement IDs  
- [Architecting AI Infrastructure](https://frankdenneman.nl/architecting-ai-infrastructure) — frankdenneman.nl

## License

Use and adapt as you like. Profile data is derived from NVIDIA vGPU documentation; refer to NVIDIA for official specs.
