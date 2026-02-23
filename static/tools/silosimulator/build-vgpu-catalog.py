#!/usr/bin/env python3
import csv
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
CSV_PATH = HERE / "vgpu-catalog.csv"
OUT_PATH = HERE / "vgpu-catalog.json"

def norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())

def slug(s: str) -> str:
    s = norm(s).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s

def parse_gb(cell: str) -> int:
    c = norm(cell).lower().replace("gb", "").strip()
    return int(float(c))

def parse_int(cell: str) -> int:
    return int(float(norm(cell)))

def is_row_start(row, label):
    return len(row) >= 1 and norm(row[0]).lower() == label.lower()

def read_rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return [ [norm(c) for c in r] for r in csv.reader(f) ]

def find_col_idx(header_row, wanted):
    wanted = wanted.lower()
    for i, c in enumerate(header_row):
        if norm(c).lower() == wanted:
            return i
    return None

def parse_sections(rows):
    """
    Parses CSV that looks like:

    GPU Memory,96 GB,,,,
    NVIDIA GPUs,NVIDIA RTX PRO 6000 SE 96GB,,,,
    Architecture ,Blackwell,,,,
    vGPU Profiles,FrameBuffer,Maximum vGPUs per GPU in Mixed-Size Mod,Supported Placement IDs,,
    DC-96C,96,1,0,,
    ...

    Multiple GPU blocks can be concatenated in the same CSV.
    """
    gpus = []
    i = 0
    n = len(rows)

    while i < n:
        row = rows[i]
        # Start of a GPU section
        if is_row_start(row, "GPU Memory"):
            mem_cell = row[1] if len(row) > 1 else ""
            if not mem_cell:
                raise SystemExit(f"Found 'GPU Memory' but no value on line {i+1}")
            mem_gb = parse_gb(mem_cell)

            # Next rows: GPU name + arch (order may vary, allow small scan window)
            gpu_name = None
            arch = None

            # scan next ~10 rows for metadata + table header
            j = i + 1
            header_idx = None
            while j < min(i + 15, n):
                r = rows[j]
                k0 = norm(r[0]).lower() if r else ""
                if k0 in ("nvidia gpus", "gpu", "gpu name", "gpu model"):
                    gpu_name = r[1] if len(r) > 1 else gpu_name
                if k0.startswith("architecture"):
                    arch = r[1] if len(r) > 1 else arch

                # table header row
                if k0 in ("vgpu profiles", "vGPU profiles".lower()):
                    header_idx = j
                    break
                j += 1

            if header_idx is None:
                raise SystemExit(
                    f"Could not find the vGPU table header after GPU Memory {mem_gb} GB (starting line {i+1}). "
                    "Expected a row starting with 'vGPU Profiles'."
                )

            if not gpu_name:
                raise SystemExit(f"Missing 'NVIDIA GPUs,<name>' row for GPU Memory {mem_gb} GB (starting line {i+1}).")
            if not arch:
                arch = "Unknown"

            header = rows[header_idx]

            # Columns we need (your header has slight truncation: 'Mod' vs 'Mode')
            col_profile = 0  # first column is vGPU Profiles
            col_fb = find_col_idx(header, "FrameBuffer")
            if col_fb is None:
                col_fb = find_col_idx(header, "Framebuffer")
            col_max = None
            # find the "Maximum vGPUs..." column by substring match
            for idx, c in enumerate(header):
                if "maximum vgpus" in norm(c).lower():
                    col_max = idx
                    break
            col_pid = None
            for idx, c in enumerate(header):
                if "supported placement id" in norm(c).lower():
                    col_pid = idx
                    break

            if col_fb is None or col_max is None or col_pid is None:
                raise SystemExit(
                    f"Header row for {gpu_name} is missing expected columns. "
                    f"Need FrameBuffer + Maximum vGPUs + Supported Placement IDs. Header was: {header}"
                )

            profiles = []
            k = header_idx + 1
            while k < n:
                r = rows[k]
                # stop on next section
                if is_row_start(r, "GPU Memory"):
                    break
                # stop on empty line
                if len(r) == 0 or (len(r) == 1 and r[0] == ""):
                    k += 1
                    continue

                # skip stray labels
                first = norm(r[0])
                if first == "" or first.lower() in ("nvidia gpus", "architecture", "vgpu profiles"):
                    k += 1
                    continue

                # profile row
                try:
                    prof_name = first
                    fb = parse_int(r[col_fb]) if col_fb < len(r) else None
                    mx = parse_int(r[col_max]) if col_max < len(r) else None
                    pid_raw = r[col_pid] if col_pid < len(r) else ""
                    pid = norm(pid_raw)

                    if fb is None or mx is None:
                        raise ValueError("missing framebuffer/max")

                    profiles.append({
                        "name": prof_name,
                        "gb": fb,
                        "maxVms": mx,
                        # Keep placement IDs as a displayable string (can be "0" or "0, 48, 72")
                        "placementId": pid
                    })
                except Exception as e:
                    raise SystemExit(f"Failed parsing profile row for {gpu_name} on line {k+1}: {r}\nError: {e}")

                k += 1

            # sort profiles for nicer UX
            profiles.sort(key=lambda p: (p["gb"], p["name"]))

            gpus.append({
                "key": f"{slug(gpu_name)}-{mem_gb}",
                "label": gpu_name,
                "memoryGB": mem_gb,
                "arch": arch,
                "profiles": profiles
            })

            # continue scanning from end of section
            i = k
            continue

        i += 1

    if not gpus:
        raise SystemExit("No GPU sections found. Expected lines starting with 'GPU Memory,<X GB>'.")

    # sort by memory desc then label
    gpus.sort(key=lambda g: (-g["memoryGB"], g["label"]))

    return {
        "version": "generated-from-section-csv",
        "source": "user CSV",
        "gpus": gpus
    }

def main():
    rows = read_rows(CSV_PATH)
    catalog = parse_sections(rows)

    OUT_PATH.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote: {OUT_PATH}")
    print(f"GPUs: {len(catalog['gpus'])}")
    for g in catalog["gpus"]:
        print(f"  - {g['key']}  ({g['label']}, {g['memoryGB']} GB, profiles={len(g['profiles'])})")

if __name__ == "__main__":
    main()
