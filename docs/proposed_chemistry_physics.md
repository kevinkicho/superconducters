# Proposed Chemistry and Physics for Room-Temperature Superconductivity

## 2024–2026 Breakthroughs: Updated Chemistry and Physics

This document updates the previous `proposed_chemistry_physics.md` (root level) with seven major breakthroughs from 2024–2026 that fundamentally reshape the chemistry and physics of room-temperature superconductivity. Each section presents the key experimental/theoretical findings, the underlying mechanism, and implications for discovery and manufacturing.

---

## 1. LaSc₂H₂₄ — First Reproducible Room-Temperature Superconductor

### What
Ternary clathrate hydride LaSc₂H₂₄ exhibits zero resistance and perfect diamagnetism at 271–298 K under 195–266 GPa. This is the first experimentally confirmed room-temperature superconductor, validated by thirteen independent experimental runs by Song, Ma, Wang et al. (2025).

### Key Data Points
- **Tc,onset** = 298 K (25 °C) at ~260 GPa
- **Structure**: Hexagonal P6/mmm (MgB₂-type metal sublattice) with La@H₃₀ and Sc@H₂₄ cages
- **Superconducting gap**: Isotropic single-gap s-wave (confirmed by anisotropic Migdal–Eliashberg calculations)
- **Upper critical field**: μ₀Hc₂(0) = 89–228 T; coherence length ~1.7–1.9 nm

### Mechanism (Sc-Induced Gap Unification)
Wang et al. (2026) elucidated the microscopic mechanism: Sc 3d electrons play a dual role:
1. **Jahn–Teller effect**: Sc 3d electrons distort specific interlayer H–H bonds, softening associated phonon modes and enhancing electron–phonon coupling (EPC).
2. **Electronic reconstruction**: Sc 3d electrons reconstruct the electronic structure into an MgB₂-like configuration, generating Sc–H–Sc σ/π bonding states with EPC strengths comparable to LaH₁₀.

Crucially, Sc–H hybridization merges the previously separate high-EPC H–H and La–H gap channels into a single isotropic gap with uniformly large coupling — a mechanism termed **Sc-induced gap unification**.

### Synthesis
Precursor mixture (1:2 La–Sc alloy + NH₃BH₃) loaded into diamond anvil cell (DAC), compressed to >195 GPa, and heated with a pulsed laser to drive reaction.

### Implications
- Validates the ternary hydride strategy for room-temperature Tc
- Provides a blueprint for selecting dopants that unify superconducting gaps
- Extreme pressure (~200 GPa) remains the primary barrier to practical application

### Sources
- Song et al., arXiv:2510.01273 (2025) — experimental synthesis & characterization. https://www.alphaxiv.org/overview/2510.01273v2
- Wang et al., arXiv:2601.01398 (2026) — mechanism (gap unification). https://arxiv.org/html/2601.01398v1
- Liu et al., *PNAS* 121, e2401840121 (2024) — theoretical prediction. https://pmc.ncbi.nlm.nih.gov/articles/PMC11214075/

---

## 2. Zentropy Theory for High-Tc Superconductor Design

### What
Penn State's Zi-Kui Liu developed **zentropy theory**, which bridges BCS theory with density functional theory (DFT) by using a nested configurational-entropy formulation. It links a material's electronic structure at T=0 K to its temperature-dependent superconducting transition, enabling first-principles prediction of Tc without empirical fitting.

### Key Results
- Successfully predicted Tc for both conventional (BCS) and high-temperature (cuprate) superconductors
- Forecasted potential superconductivity in Cu, Ag, and Au at extremely low temperatures — metals not normally considered superconductors
- Published in *Superconductor Science and Technology* (2025)

### Mechanism
The theory connects the symmetry-broken electronic configurations captured by DFT (even though DFT does not directly model Cooper pairs) to the statistical mechanics of thermal excitations via zentropy. The key insight: the electron density predicted by DFT for the ground state configuration carries information about the paired-electron state, and the nested configurational entropy accounts for all symmetry-broken configurations that become thermally accessible as temperature increases.

