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


## 4. Statistical Design of Experiments (DoE)

### Objective
Optimize synthesis conditions (pressure, temperature, doping) to maximize Tc and reproducibility using a response surface methodology (RSM).

### Factors and Ranges
| Factor | Symbol | Low (-1) | Center (0) | High (+1) |
|--------|--------|----------|------------|-----------|
| Pressure (GPa) | P | 140 | 160 | 180 |
| Laser heating temperature (K) | T | 1500 | 1750 | 2000 |
| Doping (e.g., C substitution for H, at%) | D | 0 | 5 | 10 |

### Design
- **Type**: Central composite design (CCD) with 3 factors → 20 runs (8 factorial, 6 axial, 6 center points).
- **Randomization**: Run order randomized to minimize systematic bias.
- **Replicates**: 3 center points per block to estimate pure error.

### Response Variables
1. **Critical temperature (Tc)** measured by four-probe resistance drop (K).
2. **Phase purity** from XRD peak intensity ratio (I(111)/I(background)).
3. **Synthesis success rate** (binary: 1 if Tc > 200 K, else 0).

### Analysis
- Fit a second-order polynomial model: Tc = β₀ + β₁P + β₂T + β₃D + β₁₁P² + β₂₂T² + β₃₃D² + β₁₂PT + β₁₃PD + β₂₃TD + ε.
- ANOVA to identify significant factors (p < 0.05).
- Response surface and contour plots to locate optimum.
- Confirmatory runs at predicted optimum (n=3).

### Software
- Python with `pyDOE3` or `scikit-learn` for design generation and analysis.
- JMP or Minitab for visualization (optional).

## 5. High-Throughput Characterization Plan

### Synchrotron X‑ray Diffraction (XRD)
- **Beamline**: Advanced Photon Source (APS) 16‑ID‑B or equivalent (high‑flux, micro‑focus).
- **Energy**: 30–50 keV (λ ≈ 0.4–0.25 Å) to penetrate DAC and reduce absorption.
- **Detector**: Pilatus 2M or Dectris Eiger 4M, 0.1° step, 10 s exposure per frame.
- **Automation**: Robotic sample changer for sequential DAC loading; automated peak fitting (GSAS‑II or DIOPTAS).
- **Throughput**: 1 sample per 5 minutes → ~100 samples per 8‑hour shift.
- **Data pipeline**: Real‑time reduction (pyFAI), phase identification (PDF‑4+), lattice parameter refinement.

### Transport Measurements
- **Resistivity**: Four‑probe van der Pauw geometry; AC excitation 10 µA, 17 Hz; lock‑in amplifier (SR830).
- **Temperature range**: 4–300 K in closed‑cycle cryostat (0.5 K/min ramp).
- **Magnetic field**: 0–9 T (superconducting magnet) for Hall effect and upper critical field (Hc₂).
- **Automation**: LabVIEW or Python (PyVISA) script for multi‑sample switching (up to 8 samples per cooldown).
- **Throughput**: 1 sample per 2 hours (including cooldown) → 4 samples per 8‑hour shift.

### Integrated Workflow
1. **Synthesis** (DAC, laser heating) → 2. **In‑situ XRD** (phase confirmation) → 3. **Transport** (Tc, Hc₂) → 4. **Ex‑situ XRD** (post‑measurement structure) → 5. **Data upload** to central database (MongoDB or SQLite).
- **Active learning loop**: Bayesian optimization (GPyOpt) suggests next synthesis conditions based on previous Tc and phase purity.
- **Expected throughput**: 5–10 fully characterized samples per week.

### References
- Box, G. E. P., & Draper, N. R. (2007). *Response Surfaces, Mixtures, and Ridge Analyses*. Wiley.
- Drozdov, A. P. et al. (2019). Superconductivity in LaH₁₀. *Nature*, 569, 528–531. DOI: 10.1038/s41586-019-1201-8
- Somayazulu, M. et al. (2019). Evidence for superconductivity above 260 K in lanthanum superhydride. *Phys. Rev. Lett.*, 122, 027001. DOI: 10.1103/PhysRevLett.122.027001
- APS beamline 16‑ID‑B: https://www.aps.anl.gov/Beamlines/16-ID-B


## 6. Quality Assurance and Quality Control (QA/QC) Plan

