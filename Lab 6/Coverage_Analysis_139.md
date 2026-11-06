# Lab 6 - Code Coverage and Branch Coverage Analysis

- Name: D Pranav Sai
- SRN: PES1UG24CS139
- Application: Pet Walking Service
- Repository: SETAPESU26/L6_L7_13_pet_walking_service
- Branch: main
- Source revision inspected: 2a74fd3
- Execution date: 6 November 2026

## Scope and repository inspection

All six original repository files were inspected. `Lab 6/README.md` identifies
`Lab 6/pet_walking_service.py` as the Lab 6 application and
`Lab 6/test_pet_walking.py` as its starter suite. The other three files,
`Lab 7/README.md`, `Lab 7/processor.py`, and `Lab 7/test_processor.py`, concern a
separate Hypothesis fuzz-testing exercise and are outside this Lab 6 measurement.
No application, starter test, or Lab 7 file was modified.

The assignment documents supply the repository allocation and lab requirements.
The user's request determines the two separate test filenames, terminal text
deliverables, local commits, and prohibition on pushing. This submission provides
actual captured terminal text in the requested `Lab6_Screenshots` directory;
these `.txt` files are terminal transcripts, not image screenshots.

## Application behavior and control-flow inventory

The application has two functions, no classes, no imports, and no exception
handlers. It has one explicit `raise ValueError` at line 3; malformed nested
objects can also propagate native `TypeError` or `AttributeError` exceptions.
All line references below refer to the unchanged application.

| Function / lines | Decisions, loops, and behavior |
| --- | --- |
| `process_walking_routes`, 1-59 | Accepts a routes list and a nonnegative transport fee; returns a revenue/status dictionary. |
| 2-3 | Rejects a non-list OR a negative fee. Tests exercise each validation operand, including short-circuit rejection, and acceptance at fee zero. |
| 8-10 | Outer route loop; unconfirmed or missing confirmation skips the route. Zero, one, and multiple routes are tested. |
| 12-23 | Defaults to `standard_30` and empty walks. Session chain selects `standard_60` (35), `standard_30` (22), or `express_15` (14); unknown sessions increment incidents and skip the route. |
| 27-34 | Inner walk loop; pet counts default to zero. Nonpositive counts increment incidents and skip the rest of that walk. Empty, single, and multiple walks are tested. |
| 36-41 | Aggression increments incidents. For `standard_60`, it clears all prior earnings on that route and breaks the walk loop. Other sessions add zero for the walk and continue to the medication decision. |
| 42-45 | More than three pets: `(base_fee + pets * 8) * 0.90`; otherwise `base_fee + pets * 5`. Tests include 1, 3, and 4 pets and all three session prices. |
| 47-48 | Medication adds 6 unless a prior continue/break bypasses it. Both outcomes and bypass cases are tested. |
| 50-53 | Weekend adds the transport fee once per confirmed valid-session route, even for an empty or aggression-cancelled route. Route earnings accumulate across routes. |
| 55-59 | More than four incidents returns `INCIDENT_AUDIT`, taking precedence over zero earnings. Otherwise zero revenue returns `ZERO_EARNINGS`; positive revenue returns `COMPLETED`. Revenue is rounded to two decimals. |
| `inspect_gps_collars`, 62-75 | Returns GPS status from nested collar signal sequences. |
| 63-64 | Falsy matrix returns `NO_DATA`; both empty list and `None` are tested as currently implemented. |
| 66-68 | Nested collar/log loops; streak starts at zero for each collar. Tests include empty rows, one/multiple collars, and zero/one/multiple signals. An empty outer list exits at the preceding guard. |
| 69-74 | Signal below 20 increments a streak; streak of at least two immediately returns `LOST_SIGNAL_ALERT`. Signal of 20 or above resets the streak. Tests distinguish adjacent lows, separated lows, and lows on different collars. |
| 75 | Exhausting the matrix without an alert returns `ONLINE`. |

There are 20 branch points measured by coverage.py (40 possible outcomes),
including loop continuation/exhaustion and condition outcomes. Ordinary statements
initialize accumulators, read defaults, calculate fees, accumulate revenue, and
return results; all 57 executable statements were executed by each new suite.

## Line coverage versus branch coverage

