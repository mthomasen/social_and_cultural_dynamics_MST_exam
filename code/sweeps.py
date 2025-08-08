import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# We tweak globals at runtime, then restore:
import functions_and_parameters as fp
import agent as agent_module


def _ensure_dir(d: str):
    os.makedirs(d, exist_ok=True)


def _first_crossing(df: pd.DataFrame, col: str, thresh: float):
    c = df[df[col] >= thresh]
    return float(c["Step"].iloc[0]) if not c.empty else np.nan


def _final_row(df: pd.DataFrame) -> pd.Series:
    """Return the last-step row for this summary dataframe."""
    last_idx = df["Step"].idxmax()
    return df.loc[last_idx]


def sweep_backlash(run_monte_carlo, values, steps, n_runs=20, target=0.80,
                   data_dir=".", plot_dir=None, timestamp=""):
    """
    Run 'combo' for several BACKLASH_SCALE values.
    Saves overlay + final-outcome plots to plot_dir and per-value CSVs to data_dir.
    Returns a dict[value] -> summary dataframe.
    """
    _ensure_dir(data_dir)
    pdir = plot_dir or data_dir
    _ensure_dir(pdir)

    # Save originals so we can restore
    orig_fp = getattr(fp, "BACKLASH_SCALE", None)
    orig_ag = getattr(agent_module, "BACKLASH_SCALE", None)

    results = {}
    for bl in values:
        print(f"[sweep_backlash] BACKLASH_SCALE={bl}")
        if orig_fp is not None: setattr(fp, "BACKLASH_SCALE", bl)
        if orig_ag is not None: setattr(agent_module, "BACKLASH_SCALE", bl)

        _, summary = run_monte_carlo("combo", steps=steps, n_runs=n_runs)
        results[bl] = summary
        summary.to_csv(os.path.join(data_dir, f"combo_backlash_{bl}_summary_{timestamp}.csv"), index=False)

    # Restore
    if orig_fp is not None: setattr(fp, "BACKLASH_SCALE", orig_fp)
    if orig_ag is not None: setattr(agent_module, "BACKLASH_SCALE", orig_ag)

    # Overlay trajectories
    plt.figure(figsize=(10, 6))
    for bl, df in results.items():
        plt.plot(df["Step"], df["Avg"], label=f"BL={bl}")
    plt.title("Combo: Sensitivity to BACKLASH_SCALE")
    plt.xlabel("Step"); plt.ylabel("Average Sustainability Score")
    plt.legend(title="Backlash scale"); plt.tight_layout()
    p_overlay = os.path.join(pdir, f"combo_backlash_overlay_{timestamp}.png")
    plt.savefig(p_overlay); plt.close()

    # Final outcomes & time-to-target (+ CI on FinalAvg)
    rows = []
    for bl, df in results.items():
        row = _final_row(df)
        final_avg = float(row["Avg"])
        final_avg_std = float(row["Std"]) if "Std" in df.columns else float("nan")
        out = {
            "Backlash": bl,
            "FinalAvg": final_avg,
            "FinalAvgStd": final_avg_std,
            "FinalState3": float(row["Share3"]),
            "T_to_Target": _first_crossing(df, "Avg", target),
        }
        if "Share3Std" in df.columns:
            out["FinalS3Std"] = float(row["Share3Std"])
        rows.append(out)
    finals = pd.DataFrame(rows).sort_values("Backlash")
    finals["FinalAvgCI95"] = 1.96 * finals["FinalAvgStd"] / np.sqrt(n_runs)
    if "FinalS3Std" in finals.columns:
        finals["FinalS3CI95"] = 1.96 * finals["FinalS3Std"] / np.sqrt(n_runs)

    # Final Avg with CI
    plt.figure(figsize=(10, 6))
    plt.errorbar(finals["Backlash"], finals["FinalAvg"],
                 yerr=finals["FinalAvgCI95"], marker="o", capsize=3)
    plt.title("Combo: Final Average vs BACKLASH_SCALE")
    plt.xlabel("BACKLASH_SCALE"); plt.ylabel("Final Average Sustainability")
    plt.tight_layout()
    p_finalavg = os.path.join(pdir, f"combo_backlash_finalavg_{timestamp}.png")
    plt.savefig(p_finalavg); plt.close()

    # Final State3
    plt.figure(figsize=(10, 6))
    if "FinalS3CI95" in finals.columns:
        plt.errorbar(finals["Backlash"], finals["FinalState3"],
                     yerr=finals["FinalS3CI95"], marker="o", capsize=3)
    else:
        plt.plot(finals["Backlash"], finals["FinalState3"], marker="o")
    plt.title("Combo: Final Share of State 3 vs BACKLASH_SCALE")
    plt.xlabel("BACKLASH_SCALE"); plt.ylabel("Final Share in State 3")
    plt.tight_layout()
    p_finalstate3 = os.path.join(pdir, f"combo_backlash_finalstate3_{timestamp}.png")
    plt.savefig(p_finalstate3); plt.close()

    # Time to target
    plt.figure(figsize=(10, 6))
    plt.plot(finals["Backlash"], finals["T_to_Target"], marker="o")
    plt.title(f"Combo: Time to Avg ≥ {target} vs BACKLASH_SCALE")
    plt.xlabel("BACKLASH_SCALE"); plt.ylabel("Steps to target (NaN = not reached)")
    plt.tight_layout()
    p_ttt = os.path.join(pdir, f"combo_backlash_timetotarget_{timestamp}.png")
    plt.savefig(p_ttt); plt.close()

    print("Saved sweep plots:", p_overlay, p_finalavg, p_finalstate3, p_ttt)
    return results


