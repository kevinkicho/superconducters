# Experimental Protocol for LaH10 (Lanthanum Decahydride)

## Overview
This protocol details the synthesis and characterization of LaH10, a near-room-temperature superconductor with a critical temperature (Tc) of ~250–260 K at pressures of 150–170 GPa. The compound is a clathrate-like superhydride with a cubic structure (space group Fm-3m) and strong electron-phonon coupling. The procedure follows established methods from Drozdov et al. (2019) and Somayazulu et al. (2019).

## 1. Precursor Preparation
### Materials
- Lanthanum metal (99.9% purity, foil or powder, ~10–20 µm thickness)
- Ammonia borane (NH3BH3, 97% purity) as hydrogen source
- Diamond anvil cells (DAC) with 200–300 µm culet diamonds
- Rhenium gasket (pre-indented to ~30 µm thickness, hole diameter ~100 µm)
- Insulating layers: cubic boron nitride (cBN) or Al2O3 powder for electrical leads
- Electrical leads: platinum or gold foil (2–5 µm thick)
- Ruby spheres (for pressure calibration via fluorescence)

### Preparation Steps
1. **Lanthanum sample**: Cut a small piece of La foil (~20×20×10 µm) and clean with dilute HCl (0.1 M) for 10 s, rinse with ethanol, and dry in argon flow. Store in an argon-filled glovebox (O2 < 0.1 ppm, H2O < 0.1 ppm) to prevent oxidation.
2. **Hydrogen source**: Load NH3BH3 into a separate compartment of the DAC (or mix with La in a 1:10 molar ratio). NH3BH3 decomposes upon laser heating to release hydrogen.
3. **Gasket preparation**: Pre-indent rhenium gasket to ~30 µm thickness, drill a 100 µm hole, and fill with insulating cBN powder (compacted).
4. **Assembly**: Place La sample in the gasket hole, add NH3BH3 (if separate), and place ruby spheres for pressure calibration. Close DAC and apply initial pressure of ~5 GPa to seal.

## 2. High-Pressure Synthesis
### Equipment
- Diamond anvil cell (DAC) with membrane or screw-driven pressure control
- Continuous-wave or pulsed laser (1064 nm Nd:YAG, 50–100 W) for heating
- Raman spectrometer (for in situ monitoring of hydrogenation)
- Synchrotron X-ray source (for angle-dispersive X-ray diffraction, XRD)

### Procedure
1. **Pressure increase**: Gradually increase pressure to 150–170 GPa at room temperature. Monitor pressure via ruby fluorescence (R1 line shift, using the Mao-Bell scale).
2. **Laser heating**: Focus laser to a spot size of ~10–20 µm on the sample. Heat to 1500–2000 K for 10–30 s. Repeat heating cycles (3–5 times) to ensure complete reaction. The NH3BH3 decomposes, releasing hydrogen that reacts with La to form LaH10.
3. **Annealing**: After each heating cycle, allow the sample to cool to room temperature while maintaining pressure. Monitor Raman spectra for characteristic H–H stretching modes (~4000 cm⁻¹) and La–H modes (~1000–1200 cm⁻¹).
4. **Confirmation**: Perform in situ XRD to identify the cubic LaH10 phase (lattice parameter ~5.0 Å at 150 GPa). The appearance of (111), (200), (220), (311) reflections confirms the clathrate structure.

## 3. Characterization
### Structural Analysis
- **X-ray diffraction (XRD)**: Use synchrotron radiation (λ ~0.4 Å) with a MAR345 image plate or Pilatus detector. Index reflections to the Fm-3m space group. Refine lattice parameters using GSAS or DIOPTAS.
- **Raman spectroscopy**: Excitation wavelength 532 nm, power <10 mW to avoid laser heating. Look for H–H stretching modes (3500–4200 cm⁻¹) and low-frequency lattice modes. The absence of NH3BH3 peaks indicates complete decomposition.

### Electrical Transport
- **Four-probe resistance measurement**: Attach Pt or Au leads to the sample in a van der Pauw or linear geometry. Use a Keithley 2400 sourcemeter and a nanovoltmeter (e.g., Keithley 2182A). Measure resistance as a function of temperature (4–300 K) at fixed pressure.
- **Critical temperature (Tc)**: Define Tc as the temperature where resistance drops to 50% of the normal-state value (R50). The onset of superconductivity is marked by a sharp drop to zero resistance. Typical Tc for LaH10 is 250–260 K at 150–170 GPa.
- **Magnetic susceptibility**: Use a SQUID magnetometer (e.g., MPMS) with a diamond anvil cell insert. Measure DC magnetization (ZFC and FC) at 10 Oe to confirm Meissner effect. Diamagnetic shielding fraction >50% indicates bulk superconductivity.