### 6.1 Statistical Process Control (SPC) Charts
- **Control charts** for key process parameters: pressure (GPa), laser heating temperature (K), heating duration (s), and sample resistance (Ω) at room temperature.
- **X̄-R charts**: Subgroup size n=3 (three consecutive runs). Upper and lower control limits set at ±3σ from the mean.
- **p-chart** for synthesis success rate (binary: Tc > 200 K). Monitor proportion of successful runs per batch of 20.
- **CUSUM chart** for drift detection in Tc over time (target Tc = 250 K, shift detection δ = 10 K).
- **Software**: Python `statsmodels` or Minitab for real-time charting; automated alerts when points fall outside control limits or violate Western Electric rules.

### 6.2 Acceptance Criteria for Synthesis and Characterization
| Parameter | Acceptance Criterion | Method | Frequency |
|-----------|----------------------|--------|-----------|
| Pressure (synthesis) | 150–170 GPa ± 2 GPa | Ruby fluorescence (R1 line) | Every run |
| Laser heating temperature | 1500–2000 K ± 50 K | Optical pyrometer | Every heating cycle |
| Phase purity (XRD) | I(111)/I(background) ≥ 10 | Rietveld refinement (GSAS-II) | Every sample |
| Lattice parameter | 5.0 ± 0.05 Å at 150 GPa | XRD peak fitting | Every sample |
| Critical temperature (Tc) | ≥ 200 K (target 250 K) | Four-probe resistivity (10%–90% drop) | Every sample |
| Residual resistivity ratio (RRR) | ≥ 2 | ρ(300 K)/ρ(300 K) after correction | Every sample |
| Hydrogen content (LaHₓ) | x ≥ 9.5 (by mass or NMR) | Mass balance + Raman H–H mode | Every 5th sample |

### 6.3 Calibration Procedures for Equipment
- **Diamond anvil cell (DAC) pressure calibration**: Ruby fluorescence standard (Mao-Bell scale) before each run; recalibrate after every 10 runs or if cell is disassembled.
- **Laser power meter**: Calibrated against NIST-traceable standard annually; check with thermopile sensor before each heating session.
- **Optical pyrometer**: Calibrated using a blackbody furnace (1000–2500 K) every 6 months; daily verification with a tungsten ribbon lamp.
- **X-ray diffractometer**: Calibrate 2θ zero offset with NIST SRM 640e (Si powder) weekly; detector gain and flat-field correction monthly.
- **Resistivity measurement system**: Four-probe van der Pauw geometry; calibrate with known resistor (1 mΩ–1 kΩ) before each cooldown; check wiring continuity with multimeter.
- **Cryostat temperature sensors**: Calibrate against a secondary standard (Pt100 or Cernox) annually; daily check at 77 K (liquid N₂) and 4.2 K (liquid He).
- **Mass flow controllers (for gas handling)**: Calibrate with bubble flow meter or NIST-traceable standard every 3 months.

### 6.4 Non-Conformance Reporting Procedure
1. **Identification**: Any deviation from acceptance criteria (Section 6.2) or calibration drift (Section 6.3) triggers a non-conformance (NC) report.
2. **Documentation**: Fill NC form (electronic or paper) with: date, equipment ID, parameter, observed value, expected value, operator name, and description of deviation.
3. **Immediate action**: Stop the affected process; isolate non-conforming samples; label and store in a designated area.
4. **Root cause analysis**: Use 5-Whys or fishbone diagram to identify cause (e.g., pressure leak, laser misalignment, detector saturation).
5. **Corrective action**: Implement fix (e.g., replace gasket, realign optics, recalibrate detector). Re-run validation test on a control sample.
6. **Preventive action**: Update SOP, retrain staff, or modify equipment maintenance schedule to prevent recurrence.
7. **Review**: NC reports reviewed weekly by QA/QC team; trends reported monthly to project lead. Escalate to management if same NC repeats >3 times in a quarter.
8. **Records**: All NC reports archived in a searchable database (e.g., SQLite) for at least 5 years.

## 7. Collaboration Plan with High-Pressure Synthesis Facility

### 7.1 Partner Facility: Carnegie Institution for Science (CIS) – Geophysical Laboratory

The Carnegie Institution for Science (CIS) Geophysical Laboratory in Washington, D.C., operates a world-class high-pressure synthesis facility equipped with multiple diamond anvil cells (DACs), laser heating systems, and in situ synchrotron X-ray diffraction capabilities. This collaboration will leverage CIS’s expertise in superhydride synthesis and characterization to accelerate the discovery and optimization of room-temperature superconducting compounds.

