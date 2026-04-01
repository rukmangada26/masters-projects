#!/usr/bin/env python3
"""Build scrubbed *_public.ipynb copies — run from Sem 2/Predictive."""
import copy
import json
import re
from pathlib import Path
from textwrap import dedent

BASE = Path(__file__).resolve().parent
NB_MAIN = BASE / "Predictive_Proj_Code_public.ipynb"
NB_MAIN_OUT = BASE / "Predictive_Proj_Code_public.ipynb"
NB_ETL = BASE / "Predictive_proj_public.ipynb"
NB_ETL_OUT = BASE / "Predictive_proj_public.ipynb"

DISCLAIMER_MAIN = dedent("""
    > **Public (scrubbed) copy:** Real manufacturer / brand labels are replaced with **placeholders** (`MFG_ALPHA`, `MFG_BETA`, …, `FRANCHISE_A`). For this notebook to run on your CSV, those columns must use the **same placeholder strings**, or change the literals in the code. **No dataset is included.** Outputs are cleared.
    """).strip()

DISCLAIMER_ETL = dedent("""
    > **Public (scrubbed) copy:** The manufacturer allow-list uses **placeholder codes** (`MFG_*`) instead of real company names. Pre-map labels in your data or edit the list. Sponsor-specific path hints are generic. **Outputs are cleared.** Modeling: `../Predictive_Proj_Code_public.ipynb`.
    """).strip()


def scrub_text(text: str) -> str:
    """Apply ordered replacements (longest / most specific first)."""
    steps = [
        ("IMPOSSIBLE FOODS INC", "MFG_DELTA"),
        ("BEYOND MEAT INC", "MFG_BETA"),
        ("CONAGRA BRANDS", "MFG_ALPHA"),
        ("KELLANOVA", "MFG_GAMMA"),
        ("GARDEIN", "FRANCHISE_A"),
        ("gardein_filtered.csv", "franchise_a_filtered.csv"),
        ("gardein_data", "franchise_a_data"),
        ("gardein_rows", "franchise_a_rows"),
        ("df_conagra", "df_mfg_alpha"),
        ("conagra_sales", "mfg_alpha_sales"),
        ("conagra_effect", "mfg_alpha_effect"),
        ("kellanova_sales", "mfg_gamma_sales"),
        ("kellanova_effect", "mfg_gamma_effect"),
        ("beyond_sales", "mfg_beta_sales"),
        ("Beyond Meat (Base)", "MFG_BETA (reference)"),
        ("label='Conagra'", "label='MFG_ALPHA'"),
        ("label='Kellanova'", "label='MFG_GAMMA'"),
        # Paths / institution-specific layout
        (
            "Library/CloudStorage/OneDrive-TheUniversityofTexasatDallas/Sem 2/Predictive/Project",
            /Users/rukmangadaruku/Library/CloudStorage/OneDrive-TheUniversityofTexasatDallas/Sem 2/proj for git upload,
        ),
        (
            "Library/CloudStorage/OneDrive-TheUniversityofTexasatDallas/Sem 2/Predictive",
            /Users/rukmangadaruku/Library/CloudStorage/OneDrive-TheUniversityofTexasatDallas/Sem 2/proj for git upload,
        ),
    ]
    for old, new in steps:
        text = text.replace(old, new)

    text = text.replace("utd_proj = Path.home()", "fallback_proj = Path.home()")
    text = text.replace("if utd_proj.is_dir()", "if fallback_proj.is_dir()")
    text = text.replace("(utd_proj /", "(fallback_proj /")
    text = text.replace("    utd = Path.home()", "    fallback_root = Path.home()")
    text = text.replace("if utd.is_dir():", "if fallback_root.is_dir():")
    text = text.replace("(utd /", "(fallback_root /")
    text = re.sub(r"\butd\b", "fallback_root", text)  # remaining variable name
    text = text.replace("Typical UTD OneDrive layout", "Optional Path.home() fallback")

    # Markdown / titles (case variants)
    text = text.replace("Conagra-only", "Single MFG (MFG_ALPHA)")
    text = text.replace("Conagra", "Sponsor org")
    text = text.replace("CONAGRA", "MFG_ALPHA")
    text = text.replace(
        "## Appendix A — Single-manufacturer subset (Sponsor org)\n\nSame sklearn `Pipeline` idea on rows where manufacturer name contains `MFG_ALPHA`",
        "## Appendix A — Single-manufacturer subset (MFG_ALPHA)\n\nSame sklearn `Pipeline` idea on rows where manufacturer name contains `MFG_ALPHA`",
    )
    text = text.replace(
        "Reuse `df_raw` from the first cell; Sponsor org-only rows",
        "Reuse `df_raw` from the first cell; filter to rows with Manufacturer Name matching MFG_ALPHA",
    )
    text = text.replace(
        "## Appendix C — Optional: extract one brand from large CSV\n\nChunked read to pull rows matching a brand string and write `data/franchise_a_filtered.csv`.",
        "## Appendix C — Optional: extract one franchise from large CSV\n\nChunked read to pull rows matching a franchise string and write `data/franchise_a_filtered.csv`.",
    )

    return text


