from flask import Blueprint, request, jsonify
import sqlite3
from datetime import datetime, date

tasks_bp = Blueprint('tasks', __name__)

# 获取所有训练任务
@tasks_bp.route('/tasks', methods=['GET'])
def get_tasks():
    conn = sqlite3.connect('salus.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 支持按日期筛选
    specific_date = request.args.get('date')
    day_of_week = request.args.get('day_of_week')
    cycle_id = request.args.get('cycle_id')
    
    query = '''
        SELECT t.*, e.name as exercise_name, e.duration_sec, e.rest_sec
        FROM training_tasks t
        JOIN exercises e ON t.exercise_id = e.id
    '''
    
    params = []
    where_clauses = []
    
    if specific_date:
        try:
            # 验证日期格式
            parsed_date = datetime.strptime(specific_date, '%Y-%m-%d').date()
            where_clauses.append('(t.specific_date = ? OR t.specific_date IS NULL)')
            params.append(specific_date)
        except ValueError:
            conn.close()
            return jsonify({"error": "日期格式无效，请使用YYYY-MM-DD格式"}), 400
    
    if day_of_week:
        try:
            day = int(day_of_week)
            if 0 <= day <= 6:
                if where_clauses:
                    where_clauses.append('(t.day_of_week = ? OR t.day_of_week IS NULL)')
                else:
                    where_clauses.append('t.day_of_week = ?')
                params.append(day)
            else:
                conn.close()
                return jsonify({"error": "星期几必须是0-6之间的整数"}), 400
        except ValueError:
            conn.close()
            return jsonify({"error": "星期几必须是整数"}), 400
    
    if cycle_id:
        try:
            cycle = int(cycle_id)
            where_clauses.append('t.cycle_id = ?')
            params.append(cycle)
        except ValueError:
            conn.close()
            return jsonify({"error": "周期ID必须是整数"}), 400
    
    if where_clauses:
        query += ' WHERE ' + ' AND '.join(where_clauses)
    
    query += ' ORDER BY t.scheduled_time'
    
    cursor.execute(query, params)
    tasks = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return jsonify(tasks)

# 获取单个训练任务
@tasks_bp.route('/tasks/<int:id>', methods=['GET'])
def get_task(id):
    conn = sqlite3.connect('salus.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT t.*, e.name as exercise_name, e.duration_sec, e.rest_sec
        FROM training_tasks t
        JOIN exercises e ON t.exercise_id = e.id
        WHERE t.id = ?
    ''', (id,))
    
    task = cursor.fetchone()
    
    if task is None:
        conn.close()
        return jsonify({"error": "训练任务不存在"}), 404
    
    # 获取完成记录
    cursor.execute('''
        SELECT * FROM completions
        WHERE task_id = ?
        ORDER BY completed_at DESC
    ''', (id,))
    
    completions = [dict(row) for row in cursor.fetchall()]
    
    result = dict(task)
    result['completions'] = completions
    
    conn.close()
    return jsonify(result)

# 创建新的训练任务
@tasks_bp.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    
    required_fields = ['cycle_id', 'exercise_id', 'scheduled_time', 'sets']
    if not data or not all(k in data for k in required_fields):
        return jsonify({"error": f"请提供必要的字段：{', '.join(required_fields)}"}), 400
    
    conn = sqlite3.connect('salus.db')
    cursor = conn.cursor()
    
    # 验证周期ID是否存在
    cursor.execute('SELECT id FROM recovery_cycles WHERE id = ?', (data['cycle_id'],))
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({"error": "指定的康复周期不存在"}), 400
    
    # 验证运动ID是否存在
    cursor.execute('SELECT id FROM exercises WHERE id = ?', (data['exercise_id'],))
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({"error": "指定的运动类型不存在"}), 400
    
    # 验证时间格式
    try:
        datetime.strptime(data['scheduled_time'], '%H:%M:%S')
    except ValueError:
        try:
            # 尝试没有秒的格式
            time_str = datetime.strptime(data['scheduled_time'], '%H:%M').strftime('%H:%M:%S')
            data['scheduled_time'] = time_str
        except ValueError:
            conn.close()
            return jsonify({"error": "时间格式无效，请使用HH:MM:SS或HH:MM格式"}), 400
    
    # 验证specific_date格式（如果提供）
    if 'specific_date' in data and data['specific_date']:
        try:
            datetime.strptime(data['specific_date'], '%Y-%m-%d')
        except ValueError:
            conn.close()
            return jsonify({"error": "日期格式无效，请使用YYYY-MM-DD格式"}), 400
    
    # 验证day_of_week（如果提供）
    if 'day_of_week' in data and data['day_of_week'] is not None:
        try:
            day = int(data['day_of_week'])
            if not (0 <= day <= 6):
                conn.close()
                return jsonify({"error": "星期几必须是0-6之间的整数"}), 400
        except ValueError:
            conn.close()
            return jsonify({"error": "星期几必须是整数"}), 400
    
    cursor.execute(
        '''
        INSERT INTO training_tasks 
        (cycle_id, exercise_id, scheduled_time, sets, day_of_week, specific_date)
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
        (
            data['cycle_id'], 
            data['exercise_id'], 
            data['scheduled_time'], 
            data['sets'], 
            data.get('day_of_week'), 
            data.get('specific_date')
        )
    )
    
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    
    return jsonify({"id": new_id, "message": "训练任务创建成功"}), 201

# 更新训练任务
@tasks_bp.route('/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "请提供更新数据"}), 400
    
    conn = sqlite3.connect('salus.db')
    cursor = conn.cursor()
    
    # 检查训练任务是否存在
    cursor.execute('SELECT id FROM training_tasks WHERE id = ?', (id,))
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({"error": "训练任务不存在"}), 404
    
    # 构建更新语句
    fields = []
    values = []
    
    if 'cycle_id' in data:
        # 验证周期ID是否存在
        cursor.execute('SELECT id FROM recovery_cycles WHERE id = ?', (data['cycle_id'],))
        if cursor.fetchone() is None:
            conn.close()
            return jsonify({"error": "指定的康复周期不存在"}), 400
        
        fields.append('cycle_id = ?')
        values.append(data['cycle_id'])
    
    if 'exercise_id' in data:
        # 验证运动ID是否存在
        cursor.execute('SELECT id FROM exercises WHERE id = ?', (data['exercise_id'],))
        if cursor.fetchone() is None:
            conn.close()
            return jsonify({"error": "指定的运动类型不存在"}), 400
        
        fields.append('exercise_id = ?')
        values.append(data['exercise_id'])
    
    if 'scheduled_time' in data:
        # 验证时间格式
        try:
            datetime.strptime(data['scheduled_time'], '%H:%M:%S')
            fields.append('scheduled_time = ?')
            values.append(data['scheduled_time'])
        except ValueError:
            try:
                # 尝试没有秒的格式
                time_str = datetime.strptime(data['scheduled_time'], '%H:%M').strftime('%H:%M:%S')
                fields.append('scheduled_time = ?')
                values.append(time_str)
            except ValueError:
                conn.close()
                return jsonify({"error": "时间格式无效，请使用HH:MM:SS或HH:MM格式"}), 400
    
    if 'sets' in data:
        fields.append('sets = ?')
        values.append(data['sets'])
    
    if 'day_of_week' in data:
        if data['day_of_week'] is not None:
            try:
                day = int(data['day_of_week'])
                if not (0 <= day <= 6):
                    conn.close()
                    return jsonify({"error": "星期几必须是0-6之间的整数"}), 400
            except ValueError:
                conn.close()
                return jsonify({"error": "星期几必须是整数"}), 400
        
        fields.append('day_of_week = ?')
        values.append(data['day_of_week'])
    
    if 'specific_date' in data:
        if data['specific_date']:
            try:
                datetime.strptime(data['specific_date'], '%Y-%m-%d')
            except ValueError:
                conn.close()
                return jsonify({"error": "日期格式无效，请使用YYYY-MM-DD格式"}), 400
        
        fields.append('specific_date = ?')
        values.append(data['specific_date'])
    
    if 'is_completed' in data:
        fields.append('is_completed = ?')
        values.append(1 if data['is_completed'] else 0)
    
    if not fields:
        conn.close()
        return jsonify({"error": "没有提供有效的更新字段"}), 400
    
    values.append(id)
    
    cursor.execute(
        f'UPDATE training_tasks SET {", ".join(fields)} WHERE id = ?',
        tuple(values)
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({"message": "训练任务更新成功"})

# 删除训练任务
@tasks_bp.route('/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    conn = sqlite3.connect('salus.db')
    cursor = conn.cursor()
    
    # 检查训练任务是否存在
    cursor.execute('SELECT id FROM training_tasks WHERE id = ?', (id,))
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({"error": "训练任务不存在"}), 404
    
    # 删除相关的完成记录
    cursor.execute('DELETE FROM completions WHERE task_id = ?', (id,))
    
    # 删除训练任务
    cursor.execute('DELETE FROM training_tasks WHERE id = ?', (id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({"message": "训练任务及相关完成记录删除成功"})

# 标记任务为已完成
@tasks_bp.route('/tasks/<int:id>/complete', methods=['POST'])
def complete_task(id):
    data = request.get_json() or {}
    
    conn = sqlite3.connect('salus.db')
    cursor = conn.cursor()
    
    # 检查训练任务是否存在
    cursor.execute('SELECT id FROM training_tasks WHERE id = ?', (id,))
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({"error": "训练任务不存在"}), 404
    
    # 更新任务状态为已完成
    cursor.execute('UPDATE training_tasks SET is_completed = 1 WHERE id = ?', (id,))
    
    # 添加完成记录
    cursor.execute(
        'INSERT INTO completions (task_id, actual_sets, notes) VALUES (?, ?, ?)',
        (id, data.get('actual_sets'), data.get('notes', ''))
    )
    
    conn.commit()
    completion_id = cursor.lastrowid
    conn.close()
    
    return jsonify({
        "message": "任务已标记为完成",
        "completion_id": completion_id
    })