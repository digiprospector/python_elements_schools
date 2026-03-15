#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库管理 - Supabase 版本，支持标签筛选和错题本
"""

from supabase import create_client
from datetime import datetime


class MathDatabase:
    def __init__(self, supabase_url, supabase_key):
        self.client = create_client(supabase_url, supabase_key)

    def add_user(self, username):
        """添加用户"""
        # 先查询是否存在
        result = self.client.table('users').select('id').eq('username', username).execute()
        if result.data:
            return result.data[0]['id']
        # 不存在则插入
        result = self.client.table('users').insert({'username': username}).execute()
        return result.data[0]['id']

    def get_problem_by_id(self, problem_id):
        """根据ID获取题目"""
        result = self.client.table('problems').select('*').eq('id', problem_id).execute()
        if result.data:
            return result.data[0]
        return None

    def record_answer(self, user_id, problem_id, user_answer):
        """记录用户答题"""
        # 获取题目信息
        problem = self.get_problem_by_id(problem_id)
        if not problem:
            return False

        correct_answer = problem['answer']
        tags = problem['tags']
        is_correct = (user_answer == correct_answer)

        # 记录答题
        self.client.table('user_answers').insert({
            'user_id': user_id,
            'problem_id': problem_id,
            'user_answer': user_answer,
            'is_correct': is_correct
        }).execute()

        # 处理错题本
        if not is_correct:
            # 答错了，添加到错题本或更新错误次数
            existing = (self.client.table('wrong_problems')
                        .select('*')
                        .eq('user_id', user_id)
                        .eq('problem_id', problem_id)
                        .execute())
            if existing.data:
                # 已存在，更新
                (self.client.table('wrong_problems')
                 .update({
                     'wrong_count': existing.data[0]['wrong_count'] + 1,
                     'correct_streak': 0,
                     'updated_at': datetime.now().isoformat()
                 })
                 .eq('user_id', user_id)
                 .eq('problem_id', problem_id)
                 .execute())
            else:
                # 不存在，插入
                self.client.table('wrong_problems').insert({
                    'user_id': user_id,
                    'problem_id': problem_id,
                    'tags': tags,
                    'wrong_count': 1,
                    'correct_streak': 0
                }).execute()
        else:
            # 答对了，检查是否是错题本中的同类型题目
            self._update_correct_streak(user_id, tags)

        return is_correct

    def _update_correct_streak(self, user_id, tags):
        """更新连续正确次数"""
        # 获取用户所有错题
        result = (self.client.table('wrong_problems')
                  .select('id,tags,correct_streak')
                  .eq('user_id', user_id)
                  .execute())

        tags_list = tags.split(',')

        for wp in result.data:
            wp_tags = wp['tags'].split(',')
            # 如果有至少2个相同标签，认为是同类型题目
            common_tags = set(tags_list) & set(wp_tags)
            if len(common_tags) >= 2:
                new_streak = wp['correct_streak'] + 1
                if new_streak >= 3:
                    # 连续做对3次，从错题本删除
                    (self.client.table('wrong_problems')
                     .delete()
                     .eq('id', wp['id'])
                     .execute())
                else:
                    # 更新连续正确次数
                    (self.client.table('wrong_problems')
                     .update({
                         'correct_streak': new_streak,
                         'updated_at': datetime.now().isoformat()
                     })
                     .eq('id', wp['id'])
                     .execute())

    def get_user_statistics(self, user_id):
        """获取用户答题统计"""
        result = self.client.rpc('get_user_statistics', {'p_user_id': user_id}).execute()
        if result.data:
            stats = result.data
            # RPC 返回 JSON，确保字段为整数
            return {
                'total_answers': int(stats.get('total_answers') or 0),
                'correct_count': int(stats.get('correct_count') or 0),
                'wrong_count': int(stats.get('wrong_count') or 0)
            }
        return {'total_answers': 0, 'correct_count': 0, 'wrong_count': 0}

    def get_problems_by_filters(self, count=10, problem_type=None, required_tags=None):
        """根据筛选条件获取题目（通过 RPC 随机取题）"""
        params = {'p_count': count}
        if problem_type:
            params['p_type'] = problem_type
        if required_tags:
            params['p_tags'] = required_tags

        result = self.client.rpc('get_random_problems', params).execute()
        return result.data or []

    def debug_problems_by_filters(self, problem_type=None, required_tags=None):
        """Debug: 返回查询描述和全部符合条件的题目（不限数量）"""
        query = self.client.table('problems').select('*')
        desc_parts = ['SELECT * FROM problems WHERE 1=1']

        if problem_type:
            query = query.eq('type', problem_type)
            desc_parts.append(f"AND type = '{problem_type}'")

        if required_tags:
            for tag in required_tags:
                query = query.like('tags', f'%{tag}%')
                desc_parts.append(f"AND tags LIKE '%{tag}%'")

        result = query.execute()
        debug_desc = ' '.join(desc_parts)
        return debug_desc, result.data or []

    def get_wrong_problems(self, user_id):
        """获取用户的错题本"""
        # 先获取错题记录
        wrong_result = (self.client.table('wrong_problems')
                        .select('id,problem_id,wrong_count,correct_streak,created_at,updated_at')
                        .eq('user_id', user_id)
                        .order('updated_at', desc=True)
                        .execute())

        if not wrong_result.data:
            return []

        # 获取对应的题目信息
        problem_ids = [wp['problem_id'] for wp in wrong_result.data]
        problems_result = (self.client.table('problems')
                           .select('*')
                           .in_('id', problem_ids)
                           .execute())

        # 构建题目字典
        problems_dict = {p['id']: p for p in problems_result.data}

        # 合并结果
        results = []
        for wp in wrong_result.data:
            problem = problems_dict.get(wp['problem_id'])
            if problem:
                merged = {
                    'wrong_id': wp['id'],
                    'wrong_count': wp['wrong_count'],
                    'correct_streak': wp['correct_streak'],
                    'created_at': wp['created_at'],
                    'updated_at': wp['updated_at'],
                    **problem
                }
                results.append(merged)

        return results

    def get_similar_problems(self, tags, count=10, exclude_id=None):
        """根据标签获取相似题目（通过 RPC）"""
        params = {'p_tags': tags, 'p_count': count}
        if exclude_id:
            params['p_exclude_id'] = exclude_id

        result = self.client.rpc('get_similar_problems', params).execute()
        return result.data or []
