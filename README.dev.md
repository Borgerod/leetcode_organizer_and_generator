# Developer Release Guide

This file is for the package maintainer of `leetcrate`.
It explains exactly how to bump version, push, and optionally publish to PyPI.

## What You Should Normally Use

Use these commands. This is the main workflow.

```powershell
# --release is optional
actions update patch --release
actions update minor --release
actions update major --release
```

If you do not want to publish to PyPI, run the same commands without `--release`:

```powershell
actions update patch
actions update minor
actions update major
```

## What `actions update` Does

For `patch`, `minor`, and `major`, the script does this for you:

1. **Verifies version bump** — checks GitHub for latest version and ensures you're not skipping versions.
2. Runs `bumpver` with the correct bump type.
3. Updates version in all configured files (from `bumpver.toml`).
4. Builds package artifacts.
5. Pushes commits and tags (after confirmation prompt).
6. If `--release` is included: creates GitHub release and uploads to PyPI.

## Version Safety Features

### ✓ Automatic Version Verification

Before bumping, `actions update` checks:

- Your local version vs. GitHub's latest version
- Whether the new version is the correct next iteration (prevents skipping versions)

If something seems off, you'll be prompted to confirm before proceeding.

This prevents mistakes like:

```
GitHub: [..., v1.2.2, v1.2.3]
You bump patch → creates v1.2.5 (skipped v1.2.4)
```

### ✓ Rollback if You Change Your Mind (Before Push)

If you press ESC at the confirmation prompt, the version bump is rolled back completely.
Code changes are preserved; only the version revert is committed.

## Bumpver Rule (Important)

Do not manually edit version numbers in package files.
Do not run `bumpver update ...` manually.

**Always use `actions update ...`** so version verification runs.

`bumpver.toml` is configured to update all version fields consistently across the project.

## Recover from Mistakes

### Scenario 1: Bumped locally but changed your mind

If you've bumped the version locally but **haven't pushed** yet, and want to undo **only the version** (keeping your code changes):

```powershell
actions rollback-version
```

This will:

- Revert version files to previous commit
- Preserve all your code changes
- Create a new commit that undoes the version bump

### Scenario 2: Bumped and pushed to GitHub by mistake

If you've already pushed a version bump and need to fix it:

1. Fix your code locally (if needed)
2. Run `actions rollback-version` to undo the bump commit
3. Run `actions update [patch|minor|major]` again to bump correctly

Then you'll need to force-push (use with caution):

```powershell
git push origin main --force-with-lease --follow-tags
```

## Manual / Custom Flow (Advanced)

Use this only if you intentionally do not want to use `actions update`.

<details>
<summary>Manual publish commands (PowerShell)</summary>

```powershell
python -m pip install --upgrade build
python -m build
git push --follow-tags
gh release create "v$(bumpver show --current-version)" --title "v$(bumpver show --current-version)" --notes "Automated release"
$env:PYPI_TOKEN = Get-Content keys\pypi.txt
python -m pip install --upgrade twine
twine upload dist\* -u __token__ -p $env:PYPI_TOKEN
```

</details>
