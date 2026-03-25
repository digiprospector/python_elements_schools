#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from problem_catalog import build_project_problems, find_catalog_entry


class StaticProjectCatalogTests(unittest.TestCase):
    def test_subtraction_problem_bank_supports_three_digit_minuends(self):
        entry = find_catalog_entry("数学", "小二下", "一位数和两位数加减法")
        self.assertIsNotNone(entry)

        problems = build_project_problems(entry)
        self.assertEqual(entry["expected_count"], len(problems))

        subtraction_problems = [problem for problem in problems if problem["type"] == "减法"]
        self.assertEqual(14751, len(subtraction_problems))

        three_digit_problems = [
            problem
            for problem in subtraction_problems
            if "被减数是三位数" in problem["tags"].split(",")
        ]
        self.assertTrue(three_digit_problems)

        sample_problem = three_digit_problems[0]
        self.assertGreaterEqual(sample_problem["num1"], 100)
        self.assertLessEqual(sample_problem["num1"], 198)
        self.assertLessEqual(sample_problem["num2"], 99)
        self.assertEqual(sample_problem["answer"], sample_problem["num1"] - sample_problem["num2"])


if __name__ == "__main__":
    unittest.main()
