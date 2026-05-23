# HFPMVS

Official CUDA implementation of **High Fidelity Aggregated Planar Prior Assisted PatchMatch Multi-View Stereo** (HFP-MVS / HFPMVS).

This repository extends the PatchMatch MVS pipeline with **segmentation-guided aggregated planar priors**: SAM-based region masks distinguish depth-continuous object interiors from boundaries, Delaunay triangulation fits **object planes** and **boundary planes**, and a multi-plane aggregated prior is embedded into GPU PatchMatch matching costs. The goal is sharper object boundaries and more complete reconstruction on weakly textured regions (ETH3D, Tanks & Temples).



## Requirements

| Dependency | Version (tested / configured) |
|------------|-------------------------------|
| OS | Linux (recommended) |
| GPU | NVIDIA GPU with CUDA support (arch `sm_61`, `sm_70` in `CMakeLists.txt`) |
| CUDA | 11.8 (edit `CUDA_TOOLKIT_ROOT_DIR` in `CMakeLists.txt` if needed) |
| CMake | ≥ 2.8 |
| OpenCV | 4.x (with `imgproc`, `calib3d`, `highgui`, etc.) |
| Compiler | GCC with C++11, OpenMP |

---

## Build

```bash
mkdir -p build && cd build
cmake ..
make -j
```

The executable is **`HFPMVS`** (built in the build directory or project root, depending on your CMake layout).

Alternatively, use the helper script (Linux):

```bash
python run.py   # calls cmake + make inside run.py::build()
```

Before building, set `CUDA_TOOLKIT_ROOT_DIR` and GPU architectures in `CMakeLists.txt` to match your machine.

---

## Data preparation

Input layout follows the **ACMM / COLMAP MVS** dense folder convention:

```text
dense_folder/
├── pair.txt
├── images/
│   ├── 00000000.jpg
│   └── ...
├── cams/
│   ├── 00000000_cam.txt
│   └── ...
└── region_1/                    # SAM segmentation masks (planar-prior stage)
    ├── 0/
    │   └── region.png           # grayscale, same semantics as image id
    └── ...
```

### `pair.txt`

```
<num_images>
<ref_id> <num_src> <src_id_0> <score_0> <src_id_1> <score_1> ...
...
```

Only source pairs with `score > 0` are used (`main.cpp`).

### `*_cam.txt`

ACMM-style camera file: extrinsics `R|t`, intrinsics `K`, then `depth_min interval depth_num depth_max` (see `ReadCamera` in `HFPMVS.cpp`).

### Segmentation masks

For planar-prior passes, each reference view needs:

```text
dense_folder/<region_name>/<ref_image_id>/region.png
```

- `region_name` is `region_1` on the coarsest pyramid level and `region_no_span` on finer levels (see `main.cpp`).
- Pixels in the **same SAM segment** should share the same label; the code uses label equality inside Delaunay triangles to decide object vs. boundary planes.

Prepare masks with [Segment Anything](https://github.com/facebookresearch/segment-anything) (or your own pipeline) and export one mask per view.

---

## Usage

```bash
./HFPMVS <dense_folder> <output_folder>
```

Example:

```bash
./HFPMVS /path/to/dense /path/to/output
```

### Pipeline (default `main.cpp`)

1. **Multi-scale scheduling** — compute per-image downscale count (bound: long edge ≤ 1000 px).
2. **Coarsest scale**
   - Planar prior + PatchMatch (`region_1`).
   - Geometric consistency (2 iterations; second uses multi-geometry).
3. **Finer scales**
   - Joint bilateral upsampling of `depths_geom.dmb`.
   - Hierarchy + planar prior (`region_no_span`) + geometric consistency.
4. **Fusion** — write `output_folder/HFPMVS/HFPMVS_model.ply`.

Per-view results are stored under:

```text
output_folder/HFPMVS/<image_id>/
├── depths.dmb          # photometric depth
├── depths_geom.dmb     # after geometric consistency
├── depths_prior.dmb    # planar prior depth (planar stage)
├── normals.dmb
├── normals_prior.dmb
├── costs.dmb
├── plane_masks.dmb
└── triangulation.png   # debug: Delaunay + boundary/object edges
```

Depth/normal files use the **DMB** binary format (`readDepthDmb` / `writeDepthDmb` in `HFPMVS.cpp`).

---

## Project structure

| File | Description |
|------|-------------|
| `HFPMVS.h` / `HFPMVS.cpp` | Host-side MVS class, I/O, planar prior, camera handling |
| `HFPMVS.cu` | CUDA PatchMatch kernels (NCC, propagation, region constraints) |
| `main.cpp` | Multi-scale orchestration, fusion, CLI |
| `main.h` | `Camera`, `Problem`, shared types |
| `debugger.cu` / `debugger.h` | Optional runtime logging |
| `run.py` | Build / run / evaluation helpers (paths are machine-specific) |
| `CMakeLists.txt` | CUDA + OpenCV build |

---

## Citation

If you use this code, please cite our paper:

```bibtex
@inproceedings{hfpmvs2024,
  title={High Fidelity Aggregated Planar Prior Assisted PatchMatch Multi-View Stereo},
  booktitle={ACM Multimedia},
  year={2024}
}
```

Please replace the BibTeX entry with the final published metadata from your PDF / publisher page.


---

## Acknowledgements

This implementation builds upon ideas and code from **ACMMP** / **ACMM** PatchMatch MVS. We thank the original authors for releasing their CUDA framework.

---

## License

If not specified in the repository, please contact the authors for licensing terms before redistribution.
