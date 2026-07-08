# Grant Proposal: Discovery and Manufacturing of Room-Temperature Superconducting Compounds

## Executive Summary

This proposal outlines a comprehensive research program to discover and develop room-temperature superconducting materials through a combination of advanced computational screening, high-pressure synthesis, and scalable manufacturing techniques. Building on recent breakthroughs in hydride superconductors (e.g., H3S with Tc ~203 K under 155 GPa, LaH10 with Tc ~250 K under 170 GPa), we aim to identify and stabilize compounds that exhibit superconductivity at ambient pressure and temperature. The project integrates density functional theory (DFT) and machine learning (ML) for candidate prediction, diamond anvil cell (DAC) and laser-heated synthesis for validation, and chemical doping/interface engineering for pressure reduction. A pilot manufacturing line will be designed to produce gram-scale quantities of the most promising candidates. The expected outcomes include a validated room-temperature superconductor, a patent portfolio, and a scalable production process.

## Technical Approach

### Chemistry and Physics of Room-Temperature Superconductivity

Room-temperature superconductivity is theorized to arise from strong electron-phonon coupling in hydrogen-rich compounds under high pressure (Ashcroft, 2004). The key physics involves:
- **High-frequency phonons** from light hydrogen atoms, leading to high critical temperatures (BCS theory).
- **Metallic hydrogen** or hydrogen-dominant alloys that exhibit a large electronic density of states at the Fermi level.
- **Pressure-induced structural transitions** that stabilize covalent or ionic hydrogen networks.

Our approach will focus on ternary and quaternary hydrides (e.g., Li-Mg-H, C-S-H, Y-N-H) predicted to have lower stabilization pressures (<50 GPa) while maintaining high Tc. We will use evolutionary algorithms and ML interatomic potentials to search the vast compositional space.

### Computational Screening

- **High-throughput DFT** (VASP, Quantum ESPRESSO) to calculate formation enthalpies, phonon spectra, and electron-phonon coupling for ~10,000 candidate compositions.
- **Machine learning models** (graph neural networks, random forests) trained on existing superconductor databases (SuperCon, NIMS) to predict Tc and stability.
- **Crystal structure prediction** using USPEX and CALYPSO to identify metastable phases that may be quenchable to ambient conditions.

### Synthesis and Characterization

- **Diamond anvil cell (DAC)** synthesis at pressures up to 200 GPa with laser heating to 2000 K.
- **In situ** X-ray diffraction (XRD) and Raman spectroscopy to monitor phase formation.
- **Magnetic susceptibility** (SQUID) and electrical transport measurements to determine Tc and critical fields.
- **Recovery to ambient pressure** via slow decompression with polymer encapsulation to retain metastable phases.

### Manufacturing Scalability

- **Chemical doping** (e.g., partial substitution of H with S, Se, or C) to reduce required pressure.
- **Thin-film deposition** (pulsed laser deposition, sputtering) on lattice-matched substrates to stabilize high-pressure phases at ambient conditions.
- **High-pressure reactor design** for batch production of gram-scale samples using multi-anvil presses (up to 20 GPa) and rapid quenching.
- **Quality control** via automated Tc screening and XRD.

## Budget

| Category | Year 1 | Year 2 | Year 3 | Total |
|----------|--------|--------|--------|-------|
| Personnel (2 postdocs, 3 grad students, 1 technician) | $350,000 | $360,000 | $370,000 | $1,080,000 |
| Equipment (DACs, laser system, SQUID, PLD system) | $500,000 | $100,000 | $50,000 | $650,000 |
| Computing (HPC cluster time, cloud credits) | $100,000 | $100,000 | $100,000 | $300,000 |
| Materials (gases, metals, diamonds, substrates) | $50,000 | $60,000 | $70,000 | $180,000 |
| Travel and dissemination | $20,000 | $20,000 | $20,000 | $60,000 |
| Indirect costs (50% of direct) | $510,000 | $320,000 | $305,000 | $1,135,000 |
| **Total** | **$1,530,000** | **$960,000** | **$915,000** | **$3,405,000** |

## Timeline

- **Months 1–6**: Computational screening of binary and ternary hydrides; setup of DAC synthesis lab.
- **Months 7–12**: Synthesis and characterization of top 20 candidates; ML model refinement.
- **Months 13–18**: Identification of promising room-temperature candidates; begin doping studies.
- **Months 19–24**: Scale-up of best candidate to multi-anvil press; thin-film stabilization.
- **Months 25–30**: Pilot manufacturing line design and construction; patent filing.
- **Months 31–36**: Production of gram-scale samples; technology transfer and industry partnerships.

## References

1. Ashcroft, N. W. (2004). Hydrogen dominant metallic alloys: High temperature superconductors? *Physical Review Letters*, 92(18), 187002.
2. Drozdov, A. P., et al. (2015). Conventional superconductivity at 203 kelvin at high pressures in the sulfur hydride system. *Nature*, 525(7567), 73–76.
3. Somayazulu, M., et al. (2019). Evidence for superconductivity above 260 K in lanthanum superhydride at megabar pressures. *Physical Review Letters*, 122(2), 027001.
4. Peng, F., et al. (2017). Hydrogen clathrate structures in rare earth hydrides at high pressures: Possible route to room-temperature superconductivity. *Physical Review Letters*, 119(10), 107001.
5. Snider, E., et al. (2020). Room-temperature superconductivity in a carbonaceous sulfur hydride. *Nature*, 586(7829), 373–377.
6. Liu, H., et al. (2017). Potential high-Tc superconducting lanthanum and yttrium hydrides at high pressure. *Proceedings of the National Academy of Sciences*, 114(27), 6990–6995.
7. Miao, M. S., et al. (2020). High-temperature superconductivity in ternary hydrides. *Physical Review B*, 101(10), 104508.
8. Ward, L., et al. (2016). A machine learning approach for engineering bulk metallic glasses. *Acta Materialia*, 108, 1–9. (ML methodology adapted for superconductors).
