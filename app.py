#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Math practice system Flask app.
"""

import os
import random
import secrets

from flask import Flask, jsonify, render_template, request, session

from database_v3 import DatabaseSchemaError, DatabaseWriteError, MathDatabase
from problem_catalog import (
    PROJECT_CATALOG,
    build_project_problems,
    build_template_filter_description,
    build_scope_tags,
    filter_problems_by_selected_groups,
    find_catalog_entry,
    format_answer,
    generate_template_problems,
    get_scope_from_tags,
    get_catalog_for_ui,
    normalize_tag_groups,
    get_selected_tag_groups,
    is_template_project,
)


app = Flask(__name__)


class AppConfigError(RuntimeError):
    """Raised when required application configuration is missing."""


is_vercel_runtime = os.environ.get("VERCEL_ENV") in {"preview", "production"} or os.environ.get("VERCEL") == "1"

app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(16)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=is_vercel_runtime,
)

db = None
seed_checked = False


def ensure_problem_banks_seeded(db):
    for entry in PROJECT_CATALOG:
        if is_template_project(entry):
            continue

        scope_tags = build_scope_tags(entry["subject"], entry["grade"], entry["project"])
        existing_count = db.get_problem_count(required_tags=scope_tags)
        expected_count = int(entry.get("expected_count") or 0)

        if existing_count > 0 and expected_count > 0 and existing_count < expected_count:
            print(
                f"检测到题库不完整: {entry['subject']} / {entry['grade']} / {entry['project']} "
                f"(当前 {existing_count}, 期望 {expected_count})，正在重建"
            )
            deleted = db.purge_project_data(scope_tags)
            print(f"已清理旧题 {deleted} 道，开始重新初始化")
            existing_count = 0

        if existing_count > 0 and (expected_count == 0 or existing_count >= expected_count):
            print(
                f"题库已存在: {entry['subject']} / {entry['grade']} / {entry['project']} "
                f"({existing_count} 题)"
            )
            continue

        print(f"正在初始化题库: {entry['subject']} / {entry['grade']} / {entry['project']}")
        problems = build_project_problems(entry)
        inserted = db.insert_problems(problems)
        print(f"题库初始化完成: {entry['project']} ({inserted} 题)")


def get_current_selection():
    subject = session.get("subject", "")
    grade = session.get("grade", "")
    project = session.get("project", "")
    if not subject or not grade or not project:
        return None
    if not find_catalog_entry(subject, grade, project):
        return None
    return {"subject": subject, "grade": grade, "project": project}


def get_scope_tags_from_selection(selection):
    return build_scope_tags(selection["subject"], selection["grade"], selection["project"])


def build_practice_settings_scope_key(selection):
    return "::".join([selection["subject"], selection["grade"], selection["project"]])


def get_allowed_practice_tags(catalog_entry):
    allowed_tags = set()
    practice_config = catalog_entry.get("practice_config") or {}
    for group in normalize_tag_groups(practice_config):
        allowed_tags.update(group.get("options", []))
    return allowed_tags


def validate_required_tag_groups(catalog_entry, type_value, selected_tags):
    for group in get_selected_tag_groups(catalog_entry, selected_tags, type_value):
        if group["required"] and not group["selected_options"]:
            raise ValueError(f"请至少选择一个“{group['title'] or '筛选条件'}”")


def normalize_practice_settings(selection, settings):
    catalog_entry = find_catalog_entry(selection["subject"], selection["grade"], selection["project"])
    if not catalog_entry:
        raise ValueError("当前学习路径无效")

    practice_config = catalog_entry.get("practice_config") or {}

    try:
        count = int(settings.get("count", 10))
    except (TypeError, ValueError):
        raise ValueError("题目数量无效") from None

    if count < 1 or count > 50:
        raise ValueError("题目数量超出允许范围")

    raw_type_value = settings.get("type", "")
    if raw_type_value is None:
        raw_type_value = ""
    type_value = str(raw_type_value).strip()
    allowed_types = {option.get("value", "") for option in practice_config.get("type_options", [])}
    if type_value not in allowed_types:
        raise ValueError("题目类型无效")

    tags = settings.get("tags", [])
    if not isinstance(tags, list):
        raise ValueError("标签格式无效")

    allowed_tags = get_allowed_practice_tags(catalog_entry)
    normalized_tags = []
    for tag in tags:
        tag_value = str(tag).strip()
        if not tag_value:
            continue
        if tag_value not in allowed_tags:
            raise ValueError("包含未支持的标签")
        if tag_value not in normalized_tags:
            normalized_tags.append(tag_value)

    validate_required_tag_groups(catalog_entry, type_value, normalized_tags)

    return {
        "count": count,
        "type": type_value,
        "tags": normalized_tags,
    }


def strip_scope_tags(tags):
    if isinstance(tags, str):
        tag_list = [tag for tag in tags.split(",") if tag]
    else:
        tag_list = list(tags)
    return [tag for tag in tag_list if not (tag.startswith("科目:") or tag.startswith("年级:") or tag.startswith("项目:"))]


def serialize_problem(problem):
    serialized = dict(problem)
    scope = get_scope_from_tags(serialized["tags"])
    if scope:
        entry = find_catalog_entry(scope["subject"], scope["grade"], scope["project"])
    else:
        entry = None

    answer_mode = entry["answer_mode"] if entry else "integer"
    serialized["answer_mode"] = answer_mode
    serialized["answer_display"] = format_answer(answer_mode, serialized["answer"])
    return serialized


config_path = os.path.join(os.path.dirname(__file__), "config.py")


def is_truthy_env(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def should_auto_seed_problem_banks():
    if "AUTO_SEED_PROBLEM_BANKS" in os.environ:
        return is_truthy_env("AUTO_SEED_PROBLEM_BANKS")
    return not is_truthy_env("VERCEL")


def load_supabase_config():
    env_url = os.environ.get("SUPABASE_URL", "").strip()
    env_key = os.environ.get("SUPABASE_KEY", "").strip()

    if env_url and env_key:
        return env_url, env_key

    if os.path.exists(config_path):
        from config import SUPABASE_KEY, SUPABASE_URL

        if (
            SUPABASE_URL != "https://your-project.supabase.co"
            and SUPABASE_KEY != "your-anon-key"
        ):
            return SUPABASE_URL, SUPABASE_KEY

    raise AppConfigError(
        "缺少 Supabase 配置。请设置环境变量 SUPABASE_URL 和 SUPABASE_KEY，"
        "或在本地 config.py 中填入真实配置。"
    )


def get_db():
    global db, seed_checked

    if db is None:
        supabase_url, supabase_key = load_supabase_config()
        db = MathDatabase(supabase_url, supabase_key)

    if not seed_checked and should_auto_seed_problem_banks():
        ensure_problem_banks_seeded(db)
        seed_checked = True

    return db


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/practice")
def practice():
    return render_template("practice.html")


@app.route("/statistics")
def statistics():
    return render_template("statistics.html")


@app.route("/wrong-book")
def wrong_book():
    return render_template("wrong_book.html")


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()

    if not username:
        return jsonify({"success": False, "message": "用户名不能为空"})

    try:
        database = get_db()
        user_id = database.add_user(username)
    except AppConfigError as exc:
        return jsonify({"success": False, "message": str(exc)}), 500
    except DatabaseSchemaError as exc:
        return jsonify({"success": False, "message": str(exc)}), 500
    except DatabaseWriteError as exc:
        return jsonify({"success": False, "message": f"Supabase 写入失败: {exc}"}), 500

    session["user_id"] = user_id
    session["username"] = username

    return jsonify({"success": True, "user_id": user_id, "username": username})


@app.route("/api/session_state", methods=["GET"])
def session_state():
    practice_settings = None

    if "user_id" in session:
        selection = get_current_selection()
        if selection:
            try:
                database = get_db()
                settings_map = database.get_user_practice_settings(session["user_id"])
                practice_settings = settings_map.get(build_practice_settings_scope_key(selection))
            except AppConfigError as exc:
                return jsonify({"success": False, "message": str(exc)}), 500
            except (DatabaseSchemaError, DatabaseWriteError) as exc:
                return jsonify({"success": False, "message": str(exc)}), 500

    return jsonify(
        {
            "success": True,
            "logged_in": "user_id" in session,
            "username": session.get("username", ""),
            "selection": {
                "subject": session.get("subject", ""),
                "grade": session.get("grade", ""),
                "project": session.get("project", ""),
            },
            "catalog": get_catalog_for_ui(),
            "practice_settings": practice_settings,
        }
    )


@app.route("/api/set_learning_path", methods=["POST"])
def set_learning_path():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "请先登录"})

    data = request.get_json() or {}
    subject = data.get("subject", "").strip()
    grade = data.get("grade", "").strip()
    project = data.get("project", "").strip()

    if not find_catalog_entry(subject, grade, project):
        return jsonify({"success": False, "message": "学习路径选择无效"})

    session["subject"] = subject
    session["grade"] = grade
    session["project"] = project

    return jsonify(
        {
            "success": True,
            "selection": {
                "subject": subject,
                "grade": grade,
                "project": project,
            },
        }
    )


@app.route("/api/save_practice_settings", methods=["POST"])
def save_practice_settings():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "请先登录"}), 401

    selection = get_current_selection()
    if not selection:
        return jsonify({"success": False, "message": "请先选择科目、年级和项目"}), 400

    data = request.get_json() or {}

    try:
        normalized_settings = normalize_practice_settings(selection, data)
        database = get_db()
        database.save_user_practice_settings(
            session["user_id"],
            build_practice_settings_scope_key(selection),
            normalized_settings,
        )
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400
    except AppConfigError as exc:
        return jsonify({"success": False, "message": str(exc)}), 500
    except (DatabaseSchemaError, DatabaseWriteError) as exc:
        return jsonify({"success": False, "message": str(exc)}), 500

    return jsonify({"success": True, "practice_settings": normalized_settings})


@app.route("/api/get_problems", methods=["GET"])
def get_problems():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "请先登录"}), 401

    selection = get_current_selection()
    if not selection:
        return jsonify({"success": False, "message": "请先选择科目、年级和项目"}), 400

    count = request.args.get("count", 10, type=int)
    problem_type = request.args.get("type", None)
    tags = request.args.getlist("tags[]")

    try:
        normalized_request = normalize_practice_settings(
            selection,
            {"count": count, "type": problem_type, "tags": tags},
        )
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400

    count = normalized_request["count"]
    problem_type = normalized_request["type"] or None
    tags = normalized_request["tags"]
    catalog_entry = find_catalog_entry(selection["subject"], selection["grade"], selection["project"])

    try:
        database = get_db()
        if catalog_entry and is_template_project(catalog_entry):
            generated_problems = generate_template_problems(catalog_entry, count, tags, problem_type or "")
            problems = database.insert_problems_and_return(generated_problems)
            scoped_count = -1
        else:
            scope_tags = get_scope_tags_from_selection(selection)
            if tags:
                candidate_problems = database.get_all_problems_by_filters(problem_type, scope_tags)
                selected_groups = get_selected_tag_groups(catalog_entry, tags, problem_type or "")
                filtered_problems = filter_problems_by_selected_groups(candidate_problems, selected_groups)
                random.SystemRandom().shuffle(filtered_problems)
                problems = filtered_problems[:count]
                scoped_count = len(candidate_problems)
            else:
                problems = database.get_problems_by_filters(count, problem_type, scope_tags)
                if not problems:
                    scoped_count = database.get_problem_count(required_tags=scope_tags)
                else:
                    scoped_count = -1
    except AppConfigError as exc:
        return jsonify({"success": False, "message": str(exc)}), 500
    except (DatabaseSchemaError, DatabaseWriteError) as exc:
        return jsonify({"success": False, "message": str(exc)}), 500

    if not problems:
        if scoped_count == 0:
            return jsonify({"success": False, "message": "当前项目题库为空，自动初始化没有成功。"}), 500
        return jsonify({"success": False, "message": "没有找到符合条件的题目，请调整筛选条件。"}), 400

    return jsonify({"success": True, "problems": [serialize_problem(problem) for problem in problems]})


@app.route("/api/debug_problems", methods=["GET"])
def debug_problems():
    selection = get_current_selection()
    if not selection:
        return jsonify({"success": False, "message": "请先选择科目、年级和项目"}), 400

    problem_type = request.args.get("type", None)
    tags = request.args.getlist("tags[]")

    try:
        normalized_request = normalize_practice_settings(
            selection,
            {"count": 10, "type": problem_type, "tags": tags},
        )
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400

    problem_type = normalized_request["type"] or None
    tags = normalized_request["tags"]
    catalog_entry = find_catalog_entry(selection["subject"], selection["grade"], selection["project"])

    try:
        if catalog_entry and is_template_project(catalog_entry):
            desc = build_template_filter_description(catalog_entry, tags, problem_type or "")
            problems = generate_template_problems(catalog_entry, 10, tags, problem_type or "")
        else:
            scope_tags = get_scope_tags_from_selection(selection)
            database = get_db()
            desc, problems = database.debug_problems_by_filters(problem_type, scope_tags)
            if tags:
                selected_groups = get_selected_tag_groups(catalog_entry, tags, problem_type or "")
                desc = f"{desc} | {build_template_filter_description(catalog_entry, tags, problem_type or '')}"
                problems = filter_problems_by_selected_groups(problems, selected_groups)
    except AppConfigError as exc:
        return jsonify({"success": False, "message": str(exc)}), 500
    except (DatabaseSchemaError, DatabaseWriteError) as exc:
        return jsonify({"success": False, "message": str(exc)}), 500

    print(f"\n[DEBUG] Query: {desc}")
    print(f"[DEBUG] 匹配题目数量: {len(problems)}")

    return jsonify(
        {
            "success": True,
            "sql": desc,
            "total": len(problems),
            "problems": [serialize_problem(problem) for problem in problems],
        }
    )


@app.route("/api/submit_answer", methods=["POST"])
def submit_answer():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "请先登录"})

    data = request.get_json() or {}
    problem_id = data.get("problem_id")
    user_answer = data.get("user_answer")

    if problem_id is None or user_answer is None:
        return jsonify({"success": False, "message": "参数错误"})

    try:
        user_answer = int(user_answer)
    except ValueError:
        return jsonify({"success": False, "message": "答案必须是数字"})

    try:
        database = get_db()
        is_correct = database.record_answer(session["user_id"], problem_id, user_answer)
        problem = database.get_problem_by_id(problem_id)
    except AppConfigError as exc:
        return jsonify({"success": False, "message": str(exc)}), 500
    except (DatabaseSchemaError, DatabaseWriteError) as exc:
        return jsonify({"success": False, "message": str(exc)}), 500

    if problem:
        serialized_problem = serialize_problem(problem)
        correct_answer = serialized_problem["answer"]
        correct_answer_display = serialized_problem["answer_display"]
    else:
        correct_answer = None
        correct_answer_display = None

    return jsonify(
        {
            "success": True,
            "is_correct": is_correct,
            "correct_answer": correct_answer,
            "correct_answer_display": correct_answer_display,
        }
    )


@app.route("/api/get_statistics", methods=["GET"])
def get_statistics():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "请先登录"})

    try:
        database = get_db()
        stats = database.get_user_statistics(session["user_id"])
    except AppConfigError as exc:
        return jsonify({"success": False, "message": str(exc)}), 500
    except (DatabaseSchemaError, DatabaseWriteError) as exc:
        return jsonify({"success": False, "message": str(exc)}), 500

    if stats["total_answers"] > 0:
        stats["accuracy"] = round(stats["correct_count"] / stats["total_answers"] * 100, 1)
    else:
        stats["accuracy"] = 0

    stats["username"] = session.get("username", "")
    stats["selection"] = {
        "subject": session.get("subject", ""),
        "grade": session.get("grade", ""),
        "project": session.get("project", ""),
    }

    return jsonify({"success": True, "statistics": stats})


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})


@app.route("/api/get_wrong_problems", methods=["GET"])
def get_wrong_problems():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "请先登录"})

    try:
        database = get_db()
        wrong_problems = database.get_wrong_problems(session["user_id"])
    except AppConfigError as exc:
        return jsonify({"success": False, "message": str(exc)}), 500
    except (DatabaseSchemaError, DatabaseWriteError) as exc:
        return jsonify({"success": False, "message": str(exc)}), 500

    selection = get_current_selection()
    if selection:
        scope_tags = set(get_scope_tags_from_selection(selection))
        wrong_problems = [
            problem
            for problem in wrong_problems
            if scope_tags.issubset(set(problem["tags"].split(",")))
        ]

    return jsonify({"success": True, "wrong_problems": [serialize_problem(problem) for problem in wrong_problems]})


@app.route("/api/get_similar_problems", methods=["POST"])
def get_similar_problems():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "请先登录"})

    selection = get_current_selection()
    if not selection:
        return jsonify({"success": False, "message": "请先选择科目、年级和项目"}), 400

    data = request.get_json() or {}
    tags = data.get("tags")
    count = data.get("count", 10)
    exclude_id = data.get("exclude_id")

    if not tags:
        return jsonify({"success": False, "message": "参数错误"})

    try:
        candidate_count = max(int(count) * 20, 100)
        scope_tags = set(get_scope_tags_from_selection(selection))
        content_tags = strip_scope_tags(tags)
        if len(content_tags) < 2:
            return jsonify({"success": False, "message": "当前题目的有效相似标签不足。"}), 400
        database = get_db()
        problems = database.get_similar_problems(",".join(content_tags), candidate_count, exclude_id)
    except AppConfigError as exc:
        return jsonify({"success": False, "message": str(exc)}), 500
    except (DatabaseSchemaError, DatabaseWriteError) as exc:
        return jsonify({"success": False, "message": str(exc)}), 500

    scoped_problems = [
        problem
        for problem in problems
        if scope_tags.issubset(set(problem["tags"].split(",")))
    ][: int(count)]

    return jsonify({"success": True, "problems": [serialize_problem(problem) for problem in scoped_problems]})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
