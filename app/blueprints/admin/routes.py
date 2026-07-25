from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy import desc, func
from app import db
from app.models import User, Company, CompanyRegistrationRequest, Property, VisitRequest
from app.forms import ApproveCompanyCreateUserForm, UserManagementForm, CompanyEditForm, PropertyForm

admin_bp = Blueprint('admin', __name__)

def check_admin_access():
    if not current_user.is_authenticated:
        abort(401)
    if not current_user.is_admin():
        flash('Acesso restrito ao Painel Administrativo.', 'danger')
        abort(403)

@admin_bp.before_request
def before_request_hook():
    check_admin_access()


@admin_bp.route('/dashboard')
def dashboard():
    pending_requests_count = CompanyRegistrationRequest.query.filter_by(status='pending').count()
    total_users = User.query.count()
    total_companies = Company.query.count()
    total_properties = Property.query.count()
    highlighted_count = Property.query.filter_by(is_highlighted=True).count()

    recent_requests = CompanyRegistrationRequest.query.order_by(desc(CompanyRegistrationRequest.created_at)).limit(5).all()
    recent_users = User.query.order_by(desc(User.created_at)).limit(5).all()
    recent_properties = Property.query.order_by(desc(Property.created_at)).limit(5).all()

    return render_template('admin/dashboard.html',
                           pending_requests_count=pending_requests_count,
                           total_users=total_users,
                           total_companies=total_companies,
                           total_properties=total_properties,
                           highlighted_count=highlighted_count,
                           recent_requests=recent_requests,
                           recent_users=recent_users,
                           recent_properties=recent_properties)


# =========================================================================
# 1. SOLICITAÇÕES DE CADASTRO DE EMPRESÁRIOS (FLUXO COMERCIAL OBRIGATÓRIO)
# =========================================================================

@admin_bp.route('/solicitacoes')
def company_requests():
    status_filter = request.args.get('status', 'pending')
    
    if status_filter == 'all':
        requests_list = CompanyRegistrationRequest.query.order_by(desc(CompanyRegistrationRequest.created_at)).all()
    else:
        requests_list = CompanyRegistrationRequest.query.filter_by(status=status_filter).order_by(desc(CompanyRegistrationRequest.created_at)).all()

    pending_count = CompanyRegistrationRequest.query.filter_by(status='pending').count()

    return render_template('admin/company_requests.html',
                           requests=requests_list,
                           status_filter=status_filter,
                           pending_count=pending_count)


@admin_bp.route('/solicitacoes/<int:id>/aprovar', methods=['GET', 'POST'])
def approve_request(id):
    req = CompanyRegistrationRequest.query.get_or_404(id)
    
    form = ApproveCompanyCreateUserForm()
    
    # Pre-populate form with request lead details on GET
    if request.method == 'GET':
        form.company_name.data = req.company_name
        form.cnpj_cpf.data = req.cnpj_cpf
        form.business_type.data = req.business_type
        form.company_phone.data = req.phone
        form.company_whatsapp.data = req.whatsapp or req.phone
        form.company_email.data = req.email
        form.user_name.data = req.contact_person
        form.user_email.data = req.email
        form.user_phone.data = req.phone

    if form.validate_on_submit():
        # 1. Create Company
        new_company = Company(
            name=form.company_name.data.strip(),
            cnpj_cpf=form.cnpj_cpf.data.strip(),
            business_type=form.business_type.data,
            phone=form.company_phone.data.strip(),
            whatsapp=form.company_whatsapp.data.strip(),
            email=form.company_email.data.lower().strip(),
            neighborhood=form.company_neighborhood.data,
            address=form.company_address.data.strip() if form.company_address.data else '',
            is_approved=True
        )
        db.session.add(new_company)
        db.session.flush()  # get company.id

        # 2. Create Entrepreneur User
        new_user = User(
            name=form.user_name.data.strip(),
            email=form.user_email.data.lower().strip(),
            phone=form.user_phone.data.strip() if form.user_phone.data else '',
            role='entrepreneur',
            status='active',
            company_id=new_company.id
        )
        new_user.set_password(form.user_password.data)
        db.session.add(new_user)

        # 3. Update Request Status
        req.status = 'approved'

        db.session.commit()

        flash(f'Solicitação aprovada! Empresa "{new_company.name}" e Usuário Empresário "{new_user.email}" criados com sucesso!', 'success')
        return redirect(url_for('admin.company_requests'))

    return render_template('admin/approve_request.html', form=form, req=req)