### Future Plans
- Screen a database of **5 million materials** to identify new superconducting candidates
- Predict how pressure affects Tc
- Collaborate with experimental groups to synthesize predicted compounds

### Implications
If validated by experimental synthesis of a zentropy-predicted superconductor, this would be a transformative predictive tool, demystifying high-Tc design and enabling rational search.

### Sources
- ScienceDaily, "Are room-temperature superconductors finally within reach?" (31 Oct 2025). https://www.sciencedaily.com/releases/2025/10/251030075132.htm
- Z.-K. Liu & S.-L. Shang, *Supercond. Sci. Technol.* (2025). DOI: 10.1088/1361-6668/adedbc
- Z.-K. Liu, *Zentropy: Theory and Fundamentals* (Jenny Stanford Publishing, 2024)
- Z.-K. Liu, *Zentropy: Tools, Modelling, and Applications* (Jenny Stanford Publishing, 2024)

---

## 3. Twisted WSe₂ Moiré Superconductivity

### What
Two *Nature* papers (Oct 2024/Jan 2025) report robust superconductivity in twisted bilayer WSe₂ (tWSe₂) at twist angles of 3.5°, 3.65°, and 5.0°. This is the first observation of moiré flat-band superconductivity in a transition metal dichalcogenide (TMD) system, extending the phenomenon beyond graphene.

### Key Data Points
- **Tc** = 426 mK (5.0° tWSe₂) — very low, but demonstrates the mechanism
- Superconductivity emerges at **half-band filling** near Coulomb-induced charge localization
- Adjacent to a metallic state with Fermi surface reconstruction (possibly antiferromagnetic order)
- Strong spin–orbit coupling and honeycomb moiré lattice

### Mechanism
Flat moiré bands at half-filling give rise to strong electronic correlations. The proximity to a charge-localized (Mott-like) state suggests an unconventional pairing mechanism driven by electronic interactions rather than phonons. The strong Ising spin–orbit coupling in WSe₂ protects the superconducting state against in-plane magnetic fields.

### Implications
- Opens a new platform for studying unconventional superconductivity in strongly correlated 2D systems
- Tc may be raised by optimizing twist angle, dielectric screening, and doping
- Demonstrates that moiré engineering is a viable route to designer superconductivity

### Sources
- Xia et al., *Nature* 637, 839–843 (2025). DOI: 10.1038/s41586-024-08116-2
- Guo et al., *Nature* 637, 844–848 (2025). DOI: 10.1038/s41586-024-08381-1
- arXiv:2405.14784 (unconventional SC in 3.65° tWSe₂)

---

## 4. H₃S Tunneling Gap Anomaly — Direct Spectroscopic Confirmation

### What
The Max Planck Institute for Chemistry team (Du et al., 2025) performed the first direct measurement of the superconducting gap in a hydride superconductor using planar electron tunneling spectroscopy under high pressure. This provides the "smoking gun" microscopic evidence that hydride superconductivity is phonon-mediated.

### Key Results
- **H₃S gap**: ~60 meV (fully open, s-wave)
- **D₃S gap**: ~44 meV
- **Isotope effect**: Δ(D)/Δ(H) ~0.73 — confirms phonon-mediated pairing
- Confirms conventional BCS/Eliashberg mechanism in hydrides

### Technique
Planar tunnel junctions were fabricated directly in the DAC, allowing electron tunneling spectroscopy at megabar pressures for the first time. The superconducting gap was measured as a function of temperature, and its temperature dependence follows the BCS prediction.

### Implications
- Provides definitive proof that hydride superconductivity is conventional phonon-mediated
- The technique can now be applied to LaH₁₀, YH₉, and LaSc₂H₂₄ to map gap structures and confirm pairing symmetry
- Validates the theoretical framework (Eliashberg theory) used to predict new hydride superconductors

### Sources
- Du et al., *Nature* (23 Apr 2025). DOI: 10.1038/s41586-025-08895-2
- Phys.org summary: https://phys.org/news/2025-04-high-pressure-electron-tunneling-spectroscopy.html
- MPIC press release: https://www.mpic.de/5700716/nature-of-superconductivity

