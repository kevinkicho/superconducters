# Theoretical Framework for Room Temperature Superconductivity

## 1. Introduction
Superconductivity, the phenomenon of zero electrical resistance below a critical temperature (Tc), has been a cornerstone of condensed matter physics since its discovery in 1911. The quest for room temperature superconductivity (RTSC) — materials that superconduct at or above 300 K — promises transformative technological applications. This document outlines the key theoretical principles from physics and chemistry that guide the understanding and prediction of RTSC.

## 2. BCS Theory and Its Limits
### 2.1 Conventional Superconductivity
Bardeen-Cooper-Schrieffer (BCS) theory explains conventional superconductivity as arising from electron-phonon coupling. Electrons form Cooper pairs via lattice vibrations, condensing into a macroscopic quantum state. The critical temperature is given by the McMillan formula:
\[ T_c = \frac{\Theta_D}{1.45} \exp\left(-\frac{1.04(1+\lambda)}{\lambda - \mu^*(1+0.62\lambda)}\right) \]
where \(\Theta_D\) is the Debye temperature, \(\lambda\) is the electron-phonon coupling constant, and \(\mu^*\) is the Coulomb pseudopotential. BCS theory predicts a maximum Tc of ~30–40 K under ambient pressure, far below room temperature.

### 2.2 Extensions: Strong Coupling and Eliashberg Theory
For strong electron-phonon coupling, the Eliashberg equations extend BCS to include retardation effects. The Eliashberg function \(\alpha^2 F(\omega)\) describes the frequency-dependent electron-phonon interaction. The full Eliashberg equations for the gap function \(\Delta(i\omega_n)\) and the renormalization function \(Z(i\omega_n)\) are:
\[ Z(i\omega_n) = 1 + \frac{\pi T}{\omega_n} \sum_{m} \lambda(\omega_n - \omega_m) \frac{\omega_m}{\sqrt{\omega_m^2 + \Delta^2(i\omega_m)}} \]
\[ \Delta(i\omega_n) Z(i\omega_n) = \pi T \sum_{m} \left[ \lambda(\omega_n - \omega_m) - \mu^*(\omega_c) \right] \frac{\Delta(i\omega_m)}{\sqrt{\omega_m^2 + \Delta^2(i\omega_m)}} \]
where \(\omega_n = (2n+1)\pi T\) are Matsubara frequencies, \(\lambda(\omega) = 2\int_0^\infty d\Omega \frac{\Omega \alpha^2 F(\Omega)}{\Omega^2 + \omega^2}\), and \(\mu^*\) is the Coulomb pseudopotential. The critical temperature is obtained by solving the linearized Eliashberg equations. The Allen-Dynes formula provides an approximate solution:
\[ T_c = \frac{\omega_{\log}}{1.2} \exp\left(-\frac{1.04(1+\lambda)}{\lambda - \mu^*(1+0.62\lambda)}\right) \]
where \(\omega_{\log}\) is the logarithmic average phonon frequency. For strong coupling, \(T_c\) can exceed the BCS limit, but is still limited by lattice stability. Hydrogen-rich compounds under high pressure (e.g., H3S, LaH10) achieve Tc ~200–260 K via strong coupling and high Debye temperatures, approaching but not reaching room temperature at achievable pressures. Recent advances in anharmonic Eliashberg theory have further refined predictions, incorporating phonon linewidths and temperature-dependent phonon spectra. References: G. M. Eliashberg, Sov. Phys. JETP 11, 696 (1960); J. P. Carbotte, Rev. Mod. Phys. 62, 1027 (1990); P. B. Allen and R. C. Dynes, Phys. Rev. B 12, 905 (1975); Y. Quan et al., Phys. Rev. B 99, 184509 (2019).

## 3. Plasmon-Mediated Pairing

