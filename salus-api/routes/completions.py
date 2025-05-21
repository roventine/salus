from flask import Blueprint, request, jsonify
import sqlite3
from datetime import datetime

completions_bp = Blueprint('completions', __name__)

# 获取所有完成记录
@completions_bp.route('/completions', methods=['GET'])
def get_completions():
    conn = sqlite3.connect('salus.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 支持按日期范围筛选
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    task_id = request.args.get('task_id')
    
    query = '''
        SELECT c.*, t.scheduled_time, e.name as exercise_name
        FROM completions c
        JOIN training_tasks t ON c.task_id = t.id
        JOIN exercises e ON t.exercise_id = e.id
    '''
    
    params = []
    where_clauses = []
    
    if start_date:
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            where_clauses.append('date(c.completed_at) >= ?')
            params.append(start_date)
        except ValueError:
            conn.close()
            return jsonify({"error": "开始日期格式无效，请使用YYYY-MM-DD格式"}), 400
    
    if end_date:
        try:
            datetime.strptime(end_date, '%Y-%m-%d')
            where_clauses.append('date(c.completed_at) <= ?')
            params.append(end_date)
        except ValueError:
            conn.close()
            return jsonify({"error": "结束日期格式无效，请使用YYYY-MM-DD格式"}), 400
    
    if task_id:
        try:
            task = int(task_id)
            where_clauses.append('c.task_id = ?')
            params.append(task)
        except ValueError:
            conn.close()
            return jsonify({"error": "任务ID必须是整数"}), 400
    
    if where_clauses:
        query += ' WHERE ' + ' AND '.join(where_clauses)
    
    query += ' ORDER BY c.completed_at DESC'
    
    cursor.execute(query, params)
    completions = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return jsonify(completions)

# 获取单个完成记录
@completions_bp.route('/completions/<int:id>', methods=['GET'])
def get_completion(id):
    conn = sqlite3.connect('salus.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT c.*, t.scheduled_time, e.name as exercise_name
        FROM completions c
        JOIN training_tasks t ON c.task_id = t.id
        JOIN exercises e ON t.exercise_id = e.id
        WHERE c.id = ?
    ''', (id,))
    
    completion = cursor.fetchone()
    
    if completion is None:
        conn.close()
        return jsonify({"error": "完成记录不存在"}), 404
    
    conn.close()
    return jsonify(dict(completion))

# 创建完成记录
@completions_bp.route('/completions', methods=['POST'])
def create_completion():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "无效的请求数据"}), 400
    
    required_fields = ['task_id']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"缺少必填字段: {field}"}), 400
    
    task_id = data['task_id']
    actual_sets = data.get('actual_sets')
    notes = data.get('notes', '')
    
    conn = sqlite3.connect('salus.db')
    cursor = conn.cursor()
    
    # 验证任务是否存在
    cursor.execute('SELECT id FROM training_tasks WHERE id = ?', (task_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"error": "任务不存在"}), 404
    
    # 插入完成记录
    cursor.execute('''
        INSERT INTO completions (task_id, completed_at, actual_sets, notes)
        VALUES (?, datetime('now', 'localtime'), ?, ?)
    ''', (task_id, actual_sets, notes))
    
    # 更新任务状态为已完成
    cursor.execute('''
        UPDATE training_tasks
        SET is_completed = 1
        WHERE id = ?
    ''', (task_id,))
    
    completion_id = cursor.lastrowid
    conn.commit()
    
    # 获取新创建的记录
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.*, t.scheduled_time, e.name as exercise_name
        FROM completions c
        JOIN training_tasks t ON c.task_id = t.id
        JOIN exercises e ON t.exercise_id = e.id
        WHERE c.id = ?
    ''', (completion_id,))
    
    new_completion = dict(cursor.fetchone())
    
    conn.close()
    return jsonify(new_completion), 201

# 更新完成记录
@completions_bp.route('/completions/<int:id>', methods=['PUT'])
def update_completion(id):
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "无效的请求数据"}), 400
    
    actual_sets = data.get('actual_sets')
    notes = data.get('notes')
    
    conn = sqlite3.connect('salus.db')
    cursor = conn.cursor()
    
    # 验证记录是否存在
    cursor.execute('SELECT id FROM completions WHERE id = ?', (id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"error": "完成记录不存在"}), 404
    
    # 构建更新查询
    update_fields = []
    params = []
    
    if actual_sets is not None:
        update_fields.append('actual_sets = ?')
        params.append(actual_sets)
    
    if notes is not None:
        update_fields.append('notes = ?')
        params.append(notes)
    
    if not update_fields:
        conn.close()
        return jsonify({"error": "没有提供要更新的字段"}), 400
    
    query = f'''
        UPDATE completions
        SET {', '.join(update_fields)}
        WHERE id = ?
    '''
    params.append(id)
    
    cursor.execute(query, params)
    conn.commit()
    
    # 获取更新后的记录
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.*, t.scheduled_time, e.name as exercise_name
        FROM completions c
        JOIN training_tasks t ON c.task_id = t.id
        JOIN exercises e ON t.exercise_id = e.id
        WHERE c.id = ?
    ''', (id,))
    
    updated_completion = dict(cursor.fetchone())
    
    conn.close()
    return jsonify(updated_completion)

# 删除完成记录
@completions_bp.route('/completions/<int:id>', methods=['DELETE'])
def delete_completion(id):
    conn = sqlite3.connect('salus.db')
    cursor = conn.cursor()
    
    # 验证记录是否存在
    cursor.execute('SELECT task_id FROM completions WHERE id = ?', (id,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return jsonify({"error": "完成记录不存在"}), 404
    
    task_id = result[0]
    
    # 删除记录
    cursor.execute('DELETE FROM completions WHERE id = ?', (id,))
    
    # 更新任务状态为未完成（如果没有其他完成记录）
    cursor.execute('SELECT COUNT(*) FROM completions WHERE task_id = ?', (task_id,))
    count = cursor.fetchone()[0]
    
    if count == 0:
        cursor.execute('''
            UPDATE training_tasks
            SET is_completed = 0
            WHERE id = ?
        ''', (task_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({"message": "完成记录已删除", "id": id})

# 获取统计数据
@completions_bp.route('/completions/stats', methods=['GET'])
def get_completion_stats():
    conn = sqlite3.connect('salus.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 支持按日期范围筛选
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    cycle_id = request.args.get('cycle_id')
    
    params = []
    where_clauses = []
    
    if start_date:
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            where_clauses.append('date(c.completed_at) >= ?')
            params.append(start_date)
        except ValueError:
            conn.close()
            return jsonify({"error": "开始日期格式无效，请使用YYYY-MM-DD格式"}), 400
    
    if end_date:
        try:
            datetime.strptime(end_date, '%Y-%m-%d')
            where_clauses.append('date(c.completed_at) <= ?')
            params.append(end_date)
        except ValueError:
            conn.close()
            return jsonify({"error": "结束日期格式无效，请使用YYYY-MM-DD格式"}), 400
    
    if cycle_id:
        try:
            cycle = int(cycle_id)
            where_clauses.append('t.cycle_id = ?')
            params.append(cycle)
        except ValueError:
            conn.close()
            return jsonify({"error": "周期ID必须是整数"}), 400
    
    where_clause = ' WHERE ' + ' AND '.join(where_clauses) if where_clauses else ''
    
    # 获取总完成任务数
    query = f'''
        SELECT COUNT(*) as total_completions
        FROM completions c
        JOIN training_tasks t ON c.task_id = t.id
        {where_clause}
    '''
    cursor.execute(query, params)
    total_completions = cursor.fetchone()['total_completions']
    
    # 获取总组数
    query = f'''
        SELECT SUM(c.actual_sets) as total_sets
        FROM completions c
        JOIN training_tasks t ON c.task_id = t.id
        {where_clause}
    '''
    cursor.execute(query, params)
    total_sets = cursor.fetchone()['total_sets'] or 0
    
    # 按运动类型统计
    query = f'''
        SELECT e.name, COUNT(*) as count, SUM(c.actual_sets) as total_sets
        FROM completions c
        JOIN training_tasks t ON c.task_id = t.id
        JOIN exercises e ON t.exercise_id = e.id
        {where_clause}
        GROUP BY e.name
        ORDER BY count DESC
    '''
    cursor.execute(query, params)
    exercise_stats = [dict(row) for row in cursor.fetchall()]
    
    # 按日期统计
    query = f'''
        SELECT date(c.completed_at) as date, COUNT(*) as count
        FROM completions c
        JOIN training_tasks t ON c.task_id = t.id
        {where_clause}
        GROUP BY date(c.completed_at)
        ORDER BY date
    '''
    cursor.execute(query, params)
    date_stats = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        "total_completions": total_completions,
        "total_sets": total_sets,
        "exercise_stats": exercise_stats,
        "date_stats": date_stats
    })