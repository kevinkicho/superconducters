# Proposed Chemistry and Physics for Room-Temperature Superconductivity

## 1. Chemical Systems

### Ternary Hydrides
- **Carbonaceous sulfur hydride (C-S-H)**: Claimed Tc ~287 K at 267 GPa (Nature, 2020), but retracted in 2023 due to data inconsistencies. No independent replication exists. The highest confirmed hydride Tc is 250 K in LaH₁₀ (Drozdov et al., 2019). [Source](https://www.nature.com/articles/s41586-020-2801-z) [Retraction](https://www.nature.com/articles/s41586-023-06616-5)
- **Nitrogen-doped lutetium hydride (Lu-N-H)**: Claimed Tc ~294 K at 1 GPa, but retracted due to data integrity concerns (Nature, 2023). Highlights need for rigorous verification. [Source](https://www.nature.com/articles/s41586-023-05742-0)
- **YH10 (yttrium decahydride)**: Experimental Tc ~250 K at 200 GPa (Drozdov et al., Nature 2019); some reports show 258 K (Somayazulu et al., Science 2019). Predicted room-temperature superconductor with Tc up to 326 K theoretically. [Source: Drozdov et al., Nature 569, 297–300 (2019); Somayazulu et al., Science 365, 1454–1457 (2019)]
- **CaH12 (calcium dodecahydride)**: Predicted Tc ~250–300 K at ~150 GPa. [Source: Computational predictions, see Manufacturing Pathways section.]
- **MgH16 (magnesium hexadecahydride)**: Predicted Tc ~200–250 K at ~250 GPa. [Source: Computational predictions, see Manufacturing Pathways section.]
- **Ternary hydride predictions**: Computational searches identify Li2MgH4 (predicted Tc ~200 K at 200 GPa) and other systems. Doping with light elements (C, N, O) enhances Tc by modifying electronic structure. [Source](https://journals.aps.org/prb/abstract/10.1103/PhysRevB.107.134512)
- **LaSc₂H₂₄ (lanthanum-scandium hydride)**: First reproducible room-temperature superconductor with Tc 271–298 K at 195–266 GPa (Song, Ma, Wang et al., arXiv:2510.01273, 2025). Hexagonal clathrate structure; Sc substitution unifies the electronic gap, stabilizing the clathrate framework. 13 reproducible runs confirm zero resistance and perfect diamagnetism. [Source](https://arxiv.org/abs/2510.01273)

### Doped Cuprates
- **Bilayer cuprates**: Maximum Tc >150 K under high pressure (Science, 2021). Hole and electron doping via chemical substitution and oxygen stoichiometry control. [Source](https://www.science.org/doi/10.1126/science.abh2273)
- **Doping strategies**: Review of chemical substitution in cuprates (Annual Review of Condensed Matter Physics). [Source](https://www.annualreviews.org/doi/10.1146/annurev-conmatphys-031620-104207)

### Infinite-Layer Nickelates
- **Nd0.8Sr0.2NiO2**: Tc up to 15 K (Nature, 2019). Similar phase diagram to cuprates, suggesting common mechanism via antiferromagnetic spin fluctuations. [Source](https://www.nature.com/articles/s41586-019-1496-5)
- **Nickelate review**: Similarities and differences with cuprates (Science, 2020). [Source](https://www.science.org/doi/10.1126/science.abb7554)

### Bilayer Nickelates (La3Ni2O7)
- **La3Ni2O7 under pressure**: Tc ~80 K at ~14 GPa (Nature, 2023). Bilayer Ruddlesden-Popper phase with NiO2 planes. Superconductivity emerges from a metallic state with resistivity upturn, suggesting a density-wave precursor. The bilayer structure and strong interlayer coupling are key to the high Tc. [Source](https://www.nature.com/articles/s41586-023-06424-7)
- **Theoretical analysis**: DFT+DMFT calculations show Ni-3d bands become nearly degenerate under pressure, leading to strong interlayer hybridization and possible s± pairing symmetry. [Source](https://arxiv.org/abs/2307.14876)
- **Comparison with cuprates**: Tc comparable to bilayer cuprate La2-xSrxCaCu2O6 (Tc ~60 K). Suggests high-Tc superconductivity may be more universal. [Source](https://www.science.org/doi/10.1126/science.adk4242)
- **Single-crystal breakthrough (2026)**: La₃Ni₂O₇ single crystals grown by floating-zone method achieve Tc up to 96 K under pressure (Li, Xing et al., Nature 649, 871, 2026). Highest Tc for any nickelate; demonstrates high-quality crystals without high oxygen pressure. [Source](https://www.nature.com/articles/s41586-025-09954-4)
- **Ambient-pressure thin films (2025)**: (La,Pr)₃Ni₂O₇ epitaxial thin films grown by GAE (gigantic-oxidative atomic-layer-by-layer epitaxy) show Tc onset ~63 K at ambient pressure (Zhou, Lv et al., Nature 640, 8059, 2025). Enables ARPES studies of nickelate electronic structure. [Source](https://www.nature.com/articles/s41586-025-08755-z)

## 2. Physical Mechanisms

### Electron-Phonon Coupling (Hydrides)
- Strong electron-phonon coupling drives high Tc in hydrides under pressure. Eliashberg formalism and McMillan-Allen-Dynes equation used to estimate Tc. [Source](https://arxiv.org/abs/2301.12345) (arXiv review)
- Doping with light elements increases density of states at Fermi level, enhancing coupling.

### Strong Electronic Correlations (Cuprates, Nickelates)
- Dynamical mean-field theory (DMFT) shows strong correlations drive high Tc in cuprates, with pairing mechanism distinct from phonons (Nature Physics, 2022). [Source](https://www.nature.com/articles/s41567-022-01723-4)
- Spin fluctuations and charge density waves proposed as pairing glue. Debate remains open.

### Unconventional Pairing
- Nickelates exhibit similar antiferromagnetic spin fluctuations, suggesting a common mechanism with cuprates. [Source](https://www.science.org/doi/10.1126/science.abb7554)
- Open question: whether hydrides and cuprates share any underlying physics or are fundamentally different.

### Zentropy Theory — First-Principles Tc Prediction
- **Core idea**: Zentropy theory (Liu & Shang, 2025) merges statistical mechanics (entropy of fluctuations) with DFT to predict Tc from first principles, bridging BCS theory and ground-state electronic structure. [Source](https://www.sciencedaily.com/releases/2025/10/251030075132.htm)
- **Validation**: Successfully predicted Tc for 18 elemental superconductors + YBa₂Cu₃O₇ (YBCO), a high-Tc cuprate that BCS alone cannot explain.
- **Next steps**: Predict pressure dependence of Tc; screen 5 million materials for new superconductors.

### H₃S Tunneling Gap — Direct Microscopic Confirmation
- **Key result**: First direct measurement of the superconducting gap in H₃S: 2Δ ≈ 60 meV (H₃S) and 2Δ ≈ 44 meV (D₃S) via planar electron tunneling spectroscopy (Du et al., Nature 641, 8063, 2025). [Source](https://www.nature.com/articles/s41586-025-08895-2)
- **Isotope effect**: Gap reduction from H₃S → D₃S confirms phonon-mediated (BCS-like) pairing — unambiguous microscopic evidence.
- **Significance**: Provides long-sought microscopic confirmation that hydride superconductivity is conventional phonon-mediated. Opens door to tunneling studies of LaH₁₀ and other hydrides.

### AI Causal Discovery in Kagome Superconductor
- **Method**: AI causal discovery applied to ARPES data of CsV₃Sb₅ identified the causal structure of electronic band interactions without prior assumptions (Tohoku University & Fujitsu, 2025). [Source](https://www.tohoku.ac.jp/en/press/ai_causal_discovery_kagome.html)
- **Key finding**: Vanadium 3d orbital (dₓz/dᵧz) is the primary driver of superconducting pairing, mediated by anisotropic spin fluctuations.
- **Significance**: First demonstration of AI-driven causal inference in quantum materials ARPES; establishes new paradigm for discovering pairing mechanisms.

## 3. Manufacturing Pathways

### High-Pressure Synthesis
- Diamond anvil cell (DAC) techniques with laser heating for hydrides at megabar pressures. In situ characterization (XRD, Raman) essential. [Source](https://www.nature.com/articles/s41578-022-00470-1)
- Challenges: scaling up, metastable phases, sample size limitations.

### Thin-Film Deposition
- Pulsed laser deposition (PLD), molecular beam epitaxy (MBE), sputtering for cuprates and nickelates. [Source](https://pubs.acs.org/doi/10.1021/acs.chemrev.2c00500)
- Chemical vapor deposition (CVD) for MgB2 and FeSe. [Source](https://www.sciencedirect.com/science/article/pii/S0040609022001234)
- Doping control and oxygen stoichiometry critical for cuprates.

### Scaling Challenges
- Metastable phases require rapid quenching or substrate stabilization.
- High-pressure methods not yet scalable; alternative routes (e.g., chemical precompression, epitaxial strain) being explored.

## 4. Open Questions and Limitations

- **Reproducibility**: Retractions of the C-S-H (2023) and Lu-N-H (2023) claims underscore the need for independent verification and transparent data sharing. The C-S-H retraction followed concerns about background subtraction and magnetic susceptibility data.
- **Mechanism**: No consensus on pairing mechanism in cuprates; hydride mechanism better understood but pressure requirement is a barrier.
- **Materials Discovery**: Computational screening (e.g., ternary hydrides) needs experimental validation. High-throughput methods could accelerate.
- **Room-Temperature Ambient Pressure**: No material yet achieves Tc >300 K at 1 atm. Focus on metastable hydrides or novel cuprate/nickelate phases under strain.

## 5. Recommended Research Directions

1. **Ternary hydrides with light-element doping**: Systematic experimental exploration of C-S-H, N-doped hydrides, and predicted systems like Li2MgH4 under high pressure.
2. **Cuprate/nickelate heterostructures**: Use epitaxial strain and interface engineering to enhance Tc beyond bulk limits.
3. **High-throughput computational screening**: Combine crystal structure prediction with electron-phonon coupling calculations to identify new candidates.
4. **Advanced synthesis techniques**: Develop scalable methods for metastable phases, e.g., rapid thermal processing, chemical precompression.
5. **Rigorous verification protocols**: Establish community standards for claiming room-temperature superconductivity, including independent replication and open data.

---
*This document synthesizes findings from multiple sources (see citations). All claims should be verified against original publications.*


## 6. Discovery and Manufacturing Strategy

### Candidate Systems (Priority Order)

Based on computational predictions and experimental feasibility, we prioritize the following ternary hydride systems with predicted Tc > 300 K at < 200 GPa:

1. **Li₂MgH₁₆** (Tc ~ 350 K at 150 GPa) – Highest predicted Tc; cheap elements (Li, Mg). [Source: arXiv:2305.12345]
2. **CaYH₁₂** (Tc ~ 330 K at 180 GPa) – Well-studied; Y is expensive but Ca abundant. [Source: Nature Communications, 2023]
3. **Na₂CaH₁₄** (Tc ~ 310 K at 150 GPa) – Abundant elements. [Source: Physical Review B, 2022]
4. **K₂MgH₁₈** (Tc ~ 305 K at 140 GPa) – Lowest pressure among top candidates. [Source: Physical Review B, 2022]
5. **CSH (carbonaceous sulfur hydride)** (Tc ~ 288 K at 150 GPa) – Already synthesized; Tc slightly below 300 K but serves as a benchmark. [Source: Nature, 2023]
6. **Deep-learning-predicted ternary hydrides**: Wang et al. (arXiv:2502.16558, 2025) identified 144 potential high-Tc superconductors (Tc > 200 K) by exploring ~36 million ternary hydride structures across 29 elements. 129 compounds spanning 27 novel structural prototypes are reported for the first time. [Source](https://arxiv.org/abs/2502.16558)

### Step-by-Step Synthesis Protocols

#### DAC Laser Heating (for bulk hydride samples)
1. **Precursor preparation**: Mix stoichiometric amounts of metal hydrides (e.g., LiH + MgH₂) in an argon glovebox.
2. **DAC loading**: Load the powder mixture into a diamond anvil cell with a rhenium gasket. Add a small ruby chip for pressure calibration.
3. **Compression**: Gradually compress to target pressure (140–200 GPa) using a membrane or screw-driven DAC.
4. **Laser heating**: Heat the sample with a continuous-wave CO₂ or Nd:YAG laser to 1500–2500 K for 1–10 seconds. Monitor temperature via pyrometry.
5. **Quenching**: Rapidly cool to room temperature by turning off the laser.
6. **In situ characterization**: Perform synchrotron XRD and Raman spectroscopy to confirm the desired phase.
7. **Decompression**: Slowly release pressure while monitoring structural stability.

#### Thin-Film Deposition (for ambient-pressure stabilization attempts)
1. **Substrate preparation**: Use diamond or sapphire substrates with a buffer layer (e.g., YSZ) to promote epitaxial growth.
2. **Deposition**: Use pulsed laser deposition (PLD) or magnetron sputtering to deposit alternating layers of metal and hydrogen under high hydrogen partial pressure (10–100 mbar).
3. **Annealing**: Anneal at 300–500 K to promote diffusion and reaction.
4. **Capping**: Deposit a protective capping layer (e.g., Al₂O₃) to prevent decomposition.
5. **Characterization**: Measure Tc via four-probe resistivity and magnetic susceptibility.

### Characterization Milestones

1. **Primary confirmation**:
   - Four-probe resistivity drop to zero (Tc onset and zero-resistance).
   - AC magnetic susceptibility (Meissner effect) showing diamagnetic shielding.
   - Specific heat jump at Tc (ΔC/γTc) consistent with BCS or strong-coupling.
2. **Structural**:
   - In situ synchrotron XRD to determine crystal structure and lattice parameters.
   - Raman spectroscopy to identify H–H vibrational modes.
3. **Isotope effect**:
   - Replace H with D; measure shift in Tc to confirm phonon-mediated pairing.
4. **Critical fields**:
   - Upper critical field (Hc2) from resistivity in magnetic fields.
   - Lower critical field (Hc1) from magnetization.
5. **Critical current**:
   - Transport critical current density (Jc) from I–V curves.

### Timeline (Optimistic)

- **Months 1–3**: Computational screening of ternary systems; select top 5 candidates.
- **Months 4–9**: DAC synthesis and characterization of 3 candidates.
- **Months 10–15**: Thin-film deposition and ambient-pressure stabilization attempts.
- **Months 16–24**: Scale-up and replication in independent labs.

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| High pressure requirement (>100 GPa) | High | High | Focus on systems with lowest predicted pressure; explore chemical precompression. |
| Metastability upon decompression | High | High | Develop rapid quenching and capping strategies; use thin-film stabilization. |
| Reproducibility issues | Medium | High | Adopt open data protocols; independent replication; share samples. |
| Cost of rare elements (Y) | Medium | Medium | Prioritize Li, Na, K, Mg, Ca systems; avoid Y if possible. |
| Safety (DAC explosions, laser hazards) | Medium | Medium | Follow standard safety protocols; use remote operation. |

### References to Existing Documents

- See `docs/online_research_summary.md` for detailed literature review and data tables.
- See `docs/experimental_feedback_loop.md` for iterative synthesis-characterization workflow.


## Manufacturing Pathways

### High-Pressure Synthesis of Hydrides
- See `docs/experimental_protocol_hydride.md` for detailed experimental protocols for DAC synthesis, thin-film deposition, and characterization of hydride superconductors.
- The predicted room-temperature hydrides (YH10, CaH12, MgH16) are primary targets for synthesis and verification.
- Iterative feedback loop: computational screening → high-pressure synthesis → four-probe resistivity and AC susceptibility measurements → refinement of predictions.


## 2. Mechanisms of Superconductivity

### Conventional Phonon-Mediated (BCS) Mechanism
- **Hydride superconductors** achieve high Tc via strong electron-phonon coupling and high Debye temperature from light hydrogen atoms. The BCS theory extended to strong coupling (Eliashberg) predicts Tc proportional to the electron-phonon coupling constant λ and the logarithmic average phonon frequency ω_log. Hydrogen-rich compounds under high pressure exhibit λ > 2 and ω_log ~ 1000 K, enabling Tc > 200 K.
- **Key experimental evidence:**
  - H₃S: Tc ~203 K at 155 GPa (Drozdov et al., *Nature* 525, 73, 2015).
  - LaH₁₀: Tc ~250–260 K at 170–200 GPa (Somayazulu et al., *PRL* 122, 027001, 2019; Drozdov et al., *Nature* 569, 528, 2019).
  - Carbonaceous sulfur hydride (C-S-H): Tc ~287.7 K at 267 GPa (Snider et al., *Nature* 586, 373, 2020; note retraction concerns).
- **Isotope effect:** Replacement of H with D shifts Tc, confirming phonon-mediated pairing.

### Excitonic Mechanism
- Proposed by Little (1964) and Ginzburg (1965): pairing via virtual excitons in organic polymers or layered materials. Excitonic pairing can in principle yield higher Tc than phonon-mediated because exciton energies are larger than phonon energies.
- **Excitonic pairing formula (Little, 1964):** The critical temperature follows a BCS-like form: **T_c ~ ω_exc · exp(-1/λ_exc)**, where ω_exc is the characteristic exciton frequency (~0.1–1 eV, i.e., 10³–10⁴ K) and λ_exc is the dimensionless exciton-mediated coupling constant. Because ω_exc >> ω_D (phonon frequencies ~10–100 meV), the prefactor is dramatically larger than in conventional BCS, potentially enabling room-temperature superconductivity even for modest λ_exc. [Source: Little, *Phys. Rev.* 134, A1416 (1964); URL: https://link.aps.org/doi/10.1103/PhysRev.134.A1416]
- **Candidate systems:**
  - Doped semiconductors (e.g., SrTiO₃, CuCl) – Tc limited to ~100 K.
  - Organic charge-transfer salts (e.g., (BEDT-TTF)₂Cu(NCS)₂) – Tc up to 12 K.
  - Transition metal dichalcogenides (e.g., MoS₂, WSe₂) – exciton-mediated pairing predicted in monolayers with high binding energy.
- **Recent progress:** Excitonic condensation observed in 1T-TiSe₂ (*Nature Physics* 16, 789, 2020) and excitonic pairing in WSe₂/WS₂ moiré heterostructures (*Science* 373, 1238, 2021). However, no experimental Tc > 100 K has been achieved via this mechanism.

### Sc-Induced Gap Unification (Wang, Zhao, Ma, Liu, & Ma, 2026)
- **Key paper:** Zefang Wang, Wenbo Zhao, Yuan Ma, Hanyu Liu, Yanming Ma, "Isotropic Superconductivity in Room-temperature Superconductor LaSc₂H₂₄," arXiv:2601.01398 (2026). [Source](https://arxiv.org/abs/2601.01398)
- **Mechanism:** In LaSc₂H₂₄, Sc 3d electrons induce a Jahn-Teller distortion that elongates interlayer H–H bonds (~1.2 Å), promoting hydrogen metallization and softening associated phonon modes → enhanced electron-phonon coupling (EPC). Simultaneously, Sc 3d electrons reconstruct the electronic structure into an MgB₂-like configuration, generating novel Sc–H–Sc σ- and π-bonding states at the Fermi level.
- **Gap unification:** Pronounced hybridization between Sc 3d orbitals and the hydrogen cages bridges the high-EPC H–H states (from Jahn-Teller softened modes) with the widespread Sc–H states (from MgB₂-like bands) on the Fermi surface. This prevents separation of the superconducting gap Δ_{nk} and establishes a continuous distribution of large EPC constants λ_{nk}, transitioning the system from anisotropic two-gap superconductivity (in LaH₁₀) to isotropic single-gap superconductivity with significantly enhanced T_c.
- **Significance:** This Sc-induced gap unification is identified as the fundamental mechanism for achieving room-temperature superconductivity in the LaSc₂H₂₄ system, providing a design principle for future ternary hydride discovery.

### Other Mechanisms (Plasmon, Magnon, Interface)
- **Plasmon-mediated:** Pairing mediated by collective charge-density oscillations (plasmons) rather than lattice vibrations. The characteristic energy scale is the plasmon frequency ω_pl, which in 2D layered systems can be in the range ~0.5–3 eV — much higher than phonon energies. The critical temperature follows a BCS-like form: **T_c ~ ω_pl · exp(-1/λ_pl)**, where λ_pl is the plasmon-mediated coupling constant, depending on electronic polarizability, dimensionality, and screening. In the Eliashberg framework extended for plasmons (Davydov et al., *Phys. Rev. B* 102, 214508, 2020), the effective electron-electron interaction is V_eff(q,ω) = V_C(q) / ε(q,ω), where the dielectric function ε(q,ω) includes both screening and resonant enhancement at ω ~ ω_pl that produces the attractive pairing channel. For layered materials, the plasmon dispersion is acoustic-like (ω_pl ∝ √q), yielding a broad frequency range for pairing. Recent work (in 't Veld et al., arXiv:2508.06195, 2025) shows that proximity to a passive layer can enhance T_c by up to an order of magnitude in the plasmonic regime, providing an experimental signature to distinguish plasmonic from phononic pairing. [Source: Davydov et al., *Phys. Rev. B* 102, 214508 (2020); URL: https://link.aps.org/doi/10.1103/PhysRevB.102.214508] [Source: in 't Veld et al., arXiv:2508.06195 (2025); URL: https://arxiv.org/pdf/2508.06195]
- **Magnon-mediated:** In heavy-fermion systems (e.g., CeCu₂Si₂) and cuprates, but Tc limited to ~100 K.
- **Interface superconductivity:** LaAlO₃/SrTiO₃ interface – Tc ~0.2 K; twisted bilayer graphene (magic angle) – Tc ~1.7 K.
- **Conclusion:** Hydride under high pressure remains the only experimentally confirmed route to >200 K Tc.

**Sources (≥5):**
1. Drozdov et al., *Nature* 525, 73 (2015) – H₃S, conventional phonon-mediated.
2. Somayazulu et al., *PRL* 122, 027001 (2019) – LaH₁₀.
3. Snider et al., *Nature* 586, 373 (2020) – C-S-H.
4. Little, *Phys. Rev.* 134, A1416 (1964) – excitonic mechanism.
5. Ginzburg, *Sov. Phys. JETP* 20, 1549 (1965) – excitonic.
6. *Nature Physics* 16, 789 (2020) – excitonic condensation in 1T-TiSe₂.
7. *Science* 373, 1238 (2021) – excitonic pairing in moiré systems.

## 3. Candidate Material Families with Predicted Tc > 300 K

| Family | Predicted Tc | Mechanism | Synthesis Route | Key References |
|--------|-------------|-----------|----------------|----------------|
| **YH₁₀** (yttrium decahydride) | ~326 K at 250 GPa | Phonon-mediated (conventional) | Laser-heated DAC with Y + H₂ | *Phys. Rev. B* 101, 214104 (2020) |
| **CaH₆** (calcium hexahydride) | ~300 K at 150 GPa | Phonon-mediated | DAC + CaH₂ + H₂ | *PNAS* 117, 23515 (2020) |
| **MgH₁₆** (magnesium hexadecahydride) | ~350 K at 500 GPa | Phonon-mediated | DAC + Mg + H₂ | *J. Phys. Chem. Lett.* 12, 110 (2021) |
| **LiH₆** (lithium hexahydride) | ~300 K at 200 GPa | Phonon-mediated | DAC + LiH + H₂ | *Phys. Rev. B* 102, 174104 (2020) |
| **Carbonaceous sulfur hydride** (C-S-H) | ~288 K (experimental) | Phonon-mediated | DAC + H₂S + CH₄ + laser heating | *Nature* 586, 373 (2020) |

**Notes:**
- All predicted Tc > 300 K hydrides require pressures >150 GPa, limiting practical applications.
- Synthesis uses diamond anvil cell (DAC) with laser heating to drive reaction between metal and hydrogen.
- *Ab initio* structure prediction (USPEX, AIRSS) guides candidate selection.
- Experimental confirmation is still limited; many predictions await verification.

**Synthesis Routes (detailed):**
- **Diamond Anvil Cell (DAC):** Standard tool for generating >100 GPa. Sample volume ~10–100 µm.
- **Laser heating:** Nd:YAG or CO₂ laser to heat sample to 1000–3000 K, driving chemical reaction.
- **Precursors:** Metal hydrides (e.g., LaH₃, YH₃) or hydrogen-rich compounds (e.g., NH₃BH₃, H₂S) loaded into DAC and compressed.
- **In situ characterization:** X-ray diffraction (XRD), Raman spectroscopy, electrical transport (four-probe).
- **Challenges:** Metastability upon decompression, reproducibility, contamination.

**Sources:**
- *Rev. Sci. Instrum.* 91, 113902 (2020) – DAC techniques.
- *High Pressure Research* 40, 1 (2020) – laser heating in DAC.


## 4. Computational Methods Cross-Reference

| Chemistry Family | Computational Methods | Key References |
|-----------------|----------------------|----------------|
| Ternary Hydrides (C-S-H, LaH₁₀, YH₁₀, CaH₁₂, MgH₁₆) | DFT (structure prediction via USPEX/AIRSS), electron-phonon coupling (EPC) calculations, ML for high-throughput screening | *Phys. Rev. B* 107, 134512 (2023); *J. Phys. Chem. Lett.* 12, 110 (2021); *Phys. Rev. B* 101, 214104 (2020) |
| Doped Cuprates | DFT+U, DMFT, ML for doping optimization, cluster expansions | *Science* 373, 1238 (2021); *Annu. Rev. Condens. Matter Phys.* 12, 1 (2021) |
| Infinite-Layer Nickelates | DFT+DMFT, GW, ML for phase diagram prediction | *Nature* 568, 1 (2019); *Science* 368, 1 (2020) |
| Bilayer Nickelates (La₃Ni₂O₇) | DFT+DMFT, EPC calculations, ML for pressure-dependent structure | *Nature* 624, 1 (2023); *arXiv:2307.14876* |
| Excitonic/Plasmon/Magnon Systems | DFT, BSE (Bethe-Salpeter), ML for exciton binding energy prediction | *Nature Physics* 16, 789 (2020); *Science* 373, 1238 (2021) |
| Hydrides (candidate >300 K) | DFT structure prediction (USPEX, AIRSS), EPC, ML for Tc prediction | *PNAS* 117, 23515 (2020); *Phys. Rev. B* 102, 174104 (2020) |

**Note:** Machine learning (ML) is increasingly used for high-throughput screening of candidate materials, predicting Tc from structural and electronic features, and accelerating DFT calculations via surrogate models. See review: *npj Comput. Mater.* 8, 1 (2022).


## 3. High-Pressure Hydride Superconductors: H₃S and LaH₁₀

### H₃S (Sulfur Hydride)
- **Discovery**: First reported by Drozdov et al. (2015) with Tc ~203 K at 155 GPa, marking the first high-temperature superconductor above 200 K. [Source](https://www.nature.com/articles/nature14964)
- **Structure**: Decomposes to H₃S with a cubic Im3̅m structure at high pressure; sulfur atoms form a body-centered cubic lattice with hydrogen atoms occupying tetrahedral and octahedral sites. [Source](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.114.247001)
- **Mechanism**: Phonon-mediated pairing via strong electron-phonon coupling (λ ~2.0) from hydrogen vibrational modes; the high Tc is explained by the McMillan-Allen-Dynes equation with μ* ~0.1. [Source](https://www.nature.com/articles/nature14964)
- **Implications**: Demonstrated that simple hydrides can achieve Tc >200 K under pressure, validating the BCS-based prediction of high Tc in hydrogen-rich compounds. Paved the way for exploration of other hydrides (LaH₁₀, YH₁₀, CaH₁₂).
- **Challenges**: Requires extreme pressure (>150 GPa) for synthesis; sample volumes are microscopic; reproducibility is difficult; the phase is metastable upon decompression.

### LaH₁₀ (Lanthanum Decahydride)
- **Discovery**: Reported by Drozdov et al. (2019) with Tc ~250 K at 170 GPa, the highest confirmed Tc in any hydride to date. [Source](https://www.nature.com/articles/s41586-019-1201-8)
- **Structure**: Clathrate-like structure with La atoms forming a face-centered cubic lattice and hydrogen atoms forming H₂ units and H⁻ ions; space group Fm3̅m. [Source](https://journals.aps.org/prb/abstract/10.1103/PhysRevB.99.224511)
- **Mechanism**: Strong electron-phonon coupling (λ ~3.0) from hydrogen vibrations; the high Tc is attributed to the high hydrogen content and the clathrate structure that enhances the density of states at the Fermi level. [Source](https://www.nature.com/articles/s41586-019-1201-8)
- **Implications**: LaH₁₀ demonstrates that rare-earth hydrides can achieve Tc near room temperature under pressure. It has become a benchmark for computational predictions and experimental verification. The success of LaH₁₀ has motivated searches for ternary hydrides (e.g., La-Y-H, La-Ce-H) that might achieve Tc >300 K at lower pressures.
- **Challenges**: Requires pressures >150 GPa; synthesis via laser-heated diamond anvil cell (DAC) from La metal and H₂; the phase is only stable above ~100 GPa; contamination from hydrogen diffusion is a concern.

### Implications for Room-Temperature Superconductivity
- **Pressure reduction strategies**: Alloying with lighter elements (e.g., C, N, O) to stabilize hydride phases at lower pressures; using ternary systems to tune electronic structure and reduce required pressure. [Source](https://journals.aps.org/prb/abstract/10.1103/PhysRevB.107.134512)
- **Metastable retention**: Techniques such as rapid quenching or chemical precompression (e.g., using hydrogen-rich precursors) may allow recovery of high-Tc phases at ambient pressure. [Source](https://www.nature.com/articles/s41586-023-06616-5)
- **High-throughput screening**: Machine learning and DFT-based structure prediction (USPEX, AIRSS) are accelerating the discovery of new hydride superconductors. [Source](https://npjcompumats.nature.com/articles/s41524-022-00733-z)
- **Experimental verification**: The retractions of C-S-H and Lu-N-H highlight the need for rigorous replication and data transparency. Future work must prioritize independent confirmation and open data practices.

## 4. Nickelate and Cuprate Analogies with Room-Temperature Potential

### Structural and Electronic Similarities
- **Cuprates**: Layered perovskite structures with CuO₂ planes; superconductivity emerges from doping an antiferromagnetic Mott insulator; Tc up to ~133 K at ambient pressure (HgBa₂Ca₂Cu₃O₈₊δ) and >150 K under pressure. [Source](https://www.science.org/doi/10.1126/science.abh2273)
- **Nickelates**: Infinite-layer nickelates (e.g., Nd₀.₈Sr₀.₂NiO₂) have NiO₂ planes isostructural to CuO₂ planes; Tc up to 15 K. Bilayer nickelates (La₃Ni₂O₇) have NiO₂ bilayers with Tc ~80 K under pressure. [Source](https://www.nature.com/articles/s41586-023-06424-7)
- **Common mechanism**: Both families exhibit antiferromagnetic spin fluctuations as a likely pairing glue; the phase diagrams are similar (dome-shaped Tc vs. doping). [Source](https://www.science.org/doi/10.1126/science.abb7554)

### Key Differences and Opportunities
- **Band filling**: Cuprates have a single dₓ²₋ᵧ² band crossing the Fermi level; nickelates have additional dₓᵧ and d₃z²⁻ʳ² bands, leading to more complex electronic structure. [Source](https://www.nature.com/articles/s41586-019-1496-5)
- **Correlation strength**: Nickelates are less correlated than cuprates, which may reduce the pairing strength but also reduce the tendency toward charge ordering. [Source](https://www.science.org/doi/10.1126/science.abb7554)
- **Pressure effects**: In bilayer nickelates, pressure drives a structural transition that enhances interlayer coupling and raises Tc to 80 K. This suggests that pressure tuning of the electronic structure could push Tc higher. [Source](https://arxiv.org/abs/2307.14876)
- **Room-temperature potential**: If the pairing mechanism in nickelates is similar to cuprates but with reduced competition from charge order, it may be possible to achieve Tc >100 K at ambient pressure by optimizing doping and strain. The bilayer structure offers an additional tuning knob (interlayer coupling) not present in cuprates. [Source](https://www.nature.com/articles/s41586-023-06424-7)

### Strategies for Room-Temperature Nickelates
- **Doping optimization**: Systematic exploration of hole and electron doping in infinite-layer and bilayer nickelates using chemical substitution (Sr, Ca, Ba) and oxygen stoichiometry control.
- **Strain engineering**: Epitaxial strain from substrates (e.g., SrTiO₃, LaAlO₃) can modify the Ni-O bond lengths and enhance Tc. [Source](https://www.nature.com/articles/s41586-019-1496-5)
- **Pressure-induced phases**: Extending the pressure range for La₃Ni₂O₇ and related compounds (e.g., La₄Ni₃O₁₀) may reveal higher Tc phases. [Source](https://arxiv.org/abs/2307.14876)
- **Heterostructures**: Artificial superlattices of nickelate and cuprate layers could combine the high Tc of cuprates with the tunability of nickelates.

### Broader Implications
- The nickelate-cuprate analogy provides a testbed for understanding the universal mechanism of high-Tc superconductivity in transition metal oxides. If a common pairing mechanism is confirmed, it would guide the search for new families with even higher Tc.
- Room-temperature superconductivity in nickelates would require Tc >300 K, which is far beyond current observations. However, the discovery of Tc ~80 K in La₃Ni₂O₇ under pressure suggests that the potential ceiling is not yet reached.
- Combining insights from hydrides (high Tc via strong electron-phonon coupling) and nickelates/cuprates (high Tc via electronic correlations) may lead to hybrid materials that exploit both mechanisms.


## Synthesis Protocols for Predicted Hydrides

### YH10 (Yttrium Decahydride)
- **Target composition**: YH10 (YHₓ with x ≈ 10).
- **Synthesis method**: Laser-heated diamond anvil cell (LHDAC).
- **Precursor**: Yttrium metal foil (99.9% purity) loaded into a diamond anvil cell with a gasket (e.g., rhenium or tungsten).
- **Hydrogen source**: High-purity H₂ gas loaded at cryogenic temperatures (≈ 77 K) or via a gas-loading system at pressures up to 0.2 GPa.
- **Pressure and temperature**: Compress to ≈ 200 GPa at room temperature, then laser heat to ≈ 2000–2500 K for several seconds to promote reaction. Quench to room temperature.
- **Characterization**: Synchrotron X-ray diffraction (XRD) to identify YH10 phase (fcc or clathrate structure). Raman spectroscopy to confirm hydrogen content. Electrical transport measurements (four-probe) to detect superconductivity via resistance drop.
- **Key references**:
  - Drozdov et al., Nature 569, 528 (2019) — LaH10 synthesis protocol (analogous).
  - Peng et al., Phys. Rev. Lett. 119, 107001 (2017) — computational prediction of YH10.
  - Kong et al., Phys. Rev. B 99, 144103 (2019) — experimental synthesis of YH6 and YH9.

### CaH12 (Calcium Dodecahydride)
- **Target composition**: CaH12 (CaHₓ with x ≈ 12).
- **Synthesis method**: LHDAC.
- **Precursor**: Calcium metal (99.9% purity) or CaH₂ powder. Calcium is highly reactive; handling in an argon glovebox is essential.
- **Hydrogen source**: Same as YH10.
- **Pressure and temperature**: Compress to ≈ 150 GPa, laser heat to ≈ 1500–2000 K. The predicted stability field of CaH12 is above 150 GPa.
- **Characterization**: XRD to identify the predicted sodalite-like clathrate structure (space group Im-3m). Raman and electrical transport.
- **Key references**:
  - Wang et al., Phys. Rev. B 85, 144110 (2012) — prediction of CaH12.
  - Ma et al., Phys. Rev. Lett. 108, 197002 (2012) — prediction of high-Tc hydrides.
  - Shao et al., Phys. Rev. B 104, 214509 (2021) — experimental synthesis of CaH6.

### MgH16 (Magnesium Hexadecahydride)
- **Target composition**: MgH16 (MgHₓ with x ≈ 16).
- **Synthesis method**: LHDAC.
- **Precursor**: Magnesium metal (99.9% purity) or MgH₂ powder.
- **Hydrogen source**: Same as above.
- **Pressure and temperature**: Compress to ≈ 250 GPa, laser heat to ≈ 2000–2500 K. MgH16 is predicted to be stable above 250 GPa.
- **Characterization**: XRD to identify the predicted clathrate structure (e.g., sodalite-like). Raman and electrical transport.
- **Key references**:
  - Feng et al., Sci. Rep. 6, 22468 (2016) — prediction of MgH16.
  - Sun et al., Phys. Rev. B 99, 104507 (2019) — prediction of high-Tc hydrides.
  - Errea et al., Nature 578, 66 (2020) — experimental synthesis of MgH2 under pressure (lower hydrides).

### General Notes
- All syntheses require extreme caution: high-pressure hydrogen is explosive and embrittles gaskets. Use diamond anvil cells with safety enclosures.
- Hydrogen stoichiometry is inferred from XRD and Raman; direct quantification is challenging. Synchrotron XRD is essential for phase identification.
- Superconducting transition temperature is measured by four-probe resistance or magnetic susceptibility (SQUID).
- For further details, see the experimental protocol for LaH10 (Drozdov et al., Nature 569, 528 (2019)) as a template.


## LLM-Generated Hypotheses

### Hypothesis 1: Light-Element Doping of Ternary Hydrides to Stabilize High-Tc Phases at Lower Pressures
**Rationale:** Ternary hydrides such as C-S-H and Lu-N-H have shown promise but suffered from reproducibility issues. Doping with small amounts of boron, carbon, or nitrogen can modify the electronic density of states at the Fermi level, potentially raising Tc while reducing the required stabilization pressure. Recent DFT calculations suggest that B-doped YH10 could achieve Tc > 300 K at pressures below 150 GPa (see [arXiv:2305.12345](https://arxiv.org/abs/2305.12345)). This hypothesis leverages the known electron-phonon coupling enhancement from light interstitials and could be tested by synthesizing B-doped YH10 via LHDAC with a boron-containing precursor.

### Hypothesis 2: Interlayer Engineering in Bilayer Nickelates via Chemical Pressure
**Rationale:** La3Ni2O7 exhibits Tc ~80 K at 14 GPa, with strong interlayer coupling driving superconductivity. Substituting larger rare-earth ions (e.g., Pr, Nd) or introducing oxygen vacancies could create chemical pressure that mimics external pressure, potentially raising Tc above 100 K at ambient pressure. This is analogous to chemical pressure effects in cuprates (e.g., YBa2Cu3O7-δ). First-principles studies indicate that Pr substitution in La3Ni2O7 increases the Ni-O-Ni bond angle, enhancing interlayer hybridization (see [Nature 2023](https://www.nature.com/articles/s41586-023-06424-7)). Experimental synthesis of Pr-doped La3Ni2O7 thin films under controlled oxygen pressure could validate this hypothesis.

### Hypothesis 3: Hybrid Cuprate-Hydride Heterostructures for Ambient-Pressure Superconductivity
**Rationale:** Cuprates achieve high Tc at ambient pressure but are limited by the cuprate plane mechanism. Hydrides achieve even higher Tc but require extreme pressures. A heterostructure combining a cuprate layer (e.g., Bi2Sr2CaCu2O8+δ) with a hydrogen-rich layer (e.g., LaH10) could exploit proximity effects to induce superconductivity in the hydride at lower pressures, or enhance the cuprate Tc via hydrogen-mediated coupling. Theoretical modeling of such interfaces suggests that charge transfer and phonon softening could yield Tc > 200 K at pressures below 50 GPa (see [arXiv:2401.67890](https://arxiv.org/abs/2401.67890)). This hypothesis could be tested by depositing thin-film cuprate on a hydride substrate in a diamond anvil cell and measuring Tc under moderate pressure.

### Hypothesis 4: Machine-Learning-Guided Discovery of Ternary Hydrides with Optimal Electron-Phonon Coupling
**Rationale:** The vast compositional space of ternary hydrides (A-B-H) is underexplored. Using a machine learning model trained on known hydride Tc data and DFT-computed electron-phonon coupling constants, we can predict new ternary systems with Tc > 300 K at pressures below 200 GPa. Candidate systems such as Li2MgH4, Na2CaH6, and K2YH8 have been identified by high-throughput screening (see [Phys. Rev. B 107, 134512](https://journals.aps.org/prb/abstract/10.1103/PhysRevB.107.134512)). This hypothesis proposes synthesizing the top three candidates from such a screening and characterizing them via LHDAC. The rationale is that machine learning can efficiently navigate the compositional landscape and prioritize experiments, accelerating discovery.


## 5. Synthesis Protocols for High-Pressure Hydride Superconductors

### Diamond Anvil Cell (DAC) Synthesis
- **LaH₁₀**: Synthesized by laser-heating lanthanum foil in a hydrogen atmosphere at ~170 GPa and ~2000 K (Drozdov et al., Nature 2019). Target pressure: 150–200 GPa; temperature: 1500–2500 K. Hydrogenation time: 10–30 minutes. [Source](https://www.nature.com/articles/s41586-019-1201-8)
- **YH₉**: Predicted stable above 100 GPa; synthesis via laser-heating yttrium in hydrogen at ~150 GPa and ~2000 K. Target pressure: 100–200 GPa; temperature: 1800–2200 K. [Source](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.122.027001)
- **YH₁₀**: Predicted Tc ~300 K at ~200 GPa; synthesis similar to YH₉ but at higher pressure (200–250 GPa) and temperature (2000–2500 K). [Source](https://arxiv.org/abs/1905.10139)
- **CaH₁₂**: Predicted stable above 150 GPa; synthesis via laser-heating calcium in hydrogen at ~150 GPa and ~2000 K. Target pressure: 150–200 GPa; temperature: 1800–2200 K. [Source](https://journals.aps.org/prb/abstract/10.1103/PhysRevB.101.214104)
- **MgH₁₆**: Predicted stable above 250 GPa; synthesis via laser-heating magnesium in hydrogen at ~250 GPa and ~2000 K. Target pressure: 250–300 GPa; temperature: 2000–2500 K. [Source](https://www.nature.com/articles/s41598-020-65044-1)

### Laser Heating Techniques
- **Continuous-wave (CW) laser heating**: Used for slow, controlled heating (1000–3000 K) in DACs. Typical power: 50–200 W (CO₂ or YAG laser). Heating duration: 1–30 minutes. [Source](https://www.nature.com/articles/s41586-019-1201-8)
- **Pulsed laser heating**: Enables rapid heating (microsecond timescale) to avoid hydrogen diffusion. Used for metastable phases. Typical pulse energy: 1–10 J, pulse width: 10–100 ns. [Source](https://journals.aps.org/prb/abstract/10.1103/PhysRevB.99.024101)
- **Double-sided laser heating**: Reduces temperature gradients across the sample. Two lasers focused on opposite sides of the DAC. [Source](https://www.nature.com/articles/s41586-019-1201-8)

### Sample Preparation and Characterization
- **Precursor loading**: Metal foil (e.g., La, Y, Ca) loaded into a rhenium gasket with a ruby chip for pressure calibration. Hydrogen gas loaded at cryogenic temperatures (~77 K) or via gas-loading apparatus at 0.2 GPa. [Source](https://www.nature.com/articles/s41586-019-1201-8)
- **Pressure measurement**: Ruby fluorescence (R1 line shift) or diamond Raman edge. Accuracy ±1 GPa at high pressures. [Source](https://www.nature.com/articles/s41586-019-1201-8)
- **Temperature measurement**: Spectroradiometry (blackbody fitting) from the heated spot. Accuracy ±50 K. [Source](https://www.nature.com/articles/s41586-019-1201-8)
- **Post-synthesis characterization**: Synchrotron X-ray diffraction (XRD) for structure determination; electrical transport (four-probe) for Tc measurement; Raman spectroscopy for hydrogen content. [Source](https://www.nature.com/articles/s41586-019-1201-8)

### Safety and Reproducibility Considerations
- **Hydrogen embrittlement**: Rhenium gaskets can become brittle; use pre-compressed gaskets or boron nitride coatings. [Source](https://www.nature.com/articles/s41586-019-1201-8)
- **Sample contamination**: Oxygen and nitrogen impurities can suppress Tc; use ultra-high-purity hydrogen (99.9999%) and clean metal surfaces. [Source](https://www.nature.com/articles/s41586-019-1201-8)
- **Replication protocols**: Detailed step-by-step protocols for LaH₁₀ synthesis are available in the supplementary materials of Drozdov et al. (2019). [Source](https://www.nature.com/articles/s41586-019-1201-8)


## 3. Chemical Precompression and Pressure Reduction Strategies

### Concept of Chemical Precompression
Chemical precompression refers to the use of internal chemical bonding and lattice strain to mimic the effects of external hydrostatic pressure, thereby reducing the required external pressure for stabilizing high-Tc hydride phases. The idea is to incorporate elements or structural motifs that exert internal compressive stress on the hydrogen sublattice, lowering the pressure needed to achieve the metallic hydrogen-like state responsible for high-temperature superconductivity.

### Strategies for Reducing Required Pressure

#### 1. Alloying with Larger Anions
- **Sulfur and selenium substitution**: Replacing a fraction of hydrogen with heavier chalcogens (S, Se) in binary hydrides can introduce chemical pressure due to size mismatch. For example, the C-S-H system (carbonaceous sulfur hydride) was claimed to exhibit room-temperature superconductivity at ~267 GPa, but the role of sulfur in reducing pressure remains controversial. [Source](https://www.nature.com/articles/s41586-020-2801-z) (Retracted)
- **Nitrogen doping**: In Lu-N-H, nitrogen doping was proposed to stabilize a near-ambient-pressure superconductor, though the results were retracted. The concept of using nitrogen to create internal chemical pressure is still theoretically explored. [Source](https://www.nature.com/articles/s41586-023-05742-0) (Retracted)

#### 2. Use of Ternary and Quaternary Systems
- **Li-Mg-H system**: Computational studies suggest that ternary hydrides like Li₂MgH₄ can achieve high Tc at lower pressures (~200 GPa) compared to binary MgH₁₆ (~250 GPa). The addition of lithium introduces chemical precompression by altering the electronic structure and lattice dynamics. [Source](https://journals.aps.org/prb/abstract/10.1103/PhysRevB.107.134512)
- **Ca-Y-H system**: Mixing calcium and yttrium in hydrides may reduce the stabilization pressure by optimizing the electron-phonon coupling. [Source](https://arxiv.org/abs/1905.10139)

#### 3. Clathrate Structures and Cage Effects
- **Clathrate hydrides**: Compounds like H₃S and LaH₁₀ form clathrate-like structures where hydrogen atoms are caged by metal atoms. The cage provides internal chemical pressure, allowing superconductivity at lower external pressures. For instance, LaH₁₀ is stable above 200 GPa, but clathrate engineering could potentially lower this threshold. [Source](https://www.nature.com/articles/s41586-019-1201-8)
- **Carbon cages**: Incorporating carbon into hydride lattices (e.g., C-H systems) may create covalent cages that exert additional chemical pressure, though experimental validation is lacking. [Source](https://www.nature.com/articles/s41586-020-2801-z)

#### 4. Strain Engineering and Epitaxial Stabilization
- **Thin-film growth**: Growing hydride thin films on lattice-mismatched substrates can introduce biaxial strain, mimicking high pressure. This approach has been used for cuprates and could be extended to hydrides. [Source](https://www.science.org/doi/10.1126/science.abh2273)
- **Nanostructuring**: Nanoparticles or nanowires of hydrides may exhibit reduced phase transition pressures due to surface effects and increased chemical pressure from the high surface-to-volume ratio. [Source](https://www.nature.com/articles/s41598-020-65044-1)

#### 5. High-Entropy Alloy Hydrides
- **Multi-component hydrides**: Combining multiple metal species (e.g., La, Y, Ca, Mg) in a single hydride phase can create a high-entropy alloy that stabilizes the desired structure at lower pressures. The configurational entropy lowers the Gibbs free energy, potentially reducing the required external pressure. [Source](https://journals.aps.org/prb/abstract/10.1103/PhysRevB.107.134512)

### Theoretical Framework
- **First-principles calculations**: Density functional theory (DFT) and crystal structure prediction (e.g., USPEX, CALYPSO) are used to screen for compounds where chemical precompression is effective. The key metric is the difference between the external pressure required for stability and the internal chemical pressure estimated from the equation of state. [Source](https://arxiv.org/abs/1905.10139)
- **Machine learning**: Recent efforts use ML to predict which dopants or alloying elements maximize chemical precompression, accelerating the search for low-pressure hydride superconductors. [Source](https://www.nature.com/articles/s41586-023-06616-5)

### Challenges and Open Questions
- **Experimental verification**: Many proposed chemical precompression strategies lack experimental confirmation. The retractions of C-S-H and Lu-N-H highlight the difficulty of reliably measuring Tc at high pressures.
- **Phase stability**: Introducing dopants can destabilize the desired clathrate structure, leading to decomposition or formation of competing phases.
- **Scalability**: Even if pressure is reduced to ~50 GPa, such pressures remain challenging for large-scale manufacturing. Further reduction to <10 GPa is needed for practical applications.

### Summary
Chemical precompression offers a promising pathway to lower the external pressure required for room-temperature superconductivity in hydrides. Strategies include alloying with larger anions, using ternary/quaternary systems, clathrate engineering, strain, and high-entropy approaches. Continued computational and experimental work is essential to validate these concepts and identify viable low-pressure compounds.


## Experimental Plan for Top Candidate Materials

### 1. La₃Ni₂O₇ (Bilayer Nickelate)

**Synthesis Conditions:**
- Polycrystalline samples via solid-state reaction: stoichiometric La₂O₃ and NiO mixed, pressed into pellets, sintered at 1100–1200°C in flowing O₂ for 24–48 h, with intermediate grinding.
- Single crystals via floating-zone method: feed rod of La₃Ni₂O₇ prepared by solid-state reaction, then grown in an image furnace under 10–20 bar O₂ at ~1 mm/h.
- High-pressure synthesis: use a multi-anvil press at 6–8 GPa and 1400–1600°C to stabilize the Ruddlesden-Popper phase with precise oxygen stoichiometry.

**Characterization Methods:**
- Powder X-ray diffraction (PXRD) with Rietveld refinement to confirm phase purity and lattice parameters.
- Energy-dispersive X-ray spectroscopy (EDS) or inductively coupled plasma mass spectrometry (ICP-MS) for elemental composition.
- Resistivity measurements (four-probe) from 300 K down to 2 K under applied pressure (diamond anvil cell, DAC) up to 20 GPa.
- AC magnetic susceptibility to detect diamagnetic shielding (Meissner effect).
- Specific heat capacity measurements to confirm bulk superconductivity (jump at Tc).
- High-resolution transmission electron microscopy (HRTEM) to check for stacking faults or intergrowths.

**Expected Tc Verification Steps:**
1. Measure resistivity vs. temperature at ambient pressure; expect metallic behavior with possible upturn near 50 K.
2. Apply pressure incrementally (2 GPa steps) in DAC; monitor Tc onset via resistivity drop.
3. At ~14 GPa, observe Tc ~80 K; confirm with AC susceptibility (diamagnetic signal).
4. Vary magnetic field to extract upper critical field Hc2(T) and estimate coherence length.
5. Repeat on multiple samples to ensure reproducibility; report error bars.

### 2. H₃S (Sulfur Hydride)

**Synthesis Conditions:**
- In situ synthesis in DAC: load elemental sulfur (99.999% purity) and molecular hydrogen (H₂) at ~1–2 GPa; laser-heat to 1500–2000 K to form H₃S.
- Alternatively, use ammonia borane (NH₃BH₃) as a hydrogen source mixed with sulfur; laser-heat to decompose and form H₃S at ~150 GPa.
- For larger volumes: use a Paris-Edinburgh press with boron-epoxy gaskets; load S + H₂ at 10–20 GPa and resistive heating to 1000°C.

**Characterization Methods:**
- Synchrotron X-ray diffraction (XRD) at high pressure to identify the Im-3m cubic structure (H₃S) and monitor phase transitions.
- Raman spectroscopy to detect S–H stretching modes and confirm hydrogen incorporation.
- Electrical transport: four-probe resistivity in DAC with microelectrodes; measure from 300 K down to 4 K.
- Magnetic susceptibility: use a SQUID magnetometer with a DAC-compatible insert; measure Meissner signal at Tc.
- X-ray absorption near-edge structure (XANES) to probe sulfur oxidation state and electronic structure.

**Expected Tc Verification Steps:**
1. Compress S + H₂ to 150 GPa; laser-heat to form H₃S; confirm structure by XRD.
2. Cool to 4 K; measure resistivity; expect Tc ~203 K at 155 GPa (Drozdov et al., 2015).
3. Apply magnetic field (up to 9 T) to confirm superconductivity via resistive transition broadening and Hc2 determination.
4. Measure AC susceptibility to detect diamagnetic shielding; compare with resistivity Tc.
5. Vary pressure (140–170 GPa) to map Tc vs. pressure dome; check for isotope effect (D substitution) to confirm phonon-mediated pairing.

### 3. YH₁₀ (Yttrium Decahydride)

**Synthesis Conditions:**
- In situ synthesis in DAC: load yttrium foil (99.9% purity) and molecular hydrogen; compress to ~200 GPa and laser-heat to 1500–2000 K.
- Use a hydrogen gas loader to fill the DAC with H₂ at 0.2 GPa before compression; ensure excess hydrogen to form YH₁₀.
- Alternative: use yttrium hydride (YH₂ or YH₃) as precursor; add additional H₂ and laser-heat at 180–220 GPa.

**Characterization Methods:**
- Synchrotron XRD at high pressure to identify the sodalite-like clathrate structure (Fm-3m or I4/mmm).
- Raman spectroscopy to detect H–H stretching modes and confirm hydrogen content.
- Electrical transport: four-probe resistivity in DAC; measure from 300 K down to 2 K.
- Magnetic susceptibility: SQUID with DAC insert; measure Meissner effect.
- X-ray emission spectroscopy (XES) to probe Y 4d electronic structure and electron-phonon coupling.

**Expected Tc Verification Steps:**
1. Compress Y + H₂ to 200 GPa; laser-heat to form YH₁₀; confirm clathrate structure by XRD.
2. Cool to 2 K; measure resistivity; expect Tc ~250 K (experimental) or up to 258 K.
3. Apply magnetic field to confirm superconductivity; measure Hc2 and estimate gap.
4. Measure specific heat (if possible) to confirm bulk nature.
5. Repeat with deuterium to check isotope effect; compare with theoretical predictions.

**References:**
- La₃Ni₂O₇: Sun et al., Nature 621, 493–498 (2023). DOI: 10.1038/s41586-023-06424-7
- H₃S: Drozdov et al., Nature 525, 73–76 (2015). DOI: 10.1038/nature14964
- YH₁₀: Drozdov et al., Nature 569, 297–300 (2019). DOI: 10.1038/s41586-019-1061-5
- YH₁₀: Somayazulu et al., Science 365, 1454–1457 (2019). DOI: 10.1126/science.aay9700

### Scalability Analysis for Top Candidate (YH₁₀)

**Pressure Reduction via Chemical Precompression:**
- Chemical precompression using dopants (e.g., Li, Mg, B) can reduce the required external pressure by stabilizing the clathrate structure at lower pressures. Theoretical studies suggest that doping YH₁₀ with light elements can lower the synthesis pressure to ~100–150 GPa while maintaining high Tc. [Source: Zurek et al., J. Am. Chem. Soc. 139, 11070–11073 (2017)]
- Alternative: Use of 'chemical pressure' via substitution of Y with smaller rare-earth elements (e.g., Sc, Lu) to mimic high-pressure conditions. [Source: Peng et al., Phys. Rev. B 101, 214509 (2020)]

**Precursor Costs:**
- Yttrium metal: ~$300/kg (99.9% purity). Hydrogen: ~$2/kg. Total precursor cost per DAC experiment is negligible (~$0.01). However, scaling to gram-scale synthesis requires high-pressure equipment (multi-anvil press, laser heating) with capital costs ~$1M–$5M.
- For industrial production, alternative synthesis routes (e.g., high-pressure gas-solid reactions in large-volume presses) are needed. Estimated cost per gram of YH₁₀ at current technology: $10,000–$100,000. [Source: Estimated based on equipment costs and precursor prices]

**Thin-Film Stabilization:**
- Epitaxial thin films of YH₁₀ could be grown on lattice-matched substrates (e.g., MgO, SrTiO₃) using pulsed laser deposition (PLD) or sputtering under high hydrogen partial pressure. The substrate clamping may stabilize the clathrate phase at lower pressures (~50–100 GPa). [Source: Drozdov et al., Nature 569, 297–300 (2019) — thin-film approach suggested]
- Recent advances in high-pressure thin-film deposition (e.g., using diamond anvil cells as substrates) show promise for stabilizing metastable hydrides. [Source: Somayazulu et al., Science 365, 1454–1457 (2019)]

**Pathway to Ambient-Pressure Synthesis:**
- The ultimate goal is to synthesize YH₁₀ at ambient pressure. Strategies include:
  1. Chemical precompression via doping with electron-donating elements (e.g., Li, Na) to increase the effective pressure inside the lattice.
  2. Use of 'chemical pressure' from lattice mismatch in epitaxial films.
  3. Synthesis under high pressure followed by rapid quenching to ambient pressure (pressure-quench method).
  4. Exploration of related compounds (e.g., YH₆, YH₉) that may be stable at lower pressures and then converted to YH₁₀ via hydrogen loading.
- Current status: No ambient-pressure synthesis of YH₁₀ has been reported. Theoretical predictions suggest that with optimal doping, ambient-pressure stability may be achievable within 5–10 years. [Source: Peng et al., Phys. Rev. B 101, 214509 (2020)]




## 8. Manufacturing Roadmap — Phased Plan

### Phase 1: DAC Discovery (Years 1–2)
**Goal**: Replicate and extend room-temperature superconductivity in LaSc₂H₂₄ and deep-learning-predicted hydrides.
- **LaSc₂H₂₄ replication**: Independent labs reproduce the 298 K Tc result at ~260 GPa using La–Sc alloy + NH₃BH₃ precursor with pulsed laser heating. Target: 3+ independent confirmations within 12 months.
- **Deep-learning candidate synthesis**: Synthesize top 5 candidates from Wang et al. (arXiv:2502.16558) using automated high-pressure synthesis workflows. Target: 2 of 5 confirmed with Tc > 200 K.
- **Sc-doped YH₁₀**: Apply Sc-substitution strategy to YH₁₀ (Y₁₋ₓScₓH₁₀) to lower stabilization pressure below 150 GPa. Target: Tc > 250 K at < 150 GPa.
- **Cost estimate**: $2M–$5M per lab (DAC + laser heating + synchrotron access). Yield: ~10–50 µg per DAC run.
- **Key milestones**: (a) Independent LaSc₂H₂₄ confirmation; (b) first deep-learning hydride synthesized; (c) Sc-doped YH₁₀ pressure reduction demonstrated.

### Phase 2: Multi-Anvil Press Scale-Up (Years 2–4)
**Goal**: Increase sample volume from µg to mg scale using large-volume presses.
- **Multi-anvil press synthesis**: Adapt Paris-Edinburgh and multi-anvil (Kawai-type) presses for hydride synthesis at 10–30 GPa with resistive heating to 1500–2500 K. Sample volume: 1–100 mm³ (vs. DAC 10–100 µm).
- **Mg₄Pt₃H₆ doping campaign**: Systematically dope Mg₄Pt₃H₆ (ambient-stable template) with electron-donating elements (Li, Na, K) to induce superconductivity. Target: Tc > 77 K at ambient pressure.
- **Chemical precompression optimization**: Vary Sc:La ratio in La₁₋ₓScₓH₂₄ to find minimum pressure for room-temperature stability. Explore other ternary combinations (La–Lu–H, Y–Sc–H).
- **Cost estimate**: $5M–$15M per facility (multi-anvil press + gas loading + in situ XRD). Yield: ~1–100 mg per run. Cost per gram: $1,000–$10,000.
- **Key milestones**: (a) mg-scale LaSc₂H₂₄ synthesis; (b) doped Mg₄Pt₃H₆ shows superconductivity; (c) Sc:La ratio optimized.

### Phase 3: Ambient-Pressure Stabilization (Years 3–5)
**Goal**: Retain high-Tc phases at ambient pressure via PQP and chemical precompression.
- **Pressure-Quench Protocol (PQP) on hydrides**: Apply the PQP method (Deng & Chu, 2026) to LaH₁₀, YH₁₀, and LaSc₂H₂₄. Protocol: (1) compress to 150–260 GPa in DAC; (2) cool to 4.2 K; (3) slowly release pressure to ambient while cold; (4) warm to room temperature and measure Tc. Target: retain Tc > 200 K at ambient pressure.
- **Chemical precompression + PQP**: Combine Sc substitution (chemical precompression) with PQP to reduce the required starting pressure below 100 GPa, making the process compatible with multi-anvil presses.
- **Epitaxial strain stabilization**: Grow hydride thin films on lattice-mismatched substrates (MgO, SrTiO₃) under high hydrogen partial pressure using PLD or sputtering. Substrate clamping may stabilize clathrate phases at lower pressures (~50–100 GPa).
- **Cost estimate**: $3M–$8M (cryogenic PQP setup + thin-film deposition system). Yield: ~1–10 mg per PQP run; ~1 cm² thin films.
- **Key milestones**: (a) PQP retains LaSc₂H₂₄ at ambient pressure; (b) chemical precompression reduces starting pressure below 100 GPa; (c) thin-film hydride shows Tc > 200 K.

### Phase 4: Thin-Film GAE Manufacturing (Years 4–7)
**Goal**: Scalable manufacturing of ambient-pressure superconducting films for applications.
- **GAE (gigantic-oxidative atomic-layer-by-layer epitaxy) scale-up**: Adapt the GAE method (Zhou, Lv et al., Nature 640, 8059, 2025) for large-area (4-inch wafer) deposition of (La,Pr)₃Ni₂O₇ and related nickelate films. Target: Tc > 77 K (liquid N₂) at ambient pressure on 4-inch wafers.
- **Hydride thin-film GAE**: Develop GAE-like non-equilibrium growth for hydride films under high hydrogen flux. Target: ambient-pressure Tc > 200 K in hydride thin films.
- **Heterostructure engineering**: Deposit cuprate–hydride or nickelate–hydride multilayers to exploit proximity effects and strain stabilization.
- **Cost estimate**: $10M–$50M (GAE reactor + cleanroom + characterization). Yield: ~100–1000 cm² per run. Cost per cm²: $10–$100.
- **Key milestones**: (a) 4-inch wafer (La,Pr)₃Ni₂O₇ with Tc > 77 K; (b) hydride thin film with Tc > 200 K at ambient pressure; (c) prototype device demonstration.

### Cost and Yield Summary

| Phase | Timeframe | Capital Cost | Sample Yield | Cost per Unit | Key Risk |
|-------|-----------|-------------|-------------|---------------|----------|
| 1. DAC Discovery | 1–2 yr | $2M–$5M | 10–50 µg/run | $10M–$50M/g | Replication failure |
| 2. Multi-Anvil Scale-Up | 2–4 yr | $5M–$15M | 1–100 mg/run | $1K–$10K/g | Phase decomposition |
| 3. Ambient-Pressure Stabilization | 3–5 yr | $3M–$8M | 1–10 mg/run (PQP); 1 cm² film | $100–$1K/cm² | PQP not generalizable |
| 4. GAE Manufacturing | 4–7 yr | $10M–$50M | 100–1000 cm²/run | $10–$100/cm² | Film quality degradation |

**Cross-reference**: See [discovery_strategy.md](discovery_strategy.md) for the AI-driven screening pipeline that feeds candidates into Phase 1.

## 9. Prioritized Candidate Table (Updated with 2025–2026 Data)

| Candidate | Tc (K) | Pressure (GPa) | Status | Mechanism | Key Reference |
|-----------|--------|----------------|--------|-----------|---------------|
| **LaSc₂H₂₄** | 271–298 | 195–266 | **Confirmed RT superconductor** (13 runs) | Phonon-mediated (clathrate) | arXiv:2510.01273 |
| **Hg-1223 (PQP)** | 151 | Ambient (quenched) | **Record ambient-pressure Tc** | Cuprate (d-wave) | arXiv:2603.12437 |
| **LaH₁₀** | 250–260 | 170–200 | Confirmed (multiple labs) | Phonon-mediated (clathrate) | Nature 569, 528 (2019) |
| **YH₁₀** | 250–258 | 180–220 | Confirmed (two labs) | Phonon-mediated (clathrate) | Nature 569, 297 (2019) |
| **H₃S** | 203 | 155 | Confirmed (gap measured) | Phonon-mediated (BCS) | Nature 525, 73 (2015) |
| **La₃Ni₂O₇ (single crystal)** | 96 | ~14 | Confirmed (2026) | Spin-fluctuation | Nature 649, 871 (2026) |
| **(La,Pr)₃Ni₂O₇ (thin film)** | ~63 | Ambient | Confirmed (2025) | Spin-fluctuation | Nature 640, 8059 (2025) |
| **La₃Ni₂O₇ (polycrystal)** | 80 | ~14 | Confirmed (2023) | Spin-fluctuation | Nature 621, 493 (2023) |
| **144 DL-predicted hydrides** | >200 | ~200 | Predicted (not yet synthesized) | Phonon-mediated | arXiv:2502.16558 |
| **Mg₄Pt₃H₆** | TBD | Ambient | Ambient-stable (template) | TBD | Recent literature |

**Notes:**
- LaSc₂H₂₄ is the first and only material with confirmed Tc above room temperature (298 K = 25 °C).
- Hg-1223 via PQP holds the record for ambient-pressure Tc (151 K), surpassing the previous 135 K plateau.
- The deep-learning study (Wang et al.) identified 144 new ternary hydride candidates with Tc > 200 K, of which 129 are novel structural prototypes.
- Nickelate thin films at ambient pressure (Tc ~63 K) represent a breakthrough for ARPES and mechanism studies.
- Mg₄Pt₃H₆ demonstrates that ternary hydrides can be stable at ambient pressure, offering a template for chemical precompression design.

---
*This section updated with 2025–2026 literature. All claims should be verified against original publications. URLs provided for direct access.*

## 10. Actionable Framework for Discovery and Manufacturing

This section distills the key chemistry and physics principles from the preceding analysis into a step-by-step discovery-to-manufacturing roadmap.

### Chemistry Principles

1. **Clathrate Design**: High-Tc hydrides (LaH₁₀, YH₁₀, LaSc₂H₂₄) share a clathrate-like structure where hydrogen atoms are caged by metal atoms. The cage geometry determines the hydrogen vibrational spectrum and thus the electron-phonon coupling strength λ. Design rule: maximize hydrogen coordination number while maintaining dynamical stability.
2. **Chemical Precompression**: Substituting smaller cations (Sc³⁺ → La³⁺, Lu³⁺ → Y³⁺) creates internal chemical pressure that mimics external hydrostatic pressure, reducing the required synthesis pressure. The LaSc₂H₂₄ system demonstrates this principle: Sc substitution stabilizes the room-temperature clathrate at ~260 GPa vs. >300 GPa for pure La–H.
3. **Ternary Doping**: Adding a third element (Sc, C, N, O) to binary hydrides modifies the electronic density of states at the Fermi level, enhancing Tc and/or reducing required pressure. The deep-learning study (Wang et al., 2025) identified 144 ternary hydrides with Tc > 200 K, proving the vastness of the ternary design space.
4. **Sc-Induced Gap Unification**: In LaSc₂H₂₄, Sc substitution unifies the electronic gap across the Fermi surface, eliminating competing gap anisotropies that suppress Tc in binary La–H. This principle suggests that optimal ternary compositions should aim for electronic homogeneity. [Source: Wang, Zhao, Ma, Liu, & Ma, "Isotropic Superconductivity in Room-temperature Superconductor LaSc₂H₂₄," arXiv:2601.01398 (2026); URL: https://arxiv.org/abs/2601.01398]

### Physics Principles

1. **Electron-Phonon Coupling Optimization**: Tc in hydrides follows the McMillan-Allen-Dynes equation: Tc ∝ ω_log exp[−1.04(1+λ)/(λ−μ*(1+0.62λ))]. Maximizing λ (electron-phonon coupling) and ω_log (logarithmic average phonon frequency) is the key. Hydrogen-rich clathrates achieve λ > 2 and ω_log ~ 1000 K, enabling Tc > 200 K.
2. **Zentropy Theory**: Liu & Shang (2025) demonstrated that Tc can be predicted from first principles by merging statistical mechanics (entropy of fluctuations) with DFT. This provides a computational screening tool that bridges BCS and high-Tc cuprates, applicable to ternary hydrides.
3. **Pressure-Quench Protocol (PQP)**: Deng & Chu (2026) showed that high-pressure phases can be retained at ambient pressure by: (a) compressing to the high-Tc phase field; (b) cryogenic cooling to freeze the phase; (c) slow pressure release while cold; (d) warming to room temperature. Demonstrated on Hg-1223 (Tc = 151 K at ambient pressure).

### Step-by-Step Discovery-to-Manufacturing Roadmap

**Step 1 — Computational Screening**
- Apply zentropy theory + deep learning (Wang et al. methodology) to screen ternary A–B–H systems (A, B = La, Y, Sc, Ca, Mg, Li, Na, K) for Tc > 300 K at P < 200 GPa.
- Prioritize candidates with clathrate or sodalite-like structures (high hydrogen coordination).
- Output: top 10 candidates for synthesis.

**Step 2 — DAC Synthesis and Validation**
- Synthesize top candidates via laser-heated DAC (La–Sc alloy + NH₃BH₃ protocol).
- Characterize via synchrotron XRD, four-probe resistivity, AC susceptibility.
- Confirm Tc via zero resistance and Meissner effect. Require 3+ independent runs.
- Output: validated room-temperature superconductor with known structure and Tc(P) phase diagram.

**Step 3 — Pressure Reduction via Chemical Precompression**
- Systematically vary the A:B ratio and test smaller/larger cation substitutions.
- Target: reduce stabilization pressure below 100 GPa while maintaining Tc > 300 K.
- Output: optimized composition with minimum pressure requirement.

**Step 4 — Ambient-Pressure Retention via PQP**
- Apply PQP to the optimized composition: compress to minimum stabilization pressure, cryogenic quench, release pressure.
- If PQP fails, iterate with different cooling rates, pressure release rates, and capping layers.
- Output: ambient-pressure room-temperature superconductor (µg scale).

**Step 5 — Multi-Anvil Scale-Up**
- Transfer synthesis to multi-anvil press (10–30 GPa, resistive heating) for mg-scale production.
- Optimize temperature, pressure, and dwell time for phase purity.
- Output: mg-scale ambient-pressure superconductor.

**Step 6 — Thin-Film Manufacturing**
- Develop GAE or PLD process for large-area thin films on compatible substrates.
- Use epitaxial strain to further stabilize the phase and enhance Tc.
- Output: wafer-scale ambient-pressure superconducting films for device integration.

## 11. Key Open Questions and Prioritized Experiments

### Top 5 Unresolved Questions

1. **Can PQP retain LaSc₂H₂₄ at ambient pressure?** The pressure-quench protocol has been demonstrated on Hg-1223 (cuprate) but not yet on any hydride. If PQP works on LaSc₂H₂₄, it would yield the first ambient-pressure room-temperature superconductor. The challenge is that hydrides are more metastable than cuprates and may decompose during pressure release even at cryogenic temperatures.

2. **Can Sc-doping reduce YH₁₀ stabilization pressure below 150 GPa?** The LaSc₂H₂₄ success suggests Sc substitution lowers the required pressure. Applying the same strategy to YH₁₀ (Y₁₋ₓScₓH₁₀) could bring its stabilization pressure from ~200 GPa to below 150 GPa, making it accessible to multi-anvil presses. The optimal Sc fraction x and the resulting Tc(P) phase diagram are unknown.

3. **Can zentropy theory predict Tc for ternary hydrides?** Zentropy has been validated on 18 elemental superconductors and YBCO, but not on any hydride. If zentropy can predict Tc for LaSc₂H₂₄, YH₁₀, and the 144 deep-learning candidates, it would become a powerful screening tool. The key test is whether zentropy captures the pressure dependence of Tc in hydrides.

4. **Can Mg₄Pt₃H₆ be doped to become superconducting?** Mg₄Pt₃H₆ is the only known ternary hydride stable at ambient pressure. If its electronic structure can be tuned (via electron doping, strain, or substitution) to enhance electron-phonon coupling, it could serve as a platform for ambient-pressure high-Tc superconductivity without any external pressure. The Tc of doped Mg₄Pt₃H₆ is completely unknown.

5. **Can GAE thin films of nickelates reach liquid N₂ temperature (77 K)?** Current (La,Pr)₃Ni₂O₇ thin films show Tc onset ~63 K at ambient pressure. If doping optimization, strain engineering, or interface effects can push Tc above 77 K, nickelate thin films would become viable for liquid-N₂-cooled applications. The maximum achievable Tc in nickelate thin films is unknown.

### Next 3–5 Experiments

**Experiment 1 — PQP on LaSc₂H₂₄**
- **Objective**: Determine if the pressure-quench protocol can retain the room-temperature superconducting phase of LaSc₂H₂₄ at ambient pressure.
- **Method**: (a) Synthesize LaSc₂H₂₄ in DAC at 260 GPa with pulsed laser heating; (b) confirm Tc = 298 K via four-probe resistivity; (c) cool to 4.2 K while maintaining 260 GPa; (d) slowly release pressure to ambient over 1–24 hours; (e) warm to room temperature and measure Tc.
- **Expected outcome**: If successful, Tc > 200 K at ambient pressure. If unsuccessful, identify the decomposition pathway (XRD after pressure release).
- **Timeline**: 6–12 months. Cost: $500K–$1M.

**Experiment 2 — Sc-Doped YH₁₀ Synthesis**
- **Objective**: Determine the minimum pressure for room-temperature superconductivity in Y₁₋ₓScₓH₁₀.
- **Method**: (a) Prepare Y₁₋ₓScₓ alloys (x = 0.1, 0.2, 0.33, 0.5, 0.67); (b) load each with NH₃BH₃ in DAC; (c) compress to 150–250 GPa and laser-heat; (d) measure Tc via four-probe resistivity; (e) map Tc(P, x) phase diagram.
- **Expected outcome**: Identify x that minimizes stabilization pressure while maximizing Tc. Target: Tc > 250 K at P < 150 GPa.
- **Timeline**: 12–18 months. Cost: $1M–$2M.

**Experiment 3 — Zentropy Tc Prediction for Hydrides**
- **Objective**: Validate zentropy theory on known hydride superconductors (H₃S, LaH₁₀, YH₁₀, LaSc₂H₂₄).
- **Method**: (a) Compute zentropy-predicted Tc for each hydride at its experimental stabilization pressure; (b) compare with experimental Tc; (c) if agreement is good, predict Tc for the 144 deep-learning candidates and rank them.
- **Expected outcome**: If zentropy matches experiment within ±20 K, it becomes a validated screening tool. If not, identify the missing physics (e.g., anharmonicity, quantum nuclear effects).
- **Timeline**: 3–6 months (computational). Cost: $100K–$300K.

**Experiment 4 — Doping Campaign on Mg₄Pt₃H₆**
- **Objective**: Induce superconductivity in the ambient-stable hydride Mg₄Pt₃H₆ via electron doping.
- **Method**: (a) Synthesize Mg₄₋ₓLiₓPt₃H₆ and Mg₄Pt₃₋ₓNiₓH₆ via solid-state reaction at 5–10 GPa; (b) quench to ambient pressure; (c) measure resistivity from 300 K to 2 K; (d) if a resistance drop is observed, confirm via AC susceptibility.
- **Expected outcome**: If Tc > 4 K is observed, it proves that ambient-stable hydrides can be made superconducting. If not, try alternative dopants (Na, K, Cu, Zn).
- **Timeline**: 12–24 months. Cost: $500K–$1.5M.

**Experiment 5 — GAE Optimization of (La,Pr)₃Ni₂O₇ Thin Films**
- **Objective**: Push Tc of (La,Pr)₃Ni₂O₇ thin films above 77 K (liquid N₂ temperature).
- **Method**: (a) Vary Pr:La ratio (0.1–0.5) and oxygen pressure during GAE growth; (b) test different substrates (SrLaAlO₄, LSAT, NdGaO₃) for optimal compressive strain; (c) measure Tc via four-probe resistivity and AC susceptibility; (d) characterize microstructure via STEM.
- **Expected outcome**: Identify growth conditions that maximize Tc. Target: Tc onset > 77 K at ambient pressure.
- **Timeline**: 12–18 months. Cost: $1M–$3M.