---

## 5. Pressure-Quenched Hg-1223 — Ambient-Pressure Tc Record of 151 K

### What
The University of Houston team (Deng, Chu, et al., 2026) developed a **pressure-quench protocol (PQP)** that traps a metastable high-pressure phase of HgBa₂Ca₂Cu₃O₈₊δ (Hg-1223) at ambient pressure, achieving Tc = 151 K — breaking the 133 K record that stood since 1993.

### Key Data Points
- **Ambient-pressure Tc** = 151 K (previous record ~133 K)
- **Quench pressure** PQ = 10–30 GPa
- **Quench temperature** TQ = 4.2 K (liquid helium)
- Supported by synchrotron XRD and phonon calculations

### The Pressure-Quench Protocol (PQP)
1. Compress Hg-1223 to 10–30 GPa in a DAC to reach the high-Tc phase
2. Cool to 4.2 K while maintaining pressure
3. Rapidly release pressure (quench) to ambient in milliseconds
4. Warm sample gradually; measure resistance drop at 151 K, confirming superconductivity

The metastable state persists for days in liquid nitrogen, stable enough for detailed study.

### Implications
- The PQP concept is potentially revolutionary — if applicable to hydrides, it could yield ambient-pressure room-temperature superconductivity
- Demonstrates that high-pressure phases can be "locked in" at ambient conditions
- However, the Hg-1223 result has not yet shown definitive zero resistance, and independent replication is needed

### Sources
- Deng et al., *PNAS* 123, e2536178123 (2026). DOI: 10.1073/pnas.2536178123
- arXiv:2603.12437 (2026). https://arxiv.org/abs/2603.12437
- Physics APS: https://physics.aps.org/articles/v19/37
- University of Houston press release: https://www.uh.edu/nsm/news-events/stories/2026/0310-superconductivity-record.php

---

## 6. Li–Na–H Clathrate Room-Temperature Superconductor Predictions

### What
High-throughput screening combined with crystal structure prediction by An, Duan, et al. identified two thermodynamically stable room-temperature superconductors in the Li–Na–H system. These are the first thermodynamically stable ternary hydrides predicted to exhibit room-temperature Tc.

### Key Predictions
- **Li₂NaH₁₇** (type-II clathrate, Fd-3m): predicted Tc = 340 K at 300 GPa
- **LiNa₃H₂₃** (type-I clathrate, Pm-3n): predicted Tc = 310 K at 350 GPa
- Li₂NaH₁₇ has the **highest Tc among all predicted thermodynamically stable ternary hydrides**
- Later refinement (Adv. Funct. Mater. 2025) suggests Li₂NaH₁₇ may reach 357 K at 220 GPa

### Mechanism
- Dominant H-derived density of states (DOS) at the Fermi level
- Strong Fermi surface nesting
- The clathrate cage structure (type-I and type-II) provides optimal hydrogen contact geometry for strong electron–phonon coupling

### Implications
- Demonstrates that room-temperature superconductivity is accessible in **light-alkali hydrides**, not only rare-earth systems
- Li and Na are abundant and cheap, offering a cost advantage over Y, La, Sc
- However, required pressures (300–350 GPa) are even higher than LaSc₂H₂₄, posing severe synthesis challenges

### Sources
- An et al., *Adv. Funct. Mater.* 35, 2418692 (2025). DOI: 10.1002/adfm.202418692
- An et al., arXiv:2303.09805 (2023). https://arxiv.org/abs/2303.09805
- Ma et al., arXiv:2412.13431 (2024) — high-throughput discovery of ternary clathrate hydrides

---

## 7. AI Causal Discovery for Superconductor Screening

### What
Tohoku University and Fujitsu (Dec 2025) used **causal discovery AI** to analyze ARPES measurement data from the kagome superconductor CsV₃Sb₅, automatically extracting causal relationships and revealing a previously unknown mechanism: the chemical bonding state of cesium (Cs) atoms strongly influences the electronic state of the V₃Sb₅ layer that is responsible for superconductivity.

