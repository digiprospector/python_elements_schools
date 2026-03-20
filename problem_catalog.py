#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project catalog and problem generators.
"""

ANSWER_ENCODING_BASE = 100


def build_scope_tags(subject, grade, project):
    return [f"科目:{subject}", f"年级:{grade}", f"项目:{project}"]


def encode_answer(answer_mode, primary, secondary=None):
    if answer_mode == "quotient_remainder":
        if secondary is None:
            raise ValueError("quotient_remainder mode requires both quotient and remainder")
        return int(primary) * ANSWER_ENCODING_BASE + int(secondary)
    return int(primary)


def format_answer(answer_mode, value):
    if answer_mode == "quotient_remainder":
        quotient = int(value) // ANSWER_ENCODING_BASE
        remainder = int(value) % ANSWER_ENCODING_BASE
        return f"{quotient} 余 {remainder}"
    return str(value)


def get_scope_from_tags(tags):
    values = {}
    for tag in tags.split(","):
        if ":" not in tag:
            continue
        key, value = tag.split(":", 1)
        values[key] = value

    subject = values.get("科目")
    grade = values.get("年级")
    project = values.get("项目")
    if not subject or not grade or not project:
        return None
    return {"subject": subject, "grade": grade, "project": project}


def analyze_addition(num1, num2, answer):
    tags = []

    tags.append("加数1是一位数" if num1 <= 9 else "加数1是两位数")
    tags.append("加数2是一位数" if num2 <= 9 else "加数2是两位数")

    if (num1 % 10) + (num2 % 10) >= 10:
        tags.append("需要进位")
    else:
        tags.append("不进位")

    if answer > 99:
        tags.append("结果大于99")
    else:
        tags.append("结果小于100")

    if answer > 50:
        tags.append("结果大于50")
    elif answer <= 20:
        tags.append("结果小于等于20")

    return tags


def analyze_subtraction(num1, num2, answer):
    tags = []

    tags.append("被减数是一位数" if num1 <= 9 else "被减数是两位数")
    tags.append("减数是一位数" if num2 <= 9 else "减数是两位数")

    if (num1 % 10) < (num2 % 10):
        tags.append("需要退位")
    else:
        tags.append("不退位")

    if num1 > 50:
        tags.append("被减数大于50")

    if answer == 0:
        tags.append("结果为0")
    elif answer < 10:
        tags.append("结果小于10")
    elif answer >= 50:
        tags.append("结果大于等于50")

    return tags


def analyze_division_with_remainder(dividend, divisor, quotient, remainder):
    tags = []
    tags.append("被除数是一位数" if dividend <= 9 else "被除数是两位数")
    tags.append(f"除数是{divisor}")
    tags.append(f"商是{quotient}")
    tags.append(f"余数是{remainder}")
    return tags


def generate_add_sub_problem_bank(subject, grade, project):
    scope_tags = build_scope_tags(subject, grade, project)
    numbers = list(range(1, 100))
    problems = []

    for num1 in numbers:
        for num2 in numbers:
            answer = num1 + num2
            tags = analyze_addition(num1, num2, answer) + scope_tags
            problems.append(
                {
                    "question": f"{num1} + {num2} = ?",
                    "num1": num1,
                    "num2": num2,
                    "answer": encode_answer("integer", answer),
                    "type": "加法",
                    "tags": ",".join(tags),
                }
            )

    for num1 in numbers:
        for num2 in numbers:
            if num1 < num2:
                continue

            answer = num1 - num2
            tags = analyze_subtraction(num1, num2, answer) + scope_tags
            problems.append(
                {
                    "question": f"{num1} - {num2} = ?",
                    "num1": num1,
                    "num2": num2,
                    "answer": encode_answer("integer", answer),
                    "type": "减法",
                    "tags": ",".join(tags),
                }
            )

    return problems


def generate_division_with_remainder_bank(subject, grade, project):
    scope_tags = build_scope_tags(subject, grade, project)
    problems = []

    for divisor in range(2, 10):
        for quotient in range(1, 10):
            for remainder in range(1, divisor):
                dividend = divisor * quotient + remainder
                if dividend >= 100:
                    continue

                tags = analyze_division_with_remainder(dividend, divisor, quotient, remainder) + scope_tags
                problems.append(
                    {
                        "question": f"{dividend} ÷ {divisor} = ? 余 ?",
                        "num1": dividend,
                        "num2": divisor,
                        "answer": encode_answer("quotient_remainder", quotient, remainder),
                        "type": "除法",
                        "tags": ",".join(tags),
                    }
                )

    return problems


ADD_SUB_PRACTICE_CONFIG = {
    "answer_mode": "integer",
    "type_options": [
        {"value": "", "label": "全部"},
        {"value": "加法", "label": "加法"},
        {"value": "减法", "label": "减法"},
    ],
    "tag_groups": [
        {
            "id": "addition",
            "title": "加法选项",
            "visible_for": ["", "加法"],
            "options": [
                "加数1是一位数",
                "加数1是两位数",
                "加数2是一位数",
                "加数2是两位数",
                "需要进位",
                "不进位",
                "结果大于99",
                "结果小于100",
                "结果大于50",
                "结果小于等于20",
            ],
        },
        {
            "id": "subtraction",
            "title": "减法选项",
            "visible_for": ["", "减法"],
            "options": [
                "被减数是一位数",
                "被减数是两位数",
                "减数是一位数",
                "减数是两位数",
                "需要退位",
                "不退位",
                "被减数大于50",
                "结果为0",
                "结果小于10",
                "结果大于等于50",
            ],
        },
    ],
}


DIVISION_WITH_REMAINDER_PRACTICE_CONFIG = {
    "answer_mode": "quotient_remainder",
    "type_options": [
        {"value": "", "label": "全部"},
        {"value": "除法", "label": "除法"},
    ],
    "tag_groups": [
        {
            "id": "division",
            "title": "除法选项",
            "visible_for": ["", "除法"],
            "options": [
                "被除数是一位数",
                "被除数是两位数",
            ],
        }
    ],
}


PROJECT_CATALOG = [
    {
        "subject": "数学",
        "grade": "小二下",
        "project": "一位数和两位数加减法",
        "expected_count": 14751,
        "answer_mode": "integer",
        "practice_config": ADD_SUB_PRACTICE_CONFIG,
        "generator": generate_add_sub_problem_bank,
    },
    {
        "subject": "数学",
        "grade": "小二下",
        "project": "带余数的除法",
        "expected_count": 324,
        "answer_mode": "quotient_remainder",
        "practice_config": DIVISION_WITH_REMAINDER_PRACTICE_CONFIG,
        "generator": generate_division_with_remainder_bank,
    },
]


def get_catalog_for_ui():
    return [
        {
            "subject": item["subject"],
            "grade": item["grade"],
            "project": item["project"],
            "answer_mode": item["answer_mode"],
            "practice_config": item["practice_config"],
        }
        for item in PROJECT_CATALOG
    ]


def find_catalog_entry(subject, grade, project):
    for item in PROJECT_CATALOG:
        if item["subject"] == subject and item["grade"] == grade and item["project"] == project:
            return item
    return None


def build_project_problems(entry):
    return entry["generator"](entry["subject"], entry["grade"], entry["project"])
