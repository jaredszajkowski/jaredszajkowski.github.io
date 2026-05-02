# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal quantitative finance blog at https://www.jaredszajkowski.com, built with Hugo (Congo theme) and automated with PyDoit. Blog posts are authored as Jupyter notebooks, executed, exported to Markdown, then assembled into Hugo content.

## Key Commands

### Hugo (site)
```bash
hugo server          # Local dev server
hugo                 # Build site to public/
```

### PyDoit (full build pipeline)
```bash
doit                 # Run all tasks in dependency order
doit <task_name>     # Run a specific task (e.g., doit run_post_notebooks)
```

**Task execution order** (each depends on the prior):
1. `config` — create required directories
2. `list_posts_subdirs` — enumerate post directories
3. `run_post_notebooks` — execute changed notebooks (hash-based change detection)
4. `export_post_notebooks` — convert to HTML, PDF, and Markdown
5. `build_post_indices` — combine `frontmatter.md` + notebook `.md` → `index.md`
6. `clean_public` — remove `public/`
7. `build_site` — run `hugo`
8. `copy_notebook_exports` — copy `.html` exports into `public/posts/<slug>/`
9. `copy_projects_research_exports` — copy research HTML into `public/projects-research/`
10. `create_schwab_callback` — write OAuth callback page

### Python dependencies
```bash
pip install -r requirements.txt
```

### Code formatting
```bash
black src/           # Format Python source files
```

## Architecture

### Content pipeline
Each post lives in `content/posts/<post-name>/` and follows one of two patterns:

**Notebook-driven posts** (most common):
- `<post-name>.ipynb` — the source notebook (executed in place by `jupyter nbconvert`)
- `frontmatter.md` — Hugo front matter only (title, date, tags, etc.)
- `dodo.py` combines these: `frontmatter.md` + exported `<post-name>.md` → `index.md`, then appends a `{{< post-files >}}` shortcode

**Template-driven posts**:
- `index_temp.md` + `index_dep.txt` — `src/build_index.py` assembles `index.md` from these

### Configuration
- `src/settings.py` is the single source of truth for all directory paths. It uses `python-decouple` and reads from `.env` at the repo root (`BASE_DIR / .env`). All path variables (`BASE_DIR`, `WEBSITES_DIR`, `CONTENT_DIR`, `POSTS_DIR`, `PAGES_DIR`, `PUBLIC_DIR`, `SOURCE_DIR`, `DATA_DIR`, `DATA_MANUAL_DIR`, `OS_TYPE`) are defined in a `defaults` dict and exposed via `config(var_name)`; values from the `.env` file are merged on top of these defaults. `dodo.py` imports `config` and resolves all paths through it.
- Data directories (`Data/`, `Data_Manual/`) live one level up from the repo root, inside the shared `Websites/` parent.
- Hugo config is split across `config/_default/`: `hugo.toml` (core), `params.toml` (Congo theme), `languages.en.toml`, `menus.en.toml`.

### Python source (`src/`)
Scripts are standalone and follow naming conventions:
- `yf_*`, `ndl_*`, `polygon_*`, `coinbase_*`, `databento_*` — data fetch/process per source (each typically has `_pull_data`, `_process_data`, `_month_end`, `_quarter_end` variants)
- `schwab_*` — Schwab brokerage integration (OAuth via `schwab_oauth.py`, order history via `schwab_order_history.py`)
- `coinbase_trading_bot.py`, `*_websocket.py` — live trading / streaming clients
- `plot_*` — visualization helpers (time series, bar, scatter, histogram, heatmap, regression, equity/drawdown, etc.)
- `backtest_*`, `create_signals.py`, `compute_daily_performance.py`, `analyze_trades.py`, `calc_*`, `add_rsi_ma_bb.py`, `calculate_rsi.py`, `strategy_harry_brown_perm_port.py` — signal generation, strategy backtests, and trade/PnL analysis
- `run_regression.py`, `summary_stats.py`, `sm_ols_summary_markdown.py`, `df_info*.py`, `pandas_set_decimal_places.py`, `round_to_nice_value.py`, `label_start_end_min_max.py` — statistics, formatting, and DataFrame utilities
- `build_index.py`, `list_posts_subdirs.py`, `export_track_md_deps.py` — content pipeline helpers invoked by `dodo.py`
- `settings.py`, `load_api_keys.py` — shared config/credentials utilities

### Notebook change detection
`dodo.py` hashes code and markdown cells of each notebook (`notebook_source_hash()`). If the hash matches the stored `.last_source_hash` file, the notebook is skipped. This avoids re-executing expensive notebooks on every build.

### Theme
Congo theme is installed as a git submodule under `themes/congo/`. Custom color overrides live in `assets/css/custom.css`.

### Deployment
GitHub Actions (`.github/workflows/hugo.yaml`) builds and deploys to GitHub Pages on push to `main` (or via `workflow_dispatch`). It caches Hugo's image processing output. The workflow uses Hugo 0.158.0 (extended), Node.js 24.14.0, Go 1.26.1, and Dart Sass 1.98.0, and checks out submodules recursively so the Congo theme is included.

### Notes / gotchas
- The `doit deploy_site` task is currently commented out in `dodo.py`; commits and pushes are done manually.
- `task_copy_notebook_exports` writes notebook HTML to `public/posts/<slug>/<slug>.html` (date-based paths are no longer used; the date in front matter is parsed but not used in the output path).
