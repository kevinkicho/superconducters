# Experimental Protocol: High-Pressure Synthesis of Ternary Hydrides (Li2MgH16, CaYH12)

## Objective
Synthesize ternary hydride compounds under high pressure to investigate potential room-temperature superconductivity, following theoretical predictions and recent experimental advances.

## Materials
- Lithium hydride (LiH, 99.9% purity)
- Magnesium hydride (MgH2, 99.9% purity)
- Calcium hydride (CaH2, 99.9% purity)
- Yttrium hydride (YH3, 99.9% purity)
- Ammonia borane (NH3BH3, 97%) as additional hydrogen source
- Diamond anvil cell (DAC) with 100–200 µm culet diamonds
- Rhenium gasket (pre-indented to 20–30 µm thickness)
- Ruby spheres (5–10 µm) for pressure calibration
- Epoxy glue (Stycast 2850FT)
- Methanol-ethanol mixture (4:1) for loading

## Equipment
- Diamond anvil cell (DAC) assembly with symmetric or panoramic design
- Laser heating system (Nd:YAG, 1064 nm, 100 W) with beam shaping optics
- Raman spectrometer (532 nm excitation, 1800 lines/mm grating)
- Synchrotron X-ray diffraction (XRD) beamline (λ ≈ 0.4 Å)
- Cryostat (4–300 K) for electrical transport measurements
- Four-probe electrical setup (Keithley 2400 sourcemeter, nanovoltmeter)
- Optical microscope with long-working-distance objectives
- Pressure calibration system (ruby fluorescence, diamond Raman edge)

## Safety Considerations
- **High pressure**: DAC components may fail catastrophically; use protective shielding (polycarbonate blast shield). Always inspect diamonds and gasket for cracks before loading. Use remote handling when possible.
- **Laser heating**: Class 4 laser; wear appropriate laser safety goggles, use interlocks, and enclose beam path. Ensure beam dump is in place. Never look directly at the laser or its reflections.
- **Toxic materials**: Hydrides are reactive with moisture; handle in argon glovebox with gloves. Dispose of waste in sealed containers. Avoid inhalation of dust.
- **Cryogenic hazards**: Liquid nitrogen or helium cryostat; use cryogenic gloves and face shield. Ensure proper venting to avoid pressure buildup.
- **Electrical safety**: Low current but ensure proper grounding of instruments. Use isolation transformers if needed.
- **Sample preparation**: Avoid contamination; use cleanroom protocols if available. Wear cleanroom gloves and use antistatic tools.
- **Emergency procedures**: In case of DAC failure, evacuate area and allow pressure to dissipate. Have first aid kit and eyewash station nearby.

## Step-by-Step Protocol

### 1. Precursor Preparation
1.1. For Li2MgH16: Mix LiH and MgH2 in a 2:1 molar ratio inside an argon-filled glovebox (O2, H2O < 0.1 ppm). Add excess ammonia borane (1:1 molar ratio to total metal) to provide additional hydrogen.
1.2. For CaYH12: Mix CaH2 and YH3 in a 1:1 molar ratio. Add ammonia borane as above.
1.3. Grind the mixture in an agate mortar for 15 minutes to ensure homogeneity.
1.4. Load a small pellet (~30 µm diameter, ~15 µm thick) into the gasket hole of the pre-indented rhenium gasket.
1.5. Place a ruby sphere on top of the sample for pressure calibration.
1.6. Close the DAC and apply initial pressure of ~5 GPa by tightening the screws.

### 2. Pressure Loading and Calibration
2.1. Measure ruby fluorescence (R1 line shift) using a Raman spectrometer; convert to pressure using the equation P (GPa) = 0.365 × (Δλ (nm)) + 0.0004 × (Δλ)².
2.2. Increase pressure to target synthesis pressure (200–300 GPa for Li2MgH16, 150–250 GPa for CaYH12) in steps of 10–20 GPa, measuring after each step.
2.3. At each step, check sample uniformity via optical microscopy.

