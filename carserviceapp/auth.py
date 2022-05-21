from unicodedata import category
from flask import Blueprint, flash, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, login_user, logout_user, current_user
from carserviceapp import db
from carserviceapp.models import User



auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Успешный вход!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Неправильный пароль', category='danger')
        else:
            flash('Пользователя не существует', category='danger')
        
    return render_template('login.html', user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта', category='danger')
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        usertype = request.form.get('usertype')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(username=username).first()
        
        if user:
            flash(f'Пользователь уже сущетвует', category='danger')
        elif len(username) < 2:
            flash('Слишком короткое имя пользователя', category='danger')
        elif password1 != password2:
            flash('Пароли не совпадают', category='danger')
        else:
            new_user = User(username=username, usertype=usertype, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash(f'Пользователь {username} создан!', category='success')
            return redirect(url_for('views.home'))
    return render_template('sign-up.html', user=current_user)

