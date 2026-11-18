# Lab 5 — Static Code Analysis

**File analysed:** `library_system.py`
**Tools:** Pylint, Bandit, Flake8

## Before vs After

| Tool | Before | After |
|---|---|---|
| Pylint | 6.07/10 | **10.00/10** |
| Bandit | 1 Medium, 1 Low | **0 issues** |
| Flake8 | 14 violations | **0 violations** |

Raw reports: `reports_before/` and `reports_after/`.

## Issue Table

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---|---|---|
| Use of `eval` (B307 / W0123) | **Security — Medium** | 45 | `eval()` on a rule string lets arbitrary Python run if the rule comes from a user or file. | Replaced with a small `ast.parse` + `operator` evaluator that only allows `+ - * /`, numeric literals and the name `days`; anything else raises `ValueError`. |
| Bare `except: pass` (B110 / W0702 / E722) | **Security / Bug — Low** | 21–22 | Swallows *every* exception silently, hiding real bugs. | Narrowed to `except (KeyError, ValueError)` and print an explanatory message instead of passing. |
| Mutable default argument (W0102) | **Bug** | 9 | `dates=[]` is created once and shared across all calls, so the count keeps growing. | Default changed to `None`, list created inside the function. |
| Global mutation (W0603) | **Bug / Design** | 28, 35 | `global FINE_PER_DAY` and `global loans` rebind module state, making behaviour order-dependent. | Fine rate moved into a `CONFIG` dict mutated in place; `load_records` uses `loans.clear()` / `loans.update()`. |
| File handles never closed on error (R1732, W1514) | **Bug** | 34, 40 | `open()` without `with` leaks the handle if an exception occurs; no encoding specified. | Rewrote both as `with open(..., encoding="utf-8")`. |
| Unused import (W0611 / F401) | **Style** | 2 | `os` imported but never used. | Removed. |
| Non-PEP8 function name (C0103) | **Style** | 27 | `renewBook` is camelCase. | Renamed to `renew_book`. |
| Missing docstrings (C0114, C0116) | **Style** | module + 8 functions | No module or function documentation. | Added a module docstring and one-line docstrings to every function. |
| Old-style `%` formatting (C0209) | **Style** | 14 | `"%s ... %d" % (...)`. | Converted to an f-string. |
| PEP8 formatting (E302, E305, E501) | **Style** | throughout | One blank line between top-level defs; three lines over 79 chars; `main()` called at import time. | Two blank lines between defs, long lines wrapped, `main()` moved under `if __name__ == "__main__":`. |
| Negative fine (logic) | **Bug** | 24 | `calculate_fine(-3)` returned `-6`, i.e. the library owes the student. | Clamped with `max(0, days_overdue)`. |
| Non-string book id | **Bug** | 56 | `add_book_loan("S103", 4521)` stored an int, breaking `remove()` by string. | Coerced with `str(book_id)` on insert. |

## Commits

1. `fix(bandit)` — safe AST evaluator replacing `eval`, removed bare `try/except/pass`
2. `fix(pylint)` — docstrings, mutable default, f-strings, snake_case, `with open`, no globals (6.07 → 10.00)
3. `fix(flake8)` — PEP8 blank lines, line length, `__main__` guard

## Reflection

**1. What is static analysis and why use it?**
It inspects source code without running it, so it catches defects on paths that tests may never exercise — here, the `eval` vulnerability and the shared mutable default would both have passed a casual run of the program.

**2. Which tool was most useful?**
Bandit found the only genuinely dangerous issue (`eval`), so it had the highest value per finding. Pylint found the most issues overall and was the best guide to design problems (globals, mutable defaults). Flake8 was purely cosmetic but is the cheapest to keep enforced.

**3. Do the tools overlap?**
Yes — the bare `except` was flagged by all three (B110, W0702, E722), and the unused import by both Pylint and Flake8. Pylint is a superset of most of Flake8's checks, but Bandit's security rules are unique to it.

**4. Were any warnings false positives?**
None were strictly wrong, though `consider-using-with` and the missing-docstring checks are style opinions rather than defects. In a small script they could reasonably be suppressed; fixing them was cheap here so nothing was disabled with `# nosec` or `# pylint: disable`.

**5. How does this improve maintainability?**
The fixes made state explicit (no `global`), made failures visible rather than silent, and made every function self-describing. A later reader can now tell what each function does and trust that an error will surface instead of being swallowed.

**6. Would you add this to CI?**
Yes — running all three on every pull request, failing the build on any Bandit finding and on a Pylint score below ~9.5, keeps the codebase from regressing without requiring manual review of style.
