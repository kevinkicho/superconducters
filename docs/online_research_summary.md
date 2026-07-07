# Online Research Summary: Room-Temperature Superconductivity

## Key Findings from Literature and Web Research

### 1. High-Pressure Hydrides (Highest Confirmed Tc)
- **LaH₁₀ (lanthanum decahydride)** under ~170 GPa shows Tc ~250 K (−23°C). This is the highest confirmed superconducting transition temperature to date.
  - Source: Drozdov et al., *Nature* 569, 528–531 (2019). [https://www.nature.com/articles/s41586-019-1201-8](https://www.nature.com/articles/s41586-019-1201-8)
- **YH₆, YH₉** (yttrium hydrides) also exhibit high Tc (~243 K at 201 GPa for YH₉).
  - Source: Kong et al., *Nature Communications* 12, 5075 (2021).
- **Carbonaceous sulfur hydride** (CSH) claimed Tc ~287 K at 267 GPa (Dias et al., *Nature* 586, 373–377, 2020) — **retracted** in 2022 due to data fabrication concerns.
  - Retraction notice: *Nature* 612, 388 (2022).

### 2. Retracted / Controversial Claims
- **LK-99 (Pb₁₀₋ₓCuₓ(PO₄)₆O)** — claimed room-temperature ambient-pressure superconductivity in July 2023. Multiple replication attempts failed; the observed diamagnetism and resistance drops are attributed to impurities (Cu₂S) and measurement artifacts.
  - Summary of replication failures: [https://www.nature.com/articles/d41586-023-02481-0](https://www.nature.com/articles/d41586-023-02481-0)
- **Dias et al. room-temperature claim** (CSH) retracted; the lead author was found to have fabricated data.

### 3. Promising Directions for Ambient-Pressure Room-Temperature Superconductivity
- **Ternary hydrides** (e.g., Li₂MgH₁₆, CaYH₁₂) predicted by crystal structure prediction (USPEX, CALYPSO) to have high Tc at lower pressures.
  - Source: Sun et al., *Physical Review Letters* 123, 097001 (2019).
- **Machine learning / high-throughput screening** for novel superhydrides and clathrate structures.
  - Source: Hutcheon et al., *Nature Communications* 11, 5577 (2020).
- **Dense hydrogen alloys** (e.g., H₃S, LaH₁₀) — the BCS-like mechanism with strong electron-phonon coupling is well established; the challenge is reducing the required pressure.
- **Electride superconductors** (e.g., Ca₂N, Y₂C) — possible ambient-pressure candidates with high Tc predicted.
  - Source: Pickard et al., *Physical Review B* 102, 214101 (2020).

### 4. Chemistry and Physics of Superconductivity
- **BCS theory**: Tc ∝ ω_D exp(-1/λ), where λ is electron-phonon coupling. High hydrogen content maximizes ω_D (light mass) and λ (strong coupling).
- **Pressure** stabilizes hydrogen-rich phases and metallizes hydrogen. Ambient-pressure synthesis requires chemical precompression (e.g., using rare-earth or alkaline-earth metals).
- **Doping** (e.g., hole or electron doping) can tune the Fermi level to enhance Tc.

### 5. Bilayer Nickelate La₃Ni₂O₇ (Tc ~80 K at 14 GPa)
- **La₃Ni₂O₇** is a bilayer Ruddlesden–Popper nickelate that becomes superconducting at ~80 K under ~14 GPa hydrostatic pressure (Sun et al., *Nature* 621, 493–498, 2023).
  - Source: [https://www.nature.com/articles/s41586-023-06424-7](https://www.nature.com/articles/s41586-023-06424-7)
- The compound crystallizes in a tetragonal structure (I4/mmm) at ambient pressure, with NiO₂ bilayers separated by La–O spacer layers.
- Pressure suppresses a density-wave-like transition near 120 K and induces superconductivity.
- The superconducting mechanism is debated; likely involves strong electron correlations and possibly spin fluctuations, with Ni 3d–O 2p hybridization.
- Confirmed by multiple groups, but sample synthesis (high-pressure floating zone) is challenging and oxygen non-stoichiometry can affect Tc.
- This material is a promising platform for exploring room-temperature superconductivity via chemical substitution (e.g., Sr, Ca) or epitaxial strain.

### 6. Manufacturing Challenges
- **High-pressure synthesis** (diamond anvil cells, multi-anvil presses) is not scalable. Current record Tc materials require >100 GPa.
- **Metastable retention** — some high-pressure phases can be quenched to ambient pressure (e.g., H₃S decomposes upon decompression).
- **Thin-film deposition** (e.g., MBE, PLD) may allow stabilization of metastable phases on substrates.

### 7. Conclusions and Open Questions
- No confirmed room-temperature ambient-pressure superconductor exists as of 2025.
- The hydride route is the most promising but requires pressure reduction by orders of magnitude.
- Machine learning and high-throughput DFT are accelerating discovery.
- Retracted claims highlight the need for rigorous replication and open data.

### 8. Cuprate High-Temperature Superconductors
- Cuprates (e.g., YBa₂Cu₃O₇, Bi₂Sr₂CaCu₂O₈) exhibit high Tc up to ~135 K at ambient pressure, but not room temperature.
- The mechanism is unconventional (d-wave pairing, spin fluctuations).
- Key references: Bednorz & Müller, Z. Phys. B 64, 189 (1986); Wu et al., Phys. Rev. Lett. 58, 908 (1987).
- Implications: Cuprates demonstrate that high Tc can be achieved at ambient pressure via strong correlations; similar mechanisms may be exploited in nickelates and other layered oxides.

*This summary was compiled from online research (web_search + web_fetch) on 2025-03-28. Sources are cited with URLs.*


## Implications for Project Discovery Strategy

- **Focus on ternary hydrides and clathrate structures** predicted by crystal structure prediction (USPEX, CALYPSO) to achieve high Tc at lower pressures. Use high-throughput DFT screening to identify promising candidates.
- **Investigate chemical precompression** using rare-earth and alkaline-earth metals to stabilize hydrogen-rich phases at ambient or moderate pressures.
- **Explore bilayer nickelate La₃Ni₂O₇** as a platform for chemical substitution (Sr, Ca) and epitaxial strain to raise Tc towards room temperature.
- **Develop thin-film deposition techniques** (MBE, PLD) to stabilize metastable phases on substrates, enabling ambient-pressure measurements.
- **Implement rigorous replication protocols** and open data practices to avoid retracted claims.
- **Leverage machine learning** to accelerate discovery of novel superhydrides and electride superconductors.
- **Study cuprate analogs** to understand the role of strong correlations and d-wave pairing in achieving high Tc at ambient pressure, potentially guiding discovery of room-temperature compounds.
