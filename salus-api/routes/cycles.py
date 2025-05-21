from flask import Blueprint, request, jsonify
import sqlite3
from datetime import datetime

cycles_bp = Blueprint('cycles', __name__)

# 获取所有康复周期
@cycles_bp.route('/cycles', methods=['GET'])
def get_cycles():
    conn = sqlite3.connect('salus.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM recovery_cycles ORDER BY start_date DESC')
    cycles = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return jsonify(cycles)

# 获取单个康复周期
@cycles_bp.route('/cycles/<int:id>', methods=['GET'])
def get_cycle(id):
    conn = sqlite3.connect('salus.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM recovery_cycles WHERE id = ?', (id,))
    cycle = cursor.fetchone()
    
    if cycle is None:
        conn.close()
        return jsonify({"error": "康复周期不存在"}), 404
    
    # 获取该周期的所有训练任务
    cursor.execute('''
        SELECT t.*, e.name as exercise_name 
        FROM training_tasks t
        JOIN exercises e ON t.exercise_id = e.id
        WHERE t.cycle_id = ?
        ORDER BY t.day_of_week, t.scheduled_time
    ''', (id,))
    
    tasks = [dict(row) for row in cursor.fetchall()]
    
    result = dict(cycle)
    result['tasks'] = tasks
    
    conn.close()
    return jsonify(result)

# 创建新的康复周期
@cycles_bp.route('/cycles', methods=['POST'])
def create_cycle():
    data = request.get_json()
    
    if not data or not all(k in data for k in ('name', 'start_date', 'end_date')):
        return jsonify({"error": "请提供必要的字段：name, start_date, end_date"}), 400
    
    conn = sqlite3.connect('salus.db')
    cursor = conn.cursor()
    
    try:
        # 验证日期格式
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        
        if start_date > end_date:
            conn.close()
            return jsonify({"error": "开始日期不能晚于结束日期"}), 400
        
        cursor.execute(
            'INSERT INTO recovery_cycles (name, start_date, end_date, notes) VALUES (?, ?, ?, ?)',
            (data['name'], data['start_date'], data['end_date'], data.get('notes', ''))
        )
        
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        
        return jsonify({"id": new_id, "message": "康复周期创建成功"}), 201
    
    except ValueError:
        conn.close()
        return jsonify({"error": "日期格式无效，请使用YYYY-MM-DD格式"}), 400

# 更新康复周期
@cycles_bp.route('/cycles/<int:id>', methods=['PUT'])
def update_cycle(id):
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "请提供更新数据"}), 400
    
    conn = sqlite3.connect('salus.db')
    cursor = conn.cursor()
    
    # 检查康复周期是否存在
    cursor.execute('SELECT id FROM recovery_cycles WHERE id = ?', (id,))
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({"error": "康复周期不存在"}), 404
    
    # 构建更新语句
    fields = []
    values = []
    
    if 'name' in data:
        fields.append('name = ?')
        values.append(data['name'])
    
    if 'start_date' in data:
        try:
            datetime.strptime(data['start_date'], '%Y-%m-%d')
            fields.append('start_date = ?')
            values.append(data['start_date'])
        except ValueError:
            conn.close()
            return jsonify({"error": "开始日期格式无效，请使用YYYY-MM-DD格式"}), 400
    
    if 'end_date' in data:
        try:
            datetime.strptime(data['end_date'], '%Y-%m-%d')
            fields.append('end_date = ?')
            values.append(data['end_date'])
        except ValueError:
            conn.close()
            return jsonify({"error": "结束日期格式无效，请使用YYYY-MM-DD格式"}), 400
    
    if 'notes' in data:
        fields.append('notes = ?')
        values.append(data['notes'])
    
    if not fields:
        conn.close()
        return jsonify({"error": "没有提供有效的更新字段"}), 400
    
    values.append(id)
    
    cursor.execute(
        f'UPDATE recovery_cycles SET {", ".join(fields)} WHERE id = ?',
        tuple(values)
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({"message": "康复周期更新成功"})

# 删除康复周期
@cycles_bp.route('/cycles/<int:id>', methods=['DELETE'])
def delete_cycle(id):
    conn = sqlite3.connect('salus.db')
    cursor = conn.cursor()
    
    # 检查康复周期是否存在
    cursor.execute('SELECT id FROM recovery_cycles WHERE id = ?', (id,))
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({"error": "康复周期不存在"}), 404
    
    # 检查是否有训练任务引用了该康复周期
    cursor.execute('SELECT id FROM training_tasks WHERE cycle_id = ?', (id,))
    if cursor.fetchone() is not None:
        # 删除关联的训练任务
        cursor.execute('DELETE FROM training_tasks WHERE cycle_id = ?', (id,))
    
    cursor.execute('DELETE FROM recovery_cycles WHERE id = ?', (id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({"message": "康复周期及相关训练任务删除成功"})