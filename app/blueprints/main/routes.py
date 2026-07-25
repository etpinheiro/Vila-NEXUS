from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from sqlalchemy import or_, desc
from app import db
from app.models import Property, Company, CompanyRegistrationRequest, Favorite
from app.forms import CompanyRegistrationRequestForm
from flask_login import current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Highlights / Destaques
    highlighted_properties = Property.query.filter_by(status='disponivel', is_highlighted=True).order_by(desc(Property.created_at)).limit(6).all()
    
    # If not enough highlighted properties, get latest available
    if len(highlighted_properties) < 6:
        extra_ids = [p.id for p in highlighted_properties]
        extra_properties = Property.query.filter_by(status='disponivel').filter(~Property.id.in_(extra_ids) if extra_ids else True).order_by(desc(Property.created_at)).limit(6 - len(highlighted_properties)).all()
        highlighted_properties.extend(extra_properties)

    # Latest properties
    latest_properties = Property.query.filter_by(status='disponivel').order_by(desc(Property.created_at)).limit(6).all()
    
    # Approved Companies count & list
    featured_companies = Company.query.filter_by(is_approved=True).limit(6).all()
    
    # System Stats
    total_properties = Property.query.filter_by(status='disponivel').count()
    total_companies = Company.query.filter_by(is_approved=True).count()
    total_rentals = Property.query.filter(Property.purpose.in_(['Aluguel', 'Temporada', 'Hospedagem'])).count()

    # User favorite IDs if logged in
    user_favorite_ids = []
    if current_user.is_authenticated:
        user_favorite_ids = [f.property_id for f in Favorite.query.filter_by(user_id=current_user.id).all()]

    return render_template('main/index.html',
                           highlighted_properties=highlighted_properties,
                           latest_properties=latest_properties,
                           featured_companies=featured_companies,
                           total_properties=total_properties,
                           total_companies=total_companies,
                           total_rentals=total_rentals,
                           user_favorite_ids=user_favorite_ids)


@main_bp.route('/imoveis')
def properties():
    page = request.args.get('page', 1, type=int)
    purpose = request.args.get('purpose', '')
    property_type = request.args.get('property_type', '')
    neighborhood = request.args.get('neighborhood', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    bedrooms = request.args.get('bedrooms', type=int)
    query_str = request.args.get('q', '')
    sort_by = request.args.get('sort', 'newest')

    query = Property.query.filter_by(status='disponivel')

    if purpose:
        query = query.filter(Property.purpose == purpose)
    if property_type:
        query = query.filter(Property.property_type == property_type)
    if neighborhood:
        query = query.filter(Property.neighborhood == neighborhood)
    if min_price is not None:
        query = query.filter(Property.price >= min_price)
    if max_price is not None:
        query = query.filter(Property.price <= max_price)
    if bedrooms is not None and bedrooms > 0:
        query = query.filter(Property.bedrooms >= bedrooms)
    if query_str:
        search_pattern = f"%{query_str}%"
        query = query.filter(or_(
            Property.title.ilike(search_pattern),
            Property.description.ilike(search_pattern),
            Property.address.ilike(search_pattern),
            Property.features.ilike(search_pattern)
        ))

    # Sorting
    if sort_by == 'price_asc':
        query = query.order_by(Property.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Property.price.desc())
    else:
        query = query.order_by(desc(Property.created_at))

    pagination = query.paginate(page=page, per_page=current_app.config['PROPERTIES_PER_PAGE'], error_out=False)
    properties_list = pagination.items

    user_favorite_ids = []
    if current_user.is_authenticated:
        user_favorite_ids = [f.property_id for f in Favorite.query.filter_by(user_id=current_user.id).all()]

    active_filters_count = sum(1 for v in [purpose, property_type, neighborhood, min_price, max_price, bedrooms, query_str] if v)
    has_active_filters = active_filters_count > 0

    return render_template('main/properties.html',
                           properties=properties_list,
                           pagination=pagination,
                           purpose=purpose,
                           property_type=property_type,
                           neighborhood=neighborhood,
                           min_price=min_price,
                           max_price=max_price,
                           bedrooms=bedrooms,
                           q=query_str,
                           sort=sort_by,
                           user_favorite_ids=user_favorite_ids,
                           has_active_filters=has_active_filters,
                           active_filters_count=active_filters_count)


@main_bp.route('/imovel/<int:id>')
def property_detail(id):
    prop = Property.query.get_or_404(id)
    
    # Increment view counter
    prop.views_count += 1
    db.session.commit()

    # Related properties in same neighborhood or purpose
    related_properties = Property.query.filter(
        Property.id != prop.id,
        Property.status == 'disponivel',
        or_(Property.neighborhood == prop.neighborhood, Property.purpose == prop.purpose)
    ).limit(3).all()

    is_favorite = False
    if current_user.is_authenticated:
        is_favorite = Favorite.query.filter_by(user_id=current_user.id, property_id=prop.id).first() is not None

    return render_template('main/property_detail.html',
                           property=prop,
                           related_properties=related_properties,
                           is_favorite=is_favorite)


@main_bp.route('/solicitar-cadastro', methods=['GET', 'POST'])
def request_company_registration():
    form = CompanyRegistrationRequestForm()
    if form.validate_on_submit():
        reg_request = CompanyRegistrationRequest(
            company_name=form.company_name.data.strip(),
            contact_person=form.contact_person.data.strip(),
            cnpj_cpf=form.cnpj_cpf.data.strip(),
            business_type=form.business_type.data,
            phone=form.phone.data.strip(),
            whatsapp=form.whatsapp.data.strip() if form.whatsapp.data else form.phone.data.strip(),
            email=form.email.data.lower().strip(),
            notes=form.notes.data.strip() if form.notes.data else '',
            status='pending'
        )
        db.session.add(reg_request)
        db.session.commit()
        
        flash('Sua solicitação comercial foi enviada com sucesso! Nossa equipe de administração entrará em contato por WhatsApp ou telefone para apresentar os planos e criar sua conta empresarial.', 'success')
        return redirect(url_for('main.request_company_success'))

    return render_template('main/request_company.html', form=form)


@main_bp.route('/solicitar-cadastro/sucesso')
def request_company_success():
    return render_template('main/request_company_success.html')


@main_bp.route('/empresas')
def companies():
    companies_list = Company.query.filter_by(is_approved=True).order_by(Company.name).all()
    return render_template('main/companies.html', companies=companies_list)


@main_bp.route('/empresa/<int:id>')
def company_detail(id):
    comp = Company.query.get_or_404(id)
    comp_properties = Property.query.filter_by(company_id=comp.id, status='disponivel').order_by(desc(Property.created_at)).all()
    return render_template('main/company_detail.html', company=comp, properties=comp_properties)


@main_bp.route('/sobre')
def about():
    return render_template('main/about.html')


@main_bp.route('/contato')
def contact():
    return render_template('main/contact.html')
