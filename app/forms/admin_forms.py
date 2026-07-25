from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, ValidationError
from app.models.user import User

class ApproveCompanyCreateUserForm(FlaskForm):
    # Dados da Empresa
    company_name = StringField('Nome da Empresa / Razão Social', validators=[DataRequired(), Length(min=3, max=150)])
    cnpj_cpf = StringField('CNPJ ou CPF', validators=[DataRequired(), Length(min=11, max=30)])
    business_type = SelectField('Tipo de Negócio', choices=[
        ('Imobiliária', 'Imobiliária'),
        ('Hotel', 'Hotel'),
        ('Pousada', 'Pousada'),
        ('Proprietário Particular', 'Proprietário Particular'),
        ('Construtora / Incorporadora', 'Construtora / Incorporadora'),
        ('Outro', 'Outro')
    ], validators=[DataRequired()])
    company_phone = StringField('Telefone da Empresa', validators=[DataRequired(), Length(min=8, max=30)])
    company_whatsapp = StringField('WhatsApp da Empresa', validators=[DataRequired(), Length(min=8, max=30)])
    company_email = StringField('E-mail Comercial da Empresa', validators=[DataRequired(), Email()])
    company_neighborhood = SelectField('Bairro', choices=[
        ('Vila dos Cabanos', 'Vila dos Cabanos'),
        ('Novo Paraíso', 'Novo Paraíso'),
        ('Praia do Caripi', 'Praia do Caripi'),
        ('Centro Barcarena', 'Centro Barcarena'),
        ('Vila do Conde', 'Vila do Conde'),
        ('Distrito Industrial', 'Distrito Industrial'),
        ('São Francisco', 'São Francisco')
    ], validators=[DataRequired()])
    company_address = StringField('Endereço Completo', validators=[Length(max=255)])
    
    # Dados do Usuário Empresário
    user_name = StringField('Nome do Usuário Empresário', validators=[DataRequired(), Length(min=3, max=120)])
    user_email = StringField('E-mail de Login do Empresário', validators=[DataRequired(), Email()])
    user_phone = StringField('Telefone do Usuário', validators=[Length(max=30)])
    user_password = PasswordField('Senha Inicial de Acesso', validators=[DataRequired(), Length(min=6)])
    
    submit = SubmitField('Confirmar Aprovação Comercial e Criar Usuário')

    def validate_user_email(self, field):
        if User.query.filter_by(email=field.data.lower().strip()).first():
            raise ValidationError('Este e-mail já pertence a um usuário existente no sistema.')


class UserManagementForm(FlaskForm):
    name = StringField('Nome Completo', validators=[DataRequired(), Length(min=3, max=120)])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    phone = StringField('Telefone', validators=[Length(max=30)])
    role = SelectField('Perfil de Acesso', choices=[
        ('client', 'Cliente'),
        ('entrepreneur', 'Empresário'),
        ('admin', 'Administrador System')
    ], validators=[DataRequired()])
    status = SelectField('Status da Conta', choices=[
        ('active', 'Ativo'),
        ('blocked', 'Bloqueado')
    ], validators=[DataRequired()])
    company_id = SelectField('Empresa Vinculada', coerce=int, validators=[])
    new_password = PasswordField('Definir Nova Senha (opcional)', validators=[Length(max=100)])
    submit = SubmitField('Salvar Usuário')


class CompanyEditForm(FlaskForm):
    name = StringField('Nome da Empresa / Razão Social', validators=[DataRequired(), Length(min=3, max=150)])
    cnpj_cpf = StringField('CNPJ ou CPF', validators=[Length(max=30)])
    business_type = SelectField('Tipo de Negócio', choices=[
        ('Imobiliária', 'Imobiliária'),
        ('Hotel', 'Hotel'),
        ('Pousada', 'Pousada'),
        ('Proprietário Particular', 'Proprietário Particular'),
        ('Construtora / Incorporadora', 'Construtora / Incorporadora'),
        ('Outro', 'Outro')
    ], validators=[DataRequired()])
    phone = StringField('Telefone da Empresa', validators=[DataRequired(), Length(min=8, max=30)])
    whatsapp = StringField('WhatsApp da Empresa', validators=[Length(max=30)])
    email = StringField('E-mail da Empresa', validators=[DataRequired(), Email()])
    neighborhood = SelectField('Bairro', choices=[
        ('Vila dos Cabanos', 'Vila dos Cabanos'),
        ('Novo Paraíso', 'Novo Paraíso'),
        ('Praia do Caripi', 'Praia do Caripi'),
        ('Centro Barcarena', 'Centro Barcarena'),
        ('Vila do Conde', 'Vila do Conde'),
        ('Distrito Industrial', 'Distrito Industrial'),
        ('São Francisco', 'São Francisco')
    ], validators=[DataRequired()])
    address = StringField('Endereço Completo', validators=[Length(max=255)])
    description = TextAreaField('Descrição da Empresa', validators=[Length(max=2000)])
    submit = SubmitField('Salvar Alterações da Empresa')