### Additional Measurements
- **Pressure dependence**: Vary pressure from 100 to 200 GPa in steps of 10 GPa. Record Tc at each pressure to map the Tc(P) phase diagram. LaH10 is stable above ~130 GPa; Tc increases with pressure up to ~170 GPa then decreases.
- **Isotope effect**: Replace H with D (using ND3BD3) to confirm phonon-mediated pairing. The shift in Tc (ΔTc ~ 10–15 K) verifies the isotope effect.

## 4. Measurement Protocols
### Temperature Control
- Use a closed-cycle cryostat (e.g., Janis CCS-350) or a helium-flow cryostat for temperatures 4–300 K.
- For high-temperature measurements (above 300 K), use a resistive heater integrated into the DAC.
- Temperature measured with a Cernox thermometer (Lakeshore) attached to the diamond anvil.

### Data Acquisition
- **Resistance vs. temperature**: Sweep temperature at 1 K/min. Record resistance every 0.5 K. Apply a constant current of 10–100 µA (ensure linear I-V regime).
- **Pressure calibration**: Measure ruby fluorescence before and after each temperature sweep. Pressure drift should be <1 GPa.
- **XRD at high pressure**: Collect diffraction patterns at each pressure step (exposure time 30–60 s). Use CeO2 or Si standard for detector calibration.

## 5. Safety Considerations
- High-pressure DACs can fail catastrophically. Use protective shielding (polycarbonate or steel) around the DAC.
- Laser heating requires Class 4 laser safety: wear appropriate goggles, use beam blocks, and interlock systems.
- Ammonia borane is toxic and flammable; handle in a fume hood or glovebox.
- Lanthanum metal is pyrophoric in fine powder; store under inert atmosphere.

## 6. References
- Drozdov, A. P. et al. (2019). Superconductivity at 250 K in lanthanum hydride under high pressure. *Nature*, 569, 528–531. https://doi.org/10.1038/s41586-019-1201-8
- Somayazulu, M. et al. (2019). Evidence for superconductivity above 260 K in lanthanum superhydride at megabar pressures. *Physical Review Letters*, 122, 027001. https://doi.org/10.1103/PhysRevLett.122.027001
- Errea, I. et al. (2020). Quantum crystal structure in the 250 K superconducting lanthanum hydride. *Nature*, 578, 66–69. https://doi.org/10.1038/s41586-020-1955-z
- Geballe, Z. M. et al. (2018). Synthesis and stability of lanthanum superhydrides. *Angewandte Chemie International Edition*, 57, 688–692. https://doi.org/10.1002/anie.201709970

## 7. Experimental Validation Plan for LaH10 (Top Candidate)

### Required Equipment
- Diamond anvil cell (DAC) with 200–300 µm culet diamonds (e.g., from Almax easyLab or Diacell)
- Continuous-wave Nd:YAG laser (1064 nm, 50–100 W) for laser heating
- Raman spectrometer (e.g., Horiba LabRAM HR Evolution) with 532 nm and 633 nm excitation
- Synchrotron X-ray source (e.g., APS 13-ID-D, ESRF ID27) for angle-dispersive XRD
- Four-probe electrical measurement setup: Keithley 2400 sourcemeter, Keithley 2182A nanovoltmeter
- Closed-cycle cryostat (e.g., Janis CCS-350) or helium-flow cryostat (4–300 K)
- SQUID magnetometer (e.g., Quantum Design MPMS) with DAC insert
- Ruby fluorescence pressure calibration system (e.g., Ocean Optics HR4000 spectrometer)
- Optical microscope with long-working-distance objectives
- Glovebox (O2 < 0.1 ppm, H2O < 0.1 ppm) for sample handling
- Fume hood for chemical preparation

### Materials and Purity
- Lanthanum metal: 99.9% purity (REacton or Alfa Aesar), foil or powder, 10–20 µm thickness
- Ammonia borane (NH3BH3): 97% purity (Sigma-Aldrich), stored under inert atmosphere
- Rhenium gasket: 99.97% purity, pre-indented to ~30 µm
- Insulating powder: cubic boron nitride (cBN) or Al2O3 (99.5% purity)
- Electrical leads: platinum or gold foil (2–5 µm thick, 99.99% purity)
- Ruby spheres: ~5 µm diameter, Cr-doped Al2O3
- Dilute HCl (0.1 M), ethanol (99.9%), argon gas (99.999%)
- For isotope effect: ND3BD3 (deuterated ammonia borane, 98% D enrichment)

