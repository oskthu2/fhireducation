#!/usr/bin/env python3
"""Sammanfattar resultatet från FHIR Validator (-output) som en Markdown-tabell.

Skriver till stdout och, i GitHub Actions, till jobbets sammanfattning ($GITHUB_STEP_SUMMARY).
Avslutar med felkod 1 om någon instans har fel (severity error/fatal).
"""
import json
import os
import sys

FILE_EXT = "http://hl7.org/fhir/StructureDefinition/operationoutcome-file"
LINE_EXT = "http://hl7.org/fhir/StructureDefinition/operationoutcome-issue-line"
ICONS = {"fatal": "⛔", "error": "❌", "warning": "⚠️", "information": "ℹ️"}


def ext_value(element, url):
    for ext in element.get("extension", []):
        if ext.get("url") == url:
            for key, value in ext.items():
                if key.startswith("value"):
                    return value
    return None


def outcomes(result):
    if result.get("resourceType") == "Bundle":
        return [entry["resource"] for entry in result.get("entry", [])]
    return [result]


def main(path):
    with open(path, encoding="utf-8") as f:
        result = json.load(f)

    lines = ["## Resultat från FHIR Validator", ""]
    total_errors = 0
    for oo in outcomes(result):
        file_name = os.path.basename(ext_value(oo, FILE_EXT) or "okänd fil")
        issues = oo.get("issue", [])
        errors = sum(1 for i in issues if i.get("severity") in ("error", "fatal"))
        warnings = sum(1 for i in issues if i.get("severity") == "warning")
        total_errors += errors
        status = "✅ Giltig" if errors == 0 else "❌ Ogiltig"
        lines.append(f"### `{file_name}` – {status} ({errors} fel, {warnings} varningar)")
        lines.append("")
        shown = [i for i in issues if i.get("severity") != "information"
                 and not (i.get("details", {}).get("text") or "").startswith("All OK")]
        if not shown:
            lines.append("Inga fel eller varningar.")
        else:
            lines.append("| | Rad | Var | Meddelande |")
            lines.append("|---|---|---|---|")
            for issue in shown:
                icon = ICONS.get(issue.get("severity"), "")
                line = ext_value(issue, LINE_EXT) or ""
                where = ", ".join(issue.get("expression") or issue.get("location") or [])
                text = (issue.get("details", {}).get("text") or issue.get("diagnostics") or "")
                text = text.replace("|", "\\|").replace("\n", " ")
                lines.append(f"| {icon} | {line} | `{where}` | {text} |")
        lines.append("")

    report = "\n".join(lines)
    print(report)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(report + "\n")
    return 1 if total_errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
