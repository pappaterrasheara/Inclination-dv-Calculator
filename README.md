# Inclination Delta-V Calculator

A Python tool to calculate the delta-v (Δv) required to perform an orbital inclination change maneuver. By inputting the spacecraft’s current orbital velocity and the desired inclination change angle, this script applies fundamental orbital mechanics formulas to provide precise Δv estimates.

---

## Table of Contents
- [Overview](#overview)  
- [Background](#background)  
- [How It Works](#how-it-works)  
- [Usage](#usage)  
- [Code Structure](#code-structure)  
- [Example](#example)  
- [Requirements](#requirements)  
- [Future Improvements](#future-improvements)  
- [License](#license)  

---

## Overview

Orbital inclination changes are among the most fuel-intensive maneuvers in spacecraft missions. Knowing the delta-v needed for such maneuvers is critical for mission design and fuel budgeting. This calculator takes velocity (m/s) and inclination change (degrees) as inputs and computes the required Δv using the classical inclination change formula:

\[
\Delta v = 2 v \sin\left(\frac{\Delta i}{2}\right)
\]

where:  
- \(v\) = orbital velocity  
- \(\Delta i\) = inclination change angle in radians

---

## Background

In orbital mechanics, inclination refers to the tilt of a spacecraft's orbit relative to a reference plane (usually Earth's equator). Changing inclination requires a velocity change perpendicular to the current orbital velocity vector, which demands fuel (delta-v).

Calculating the exact delta-v helps engineers optimize mission profiles, minimizing fuel consumption while achieving desired orbital parameters.

---

## How It Works

1. The user provides two inputs:
   - **Velocity (v):** Current orbital velocity in meters per second (m/s).
   - **Inclination change (Δi):** Desired change in inclination angle in degrees.

2. The program converts the inclination change from degrees to radians for trigonometric calculations.

3. It calculates delta-v using the formula:  
   \[
   \Delta v = 2 v \sin\left(\frac{\Delta i}{2}\right)
   \]

4. The result (delta-v) is displayed in meters per second (m/s), representing the velocity change required to perform the inclination adjustment.

---

## Usage

Run the script using Python 3:

```bash
python inc_dv_calc.py
