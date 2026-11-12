"""
plot_delta_v.py
Author: Sheara Pappaterra

Plots Δv versus inclination change for several orbits and saves
docs/delta_v_vs_inclination.png. Requires matplotlib.
"""
import os

import matplotlib.pyplot as plt

from inclination_delta_v_calculator import circular_velocity, delta_v_plane_change

ORBITS = [
    ("Low Earth orbit, 400 km", 400),
    ("GPS orbit, 20,200 km", 20200),
    ("Geostationary, 35,786 km", 35786),
]


def main():
    angles = [a / 2 for a in range(0, 181)]  # 0 to 90 degrees
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for label, altitude in ORBITS:
        v = circular_velocity(altitude)
        ax.plot(angles, [delta_v_plane_change(v, a) / 1000 for a in angles], linewidth=2.2, label=label)

    ax.set_title("Plane changes get expensive fast, and cost less in higher orbits", fontsize=13)
    ax.set_xlabel("Inclination change (degrees)")
    ax.set_ylabel("Δv (km/s)")
    ax.grid(alpha=0.3)
    ax.legend(frameon=False)
    ax.set_xlim(0, 90)
    ax.set_ylim(bottom=0)
    fig.tight_layout()

    os.makedirs("docs", exist_ok=True)
    out = os.path.join("docs", "delta_v_vs_inclination.png")
    fig.savefig(out, dpi=160)
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