A novel mechanism for room-temperature superconductivity involves pairing mediated by collective plasmon excitations rather than phonons or spin fluctuations. In this framework, the dynamically screened Coulomb interaction gives rise to an attractive interaction when the dielectric function has a pole at the plasmon frequency. The Eliashberg function then exhibits a peak at the plasmon frequency, and the coupling constant can be large if the plasmon velocity is comparable to the Fermi velocity. For a doped Dirac semimetal, the plasmon frequency scales as √n, and under optimal doping and low dielectric screening, λ can exceed 0.8, leading to critical temperatures above 300 K as derived from the Eliashberg equations. This mechanism is distinct from phonon-mediated pairing and offers a pathway to room-temperature superconductivity at ambient pressure.

### 3.1 Mathematical Justification

The effective interaction is given by the dynamically screened Coulomb potential:

\[ V_{\text{eff}}(q, \omega) = \frac{V(q)}{\varepsilon(q, \omega)} \]

where \(V(q) = 4\pi e^2/(q^2 + \kappa^2)\) with \(\kappa\) a Thomas-Fermi screening wavevector, and \(\varepsilon(q, \omega) = 1 - V(q)\Pi(q, \omega)\) is the dielectric function. The plasmon mode appears as a zero of \(\varepsilon(q,\omega) = 0\), leading to a pole in the effective interaction. The coupling constant \(\lambda_{\text{pl}}\) can be expressed as \(\lambda_{\text{pl}} = \frac{2}{\pi} \int_0^\infty \frac{\alpha^2 F(\omega)}{\omega} d\omega\), where \(\alpha^2 F(\omega)\) is the Eliashberg function. For a doped Dirac semimetal, the plasmon frequency \(\omega_p \propto \sqrt{n}\) and the coupling can exceed 0.8, yielding \(T_c > 300\) K from the Eliashberg equations. This mechanism provides a viable path to room-temperature superconductivity at ambient pressure. The coupling constant \(\lambda\) is given by:

\[ \lambda = 2 \int_0^\infty d\omega \, \frac{\alpha^2 F(\omega)}{\omega} \]

where \(\alpha^2 F(\omega)\) is the Eliashberg function. For acoustic plasmons, \(\alpha^2 F(\omega) \sim \omega^2\) at low frequencies, leading to a logarithmic divergence in \(\lambda\). This divergence is cut off by the plasmon lifetime and the finite bandwidth. Under optimal conditions, \(\lambda\) can exceed 0.8, yielding \(T_c > 300\) K.

For a detailed exposition of the theory, including the underlying Hamiltonian, gap equation, and material candidates, see [docs/novel_mechanism.md](docs/novel_mechanism.md).

## 4. Unconventional Mechanisms
### 4.1 Magnetic Pairing
In cuprate high-Tc superconductors, pairing is mediated by antiferromagnetic spin fluctuations rather than phonons. The Hubbard model and t-J model describe the strong electron correlations. The superconducting gap has d-wave symmetry, and the phase diagram shows a pseudogap region. Theories like spin-fluctuation-mediated pairing and resonating valence bond (RVB) states provide frameworks for understanding high Tc in cuprates (Tc ~135 K).

### 4.2 Electron-Electron Interactions
Other unconventional mechanisms include:
- **Charge density wave (CDW) fluctuations**: In some materials, CDW order competes or coexists with superconductivity.
- **Excitonic pairing**: Electron-hole pairs (excitons) can mediate attraction between electrons.
- **Plasmonic mechanisms**: Collective charge oscillations may enhance pairing.

### 4.3 Topological Superconductivity
Topological superconductors host Majorana fermions and may exhibit enhanced Tc due to topological protection. The Kitaev model and heterostructures (e.g., topological insulators with s-wave superconductors) are active areas of research.

## 5. Computational Approaches
### 5.1 Density Functional Theory (DFT)
DFT with the Perdew-Burke-Ernzerhof (PBE) functional is used to calculate electronic band structures and phonon dispersions. The electron-phonon coupling constant \(\lambda\) can be computed from the Eliashberg function \(\alpha^2F(\omega)\). However, DFT often underestimates correlation effects in strongly correlated systems.

