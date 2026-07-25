from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class CompanyRegistrationRequestForm(FlaskForm):
    company_name = StringField('Nome da Empresa / Empreendimento', validators=[DataRequired(), Length(min=3, max=150)])
    contact_person = StringField('Nome do Responsável Comercial', validators=[DataRequired(), Length(min=3, max=120)])
    cnpj_cpf = StringField('CNPJ ou CPF do Responsável', validators=[DataRequired(), Length(min=11, max=30)])
    business_type = SelectField('Tipo de Empresa / Atuação', choices=[
        ('Imobiliária', 'Imobiliária'),
        ('Hotel', 'Hotel'),
        ('Pousada', 'Pousada'),
        ('Proprietário Particular', 'Proprietário Particular (Múltiplos Imóveis)'),
        ('Construtora / Incorporadora', 'Construtora / Incorporadora'),
        ('Outro', 'Outro')
    ], validators=[DataRequired()])
    phone = StringField('Telefone Principal', validators=[DataRequired(), Length(min=8, max=30)])
    whatsapp = StringField('WhatsApp para Contato Direto', validators=[DataRequired(), Length(min=8, max=30)])
    email = StringField('E-mail Corporativo', validators=[DataRequired(), Email()])
    notes = TextAreaField('Informações Adicionais / Porte do Portfólio (Quantidade aproximada de imóveis)', validators=[Length(max=1000)])
    submit = SubmitField('Enviar Solicitação de Cadastro Comercial')
