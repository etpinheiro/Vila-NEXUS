import os
from flask import Blueprint, jsonify, request, current_app
from flask_login import current_user, login_required
from app import db
from app.models import Favorite, VisitRequest, PropertyImage, Property

api_bp = Blueprint('api', __name__)

@api_bp.route('/favoritar/<int:property_id>', methods=['POST'])
def toggle_favorite(property_id):
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'Faça login para favoritar imóveis.', 'require_login': True}), 401

    fav = Favorite.query.filter_by(user_id=current_user.id, property_id=property_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
        return jsonify({'success': True, 'is_favorite': False, 'message': 'Imóvel removido dos seus favoritos.'})
    else:
        new_fav = Favorite(user_id=current_user.id, property_id=property_id)
        db.session.add(new_fav)
        db.session.commit()
        return jsonify({'success': True, 'is_favorite': True, 'message': 'Imóvel salvo nos seus favoritos!'})


@api_bp.route('/solicitar-visita', methods=['POST'])
def submit_visit_request():
    data = request.get_json() or request.form
    
    property_id = data.get('property_id')
    client_name = data.get('client_name')
    client_email = data.get('client_email')
    client_phone = data.get('client_phone')
    preferred_date = data.get('preferred_date')
    notes = data.get('notes', '')

    if not (property_id and client_name and client_email and client_phone and preferred_date):
        return jsonify({'success': False, 'message': 'Por favor, preencha todos os campos obrigatórios.'}), 400

    prop = Property.query.get(property_id)
    if not prop:
        return jsonify({'success': False, 'message': 'Imóvel não encontrado.'}), 404

    visit = VisitRequest(
        user_id=current_user.id if current_user.is_authenticated else None,
        property_id=property_id,
        client_name=client_name.strip(),
        client_email=client_email.lower().strip(),
        client_phone=client_phone.strip(),
        preferred_date=preferred_date.strip(),
        notes=notes.strip(),
        status='pending'
    )
    db.session.add(visit)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Solicitação de visita enviada com sucesso! O anunciante entrará em contato em breve.'})


@api_bp.route('/imagem/<int:image_id>/excluir', methods=['POST'])
@login_required
def delete_image(image_id):
    img = PropertyImage.query.get_or_404(image_id)
    prop = Property.query.get(img.property_id)

    if not current_user.is_admin() and prop.company_id != current_user.company_id:
        return jsonify({'success': False, 'message': 'Sem permissão.'}), 403

    # Remove physical file if exists
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], img.filename)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception:
            pass

    was_primary = img.is_primary
    prop_id = img.property_id
    db.session.delete(img)
    db.session.commit()

    # If deleted image was primary, set another image as primary
    if was_primary:
        next_img = PropertyImage.query.filter_by(property_id=prop_id).first()
        if next_img:
            next_img.is_primary = True
            db.session.commit()

    return jsonify({'success': True, 'message': 'Imagem excluída com sucesso.'})


@api_bp.route('/imagem/<int:image_id>/definir-capa', methods=['POST'])
@login_required
def set_primary_image(image_id):
    img = PropertyImage.query.get_or_404(image_id)
    prop = Property.query.get(img.property_id)

    if not current_user.is_admin() and prop.company_id != current_user.company_id:
        return jsonify({'success': False, 'message': 'Sem permissão.'}), 403

    # Reset all images for this property
    PropertyImage.query.filter_by(property_id=prop.id).update({'is_primary': False})
    img.is_primary = True
    db.session.commit()

    return jsonify({'success': True, 'message': 'Capa do imóvel definida com sucesso.'})