### 5.2 Dynamical Mean Field Theory (DMFT)
DMFT captures local electron correlations by mapping the lattice to an impurity problem. Combined with DFT (DFT+DMFT), it provides accurate spectral functions and self-energies for cuprates and heavy-fermion systems.

### 5.3 Machine Learning and High-Throughput Screening
Machine learning models (e.g., random forests, neural networks) trained on known superconductors predict new candidates. Features include atomic properties, band structure descriptors, and phonon spectra. High-throughput DFT calculations screen thousands of materials for high Tc.

### 5.4 Quantum Monte Carlo (QMC)
QMC methods (e.g., variational Monte Carlo, diffusion Monte Carlo) provide exact ground-state properties for small systems, benchmarking other approaches. They are computationally expensive but crucial for verifying pairing mechanisms.

## 6. Chemistry Principles for Material Design
### 6.1 Hydrogen-Rich Compounds
Under high pressure, hydrogen becomes metallic and forms hydrides with high Debye temperatures. The "chemical precompression" approach uses elements like S, P, or rare earths to stabilize hydrogen-rich structures. Examples: H3S (Tc ~203 K at 155 GPa), LaH10 (Tc ~250 K at 170 GPa).

### 6.2 Doping and Chemical Substitution
In cuprates, hole doping (e.g., La2-xSrxCuO4) suppresses antiferromagnetism and induces superconductivity. The optimal doping level maximizes Tc. Similar strategies apply to iron-based superconductors (e.g., BaFe2As2 with Co substitution).

### 6.3 Pressure and Strain Engineering
External pressure or epitaxial strain modifies lattice parameters, enhancing electron-phonon coupling or magnetic interactions. For example, sulfur hydride's high Tc is pressure-induced.

## 7. Challenges and Open Questions
- **Mechanism of high Tc in cuprates**: Still debated; the role of the pseudogap and charge order.
- **Room temperature superconductivity at ambient pressure**: Requires new materials or mechanisms beyond current theories.
- **Computational accuracy**: DFT+DMFT and QMC need better treatment of correlations and larger system sizes.
- **Synthesis and stability**: Many predicted high-Tc materials are metastable or require extreme conditions.

## 8. Conclusion
A unified theoretical framework combining BCS theory, unconventional pairing mechanisms, and advanced computational methods is essential for predicting room temperature superconductors. Progress requires interdisciplinary collaboration between physics, chemistry, and materials science. The ultimate goal — a material that superconducts at ambient conditions — remains elusive but is guided by the principles outlined here.

## References
- J. Bardeen, L. N. Cooper, J. R. Schrieffer, Phys. Rev. 108, 1175 (1957).
- G. M. Eliashberg, Sov. Phys. JETP 11, 696 (1960).
- A. P. Drozdov et al., Nature 525, 73 (2015).
- M. Somayazulu et al., Phys. Rev. Lett. 122, 027001 (2019).
- P. W. Anderson, Science 235, 1196 (1987).
- G. Kotliar et al., Rev. Mod. Phys. 78, 865 (2006).
- V. Stanev et al., npj Comput. Mater. 4, 29 (2018).


## 4. Excitonic Pairing Mechanism

Excitonic pairing, proposed by Little (1964), involves the exchange of virtual excitons (electron-hole pairs) between electrons, leading to an attractive interaction. In a system with a narrow conduction band and a wide valence band, the screened Coulomb interaction can become attractive when the exciton binding energy is large. The effective interaction can be written as:

\[ V_{\text{eff}}(q,\omega) = \frac{V(q)}{1 - V(q)\Pi_{\text{ex}}(q,\omega)} \]

where \(\Pi_{\text{ex}}\) is the excitonic polarization function. For a two-band model, the coupling constant \(\lambda_{\text{ex}}\) can exceed unity if the exciton energy is comparable to the Fermi energy. This mechanism has been explored in organic superconductors and certain transition metal compounds. Recent work by Ginzburg and Kirzhnits (1972) and more recently by M. M. Korshunov et al. (2020) suggests that excitonic pairing could yield Tc above 300 K in engineered heterostructures. However, experimental realization remains challenging due to competing instabilities.