### Safety Protocols
- **High-pressure safety**: DACs can fail explosively. Use polycarbonate or steel shielding around the DAC. Never exceed rated pressure of diamond anvils. Inspect diamonds for cracks before each run.
- **Laser safety**: Class 4 laser operation requires dedicated interlocked enclosure, laser safety goggles (OD >5 at 1064 nm), and beam blocks. Only trained personnel operate the laser.
- **Chemical hazards**: Ammonia borane is toxic and flammable; handle in fume hood or glovebox. Lanthanum powder is pyrophoric; store under inert gas. Dispose of chemical waste according to institutional guidelines.
- **Cryogen safety**: Liquid helium and nitrogen handling requires cryogenic gloves and face shield. Ensure proper ventilation to avoid asphyxiation.
- **Electrical safety**: Use grounded equipment and current-limiting resistors. Avoid contact with high-current leads.

### Step-by-Step Synthesis and Characterization Procedure
1. **Precursor loading** (Day 1): Clean La foil, load into DAC with NH3BH3 and ruby spheres. Apply 5 GPa initial pressure.
2. **Pressure ramp** (Day 2): Increase pressure to 150 GPa at 0.5 GPa/min. Monitor ruby fluorescence every 10 GPa.
3. **Laser heating** (Day 3): Heat sample to 1800 K for 20 s, repeat 4 times. Monitor Raman for H–H modes.
4. **XRD confirmation** (Day 4): Collect diffraction pattern at 150 GPa. Index to Fm-3m, lattice parameter ~5.0 Å.
5. **Electrical transport** (Days 5–7): Attach Pt leads, measure R(T) from 300 K to 4 K at 1 K/min. Identify Tc (R50).
6. **Magnetic susceptibility** (Day 8): Measure ZFC/FC magnetization at 10 Oe from 300 K to 4 K. Confirm Meissner effect.
7. **Pressure dependence** (Days 9–12): Vary pressure 100–200 GPa in 10 GPa steps. Record Tc at each step.
8. **Isotope effect** (Days 13–15): Repeat with ND3BD3. Measure ΔTc.
9. **Data analysis** (Days 16–20): Refine lattice parameters, fit Tc(P) curve, compute electron-phonon coupling λ.

### Expected Outcomes
- Successful synthesis of LaH10 with cubic clathrate structure (Fm-3m) at 150–170 GPa.
- Tc of 250–260 K confirmed by resistance drop to zero and diamagnetic shielding fraction >50%.
- Pressure dependence: Tc increases with pressure up to ~170 GPa then decreases, consistent with literature.
- Isotope shift ΔTc ~10–15 K, confirming phonon-mediated pairing.
- Raman spectra show characteristic H–H stretching modes (~4000 cm⁻¹) and absence of NH3BH3 peaks.

### Contingency Steps
- **If LaH10 not formed**: Check pressure calibration; increase laser heating temperature to 2000 K or add more NH3BH3. Try longer heating cycles (30 s).
- **If Tc lower than expected**: Verify sample purity; check for oxygen contamination. Consider using higher-purity La (99.99%).
- **If DAC fails**: Replace diamonds and gasket. Use larger culet (300 µm) for lower pressure gradient.
- **If electrical contacts fail**: Reattach leads with silver epoxy. Use van der Pauw geometry if linear geometry fails.
- **If XRD pattern ambiguous**: Collect longer exposure (120 s) or use smaller beam size. Compare with simulated pattern from known LaH10 structure.
- **If no isotope shift observed**: Verify deuteration level of ND3BD3 via mass spectrometry. Increase D enrichment to >99%.

### Estimated Timeline (6 Months)
| Phase | Duration | Milestones |
|-------|----------|------------|
| Equipment setup and calibration | 1 month | DAC assembly, laser alignment, cryostat commissioning |
| Precursor preparation and initial synthesis | 1 month | First successful LaH10 synthesis confirmed by XRD |
| Electrical transport and magnetic measurements | 1.5 months | Tc determination, Meissner effect, pressure dependence |
| Isotope effect and additional characterization | 1 month | ΔTc measurement, Raman mapping |
| Data analysis and manuscript preparation | 1.5 months | Final Tc(P) curve, electron-phonon coupling, publication draft |

### Budget Estimate
| Item | Estimated Cost (USD) |
|------|---------------------|
| Diamond anvil cells (2 sets) | $20,000 |
| Laser system (Nd:YAG, 100 W) | $50,000 |
| Raman spectrometer | $80,000 |
| Cryostat (closed-cycle) | $40,000 |
| SQUID magnetometer (shared facility access) | $15,000 (6 months) |
| Synchrotron beamtime (3 days) | $10,000 |
| Chemicals and consumables (La, NH3BH3, gaskets, etc.) | $5,000 |
| Glovebox and fume hood (if not available) | $30,000 |
| Miscellaneous (tools, software licenses, shipping) | $5,000 |
| Personnel (1 postdoc, 1 graduate student, 6 months) | $60,000 |
| **Total** | **$315,000** |

*Note: Costs assume shared facility access for synchrotron and SQUID. If dedicated equipment is purchased, total may exceed $500,000.*
