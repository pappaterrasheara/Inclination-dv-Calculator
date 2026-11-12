# Inclination Δv Calculator

**How much does it cost to tilt an orbit?** A Python tool that calculates the Δv for orbital plane changes, from a single burn to a full orbit transfer, and shows how combining burns saves fuel.

![Δv versus inclination change for low Earth, GPS and geostationary orbits](docs/delta_v_vs_inclination.png)

Plane changes are among the most expensive maneuvers in spaceflight. A 28.5° change in a 400 km orbit costs about **3.8 km/s**, nearly half the orbital speed. This tool shows that cost step by step, and how mission designers cut it.

## Features

- **Plane change Δv** from an orbital velocity or an altitude
- **Orbit transfers** (Hohmann) with a plane change, comparing separate burns with one combined burn
- **Propellant estimates** from the Tsiolkovsky rocket equation
- **Earth, Moon and Mars**
- **13 unit tests plus doctests,** run automatically on every push with GitHub Actions
- Standard library only for the calculator; matplotlib only for the plot

## Quick start

```bash
git clone <this repo>
cd <repo folder>
python inclination_delta_v_calculator.py
```

## Example: low Earth orbit to geostationary orbit

A satellite launched from Cape Canaveral starts in a 28.5° orbit, but geostationary orbit sits over the equator at 0°. How should it get there?

```bash
python inclination_delta_v_calculator.py transfer --from-altitude 300 --to-altitude 35786 --delta-i 28.5
```

```
=== Transfer: 300 km → 35786 km, Δi = 28.5° (Earth) ===
Transfer time: 5.28 h

Option A, separate burns
  Burn 1 (enter transfer)          2,425.7 m/s
  Burn 2 (circularize)             1,466.8 m/s
  Plane change (higher orbit)      1,513.7 m/s
  Total                            5,406.2 m/s

Option B, plane change combined with the burn at the high point
  Burn 1                           2,425.7 m/s
  Burn 2                           1,830.2 m/s
  Total                            4,256.0 m/s

Combining saves 1,150.3 m/s (21.3% less Δv).
```

Folding the plane change into the circularization burn, where the spacecraft moves slowest, saves over 1 km/s. That's why real geostationary missions do it this way.

## More examples

```bash
# Plane change from an altitude
python inclination_delta_v_calculator.py plane-change --altitude 400 --delta-i 28.5

# Add an engine and spacecraft mass to estimate propellant
python inclination_delta_v_calculator.py plane-change --altitude 400 --delta-i 10 --isp 320 --mass 1500

# Mars orbit
python inclination_delta_v_calculator.py plane-change --body mars --altitude 300 --delta-i 15

# Regenerate the plot
pip install -r requirements.txt
python plot_delta_v.py
```

## The physics

**Pure plane change:** the speed stays the same, and the velocity vector turns by Δi.

$$
\Delta v = 2v\sin\left(\frac{\Delta i}{2}\right)
$$

**Combined burn:** change speed and plane at once, by the law of cosines.

$$
\Delta v = \sqrt{v_1^2 + v_2^2 - 2v_1v_2\cos\Delta i}
$$

**Orbital speed** anywhere on an orbit (vis-viva), with $a$ the semi-major axis:

$$
v = \sqrt{\mu\left(\frac{2}{r} - \frac{1}{a}\right)}
$$

**Propellant** (Tsiolkovsky rocket equation):

$$
m_{prop} = m_0\left(1 - e^{-\Delta v / (I_{sp} g_0)}\right)
$$

## Assumptions

- Circular start and target orbits, and impulsive (instant) burns.
- Plane changes happen at the ascending or descending node.
- Two-body gravity only: no drag, no Earth oblateness (J2), no third bodies.

## Project structure

```
├── inclination_delta_v_calculator.py   # physics + command-line tool
├── plot_delta_v.py                     # generates the plot in docs/
├── tests/test_calculator.py            # 13 unit tests
├── docs/delta_v_vs_inclination.png
└── .github/workflows/tests.yml         # runs the tests on every push
```

## Running the tests

```bash
python -m unittest discover -s tests -v
python -m doctest -v inclination_delta_v_calculator.py
```

The tests check known values, including the classic result of about 4.26 km/s for a combined low Earth orbit to geostationary transfer.

## Roadmap

- Elliptical start and target orbits
- Bi-elliptic transfers for very large orbit changes
- Optimal split of the plane change between both burns

## License

MIT, see [LICENSE](LICENSE).
