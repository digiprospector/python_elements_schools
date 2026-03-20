#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase-backed database access for the math practice system.
"""

from datetime import datetime

from postgrest.exceptions import APIError
from supabase import create_client


class DatabaseSchemaError(RuntimeError):
    """Raised when the remote Supabase schema is missing required objects."""


class DatabaseWriteError(RuntimeError):
    """Raised when the app cannot write required data to Supabase."""


class MathDatabase:
    def __init__(self, supabase_url, supabase_key):
        self.client = create_client(supabase_url, supabase_key)

    def _wrap_api_error(self, exc):
        code = getattr(exc, "code", None)
        if code == "PGRST205":
            raise DatabaseSchemaError(
                "Supabase 缺少必须的表或函数。请先在 SQL Editor 执行 supabase_schema.sql。"
            ) from exc
        raise DatabaseWriteError(str(exc)) from exc

    def _wrap_practice_settings_error(self, exc):
        if "practice_settings" in str(exc):
            raise DatabaseSchemaError(
                "Supabase 缂哄皯 users.practice_settings 瀛楁銆傝閲嶆柊鎵ц supabase_schema.sql 鏇存柊琛ㄧ粨鏋勩€?"
            ) from exc
        self._wrap_api_error(exc)

    def add_user(self, username):
        try:
            result = self.client.table("users").select("id").eq("username", username).execute()
        except APIError as exc:
            self._wrap_api_error(exc)

        if result.data:
            return result.data[0]["id"]

        try:
            result = self.client.table("users").insert({"username": username}).execute()
        except APIError as exc:
            self._wrap_api_error(exc)
        return result.data[0]["id"]

    def get_user_practice_settings(self, user_id):
        try:
            result = (
                self.client.table("users")
                .select("practice_settings")
                .eq("id", user_id)
                .limit(1)
                .execute()
            )
        except APIError as exc:
            self._wrap_practice_settings_error(exc)

        if not result.data:
            return {}

        settings = result.data[0].get("practice_settings") or {}
        return settings if isinstance(settings, dict) else {}

    def save_user_practice_settings(self, user_id, scope_key, settings):
        settings_map = self.get_user_practice_settings(user_id)
        settings_map[scope_key] = settings

        try:
            (
                self.client.table("users")
                .update({"practice_settings": settings_map})
                .eq("id", user_id)
                .execute()
            )
        except APIError as exc:
            self._wrap_practice_settings_error(exc)

        return settings

    def get_problem_by_id(self, problem_id):
        try:
            result = self.client.table("problems").select("*").eq("id", problem_id).execute()
        except APIError as exc:
            self._wrap_api_error(exc)

        if result.data:
            return result.data[0]
        return None

    def get_problem_count(self, problem_type=None, required_tags=None):
        try:
            query = self.client.table("problems").select("id", count="exact")
            if problem_type:
                query = query.eq("type", problem_type)
            if required_tags:
                for tag in required_tags:
                    query = query.like("tags", f"%{tag}%")
            result = query.limit(1).execute()
        except APIError as exc:
            self._wrap_api_error(exc)

        return int(result.count or 0)

    def insert_problems(self, problems, batch_size=500):
        inserted = 0
        for start in range(0, len(problems), batch_size):
            batch = problems[start:start + batch_size]
            try:
                self.client.table("problems").insert(batch).execute()
            except APIError as exc:
                self._wrap_api_error(exc)
            inserted += len(batch)
        return inserted

    def record_answer(self, user_id, problem_id, user_answer):
        problem = self.get_problem_by_id(problem_id)
        if not problem:
            return False

        correct_answer = problem["answer"]
        tags = problem["tags"]
        is_correct = user_answer == correct_answer

        try:
            self.client.table("user_answers").insert(
                {
                    "user_id": user_id,
                    "problem_id": problem_id,
                    "user_answer": user_answer,
                    "is_correct": is_correct,
                }
            ).execute()
        except APIError as exc:
            self._wrap_api_error(exc)

        if not is_correct:
            try:
                existing = (
                    self.client.table("wrong_problems")
                    .select("*")
                    .eq("user_id", user_id)
                    .eq("problem_id", problem_id)
                    .execute()
                )
            except APIError as exc:
                self._wrap_api_error(exc)

            if existing.data:
                try:
                    (
                        self.client.table("wrong_problems")
                        .update(
                            {
                                "wrong_count": existing.data[0]["wrong_count"] + 1,
                                "correct_streak": 0,
                                "updated_at": datetime.now().isoformat(),
                            }
                        )
                        .eq("user_id", user_id)
                        .eq("problem_id", problem_id)
                        .execute()
                    )
                except APIError as exc:
                    self._wrap_api_error(exc)
            else:
                try:
                    self.client.table("wrong_problems").insert(
                        {
                            "user_id": user_id,
                            "problem_id": problem_id,
                            "tags": tags,
                            "wrong_count": 1,
                            "correct_streak": 0,
                        }
                    ).execute()
                except APIError as exc:
                    self._wrap_api_error(exc)
        else:
            self._update_correct_streak(user_id, tags)

        return is_correct

    def _update_correct_streak(self, user_id, tags):
        try:
            result = (
                self.client.table("wrong_problems")
                .select("id,tags,correct_streak")
                .eq("user_id", user_id)
                .execute()
            )
        except APIError as exc:
            self._wrap_api_error(exc)

        tags_list = tags.split(",")

        for wrong_problem in result.data:
            wrong_tags = wrong_problem["tags"].split(",")
            common_tags = set(tags_list) & set(wrong_tags)
            if len(common_tags) < 2:
                continue

            new_streak = wrong_problem["correct_streak"] + 1
            try:
                if new_streak >= 3:
                    self.client.table("wrong_problems").delete().eq("id", wrong_problem["id"]).execute()
                else:
                    (
                        self.client.table("wrong_problems")
                        .update(
                            {
                                "correct_streak": new_streak,
                                "updated_at": datetime.now().isoformat(),
                            }
                        )
                        .eq("id", wrong_problem["id"])
                        .execute()
                    )
            except APIError as exc:
                self._wrap_api_error(exc)

    def get_user_statistics(self, user_id):
        try:
            result = self.client.rpc("get_user_statistics", {"p_user_id": user_id}).execute()
        except APIError as exc:
            self._wrap_api_error(exc)

        if result.data:
            stats = result.data
            return {
                "total_answers": int(stats.get("total_answers") or 0),
                "correct_count": int(stats.get("correct_count") or 0),
                "wrong_count": int(stats.get("wrong_count") or 0),
            }
        return {"total_answers": 0, "correct_count": 0, "wrong_count": 0}

    def get_problems_by_filters(self, count=10, problem_type=None, required_tags=None):
        params = {"p_count": count}
        if problem_type:
            params["p_type"] = problem_type
        if required_tags:
            params["p_tags"] = required_tags

        try:
            result = self.client.rpc("get_random_problems", params).execute()
        except APIError as exc:
            self._wrap_api_error(exc)
        return result.data or []

    def debug_problems_by_filters(self, problem_type=None, required_tags=None):
        query = self.client.table("problems").select("*")
        desc_parts = ["SELECT * FROM problems WHERE 1=1"]

        if problem_type:
            query = query.eq("type", problem_type)
            desc_parts.append(f"AND type = '{problem_type}'")

        if required_tags:
            for tag in required_tags:
                query = query.like("tags", f"%{tag}%")
                desc_parts.append(f"AND tags LIKE '%{tag}%'")

        try:
            result = query.execute()
        except APIError as exc:
            self._wrap_api_error(exc)
        return " ".join(desc_parts), result.data or []

    def get_wrong_problems(self, user_id):
        try:
            wrong_result = (
                self.client.table("wrong_problems")
                .select("id,problem_id,wrong_count,correct_streak,created_at,updated_at")
                .eq("user_id", user_id)
                .order("updated_at", desc=True)
                .execute()
            )
        except APIError as exc:
            self._wrap_api_error(exc)

        if not wrong_result.data:
            return []

        problem_ids = [wrong_problem["problem_id"] for wrong_problem in wrong_result.data]
        try:
            problems_result = self.client.table("problems").select("*").in_("id", problem_ids).execute()
        except APIError as exc:
            self._wrap_api_error(exc)

        problems_dict = {problem["id"]: problem for problem in problems_result.data}

        results = []
        for wrong_problem in wrong_result.data:
            problem = problems_dict.get(wrong_problem["problem_id"])
            if not problem:
                continue
            results.append(
                {
                    "wrong_id": wrong_problem["id"],
                    "wrong_count": wrong_problem["wrong_count"],
                    "correct_streak": wrong_problem["correct_streak"],
                    "created_at": wrong_problem["created_at"],
                    "updated_at": wrong_problem["updated_at"],
                    **problem,
                }
            )

        return results

    def get_similar_problems(self, tags, count=10, exclude_id=None):
        params = {"p_tags": tags, "p_count": count}
        if exclude_id:
            params["p_exclude_id"] = exclude_id

        try:
            result = self.client.rpc("get_similar_problems", params).execute()
        except APIError as exc:
            self._wrap_api_error(exc)
        return result.data or []