Line coverage measures executed executable statements divided by executable
statements. Branch coverage measures executed control-flow destinations divided
by possible destinations. Executing the body of an `if` once does not prove its
false path has been exercised. Full branch coverage also does not prove every
combination of paths, condition operands, or possible input has been tested.

In branch mode, the coverage terminal `Cover` column combines statements and
branches. It must not be mistaken for branch-only coverage. The branch-only
percentages below use coverage JSON's `covered_branches / num_branches`.

## Measured results

Environment: Python 3.12.4, pytest 9.2.0, coverage.py 7.17.2. The virtual
environment is in the parent workspace's `work/venv`, outside the repository.

| Suite / independent run | Tests passing | Statements | Line coverage | Branch outcomes | Branch-only coverage | Terminal Cover |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Starter, line mode | 1 | 27/57 | 47.37% | Not measured | Not measured | 47% |
| Starter, branch mode | 1 | 27/57 | 47.37% | 15/40 | 37.50% | 43% |
| `CodeCoverageTest_139_application.py`, line mode | 42 | 57/57 | 100% | Not measured in this run | Not measured | 100% |
| `BranchCoverageTest_139_application.py`, branch mode | 63 | 57/57 | 100% | 40/40 | 100% | 100% |

All coverage erase, run, and report commands exited with code 0. Each suite was
run after its own erase; results were not combined to reach the target.

## Initially untested statements and branches

The starter tests only one confirmed weekday `standard_30` walk with one pet,
no aggression, and no medication. It never calls the GPS function.

Initial missing lines (30):

```text
3, 10, 16, 19, 20, 22, 23, 33, 34, 37, 38, 39, 40, 41,
43, 48, 51, 56, 58, 63, 64, 66, 67, 68, 69, 70, 71, 72, 74, 75
```

Initial missing branch arcs (source line -> destination line; 25):

```text
2->3, 9->10, 15->16, 17->19, 19->20, 19->22, 32->33,
36->37, 38->39, 38->41, 42->43, 47->48, 50->51, 55->56,
57->58, 63->64, 63->66, 66->67, 66->75, 68->66, 68->69,
69->70, 69->74, 71->68, 71->72
```

These gaps correspond to input rejection, skipping routes, alternate/invalid
sessions, invalid pet counts, aggression and break behavior, bulk-pet pricing,
medication, weekends, audit/zero status results, and the entire GPS body.

## Additional cases that improved coverage

Both suites execute real application functions without mocks. Parameterized
cases cover every session, the three/four-pet pricing boundary, medication,
weekend fees, empty/default inputs, multiple routes and walks, incident counts
at four and five, and zero/positive earnings with audit precedence. Aggression
tests verify both continued short sessions and cancellation of long sessions;
an unreachable malformed sentinel after the break proves later walks are skipped.
GPS tests exercise signals 19 and 20, consecutive-low early returns, healthy
signals resetting the streak, and streak isolation between collars. Native-error
tests document existing behavior for malformed nested objects, rather than
assuming validation not present in the source. Rounding is asserted directly.

## Reproduction and coverage scope

