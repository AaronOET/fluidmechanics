import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brentq


def colebrook_white(Re, eps_over_D):
    """Solve Colebrook-White equation for Darcy friction factor f.

    1/sqrt(f) = -2*log10( eps/(3.7*D) + 2.51/(Re*sqrt(f)) )
    """
    def residual(f):
        return 1.0 / np.sqrt(f) + 2.0 * np.log10(
            eps_over_D / 3.7 + 2.51 / (Re * np.sqrt(f))
        )
    return brentq(residual, 1e-6, 1.0)


def main():
    Re_range = np.logspace(np.log10(10_000), np.log10(2_000_000), 200)
    roughness_list = [0.0, 1e-6, 1e-5, 5e-5, 1e-4, 5e-4, 1e-3, 5e-3, 1e-2, 5e-2]

    fig, ax = plt.subplots(figsize=(10, 7))

    for eps_D in roughness_list:
        f_vals = [colebrook_white(Re, eps_D) for Re in Re_range]
        label = "smooth" if eps_D == 0 else f"ε/D = {eps_D:g}"
        ax.plot(Re_range, f_vals, label=label)

    # Laminar reference f = 64/Re for Re < 4000 (shown outside range for reference only)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Reynolds number, Re")
    ax.set_ylabel("Darcy friction factor, f")
    ax.set_title("Moody Chart — Colebrook–White equation")
    ax.grid(True, which="both", ls="--", alpha=0.5)
    ax.legend(loc="best", fontsize=8)
    ax.set_xlim(1e4, 2e6)

    out_path = "moody_chart.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    print(f"Saved plot to {out_path}")


if __name__ == "__main__":
    main()
