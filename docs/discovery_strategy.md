# Discovery Strategy

## Decision Support Algorithm

The decision support algorithm is a multi-criteria scoring system that ranks candidate materials for room-temperature superconductivity. It integrates theoretical predictions, experimental feasibility, and manufacturing scalability into a single composite score.

### Composite Scoring

Each candidate material is evaluated on three axes:

1. **Theoretical Promise (0–1)**: Based on DFT calculations of electronic structure, phonon-mediated pairing strength, and predicted critical temperature (Tc). Higher weight is given to materials with Tc > 300 K in first-principles models.
2. **Synthesis Feasibility (0–1)**: Assesses the availability of precursor elements, required pressure/temperature conditions, and known synthesis routes. Materials that can be synthesized at ambient pressure score higher.
3. **Manufacturing Scalability (0–1)**: Considers cost of raw materials, process complexity, and potential for thin-film or bulk production. Materials with abundant, low-cost elements and established fabrication methods score higher.

The composite score is a weighted sum:

```
Score = w1 * TheoreticalPromise + w2 * SynthesisFeasibility + w3 * ManufacturingScalability
```

Default weights are w1=0.5, w2=0.3, w3=0.2, but these can be adjusted by the user to reflect strategic priorities.

### Example Outputs

| Material | Theoretical Promise | Synthesis Feasibility | Manufacturing Scalability | Composite Score |
|----------|---------------------|------------------------|---------------------------|-----------------|
| Material A | 0.92 | 0.65 | 0.70 | 0.80 |
| Material B | 0.78 | 0.85 | 0.60 | 0.77 |
| Material C | 0.88 | 0.50 | 0.45 | 0.68 |

The algorithm outputs a ranked list with composite scores, enabling researchers to focus on the most promising candidates. 

### Integration with Physics and Chemistry

The scoring criteria are grounded in the physics of superconductivity (BCS theory, Eliashberg equations, Hubbard models) and chemistry of material synthesis (phase diagrams, doping strategies, crystal structure stability). The algorithm is updated as new experimental data and theoretical insights become available.
