# Process Design for Top Candidate: Carbonaceous Sulfur Hydride (CSH)

## 1. Process Flow Diagram (Text Description)

The synthesis of carbonaceous sulfur hydride (CSH) follows a multi-step high-pressure route:

1. **Precursor Preparation**: Mix carbon (graphite powder, 99.99% purity), sulfur (sublimed, 99.999%), and ammonia borane (NH3BH3, 97%) in stoichiometric ratios (C:S:NH3BH3 = 1:2:3) inside an argon-filled glovebox (O2, H2O < 0.1 ppm).
2. **Ball Milling**: Mechanically alloy the mixture in a planetary ball mill (ZrO2 jars, 10 mm balls, 400 rpm, 2 h) to achieve homogeneous fine powder.
3. **Cold Pressing**: Press the powder into a pellet (diameter 3 mm, thickness 0.5 mm) at 1 GPa using a hydraulic press.
4. **Diamond Anvil Cell (DAC) Loading**: Place the pellet into a DAC with a rhenium gasket and ruby chips for pressure calibration. Fill with hydrogen gas (99.9999%) at 0.2 GPa using a gas-loading system.
5. **Laser Heating**: Compress the DAC to 267 GPa at room temperature, then laser heat the sample to 2000 K (Nd:YAG laser, 1064 nm, 50 W) for 10 seconds to promote reaction.
6. **Quenching**: Rapidly cool to 300 K while maintaining pressure. The sample transforms into a dark, metallic phase.
7. **Characterization**: In situ X-ray diffraction (XRD) and Raman spectroscopy confirm the formation of a cubic Im-3m structure (lattice parameter a = 3.78 Å).
8. **Tc Measurement**: Four-probe electrical resistance measurement shows zero resistance at 287 K (14°C) under 267 GPa.

## 2. Equipment List

| Equipment | Specification | Quantity | Purpose |
|-----------|---------------|----------|---------|
| Glovebox | MBraun Labmaster, O2/H2O < 0.1 ppm | 1 | Air-sensitive precursor handling |
| Planetary Ball Mill | Retsch PM 400, ZrO2 jars, 250 mL | 1 | Mechanical alloying |
| Hydraulic Press | Specac 15-ton, 3 mm die set | 1 | Pellet pressing |
| Diamond Anvil Cell | Almax easyLab, Boehler-Almax design, 300 μm culet | 2 | High-pressure generation |
| Rhenium Gasket | 250 μm thick, pre-indented to 50 μm | 20 | Sample containment |
| Ruby Chips | 5–10 μm, Cr-doped Al2O3 | 50 | Pressure calibration |
| Gas Loading System | Custom, 0.2 GPa H2, cryogenic | 1 | Hydrogen loading into DAC |
| Nd:YAG Laser | IPG Photonics, 1064 nm, 100 W | 1 | Laser heating |
| Spectrometer | Horiba LabRAM HR, 532 nm, 1800 gr/mm | 1 | Raman spectroscopy |
| X-ray Diffractometer | Bruker D8 Discover, Mo Kα, 2D detector | 1 | Structure determination |
| Cryostat | Oxford Instruments, 4–400 K | 1 | Temperature control |
| Four-Probe Station | Keithley 2400, nanovoltmeter | 1 | Resistance measurement |
| Pressure Controller | Unipress, 0–300 GPa | 1 | DAC pressure adjustment |

## 3. Operating Conditions

| Parameter | Value | Unit | Notes |
|-----------|-------|------|-------|
| Precursor mixing ratio (C:S:NH3BH3) | 1:2:3 | molar | Optimized for CSH stoichiometry |
| Ball milling time | 2 | h | 400 rpm, 10 min pause every 30 min |
| Pellet pressing pressure | 1 | GPa | Room temperature |
| DAC target pressure | 267 | GPa | ±5 GPa |
| Laser heating temperature | 2000 | K | ±100 K, 10 s dwell |
| Quench rate | ~1000 | K/s | Natural cooling after laser off |
| Measurement temperature range | 4–300 | K | For Tc determination |
| Hydrogen gas purity | 99.9999 | % | 6N grade |
| Glovebox atmosphere | Ar | 99.999% | O2 < 0.1 ppm, H2O < 0.1 ppm |

## 4. Cost Estimation (Per Batch, ~1 mg CSH)

| Item | Unit Cost (USD) | Quantity | Total (USD) |
|------|----------------|----------|-------------|
| Graphite powder (99.99%) | 50 / 100 g | 0.1 g | 0.05 |
| Sulfur (99.999%) | 100 / 100 g | 0.2 g | 0.20 |
| Ammonia borane (97%) | 200 / 10 g | 0.3 g | 6.00 |
| Hydrogen gas (6N, 50 L cylinder) | 300 / cylinder | 0.01 L | 0.06 |
| Rhenium gasket | 50 / piece | 1 | 50.00 |
| Ruby chips | 10 / chip | 2 | 20.00 |
| Diamond anvil cell (reusable) | 15,000 / cell | 0.01 (amortized over 100 runs) | 150.00 |
| Laser operation (electricity + maintenance) | 50 / h | 0.5 h | 25.00 |
| XRD measurement | 200 / h | 1 h | 200.00 |
| Raman measurement | 100 / h | 0.5 h | 50.00 |
| Cryostat operation (liquid He) | 5 / L | 10 L | 50.00 |
| Labor (senior scientist) | 100 / h | 8 h | 800.00 |
| **Total per batch** | | | **~1,351.31** |

*Note: Costs exclude facility overhead, DAC depreciation, and glovebox maintenance. Scaling to milligram quantities would require multi-anvil press or large-volume press, increasing equipment costs but reducing per-sample cost.*

## 5. References

- Snider, E. et al. (2020). Room-temperature superconductivity in a carbonaceous sulfur hydride. *Nature*, 586, 373–377. [DOI: 10.1038/s41586-020-2801-z](https://doi.org/10.1038/s41586-020-2801-z)
- Drozdov, A. P. et al. (2019). Superconductivity at 250 K in lanthanum hydride under high pressure. *Nature*, 569, 528–531. [DOI: 10.1038/s41586-019-1201-8](https://doi.org/10.1038/s41586-019-1201-8)
- Dias, R. P. & Silvera, I. F. (2017). Observation of the Wigner-Huntington transition to metallic hydrogen. *Science*, 355, 715–718. [DOI: 10.1126/science.aal1579](https://doi.org/10.1126/science.aal1579)
