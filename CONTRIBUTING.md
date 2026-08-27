# Contributing

## Environment

Use Python 3.12 or 3.13 and the locked uv environment.

```powershell
uv sync --frozen
npm ci
```

## Required checks

```powershell
uv run python scripts/generate_teaching_data.py --check
uv run python scripts/check_publication.py
uv run python scripts/validate_test_notebooks.py
uv run python scripts/execute_lessons.py
uv run pytest -q
npm test
uv run python scripts/build_site.py
npm run test:e2e
```

Lesson notebooks may contain real executed outputs only after a top-to-bottom run. Test notebooks must keep execution counts null, outputs empty, and learner answer variables set to `None`.

Do not add analytics, remote form endpoints, or identity collection. Certificate names and scores remain in the learner's browser.
