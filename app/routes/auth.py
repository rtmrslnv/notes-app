from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from models import User

auth_bp = Blueprint('auth', __name__, url_prefix='')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''
        u = User.query.filter_by(username=username).first()
        if not u or not u.check_password(password):
            flash('Неправильное имя или пароль', 'error')
            return render_template('login.html')
        session['user_id'] = u.id
        next_url = request.args.get('next') or url_for('notes.list_notes')
        return redirect(next_url)
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('auth.login'))
