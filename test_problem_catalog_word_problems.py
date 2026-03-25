#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import re
import unittest

from app import normalize_practice_settings
from problem_catalog import (
    filter_problems_by_selected_groups,
    find_catalog_entry,
    generate_template_problems,
    get_project_templates,
    get_selected_tag_groups,
    is_template_project,
)


class WordProblemCatalogTests(unittest.TestCase):
    def test_division_word_problem_requires_method_selection(self):
        selection = {"subject": "数学", "grade": "小二下", "project": "应用题：有余数除法"}

        with self.assertRaisesRegex(ValueError, "请至少选择一个“解题方法”"):
            normalize_practice_settings(selection, {"count": 10, "type": "", "tags": []})

        normalized = normalize_practice_settings(
            selection,
            {"count": 10, "type": "", "tags": ["进一法"]},
        )
        self.assertEqual(["进一法"], normalized["tags"])

    def test_template_projects_have_enough_template_types(self):
        division_entry = find_catalog_entry("数学", "小二下", "应用题：有余数除法")
        mixed_entry = find_catalog_entry("数学", "小二下", "应用题：两步混合运算")

        self.assertTrue(is_template_project(division_entry))
        self.assertTrue(is_template_project(mixed_entry))
        self.assertGreaterEqual(len(get_project_templates(division_entry)), 12)
        self.assertGreaterEqual(len(get_project_templates(mixed_entry)), 16)
        self.assertGreaterEqual(
            len(get_project_templates(division_entry)) + len(get_project_templates(mixed_entry)),
            28,
        )

    def test_division_word_problem_generation_matches_method(self):
        entry = find_catalog_entry("数学", "小二下", "应用题：有余数除法")
        self.assertIsNotNone(entry)

        problems = generate_template_problems(entry, 20, ["进一法"], rng=random.Random(1234))
        self.assertEqual(20, len(problems))
        self.assertEqual(len(problems), len({problem["question"] for problem in problems}))

        for problem in problems:
            with self.subTest(question=problem["question"]):
                quotient, remainder = divmod(problem["num1"], problem["num2"])
                tags = set(problem["tags"].split(","))

                self.assertEqual("有余数除法应用题", problem["type"])
                self.assertIn("模板题", tags)
                self.assertIn("应用题", tags)
                self.assertIn("有余数除法", tags)
                self.assertIn("进一法", tags)
                self.assertEqual(problem["answer"], quotient + 1)
                self.assertGreater(remainder, 0)

    def test_division_word_problem_group_options_use_or_matching(self):
        entry = find_catalog_entry("数学", "小二下", "应用题：有余数除法")
        self.assertIsNotNone(entry)

        selected_groups = get_selected_tag_groups(
            entry,
            ["进一法", "去尾法", "装盒装袋", "乘车安排"],
        )
        self.assertCountEqual(["进一法", "去尾法"], selected_groups[0]["selected_options"])
        self.assertCountEqual(["装盒装袋", "乘车安排"], selected_groups[1]["selected_options"])

        problems = generate_template_problems(
            entry,
            20,
            ["进一法", "去尾法", "装盒装袋", "乘车安排"],
            rng=random.Random(4321),
        )
        self.assertEqual(20, len(problems))

        methods = set()
        scenes = set()
        for problem in problems:
            tags = set(problem["tags"].split(","))
            methods.update(tags & {"进一法", "去尾法"})
            scenes.update(tags & {"装盒装袋", "乘车安排"})
            self.assertTrue(tags & {"进一法", "去尾法"})
            self.assertTrue(tags & {"装盒装袋", "乘车安排"})

        self.assertEqual({"进一法", "去尾法"}, methods)
        self.assertTrue(scenes.issubset({"装盒装袋", "乘车安排"}))

    def test_add_sub_project_option_groups_use_or_matching(self):
        entry = find_catalog_entry("数学", "小二下", "一位数和两位数加减法")
        self.assertIsNotNone(entry)

        selected_groups = get_selected_tag_groups(
            entry,
            ["加数1是一位数", "加数1是两位数", "需要进位"],
            "加法",
        )
        self.assertCountEqual(["加数1是一位数", "加数1是两位数"], selected_groups[0]["selected_options"])
        self.assertEqual(["需要进位"], selected_groups[2]["selected_options"])

        sample_problems = [
            {"tags": "加数1是一位数,需要进位,科目:数学", "question": "a"},
            {"tags": "加数1是两位数,需要进位,科目:数学", "question": "b"},
            {"tags": "加数1是一位数,不进位,科目:数学", "question": "c"},
        ]
        filtered = filter_problems_by_selected_groups(sample_problems, selected_groups)
        self.assertEqual(["a", "b"], [problem["question"] for problem in filtered])

    def test_all_type_selection_does_not_cross_filter_add_and_sub_groups(self):
        entry = find_catalog_entry("数学", "小二下", "一位数和两位数加减法")
        self.assertIsNotNone(entry)

        selected_groups = get_selected_tag_groups(
            entry,
            [
                "加数1是两位数",
                "加数2是两位数",
                "需要进位",
                "被减数是三位数",
                "减数是两位数",
                "需要退位",
            ],
            "",
        )

        sample_problems = [
            {
                "type": "加法",
                "tags": "加数1是两位数,加数2是两位数,需要进位,科目:数学",
                "question": "add_ok",
            },
            {
                "type": "减法",
                "tags": "被减数是三位数,减数是两位数,需要退位,科目:数学",
                "question": "sub_ok",
            },
            {
                "type": "加法",
                "tags": "加数1是两位数,加数2是两位数,不进位,科目:数学",
                "question": "add_fail",
            },
        ]

        filtered = filter_problems_by_selected_groups(sample_problems, selected_groups)
        self.assertEqual(["add_ok", "sub_ok"], [problem["question"] for problem in filtered])

    def test_mixed_word_problem_generation_matches_tags(self):
        entry = find_catalog_entry("数学", "小二下", "应用题：两步混合运算")
        self.assertIsNotNone(entry)

        problems = generate_template_problems(entry, 24, ["先乘后减"], rng=random.Random(5678))
        self.assertEqual(24, len(problems))
        self.assertEqual(len(problems), len({problem["question"] for problem in problems}))

        for problem in problems:
            with self.subTest(question=problem["question"]):
                numbers = [int(value) for value in re.findall(r"\d+", problem["question"])]
                tags = set(problem["tags"].split(","))
                answer = problem["answer"]

                self.assertEqual("两步混合运算应用题", problem["type"])
                self.assertIn("模板题", tags)
                self.assertIn("两步混合", tags)
                self.assertIn("先乘后减", tags)
                self.assertEqual(answer, numbers[0] * numbers[1] - numbers[2])

                if "结果小于等于20" in tags:
                    self.assertLessEqual(answer, 20)
                elif "结果21到50" in tags:
                    self.assertGreater(answer, 20)
                    self.assertLessEqual(answer, 50)
                elif "结果大于50" in tags:
                    self.assertGreater(answer, 50)
                else:
                    self.fail(f"Missing result range tag: {problem['tags']}")


if __name__ == "__main__":
    unittest.main()
