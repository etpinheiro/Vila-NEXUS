from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Favorite, VisitRequest
from app.forms import LoginForm, ClientRegisterForm, ProfileForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        elif current_user.is_entrepreneur():
            return redirect(url_for('entrepreneur.dashboard'))
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user and user.check_password(form.password.data):
            if not user.is_active_user():
                flash('Esta conta está bloqueada pelo administrador. Entre em contato com o suporte.', 'danger')
                return render_template('auth/login.html', form=form)

            login_user(user, remember=form.remember_me.data)
            flash(f'Bem-vindo(a) de volta, {user.name}!', 'success')
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
                
            if user.is_admin():
                return redirect(url_for('admin.dashboard'))
            elif user.is_entrepreneur():
                return redirect(url_for('entrepreneur.dashboard'))
            return redirect(url_for('main.index'))
        else:
            flash('E-mail ou senha incorretos. Verifique suas credenciais.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/registrar-cliente', methods=['GET', 'POST'])
def register_client():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = ClientRegisterForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data.strip(),
            email=form.email.data.lower().strip(),
            phone=form.phone.data.strip(),
            role='client',
            status='active'
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash('Sua conta de cliente foi criada com sucesso! Agora você pode favoritar imóveis e solicitar visitas.', 'success')
        return redirect(url_for('main.index'))

    return render_template('auth/register_client.html', form=form)


@auth_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.name = form.name.data.strip()
        current_user.phone = form.phone.data.strip()
        
        # Check email change conflict
        new_email = form.email.data.lower().strip()
        if new_email != current_user.email:
            existing = User.query.filter_by(email=new_email).first()
            if existing:
                flash('Este e-mail já está em uso por outra conta.', 'danger')
                return render_template('auth/profile.html', form=form)
            current_user.email = new_email

        # Check password change
        if form.new_password.data:
            if not current_user.check_password(form.current_password.data):
                flash('A senha atual fornecida está incorreta.', 'danger')
                return render_template('auth/profile.html', form=form)
            current_user.set_password(form.new_password.data)
            flash('Senha atualizada com sucesso!', 'success')

        db.session.commit()
        flash('Seus dados de perfil foram salvos com sucesso.', 'success')
        return redirect(url_for('auth.profile'))

    # Load client favorites and visit requests if client
    user_favorites = []
    user_visits = []
    if current_user.is_client():
        user_favorites = Favorite.query.filter_by(user_id=current_user.id).all()
        user_visits = VisitRequest.query.filter_by(user_id=current_user.id).order_by(VisitRequest.created_at.desc()).all()

    return render_template('auth/profile.html', form=form, favorites=user_favorites, visits=user_visits)
