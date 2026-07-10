"""
Discovery announcement module for superconductor pipeline.

Provides functions for generating discovery announcements and reports.
"""

import json
import os
from datetime import datetime


def generate_discovery_announcement(candidates=None, predictions=None):
    """
    Generate a discovery announcement for the top candidate materials.

    Args:
        candidates (list, optional): List of candidate compounds.
        predictions (dict, optional): Dict mapping compound to predicted Tc.

    Returns:
        str: Markdown announcement text.
    """
    if candidates is None:
        candidate_file = "candidate_materials.md"
        if os.path.exists(candidate_file):
            with open(candidate_file, "r") as f:
                content = f.read()
            lines = content.split("\n")
            candidates = []
            for line in lines:
                if line.startswith("- [ ]") or line.startswith("- [x]"):
                    parts = line.split(" - ")
                    if len(parts) >= 1:
                        compound = parts[0].replace("- [ ] ", "").replace("- [x] ", "").strip()
                        candidates.append(compound)
        else:
            candidates = ["LaH10", "H3S", "YBa2Cu3O7"]

    if predictions is None:
        predictions = {}

    announcement = f"""# Discovery Announcement

**Date:** {datetime.utcnow().strftime('%Y-%m-%d')}

## Top Candidates

"""
    for i, c in enumerate(candidates[:5], 1):
        tc = predictions.get(c, "N/A")
        announcement += f"{i}. **{c}** - Predicted Tc: {tc} K\n"

    announcement += """
## Next Steps
1. Synthesize top candidates using high-pressure methods.
2. Characterize Tc, structure, and stability.
3. Optimize synthesis parameters via Bayesian optimization.
"""
    return announcement
