#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project catalog and problem generators.
"""

import random


ANSWER_ENCODING_BASE = 100
WORD_PROBLEM_DIVISION_TYPE = "有余数除法应用题"
WORD_PROBLEM_MIXED_TYPE = "两步混合运算应用题"
TAG_ALIASES = {
    "结果是三位数": ["结果是三位数", "结果大于99"],
    "结果是两位数": ["结果是两位数", "结果小于100"],
}


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


def normalize_tag_groups(practice_config, type_value=""):
    normalized_groups = []

    for group in (practice_config or {}).get("tag_groups", []):
        visible_for = group.get("visible_for") or [""]
        if visible_for and type_value not in visible_for:
            continue

        option_groups = group.get("option_groups")
        if option_groups:
            for option_group in option_groups:
                normalized_groups.append(
                    {
                        "id": option_group.get("id", group.get("id")),
                        "title": option_group.get("title", group.get("title", "")),
                        "required": bool(option_group.get("required", group.get("required", False))),
                        "match": option_group.get("match", "any"),
                        "options": list(option_group.get("options", [])),
                        "parent_title": group.get("title", ""),
                        "applies_to_types": [value for value in visible_for if value],
                    }
                )
            continue

        normalized_groups.append(
            {
                "id": group.get("id"),
                "title": group.get("title", ""),
                "required": bool(group.get("required")),
                "match": group.get("match", "all"),
                "options": list(group.get("options", [])),
                "parent_title": group.get("title", ""),
                "applies_to_types": [value for value in visible_for if value],
            }
        )

    return normalized_groups


def build_result_range_tag(answer):
    if answer <= 20:
        return "结果小于等于20"
    if answer <= 50:
        return "结果21到50"
    return "结果大于50"


def analyze_addition(num1, num2, answer):
    tags = []

    tags.append("加数1是一位数" if num1 <= 9 else "加数1是两位数")
    tags.append("加数2是一位数" if num2 <= 9 else "加数2是两位数")

    if (num1 % 10) + (num2 % 10) >= 10:
        tags.append("需要进位")
    else:
        tags.append("不进位")

    if answer > 99:
        tags.append("结果是三位数")
    else:
        tags.append("结果是两位数")

    if answer > 50:
        tags.append("结果大于50")
    elif answer <= 20:
        tags.append("结果小于等于20")

    return tags


def analyze_subtraction(num1, num2, answer):
    tags = []

    if num1 <= 9:
        tags.append("被减数是一位数")
    elif num1 <= 99:
        tags.append("被减数是两位数")
    else:
        tags.append("被减数是三位数")
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
    addition_numbers = list(range(1, 100))
    subtraction_num1_numbers = list(range(1, 199))
    subtraction_num2_numbers = list(range(1, 100))
    problems = []

    for num1 in addition_numbers:
        for num2 in addition_numbers:
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

    for num1 in subtraction_num1_numbers:
        for num2 in subtraction_num2_numbers:
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


DIVISION_WORD_TEMPLATES = [
    {
        "id": "div_bus_trip",
        "template_name": "春游乘车",
        "method": "进一法",
        "scene_tag": "乘车安排",
        "context_tag": "校园生活",
        "template": "二年级有{total}名同学去春游，每辆车最多坐{divisor}人，至少需要多少辆车？",
    },
    {
        "id": "div_buns_tray_up",
        "template_name": "包子装盘",
        "method": "进一法",
        "scene_tag": "装盒装袋",
        "context_tag": "整理物品",
        "template": "食堂做了{total}个包子，每盘最多放{divisor}个，至少需要多少个盘子才能全部装下？",
    },
    {
        "id": "div_flowers_bundle_up",
        "template_name": "纸花扎束",
        "method": "进一法",
        "scene_tag": "装盒装袋",
        "context_tag": "手工制作",
        "template": "手工课做了{total}朵纸花，每束最多扎{divisor}朵，至少要扎成多少束才能全部装下？",
    },
    {
        "id": "div_parents_rows",
        "template_name": "家长入座",
        "method": "进一法",
        "scene_tag": "座位安排",
        "context_tag": "校园生活",
        "template": "报告厅来了{total}位家长，每排最多坐{divisor}位，至少需要安排多少排座位？",
    },
    {
        "id": "div_water_box",
        "template_name": "矿泉水装箱",
        "method": "进一法",
        "scene_tag": "装盒装袋",
        "context_tag": "校园生活",
        "template": "运动会准备了{total}瓶矿泉水，每箱最多装{divisor}瓶，至少需要多少个箱子？",
    },
    {
        "id": "div_grouping_students",
        "template_name": "分组活动",
        "method": "进一法",
        "scene_tag": "平均分组",
        "context_tag": "校园生活",
        "template": "班里有{total}名同学做活动，每组最多{divisor}人，至少可以分成多少组？",
    },
    {
        "id": "div_tree_rows",
        "template_name": "植树排队",
        "method": "进一法",
        "scene_tag": "摆放排列",
        "context_tag": "劳动实践",
        "template": "学校准备种{total}棵小树，每行最多种{divisor}棵，至少要排多少行？",
    },
    {
        "id": "div_book_shelf_layers",
        "template_name": "书架分层",
        "method": "进一法",
        "scene_tag": "摆放排列",
        "context_tag": "学习用品",
        "template": "图书角有{total}本图书，每层书架最多放{divisor}本，至少需要多少层？",
    },
    {
        "id": "div_buns_tray_down",
        "template_name": "装满盘子",
        "method": "去尾法",
        "scene_tag": "装盒装袋",
        "context_tag": "整理物品",
        "template": "食堂有{total}个包子，每盘装{divisor}个，最多可以装满多少盘？",
    },
    {
        "id": "div_flower_rows_down",
        "template_name": "花盆排队",
        "method": "去尾法",
        "scene_tag": "摆放排列",
        "context_tag": "校园生活",
        "template": "操场边有{total}盆花，每排摆{divisor}盆，最多可以摆完整的多少排？",
    },
    {
        "id": "div_workbook_groups_down",
        "template_name": "练习册平均分",
        "method": "去尾法",
        "scene_tag": "平均分配",
        "context_tag": "学习用品",
        "template": "图书角有{total}本练习册，平均分给{divisor}个学习小组，最多每组分到多少本后还能保证每组一样多？",
    },
    {
        "id": "div_redflowers_bags_down",
        "template_name": "红花装袋",
        "method": "去尾法",
        "scene_tag": "装盒装袋",
        "context_tag": "手工制作",
        "template": "手工课做了{total}朵小红花，每袋装{divisor}朵，最多可以装满多少袋？",
    },
    {
        "id": "div_badminton_tubes_down",
        "template_name": "羽毛球装筒",
        "method": "去尾法",
        "scene_tag": "装盒装袋",
        "context_tag": "体育活动",
        "template": "体育室有{total}个羽毛球，每筒装{divisor}个，最多可以装满多少筒？",
    },
    {
        "id": "div_cookie_boxes_down",
        "template_name": "饼干装盒",
        "method": "去尾法",
        "scene_tag": "装盒装袋",
        "context_tag": "购物统计",
        "template": "点心店有{total}块饼干，每盒装{divisor}块，最多可以装满多少盒？",
    },
    {
        "id": "div_desks_rows_down",
        "template_name": "课桌排行",
        "method": "去尾法",
        "scene_tag": "摆放排列",
        "context_tag": "校园生活",
        "template": "仓库里有{total}张课桌，每排摆{divisor}张，最多可以摆完整的多少排？",
    },
    {
        "id": "div_orange_bags_down",
        "template_name": "橙子装袋",
        "method": "去尾法",
        "scene_tag": "装盒装袋",
        "context_tag": "购物统计",
        "template": "水果店有{total}个橙子，每袋装{divisor}个，最多可以装满多少袋？",
    },
]


MIXED_WORD_TEMPLATES = [
    {
        "id": "mix_library_books",
        "template_name": "图书借阅",
        "pattern": "add_then_subtract",
        "scene_tag": "图书借阅",
        "context_tag": "校园生活",
        "template": "图书角原来有{start}本故事书，又买来{added}本，借给同学{removed}本，现在还剩多少本故事书？",
    },
    {
        "id": "mix_stickers",
        "template_name": "奖贴统计",
        "pattern": "add_then_subtract",
        "scene_tag": "奖励统计",
        "context_tag": "校园生活",
        "template": "班级原来有{start}张奖励贴纸，又新发了{added}张，用掉了{removed}张，还剩多少张贴纸？",
    },
    {
        "id": "mix_fruits_shop",
        "template_name": "水果进货",
        "pattern": "add_then_subtract",
        "scene_tag": "购物统计",
        "context_tag": "生活购物",
        "template": "水果店原来有{start}个苹果，又运来{added}个，卖出{removed}个，现在还有多少个苹果？",
    },
    {
        "id": "mix_chalk",
        "template_name": "粉笔领取",
        "pattern": "add_then_subtract",
        "scene_tag": "学习用品",
        "context_tag": "校园生活",
        "template": "教室原来有{start}支粉笔，又领来{added}支，用掉了{removed}支，还剩多少支粉笔？",
    },
    {
        "id": "mix_flowers",
        "template_name": "花坛布置",
        "pattern": "subtract_then_add",
        "scene_tag": "校园布置",
        "context_tag": "校园生活",
        "template": "操场边原来摆着{start}盆花，搬走了{removed}盆，又送来{added}盆，现在有多少盆花？",
    },
    {
        "id": "mix_chairs",
        "template_name": "椅子更换",
        "pattern": "subtract_then_add",
        "scene_tag": "校园布置",
        "context_tag": "校园生活",
        "template": "教室里原来有{start}把椅子，搬走了{removed}把，又搬来{added}把，现在有多少把椅子？",
    },
    {
        "id": "mix_fish",
        "template_name": "鱼缸小鱼",
        "pattern": "subtract_then_add",
        "scene_tag": "饲养观察",
        "context_tag": "生活常识",
        "template": "鱼缸里原来有{start}条小鱼，送走了{removed}条，又买来{added}条，现在有多少条小鱼？",
    },
    {
        "id": "mix_balls",
        "template_name": "篮球器材",
        "pattern": "subtract_then_add",
        "scene_tag": "体育活动",
        "context_tag": "校园生活",
        "template": "体育室原来有{start}个篮球，借出了{removed}个，又买来{added}个，现在有多少个篮球？",
    },
    {
        "id": "mix_paper_flowers",
        "template_name": "纸花制作",
        "pattern": "multiply_then_add",
        "scene_tag": "手工制作",
        "context_tag": "校园生活",
        "template": "手工课上，{groups}个小组每组做了{each}朵纸花，老师又补做了{extra}朵，一共做了多少朵纸花？",
    },
    {
        "id": "mix_flags",
        "template_name": "彩旗布置",
        "pattern": "multiply_then_add",
        "scene_tag": "校园布置",
        "context_tag": "校园生活",
        "template": "操场上有{groups}排彩旗，每排挂{each}面，又在入口处加挂了{extra}面，一共有多少面彩旗？",
    },
    {
        "id": "mix_gifts",
        "template_name": "礼物准备",
        "pattern": "multiply_then_add",
        "scene_tag": "活动准备",
        "context_tag": "生活常识",
        "template": "{groups}个礼品袋里每袋放了{each}支铅笔，又另外准备了{extra}支，一共准备了多少支铅笔？",
    },
    {
        "id": "mix_drawings",
        "template_name": "绘画展览",
        "pattern": "multiply_then_add",
        "scene_tag": "作品统计",
        "context_tag": "校园生活",
        "template": "美术角挂了{groups}排图画，每排有{each}幅，又新贴上{extra}幅，一共有多少幅图画？",
    },
    {
        "id": "mix_oranges",
        "template_name": "橙子售卖",
        "pattern": "multiply_then_subtract",
        "scene_tag": "购物统计",
        "context_tag": "生活购物",
        "template": "水果店运来{groups}箱橙子，每箱{each}个，上午卖出{removed}个，还剩多少个橙子？",
    },
    {
        "id": "mix_bread",
        "template_name": "面包售卖",
        "pattern": "multiply_then_subtract",
        "scene_tag": "购物统计",
        "context_tag": "生活购物",
        "template": "面包店烤了{groups}盘面包，每盘{each}个，卖出{removed}个后，还剩多少个面包？",
    },
    {
        "id": "mix_stars",
        "template_name": "星星贴纸",
        "pattern": "multiply_then_subtract",
        "scene_tag": "奖励统计",
        "context_tag": "校园生活",
        "template": "老师准备了{groups}张贴纸，每张有{each}颗小星星，用掉了{removed}颗，还剩多少颗小星星？",
    },
    {
        "id": "mix_pencils",
        "template_name": "铅笔借出",
        "pattern": "multiply_then_subtract",
        "scene_tag": "学习用品",
        "context_tag": "校园生活",
        "template": "文具角有{groups}盒铅笔，每盒{each}支，借给同学{removed}支后，还剩多少支铅笔？",
    },
    {
        "id": "mix_candy_box",
        "template_name": "糖果分装",
        "pattern": "add_then_divide",
        "scene_tag": "活动准备",
        "context_tag": "生活常识",
        "template": "老师先准备了{start}颗糖果，又补充了{added}颗，把这些糖果平均分给{divisor}个小组，每组分到多少颗？",
    },
    {
        "id": "mix_biscuit_share",
        "template_name": "饼干分享",
        "pattern": "add_then_divide",
        "scene_tag": "购物统计",
        "context_tag": "生活购物",
        "template": "班级原来有{start}块饼干，又买来{added}块，一共平均装入{divisor}个袋子，每袋有多少块饼干？",
    },
    {
        "id": "mix_flag_rows",
        "template_name": "彩旗布置",
        "pattern": "subtract_then_multiply",
        "scene_tag": "校园布置",
        "context_tag": "校园生活",
        "template": "仓库里有{start}面彩旗，先拿走{removed}面，剩下的每{group_size}面挂成一排，一共能挂成多少排？",
    },
    {
        "id": "mix_seed_packets",
        "template_name": "种子整理",
        "pattern": "subtract_then_multiply",
        "scene_tag": "手工制作",
        "context_tag": "生活常识",
        "template": "科学角有{start}包种子，先用掉{removed}包，剩下的每{group_size}包放一层，放了{groups}层，一共放了多少包？",
    },
    {
        "id": "mix_book_share_reward",
        "template_name": "借阅奖励",
        "pattern": "divide_then_add",
        "scene_tag": "图书借阅",
        "context_tag": "校园生活",
        "template": "图书角有{total}本故事书，平均分给{divisor}个小组后，每组再奖励{extra}本，每组现在有多少本？",
    },
    {
        "id": "mix_fruit_share_plus",
        "template_name": "水果加餐",
        "pattern": "divide_then_add",
        "scene_tag": "购物统计",
        "context_tag": "生活购物",
        "template": "食堂有{total}个水果，平均分给{divisor}个班后，每班再加发{extra}个，每班共分到多少个水果？",
    },
    {
        "id": "mix_sticker_use",
        "template_name": "贴纸使用",
        "pattern": "divide_then_subtract",
        "scene_tag": "奖励统计",
        "context_tag": "校园生活",
        "template": "老师有{total}张贴纸，平均分给{divisor}组后，每组先用掉{removed_each}张，每组还剩多少张？",
    },
    {
        "id": "mix_ball_share_minus",
        "template_name": "器材整理",
        "pattern": "divide_then_subtract",
        "scene_tag": "体育活动",
        "context_tag": "校园生活",
        "template": "器材室有{total}个球，平均分到{divisor}个筐里后，每筐拿走{removed_each}个，每筐还剩多少个？",
    },
]


# Override mixed templates to keep only the 8 requested operation orders.
MIXED_WORD_TEMPLATES = [
    {"id": "mix_mul_add_1", "template_name": "纸花制作", "pattern": "multiply_then_add", "scene_tag": "手工制作", "context_tag": "校园生活", "template": "手工课上，{groups}个小组每组做了{each}朵纸花，老师又补做了{extra}朵，一共做了多少朵纸花？"},
    {"id": "mix_mul_add_2", "template_name": "彩旗布置", "pattern": "multiply_then_add", "scene_tag": "校园布置", "context_tag": "校园生活", "template": "操场上有{groups}排彩旗，每排挂{each}面，又在入口处加挂了{extra}面，一共有多少面彩旗？"},
    {"id": "mix_add_mul_1", "template_name": "糖果加倍分发", "pattern": "add_then_multiply", "scene_tag": "活动准备", "context_tag": "生活常识", "template": "老师先准备了{start}颗糖果，又补充了{added}颗，按{times}倍分发，一共需要多少颗糖果？"},
    {"id": "mix_add_mul_2", "template_name": "作业本整理", "pattern": "add_then_multiply", "scene_tag": "学习用品", "context_tag": "校园生活", "template": "班级有{start}本作业本，又领来{added}本，把总数按{times}倍准备备用，一共准备多少本？"},
    {"id": "mix_mul_sub_1", "template_name": "橙子销售", "pattern": "multiply_then_subtract", "scene_tag": "购物统计", "context_tag": "生活购物", "template": "水果店运来{groups}箱橙子，每箱{each}个，上午卖出{removed}个，还剩多少个橙子？"},
    {"id": "mix_mul_sub_2", "template_name": "铅笔借出", "pattern": "multiply_then_subtract", "scene_tag": "学习用品", "context_tag": "校园生活", "template": "文具角有{groups}盒铅笔，每盒{each}支，借给同学{removed}支后，还剩多少支铅笔？"},
    {"id": "mix_sub_mul_1", "template_name": "彩旗整理", "pattern": "subtract_then_multiply", "scene_tag": "校园布置", "context_tag": "校园生活", "template": "仓库有{start}面彩旗，先拿走{removed}面，剩下的每面再配{times}个夹子，一共要多少个夹子？"},
    {"id": "mix_sub_mul_2", "template_name": "图书装订", "pattern": "subtract_then_multiply", "scene_tag": "图书借阅", "context_tag": "校园生活", "template": "图书角有{start}本旧书，先淘汰{removed}本，剩下的每本贴{times}张标签，一共贴多少张标签？"},
    {"id": "mix_div_add_1", "template_name": "借阅奖励", "pattern": "divide_then_add", "scene_tag": "图书借阅", "context_tag": "校园生活", "template": "图书角有{total}本故事书，平均分给{divisor}个小组后，每组再奖励{extra}本，每组现在有多少本？"},
    {"id": "mix_div_add_2", "template_name": "水果加餐", "pattern": "divide_then_add", "scene_tag": "购物统计", "context_tag": "生活购物", "template": "食堂有{total}个水果，平均分给{divisor}个班后，每班再加发{extra}个，每班共分到多少个水果？"},
    {"id": "mix_add_div_1", "template_name": "饼干分享", "pattern": "add_then_divide", "scene_tag": "购物统计", "context_tag": "生活购物", "template": "班级原来有{start}块饼干，又买来{added}块，一共平均装入{divisor}个袋子，每袋有多少块饼干？"},
    {"id": "mix_add_div_2", "template_name": "练习册分组", "pattern": "add_then_divide", "scene_tag": "学习用品", "context_tag": "校园生活", "template": "教室有{start}本练习册，又搬来{added}本，平均分给{divisor}个学习小组，每组分到多少本？"},
    {"id": "mix_div_sub_1", "template_name": "贴纸使用", "pattern": "divide_then_subtract", "scene_tag": "奖励统计", "context_tag": "校园生活", "template": "老师有{total}张贴纸，平均分给{divisor}组后，每组先用掉{removed_each}张，每组还剩多少张？"},
    {"id": "mix_div_sub_2", "template_name": "器材整理", "pattern": "divide_then_subtract", "scene_tag": "体育活动", "context_tag": "校园生活", "template": "器材室有{total}个球，平均分到{divisor}个筐里后，每筐拿走{removed_each}个，每筐还剩多少个？"},
    {"id": "mix_sub_div_1", "template_name": "铅笔分盒", "pattern": "subtract_then_divide", "scene_tag": "学习用品", "context_tag": "校园生活", "template": "文具柜有{start}支铅笔，先借出{removed}支，剩下的平均装进{divisor}个笔筒，每个笔筒有多少支？"},
    {"id": "mix_sub_div_2", "template_name": "花盆分排", "pattern": "subtract_then_divide", "scene_tag": "校园布置", "context_tag": "校园生活", "template": "操场边有{start}盆花，先搬走{removed}盆，剩下的平均摆成{divisor}排，每排有多少盆？"},
]


def build_division_template_instance(template, scope_tags, rng):
    divisor = rng.randint(2, 9)
    quotient = rng.randint(2, 9)
    remainder = rng.randint(1, divisor - 1)
    total = divisor * quotient + remainder
    answer = quotient + 1 if template["method"] == "进一法" else quotient

    tags = [
        "应用题",
        "模板题",
        "有余数除法",
        template["method"],
        template["scene_tag"],
        template["context_tag"],
        f"模板:{template['template_name']}",
    ] + scope_tags

    return {
        "question": template["template"].format(total=total, divisor=divisor),
        "num1": total,
        "num2": divisor,
        "answer": encode_answer("integer", answer),
        "type": WORD_PROBLEM_DIVISION_TYPE,
        "tags": ",".join(tags),
    }


def build_add_then_subtract_instance(template, scope_tags, rng):
    start = rng.randint(18, 58)
    added = rng.randint(6, 28)
    total = start + added
    if total > 98:
        added -= total - 98
        total = start + added
    removed = rng.randint(4, total - 2)
    answer = total - removed
    tags = [
        "应用题",
        "模板题",
        "两步混合",
        "先加后减",
        template["scene_tag"],
        template["context_tag"],
        build_result_range_tag(answer),
        f"模板:{template['template_name']}",
    ] + scope_tags
    return {
        "question": template["template"].format(start=start, added=added, removed=removed),
        "num1": start,
        "num2": added,
        "answer": encode_answer("integer", answer),
        "type": WORD_PROBLEM_MIXED_TYPE,
        "tags": ",".join(tags),
    }


def build_subtract_then_add_instance(template, scope_tags, rng):
    start = rng.randint(24, 72)
    removed = rng.randint(5, start - 6)
    added = rng.randint(3, 24)
    answer = start - removed + added
    if answer > 100:
        added -= answer - 100
        answer = start - removed + added

    tags = [
        "应用题",
        "模板题",
        "两步混合",
        "先减后加",
        template["scene_tag"],
        template["context_tag"],
        build_result_range_tag(answer),
        f"模板:{template['template_name']}",
    ] + scope_tags
    return {
        "question": template["template"].format(start=start, removed=removed, added=added),
        "num1": start,
        "num2": removed,
        "answer": encode_answer("integer", answer),
        "type": WORD_PROBLEM_MIXED_TYPE,
        "tags": ",".join(tags),
    }


def build_multiply_then_add_instance(template, scope_tags, rng):
    groups = rng.randint(2, 8)
    each = rng.randint(2, 9)
    extra = rng.randint(1, 18)
    answer = groups * each + extra

    tags = [
        "应用题",
        "模板题",
        "两步混合",
        "先乘后加",
        template["scene_tag"],
        template["context_tag"],
        build_result_range_tag(answer),
        f"模板:{template['template_name']}",
    ] + scope_tags
    return {
        "question": template["template"].format(groups=groups, each=each, extra=extra),
        "num1": groups,
        "num2": each,
        "answer": encode_answer("integer", answer),
        "type": WORD_PROBLEM_MIXED_TYPE,
        "tags": ",".join(tags),
    }


def build_multiply_then_subtract_instance(template, scope_tags, rng):
    groups = rng.randint(2, 9)
    each = rng.randint(3, 9)
    total = groups * each
    removed = rng.randint(1, total - 1)
    answer = total - removed

    tags = [
        "应用题",
        "模板题",
        "两步混合",
        "先乘后减",
        template["scene_tag"],
        template["context_tag"],
        build_result_range_tag(answer),
        f"模板:{template['template_name']}",
    ] + scope_tags
    return {
        "question": template["template"].format(groups=groups, each=each, removed=removed),
        "num1": groups,
        "num2": each,
        "answer": encode_answer("integer", answer),
        "type": WORD_PROBLEM_MIXED_TYPE,
        "tags": ",".join(tags),
    }


def build_add_then_multiply_instance(template, scope_tags, rng):
    start = rng.randint(8, 40)
    added = rng.randint(4, 30)
    times = rng.randint(2, 4)
    answer = (start + added) * times

    tags = [
        "应用题",
        "模板题",
        "两步混合",
        "先加后乘",
        template["scene_tag"],
        template["context_tag"],
        build_result_range_tag(answer),
        f"模板:{template['template_name']}",
    ] + scope_tags
    return {
        "question": template["template"].format(start=start, added=added, times=times),
        "num1": start,
        "num2": added,
        "answer": encode_answer("integer", answer),
        "type": WORD_PROBLEM_MIXED_TYPE,
        "tags": ",".join(tags),
    }


def build_add_then_divide_instance(template, scope_tags, rng):
    divisor = rng.randint(2, 9)
    quotient = rng.randint(3, 12)
    total = divisor * quotient
    start = rng.randint(1, total - 1)
    added = total - start
    answer = quotient

    tags = [
        "应用题",
        "模板题",
        "两步混合",
        "先加后除",
        template["scene_tag"],
        template["context_tag"],
        build_result_range_tag(answer),
        f"模板:{template['template_name']}",
    ] + scope_tags
    return {
        "question": template["template"].format(start=start, added=added, divisor=divisor),
        "num1": start,
        "num2": added,
        "answer": encode_answer("integer", answer),
        "type": WORD_PROBLEM_MIXED_TYPE,
        "tags": ",".join(tags),
    }


def build_subtract_then_multiply_instance(template, scope_tags, rng):
    start = rng.randint(30, 90)
    removed = rng.randint(4, start - 6)
    times = rng.randint(2, 4)
    answer = (start - removed) * times

    tags = [
        "应用题",
        "模板题",
        "两步混合",
        "先减后乘",
        template["scene_tag"],
        template["context_tag"],
        build_result_range_tag(answer),
        f"模板:{template['template_name']}",
    ] + scope_tags
    return {
        "question": template["template"].format(
            start=start,
            removed=removed,
            times=times,
        ),
        "num1": start,
        "num2": removed,
        "answer": encode_answer("integer", answer),
        "type": WORD_PROBLEM_MIXED_TYPE,
        "tags": ",".join(tags),
    }


def build_divide_then_add_instance(template, scope_tags, rng):
    divisor = rng.randint(2, 9)
    quotient = rng.randint(3, 12)
    total = divisor * quotient
    extra = rng.randint(1, 20)
    answer = quotient + extra

    tags = [
        "应用题",
        "模板题",
        "两步混合",
        "先除后加",
        template["scene_tag"],
        template["context_tag"],
        build_result_range_tag(answer),
        f"模板:{template['template_name']}",
    ] + scope_tags
    return {
        "question": template["template"].format(total=total, divisor=divisor, extra=extra),
        "num1": total,
        "num2": divisor,
        "answer": encode_answer("integer", answer),
        "type": WORD_PROBLEM_MIXED_TYPE,
        "tags": ",".join(tags),
    }


def build_divide_then_subtract_instance(template, scope_tags, rng):
    divisor = rng.randint(2, 9)
    quotient = rng.randint(4, 14)
    total = divisor * quotient
    removed_each = rng.randint(1, quotient - 1)
    answer = quotient - removed_each

    tags = [
        "应用题",
        "模板题",
        "两步混合",
        "先除后减",
        template["scene_tag"],
        template["context_tag"],
        build_result_range_tag(answer),
        f"模板:{template['template_name']}",
    ] + scope_tags
    return {
        "question": template["template"].format(
            total=total,
            divisor=divisor,
            removed_each=removed_each,
        ),
        "num1": total,
        "num2": divisor,
        "answer": encode_answer("integer", answer),
        "type": WORD_PROBLEM_MIXED_TYPE,
        "tags": ",".join(tags),
    }


def build_subtract_then_divide_instance(template, scope_tags, rng):
    divisor = rng.randint(2, 9)
    quotient = rng.randint(2, 12)
    remaining = divisor * quotient
    removed = rng.randint(3, 25)
    start = remaining + removed
    answer = quotient

    tags = [
        "应用题",
        "模板题",
        "两步混合",
        "先减后除",
        template["scene_tag"],
        template["context_tag"],
        build_result_range_tag(answer),
        f"模板:{template['template_name']}",
    ] + scope_tags
    return {
        "question": template["template"].format(start=start, removed=removed, divisor=divisor),
        "num1": start,
        "num2": removed,
        "answer": encode_answer("integer", answer),
        "type": WORD_PROBLEM_MIXED_TYPE,
        "tags": ",".join(tags),
    }


def build_mixed_template_instance(template, scope_tags, rng):
    pattern = template["pattern"]
    if pattern == "add_then_subtract":
        return build_add_then_subtract_instance(template, scope_tags, rng)
    if pattern == "subtract_then_add":
        return build_subtract_then_add_instance(template, scope_tags, rng)
    if pattern == "multiply_then_add":
        return build_multiply_then_add_instance(template, scope_tags, rng)
    if pattern == "add_then_multiply":
        return build_add_then_multiply_instance(template, scope_tags, rng)
    if pattern == "multiply_then_subtract":
        return build_multiply_then_subtract_instance(template, scope_tags, rng)
    if pattern == "add_then_divide":
        return build_add_then_divide_instance(template, scope_tags, rng)
    if pattern == "subtract_then_multiply":
        return build_subtract_then_multiply_instance(template, scope_tags, rng)
    if pattern == "divide_then_add":
        return build_divide_then_add_instance(template, scope_tags, rng)
    if pattern == "divide_then_subtract":
        return build_divide_then_subtract_instance(template, scope_tags, rng)
    if pattern == "subtract_then_divide":
        return build_subtract_then_divide_instance(template, scope_tags, rng)
    raise ValueError(f"Unsupported pattern: {pattern}")


def is_template_project(entry):
    return bool(entry.get("template_mode"))


def get_project_templates(entry):
    return list(entry.get("templates") or [])


def get_selected_tag_groups(entry, selected_tags, type_value=""):
    selected_set = set(selected_tags or [])
    practice_config = entry.get("practice_config") or {}
    groups = []

    for group in normalize_tag_groups(practice_config, type_value):
        matched_options = [option for option in group["options"] if option in selected_set]
        groups.append(
            {
                "id": group["id"],
                "title": group["title"],
                "required": group["required"],
                "match": group["match"],
                "selected_options": matched_options,
                "parent_title": group.get("parent_title", ""),
                "applies_to_types": group.get("applies_to_types", []),
            }
        )

    return groups


def build_template_filter_description(entry, selected_tags, type_value=""):
    parts = [f"筛选条件: {entry['project']}"]
    selected_groups = get_selected_tag_groups(entry, selected_tags, type_value)

    visible_selected_groups = [group for group in selected_groups if group["selected_options"]]
    if not visible_selected_groups:
        parts.append("筛选标签: 无")
        return " | ".join(parts)

    for group in visible_selected_groups:
        join_text = " 或 " if group["match"] == "any" else " 且 "
        parts.append(f"{group['title']}: {join_text.join(group['selected_options'])}")

    return " | ".join(parts)


def problem_matches_selected_groups(problem, selected_groups):
    problem_tags = set(problem["tags"].split(","))
    problem_type = str(problem.get("type") or "").strip()

    for group in selected_groups:
        applies_to_types = group.get("applies_to_types") or []
        if applies_to_types and problem_type and problem_type not in applies_to_types:
            continue

        selected_options = group["selected_options"]
        if not selected_options:
            continue

        option_set = set()
        for option in selected_options:
            option_set.update(TAG_ALIASES.get(option, [option]))

        if group["match"] == "all":
            if not option_set.issubset(problem_tags):
                return False
            continue

        if not (problem_tags & option_set):
            return False

    return True


def filter_problems_by_selected_groups(problems, selected_groups):
    if not selected_groups:
        return list(problems)

    filtered = []
    for problem in problems:
        if problem_matches_selected_groups(problem, selected_groups):
            filtered.append(problem)
    return filtered


def generate_template_problems(entry, count, selected_tags=None, type_value="", rng=None):
    selected_tags = list(selected_tags or [])
    templates = get_project_templates(entry)
    if not templates:
        return []

    scope_tags = build_scope_tags(entry["subject"], entry["grade"], entry["project"])
    selected_groups = get_selected_tag_groups(entry, selected_tags, type_value)
    rng = rng or random.SystemRandom()
    problems = []
    seen_questions = set()
    attempts = 0
    max_attempts = max(count * 40, 200)

    while len(problems) < count:
        attempts += 1
        if attempts > max_attempts:
            break

        template = rng.choice(templates)
        if entry["project"] == "应用题：有余数除法":
            problem = build_division_template_instance(template, scope_tags, rng)
        elif entry["project"] == "应用题：两步混合运算":
            problem = build_mixed_template_instance(template, scope_tags, rng)
        else:
            raise ValueError(f"Unsupported template project: {entry['project']}")

        if not problem_matches_selected_groups(problem, selected_groups):
            continue

        if problem["question"] in seen_questions:
            continue

        seen_questions.add(problem["question"])
        problems.append(problem)

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
            "option_groups": [
                {
                    "id": "addition_num1_digits",
                    "title": "加数1位数",
                    "match": "any",
                    "options": [
                        "加数1是一位数",
                        "加数1是两位数",
                    ],
                },
                {
                    "id": "addition_num2_digits",
                    "title": "加数2位数",
                    "match": "any",
                    "options": [
                        "加数2是一位数",
                        "加数2是两位数",
                    ],
                },
                {
                    "id": "addition_carry",
                    "title": "进位情况",
                    "match": "any",
                    "options": [
                        "需要进位",
                        "不进位",
                    ],
                },
                {
                    "id": "addition_result_100",
                    "title": "结果位数",
                    "match": "any",
                    "options": [
                        "结果是三位数",
                        "结果是两位数",
                    ],
                },
                {
                    "id": "addition_result_range",
                    "title": "结果范围",
                    "match": "any",
                    "options": [],
                },
            ],
        },
        {
            "id": "subtraction",
            "title": "减法选项",
            "visible_for": ["", "减法"],
            "option_groups": [
                {
                    "id": "subtraction_num1_digits",
                    "title": "被减数位数",
                    "match": "any",
                    "options": [
                        "被减数是一位数",
                        "被减数是两位数",
                        "被减数是三位数",
                    ],
                },
                {
                    "id": "subtraction_num2_digits",
                    "title": "减数位数",
                    "match": "any",
                    "options": [
                        "减数是一位数",
                        "减数是两位数",
                    ],
                },
                {
                    "id": "subtraction_borrow",
                    "title": "退位情况",
                    "match": "any",
                    "options": [
                        "需要退位",
                        "不退位",
                    ],
                },
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
            "option_groups": [
                {
                    "id": "division_dividend_digits",
                    "title": "被除数位数",
                    "match": "any",
                    "options": [
                        "被除数是一位数",
                        "被除数是两位数",
                    ],
                },
            ],
        }
    ],
}


WORD_PROBLEM_DIVISION_PRACTICE_CONFIG = {
    "answer_mode": "integer",
    "type_options": [
        {"value": "", "label": "全部"},
        {"value": WORD_PROBLEM_DIVISION_TYPE, "label": WORD_PROBLEM_DIVISION_TYPE},
    ],
    "tag_groups": [
        {
            "id": "word_division_method",
            "title": "解题方法",
            "required": True,
            "visible_for": ["", WORD_PROBLEM_DIVISION_TYPE],
            "match": "any",
            "options": [
                "进一法",
                "去尾法",
            ],
        },
        {
            "id": "word_division_scene",
            "title": "应用场景",
            "visible_for": ["", WORD_PROBLEM_DIVISION_TYPE],
            "match": "any",
            "options": [
                "乘车安排",
                "装盒装袋",
                "座位安排",
                "平均分配",
                "平均分组",
                "摆放排列",
            ],
        },
    ],
}


WORD_PROBLEM_MIXED_PRACTICE_CONFIG = {
    "answer_mode": "integer",
    "type_options": [
        {"value": "", "label": "全部"},
        {"value": WORD_PROBLEM_MIXED_TYPE, "label": WORD_PROBLEM_MIXED_TYPE},
    ],
    "tag_groups": [
        {
            "id": "word_mixed_order",
            "title": "运算顺序",
            "visible_for": ["", WORD_PROBLEM_MIXED_TYPE],
            "match": "any",
            "options": [
                "先乘后加",
                "先加后乘",
                "先乘后减",
                "先减后乘",
                "先除后加",
                "先加后除",
                "先除后减",
                "先减后除",
                "先加后减",
                "先减后加",
            ],
        },
        {
            "id": "word_mixed_scene",
            "title": "应用场景",
            "visible_for": ["", WORD_PROBLEM_MIXED_TYPE],
            "match": "any",
            "options": [
                "图书借阅",
                "奖励统计",
                "购物统计",
                "学习用品",
                "校园布置",
                "饲养观察",
                "体育活动",
                "手工制作",
                "活动准备",
                "作品统计",
            ],
        },
        {
            "id": "word_mixed_range",
            "title": "结果范围",
            "visible_for": ["", WORD_PROBLEM_MIXED_TYPE],
            "match": "any",
            "options": [
                "结果小于等于20",
                "结果21到50",
                "结果大于50",
            ],
        },
    ],
}

# Keep mixed-operation order options to the exact 8 requested choices.
WORD_PROBLEM_MIXED_PRACTICE_CONFIG["tag_groups"][0]["options"] = [
    "\u5148\u4e58\u540e\u52a0",  # 先乘后加
    "\u5148\u52a0\u540e\u4e58",  # 先加后乘
    "\u5148\u4e58\u540e\u51cf",  # 先乘后减
    "\u5148\u51cf\u540e\u4e58",  # 先减后乘
    "\u5148\u9664\u540e\u52a0",  # 先除后加
    "\u5148\u52a0\u540e\u9664",  # 先加后除
    "\u5148\u9664\u540e\u51cf",  # 先除后减
    "\u5148\u51cf\u540e\u9664",  # 先减后除
]
WORD_PROBLEM_MIXED_PRACTICE_CONFIG["tag_groups"] = [
    group for group in WORD_PROBLEM_MIXED_PRACTICE_CONFIG["tag_groups"] if group.get("id") != "word_mixed_range"
]


PROJECT_CATALOG = [
    {
        "subject": "数学",
        "grade": "小二下",
        "project": "一位数和两位数加减法",
        "expected_count": 24552,
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
    {
        "subject": "数学",
        "grade": "小二下",
        "project": "应用题：有余数除法",
        "template_mode": True,
        "template_count": len(DIVISION_WORD_TEMPLATES),
        "answer_mode": "integer",
        "practice_config": WORD_PROBLEM_DIVISION_PRACTICE_CONFIG,
        "templates": DIVISION_WORD_TEMPLATES,
    },
    {
        "subject": "数学",
        "grade": "小二下",
        "project": "应用题：两步混合运算",
        "template_mode": True,
        "template_count": len(MIXED_WORD_TEMPLATES),
        "answer_mode": "integer",
        "practice_config": WORD_PROBLEM_MIXED_PRACTICE_CONFIG,
        "templates": MIXED_WORD_TEMPLATES,
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
    if is_template_project(entry):
        raise ValueError(f"{entry['project']} is template-based and does not support prebuilt problem banks")
    return entry["generator"](entry["subject"], entry["grade"], entry["project"])
