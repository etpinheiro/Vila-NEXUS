from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.user import User

class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember_me = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar no Sistema')

class ClientRegisterForm(FlaskForm):
    name = StringField('Nome Completo', validators=[DataRequired(), Length(min=3, max=120)])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    phone = StringField('Telefone / WhatsApp', validators=[DataRequired(), Length(min=8, max=30)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6, message='A senha deve ter pelo menos 6 caracteres.')])
    confirm_password = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('password', message='As senhas devem coincidir.')])
    submit = SubmitField('Criar Minha Conta de Cliente')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower().strip()).first():
            raise ValidationError('Este e-mail já está cadastrado no sistema.')

class ProfileForm(FlaskForm):
    name = StringField('Nome Completo', validators=[DataRequired(), Length(min=3, max=120)])
    phone = StringField('Telefone / WhatsApp', validators=[Length(max=30)])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    current_password = PasswordField('Senha Atual (obrigatório se alterar a senha)')
    new_password = PasswordField('Nova Senha (deixe em branco se não quiser alterar)')
    confirm_password = PasswordField('Confirmar Nova Senha', validators=[EqualTo('new_password', message='As senhas devem coincidir.')])
    submit = SubmitField('Salvar Alterações')
