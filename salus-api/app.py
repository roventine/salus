from flask import Flask
from flask_cors import CORS
# 确保导入所有蓝图
from routes.exercises import exercises_bp
from routes.tasks import tasks_bp
from routes.completions import completions_bp
from routes.cycles import cycles_bp

app = Flask(__name__)
CORS(app)

# 注册所有蓝图
app.register_blueprint(exercises_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(completions_bp)
app.register_blueprint(cycles_bp)

if __name__ == '__main__':
    app.run(debug=False, port=5000)