@admin_bp.route('/solicitacoes/<int:id>/status', methods=['POST'])
def update_request_status(id):
    req = CompanyRegistrationRequest.query.get_or_404(id)
    new_status = request.form.get('status')
    if new_status in ['pending', 'contacted', 'rejected']:
        req.status = new_status
        db.session.commit()
        flash('Status da solicitação comercial atualizado.', 'info')
    return redirect(url_for('admin.company_requests'))


# =========================================================================
# 2. GERENCIAMENTO DE USUÁRIOS
# =========================================================================

@admin_bp.route('/usuarios')
def users_list():
    role_filter = request.args.get('role', '')
    status_filter = request.args.get('status', '')
    search_q = request.args.get('q', '')

    query = User.query

    if role_filter:
        query = query.filter_by(role=role_filter)
    if status_filter:
        query = query.filter_by(status=status_filter)
    if search_q:
        pattern = f"%{search_q}%"
        query = query.filter(User.name.ilike(pattern) | User.email.ilike(pattern))

    users = query.order_by(desc(User.created_at)).all()
    return render_template('admin/users_list.html', users=users, role_filter=role_filter, status_filter=status_filter, q=search_q)


@admin_bp.route('/usuarios/novo', methods=['GET', 'POST'])
def user_create():
    form = UserManagementForm()
    # Populate company choices
    companies = Company.query.order_by(Company.name).all()
    form.company_id.choices = [(0, 'Nenhuma (Sem vínculo empresarial)')] + [(c.id, c.name) for c in companies]

    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data.lower().strip()).first():
            flash('Este e-mail já está em uso por outro usuário.', 'danger')
            return render_template('admin/user_form.html', form=form, title="Criar Novo Usuário")

        password_to_set = form.new_password.data.strip() if form.new_password.data else '123456'
        new_user = User(
            name=form.name.data.strip(),
            email=form.email.data.lower().strip(),
            phone=form.phone.data.strip() if form.phone.data else '',
            role=form.role.data,
            status=form.status.data,
            company_id=form.company_id.data if form.company_id.data > 0 else None
        )
        new_user.set_password(password_to_set)
        db.session.add(new_user)
        db.session.commit()

        flash(f'Usuário "{new_user.name}" ({new_user.email}) criado com sucesso!', 'success')
        return redirect(url_for('admin.users_list'))

    return render_template('admin/user_form.html', form=form, title="Criar Novo Usuário")


@admin_bp.route('/usuarios/<int:id>/editar', methods=['GET', 'POST'])
def user_edit(id):
    user = User.query.get_or_404(id)
    form = UserManagementForm(obj=user)
    
    companies = Company.query.order_by(Company.name).all()
    form.company_id.choices = [(0, 'Nenhuma (Sem vínculo empresarial)')] + [(c.id, c.name) for c in companies]

    if request.method == 'GET':
        form.company_id.data = user.company_id or 0

    if form.validate_on_submit():
        user.name = form.name.data.strip()
        user.email = form.email.data.lower().strip()
        user.phone = form.phone.data.strip() if form.phone.data else ''
        user.role = form.role.data
        user.status = form.status.data
        user.company_id = form.company_id.data if form.company_id.data > 0 else None

        if form.new_password.data:
            user.set_password(form.new_password.data.strip())
            flash('Senha do usuário atualizada!', 'info')

        db.session.commit()
        flash(f'Dados do usuário "{user.name}" atualizados com sucesso!', 'success')
        return redirect(url_for('admin.users_list'))

    return render_template('admin/user_form.html', form=form, user=user, title=f"Editar Usuário: {user.name}")