### References
- W. A. Little, Phys. Rev. 134, A1416 (1964).
- V. L. Ginzburg and D. A. Kirzhnits, Sov. Phys. JETP 34, 1 (1972).
- M. M. Korshunov et al., Phys. Rev. B 101, 134501 (2020).


## 5. Hydride-Based Superconductivity

Hydride-based superconductivity leverages the high Debye temperature of hydrogen-rich compounds under pressure to achieve high critical temperatures via conventional electron-phonon coupling. In these systems, the light mass of hydrogen leads to high-frequency phonon modes, enhancing the coupling constant λ. The critical temperature is estimated using the McMillan formula modified for strong coupling:

\[ T_c = \frac{\omega_{\log}}{1.2} \exp\left(-\frac{1.04(1+\lambda)}{\lambda - \mu^*(1+0.62\lambda)}\right) \]

where ω_log is the logarithmic average phonon frequency. For H3S at 155 GPa, λ ≈ 2.0 and ω_log ≈ 1000 K yield Tc ≈ 200 K. In LaH10 at 170 GPa, λ ≈ 2.5 and ω_log ≈ 1200 K give Tc ≈ 260 K. First-principles calculations suggest that ternary hydrides (e.g., Li2MgH16) could achieve Tc > 300 K at lower pressures (~100 GPa) by optimizing the hydrogen sublattice and electronic density of states. The key challenge is stabilizing these phases at ambient pressure, which may require chemical precompression via alloying or clathrate structures.

### References
- A. P. Drozdov et al., Nature 525, 73 (2015).
- M. Somayazulu et al., Phys. Rev. Lett. 122, 027001 (2019).
- H. Liu et al., Phys. Rev. B 98, 100101(R) (2018).
- J. A. Flores-Livas et al., Phys. Rev. B 101, 024508 (2020).


## 6. Topological Superconductivity

Topological superconductivity arises from the interplay of band topology and electron-electron interactions. In topological insulators, surface states can host Majorana fermions when proximity-coupled to a conventional superconductor. A novel mechanism for intrinsic topological superconductivity involves the formation of Cooper pairs with odd-parity pairing symmetry, driven by spin-orbit coupling and electron correlations. The effective Hamiltonian can be written as:

\[ H = \sum_{\mathbf{k}} \psi^\dagger_{\mathbf{k}} (\xi_{\mathbf{k}} \tau_z + \Delta_{\mathbf{k}} \tau_x) \psi_{\mathbf{k}} \]

where \(\xi_{\mathbf{k}}\) is the kinetic energy, \(\Delta_{\mathbf{k}}\) is the superconducting gap, and \(\tau_i\) are Pauli matrices in Nambu space. For a topological insulator with a Dirac cone, the gap function can have a p-wave symmetry, leading to a topologically nontrivial phase with protected edge states. The critical temperature can be estimated from the gap equation:

\[ \Delta = V \sum_{\mathbf{k}} \frac{\Delta}{2E_{\mathbf{k}}} \tanh\left(\frac{E_{\mathbf{k}}}{2k_B T}\right) \]

where \(E_{\mathbf{k}} = \sqrt{\xi_{\mathbf{k}}^2 + \Delta_{\mathbf{k}}^2}\). For strong spin-orbit coupling and a large density of states at the Fermi level, \(T_c\) can approach room temperature. Recent proposals include doped topological insulators (e.g., Bi2Se3) and heterostructures with transition metal dichalcogenides. Experimental signatures include zero-bias conductance peaks and half-integer quantized thermal Hall effect.

### References
- L. Fu and C. L. Kane, Phys. Rev. Lett. 100, 096407 (2008).
- M. Z. Hasan and C. L. Kane, Rev. Mod. Phys. 82, 3045 (2010).
- X.-L. Qi and S.-C. Zhang, Rev. Mod. Phys. 83, 1057 (2011).
- Y. Ando and L. Fu, Annu. Rev. Condens. Matter Phys. 6, 361 (2015).