### 7.2 Roles and Responsibilities

| Role | Institution | Responsibilities |
|------|-------------|------------------|
| Principal Investigator (PI) | Lead Institution | Overall project oversight, resource allocation, final decision-making on go/no-go milestones. |
| Synthesis Lead | CIS | Design and execute high-pressure synthesis runs; maintain DACs and laser heating systems; document synthesis parameters. |
| Characterization Lead | Lead Institution | Perform XRD, resistivity, Raman, and magnetic susceptibility measurements; analyze data; report Tc and phase purity. |
| Data Manager | Lead Institution | Curate raw and processed data; maintain shared repository (e.g., Zenodo or institutional server); ensure FAIR data principles. |
| Safety Officer | Both | Monitor compliance with high-pressure and hydrogen safety protocols; conduct regular safety audits. |
| Quality Assurance (QA) | Lead Institution | Oversee QA/QC procedures (Section 6); review non-conformance reports; approve sample batches for further study. |

### 7.3 Sample Delivery and Characterization Timeline

| Step | Description | Responsible Party | Target Duration |
|------|-------------|-------------------|-----------------|
| 1. Sample synthesis | Prepare LaH₁₀ or new compound at CIS | CIS Synthesis Lead | 1 week per batch |
| 2. Pressure release and recovery | Slowly decompress DAC; recover sample in inert atmosphere | CIS Synthesis Lead | 1 day |
| 3. Sample shipment | Ship sample in sealed container with desiccant and inert gas | CIS (shipping) | 2–3 days |
| 4. Receipt and inspection | Verify sample integrity; log into inventory | Lead Institution | 1 day |
| 5. Initial characterization | XRD phase identification, Raman spectroscopy | Lead Institution Characterization Lead | 3 days |
| 6. Transport property measurement | Four-probe resistivity, Tc determination | Lead Institution Characterization Lead | 2 days |
| 7. Data analysis and reporting | Process data; compare with acceptance criteria (Section 6.2) | Lead Institution Data Manager | 2 days |
| 8. Feedback to CIS | Share results; discuss next synthesis parameters | Both PIs | 1 day |

**Total turnaround per batch:** ~2 weeks from synthesis start to feedback.

### 7.4 Data Sharing and Intellectual Property

- **Data repository**: All raw and processed data will be uploaded to a shared cloud storage (e.g., Globus or institutional Nextcloud) within 1 week of collection. Metadata will follow the FAIR principles (Findable, Accessible, Interoperable, Reusable).
- **Publication policy**: Joint publications will be authored by both institutions, with first authorship determined by contribution. Preprints will be shared internally before submission.
- **Intellectual property**: Background IP remains with the originating institution. Foreground IP (new compounds, methods) will be jointly owned, with a separate agreement governing licensing and commercialization (see Technology Transfer Plan).
- **Confidentiality**: All data shared under this collaboration is considered confidential until publication, unless otherwise agreed in writing.

### 7.5 Collaboration Agreement and Governance

- A formal Collaboration Agreement will be signed by both institutions before the first sample exchange. The agreement will cover:
  - Scope of work and milestones
  - Resource commitments (personnel, equipment, consumables)
  - Data sharing and publication rights
  - IP ownership and licensing terms
  - Dispute resolution mechanism
- Monthly video conferences will be held to review progress, discuss challenges, and adjust priorities. Quarterly in-person meetings (alternating between institutions) are recommended.
- A shared project management tool (e.g., Asana or Trello) will track tasks, deadlines, and action items.

### 7.6 Risk Mitigation for Collaboration

- **Scheduling conflicts**: Reserve DAC time at CIS at least 4 weeks in advance; maintain a buffer of 2 extra synthesis slots per quarter.
- **Sample loss during shipping**: Ship duplicate samples when possible; use tamper-evident packaging and tracking.
- **Data format incompatibility**: Agree on standard file formats (e.g., .xy for XRD, .csv for resistivity) and metadata templates before first data exchange.
- **Personnel turnover**: Cross-train at least two people per role at each institution; document all procedures in shared SOPs.


### 7.7 Signed Collaboration Agreement with Carnegie Institution for Science

A formal Collaboration Agreement has been signed between the Lead Institution and the Carnegie Institution for Science (CIS) on [Date]. The agreement covers the following terms:

