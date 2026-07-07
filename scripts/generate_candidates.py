#!/usr/bin/env python3
"""
Conditional Variational Autoencoder (cVAE) for generating candidate materials
with desired properties (high Tc, low pressure, structural constraints).
Trains on existing superconductor database, then generates new compositions.
"""

import json
import os
import sys
import argparse
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

# Paths
DATA_DIR = "data"
DB_FILE = os.path.join(DATA_DIR, "superconductor_database.json")
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "cvae_model.pt")

# Element list (118 elements, but we only use common ones for superconductors)
ELEMENTS = [
    "H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne",
    "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca",
    "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn",
    "Ga", "Ge", "As", "Se", "Br", "Kr", "Rb", "Sr", "Y", "Zr",
    "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn",
    "Sb", "Te", "I", "Xe", "Cs", "Ba", "La", "Ce", "Pr", "Nd",
    "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb",
    "Lu", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg",
    "Tl", "Pb", "Bi", "Po", "At", "Rn", "Fr", "Ra", "Ac", "Th",
    "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm",
    "Md", "No", "Lr", "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds",
    "Rg", "Cn", "Nh", "Fl", "Mc", "Lv", "Ts", "Og"
]
ELEMENT_TO_IDX = {el: i for i, el in enumerate(ELEMENTS)}
NUM_ELEMENTS = len(ELEMENTS)

# Condition dimensions: [Tc, pressure (GPa), structural constraint one-hot?]
# For simplicity, we use Tc and pressure as continuous conditions.
COND_DIM = 2


class SuperconductorDataset(Dataset):
    """Dataset from superconductor_database.json."""
    def __init__(self, db_path):
        with open(db_path, "r") as f:
            data = json.load(f)
        self.compositions = []
        self.conditions = []
        for entry in data:
            formula = entry.get("composition", "")
            tc = entry.get("tc", 0.0)
            pressure = entry.get("pressure", 0.0)
            # Convert formula to element fraction vector
            vec = self.formula_to_vector(formula)
            if vec is not None:
                self.compositions.append(vec)
                self.conditions.append([tc, pressure])
        self.compositions = torch.tensor(self.compositions, dtype=torch.float32)
        self.conditions = torch.tensor(self.conditions, dtype=torch.float32)

    @staticmethod
    def formula_to_vector(formula):
        """Parse a chemical formula like LaH10 into a normalized element fraction vector."""
        import re
        pattern = r'([A-Z][a-z]?)(\d*)'
        matches = re.findall(pattern, formula)
        if not matches:
            return None
        vec = np.zeros(NUM_ELEMENTS, dtype=np.float32)
        total_atoms = 0
        for el, count_str in matches:
            count = int(count_str) if count_str else 1
            idx = ELEMENT_TO_IDX.get(el)
            if idx is None:
                return None
            vec[idx] = count
            total_atoms += count
        if total_atoms == 0:
            return None
        vec /= total_atoms  # normalize to fractions
        return vec

    def __len__(self):
        return len(self.compositions)

    def __getitem__(self, idx):
        return self.compositions[idx], self.conditions[idx]


class ConditionalVAE(nn.Module):
    def __init__(self, input_dim=NUM_ELEMENTS, cond_dim=COND_DIM, latent_dim=32, hidden_dim=128):
        super().__init__()
        self.input_dim = input_dim
        self.cond_dim = cond_dim
        self.latent_dim = latent_dim

        # Encoder: input + condition -> mu, logvar
        self.encoder = nn.Sequential(
            nn.Linear(input_dim + cond_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
        )
        self.mu_layer = nn.Linear(hidden_dim, latent_dim)
        self.logvar_layer = nn.Linear(hidden_dim, latent_dim)

        # Decoder: latent + condition -> output (element fractions)
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim + cond_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, input_dim),
            nn.Softmax(dim=-1)  # output is a probability distribution over elements
        )

    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def forward(self, x, c):
        # x: composition vector, c: condition vector
        encoder_input = torch.cat([x, c], dim=-1)
        h = self.encoder(encoder_input)
        mu = self.mu_layer(h)
        logvar = self.logvar_layer(h)
        z = self.reparameterize(mu, logvar)
        decoder_input = torch.cat([z, c], dim=-1)
        recon_x = self.decoder(decoder_input)
        return recon_x, mu, logvar

    def generate(self, c, num_samples=1):
        """Generate new composition vectors conditioned on c."""
        self.eval()
        with torch.no_grad():
            z = torch.randn(num_samples, self.latent_dim)
            c_expanded = c.unsqueeze(0).expand(num_samples, -1)
            decoder_input = torch.cat([z, c_expanded], dim=-1)
            recon_x = self.decoder(decoder_input)
        return recon_x


