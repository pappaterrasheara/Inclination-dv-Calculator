"""
inclination_delta_v_calculator.py
Author: Sheara Pappaterra

Δv for orbital plane (inclination) changes, from a single burn to a full
orbit transfer where the plane change is combined with circularization.

Two modes:
  plane-change  Δv to tilt an orbit by Δi (the default)
  transfer      Hohmann transfer between two circular orbits with a plane
                change, comparing "separate burns" with "combined burn"

Examples:
  python inclination_delta_v_calculator.py
  python inclination_delta_v_calculator.py plane-change --altitude 400 --delta-i 28.5
  python inclination_delta_v_calculator.py plane-change --altitude 400 --delta-i 10 --isp 320 --mass 1500
  python inclination_delta_v_calculator.py transfer --from-altitude 300 --to-altitude 35786 --delta-i 28.5
  python inclination_delta_v_calculator.py plane-change --body mars --altitude 300 --delta-i 15
"""

import argparse
import math
import sys

G0 = 9.80665  # standard gravity, m/s^2

# Gravitational parameter (m^3/s^2) and mean equatorial radius (km)
BODIES = {
    "earth": {"mu": 3.986004418e14, "radius_km": 6378.137},
    "moon": {"mu": 4.9048695e12, "radius_km": 1737.4},
    "mars": {"mu": 4.282837e13, "radius_km": 3396.2},
}


# ---------------------------------------------------------------- physics

def orbit_radius_m(altitude_km, body="earth"):
    """Distance from the body's center, in meters."""
    if altitude_km < 0:
        raise ValueError("Altitude can't be negative.")
    return (BODIES[body]["radius_km"] + altitude_km) * 1000.0


def circular_velocity(altitude_km, body="earth"):
    """Speed of a circular orbit at an altitude, in m/s.

    >>> round(circular_velocity(400), 1)
    7668.6
    """
    return math.sqrt(BODIES[body]["mu"] / orbit_radius_m(altitude_km, body))


def vis_viva(r_m, a_m, body="earth"):
    """Speed anywhere on an orbit (vis-viva equation), in m/s.

    >>> r = orbit_radius_m(400)
    >>> round(vis_viva(r, r), 1) == round(circular_velocity(400), 1)
    True
    """
    return math.sqrt(BODIES[body]["mu"] * (2 / r_m - 1 / a_m))


def delta_v_plane_change(v_m_s, delta_i_deg):
    """Δv for a pure inclination change: Δv = 2 v sin(Δi / 2), in m/s.

    >>> round(delta_v_plane_change(7500, 30), 2)
    3882.29
    """
    if v_m_s <= 0:
        raise ValueError("Velocity must be greater than 0 m/s.")
    if not 0 <= delta_i_deg <= 180:
        raise ValueError("Inclination change must be between 0 and 180 degrees.")
    return 2 * v_m_s * math.sin(math.radians(delta_i_deg) / 2)


def delta_v_combined(v1_m_s, v2_m_s, delta_i_deg):
    """Δv for one burn that changes both speed and plane (law of cosines), in m/s.

    >>> round(delta_v_combined(7500, 7500, 30), 2) == round(delta_v_plane_change(7500, 30), 2)
    True
    """
    if not 0 <= delta_i_deg <= 180:
        raise ValueError("Inclination change must be between 0 and 180 degrees.")
    cos_di = math.cos(math.radians(delta_i_deg))
    return math.sqrt(v1_m_s**2 + v2_m_s**2 - 2 * v1_m_s * v2_m_s * cos_di)


def hohmann_with_plane_change(from_alt_km, to_alt_km, delta_i_deg, body="earth"):
    """Compare two ways to move between circular orbits and change plane.

    Separate: Hohmann transfer, then a plane change in the higher circular orbit.
    Combined: Hohmann transfer with the plane change folded into the burn
              at the transfer orbit's high point, where the spacecraft is slowest.

    Returns a dict of Δv values in m/s.
    """
    r1, r2 = orbit_radius_m(from_alt_km, body), orbit_radius_m(to_alt_km, body)
    a_t = (r1 + r2) / 2
    v1, v2 = circular_velocity(from_alt_km, body), circular_velocity(to_alt_km, body)
    vt1, vt2 = vis_viva(r1, a_t, body), vis_viva(r2, a_t, body)

    burn1 = abs(vt1 - v1)
    burn2 = abs(v2 - vt2)
    plane_high = delta_v_plane_change(min(v1, v2), delta_i_deg)  # higher orbit = slower
    separate = burn1 + burn2 + plane_high

    if r2 >= r1:  # raising: combine the plane change with circularization at r2
        combined_burn1, combined_burn2 = burn1, delta_v_combined(vt2, v2, delta_i_deg)
    else:         # lowering: combine it with the first burn at r1
        combined_burn1, combined_burn2 = delta_v_combined(v1, vt1, delta_i_deg), burn2
    combined = combined_burn1 + combined_burn2

    return {
        "burn1": burn1, "burn2": burn2, "plane_change_high": plane_high,
        "separate_total": separate,
        "combined_burn1": combined_burn1, "combined_burn2": combined_burn2,
        "combined_total": combined,
        "savings": separate - combined,
        "transfer_time_h": math.pi * math.sqrt(a_t**3 / BODIES[body]["mu"]) / 3600,
    }


