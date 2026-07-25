from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SelectField, DecimalField, IntegerField, FloatField, TextAreaField, BooleanField, MultipleFileField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Email, Optional

class PropertyForm(FlaskForm):
    title = StringField('Título do Anúncio', validators=[DataRequired(), Length(min=5, max=200)])
    purpose = SelectField('Finalidade', choices=[
        ('Venda', 'Venda'),
        ('Aluguel', 'Aluguel Mensal'),
        ('Temporada', 'Temporada / Diária'),
        ('Hospedagem', 'Hospedagem (Hotel/Pousada)')
    ], validators=[DataRequired()])
    property_type = SelectField('Tipo de Imóvel', choices=[
        ('Casa', 'Casa Residencial'),
        ('Apartamento', 'Apartamento'),
        ('Terreno', 'Terreno / Lote'),
        ('Pousada/Quarto', 'Pousada / Quarto'),
        ('Hotel/Suíte', 'Hotel / Suíte'),
        ('Galpão/Comercial', 'Galpão / Ponto Comercial'),
        ('Sítio/Chácara', 'Sítio / Chácara')
    ], validators=[DataRequired()])
    price = DecimalField('Preço (R$)', validators=[DataRequired(), NumberRange(min=0)])
    neighborhood = SelectField('Bairro / Localidade', choices=[
        ('Vila dos Cabanos', 'Vila dos Cabanos'),
        ('Novo Paraíso', 'Novo Paraíso'),
        ('Praia do Caripi', 'Praia do Caripi'),
        ('Centro Barcarena', 'Centro Barcarena'),
        ('Vila do Conde', 'Vila do Conde'),
        ('Distrito Industrial', 'Distrito Industrial'),
        ('São Francisco', 'São Francisco'),
        ('Laranjal', 'Laranjal')
    ], validators=[DataRequired()])
    address = StringField('Endereço Completo', validators=[DataRequired(), Length(min=5, max=255)])
    description = TextAreaField('Descrição Detalhada do Imóvel', validators=[DataRequired(), Length(min=20, max=5000)])
    
    bedrooms = IntegerField('Quartos', default=0, validators=[NumberRange(min=0)])
    bathrooms = IntegerField('Banheiros', default=0, validators=[NumberRange(min=0)])
    suites = IntegerField('Suítes', default=0, validators=[NumberRange(min=0)])
    parking_spaces = IntegerField('Vagas de Garagem', default=0, validators=[NumberRange(min=0)])
    area_sqm = FloatField('Área Útil (m²)', default=0.0, validators=[NumberRange(min=0)])
    
    features = StringField('Características / Comodidades (separadas por vírgula)', validators=[Length(max=500)],
                           render_kw={"placeholder": "Ex: Piscina, Ar Condicionado, Churrasqueira, Mobiliado, Garagem Coberta, Segurança 24h"})
    
    phone = StringField('Telefone de Contato', validators=[DataRequired(), Length(min=8, max=30)])
    email = StringField('E-mail de Contato', validators=[DataRequired(), Email()])
    
    status = SelectField('Status da Disponibilidade', choices=[
        ('disponivel', 'Disponível'),
        ('vendido', 'Vendido'),
        ('alugado', 'Alugado'),
        ('reservado', 'Reservado / Indisponível')
    ], validators=[DataRequired()])
    
    is_highlighted = BooleanField('Destacar Anúncio na Página Inicial')
    
    images = MultipleFileField('Upload de Imagens (Selecione uma ou várias imagens PNG, JPG, WEBP)',
                               validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Apenas imagens JPG, PNG ou WEBP!')])
    
    submit = SubmitField('Salvar Imóvel')