def scrub_nb(path_in: Path, path_out: Path, disclaimer: str, etl: bool):
    with open(path_in, encoding="utf-8") as f:
        nb = json.load(f)
    nb = copy.deepcopy(nb)
    new_cells = []

    # Insert disclaimer markdown
    new_cells.append(
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [disclaimer + "\n"],
        }
    )

    for cell in nb["cells"]:
        c = copy.deepcopy(cell)
        c["execution_count"] = None
        c["outputs"] = []
        if c["cell_type"] in ("markdown", "code"):
            src = "".join(c.get("source", []))
            src = scrub_text(src)
            if etl:
                src = src.replace(
                    "../Predictive_Proj_Code.ipynb",
                    "../Predictive_Proj_Code_public.ipynb",
                )
                src = src.replace(
                    '(p / "Predictive_proj.ipynb").is_file()',
                    '((p / "Predictive_proj.ipynb").is_file() or (p / "Predictive_proj_public.ipynb").is_file())',
                )
                src = src.replace(
                    '(proj / "Predictive_proj.ipynb").is_file()',
                    '((proj / "Predictive_proj.ipynb").is_file() or (proj / "Predictive_proj_public.ipynb").is_file())',
                )
                src = src.replace(
                    'Folder containing `Predictive_proj.ipynb`',
                    "Folder containing this notebook (`Predictive_proj.ipynb` or `Predictive_proj_public.ipynb`)",
                )
            else:
                src = src.replace(
                    '(p / "Predictive_Proj_Code.ipynb").is_file()',
                    '((p / "Predictive_Proj_Code.ipynb").is_file() or (p / "Predictive_Proj_Code_public.ipynb").is_file())',
                )
                src = src.replace(
                    'Folder containing `Predictive_Proj_Code.ipynb`',
                    "Folder containing `Predictive_Proj_Code.ipynb` or `Predictive_Proj_Code_public.ipynb`",
                )
            c["source"] = src.splitlines(keepends=True)
        new_cells.append(c)

    nb["cells"] = new_cells
    with open(path_out, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print("Wrote", path_out, "cells", len(new_cells))


def post_clean(path_out: Path):
    with open(path_out, encoding="utf-8") as f:
        nb = json.load(f)
    for c in nb["cells"]:
        if c["cell_type"] == "markdown":
            c.pop("execution_count", None)
            c.pop("outputs", None)
        src = "".join(c.get("source", []))
        src = src.replace(
            "Top 15 Important Features (LASSO Regression (subset MFG_ALPHA))",
            "Top 15 Important Features (LASSO, MFG_ALPHA subset)",
        )
        src = src.replace(
            "# Reuse `df_raw` from the first cell; Single MFG (MFG_ALPHA) rows\n",
            "# Reuse `df_raw` from the first cell; filter to rows with Manufacturer Name matching MFG_ALPHA\n",
        )
        if c["cell_type"] in ("markdown", "code"):
            c["source"] = src.splitlines(keepends=True)
    with open(path_out, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
        f.write("\n")


def main():
    scrub_nb(NB_MAIN, NB_MAIN_OUT, DISCLAIMER_MAIN, etl=False)
    scrub_nb(NB_ETL, NB_ETL_OUT, DISCLAIMER_ETL, etl=True)
    post_clean(NB_MAIN_OUT)
    post_clean(NB_ETL_OUT)


if __name__ == "__main__":
    main()