def propellant_mass(delta_v_m_s, isp_s, initial_mass_kg):
    """Propellant burned for a given Δv (Tsiolkovsky rocket equation), in kg.

    >>> round(propellant_mass(1000, 300, 1000), 1)
    288.2
    """
    if isp_s <= 0 or initial_mass_kg <= 0:
        raise ValueError("Isp and initial mass must be greater than 0.")
    return initial_mass_kg * (1 - math.exp(-delta_v_m_s / (isp_s * G0)))


# ---------------------------------------------------------------- reports

def print_propellant(dv, isp, mass):
    if isp is not None and mass is not None:
        prop = propellant_mass(dv, isp, mass)
        print(f"Propellant (Isp {isp:g} s, {mass:,.0f} kg start) = {prop:,.1f} kg "
              f"({prop / mass:.1%} of the spacecraft)")


def report_plane_change(args):
    if args.altitude is not None:
        v = circular_velocity(args.altitude, args.body)
        where = f"Circular {args.body.title()} orbit at {args.altitude:g} km"
    else:
        v = args.velocity if args.velocity is not None else 7500.0
        where = "Given orbital velocity"
    dv = delta_v_plane_change(v, args.delta_i)
    half = args.delta_i / 2
    print("=== Plane change ===")
    print(where)
    print(f"Orbital velocity v   = {v:,.1f} m/s")
    print(f"Inclination change   = {args.delta_i:g}°  (Δi/2 = {half:g}°)")
    print(f"sin(Δi/2)            = {math.sin(math.radians(half)):.4f}")
    print(f"Δv = 2 v sin(Δi/2)   = {dv:,.2f} m/s")
    print(f"That's {dv / v:.1%} of the orbital speed.")
    print_propellant(dv, args.isp, args.mass)


def report_transfer(args):
    r = hohmann_with_plane_change(args.from_altitude, args.to_altitude, args.delta_i, args.body)
    print(f"=== Transfer: {args.from_altitude:g} km → {args.to_altitude:g} km, "
          f"Δi = {args.delta_i:g}° ({args.body.title()}) ===")
    print(f"Transfer time: {r['transfer_time_h']:.2f} h\n")
    print("Option A, separate burns")
    print(f"  Burn 1 (enter transfer)        {r['burn1']:>9,.1f} m/s")
    print(f"  Burn 2 (circularize)           {r['burn2']:>9,.1f} m/s")
    print(f"  Plane change (higher orbit)    {r['plane_change_high']:>9,.1f} m/s")
    print(f"  Total                          {r['separate_total']:>9,.1f} m/s\n")
    print("Option B, plane change combined with the burn at the high point")
    print(f"  Burn 1                         {r['combined_burn1']:>9,.1f} m/s")
    print(f"  Burn 2                         {r['combined_burn2']:>9,.1f} m/s")
    print(f"  Total                          {r['combined_total']:>9,.1f} m/s\n")
    print(f"Combining saves {r['savings']:,.1f} m/s "
          f"({r['savings'] / r['separate_total']:.1%} less Δv).")
    print_propellant(r["combined_total"], args.isp, args.mass)


# ---------------------------------------------------------------- CLI

def build_parser():
    parser = argparse.ArgumentParser(description="Δv for orbital inclination changes.")
    sub = parser.add_subparsers(dest="mode")

    def common(p):
        p.add_argument("--delta-i", type=float, default=30, help="inclination change, degrees")
        p.add_argument("--body", choices=sorted(BODIES), default="earth")
        p.add_argument("--isp", type=float, help="engine specific impulse, s (optional)")
        p.add_argument("--mass", type=float, help="spacecraft mass before the burn, kg (optional)")

    pc = sub.add_parser("plane-change", help="Δv to tilt an orbit")
    speed = pc.add_mutually_exclusive_group()
    speed.add_argument("--velocity", type=float, help="orbital velocity, m/s")
    speed.add_argument("--altitude", type=float, help="circular orbit altitude, km")
    common(pc)

    tr = sub.add_parser("transfer", help="orbit transfer with a plane change")
    tr.add_argument("--from-altitude", type=float, required=True, help="start altitude, km")
    tr.add_argument("--to-altitude", type=float, required=True, help="target altitude, km")
    common(tr)
    return parser


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0].startswith("-"):
        argv = ["plane-change", *argv]  # default mode keeps the original behavior
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        report_transfer(args) if args.mode == "transfer" else report_plane_change(args)
    except ValueError as err:
        parser.error(str(err))


if __name__ == "__main__":
    main()
