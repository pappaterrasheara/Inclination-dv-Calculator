# inclination_delta_v_calculator.py
# Author: OpenAI + Your Edits
# Description: A smart, clear program to compute Δv for orbital inclination changes.

import math

def delta_v_inclination(v_m_s, delta_i_deg):
    """
    Compute Δv for inclination change.
    Args:
        v_m_s (float): orbital velocity in m/s
        delta_i_deg (float): inclination change in degrees
    Returns:
        float: delta-v in m/s
    """
    delta_i_rad = math.radians(delta_i_deg)
    sin_half_delta_i = math.sin(delta_i_rad / 2)
    dv = 2 * v_m_s * sin_half_delta_i
    
    print("=== Inclination Δv Calculator ===")
    print(f"Input velocity: {v_m_s} m/s")
    print(f"Inclination change: {delta_i_deg} degrees")
    print(f"Δi/2 = {delta_i_deg / 2} degrees")
    print(f"sin(Δi/2) ≈ {sin_half_delta_i:.4f}")
    print(f"2 * v = {2 * v_m_s} m/s")
    print(f"Δv ≈ {dv:.2f} m/s")
    
    return dv

if __name__ == "__main__":
    # Feel free to edit these values anytime
    velocity = 7500  # m/s
    inclination_change = 30  # degrees
    delta_v_inclination(velocity, inclination_change)
