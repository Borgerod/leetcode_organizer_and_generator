# Tools

---

## Table of Contents

- [Tools](#tools)
  - [Table of Contents](#table-of-contents)
  - [Devops commands - push, build, release.](#devops-commands---push-build-release)
  - [PowerShell](#powershell)
    - [commands](#commands)
    - [patch](#patch)
    - [minor](#minor)
    - [major](#major)
    - [build + release without pushing](#build--release-without-pushing)
  - [CMD](#cmd)
    - [commands](#commands-1)
    - [patch](#patch-1)
    - [minor](#minor-1)
    - [major](#major-1)
    - [build + release without pushing](#build--release-without-pushing-1)

---

## Devops commands - push, build, release.

_after staging changes_
updating patch will only push.
minor - will also build and release.
major - will also build and release.

---

## PowerShell

### commands

```powershell
# note: --release is optional
actions update patch --release
actions update minor --release
actions update major --release
```

### patch

```powershell
.venv\Scripts\Activate.ps1
bumpver update --patch
python scripts/generate_commit.py
git push --follow-tags
```

### minor

```powershell
.venv\Scripts\Activate.ps1
bumpver update --minor
python scripts/generate_commit.py
python -m pip install --upgrade build
python -m build
git push --follow-tags
gh release create "v$(bumpver show --current-version)" --title "v$(bumpver show --current-version)" --notes "Automated release"
```

### major

```powershell
.venv\Scripts\Activate.ps1
bumpver update --major
python scripts/generate_commit.py
python -m pip install --upgrade build
python -m build
git push --follow-tags
gh release create "v$(bumpver show --current-version)" --title "v$(bumpver show --current-version)" --notes "Automated release"
```

### build + release without pushing

```powershell
python -m pip install --upgrade build
python -m build
git push --follow-tags
gh release create "v$(bumpver show --current-version)" --title "v$(bumpver show --current-version)" --notes "Automated release"
$env:PYPI_TOKEN = Get-Content keys\pypi.txt
python -m pip install --upgrade twine
twine upload dist\* -u __token__ -p $env:PYPI_TOKEN
```

NOTE: if you get errors make sure that the builds in dist are not bugged

---

## CMD

### commands

```cmd
rem note: --release is optional
actions update patch --release
actions update minor --release
actions update major --release
```

### patch

```cmd
.venv\Scripts\activate
bumpver update --patch
python scripts/generate_commit.py
git push --follow-tags
```

### minor

```cmd
.venv\Scripts\activate
bumpver update --minor
python scripts/generate_commit.py
python -m pip install --upgrade build
python -m build
git push --follow-tags
for /f %v in ('bumpver show --current-version') do set VERSION=%v
gh release create v%VERSION% --title "v%VERSION%" --notes "Automated release"
```

### major

```cmd
.venv\Scripts\activate
bumpver update --major
python scripts/generate_commit.py
python -m pip install --upgrade build
python -m build
git push --follow-tags
for /f %v in ('bumpver show --current-version') do set VERSION=%v
gh release create v%VERSION% --title "v%VERSION%" --notes "Automated release"
```

### build + release without pushing

```cmd
python -m pip install --upgrade build
python -m build
git push --follow-tags
for /f %v in ('bumpver show --current-version') do set VERSION=%v
gh release create v%VERSION% --title "v%VERSION%" --notes "Automated release"
set /p PYPI_TOKEN=<keys\pypi.txt
python -m pip install --upgrade twine
twine upload dist\* -u __token__ -p %PYPI_TOKEN%
```

NOTE: if you get errors make sure that the builds in dist are not bugged
