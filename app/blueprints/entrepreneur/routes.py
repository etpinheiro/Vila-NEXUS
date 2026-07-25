import os
import uuid
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from sqlalchemy import desc, func
from app import db
from app.models import Property, PropertyImage, Company, VisitRequest
from app.forms import PropertyForm

entrepreneur_bp = Blueprint('entrepreneur', __name__)

def check_entrepreneur_access():
    if not current_user.is_authenticated:
        abort(401)
    if not (current_user.is_entrepreneur() or current_user.is_admin()):
        flash('Acesso restrito ao Painel do Empresário.', 'danger')
        abort(403)

@entrepreneur_bp.before_request
def before_request_hook():
    check_entrepreneur_access()


def save_image_file(file):
    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'jpg'
    unique_filename = f"prop_{uuid.uuid4().hex[:12]}_{int(os.times().elapsed)}.{ext}"
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(upload_path)
    return unique_filename


@entrepreneur_bp.route('/dashboard')
def dashboard():
    company = current_user.company
    if not company and not current_user.is_admin():
        flash('Nenhuma empresa associada ao seu usuário empresário. Entre em contato com o suporte.', 'warning')
        return render_template('entrepreneur/dashboard.html', total_properties=0, total_views=0, available_count=0, visit_requests=[])

    company_id = company.id if company else None
    
    if current_user.is_admin() and not company_id:
        properties_query = Property.query
    else:
        properties_query = Property.query.filter_by(company_id=company_id)

    total_properties = properties_query.count()
    available_count = properties_query.filter_by(status='disponivel').count()
    sold_count = properties_query.filter_by(status='vendido').count()
    rented_count = properties_query.filter_by(status='alugado').count()

    total_views = db.session.query(func.sum(Property.views_count)).filter(
        Property.company_id == company_id if company_id else True
    ).scalar() or 0

    recent_properties = properties_query.order_by(desc(Property.created_at)).limit(5).all()

    # Recent Visit Requests
    property_ids = [p.id for p in properties_query.all()]
    recent_visits = VisitRequest.query.filter(VisitRequest.property_id.in_(property_ids)).order_by(desc(VisitRequest.created_at)).limit(5).all() if property_ids else []

    return render_template('entrepreneur/dashboard.html',
                           company=company,
                           total_properties=total_properties,
                           available_count=available_count,
                           sold_count=sold_count,
                           rented_count=rented_count,
                           total_views=total_views,
                           recent_properties=recent_properties,
                           recent_visits=recent_visits)


@entrepreneur_bp.route('/imoveis')
def properties_list():
    company = current_user.company
    company_id = company.id if company else None

    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')

    if current_user.is_admin() and not company_id:
        query = Property.query
    else:
        query = Property.query.filter_by(company_id=company_id)

    if status_filter:
        query = query.filter_by(status=status_filter)

    pagination = query.order_by(desc(Property.created_at)).paginate(page=page, per_page=10, error_out=False)

    return render_template('entrepreneur/properties_list.html',
                           properties=pagination.items,
                           pagination=pagination,
                           status_filter=status_filter)


@entrepreneur_bp.route('/imovel/novo', methods=['GET', 'POST'])
def property_create():
    company = current_user.company
    if not company and not current_user.is_admin():
        flash('É necessário ter uma empresa associada para publicar imóveis.', 'danger')
        return redirect(url_for('entrepreneur.dashboard'))

    form = PropertyForm()
    # Pre-fill phone and email from company
    if request.method == 'GET':
        if company:
            form.phone.data = company.phone or company.whatsapp
            form.email.data = company.email

    if form.validate_on_submit():
        new_prop = Property(
            title=form.title.data.strip(),
            purpose=form.purpose.data,
            property_type=form.property_type.data,
            price=form.price.data,
            neighborhood=form.neighborhood.data,
            address=form.address.data.strip(),
            description=form.description.data.strip(),
            bedrooms=form.bedrooms.data or 0,
            bathrooms=form.bathrooms.data or 0,
            suites=form.suites.data or 0,
            parking_spaces=form.parking_spaces.data or 0,
            area_sqm=form.area_sqm.data or 0.0,
            features=form.features.data.strip() if form.features.data else '',
            company_id=company.id if company else Company.query.first().id,
            phone=form.phone.data.strip(),
            email=form.email.data.lower().strip(),
            status=form.status.data,
            is_highlighted=form.is_highlighted.data
        )
        db.session.add(new_prop)
        db.session.commit()

        # Handle multiple uploaded files
        uploaded_files = request.files.getlist('images')
        is_first = True
        saved_count = 0
        for file in uploaded_files:
            if file and file.filename != '':
                fn = save_image_file(file)
                img = PropertyImage(
                    property_id=new_prop.id,
                    filename=fn,
                    is_primary=is_first,
                    order=saved_count
                )
                db.session.add(img)
                is_first = False
                saved_count += 1
        
        db.session.commit()

        flash(f'Imóvel "{new_prop.title}" publicado com sucesso com {saved_count} imagens!', 'success')
        return redirect(url_for('entrepreneur.properties_list'))

    return render_template('entrepreneur/property_form.html', form=form, title="Publicar Novo Imóvel")


