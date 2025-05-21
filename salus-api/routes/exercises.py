from flask import Blueprint, request, jsonify
import sqlite3

exercises_bp = Blueprint('exercises', __name__)

# 获取所有运动类型
@exercises_bp.route('/exercises', methods=['GET'])
def get_exercises():
    conn = sqlite3.connect('salus.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM exercises ORDER BY name')
    exercises = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return jsonify(exercises)

# 获取单个运动类型
@exercises_bp.route('/exercises/<int:id>', methods=['GET'])
def get_exercise(id):
    conn = sqlite3.connect('salus.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM exercises WHERE id = ?', (id,))
    exercise = cursor.fetchone()
    
    conn.close()
    
    if exercise is None:
        return jsonify({"error": "运动类型不存在"}), 404
    
    return jsonify(dict(exercise))

# 创建新的运动类型
@exercises_bp.route('/exercises', methods=['POST'])
def create_exercise():
    data = request.get_json()
    
    if not data or not all(k in data for k in ('name', 'duration_sec', 'rest_sec')):
        return jsonify({"error": "请提供必要的字段：name, duration_sec, rest_sec"}), 400
    
    conn = sqlite3.connect('salus.db')
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT INTO exercises (name, duration_sec, rest_sec, description) VALUES (?, ?, ?, ?)',
        (data['name'], data['duration_sec'], data['rest_sec'], data.get('description', ''))
    )
    
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    
    return jsonify({"id": new_id, "message": "运动类型创建成功"}), 201

# 更新运动类型
@exercises_bp.route('/exercises/<int:id>', methods=['PUT'])
def update_exercise(id):
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "请提供更新数据"}), 400
    
    conn = sqlite3.connect('salus.db')
    cursor = conn.cursor()
    
    # 检查运动类型是否存在
    cursor.execute('SELECT id FROM exercises WHERE id = ?', (id,))
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({"error": "运动类型不存在"}), 404
    
    # 构建更新语句
    fields = []
    values = []
    
    if 'name' in data:
        fields.append('name = ?')
        values.append(data['name'])
    
    if 'duration_sec' in data:
        fields.append('duration_sec = ?')
        values.append(data['duration_sec'])
    
    if 'rest_sec' in data:
        fields.append('rest_sec = ?')
        values.append(data['rest_sec'])
    
    if 'description' in data:
        fields.append('description = ?')
        values.append(data['description'])
    
    if not fields:
        conn.close()
        return jsonify({"error": "没有提供有效的更新字段"}), 400
    
    values.append(id)
    
    cursor.execute(
        f'UPDATE exercises SET {", ".join(fields)} WHERE id = ?',
        tuple(values)
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({"message": "运动类型更新成功"})

# 删除运动类型
@exercises_bp.route('/exercises/<int:id>', methods=['DELETE'])
def delete_exercise(id):
    conn = sqlite3.connect('salus.db')
    cursor = conn.cursor()
    
    # 检查运动类型是否存在
    cursor.execute('SELECT id FROM exercises WHERE id = ?', (id,))
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({"error": "运动类型不存在"}), 404
    
    # 检查是否有训练任务引用了该运动类型
    cursor.execute('SELECT id FROM training_tasks WHERE exercise_id = ?', (id,))
    if cursor.fetchone() is not None:
        conn.close()
        return jsonify({"error": "无法删除，该运动类型已被训练任务引用"}), 400
    
    cursor.execute('DELETE FROM exercises WHERE id = ?', (id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({"message": "运动类型删除成功"})