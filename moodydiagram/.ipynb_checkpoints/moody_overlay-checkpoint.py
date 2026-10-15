"""Moody chart overlay: georeference the Nalluri chart image and overlay the
Colebrook-White curve with an interactive ipywidgets control panel.

Chart coordinates: x = log10(Re), y = Darcy friction factor f.
"""
import warnings
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import rasterio
import rasterio.control
import rasterio.transform
from rasterio.errors import NotGeoreferencedWarning
from rasterio.plot import show
import ipywidgets as widgets

from colebrook_white import colebrook_white

# Ground control points: pixel (col, row) -> (log10 Re, f)
DEFAULT_GCPS = [
    rasterio.control.GroundControlPoint(col=212, row=80, x=3, y=0.038),
    rasterio.control.GroundControlPoint(col=212, row=1240, x=3, y=0.008),
    rasterio.control.GroundControlPoint(col=1756, row=80, x=7, y=0.038),
]

# Chart axes, used for the dashed guide lines to the evaluated point
AXIS_LOG_RE = 3      # left edge of the chart (Re = 10^3)
AXIS_F = 0.008       # bottom edge of the chart

RN_VALUES = np.logspace(4, 7, 200)


# --- Georeferencing ------------------------------------------------------
def georeference(image_path, output_path, gcps=DEFAULT_GCPS):
    """Write a georeferenced GeoTIFF of the chart image and return it opened."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    transform = rasterio.transform.from_gcps(gcps)

    # The source image is a plain JPG/PNG with no geotransform yet; that is
    # expected here, so silence rasterio's NotGeoreferencedWarning.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", NotGeoreferencedWarning)
        with rasterio.open(image_path) as src:
            bands = src.read([1, 2, 3])

    with rasterio.open(
        output_path,
        "w",
        driver="GTiff",
        height=bands.shape[1],
        width=bands.shape[2],
        count=3,
        dtype=bands.dtype,
        transform=transform,
    ) as dst:
        dst.write(bands)

    return rasterio.open(output_path)


# --- Friction factor -----------------------------------------------------
def friction_factor(Re, eps_D):
    """Colebrook-White Darcy f at Re (scalar or array-like)."""
    Re_arr = np.atleast_1d(np.asarray(Re, dtype=float))
    if np.any(Re_arr <= 0):
        raise ValueError("Re must be > 0")
    f = np.array([colebrook_white(r, eps_D) for r in Re_arr])
    return f[0] if np.ndim(Re) == 0 else f


def _roughness_label(eps_D):
    return "smooth" if eps_D == 0 else f"ε/D = {eps_D:g}"


# --- Plot ----------------------------------------------------------------
def build_figure(raster, eps_D, Re_eval=0):
    """Chart image + Colebrook-White curve, optionally marking f at Re_eval.

    Returns (fig, msg) where msg describes the evaluated point ("" if none).
    """
    cf_values = friction_factor(RN_VALUES, eps_D)
    label = _roughness_label(eps_D)

    fig, ax = plt.subplots(figsize=(10, 8))
    show(raster, ax=ax)
    ax.set_aspect(110)
    ax.plot(np.log10(RN_VALUES), cf_values, color="C1", linewidth=2,
            label=f"Colebrook-White ({label})")

    msg = ""
    if Re_eval > 0:
        f_eval = friction_factor(Re_eval, eps_D)
        x = np.log10(Re_eval)
        msg = f"Re = {Re_eval:,.0f},  {label}  →  f = {f_eval:.5f}"
        ax.plot([x, x], [AXIS_F, f_eval], "--", color="tab:red", lw=1)
        ax.plot([AXIS_LOG_RE, x], [f_eval, f_eval], "--", color="tab:red", lw=1)
        ax.plot(x, f_eval, "o", color="tab:red", ms=7)
        ax.annotate(f"Re = {Re_eval:.3g}\nf = {f_eval:.4f}", (x, f_eval),
                    xytext=(8, 8), textcoords="offset points", color="tab:red",
                    fontweight="bold")

    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.02), frameon=False)
    ax.set_axis_off()
    return fig, msg


# --- Widgets -------------------------------------------------------------
_STYLE = {"description_width": "110px"}


def _text_with_log_slider(label, value, vmax, step, log_min, log_max,
                          log_step, readout_format):
    """A text box and a log slider kept in sync (the slider cannot show 0)."""
    text = widgets.BoundedFloatText(
        value=value, min=0.0, max=vmax, step=step,
        description=f"{label}:", style=_STYLE,
        layout=widgets.Layout(width="240px"),
    )
    slider = widgets.FloatLogSlider(
        value=value, base=10, min=log_min, max=log_max, step=log_step,
        description=f"{label} (log):", readout_format=readout_format,
        style=_STYLE, continuous_update=False,
        layout=widgets.Layout(width="500px"),
    )

    def _text_to_slider(change):
        v = change["new"]
        if v > 0:
            slider.value = min(max(v, 10**slider.min), 10**slider.max)

    def _slider_to_text(change):
        if text.value == 0 or not np.isclose(text.value, change["new"]):
            text.value = change["new"]

    text.observe(_text_to_slider, names="value")
    slider.observe(_slider_to_text, names="value")
    return text, slider


def moody_widget(raster, eps_D=0.008, Re=1e5):
    """Interactive overlay: set ε/D and Re, see the curve, point and f value."""
    eps_text, eps_slider = _text_with_log_slider(
        "ε/D", eps_D, vmax=0.1, step=1e-4,
        log_min=-6, log_max=-2, log_step=0.05, readout_format=".2e",
    )
    re_text, re_slider = _text_with_log_slider(
        "Re", Re, vmax=1e7, step=1000,
        log_min=3, log_max=7, log_step=0.01, readout_format=".3e",
    )
    f_readout = widgets.HTML()

    def _update(eps_D, Re_eval):
        fig, msg = build_figure(raster, eps_D, Re_eval)
        plt.show()
        f_readout.value = (f"<b>{msg}</b>" if msg
                           else "Enter Re &gt; 0 to evaluate f")

    out = widgets.interactive_output(
        _update, {"eps_D": eps_text, "Re_eval": re_text}
    )

    return widgets.VBox([
        widgets.HBox([eps_text, eps_slider]),
        widgets.HBox([re_text, re_slider]),
        f_readout,
        out,
    ])