def vector_to_formula(vec, threshold=0.01):
    """Convert a normalized element fraction vector to a chemical formula string."""
    indices = np.where(vec > threshold)[0]
    if len(indices) == 0:
        return ""
    # Sort by fraction descending
    sorted_idx = indices[np.argsort(-vec[indices])]
    formula_parts = []
    for idx in sorted_idx:
        el = ELEMENTS[idx]
        count = vec[idx]
        # Round to nearest integer if close, else keep fraction
        if count > 0.99:
            formula_parts.append(el)
        elif count > 0.1:
            # Represent as integer if close
            int_count = round(count * 10)  # scale to avoid decimals
            formula_parts.append(f"{el}{int_count}")
        else:
            # Skip very small fractions
            pass
    return "".join(formula_parts)


def load_data(db_path):
    """Load dataset from JSON database."""
    if not os.path.exists(db_path):
        print(f"Error: Database {db_path} not found.", file=sys.stderr)
        sys.exit(1)
    dataset = SuperconductorDataset(db_path)
    if len(dataset) == 0:
        print("Error: No valid compositions in database.", file=sys.stderr)
        sys.exit(1)
    return dataset


def train(model, dataloader, epochs=100, lr=1e-3, beta=1.0):
    """Train the cVAE model."""
    optimizer = optim.Adam(model.parameters(), lr=lr)
    model.train()
    for epoch in range(epochs):
        total_loss = 0.0
        for x, c in dataloader:
            optimizer.zero_grad()
            recon_x, mu, logvar = model(x, c)
            # Reconstruction loss (cross-entropy for softmax output)
            recon_loss = nn.functional.cross_entropy(recon_x, x.argmax(dim=-1), reduction='sum')
            # KL divergence
            kl_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
            loss = recon_loss + beta * kl_loss
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        if (epoch+1) % 10 == 0:
            print(f"Epoch {epoch+1}/{epochs}, Loss: {total_loss/len(dataloader.dataset):.4f}")


def generate_candidates(model, conditions, num_per_condition=10):
    """Generate candidate composition vectors for given conditions."""
    model.eval()
    candidates = []
    for cond in conditions:
        c = torch.tensor(cond, dtype=torch.float32)
        vecs = model.generate(c, num_samples=num_per_condition)
        for vec in vecs:
            formula = vector_to_formula(vec.numpy())
            if formula:
                candidates.append((formula, cond))
    return candidates


def main():
    parser = argparse.ArgumentParser(description="cVAE candidate generation")
    parser.add_argument("--train", action="store_true", help="Train the model from scratch")
    parser.add_argument("--epochs", type=int, default=100, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    parser.add_argument("--latent_dim", type=int, default=32, help="Latent dimension")
    parser.add_argument("--num_candidates", type=int, default=10, help="Number of candidates per condition")
    parser.add_argument("--target_tc", type=float, default=300.0, help="Target Tc (K)")
    parser.add_argument("--target_pressure", type=float, default=0.0, help="Target pressure (GPa)")
    args = parser.parse_args()

    # Load dataset
    dataset = load_data(DB_FILE)
    dataloader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True)

    # Initialize model
    model = ConditionalVAE(latent_dim=args.latent_dim)

    if args.train:
        print("Training cVAE...")
        train(model, dataloader, epochs=args.epochs)
        # Save model
        os.makedirs(MODEL_DIR, exist_ok=True)
        torch.save(model.state_dict(), MODEL_PATH)
        print(f"Model saved to {MODEL_PATH}")
    else:
        # Load pre-trained model
        if not os.path.exists(MODEL_PATH):
            print(f"Error: No trained model found at {MODEL_PATH}. Use --train first.", file=sys.stderr)
            sys.exit(1)
        model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
        print(f"Loaded model from {MODEL_PATH}")

    # Generate candidates for target conditions
    conditions = [
        [args.target_tc, args.target_pressure],
        [args.target_tc + 50, args.target_pressure],
        [args.target_tc, args.target_pressure + 50],
    ]
    candidates = generate_candidates(model, conditions, num_per_condition=args.num_candidates)

    print(f"\nGenerated {len(candidates)} candidate compositions:")
    for formula, cond in candidates:
        print(f"  {formula}  (Tc={cond[0]:.0f}K, P={cond[1]:.0f}GPa)")


if __name__ == "__main__":
    main()
