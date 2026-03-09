from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from models import db, Usuario
from flask_login import login_user, logout_user, login_required, current_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Verificar si el usuario ya existe
    if Usuario.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Usuario ya existe'}), 400

    if Usuario.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email ya registrado'}), 400

    # Forzar rol 'user' — el rol 'admin' no se puede asignar por esta ruta
    role = 'user'

    # Crear nuevo usuario
    nuevo_usuario = Usuario(
        username=data['username'],
        email=data['email'],
        password=generate_password_hash(data['password']),
        role=role
    )
    
    db.session.add(nuevo_usuario)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Usuario registrado exitosamente',
        'user_id': nuevo_usuario.id
    })

@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'role': current_user.role
    })