Run commands from `Lab 6` after installing `pytest==9.2.0` and
`coverage==7.17.2`. The captured runs use `COVERAGE_RCFILE` pointing to this
configuration (stored in the parent workspace's `work/coverage.ini`):

```ini
[run]
source = pet_walking_service

[report]
exclude_lines =
```

This selects the full Lab 6 application module and sets no excluded lines;
test-file execution is not counted toward the coverage percentage. No application
code or branches were omitted to increase results. `COVERAGE_FILE` stores raw
data outside the repository, and `PYTEST_ADDOPTS=-p no:cacheprovider` avoids
pytest cache artifacts. Neither setting changes application behavior.

With this configuration active, the exact required command sequences were:

```text
coverage erase
coverage run -m pytest CodeCoverageTest_139_application.py -v
coverage report -m

coverage erase
coverage run --branch -m pytest BranchCoverageTest_139_application.py -v
coverage report -m
```

For a fresh checkout without that external configuration, the equivalent
self-contained commands select the application explicitly:

```text
coverage erase
coverage run --source=pet_walking_service -m pytest CodeCoverageTest_139_application.py -v
coverage report -m
coverage erase
coverage run --source=pet_walking_service --branch -m pytest BranchCoverageTest_139_application.py -v
coverage report -m
```

The initial runs used the same scope/configuration and commands with
`test_pet_walking.py`. Machine-readable JSON reports were also generated with
`coverage json` to calculate the exact statement/branch counts and missing arcs.
Full initial terminal reports are reproduced below for auditability.

## Remaining uncovered code and limitations

Remaining uncovered lines: none. Remaining uncovered branches: none.
Excluded lines: zero. Partial branches: zero.

The target was achieved without changing business logic or suppressing code.
Coverage demonstrates execution, not proof of correctness for every input.
Existing permissive or surprising behavior is recorded by assertions; comprehensive
schema validation, exhaustive path coverage, and Lab 7 fuzz testing are outside
this assignment. The original starter test remains intact.

## Initial line coverage terminal output

```text
Initial line coverage
Working directory: C:\Users\prana\Documents\Codex\2026-11-06\lab-6-code-coverage-and-branch\L6_L7_13_pet_walking_service\Lab 6
Python: 3.12.4
Coverage scope: pet_walking_service only; no excluded lines or branches.
Equivalent portable setup: coverage run --source=pet_walking_service [--branch] -m pytest <file> -v
COVERAGE_RCFILE points to [run] source = pet_walking_service; [report] exclude_lines is empty.
PYTEST_ADDOPTS=-p no:cacheprovider; COVERAGE_FILE is stored outside the repository.

> coverage erase

Exit code: 0

> coverage run -m pytest test_pet_walking.py -v
============================= test session starts =============================
platform win32 -- Python 3.12.4, pytest-9.2.0, pluggy-1.7.0 -- C:\Users\prana\Documents\Codex\2026-11-06\lab-6-code-coverage-and-branch\work\venv\Scripts\python.exe
rootdir: C:\Users\prana\Documents\Codex\2026-11-06\lab-6-code-coverage-and-branch\L6_L7_13_pet_walking_service\Lab 6
collecting ... collected 1 item

test_pet_walking.py::test_single_standard_30_walk PASSED                 [100%]

============================== 1 passed in 0.06s ==============================
Exit code: 0

> coverage report -m
Name                     Stmts   Miss  Cover   Missing
------------------------------------------------------
pet_walking_service.py      57     30    47%   3, 10, 16, 19-23, 33-34, 37-41, 43, 48, 51, 56, 58, 63-75
------------------------------------------------------
TOTAL                       57     30    47%
Exit code: 0
```

## Initial branch coverage terminal output

```text
Initial branch coverage
Working directory: C:\Users\prana\Documents\Codex\2026-11-06\lab-6-code-coverage-and-branch\L6_L7_13_pet_walking_service\Lab 6
Python: 3.12.4
Coverage scope: pet_walking_service only; no excluded lines or branches.
Equivalent portable setup: coverage run --source=pet_walking_service [--branch] -m pytest <file> -v
COVERAGE_RCFILE points to [run] source = pet_walking_service; [report] exclude_lines is empty.
PYTEST_ADDOPTS=-p no:cacheprovider; COVERAGE_FILE is stored outside the repository.

> coverage erase

Exit code: 0

> coverage run --branch -m pytest test_pet_walking.py -v
============================= test session starts =============================
platform win32 -- Python 3.12.4, pytest-9.2.0, pluggy-1.7.0 -- C:\Users\prana\Documents\Codex\2026-11-06\lab-6-code-coverage-and-branch\work\venv\Scripts\python.exe
rootdir: C:\Users\prana\Documents\Codex\2026-11-06\lab-6-code-coverage-and-branch\L6_L7_13_pet_walking_service\Lab 6
collecting ... collected 1 item

test_pet_walking.py::test_single_standard_30_walk PASSED                 [100%]

============================== 1 passed in 0.06s ==============================
Exit code: 0

> coverage report -m
Name                     Stmts   Miss Branch BrPart  Cover   Missing
--------------------------------------------------------------------
pet_walking_service.py      57     30     40     11    43%   3, 10, 16, 19-23, 33-34, 37-41, 43, 48, 51, 56, 58, 63-75
--------------------------------------------------------------------
TOTAL                       57     30     40     11    43%
Exit code: 0
```