### Key Technical Advances
- **Causal graph compression**: New technique reduces the size of the causal graph to <1/20 of conventional size by extracting waveform parameters
- **Simplification via similarity**: Redundant nodes are removed by assessing similarity of highly correlated data pairs
- **Noise filtering**: Only causal relationships with reliability, strength, and correlation above threshold are presented

### Result
While prevailing theories held that only vanadium electrons (or vanadium + antimony electrons) were involved in superconductivity, the AI revealed that Cs 3d electrons also play a crucial role — all three elements (V, Sb, Cs) contribute to the pairing mechanism.

### Future Plans
- Fujitsu will offer a trial environment for this technology from March 2026
- Will be applied to NanoTerasu Synchrotron Light Source data for high-throughput materials discovery
- Published in *Scientific Reports* (Nature Portfolio, Dec 2025)

### Implications
- AI can discover hidden causal relationships in complex spectroscopic data that humans miss
- Can accelerate the identification of key structural and electronic features that control Tc
- Combined with high-throughput synthesis, this could dramatically speed up the discovery cycle

### Sources
- Tohoku University & Fujitsu press release (23 Dec 2025). https://www.eurekalert.org/news-releases/1110914
- Fujitsu global press release: https://global.fujitsu/en-global/pr/news/2025/12/23-01
- Phys.org summary: https://phys.org/news/2025-12-superconducting-material-ai.html

---

## 8. Synthesis Implications and Integrated Strategy

### Pressure Reduction Pathways

| Strategy | Example | Current Pressure | Target Pressure | Status |
|----------|---------|-----------------|-----------------|--------|
| Ternary hydride doping | LaSc₂H₂₄ | ~200 GPa | <100 GPa | Experimental demonstration (Sc-doped LaH₁₀) |
| Chemical precompression | Li–Na–H clathrates | ~300 GPa | <100 GPa | Theoretical prediction only |
| Pressure-quench protocol | Hg-1223 PQP | 10–30 GPa → ambient | Ambient | Demonstrated for cuprates; untested for hydrides |
| AI-guided discovery | CsV₃Sb₅ causal AI | N/A | N/A | New causal relationships identified |
| Zentropy screening | 5M materials database | N/A | N/A | Predictive method validated; experimental verification pending |

### Recommended Research Directions (2026–2030)

1. **Apply PQP to hydrides**: The pressure-quench protocol demonstrated for Hg-1223 should be systematically applied to LaSc₂H₂₄, LaH₁₀, and YH₉ to attempt ambient-pressure retention of their high-Tc phases.

2. **Ternary hydride optimization**: Guided by the Sc-induced gap unification mechanism, search for dopants (e.g., Zr, Hf, Ti) that similarly unify superconducting gaps at lower pressures.

3. **Zentropy-guided high-throughput screening**: Use the zentropy framework to screen the 5M materials database and prioritize the top 20 candidates for experimental synthesis.

4. **AI causal discovery pipeline**: Apply the Fujitsu/Tohoku causal AI to ARPES data from LaSc₂H₂₄, H₃S, and other hydrides to identify the key electronic features that correlate with high Tc.

5. **Moiré heterostructure engineering**: Explore higher twist angles, dielectric screening, and doping in tWSe₂ to raise Tc above 1 K, and search for moiré superconductivity in other TMD bilayers (e.g., MoTe₂, MoSe₂).

### Open Questions
- Can the pressure-quench protocol retain the high-Tc phase of LaSc₂H₂₄ at ambient pressure?
- Is the zentropy theory universally applicable to all classes of superconductors?
- Can AI discover a causal relationship that leads to a new superconductor with Tc > 300 K at ambient pressure?
- Are Li–Na–H clathrates synthesizable at the predicted pressures, and do they match theoretical Tc?
- What is the upper Tc limit for moiré flat-band superconductivity?

---

*This document incorporates findings from peer-reviewed literature and preprints through early 2026. All claims should be verified against original publications. URLs provided for direct access.*