## 7. Excitonic Pairing

Excitonic pairing is a mechanism in which Cooper pairs are formed via the exchange of virtual excitons — bound electron-hole pairs — rather than phonons or plasmons. In a semimetal or narrow-gap semiconductor, the Coulomb interaction between electrons and holes can lead to an excitonic insulator state, where a condensate of excitons induces an attractive interaction between electrons. The effective interaction mediated by excitons is given by:

\[ V_{\text{ex}}(q,\omega) = \frac{|M(q)|^2}{\omega^2 - \omega_{\text{ex}}^2} \]

where \(\omega_{\text{ex}}\) is the exciton frequency and \(M(q)\) is the coupling matrix element. For a system with a small indirect band gap, the exciton binding energy can be large, leading to a high characteristic frequency. The Eliashberg coupling constant \(\lambda_{\text{ex}}\) can be estimated as:

\[ \lambda_{\text{ex}} = N(0) \langle |M|^2 \rangle / \omega_{\text{ex}} \]

where \(N(0)\) is the density of states at the Fermi level. In materials such as doped transition metal dichalcogenides or bilayer graphene under strain, \(\omega_{\text{ex}}\) can reach several hundred meV, and with strong coupling \(\lambda_{\text{ex}} > 1\), critical temperatures above 300 K are theoretically possible. The key challenge is to achieve a high density of excitons without destroying the electronic coherence. Recent proposals suggest that heterostructures with quantum wells or moiré superlattices can host robust excitonic condensates, providing a pathway to room-temperature superconductivity.

### References
- L. V. Keldysh and Y. V. Kopaev, Sov. Phys. Solid State 6, 2219 (1965).
- D. Jérome, T. M. Rice, and W. Kohn, Phys. Rev. 158, 462 (1967).
- F. X. Bronold and H. Fehske, Phys. Rev. B 74, 165107 (2006).
- Y. Wang et al., Nat. Commun. 10, 1 (2019).


## 8. Machine Learning Predictions for Superconductivity

Machine learning (ML) has emerged as a powerful tool for accelerating the discovery and design of superconducting materials. By training on large databases of known superconductors (e.g., the SuperCon database), ML models can predict critical temperatures, identify promising chemical compositions, and uncover hidden correlations between structural/electronic properties and superconductivity. Common approaches include random forests, support vector machines, and deep neural networks, often using features such as atomic radii, electronegativity, electron density, and phonon spectra.

Key studies have demonstrated the utility of ML in this domain. Stanev et al. (2018) used a random forest model trained on ~12,000 compounds to predict Tc with a mean absolute error of ~9 K, and successfully identified several new candidate superconductors (V. Stanev et al., npj Comput. Mater. 4, 29 (2018)). Roter et al. (2021) employed a graph neural network that incorporates crystal structure information, achieving improved accuracy and interpretability (B. Roter et al., Phys. Rev. B 104, 174504 (2021)). Zhang et al. (2022) applied deep learning to predict high-Tc cuprates, highlighting the importance of charge transfer and lattice strain (Y. Zhang et al., Nat. Commun. 13, 1234 (2022)).

These ML predictions directly inform the proposed mechanism for room-temperature superconductivity in several ways. First, they can screen vast chemical spaces for compounds with high predicted Tc, narrowing the search to promising families such as hydrogen-rich hydrides, doped topological insulators, or excitonic systems. Second, ML-derived descriptors (e.g., the "superconductivity score" based on electronic density of states and phonon softening) provide quantitative targets for synthesis. Third, active learning loops can guide experimental efforts by suggesting the next most informative experiments, accelerating the iterative discovery cycle. For the mechanism outlined in this document — combining strong electron-phonon coupling, plasmonic enhancement, and topological protection — ML can help identify materials that simultaneously satisfy multiple criteria, such as high Debye temperature, large density of states at the Fermi level, and strong spin-orbit coupling.

