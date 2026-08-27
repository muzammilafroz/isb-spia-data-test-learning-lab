# Applied Data Coding Learning Lab

Learn reproducible Python through geospatial joins, household survey cleaning, regression, and research validation.

This is an independent educational resource, not an official assessment, credential, or answer repository. Every public data row is independently simulated for teaching. No controlled survey microdata or original recruitment materials are included.

- [Open the learning site](https://muzammilafroz.github.io/applied-economics-data-learning-lab/)
- [Run notebooks in JupyterLite](https://muzammilafroz.github.io/applied-economics-data-learning-lab/lab/)
- [Open the self-study test center](https://muzammilafroz.github.io/applied-economics-data-learning-lab/tests/)

## Learning routes

- Read the course at the GitHub Pages site.
- Run lesson and test notebooks immediately in the browser through JupyterLite.
- Open notebooks in Google Colab for a full hosted Python runtime.
- Submit notebook outputs to local browser tests. Answers and progress never leave the browser.

## Course structure

1. Python and pandas foundations
2. Geospatial validation and mapping
3. Household rates and reproducible cleaning
4. Regression, fixed effects, and credibility
5. Validation, reproducibility, and interview defense
6. Integrated capstone

## Local development

```powershell
uv sync --frozen
uv run python scripts/build_notebooks.py
uv run python scripts/execute_lessons.py --write
uv run python scripts/generate_teaching_data.py --check
uv run python scripts/validate_test_notebooks.py
uv run pytest
npm ci
npm test
uv run python scripts/build_site.py
npm run test:e2e
```

The website build and browser checks are documented in `CONTRIBUTING.md`.

## Public data boundary

All data are deterministic simulations. The project does not contain an original recruitment prompt, controlled microdata, candidate work, or public replicas of private results. Official DHS-style microdata require controlled user access and are not redistributed here.

## Licensing

- Code: MIT, see `LICENSE-CODE`.
- Instructional prose and notebooks: CC BY 4.0, see `LICENSE-CONTENT`.
- Synthetic teaching data: CC0 1.0, see `data/teaching/LICENSE`.