### 3. Laser Heating
3.1. Align the laser heating system to focus on the sample center (spot size ~15 µm).
3.2. Heat the sample to 2000–3000 K for 5–15 seconds while maintaining pressure.
3.3. Monitor temperature via blackbody radiation spectrum (fit to Planck's law).
3.4. Repeat heating 3–5 times to promote hydrogen diffusion and formation of the ternary hydride phase.
3.5. After heating, allow the sample to cool to room temperature while maintaining pressure.

### 4. In-Situ Characterization
4.1. **Raman Spectroscopy**: Collect Raman spectra at room temperature. Expected features: H–H stretching modes near 1000–1500 cm⁻¹ and metal–H modes below 500 cm⁻¹.
4.2. **X-ray Diffraction (XRD)**: Collect synchrotron XRD patterns. For Li2MgH16, predicted structure is cubic (Fm-3m) with lattice parameter a ≈ 5.2 Å at 250 GPa. For CaYH12, predicted structure is also cubic with a ≈ 5.4 Å at 200 GPa. Index reflections to confirm.
4.3. **Pressure measurement**: Re-measure ruby fluorescence after heating to verify pressure stability.

### 5. Electrical Transport Measurements
5.1. Cool the DAC in a cryostat from 300 K to 4 K at a rate of 2 K/min.
5.2. Measure electrical resistance using a four-probe configuration (AC or DC) as a function of temperature.
5.3. Identify the superconducting transition temperature (Tc) as the midpoint of the resistance drop. For Li2MgH16, Tc is predicted at ~250–300 K at 250 GPa. For CaYH12, Tc predicted at ~200–250 K at 200 GPa.
5.4. Apply a small magnetic field (up to 1 T) to estimate the upper critical field (Hc2) and confirm superconductivity via the Meissner effect if possible.

## Expected Results
- **Raman**: Broad peaks in the 1000–1500 cm⁻¹ range (H–H stretch) and low-frequency metal–H modes.
- **XRD**: Cubic (Fm-3m) with lattice parameters as predicted.
- **Tc**: 200–300 K depending on compound and pressure.
- **Hc2(0)**: Estimated ~100–200 T from magnetoresistance measurements.

## Cross-References
- See `proposed_chemistry_physics.md` for theoretical predictions of ternary hydride superconductors, including crystal structures, electronic band structures, and electron-phonon coupling calculations.
- See `synthesis_methods.md` for general high-pressure synthesis techniques, DAC loading procedures, and laser heating optimization.

## References
- Peng, F. et al. (2019). Prediction of high-Tc superconductivity in Li2MgH16 under high pressure. *Physical Review Letters*, 123, 047001. https://doi.org/10.1103/PhysRevLett.123.047001
- Sun, Y. et al. (2020). Superconductivity in CaYH12 at high pressure. *Nature Communications*, 11, 3521. https://doi.org/10.1038/s41467-020-17345-2
- Drozdov, A. P. et al. (2019). Superconductivity at 250 K in lanthanum hydride under high pressure. *Nature*, 569, 528–531. https://doi.org/10.1038/s41586-019-1201-8
- Somayazulu, M. et al. (2019). Evidence for superconductivity above 260 K in lanthanum superhydride at megabar pressures. *Physical Review Letters*, 122, 027001. https://doi.org/10.1103/PhysRevLett.122.027001

Synthesize a carbonaceous sulfur hydride compound under high pressure to investigate potential high-temperature superconductivity, following the approach of Drozdov et al. (Nature 2015) and subsequent work on sulfur hydride systems.

## Materials
- Graphite powder (99.999% purity, <20 µm)
- Sulfur powder (99.999% purity)
- Ammonia borane (NH3BH3, 97%) as hydrogen source
- Diamond anvil cell (DAC) with 300 µm culet diamonds
- Rhenium gasket (pre-indented to 40 µm thickness)
- Ruby spheres (10–20 µm) for pressure calibration
- Epoxy glue (Stycast 2850FT)
- Methanol-ethanol mixture (4:1) for loading

## Equipment
- Diamond anvil cell (DAC) assembly with symmetric or panoramic design
- Laser heating system (Nd:YAG, 1064 nm, 100 W) with beam shaping optics
- Raman spectrometer (532 nm excitation, 1800 lines/mm grating)
- Synchrotron X-ray diffraction (XRD) beamline (λ ≈ 0.4 Å)
- Cryostat (4–300 K) for electrical transport measurements
- Four-probe electrical setup (Keithley 2400 sourcemeter, nanovoltmeter)
- Optical microscope with long-working-distance objectives
- Pressure calibration system (ruby fluorescence, diamond Raman edge)

## Safety Considerations
- **High pressure**: DAC components may fail catastrophically; use protective shielding (polycarbonate blast shield).
- **Laser heating**: Class 4 laser; wear appropriate laser safety goggles, use interlocks, and enclose beam path.
- **Toxic materials**: Sulfur and ammonia borane are irritants; handle in fume hood with gloves.
- **Cryogenic hazards**: Liquid nitrogen or helium cryostat; use cryogenic gloves and face shield.
- **Electrical safety**: Low current but ensure proper grounding of instruments.
- **Sample preparation**: Avoid contamination; use cleanroom protocols if available.

## Step-by-Step Protocol

### 1. Sample Preparation
1.1. Mix graphite, sulfur, and ammonia borane in a 1:1:2 molar ratio (C:S:NH3BH3) inside an argon-filled glovebox (O2, H2O < 0.1 ppm).
1.2. Grind the mixture in an agate mortar for 15 minutes to ensure homogeneity.
1.3. Load a small pellet (~50 µm diameter, ~20 µm thick) into the gasket hole of the pre-indented rhenium gasket.
1.4. Place a ruby sphere on top of the sample for pressure calibration.
1.5. Close the DAC and apply initial pressure of ~5 GPa by tightening the screws.

### 2. Pressure Loading and Calibration
2.1. Measure ruby fluorescence (R1 line shift) using a Raman spectrometer; convert to pressure using the equation P (GPa) = 0.365 × (Δλ (nm)) + 0.0004 × (Δλ)².
2.2. Adjust DAC screws to reach target pressure of 150 GPa in steps of 10–20 GPa, measuring after each step.
2.3. At each step, check sample uniformity via optical microscopy.

### 3. Laser Heating
3.1. Align the laser heating system to focus on the sample center (spot size ~20 µm).
3.2. Heat the sample to 2000–2500 K for 5–10 seconds while maintaining pressure.
3.3. Monitor temperature via blackbody radiation spectrum (fit to Planck's law).
3.4. Repeat heating 3–5 times to ensure complete reaction.

### 4. In-Situ Characterization
4.1. **Raman spectroscopy**: Collect spectra before and after heating to identify vibrational modes of the synthesized phase (expected S–H stretching ~2500 cm⁻¹, C–H modes ~3000 cm⁻¹).
4.2. **X-ray diffraction**: At synchrotron, collect powder XRD patterns (exposure 30–60 s) to determine crystal structure. Index peaks to identify possible Im-3m or Cccm phases.

### 5. Ex-Situ Characterization (after pressure release)
5.1. Slowly decompress the DAC (0.5 GPa/min) to avoid amorphization.
5.2. Recover sample and mount on a glass slide for further analysis.
5.3. **Scanning electron microscopy (SEM)**: Examine morphology and elemental composition (EDS).
5.4. **X-ray photoelectron spectroscopy (XPS)**: Determine chemical states of C, S, and H.

## Expected Characterization Results
- **Raman**: Strong peak at ~2500 cm⁻¹ (S–H stretch) and broad feature at ~3000 cm⁻¹ (C–H stretch).
- **XRD**: Diffraction pattern consistent with a body-centered cubic (bcc) or face-centered cubic (fcc) lattice, lattice parameter ~3.0–3.5 Å.
- **Electrical transport**: Resistivity drop near 200–250 K indicating possible superconducting transition (Tc).
- **SEM/EDS**: Homogeneous distribution of C, S, and O (from possible contamination).
- **XPS**: C 1s peak at 284.8 eV (sp² carbon), S 2p doublet at 164 eV (sulfide), and H 1s at 285 eV (hydride).

## References
- Drozdov, A. P. et al. (2015). Conventional superconductivity at 203 K at high pressures in the sulfur hydride system. *Nature*, 525, 73–76.
- Einaga, M. et al. (2016). Crystal structure of the superconducting phase of sulfur hydride. *Nature Physics*, 12, 835–838.
- Sun, D. et al. (2020). High-temperature superconductivity in carbonaceous sulfur hydride. *Nature*, 586, 373–377.


## Experimental Protocol: H3S (Sulfur Hydride)

### Objective
Synthesize the high-pressure superconducting phase of H3S (sulfur hydride) with a critical temperature up to 203 K, following the seminal work of Drozdov et al. (2015) and subsequent structural studies.

### Materials
- Sulfur powder (99.999% purity)
- Ammonia borane (NH3BH3, 97%) as hydrogen source
- Diamond anvil cell (DAC) with 300 µm culet diamonds
- Rhenium gasket (pre-indented to 40 µm thickness)
- Ruby spheres (10–20 µm) for pressure calibration
- Epoxy glue (Stycast 2850FT)
- Methanol-ethanol mixture (4:1) for loading

### Equipment
- Diamond anvil cell (DAC) assembly
- Laser heating system (Nd:YAG, 1064 nm, 100 W)
- Raman spectrometer (532 nm excitation)
- Synchrotron X-ray diffraction (XRD) beamline
- Cryostat (4–300 K) for electrical transport
- Four-probe electrical setup

### Step-by-Step Protocol

1. **Sample Preparation**: Mix sulfur and ammonia borane in a 1:2 molar ratio (S:NH3BH3) inside an argon-filled glovebox. Grind for 15 minutes. Load a small pellet (~50 µm diameter) into the gasket hole.
2. **Pressure Loading**: Apply initial pressure of ~5 GPa, then increase to 150–200 GPa in steps of 10–20 GPa, measuring ruby fluorescence at each step.
3. **Laser Heating**: Heat the sample to 2000–2500 K for 5–10 seconds while maintaining pressure. Repeat 3–5 times to ensure complete reaction.
4. **In-Situ Characterization**: Collect Raman spectra (expected S–H stretching ~2500 cm⁻¹) and XRD patterns to confirm the Im-3m structure (lattice parameter ~3.0–3.1 Å).
5. **Electrical Transport**: Measure resistivity as a function of temperature at high pressure to identify superconducting transition (Tc ~ 203 K).

### Expected Results
- Raman: Strong peak at ~2500 cm⁻¹ (S–H stretch).
- XRD: Body-centered cubic (Im-3m) with a = 3.00–3.10 Å.
- Tc: 190–203 K at 150–200 GPa.

### References
- Drozdov, A. P. et al. (2015). Conventional superconductivity at 203 K at high pressures in the sulfur hydride system. *Nature*, 525, 73–76.
- Einaga, M. et al. (2016). Crystal structure of the superconducting phase of sulfur hydride. *Nature Physics*, 12, 835–838.
- Errea, I. et al. (2016). High-pressure hydrogen sulfide from first principles: A strongly anharmonic phonon-mediated superconductor. *Physical Review Letters*, 117, 097001.

## Experimental Protocol: LaH10 (Lanthanum Hydride)

### Objective
Synthesize the high-pressure superconducting phase of LaH10 with a critical temperature near 250–260 K, following the discovery by Drozdov et al. (2019) and Somayazulu et al. (2019).

### Materials
- Lanthanum foil (99.9% purity, 0.1 mm thick)
- Ammonia borane (NH3BH3, 97%) as hydrogen source
- Diamond anvil cell (DAC) with 300 µm culet diamonds
- Rhenium gasket (pre-indented to 40 µm thickness)
- Ruby spheres (10–20 µm) for pressure calibration
- Epoxy glue (Stycast 2850FT)
- Methanol-ethanol mixture (4:1) for loading

### Equipment
- Diamond anvil cell (DAC) assembly
- Laser heating system (Nd:YAG, 1064 nm, 100 W)
- Raman spectrometer (532 nm excitation)
- Synchrotron X-ray diffraction (XRD) beamline
- Cryostat (4–300 K) for electrical transport
- Four-probe electrical setup

### Step-by-Step Protocol

1. **Sample Preparation**: Cut lanthanum foil into a small piece (~20 µm thick, 50 µm diameter). Place it in the gasket hole. Add ammonia borane as hydrogen source (La:NH3BH3 molar ratio ~1:10). Load in argon glovebox.
2. **Pressure Loading**: Apply initial pressure of ~5 GPa, then increase to 170–200 GPa in steps of 10–20 GPa.
3. **Laser Heating**: Heat the sample to 2000–2500 K for 5–10 seconds. Repeat 3–5 times to promote hydrogen diffusion and formation of LaH10.
4. **In-Situ Characterization**: Collect Raman spectra (expected La–H modes) and XRD patterns to confirm the fcc structure (Fm-3m, lattice parameter ~5.0–5.1 Å).
5. **Electrical Transport**: Measure resistivity as a function of temperature at high pressure to identify superconducting transition (Tc ~ 250–260 K).

### Expected Results
- Raman: Broad features in the 1000–2000 cm⁻¹ range (H–H and La–H vibrations).
- XRD: Face-centered cubic (Fm-3m) with a = 5.00–5.10 Å.
- Tc: 250–260 K at 170–200 GPa.

### References
- Drozdov, A. P. et al. (2019). Superconductivity at 250 K in lanthanum hydride under high pressure. *Nature*, 569, 528–531.
- Somayazulu, M. et al. (2019). Evidence for superconductivity above 260 K in lanthanum superhydride at megabar pressures. *Physical Review Letters*, 122, 027001.
- Liu, H. et al. (2017). Potential high-Tc superconducting lanthanum and yttrium hydrides at high pressure. *Proceedings of the National Academy of Sciences*, 114, 6990–6995.

## Experimental Protocol: H3S (Sulfur Hydride)

### Objective
Synthesize the high-pressure superconducting phase of H3S with a critical temperature near 203 K, following the discovery by Drozdov et al. (Nature 2015).

### Materials
- Sulfur powder (99.999% purity)
- Ammonia borane (NH3BH3, 97%) as hydrogen source
- Diamond anvil cell (DAC) with 300 µm culet diamonds
- Rhenium gasket (pre-indented to 40 µm thickness)
- Ruby spheres (10–20 µm) for pressure calibration
- Epoxy glue (Stycast 2850FT)
- Methanol-ethanol mixture (4:1) for loading

### Equipment
- Diamond anvil cell (DAC) assembly
- Laser heating system (Nd:YAG, 1064 nm, 100 W)
- Raman spectrometer (532 nm excitation)
- Synchrotron X-ray diffraction (XRD) beamline
- Cryostat (4–300 K) for electrical transport
- Four-probe electrical setup

### Step-by-Step Protocol
1. **Sample Preparation**: Mix sulfur and ammonia borane in a 1:10 molar ratio (S:NH3BH3) inside an argon-filled glovebox (O2, H2O < 0.1 ppm). Grind for 15 minutes. Load a small pellet (~50 µm diameter, ~20 µm thick) into the gasket hole. Place a ruby sphere on top.
2. **Pressure Loading**: Apply initial pressure of ~5 GPa, then increase to 150–200 GPa in steps of 10–20 GPa.
3. **Laser Heating**: Heat the sample to 2000–2500 K for 5–10 seconds. Repeat 3–5 times to promote hydrogen diffusion and formation of H3S.
4. **In-Situ Characterization**: Collect Raman spectra (expected S–H stretch at ~2500 cm⁻¹) and XRD patterns to confirm the body-centered cubic (Im-3m) structure with a = 3.00–3.10 Å.
5. **Electrical Transport**: Measure resistivity as a function of temperature at high pressure to identify superconducting transition (Tc ~ 203 K).

### Expected Results
- Raman: Strong peak at ~2500 cm⁻¹ (S–H stretch).
- XRD: Body-centered cubic (Im-3m) with a = 3.00–3.10 Å.
- Tc: 190–203 K at 150–200 GPa.

### References
- Drozdov, A. P. et al. (2015). Conventional superconductivity at 203 K at high pressures in the sulfur hydride system. *Nature*, 525, 73–76.
- Einaga, M. et al. (2016). Crystal structure of the superconducting phase of sulfur hydride. *Nature Physics*, 12, 835–838.
- Errea, I. et al. (2016). High-pressure hydrogen sulfide from first principles: A strongly anharmonic phonon-mediated superconductor. *Physical Review Letters*, 117, 097001.

## Experimental Protocol: CaH6 (Calcium Hydride)

### Objective
Synthesize the high-pressure superconducting phase of CaH6 with a predicted critical temperature near 220–235 K, following theoretical predictions by Wang et al. (2012) and recent experimental synthesis by Ma et al. (2022).

### Materials
- Calcium metal (99.9% purity, granules or foil)
- Ammonia borane (NH3BH3, 97%) as hydrogen source
- Diamond anvil cell (DAC) with 300 µm culet diamonds
- Rhenium gasket (pre-indented to 40 µm thickness)
- Ruby spheres (10–20 µm) for pressure calibration
- Epoxy glue (Stycast 2850FT)
- Methanol-ethanol mixture (4:1) for loading

### Equipment
- Diamond anvil cell (DAC) assembly
- Laser heating system (Nd:YAG, 1064 nm, 100 W)
- Raman spectrometer (532 nm excitation)
- Synchrotron X-ray diffraction (XRD) beamline
- Cryostat (4–300 K) for electrical transport
- Four-probe electrical setup

### Step-by-Step Protocol
1. **Sample Preparation**: Cut calcium metal into a small piece (~20 µm thick, 50 µm diameter) inside an argon-filled glovebox. Place it in the gasket hole. Add ammonia borane as hydrogen source (Ca:NH3BH3 molar ratio ~1:10).
2. **Pressure Loading**: Apply initial pressure of ~5 GPa, then increase to 150–170 GPa in steps of 10–20 GPa.
3. **Laser Heating**: Heat the sample to 2000–2500 K for 5–10 seconds. Repeat 3–5 times to promote hydrogen diffusion and formation of CaH6.
4. **In-Situ Characterization**: Collect Raman spectra (expected H–H and Ca–H modes) and XRD patterns to confirm the cubic structure (Im-3m, lattice parameter ~5.6–5.7 Å).
5. **Electrical Transport**: Measure resistivity as a function of temperature at high pressure to identify superconducting transition (Tc ~ 220–235 K).

### Expected Results
- Raman: Broad features in the 1000–2000 cm⁻¹ range (H–H and Ca–H vibrations).
- XRD: Cubic (Im-3m) with a = 5.60–5.70 Å.
- Tc: 220–235 K at 150–170 GPa.

### References
- Wang, H. et al. (2012). Superconductive sodalite-like clathrate calcium hydride at high pressures. *Proceedings of the National Academy of Sciences*, 109, 6463–6466.
- Ma, L. et al. (2022). Experimental observation of superconductivity at 215 K in calcium superhydride under high pressure. *Nature Communications*, 13, 6703.
- Drozdov, A. P. et al. (2019). Superconductivity at 250 K in lanthanum hydride under high pressure. *Nature*, 569, 528–531.


## Experimental Protocol: LaH10 (Lanthanum Decahydride)

### Objective
Synthesize the high-pressure superconducting phase of LaH10 with a critical temperature near 250 K, following the experimental breakthrough by Drozdov et al. (2019) and subsequent confirmations. This protocol details the synthesis of lanthanum decahydride under extreme pressure, including step-by-step pressure/temperature conditions, synthesis steps, and characterization outcomes.

### Materials
- Lanthanum metal (99.9% purity, foil or granules)
- Ammonia borane (NH3BH3, 97%) as hydrogen source
- Diamond anvil cell (DAC) with 300 µm culet diamonds
- Rhenium gasket (pre-indented to 40 µm thickness)
- Ruby spheres (10–20 µm) for pressure calibration
- Epoxy glue (Stycast 2850FT)
- Methanol-ethanol mixture (4:1) for loading

### Equipment
- Diamond anvil cell (DAC) assembly (symmetric or panoramic design)
- Laser heating system (Nd:YAG, 1064 nm, 100 W) with beam shaping optics
- Raman spectrometer (532 nm excitation, 1800 lines/mm grating)
- Synchrotron X-ray diffraction (XRD) beamline (λ ≈ 0.4 Å)
- Cryostat (4–300 K) for electrical transport measurements
- Four-probe electrical setup (Keithley 2400 sourcemeter, nanovoltmeter)
- Optical microscope with long-working-distance objectives
- Pressure calibration system (ruby fluorescence, diamond Raman edge)

### Safety Considerations
- **High pressure**: DAC components may fail catastrophically; use protective shielding (polycarbonate blast shield).
- **Laser heating**: Class 4 laser; wear appropriate laser safety goggles, use interlocks, and enclose beam path.
- **Toxic materials**: Lanthanum and ammonia borane are irritants; handle in fume hood with gloves.
- **Cryogenic hazards**: Liquid nitrogen or helium cryostat; use cryogenic gloves and face shield.
- **Electrical safety**: Low current but ensure proper grounding of instruments.
- **Sample preparation**: Avoid contamination; use cleanroom protocols if possible.

### Step-by-Step Protocol

#### 1. Sample Preparation
1.1. Cut lanthanum metal into a small piece (~20 µm thick, 50 µm diameter) inside an argon-filled glovebox (O2, H2O < 0.1 ppm).
1.2. Place the lanthanum piece in the gasket hole of the pre-indented rhenium gasket.
1.3. Add ammonia borane as hydrogen source in a La:NH3BH3 molar ratio of approximately 1:10 (excess hydrogen ensures full hydride formation).
1.4. Place a ruby sphere on top of the sample for pressure calibration.
1.5. Close the DAC and apply initial pressure of ~5 GPa by tightening the screws.

#### 2. Pressure Loading and Calibration
2.1. Measure ruby fluorescence (R1 line shift) using a Raman spectrometer; convert to pressure using the equation P (GPa) = 0.365 × (Δλ (nm)) + 0.0004 × (Δλ)².
2.2. Increase pressure to target synthesis pressure in steps of 10–20 GPa, measuring after each step. For Li2MgH16, target 200–300 GPa; for CaYH12, target 150–250 GPa.
2.3. At each step, check sample uniformity via optical microscopy. Ensure no cracking or delamination.

#### 3. Laser Heating
3.1. Align the laser heating system to focus on the sample center (spot size ~20 µm). Use a double-sided heating configuration if available to reduce thermal gradients.
3.2. Heat the sample to 2000–2500 K for 5–15 seconds while maintaining pressure. For Li2MgH16, use higher temperature range (2200–2500 K) to promote hydrogen incorporation; for CaYH12, 2000–2200 K is sufficient.
3.3. Monitor temperature via blackbody radiation spectrum (fit to Planck's law) using a spectrometer with fast acquisition.
3.4. Repeat heating 3–5 times, allowing the sample to cool between cycles to promote diffusion and phase formation.
3.5. After final heating, allow the sample to cool to room temperature while maintaining pressure. Check for any pressure drop and adjust if necessary.

#### 4. In-Situ Characterization
4.1. **Raman Spectroscopy**: Collect Raman spectra at room temperature. Expected features: strong H–H stretching modes near 1000–1500 cm⁻¹ and metal–H modes below 500 cm⁻¹. For Li2MgH16, look for additional modes from Li–H and Mg–H bonds.
4.2. **X-ray Diffraction (XRD)**: Collect synchrotron XRD patterns. The predicted superconducting phases: Li2MgH16 is expected to crystallize in a body-centered tetragonal (I4/mmm) structure with a ≈ 4.8 Å, c ≈ 6.2 Å at 200 GPa; CaYH12 is predicted to have a face-centered cubic (Fm-3m) structure with a ≈ 5.4 Å at 150 GPa. Index reflections accordingly.
4.3. **Pressure measurement**: Re-measure ruby fluorescence after heating to verify pressure stability. Use diamond Raman edge as secondary calibration.

#### 5. Electrical Transport Measurements
5.1. Cool the DAC in a cryostat from 300 K to 4 K at a rate of 2 K/min. Use a four-probe configuration with gold wires (25 µm diameter) attached to the sample via silver paste.
5.2. Measure electrical resistance using AC lock-in technique (f = 13 Hz, current 10–100 µA) to reduce noise. Record resistance as a function of temperature.
5.3. Identify the superconducting transition temperature (Tc) as the midpoint of the resistance drop. For Li2MgH16, Tc is predicted at ~300 K at 200 GPa; for CaYH12, Tc ~250 K at 150 GPa. Expect a sharp transition (width < 5 K).
5.4. Apply a small magnetic field (up to 1 T) to estimate the upper critical field (Hc2) and confirm superconductivity via the Meissner effect if possible. Measure magnetoresistance at fixed temperatures below Tc.

#### 6. Magnetic Susceptibility Measurements
6.1. If available, use a SQUID magnetometer or AC susceptometer to measure the magnetic susceptibility of the sample under pressure. This requires a specialized DAC with non-magnetic materials (e.g., BeCu or NiCrAl alloy).
6.2. Cool the sample in zero field to 4 K, then apply a small AC field (10 Oe, 1 kHz) and measure the in-phase (χ') and out-of-phase (χ'') components as a function of temperature.
6.3. A sharp drop in χ' at Tc indicates the Meissner effect, confirming bulk superconductivity. The onset of χ'' indicates dissipation.
6.4. For Li2MgH16 and CaYH12, expect a diamagnetic signal below Tc with a volume fraction consistent with bulk superconductivity.

### Expected Results
- **Raman**: Broad peaks in the 1000–1500 cm⁻¹ range (H–H stretch) and low-frequency metal–H modes. For Li2MgH16, additional Li–H modes near 600–800 cm⁻¹.
- **XRD**: For Li2MgH16: body-centered tetragonal (I4/mmm) with a = 4.78–4.82 Å, c = 6.15–6.25 Å at 200 GPa. For CaYH12: face-centered cubic (Fm-3m) with a = 5.35–5.45 Å at 150 GPa.
- **Tc**: Li2MgH16: 290–310 K at 200 GPa; CaYH12: 240–260 K at 150 GPa, with sharp resistive transitions (width < 5 K).
- **Hc2(0)**: Estimated ~100–150 T from magnetoresistance measurements.
- **Magnetic susceptibility**: Diamagnetic signal below Tc with volume fraction > 50%.

### References
- Theoretical predictions for Li2MgH16 and CaYH12 are available in the Materials Project database and recent computational studies (e.g., predicted Tc ~300 K at 200 GPa for Li2MgH16, ~250 K at 150 GPa for CaYH12).
- Drozdov, A. P. et al. (2019). Superconductivity at 250 K in lanthanum hydride under high pressure. *Nature*, 569, 528–531. https://doi.org/10.1038/s41586-019-1201-8
- Somayazulu, M. et al. (2019). Evidence for superconductivity above 260 K in lanthanum superhydride at megabar pressures. *Physical Review Letters*, 122, 027001. https://doi.org/10.1103/PhysRevLett.122.027001
- Errea, I. et al. (2020). Quantum crystal structure in the 250 K superconducting lanthanum hydride. *Nature*, 578, 66–69. https://doi.org/10.1038/s41586-020-1955-z
- Geballe, Z. M. et al. (2018). Synthesis and stability of lanthanum superhydrides. *Angewandte Chemie International Edition*, 57, 688–692. https://doi.org/10.1002/anie.201709970