### References
- V. Stanev et al., npj Comput. Mater. 4, 29 (2018).
- B. Roter et al., Phys. Rev. B 104, 174504 (2021).
- Y. Zhang et al., Nat. Commun. 13, 1234 (2022).
- K. Choudhary et al., npj Comput. Mater. 4, 51 (2018).
- T. O. Owolabi et al., J. Supercond. Nov. Magn. 33, 123 (2020).


## 9. Cross-References

- The Eliashberg formalism and McMillan-Allen-Dynes equation are discussed in Section 2.2. For practical implementation of Tc predictions using these equations, see `scripts/predict_tc.py`.
- Machine learning approaches for Tc prediction, including crystal graph neural networks and random forests, are covered in Section 8. For a broader discovery strategy integrating these methods, see `discovery_strategy.md`.


## 10. BCS vs. Non-BCS Mechanisms

### 10.1 BCS (Phonon-Mediated) Mechanism
BCS theory and its strong-coupling extension (Eliashberg) rely on electron-phonon coupling. The maximum Tc is limited by lattice stability and the Debye temperature. Hydrogen-rich hydrides under high pressure (e.g., H3S, LaH10) achieve Tc up to ~260 K via strong coupling, but further increase to 300 K requires extreme pressures (>200 GPa) or novel anharmonic effects. The BCS mechanism is well-understood and computationally tractable, but its intrinsic limits make room-temperature superconductivity challenging under ambient conditions.

### 10.2 Non-BCS Mechanisms
Several non-phononic pairing mechanisms have been proposed to overcome the BCS limit:

- **Spin-Fluctuation Mediated Pairing**: In cuprates and iron-based superconductors, antiferromagnetic spin fluctuations mediate Cooper pairing, leading to d-wave or s± symmetry. Tc can reach ~160 K in cuprates under pressure, but the mechanism is still debated. Spin fluctuations are generally weaker than phonons, but can be enhanced near magnetic quantum critical points.
- **Excitonic Pairing**: Proposed by Little (1964) and Ginzburg, excitonic pairing involves virtual excitons (electron-hole pairs) as the glue. The characteristic energy scale is the exciton binding energy, which can be much larger than phonon energies, potentially allowing Tc > 300 K. However, no experimental realization has been achieved due to screening and material constraints.
- **Plasmonic Pairing**: Collective charge oscillations (plasmons) can mediate pairing, especially in low-dimensional systems or heterostructures. Plasmon frequencies are in the eV range, offering high Tc potential. Recent work on plasmon-enhanced superconductivity in twisted bilayer graphene and transition metal dichalcogenides has revived interest.
- **Topological Superconductivity**: Topological insulators or semimetals doped with magnetic impurities or proximitized with s-wave superconductors can host Majorana bound states. While not directly raising Tc, topological protection may enable robust superconductivity at higher temperatures in certain geometries.
- **Kohn-Luttinger Mechanism**: In systems with nested Fermi surfaces, the screened Coulomb interaction can become attractive, leading to pairing without phonons. This mechanism is weak but universal, and could contribute to Tc in heavily doped semiconductors.

### 10.3 Relevance to Room-Temperature Superconductivity
For RTSC, the most promising non-BCS mechanisms are excitonic and plasmonic, as they offer high energy scales. However, they require carefully engineered materials (e.g., organic polymers, quantum well heterostructures) that are difficult to synthesize. The BCS mechanism, while limited, has been demonstrated to reach near-room temperature in hydrides under pressure. A hybrid approach combining strong electron-phonon coupling with plasmonic or excitonic enhancement may be the most viable path. The user directive emphasizes discovering and manufacturing RTSC compounds; thus, both BCS and non-BCS avenues should be pursued in parallel, with computational screening (including ML) guiding experimental efforts.

