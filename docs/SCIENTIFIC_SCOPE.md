# Scientific Scope and Evidence Standard

This repository is an evidence-aware candidate toolkit and a foundation for a
future discovery workflow. It has **not** discovered, synthesized, or confirmed
a room-temperature superconductor.

## Success criterion

The default objective requires all of the following:

- critical temperature at or above 273.15 K;
- operating pressure at or below 1 GPa;
- measured electrical and magnetic evidence;
- independent replication by at least two laboratories.

No record currently satisfies all four gates.

## Evidence policy

Records are classified as measured, calculated, claimed, or unclassified, with
verification tracked separately. Retracted and disputed claims are retained for
auditability but quarantined from default ranking. A numeric `Tc` is never, by
itself, treated as confirmation. Legacy inference is deliberately conservative:
a citation without an explicit physical measurement method remains
`unclassified`, while computational method metadata is classified as
`calculated`. Explicit classifications should be added only after reviewing the
source and its underlying evidence.

The default predictor is a benchmark lookup for a small set of known materials.
It rejects unsupported formulas and pressure regimes. The historical
formula-only heuristic requires explicit opt-in and returns zero confidence.

## Required discovery gates

1. Variable-composition and crystal-structure search from a named provider.
2. Formation enthalpy and convex-hull assessment at pressure.
3. Dynamical stability with no unresolved imaginary phonons.
4. Converged electron-phonon calculations, including material anharmonicity.
5. Synthesis with sample identity, structure, composition, and raw data.
6. Zero resistance and magnetic expulsion with calibration records.
7. Independent replication in at least two laboratories.

The software defines artifacts and gates for these stages. It does not include
an HPC structure-search engine, qualified pseudopotential library, high-pressure
facility, or laboratory instruments. Those are required external providers;
missing providers cause explicit failure rather than a simulation fallback.

## Scientific benchmarks

Accepted benchmarks include H3S near 203 K at roughly 155 GPa and LaH10 near
250 K at roughly 170 GPa. These are near-room-temperature results under extreme
pressure, not ambient-condition room-temperature superconductors.

Prominent carbonaceous sulfur hydride and nitrogen-doped lutetium hydride claims
were retracted. They illustrate why raw data, provenance, magnetic evidence, and
replication are mandatory.

Primary references:

- A. P. Drozdov et al., *Nature* 525, 73–76 (2015),
  https://doi.org/10.1038/nature14964
- A. P. Drozdov et al., *Nature* 569, 528–531 (2019),
  https://doi.org/10.1038/s41586-019-1201-8
- Retraction, *Nature* 610, 804 (2022),
  https://doi.org/10.1038/s41586-022-05294-9
- Retraction, *Nature* 624, 460 (2023),
  https://doi.org/10.1038/s41586-023-06774-2