@admin_bp.route('/usuarios/<int:id>/toggle-status', methods=['POST'])
def toggle_user_status(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('Você não pode alterar o status da sua própria conta de Administrador.', 'warning')
        return redirect(url_for('admin.users_list'))

    user.status = 'blocked' if user.status == 'active' else 'active'
    db.session.commit()
    flash(f'Status do usuário "{user.name}" alterado para {user.status.upper()}.', 'success')
    return redirect(url_for('admin.users_list'))


# =========================================================================
# 3. GERENCIAMENTO DE EMPRESAS
# =========================================================================

@admin_bp.route('/empresas')
def companies_list():
    companies = Company.query.order_by(desc(Company.created_at)).all()
    return render_template('admin/companies_list.html', companies=companies)


@admin_bp.route('/empresa/<int:id>/editar', methods=['GET', 'POST'])
def company_edit(id):
    comp = Company.query.get_or_404(id)
    form = CompanyEditForm(obj=comp)
    if form.validate_on_submit():
        comp.name = form.name.data.strip()
        comp.cnpj_cpf = form.cnpj_cpf.data.strip() if form.cnpj_cpf.data else ''
        comp.business_type = form.business_type.data
        comp.phone = form.phone.data.strip()
        comp.whatsapp = form.whatsapp.data.strip() if form.whatsapp.data else ''
        comp.email = form.email.data.lower().strip()
        comp.neighborhood = form.neighborhood.data
        comp.address = form.address.data.strip() if form.address.data else ''
        comp.description = form.description.data.strip() if form.description.data else ''
        db.session.commit()
        flash(f'Empresa "{comp.name}" atualizada com sucesso!', 'success')
        return redirect(url_for('admin.companies_list'))

    return render_template('admin/company_form.html', form=form, company=comp)


# =========================================================================
# 4. GERENCIAMENTO DE IMÓVEIS & DESTAQUES
# =========================================================================

@admin_bp.route('/imoveis')
def properties_list():
    page = request.args.get('page', 1, type=int)
    highlight_filter = request.args.get('highlight', '')
    status_filter = request.args.get('status', '')

    query = Property.query

    if highlight_filter == 'true':
        query = query.filter_by(is_highlighted=True)
    if status_filter:
        query = query.filter_by(status=status_filter)

    pagination = query.order_by(desc(Property.created_at)).paginate(page=page, per_page=12, error_out=False)

    return render_template('admin/properties_list.html',
                           properties=pagination.items,
                           pagination=pagination,
                           highlight_filter=highlight_filter,
                           status_filter=status_filter)


@admin_bp.route('/imovel/<int:id>/toggle-destaque', methods=['POST'])
def toggle_property_highlight(id):
    prop = Property.query.get_or_404(id)
    prop.is_highlighted = not prop.is_highlighted
    db.session.commit()
    state = "destacado" if prop.is_highlighted else "removido dos destaques"
    flash(f'Imóvel "{prop.title}" foi {state}.', 'success')
    return redirect(url_for('admin.properties_list'))


# =========================================================================
# 5. ESTATÍSTICAS E RELATÓRIOS
# =========================================================================

@admin_bp.route('/relatorios')
def reports():
    # Properties per neighborhood
    neighborhood_stats = db.session.query(Property.neighborhood, func.count(Property.id)).group_by(Property.neighborhood).all()

    # Properties per purpose
    purpose_stats = db.session.query(Property.purpose, func.count(Property.id)).group_by(Property.purpose).all()

    # Properties per company
    company_stats = db.session.query(Company.name, func.count(Property.id)).join(Property, Property.company_id == Company.id).group_by(Company.name).all()

    # Total views per property top 10
    top_viewed = Property.query.order_by(desc(Property.views_count)).limit(10).all()

    return render_template('admin/reports.html',
                           neighborhood_stats=neighborhood_stats,
                           purpose_stats=purpose_stats,
                           company_stats=company_stats,
                           top_viewed=top_viewed)
