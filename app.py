# app.py - My LMS — Render-Optimized Version

import os
import logging
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, abort, jsonify, send_from_directory
from werkzeug.utils import secure_filename

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# ===== Logging =====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== Flask App =====
app = Flask(__name__)
app.config.from_object("config.Config")

# ===== Paths =====
folders = [
    app.instance_path,
    os.path.join(app.instance_path, 'uploads'),
    os.path.join(app.instance_path, 'materials'),
    os.path.join(app.instance_path, 'payment_proofs'),
    os.path.join(app.instance_path, 'receipts'),
    os.path.join(app.instance_path, 'profile_pics'),
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)

logger.info("App instance path: %s", app.instance_path)

# ===== Extensions =====
from utils.extensions import db, mail, socketio
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect, CSRFError, generate_csrf
from flask_session import Session
from flask_login import LoginManager, login_required, logout_user

db.init_app(app)
mail.init_app(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)
sess = Session(app)

# ===== Production Check & SocketIO =====
IS_PRODUCTION = os.environ.get("FLASK_ENV") == "production"

if IS_PRODUCTION:
    import eventlet
    eventlet.monkey_patch()
SOCKETIO_ASYNC_MODE = "eventlet" if IS_PRODUCTION else "threading"
logger.info("SocketIO async_mode=%s", SOCKETIO_ASYNC_MODE)
socketio.init_app(app, async_mode=SOCKETIO_ASYNC_MODE, manage_session=False)

# ===== Login Manager =====
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'select_portal'

@login_manager.user_loader
def load_user(user_id):
    try:
        from models import Admin, User
        if user_id.startswith("admin:"):
            uid = user_id.split(":", 1)[1]
            return Admin.query.filter_by(public_id=uid).first()
        elif user_id.startswith("user:"):
            uid = user_id.split(":", 1)[1]
            return User.query.filter_by(public_id=uid).first()
    except Exception as e:
        logger.exception("user_loader error: %s", e)
    return None

# ===== Context processors =====
@app.context_processor
def inject_csrf():
    return dict(csrf_token=generate_csrf)

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

@app.context_processor
def inject_active_assessment_period():
    def get_active_period():
        try:
            from models import TeacherAssessmentPeriod
            return TeacherAssessmentPeriod.query.filter_by(is_active=True).first()
        except Exception as e:
            logger.warning("Error fetching active assessment period: %s", e)
            return None
    return {'active_assessment_period': get_active_period}

# ===== Error Handlers =====
@app.errorhandler(CSRFError)
def handle_csrf(e):
    return jsonify({'error': 'CSRF token missing or invalid', 'reason': e.description}), 400

@app.after_request
def set_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers.setdefault('Cache-Control', 'no-store')
    return response

# ===== One-Time Initialization =====
def one_time_init():
    logger.info("===== STARTING APP INITIALIZATION =====")
    from models import Admin, SchoolClass
    from utils.helpers import get_class_choices

    db.create_all()
    logger.info("✓ Database tables created/verified")

    if not Admin.query.filter_by(username='SuperAdmin').first():
        admin = Admin(username='SuperAdmin', admin_id='ADM001')
        admin.set_password('Password123')
        db.session.add(admin)
        db.session.commit()
        logger.info("✓ SuperAdmin created")
    else:
        logger.info("✓ SuperAdmin already exists")

    existing = {c.name for c in SchoolClass.query.all()}
    created = 0
    for name, _ in get_class_choices():
        if name not in existing:
            db.session.add(SchoolClass(name=name))
            created += 1
    if created:
        db.session.commit()
        logger.info(f"✓ Created {created} default classes")
    else:
        logger.info("✓ All default classes already exist")
    logger.info("===== APP INITIALIZATION COMPLETE =====")

# ===== Blueprints (Lazy Import) =====
def register_blueprints():
    from admin_routes import admin_bp
    from teacher_routes import teacher_bp
    from student_routes import student_bp
    from parent_routes import parent_bp
    from utils.auth_routes import auth_bp
    from exam_routes import exam_bp
    from vclass_routes import vclass_bp
    from chat_routes import chat_bp
    from admissions.routes import admissions_bp

    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(teacher_bp, url_prefix="/teacher")
    app.register_blueprint(student_bp, url_prefix="/student")
    app.register_blueprint(parent_bp, url_prefix="/parent")
    app.register_blueprint(auth_bp)
    app.register_blueprint(exam_bp, url_prefix="/exam")
    app.register_blueprint(vclass_bp, url_prefix="/vclass")
    app.register_blueprint(chat_bp, url_prefix="/chat")
    app.register_blueprint(admissions_bp, url_prefix="/admissions")
    logger.info("✓ All blueprints registered")

register_blueprints()

# ===== Routes =====
@app.route('/')
def home():
    try:
        return render_template('home.html')
    except Exception as e:
        logger.exception("Template error on /: %s", e)
        return f"<h1>Template rendering error: {e}</h1>", 500

@app.route('/portal')
def select_portal():
    return render_template('portal_selection.html')

@app.route('/portal/<portal>')
def redirect_to_portal(portal):
    mapping = {
        'exams': 'exam.exam_login',
        'teachers': 'teacher.teacher_login',
        'students': 'student.student_login',
        'parents': 'parent.parent_login',
        'vclass': 'vclass.vclass_login'
    }
    key = portal.lower()
    if key not in mapping:
        abort(404)
    return redirect(url_for(mapping[key]))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('select_portal'))

@app.route('/uploads/<path:filename>')
@login_required
def uploaded_file(filename):
    filename = secure_filename(filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/routes')
def list_routes():
    from urllib.parse import unquote
    lines = [f"{rule.endpoint:30s} → {unquote(str(rule))}" for rule in app.url_map.iter_rules()]
    return "<pre>" + "\n".join(sorted(lines)) + "</pre>"

# ===== Run =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info("Starting LMS app")
    logger.info("Environment: %s", "PRODUCTION" if IS_PRODUCTION else "LOCAL")
    logger.info("SocketIO mode: %s", SOCKETIO_ASYNC_MODE)

    with app.app_context():
        one_time_init()

    socketio.run(
        app,
        host="0.0.0.0" if IS_PRODUCTION else "127.0.0.1",
        port=port,
        debug=not IS_PRODUCTION,
        allow_unsafe_werkzeug=not IS_PRODUCTION
    )
