
from typing import Dict, Optional, Iterable
import os
import matplotlib.pyplot as plt
import pandas as pd


def _ensure_dir(d: str) -> None:
    os.makedirs(d, exist_ok=True)


def plot_ci_trend(summaries: Dict[str, pd.DataFrame], outdir: str, timestamp: str,
                  title: str = "Average Sustainability Over Time (mean ± 95% CI)") -> str:
    """Plot the mean with 95% CI ribbon for each scenario."""
    _ensure_dir(outdir)
    plt.figure(figsize=(10, 6))
    for scenario, df in summaries.items():
        if not {"Step", "Avg", "CI95"}.issubset(df.columns):
            continue
        x = df["Step"].values
        y = df["Avg"].values
        ci = df["CI95"].values
        plt.plot(x, y, label=scenario)
        plt.fill_between(x, y - ci, y + ci, alpha=0.15)
    plt.title(title)
    plt.xlabel("Step")
    plt.ylabel("Average Sustainability Score")
    plt.legend(title="Scenario")
    plt.tight_layout()
    path = os.path.join(outdir, f"sustainability_trends_ci_{timestamp}.png")
    plt.savefig(path); plt.close()
    return path


def plot_state_shares(summaries: Dict[str, pd.DataFrame], outdir: str, timestamp: str) -> Dict[str, str]:
    """Stacked area of state shares (0..3) — one figure per scenario."""
    _ensure_dir(outdir)
    out = {}
    for scenario, df in summaries.items():
        if not {"Step", "Share0", "Share1", "Share2", "Share3"}.issubset(df.columns):
            continue
        plt.figure(figsize=(10, 6))
        x = df["Step"].values
        s0 = df["Share0"].values
        s1 = df["Share1"].values
        s2 = df["Share2"].values
        s3 = df["Share3"].values
        plt.stackplot(x, s0, s1, s2, s3, labels=["State0", "State1", "State2", "State3"])
        plt.title(f"State Shares Over Time — {scenario}")
        plt.xlabel("Step")
        plt.ylabel("Share")
        plt.legend(loc="upper right")
        plt.tight_layout()
        path = os.path.join(outdir, f"state_shares_{scenario}_{timestamp}.png")
        plt.savefig(path); plt.close()
        out[scenario] = path
    return out


def plot_tax_signal(summaries: Dict[str, pd.DataFrame], outdir: str, timestamp: str,
                    scenarios: Optional[Iterable[str]] = ("economic", "combo")) -> str:
    """Tax signal over time for selected scenarios."""
    _ensure_dir(outdir)
    plt.figure(figsize=(10, 6))
    for scenario in (scenarios or []):
        if scenario not in summaries:
            continue
        df = summaries[scenario]
        if not {"Step", "TaxSignal"}.issubset(df.columns):
            continue
        plt.plot(df["Step"].values, df["TaxSignal"].values, label=scenario)
    plt.title("Tax Signal Over Time (Endogenous Price Pressure)")
    plt.xlabel("Step")
    plt.ylabel("Tax Signal")
    plt.legend(title="Scenario")
    plt.tight_layout()
    path = os.path.join(outdir, f"tax_signal_{timestamp}.png")
    plt.savefig(path); plt.close()
    return path


def plot_velocity(summaries: Dict[str, pd.DataFrame], outdir: str, timestamp: str) -> str:
    """Adoption velocity over time by scenario."""
    _ensure_dir(outdir)
    plt.figure(figsize=(10, 6))
    for scenario, df in summaries.items():
        if not {"Step", "Velocity"}.issubset(df.columns):
            continue
        plt.plot(df["Step"].values, df["Velocity"].values, label=scenario)
    plt.title("Adoption Velocity Over Time")
    plt.xlabel("Step")
    plt.ylabel("Δ Average Sustainability per Step")
    plt.legend(title="Scenario")
    plt.tight_layout()
    path = os.path.join(outdir, f"velocity_{timestamp}.png")
    plt.savefig(path); plt.close()
    return path


def plot_peer_events(summaries: Dict[str, pd.DataFrame], outdir: str, timestamp: str) -> str:
    """Peer influence events per step by scenario."""
    _ensure_dir(outdir)
    plt.figure(figsize=(10, 6))
    for scenario, df in summaries.items():
        if not {"Step", "PeerEvents"}.issubset(df.columns):
            continue
        plt.plot(df["Step"].values, df["PeerEvents"].values, label=scenario)
    plt.title("Peer Influence Events Per Step")
    plt.xlabel("Step")
    plt.ylabel("Events")
    plt.legend(title="Scenario")
    plt.tight_layout()
    path = os.path.join(outdir, f"peer_events_{timestamp}.png")
    plt.savefig(path); plt.close()
    return path


def plot_gini(summaries: Dict[str, pd.DataFrame], outdir: str, timestamp: str) -> str:
    """Inequality of sustainability (Gini) over time by scenario."""
    _ensure_dir(outdir)
    plt.figure(figsize=(10, 6))
    for scenario, df in summaries.items():
        if not {"Step", "Gini"}.issubset(df.columns):
            continue
        plt.plot(df["Step"].values, df["Gini"].values, label=scenario)
    plt.title("Inequality of Sustainability (Gini) Over Time")
    plt.xlabel("Step")
    plt.ylabel("Gini Score")
    plt.legend(title="Scenario")
    plt.tight_layout()
    path = os.path.join(outdir, f"gini_{timestamp}.png")
    plt.savefig(path); plt.close()
    return path


def plot_all(summaries: Dict[str, pd.DataFrame], outdir: str, timestamp: str) -> dict:
    """Convenience wrapper to produce all figures; returns dict of paths."""
    paths = {}
    paths["ci"] = plot_ci_trend(summaries, outdir, timestamp)
    paths["state_shares"] = plot_state_shares(summaries, outdir, timestamp)
    paths["tax_signal"] = plot_tax_signal(summaries, outdir, timestamp)
    paths["velocity"] = plot_velocity(summaries, outdir, timestamp)
    paths["peer_events"] = plot_peer_events(summaries, outdir, timestamp)
    paths["gini"] = plot_gini(summaries, outdir, timestamp)
    return paths