def sweep_halflife(run_monte_carlo, values, steps, n_runs=20, target=0.80,
                   data_dir=".", plot_dir=None, timestamp=""):
    """
    Run 'combo' for several CAMPAIGN_HALF_LIFE values.
    Saves overlay + final-outcome plots to plot_dir and per-value CSVs to data_dir.
    Returns a dict[value] -> summary dataframe.
    """
    _ensure_dir(data_dir)
    pdir = plot_dir or data_dir
    _ensure_dir(pdir)

    orig_fp = getattr(fp, "CAMPAIGN_HALF_LIFE", None)
    orig_ag = getattr(agent_module, "CAMPAIGN_HALF_LIFE", None)

    results = {}
    for hl in values:
        print(f"[sweep_halflife] CAMPAIGN_HALF_LIFE={hl}")
        if orig_fp is not None: setattr(fp, "CAMPAIGN_HALF_LIFE", hl)
        if orig_ag is not None: setattr(agent_module, "CAMPAIGN_HALF_LIFE", hl)

        _, summary = run_monte_carlo("combo", steps=steps, n_runs=n_runs)
        results[hl] = summary
        summary.to_csv(os.path.join(data_dir, f"combo_halflife_{hl}_summary_{timestamp}.csv"), index=False)

    # Restore
    if orig_fp is not None: setattr(fp, "CAMPAIGN_HALF_LIFE", orig_fp)
    if orig_ag is not None: setattr(agent_module, "CAMPAIGN_HALF_LIFE", orig_ag)

    # Overlay trajectories
    plt.figure(figsize=(10, 6))
    for hl, df in results.items():
        plt.plot(df["Step"], df["Avg"], label=f"HL={hl}")
    plt.title("Combo: Sensitivity to Campaign Half-life")
    plt.xlabel("Step"); plt.ylabel("Average Sustainability Score")
    plt.legend(title="Half-life"); plt.tight_layout()
    p_overlay = os.path.join(pdir, f"combo_halflife_overlay_{timestamp}.png")
    plt.savefig(p_overlay); plt.close()

    # Final outcomes & time-to-target (+ CI on FinalAvg)
    rows = []
    for hl, df in results.items():
        row = _final_row(df)
        final_avg = float(row["Avg"])
        final_avg_std = float(row["Std"]) if "Std" in df.columns else float("nan")
        out = {
            "HalfLife": hl,
            "FinalAvg": final_avg,
            "FinalAvgStd": final_avg_std,
            "FinalState3": float(row["Share3"]),
            "T_to_Target": _first_crossing(df, "Avg", target),
        }
        if "Share3Std" in df.columns:
            out["FinalS3Std"] = float(row["Share3Std"])
        rows.append(out)
    finals = pd.DataFrame(rows).sort_values("HalfLife")
    finals["FinalAvgCI95"] = 1.96 * finals["FinalAvgStd"] / np.sqrt(n_runs)
    if "FinalS3Std" in finals.columns:
        finals["FinalS3CI95"] = 1.96 * finals["FinalS3Std"] / np.sqrt(n_runs)

    # Final Avg with CI
    plt.figure(figsize=(10, 6))
    plt.errorbar(finals["HalfLife"], finals["FinalAvg"],
                 yerr=finals["FinalAvgCI95"], marker="o", capsize=3)
    plt.title("Combo: Final Average vs Campaign Half-life")
    plt.xlabel("Campaign Half-life"); plt.ylabel("Final Average Sustainability")
    plt.tight_layout()
    p_finalavg = os.path.join(pdir, f"combo_halflife_finalavg_{timestamp}.png")
    plt.savefig(p_finalavg); plt.close()

    # Final State3
    plt.figure(figsize=(10, 6))
    if "FinalS3CI95" in finals.columns:
        plt.errorbar(finals["HalfLife"], finals["FinalState3"],
                     yerr=finals["FinalS3CI95"], marker="o", capsize=3)
    else:
        plt.plot(finals["HalfLife"], finals["FinalState3"], marker="o")
    plt.title("Combo: Final Share of State 3 vs Campaign Half-life")
    plt.xlabel("Campaign Half-life"); plt.ylabel("Final Share in State 3")
    plt.tight_layout()
    p_finalstate3 = os.path.join(pdir, f"combo_halflife_finalstate3_{timestamp}.png")
    plt.savefig(p_finalstate3); plt.close()

    # Time to target
    plt.figure(figsize=(10, 6))
    plt.plot(finals["HalfLife"], finals["T_to_Target"], marker="o")
    plt.title(f"Combo: Time to Avg ≥ {target} vs Campaign Half-life")
    plt.xlabel("Campaign Half-life"); plt.ylabel("Steps to target (NaN = not reached)")
    plt.tight_layout()
    p_ttt = os.path.join(pdir, f"combo_halflife_timetotarget_{timestamp}.png")
    plt.savefig(p_ttt); plt.close()

    print("Saved half-life sweep plots:", p_overlay, p_finalavg, p_finalstate3, p_ttt)
    return results