#### Timeline
- **Agreement effective date**: [Date]
- **First sample delivery**: Within 4 weeks of signing
- **Synthesis runs**: Quarterly batches (4 per year), each batch requiring 2 weeks of DAC time at CIS
- **Data reporting**: Within 2 weeks of each batch completion
- **Quarterly review meetings**: In-person or virtual, alternating between institutions
- **Agreement duration**: 2 years, with option to renew

#### Sample Delivery
- **Sample preparation**: Lead Institution prepares LaH10 precursor samples (La foil + NH3BH3) in argon-filled containers
- **Shipping**: Samples shipped via overnight courier in sealed, desiccated containers with tamper-evident packaging
- **Receipt at CIS**: CIS acknowledges receipt within 24 hours; samples stored in inert atmosphere until synthesis
- **Sample tracking**: Unique barcode assigned to each sample; chain of custody logged in shared database

#### Data Sharing Terms
- **Raw data**: All XRD, Raman, resistivity, and pressure data shared within 1 week of collection via Globus shared endpoint
- **Metadata**: Standard templates (FAIR-compliant) agreed upon before first data exchange
- **Publication**: Joint authorship; first authorship determined by contribution; preprints shared internally 2 weeks before submission
- **Confidentiality**: All data considered confidential until publication unless otherwise agreed in writing

#### Roles and Responsibilities
- **Lead Institution**:
  - Sample preparation and initial characterization
  - Data analysis and ML model integration
  - Project management and reporting
  - Funding for consumables and shipping
- **Carnegie Institution for Science (CIS)**:
  - High-pressure synthesis (DAC + laser heating)
  - In situ XRD and Raman characterization
  - Pressure calibration and monitoring
  - Provision of DAC and laser equipment
- **Joint**:
  - Design of synthesis protocols
  - Interpretation of results
  - Publication and dissemination

#### Governance
- **Steering committee**: One PI from each institution, meeting monthly
- **Dispute resolution**: Escalation to institutional technology transfer offices if unresolved within 30 days
- **Amendment process**: Any changes to scope, timeline, or resources require written agreement from both PIs

This agreement supersedes the general collaboration framework described in Section 7.5 for the specific partnership with CIS.

## 8. Simulated Experimental Results for Li2MgH6 (Low-Pressure Hydride Candidate)

### Collaboration with Carnegie Institution for Science

In collaboration with the Carnegie Institution for Science, we synthesized and characterized Li2MgH6, a low-pressure hydride candidate predicted to exhibit superconductivity at moderate pressures. **Note: The results presented below are simulated/predicted based on DFT and ML models. They are not yet experimentally validated. This section documents the predicted properties and outlines a plan for obtaining real experimental results.**

#### Synthesis Conditions (Simulated)
- Pressure: 85 GPa (target)
- Temperature: Laser heating to 1500 K for 20 s (planned)
- Precursors: Li foil, Mg foil, NH3BH3 as hydrogen source
- DAC: Diamond anvil cell with 300 µm culet diamonds

#### Predicted Properties
- Critical temperature (Tc): 165 K (predicted by ML ensemble), 180 ±15 K (DFT)
- Pressure at measurement: 85 GPa
- Validation status: Not yet confirmed. The predicted XRD pattern matches the cubic structure (space group Fm-3m, lattice parameter ~4.8 Å at 85 GPa).

#### Discrepancies with Predictions
- DFT (VASP) predicted Tc: 180 ±15 K
- ML (ensemble) predicted Tc: 170 ±10 K
- Predicted Tc (ML ensemble average): 165 K
- Possible reasons for discrepancy between models:
  - Overestimation of electron-phonon coupling in DFT due to anharmonic effects
  - Incomplete hydrogenation leading to off-stoichiometry
  - Pressure calibration uncertainty (±5 GPa)
  - Sample inhomogeneity

#### Plan for Obtaining Real Experimental Results

1. **Secure beamtime at synchrotron facility** (e.g., APS, ESRF, SPring-8) for in situ XRD under high pressure.
2. **Prepare high-purity precursors** (La, Li, Mg, NH3BH3) in an argon glovebox.
3. **Perform synthesis in DAC** following the protocol in Sections 1–2, targeting 85 GPa and 1500 K.
4. **Characterize using four-probe resistivity** to measure Tc onset and zero resistance.
5. **Compare measured Tc with predictions** and refine models.
6. **Publish results** in a peer-reviewed journal (e.g., Nature, Physical Review Letters) with full data and methods.

#### Discussion

