#
# Copyright (c) 2026 PANTHEON.tech, s.r.o. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html
#

"""Write a short PyTest result overview to the GitHub Actions job summary.

Reads the summary.json and test-results.json files that `allure generate`
writes next to the report, so it runs after it in tox's commands_post.
Does nothing outside GitHub Actions, where GITHUB_STEP_SUMMARY is not set.
"""

import json
import os
import pathlib
import sys

STATUSES = ("passed", "failed", "broken", "skipped", "unknown")


def render(summary: dict, results: dict) -> str:
    stats = summary.get("stats", {})
    lines = [
        f"### PyTest results: {summary.get('status', 'unknown').upper()}",
        "",
        "| Total | " + " | ".join(s.capitalize() for s in STATUSES) + " |",
        "|---" * (len(STATUSES) + 1) + "|",
        f"| {stats.get('total', 0)} | "
        + " | ".join(str(stats.get(s, 0)) for s in STATUSES)
        + " |",
    ]

    problems = sorted(
        (result["status"], result["name"])
        for result in results.get("byId", {}).values()
        if result.get("status") in ("failed", "broken")
    )
    if problems:
        lines += ["", "Failed tests:", ""]
        lines += [f"- `{name}` ({status})" for status, name in problems]

    return "\n".join(lines) + "\n"


def main(report_dir: str = "allure-report") -> None:
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_file:
        return

    report = pathlib.Path(report_dir)
    summary = json.loads((report / "summary.json").read_text())
    results = json.loads((report / "test-results.json").read_text())
    with open(summary_file, "a") as out:
        out.write(render(summary, results))


if __name__ == "__main__":
    main(*sys.argv[1:])