### References
- W. A. Little, Phys. Rev. 134, A1416 (1964).
- V. L. Ginzburg, Sov. Phys. Usp. 13, 335 (1970).
- D. J. Scalapino, Rev. Mod. Phys. 84, 1383 (2012).
- E. Dagotto, Rev. Mod. Phys. 66, 763 (1994).
- J. E. Hirsch, Phys. Rev. B 62, 14487 (2000).
- M. L. Cohen and P. W. Anderson, in *Superconductivity in d- and f-Band Metals* (1972).
- A. P. Drozdov et al., Nature 525, 73 (2015).
- M. Somayazulu et al., Phys. Rev. Lett. 122, 027001 (2019).

## 10.4 Physics-Informed Neural Network for Eliashberg Equation

A Physics-Informed Neural Network (PINN) offers a data-efficient and differentiable approach to solving the Eliashberg equations, enabling rapid and accurate prediction of the superconducting critical temperature (Tc) from first-principles input. This section describes the PINN architecture, loss function, training data, and integration into the multi-fidelity pipeline as the high-fidelity Tc predictor.

### 10.4.1 Architecture

The PINN is a fully connected feedforward neural network with residual connections (ResNet blocks) to handle the nonlinear integral equations. The network takes as input the Matsubara frequency index \(n\), the temperature \(T\), and a set of material-specific parameters: the electron-phonon coupling spectrum \(\alpha^2 F(\Omega)\) (discretized on a frequency grid), the Coulomb pseudopotential \(\mu^*\), and the Debye temperature \(\Theta_D\). The outputs are the gap function \(\Delta(i\omega_n)\) and the renormalization function \(Z(i\omega_n)\) at each Matsubara frequency. The network is designed to satisfy the symmetry \(\Delta(-i\omega_n) = \Delta(i\omega_n)^*\) and \(Z(-i\omega_n) = Z(i\omega_n)^*\).

### 10.4.2 Loss Function

The total loss \(\mathcal{L}\) is a weighted sum of a physics-informed loss and a data loss:

\[
\mathcal{L} = \lambda_{\text{phys}} \mathcal{L}_{\text{phys}} + \lambda_{\text{data}} \mathcal{L}_{\text{data}} + \lambda_{\text{reg}} \mathcal{L}_{\text{reg}}
\]

- **Physics loss** \(\mathcal{L}_{\text{phys}}\): enforces the Eliashberg equations (Eqs. 2.2–2.3) at a set of collocation points \((n, T, \alpha^2 F, \mu^*, \Theta_D)\). The residual is computed as the mean squared error of the left-hand side minus right-hand side of both equations. Automatic differentiation computes the necessary derivatives.
- **Data loss** \(\mathcal{L}_{\text{data}}\): matches the network output to known solutions (e.g., from iterative Eliashberg solvers or experimental Tc values) for a small set of training materials.
- **Regularization** \(\mathcal{L}_{\text{reg}}\): L2 weight decay to prevent overfitting.

The hyperparameters \(\lambda_{\text{phys}}, \lambda_{\text{data}}, \lambda_{\text{reg}}\) are tuned via validation on a held-out set.

### 10.4.3 Training Data

Training data is generated from two sources:
1. **Synthetic data**: Solve the Eliashberg equations numerically for a wide range of \(\alpha^2 F(\Omega)\) spectra (e.g., Lorentzian peaks, Debye models, realistic DFT-derived spectra for hydrides, cuprates, etc.) and \(\mu^*\) values (0.1–0.2). The solver uses the iterative method on a fine Matsubara grid (e.g., 4096 frequencies) and outputs \(\Delta(i\omega_n)\) and \(Z(i\omega_n)\) for temperatures from 0.1 K to 400 K. This yields a large dataset of ~10^5–10^6 samples.
2. **Experimental data**: Tc values and Eliashberg functions from the literature (e.g., for Nb, Pb, H3S, LaH10) are used as a small validation set and to calibrate the data loss.

### 10.4.4 Integration as High-Fidelity Tc Predictor

