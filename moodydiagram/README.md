# Moody diagram — Colebrook–White overlay

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/AaronOET/fluidmechanics/main?urlpath=lab/tree/moodydiagram/moody_diagram.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AaronOET/fluidmechanics/blob/main/moodydiagram/moody_diagram.ipynb)

An interactive Jupyter notebook that draws the Colebrook–White friction-factor
curve on top of a scanned Moody chart, so you can read the Darcy friction
factor **f** for any Reynolds number **Re** and relative roughness **ε/D**.

Click the **launch binder** or **Open in Colab** badge above to run it in your
browser with nothing to install. The first Binder launch can take a few minutes
while it builds the environment; on Colab the notebook downloads its helper
files on first run.

## What the notebook does

[`moody_diagram.ipynb`](moody_diagram.ipynb):

1. **Georeferences the chart image.** The Moody chart scan is mapped to chart
   coordinates (x = log₁₀ Re, y = f) using ground control points, and saved as
   a GeoTIFF in `RAS/`.
2. **Overlays the Colebrook–White curve** for the chosen ε/D across
   Re = 10⁴ – 10⁷, solving

   $$\frac{1}{\sqrt{f}} = -2\log_{10}\left(\frac{\varepsilon/D}{3.7} + \frac{2.51}{Re\sqrt{f}}\right)$$

3. **Evaluates a point.** Enter a Reynolds number and the notebook marks it on
   the curve, draws guide lines to the axes and prints the friction factor.

Use the text boxes for exact values or the log sliders to sweep:

| Control | Range |
|---|---|
| ε/D | 0 (smooth) – 0.1 |
| Re | 10³ – 10⁷ |

## Files

| File | Purpose |
|---|---|
| [`moody_diagram.ipynb`](moody_diagram.ipynb) | The interactive notebook |
| [`moody_overlay.py`](moody_overlay.py) | Georeferencing, plotting and widget code |
| [`colebrook_white.py`](colebrook_white.py) | Colebrook–White solver; run it directly to plot a standalone Moody chart |
| `bgimgs/` | Background Moody chart image |
| `RAS/` | Georeferenced GeoTIFF written by the notebook |

## Running locally

Create the environment from [`environment.yml`](../environment.yml) at the
repository root (conda-forge is recommended because of `rasterio`):

```bash
conda env create -f environment.yml
conda activate fluidmechanics
jupyter lab moodydiagram/moody_diagram.ipynb
```

## Image credit

Background Moody chart from *Nalluri & Featherstone's Civil Engineering
Hydraulics: Essential Theory with Worked Examples*, 6th Edition, Figure 4.2,
p. 92.