def sweep_taxmax(run_monte_carlo, values, steps, n_runs=20, target=0.80,
                 data_dir=".", plot_dir=None, timestamp=""):
    """
    Run 'combo' for several TAX_MAX values.
    Saves overlay + final-outcome plots to plot_dir and per-value CSVs to data_dir.
    Returns a dict[value] -> summary dataframe.
    """
    _ensure_dir(data_dir)
    pdir = plot_dir or data_dir
    _ensure_dir(pdir)

    orig_tax_max = getattr(fp, "TAX_MAX", None)

    results = {}
    for tx in values:
        print(f"[sweep_taxmax] TAX_MAX={tx}")
        if orig_tax_max is not None: setattr(fp, "TAX_MAX", tx)  # tax_signal() reads this at runtime

        _, summary = run_monte_carlo("combo", steps=steps, n_runs=n_runs)
        results[tx] = summary
        summary.to_csv(os.path.join(data_dir, f"combo_taxmax_{tx}_summary_{timestamp}.csv"), index=False)

    # Restore
    if orig_tax_max is not None: setattr(fp, "TAX_MAX", orig_tax_max)

    # Overlay trajectories
    plt.figure(figsize=(10, 6))
    for tx, df in results.items():
        plt.plot(df["Step"], df["Avg"], label=f"TAX_MAX={tx}")
    plt.title("Combo: Sensitivity to TAX_MAX (Price Pressure Ceiling)")
    plt.xlabel("Step"); plt.ylabel("Average Sustainability Score")
    plt.legend(title="TAX_MAX"); plt.tight_layout()
    p_overlay = os.path.join(pdir, f"combo_taxmax_overlay_{timestamp}.png")
    plt.savefig(p_overlay); plt.close()

    # Final outcomes & time-to-target (+ CI on FinalAvg)
    rows = []
    for tx, df in results.items():
        row = _final_row(df)
        final_avg = float(row["Avg"])
        final_avg_std = float(row["Std"]) if "Std" in df.columns else float("nan")
        out = {
            "TAX_MAX": tx,
            "FinalAvg": final_avg,
            "FinalAvgStd": final_avg_std,
            "FinalState3": float(row["Share3"]),
            "T_to_Target": _first_crossing(df, "Avg", target),
        }
        if "Share3Std" in df.columns:
            out["FinalS3Std"] = float(row["Share3Std"])
        rows.append(out)
    finals = pd.DataFrame(rows).sort_values("TAX_MAX")
    finals["FinalAvgCI95"] = 1.96 * finals["FinalAvgStd"] / np.sqrt(n_runs)
    if "FinalS3Std" in finals.columns:
        finals["FinalS3CI95"] = 1.96 * finals["FinalS3Std"] / np.sqrt(n_runs)

    # Final Avg with CI
    plt.figure(figsize=(10, 6))
    plt.errorbar(finals["TAX_MAX"], finals["FinalAvg"],
                 yerr=finals["FinalAvgCI95"], marker="o", capsize=3)
    plt.title("Combo: Final Average vs TAX_MAX")
    plt.xlabel("TAX_MAX"); plt.ylabel("Final Average Sustainability")
    plt.tight_layout()
    p_finalavg = os.path.join(pdir, f"combo_taxmax_finalavg_{timestamp}.png")
    plt.savefig(p_finalavg); plt.close()

    # Final State3
    plt.figure(figsize=(10, 6))
    if "FinalS3CI95" in finals.columns:
        plt.errorbar(finals["TAX_MAX"], finals["FinalState3"],
                     yerr=finals["FinalS3CI95"], marker="o", capsize=3)
    else:
        plt.plot(finals["TAX_MAX"], finals["FinalState3"], marker="o")
    plt.title("Combo: Final Share of State 3 vs TAX_MAX")
    plt.xlabel("TAX_MAX"); plt.ylabel("Final Share in State 3")
    plt.tight_layout()
    p_finalstate3 = os.path.join(pdir, f"combo_taxmax_finalstate3_{timestamp}.png")
    plt.savefig(p_finalstate3); plt.close()

    # Time to target
    plt.figure(figsize=(10, 6))
    plt.plot(finals["TAX_MAX"], finals["T_to_Target"], marker="o")
    plt.title(f"Combo: Time to Avg ≥ {target} vs TAX_MAX")
    plt.xlabel("TAX_MAX"); plt.ylabel("Steps to target (NaN = not reached)")
    plt.tight_layout()
    p_ttt = os.path.join(pdir, f"combo_taxmax_timetotarget_{timestamp}.png")
    plt.savefig(p_ttt); plt.close()

    print("Saved TAX_MAX sweep plots:", p_overlay, p_finalavg, p_finalstate3, p_ttt)
    return results