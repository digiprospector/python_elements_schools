#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Export project problem banks to JSON.
"""

import argparse
import json
from datetime import datetime

from problem_catalog import PROJECT_CATALOG, build_project_problems, find_catalog_entry


def export_project(entry, output_path):
    problems = build_project_problems(entry)
    payload = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "subject": entry["subject"],
        "grade": entry["grade"],
        "project": entry["project"],
        "total_count": len(problems),
        "problems": problems,
    }
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    return len(problems)


def main():
    parser = argparse.ArgumentParser(description="Export a tagged problem bank to JSON.")
    parser.add_argument("--subject", default="数学", help="Subject name")
    parser.add_argument("--grade", default="小二下", help="Grade name")
    parser.add_argument("--project", default="一位数和两位数加减法", help="Project name")
    parser.add_argument("--output", default="math_problems_tagged.json", help="Output JSON path")
    parser.add_argument("--list", action="store_true", help="List available projects")
    args = parser.parse_args()

    if args.list:
        for item in PROJECT_CATALOG:
            print(f"{item['subject']} / {item['grade']} / {item['project']}")
        return

    entry = find_catalog_entry(args.subject, args.grade, args.project)
    if not entry:
        raise SystemExit("Project not found. Use --list to see available projects.")

    total = export_project(entry, args.output)
    print(f"Exported {total} problems to {args.output}")


if __name__ == "__main__":
    main()
