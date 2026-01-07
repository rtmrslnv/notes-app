from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User

register_bp = Blueprint('register', __name__)

@register_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''
        if not username or not password:
            flash('Введите имя пользователя и пароль', 'error')
            return render_template('register.html')
        if User.query.filter_by(username=username).first():
            flash('Пользователь с таким именем уже существует', 'error')
            return render_template('register.html')
        u = User(username=username)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        session['user_id'] = u.id
        return redirect(url_for('notes.list_notes'))
    return render_template('register.html')