@entrepreneur_bp.route('/imovel/<int:id>/editar', methods=['GET', 'POST'])
def property_edit(id):
    prop = Property.query.get_or_404(id)

    # Permission check
    if not current_user.is_admin() and prop.company_id != current_user.company_id:
        flash('Você não tem permissão para editar este imóvel.', 'danger')
        return redirect(url_for('entrepreneur.properties_list'))

    form = PropertyForm(obj=prop)
    if form.validate_on_submit():
        prop.title = form.title.data.strip()
        prop.purpose = form.purpose.data
        prop.property_type = form.property_type.data
        prop.price = form.price.data
        prop.neighborhood = form.neighborhood.data
        prop.address = form.address.data.strip()
        prop.description = form.description.data.strip()
        prop.bedrooms = form.bedrooms.data or 0
        prop.bathrooms = form.bathrooms.data or 0
        prop.suites = form.suites.data or 0
        prop.parking_spaces = form.parking_spaces.data or 0
        prop.area_sqm = form.area_sqm.data or 0.0
        prop.features = form.features.data.strip() if form.features.data else ''
        prop.phone = form.phone.data.strip()
        prop.email = form.email.data.lower().strip()
        prop.status = form.status.data
        prop.is_highlighted = form.is_highlighted.data

        # Handle additional images
        uploaded_files = request.files.getlist('images')
        has_primary = any(img.is_primary for img in prop.images)
        saved_count = len(prop.images)

        for file in uploaded_files:
            if file and file.filename != '':
                fn = save_image_file(file)
                img = PropertyImage(
                    property_id=prop.id,
                    filename=fn,
                    is_primary=(not has_primary and saved_count == 0),
                    order=saved_count
                )
                db.session.add(img)
                saved_count += 1

        db.session.commit()
        flash(f'Anúncio do imóvel "{prop.title}" atualizado com sucesso!', 'success')
        return redirect(url_for('entrepreneur.properties_list'))

    return render_template('entrepreneur/property_form.html', form=form, property=prop, title=f"Editar: {prop.title}")


@entrepreneur_bp.route('/imovel/<int:id>/excluir', methods=['POST'])
def property_delete(id):
    prop = Property.query.get_or_404(id)

    if not current_user.is_admin() and prop.company_id != current_user.company_id:
        flash('Você não tem permissão para excluir este imóvel.', 'danger')
        return redirect(url_for('entrepreneur.properties_list'))

    title = prop.title
    db.session.delete(prop)
    db.session.commit()
    flash(f'Imóvel "{title}" excluído com sucesso.', 'info')
    return redirect(url_for('entrepreneur.properties_list'))


@entrepreneur_bp.route('/visitas')
def visit_requests():
    company = current_user.company
    company_id = company.id if company else None

    if current_user.is_admin() and not company_id:
        property_ids = [p.id for p in Property.query.all()]
    else:
        property_ids = [p.id for p in Property.query.filter_by(company_id=company_id).all()]

    visits = VisitRequest.query.filter(VisitRequest.property_id.in_(property_ids)).order_by(desc(VisitRequest.created_at)).all() if property_ids else []

    return render_template('entrepreneur/visit_requests.html', visits=visits)


@entrepreneur_bp.route('/visita/<int:id>/status', methods=['POST'])
def update_visit_status(id):
    visit = VisitRequest.query.get_or_404(id)
    new_status = request.form.get('status')
    if new_status in ['pending', 'scheduled', 'completed', 'cancelled']:
        visit.status = new_status
        db.session.commit()
        flash('Status da visita atualizado com sucesso!', 'success')
    return redirect(url_for('entrepreneur.visit_requests'))