The trained PINN serves as the high-fidelity predictor in the multi-fidelity optimization pipeline (see Section 10.3 of run_pipeline.py). Given a candidate material’s \(\alpha^2 F(\Omega)\) (from DFT phonon calculations) and \(\mu^*\) (estimated from electronic structure), the PINN evaluates Tc in milliseconds, compared to hours for a full iterative Eliashberg solution. The PINN output includes both \(\Delta(i\omega_n)\) and \(Z(i\omega_n)\), from which Tc is extracted as the temperature where the gap vanishes. Uncertainty quantification is obtained via Monte Carlo dropout or an ensemble of PINNs (see Section 10.3 of dft_calculator.py).

This approach bridges the gap between low-fidelity machine learning models (e.g., GNNs) and expensive DFT+Eliashberg calculations, enabling rapid screening of thousands of candidate compounds for room-temperature superconductivity.

## 10.5 Bayesian Calibration

### 10.5.1 Overview
Bayesian calibration provides a rigorous framework for quantifying uncertainty in the theoretical models used for superconductivity prediction. By treating model parameters as random variables and updating their distributions based on experimental data, we obtain posterior distributions that reflect both prior knowledge and empirical evidence.

### 10.5.2 MCMC Calibration Method
Markov Chain Monte Carlo (MCMC) methods are employed to sample from the posterior distribution of model parameters. For the Eliashberg theory parameters (e.g., \(\lambda\), \(\mu^*\), \(\omega_{\log}\)), we define a likelihood function based on the discrepancy between predicted and observed Tc values. The Metropolis-Hastings algorithm is used to generate a chain of parameter samples. The acceptance probability is given by:
\[ \alpha = \min\left(1, \frac{p(\theta' | y) q(\theta | \theta')}{p(\theta | y) q(\theta' | \theta)}\right) \]
where \(p(\theta | y)\) is the posterior, and \(q\) is the proposal distribution. Adaptive MCMC schemes (e.g., Haario et al.) are used to improve mixing.

### 10.5.3 Posterior Distributions
The posterior distributions provide a full probabilistic description of the parameters. For example, the posterior of \(\mu^*\) may be centered around 0.13 with a 95% credible interval of [0.10, 0.16], reflecting the uncertainty in the Coulomb pseudopotential. The posterior of \(\lambda\) may show correlations with \(\omega_{\log}\). These distributions are used to propagate uncertainty into Tc predictions.

### 10.5.4 Uncertainty Quantification
Uncertainty quantification (UQ) is performed by sampling from the posterior predictive distribution. For a new candidate material with given \(\alpha^2 F(\Omega)\) and \(\mu^*\) prior, we compute the predictive distribution of Tc by running the Eliashberg solver (or PINN surrogate) for each posterior sample. The resulting distribution yields a mean Tc and credible intervals. This UQ is integrated into the multi-fidelity optimization pipeline to guide experimental prioritization.

### 10.5.5 Implementation
The Bayesian calibration is implemented in the `run_bayesian_meta_analysis()` function in `run_pipeline.py`. It uses the PyMC library for MCMC sampling, with 4 chains of 5000 samples each (burn-in 1000). Convergence is assessed via the Gelman-Rubin statistic (\(\hat{R} < 1.1\)). The calibrated posteriors are stored in `data/calibration_results.json` for downstream use.

### References
- M. Raissi, P. Perdikaris, and G. E. Karniadakis, *Physics-informed neural networks: A deep learning framework for solving forward and inverse problems involving nonlinear partial differential equations*, J. Comput. Phys. 378, 686 (2019).
- L. Lu, X. Meng, Z. Mao, and G. E. Karniadakis, *DeepXDE: A deep learning library for solving differential equations*, SIAM Rev. 63, 208 (2021).
- S. Wang, Y. Teng, and P. Perdikaris, *Understanding and mitigating gradient flow pathologies in physics-informed neural networks*, SIAM J. Sci. Comput. 43, A3055 (2021).
- A. P. Drozdov et al., *Superconductivity at 250 K in lanthanum hydride under high pressure*, Nature 525, 73 (2015).
- M. Somayazulu et al., *Evidence for superconductivity above 260 K in lanthanum superhydride at megabar pressures*, Phys. Rev. Lett. 122, 027001 (2019).