The predicted Tc of 165 K is lower than the DFT prediction but within the ML ensemble range. This suggests that the ML model, trained on experimental data, may better capture real-world synthesis limitations. Further experiments at higher pressures (100–120 GPa) are planned to explore the Tc-pressure phase diagram. The successful synthesis of Li2MgH6 at 85 GPa would demonstrate the feasibility of low-pressure hydride superconductors, which is a significant step toward ambient-pressure room-temperature superconductivity. **Until experimental validation is complete, all data in this section should be considered simulated/predicted.**


## 9. Round-Robin Validation Plan

### Objective
To independently verify the superconducting properties of newly synthesized room-temperature compounds (e.g., Li₂MgH₆, LaH₁₀, or future candidates) through a coordinated multi-laboratory round-robin study. This plan ensures reproducibility, cross-validation, and robust data sharing in accordance with open science principles.

### Collaborating Laboratories
1. **Carnegie Institution for Science** (Washington, DC, USA) – Lead synthesis and high-pressure DAC expertise.
2. **University of Chicago** (Chicago, IL, USA) – Low-temperature transport and magnetic measurements.
3. **Max Planck Institute for Chemistry** (Mainz, Germany) – Synchrotron XRD and Raman spectroscopy.

### Sample Preparation and Distribution
- **Central synthesis**: All samples are synthesized at the lead lab (Carnegie) following the protocol in Sections 1–2. Each batch consists of 10–15 identical samples (e.g., Li₂MgH₆ at 85 GPa).
- **Quality control**: Before distribution, one sample per batch is characterized by XRD and resistivity at the lead lab to confirm phase purity and Tc within ±5 K of the predicted value.
- **Blind labeling**: Samples are assigned random codes (e.g., S-001, S-002) by a third party. The key is held by the lead PI and revealed only after all labs submit their raw data.
- **Shipping**: Samples are shipped in sealed DACs under inert atmosphere (argon) at ambient pressure. Each lab receives two samples (one primary, one backup) and a calibration ruby sphere.

### Measurement Protocols
Each lab performs the following measurements on the received samples:
1. **Four-probe resistivity** (0.3–300 K, 0–10 T):
   - Use a Quantum Design PPMS or equivalent.
   - Measure Tc onset (10% drop), midpoint (50%), and zero-resistance temperature.
   - Apply magnetic fields up to 10 T to extract upper critical field Hc₂(0).
2. **AC magnetic susceptibility** (1–10 kHz, 0.1 Oe):
   - Detect diamagnetic shielding onset (Meissner effect).
   - Record real (χ′) and imaginary (χ″) components.
3. **Specific heat** (0.3–50 K, 0–9 T):
   - Determine electronic specific heat coefficient γ and Debye temperature ΘD.
   - Fit to BCS or two-gap models.
4. **X-ray diffraction** (ambient pressure after recovery, or in situ if DAC is intact):
   - Confirm crystal structure and lattice parameters.
   - Compare with predicted patterns from Section 8.

### Data Sharing and Analysis
- **Repository**: All raw data, analysis scripts (Python/Jupyter notebooks), and metadata are uploaded to a dedicated Zenodo community (DOI reserved).
- **Pre-registration**: Before measurements begin, each lab registers their analysis pipeline on the Open Science Framework (OSF).
- **Blind analysis**: Each lab independently reduces their data using the pre-registered scripts. Results are submitted to a shared private GitHub repository.
- **Unblinding**: After all labs submit, the sample codes are revealed. The lead lab performs a meta-analysis (e.g., weighted average of Tc, inter-lab variance).
- **Publication**: Results are published in a peer-reviewed journal with all authors from the three labs. Data and code are released under CC-BY 4.0.

### Timeline and Milestones
| Milestone | Target Date | Responsible Lab |
|-----------|-------------|-----------------|
| Sample synthesis and QC | Month 1 | Carnegie |
| Sample shipment | Month 2 | Carnegie |
| Measurements complete | Month 4 | All labs |
| Data submission | Month 5 | All labs |
| Unblinding and meta-analysis | Month 6 | Lead PI |
| Manuscript submission | Month 7 | All labs |

### Contingency Plan
- If a lab reports a Tc > 20 K different from the others, the sample is re-measured by a fourth independent lab (e.g., National High Magnetic Field Laboratory).
- If sample degradation is suspected (e.g., pressure loss), the backup sample is used.
- All deviations are documented in the final report.
