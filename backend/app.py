# backend/app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, date
import json
from sqlalchemy.orm import joinedload
import random
import pandas as pd
from io import BytesIO
from collections import defaultdict
import math

# ✅ IMPORTACIONES
from config import Config

# Inicializar Flask
app = Flask(__name__, 
            template_folder='../frontend',
            static_folder='../frontend')

# Cargar configuración
app.config.from_object(Config)

# Inicializar extensiones
db = SQLAlchemy(app)
CORS(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ========== DEFINIR MODELOS COMPLETOS ==========

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    
    def is_active(self):
        return self.activo
    
    def get_id(self):
        return str(self.id)
    
    def is_authenticated(self):
        return True
    
    def is_anonymous(self):
        return False

class Profesor(db.Model):
    __tablename__ = 'profesor'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    categoria_academica = db.Column(db.String(50))
    categoria_cientifica = db.Column(db.String(50))
    email = db.Column(db.String(120))
    telefono = db.Column(db.String(20))
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación
    asignaturas = db.relationship('Asignatura', backref='profesor_rel', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nombres': self.nombres,
            'apellidos': self.apellidos,
            'categoria_academica': self.categoria_academica,
            'categoria_cientifica': self.categoria_cientifica,
            'email': self.email,
            'telefono': self.telefono,
            'activo': self.activo,
            'nombre_completo': f"{self.nombres} {self.apellidos}"
        }

class Asignatura(db.Model):
    __tablename__ = 'asignatura'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(10), unique=True, nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    año_academico = db.Column(db.Integer, nullable=False)
    periodo = db.Column(db.Integer, nullable=False)
    horas_presenciales = db.Column(db.Integer, default=0)
    horas_no_presenciales = db.Column(db.Integer, default=0)
    horas_totales = db.Column(db.Integer, default=0)
    tipo_evaluacion = db.Column(db.String(20), default='EF')
    color = db.Column(db.String(7), default='#3498db')
    profesor_id = db.Column(db.Integer, db.ForeignKey('profesor.id'))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        profesor_nombre = None
        if self.profesor_rel:
            profesor_nombre = f"{self.profesor_rel.nombres} {self.profesor_rel.apellidos}"
        
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'año_academico': self.año_academico,
            'periodo': self.periodo,
            'horas_presenciales': self.horas_presenciales,
            'horas_no_presenciales': self.horas_no_presenciales,
            'horas_totales': self.horas_totales,
            'tipo_evaluacion': self.tipo_evaluacion,
            'color': self.color,
            'profesor_id': self.profesor_id,
            'profesor_nombre': profesor_nombre
        }

class Turno(db.Model):
    __tablename__ = 'turno'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    hora_inicio = db.Column(db.String(5), nullable=False)
    hora_fin = db.Column(db.String(5), nullable=False)
    duracion_minutos = db.Column(db.Integer, default=90)
    seccion = db.Column(db.String(10), nullable=False)
    orden = db.Column(db.Integer, nullable=False)
    activo = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'hora_inicio': self.hora_inicio,
            'hora_fin': self.hora_fin,
            'duracion_minutos': self.duracion_minutos,
            'seccion': self.seccion,
            'orden': self.orden,
            'activo': self.activo
        }

# ========== MODELOS PARA HORARIOS ==========

class HorarioGeneral(db.Model):
    """Metadatos del horario (año, semestre, carrera, etc.)"""
    __tablename__ = 'horario_general'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False, default="Horario Docente")
    año_academico = db.Column(db.String(20), nullable=False)  # "2025-2026"
    semestre = db.Column(db.Integer, nullable=False)  # 1 o 2
    año_carrera = db.Column(db.Integer, nullable=False)  # 1, 2, 3, 4
    carrera = db.Column(db.String(100), default="INGENIERÍA INFORMÁTICA")
    modalidad = db.Column(db.String(50), default="Diurno")  # Diurno o Por Encuentros
    semanas_totales = db.Column(db.Integer, default=22)
    semanas_clases = db.Column(db.Integer, default=19)
    semanas_examenes = db.Column(db.Integer, default=3)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    creado_por = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, onupdate=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    
    # Relaciones
    usuario = db.relationship('Usuario', backref='horarios')
    semanas = db.relationship('HorarioSemanal', backref='horario_general', cascade='all, delete-orphan', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'año_academico': self.año_academico,
            'semestre': self.semestre,
            'año_carrera': self.año_carrera,
            'carrera': self.carrera,
            'modalidad': self.modalidad,
            'semanas_totales': self.semanas_totales,
            'semanas_clases': self.semanas_clases,
            'semanas_examenes': self.semanas_examenes,
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_fin': self.fecha_fin.isoformat() if self.fecha_fin else None,
            'creado_por': self.creado_por,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None,
            'activo': self.activo
        }

class HorarioSemanal(db.Model):
    """Cada asignación específica en el horario"""
    __tablename__ = 'horario_semanal'
    
    id = db.Column(db.Integer, primary_key=True)
    horario_general_id = db.Column(db.Integer, db.ForeignKey('horario_general.id'), nullable=False)
    semana_numero = db.Column(db.Integer, nullable=False)  # 1 a 22
    dia_semana = db.Column(db.Integer, nullable=False)  # 0=Lunes, 1=Martes, ..., 4=Viernes
    turno_id = db.Column(db.Integer, db.ForeignKey('turno.id'), nullable=False)
    asignatura_id = db.Column(db.Integer, db.ForeignKey('asignatura.id'))
    profesor_id = db.Column(db.Integer, db.ForeignKey('profesor.id'))
    es_examen = db.Column(db.Boolean, default=False)
    fecha_especifica = db.Column(db.Date)  # Fecha exacta (ej: 2025-09-01)
    color = db.Column(db.String(7), default='#3498db')  # Color de la asignatura
    
    # Relaciones
    turno = db.relationship('Turno')
    asignatura = db.relationship('Asignatura')
    profesor = db.relationship('Profesor')
    
    def to_dict(self):
        return {
            'id': self.id,
            'horario_general_id': self.horario_general_id,
            'semana_numero': self.semana_numero,
            'dia_semana': self.dia_semana,
            'turno_id': self.turno_id,
            'asignatura_id': self.asignatura_id,
            'profesor_id': self.profesor_id,
            'es_examen': self.es_examen,
            'fecha_especifica': self.fecha_especifica.isoformat() if self.fecha_especifica else None,
            'color': self.color,
            'asignatura_nombre': self.asignatura.nombre if self.asignatura else None,
            'asignatura_codigo': self.asignatura.codigo if self.asignatura else None,
            'profesor_nombre': f"{self.profesor.nombres} {self.profesor.apellidos}" if self.profesor else None,
            'turno_nombre': self.turno.nombre if self.turno else None,
            'hora_inicio': self.turno.hora_inicio if self.turno else None,
            'hora_fin': self.turno.hora_fin if self.turno else None,
            'seccion': self.turno.seccion if self.turno else None
        }

# ========== HELPER FUNCTIONS ==========

def obtener_horario_por_filtros(año_param=None, semestre_param=None):
    """Función helper para obtener horario basado en filtros"""
    try:
        if año_param and semestre_param:
            # Buscar horario específico por año y semestre
            horario = HorarioGeneral.query.filter_by(
                activo=True,
                año_carrera=año_param,
                semestre=semestre_param
            ).order_by(HorarioGeneral.creado_en.desc()).first()
            
            # Si no encuentra, buscar cualquier horario activo
            if not horario:
                horario = HorarioGeneral.query.filter_by(
                    activo=True
                ).order_by(HorarioGeneral.creado_en.desc()).first()
        else:
            # Si no se especifica, devolver el último activo
            horario = HorarioGeneral.query.filter_by(
                activo=True
            ).order_by(HorarioGeneral.creado_en.desc()).first()
        
        return horario
    except Exception as e:
        print(f"Error en obtener_horario_por_filtros: {str(e)}")
        return None

# ========== LOGIN MANAGER ==========

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# ========== RUTAS PRINCIPALES ==========

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username', '')
        password = data.get('password', '')
        
        usuario = Usuario.query.filter_by(username=username).first()
        
        if usuario and check_password_hash(usuario.password, password):
            login_user(usuario)
            return jsonify({
                'success': True,
                'message': 'Login exitoso',
                'role': usuario.role,
                'username': usuario.username
            })
        
        return jsonify({'success': False, 'message': 'Credenciales incorrectas'})
    
    return render_template('login.html')

# Ruta para admin (manejo con JavaScript)
@app.route('/admin/logout')
@login_required
def admin_logout():
    if current_user.role != 'admin':
        return redirect(url_for('logout'))
    
    logout_user()
    return jsonify({
        'success': True, 
        'message': 'Sesión de admin cerrada',
        'redirect': '/'
    })

# Ruta para usuarios normales
@app.route('/user/logout')
@login_required
def user_logout():
    logout_user()
    return redirect(url_for('index'))

# Ruta general (para compatibilidad)
@app.route('/logout')
@login_required
def logout():
    if current_user.role == 'admin':
        return admin_logout()
    else:
        return user_logout()

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return render_template('admin/dashboard.html')
    else:
        return render_template('user/dashboard.html')
    
# ========== NUEVA RUTA PARA VISTA SEMESTRAL COMPLETA DE USUARIO ==========

@app.route('/user/horario-semestral-completo')
@login_required
def horario_semestral_completo():
    """Página de horario semestral completo para usuarios (igual que admin)"""
    if current_user.role == 'admin':
        return redirect(url_for('dashboard'))
    return render_template('user/horario_semestral_completo.html')

# ========== NUEVO ENDPOINT PARA VISTA SEMESTRAL COMPLETA (IGUAL QUE ADMIN) ==========

@app.route('/api/mi-horario/vista-semestral-completa', methods=['GET'])
@login_required
def obtener_vista_semestral_completa_usuario():
    """Vista semestral completa IDÉNTICA a la del admin, pero solo lectura"""
    try:
        # Obtener parámetros de filtro
        año_param = request.args.get('ano', type=int)
        semestre_param = request.args.get('semestre', type=int)
        
        # Usar función helper
        horario_general = obtener_horario_por_filtros(año_param, semestre_param)
        
        if not horario_general:
            return jsonify({
                'success': False,
                'message': 'No hay horarios activos disponibles'
            })
        
        # Reutilizar la MISMA lógica que usa el admin
        from datetime import timedelta
        
        turnos = Turno.query.order_by(Turno.seccion, Turno.orden).all()
        
        # Obtener todas las asignaciones de este horario
        asignaciones = HorarioSemanal.query.filter_by(
            horario_general_id=horario_general.id
        ).order_by(
            HorarioSemanal.semana_numero,
            HorarioSemanal.dia_semana,
            HorarioSemanal.turno_id
        ).all()
        
        # Organizar datos por semana (EXACTAMENTE igual que en admin)
        semanas_data = []
        
        for semana_num in range(1, horario_general.semanas_totales + 1):
            es_examen = semana_num > horario_general.semanas_totales - horario_general.semanas_examenes
            
            # Calcular fechas de la semana
            fecha_lunes = horario_general.fecha_inicio + timedelta(days=(semana_num - 1) * 7)
            fecha_viernes = fecha_lunes + timedelta(days=4)
            
            # Buscar fecha específica si existe
            slot_lunes = next((a for a in asignaciones if a.semana_numero == semana_num and a.dia_semana == 0), None)
            if slot_lunes and slot_lunes.fecha_especifica:
                fecha_lunes = slot_lunes.fecha_especifica
                fecha_viernes = fecha_lunes + timedelta(days=4)
            
            semana_info = {
                'numero': semana_num,
                'es_examen': es_examen,
                'fecha_lunes': fecha_lunes.strftime('%d/%m/%Y'),
                'fecha_viernes': fecha_viernes.strftime('%d/%m/%Y'),
                'rango_fechas': f"{fecha_lunes.strftime('%d/%m/%Y')} - {fecha_viernes.strftime('%d/%m/%Y')}",
                'turnos': []
            }
            
            # Para cada turno
            for turno in turnos:
                turno_info = {
                    'id': turno.id,
                    'nombre': turno.nombre,
                    'hora_inicio': turno.hora_inicio,
                    'hora_fin': turno.hora_fin,
                    'seccion': turno.seccion,
                    'dias': {}
                }
                
                # Para cada día (Lunes a Viernes)
                dias_nombres = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
                for dia_num, dia_nombre in enumerate(dias_nombres):
                    # Buscar asignación para este slot específico
                    asignacion = next((a for a in asignaciones if 
                                     a.semana_numero == semana_num and 
                                     a.dia_semana == dia_num and 
                                     a.turno_id == turno.id), None)
                    
                    if asignacion and asignacion.asignatura:
                        turno_info['dias'][dia_nombre] = {
                            'asignatura_id': asignacion.asignatura_id,
                            'codigo': asignacion.asignatura.codigo,
                            'nombre': asignacion.asignatura.nombre,
                            'profesor': f"{asignacion.profesor.nombres} {asignacion.profesor.apellidos}" if asignacion.profesor else None,
                            'color': asignacion.color,
                            'ocupado': True,
                            'es_examen': asignacion.es_examen
                        }
                    else:
                        turno_info['dias'][dia_nombre] = {
                            'ocupado': False,
                            'es_viernes': dia_nombre == 'Viernes',
                            'es_examen': es_examen
                        }
                
                semana_info['turnos'].append(turno_info)
            
            semanas_data.append(semana_info)
        
        return jsonify({
            'success': True,
            'horario': horario_general.to_dict(),
            'semanas': semanas_data,
            'total_semanas': horario_general.semanas_totales,
            'semanas_clases': horario_general.semanas_clases,
            'semanas_examenes': horario_general.semanas_examenes,
            'turnos': [t.to_dict() for t in turnos],
            'modo': 'solo_lectura'  # Para diferenciar del admin
        })
        
    except Exception as e:
        print(f"Error en obtener_vista_semestral_completa_usuario: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ========== NUEVA RUTA PARA OBTENER HORARIOS DISPONIBLES ==========

@app.route('/api/horarios-disponibles-usuario', methods=['GET'])
@login_required
def obtener_horarios_disponibles_usuario():
    """Obtener lista de TODOS los horarios disponibles para el usuario normal"""
    try:
        # Obtener TODOS los horarios activos, ordenados por creación
        horarios = HorarioGeneral.query.filter_by(activo=True).order_by(
            HorarioGeneral.año_carrera,
            HorarioGeneral.semestre,
            HorarioGeneral.creado_en.desc()
        ).all()
        
        # Crear lista con información detallada de CADA horario
        horarios_lista = []
        for h in horarios:
            # Contar asignaciones en este horario
            asignaciones_count = HorarioSemanal.query.filter_by(
                horario_general_id=h.id
            ).filter(HorarioSemanal.asignatura_id.isnot(None)).count()
            
            # Calcular ocupación
            slots_totales = h.semanas_totales * 5 * 6  # semanas * días * turnos
            porcentaje_ocupado = (asignaciones_count / slots_totales * 100) if slots_totales > 0 else 0
            
            horarios_lista.append({
                'id': h.id,
                'año_carrera': h.año_carrera,
                'semestre': h.semestre,
                'año_academico': h.año_academico,
                'carrera': h.carrera,
                'modalidad': h.modalidad,
                'fecha_inicio': h.fecha_inicio.strftime('%d/%m/%Y') if h.fecha_inicio else None,
                'fecha_fin': h.fecha_fin.strftime('%d/%m/%Y') if h.fecha_fin else None,
                'semanas_totales': h.semanas_totales,
                'titulo': h.titulo,
                'creado_en': h.creado_en.strftime('%d/%m/%Y %H:%M') if h.creado_en else None,
                'asignaciones_count': asignaciones_count,
                'porcentaje_ocupado': round(porcentaje_ocupado, 1),
                'descripcion': f"Año {h.año_carrera} - Semestre {h.semestre} ({h.año_academico})",
                'descripcion_completa': f"Año {h.año_carrera} - Semestre {h.semestre} ({h.año_academico}) • Creado: {h.creado_en.strftime('%d/%m/%Y') if h.creado_en else 'N/A'} • {asignaciones_count} asignaciones ({porcentaje_ocupado:.1f}% ocupado)"
            })
        
        return jsonify({
            'success': True,
            'horarios_disponibles': horarios_lista,
            'total': len(horarios_lista)
        })
    except Exception as e:
        print(f"❌ Error en obtener_horarios_disponibles_usuario: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/debug/horarios', methods=['GET'])
@login_required
def debug_horarios():
    """Endpoint de depuración para ver todos los horarios (solo admin)"""
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    horarios = HorarioGeneral.query.all()
    result = []
    for h in horarios:
        result.append({
            'id': h.id,
            'titulo': h.titulo,
            'año_carrera': h.año_carrera,
            'semestre': h.semestre,
            'año_academico': h.año_academico,
            'activo': h.activo,
            'creado_en': h.creado_en.strftime('%d/%m/%Y %H:%M') if h.creado_en else None,
            'fecha_inicio': h.fecha_inicio.strftime('%d/%m/%Y') if h.fecha_inicio else None,
            'fecha_fin': h.fecha_fin.strftime('%d/%m/%Y') if h.fecha_fin else None,
            'semanas_totales': h.semanas_totales
        })
    return jsonify(result)

# ========== RUTAS PARA USUARIO NORMAL (MODIFICADAS PARA ACEPTAR FILTROS) ==========

@app.route('/api/mi-horario', methods=['GET'])
@login_required
def obtener_mi_horario():
    """Obtener el horario del usuario actual - AHORA CON SELECCIÓN DE AÑO"""
    try:
        # OBTENER PARÁMETROS DE AÑO Y SEMESTRE
        año_param = request.args.get('ano', type=int)
        semestre_param = request.args.get('semestre', type=int)
        
        # Verificar si el usuario es profesor
        profesor = Profesor.query.filter(
            (Profesor.email == current_user.email) |
            (Profesor.nombres.ilike(f"%{current_user.username}%"))
        ).first()
        
        if profesor:
            # ========== LÓGICA PARA PROFESOR ==========
            query = HorarioSemanal.query.filter_by(profesor_id=profesor.id)
            
            # Usar función helper para obtener horario
            horario_general = obtener_horario_por_filtros(año_param, semestre_param)
            
            if horario_general:
                query = query.filter_by(horario_general_id=horario_general.id)
            else:
                return jsonify({
                    'success': False,
                    'message': 'No hay horarios activos disponibles para los filtros especificados'
                })
            
            asignaciones = query.order_by(
                HorarioSemanal.semana_numero,
                HorarioSemanal.dia_semana,
                HorarioSemanal.turno_id
            ).all()
            
            # Organizar por semana
            horario_organizado = {}
            for asignacion in asignaciones:
                semana_key = f"Semana {asignacion.semana_numero}"
                if semana_key not in horario_organizado:
                    horario_organizado[semana_key] = []
                
                horario_organizado[semana_key].append({
                    'id': asignacion.id,
                    'semana_numero': asignacion.semana_numero,
                    'dia_semana': asignacion.dia_semana,
                    'dia_nombre': ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'][asignacion.dia_semana],
                    'turno_nombre': asignacion.turno.nombre if asignacion.turno else '',
                    'hora_inicio': asignacion.turno.hora_inicio if asignacion.turno else '',
                    'hora_fin': asignacion.turno.hora_fin if asignacion.turno else '',
                    'asignatura_codigo': asignacion.asignatura.codigo if asignacion.asignatura else '',
                    'asignatura_nombre': asignacion.asignatura.nombre if asignacion.asignatura else '',
                    'color': asignacion.color,
                    'es_examen': asignacion.es_examen,
                    'fecha_especifica': asignacion.fecha_especifica.isoformat() if asignacion.fecha_especifica else None
                })
            
            return jsonify({
                'success': True,
                'tipo': 'profesor',
                'profesor': {
                    'id': profesor.id,
                    'nombre_completo': f"{profesor.nombres} {profesor.apellidos}",
                    'categoria': profesor.categoria_academica
                },
                'horario': horario_organizado,
                'total_clases': len(asignaciones),
                'horario_info': horario_general.to_dict() if horario_general else None
            })
        
        # Si no es profesor, mostrar horario del grupo (basado en usuario)
        else:
            # Usar función helper para obtener horario
            horario_general = obtener_horario_por_filtros(año_param, semestre_param)
            
            if not horario_general:
                return jsonify({
                    'success': False,
                    'message': 'No hay horarios activos disponibles'
                })
            
            # Obtener asignaciones para mostrar
            asignaciones = HorarioSemanal.query.filter_by(
                horario_general_id=horario_general.id
            ).filter(
                HorarioSemanal.asignatura_id.isnot(None)
            ).order_by(
                HorarioSemanal.semana_numero,
                HorarioSemanal.dia_semana,
                HorarioSemanal.turno_id
            ).limit(50).all()
            
            # Organizar por día de la semana
            horario_por_dia = {}
            dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
            
            for dia_num, dia_nombre in enumerate(dias):
                clases_dia = []
                for asignacion in asignaciones:
                    if asignacion.dia_semana == dia_num:
                        clases_dia.append({
                            'turno': asignacion.turno.nombre if asignacion.turno else '',
                            'hora': f"{asignacion.turno.hora_inicio if asignacion.turno else ''} - {asignacion.turno.hora_fin if asignacion.turno else ''}",
                            'asignatura': asignacion.asignatura.nombre if asignacion.asignatura else '',
                            'codigo': asignacion.asignatura.codigo if asignacion.asignatura else '',
                            'profesor': f"{asignacion.profesor.nombres} {asignacion.profesor.apellidos}" if asignacion.profesor else '',
                            'color': asignacion.color
                        })
                
                if clases_dia:
                    horario_por_dia[dia_nombre] = clases_dia
            
            return jsonify({
                'success': True,
                'tipo': 'estudiante',
                'horario_general': horario_general.to_dict(),
                'horario_por_dia': horario_por_dia,
                'total_clases': len(asignaciones)
            })
            
    except Exception as e:
        print(f"Error en obtener_mi_horario: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ========== NUEVOS ENDPOINTS PARA USUARIO (MODIFICADOS) ==========

@app.route('/api/mi-horario/vista-semestral', methods=['GET'])
@login_required
def obtener_vista_semestral_usuario():
    """Obtener vista semestral del horario para el usuario"""
    try:
        # Obtener parámetros de filtro
        año_param = request.args.get('ano', type=int)
        semestre_param = request.args.get('semestre', type=int)
        
        # Verificar si es profesor
        profesor = Profesor.query.filter(
            (Profesor.email == current_user.email) |
            (Profesor.nombres.ilike(f"%{current_user.username}%"))
        ).first()
        
        if profesor:
            # Usar función helper para obtener horario
            horario_general = obtener_horario_por_filtros(año_param, semestre_param)
            
            if not horario_general:
                return jsonify({
                    'success': False,
                    'message': 'No hay horarios activos disponibles'
                })
            
            # Obtener todas las asignaciones del profesor en este horario
            asignaciones = HorarioSemanal.query.filter_by(
                profesor_id=profesor.id,
                horario_general_id=horario_general.id
            ).order_by(
                HorarioSemanal.semana_numero,
                HorarioSemanal.dia_semana,
                HorarioSemanal.turno_id
            ).all()
            
            # Organizar por semana
            horario_organizado = {}
            for asignacion in asignaciones:
                semana_key = f"Semana {asignacion.semana_numero}"
                if semana_key not in horario_organizado:
                    horario_organizado[semana_key] = []
                
                horario_organizado[semana_key].append({
                    'id': asignacion.id,
                    'semana_numero': asignacion.semana_numero,
                    'dia_semana': asignacion.dia_semana,
                    'dia_nombre': ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'][asignacion.dia_semana],
                    'turno_id': asignacion.turno_id,
                    'turno_nombre': asignacion.turno.nombre if asignacion.turno else '',
                    'hora_inicio': asignacion.turno.hora_inicio if asignacion.turno else '',
                    'hora_fin': asignacion.turno.hora_fin if asignacion.turno else '',
                    'asignatura': asignacion.asignatura.nombre if asignacion.asignatura else '',
                    'codigo': asignacion.asignatura.codigo if asignacion.asignatura else '',
                    'nombre': asignacion.asignatura.nombre if asignacion.asignatura else '',
                    'profesor': f"{asignacion.profesor.nombres} {asignacion.profesor.apellidos}" if asignacion.profesor else '',
                    'profesor_nombre': f"{asignacion.profesor.nombres} {asignacion.profesor.apellidos}" if asignacion.profesor else '',
                    'color': asignacion.color,
                    'es_examen': asignacion.es_examen,
                    'aula': 'Por asignar'
                })
            
            return jsonify({
                'success': True,
                'tipo': 'profesor',
                'horario': horario_organizado,
                'total_semanas': horario_general.semanas_totales if horario_general else 22,
                'profesor': {
                    'nombre_completo': f"{profesor.nombres} {profesor.apellidos}"
                },
                'horario_info': horario_general.to_dict() if horario_general else None
            })
        
        # Para estudiantes
        else:
            # Usar función helper para obtener horario
            horario_general = obtener_horario_por_filtros(año_param, semestre_param)
            
            if not horario_general:
                return jsonify({
                    'success': False,
                    'message': 'No hay horarios activos disponibles'
                })
            
            # Obtener asignaciones del horario
            asignaciones = HorarioSemanal.query.filter_by(
                horario_general_id=horario_general.id
            ).filter(
                HorarioSemanal.asignatura_id.isnot(None)
            ).order_by(
                HorarioSemanal.dia_semana,
                HorarioSemanal.turno_id
            ).all()
            
            # Organizar por día
            horario_por_dia = {}
            dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
            
            for dia_num, dia_nombre in enumerate(dias):
                clases_dia = []
                for asignacion in asignaciones:
                    if asignacion.dia_semana == dia_num:
                        turno_nombre = asignacion.turno.nombre if asignacion.turno else ''
                        clases_dia.append({
                            'turno': turno_nombre,
                            'hora': f"{asignacion.turno.hora_inicio if asignacion.turno else ''} - {asignacion.turno.hora_fin if asignacion.turno else ''}",
                            'asignatura': asignacion.asignatura.nombre if asignacion.asignatura else '',
                            'codigo': asignacion.asignatura.codigo if asignacion.asignatura else '',
                            'nombre': asignacion.asignatura.nombre if asignacion.asignatura else '',
                            'profesor': f"{asignacion.profesor.nombres} {asignacion.profesor.apellidos}" if asignacion.profesor else '',
                            'color': asignacion.color,
                            'es_examen': asignacion.es_examen
                        })
                
                if clases_dia:
                    horario_por_dia[dia_nombre] = clases_dia
            
            return jsonify({
                'success': True,
                'tipo': 'estudiante',
                'horario': horario_por_dia,
                'total_semanas': horario_general.semanas_totales,
                'horario_general': horario_general.to_dict()
            })
            
    except Exception as e:
        print(f"Error en obtener_vista_semestral_usuario: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/horarios/semana/<int:semana>', methods=['GET'])
@login_required
def obtener_semana_especifica(semana):
    """Obtener horario de una semana específica para el usuario actual"""
    try:
        # Obtener parámetros de filtro
        año_param = request.args.get('ano', type=int)
        semestre_param = request.args.get('semestre', type=int)
        
        # Verificar si es profesor
        profesor = Profesor.query.filter(
            (Profesor.email == current_user.email) |
            (Profesor.nombres.ilike(f"%{current_user.username}%"))
        ).first()
        
        # Usar función helper para obtener horario
        horario_general = obtener_horario_por_filtros(año_param, semestre_param)
        
        if not horario_general:
            return jsonify({'success': False, 'message': 'No hay horarios activos'})
        
        # Obtener asignaciones de la semana específica
        asignaciones = HorarioSemanal.query.filter_by(
            horario_general_id=horario_general.id,
            semana_numero=semana
        ).filter(
            HorarioSemanal.asignatura_id.isnot(None)
        ).order_by(
            HorarioSemanal.dia_semana,
            HorarioSemanal.turno_id
        ).all()
        
        # Si es profesor, filtrar solo sus clases
        if profesor:
            asignaciones = [a for a in asignaciones if a.profesor_id == profesor.id]
        
        # Organizar por día
        calendario = []
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        
        for dia_num, dia_nombre in enumerate(dias):
            clases_dia = []
            for asignacion in asignaciones:
                if asignacion.dia_semana == dia_num:
                    clases_dia.append({
                        'hora': f"{asignacion.turno.hora_inicio} - {asignacion.turno.hora_fin}",
                        'asignatura': asignacion.asignatura.codigo if asignacion.asignatura else '',
                        'nombre': asignacion.asignatura.nombre if asignacion.asignatura else '',
                        'profesor': f"{asignacion.profesor.nombres} {asignacion.profesor.apellidos}" if asignacion.profesor else '',
                        'color': asignacion.color,
                        'es_examen': asignacion.es_examen
                    })
            
            calendario.append({
                'dia': dia_nombre,
                'fecha': 'Por calcular',
                'es_hoy': False,
                'clases': clases_dia,
                'total_clases': len(clases_dia)
            })
        
        return jsonify({
            'success': True,
            'semana': semana,
            'calendario': calendario,
            'total_clases': len(asignaciones),
            'horario_info': horario_general.to_dict()
        })
        
    except Exception as e:
        print(f"Error en obtener_semana_especifica: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/mis-asignaturas', methods=['GET'])
@login_required
def obtener_mis_asignaturas():
    """Obtener asignaturas del usuario actual"""
    try:
        # Obtener parámetros de filtro
        año_param = request.args.get('ano', type=int)
        semestre_param = request.args.get('semestre', type=int)
        
        # Para profesores: asignaturas que imparte
        profesor = Profesor.query.filter(
            (Profesor.email == current_user.email) |
            (Profesor.nombres.ilike(f"%{current_user.username}%"))
        ).first()
        
        if profesor:
            # Filtrar asignaturas por año y semestre si se especifican
            query = Asignatura.query.filter_by(profesor_id=profesor.id)
            
            if año_param and semestre_param:
                query = query.filter_by(
                    año_academico=año_param,
                    periodo=semestre_param
                )
            
            asignaturas = query.all()
            
            resultado = []
            for asignatura in asignaturas:
                # Contar horas asignadas en horarios
                horas_asignadas = HorarioSemanal.query.filter_by(
                    asignatura_id=asignatura.id
                ).count() * 1.5  # Cada turno = 1.5 horas
                
                resultado.append({
                    'id': asignatura.id,
                    'codigo': asignatura.codigo,
                    'nombre': asignatura.nombre,
                    'año_academico': asignatura.año_academico,
                    'periodo': asignatura.periodo,
                    'horas_presenciales': asignatura.horas_presenciales,
                    'horas_asignadas': horas_asignadas,
                    'color': asignatura.color,
                    'porcentaje_completado': min(100, (horas_asignadas / asignatura.horas_presenciales * 100) if asignatura.horas_presenciales > 0 else 0)
                })
            
            return jsonify({
                'success': True,
                'tipo': 'profesor',
                'asignaturas': resultado,
                'total_asignaturas': len(asignaturas),
                'total_horas': sum(a.horas_presenciales for a in asignaturas)
            })
        
        # Para estudiantes: asignaturas del horario actual
        else:
            # Usar función helper para obtener horario
            horario_general = obtener_horario_por_filtros(año_param, semestre_param)
            
            if not horario_general:
                return jsonify({
                    'success': False,
                    'message': 'No hay horarios activos'
                })
            
            # Obtener asignaturas únicas del horario
            asignaturas_ids = db.session.query(HorarioSemanal.asignatura_id).filter(
                HorarioSemanal.horario_general_id == horario_general.id,
                HorarioSemanal.asignatura_id.isnot(None)
            ).distinct().all()
            
            asignaturas_ids = [id[0] for id in asignaturas_ids]
            
            asignaturas = Asignatura.query.filter(
                Asignatura.id.in_(asignaturas_ids)
            ).all()
            
            resultado = []
            for asignatura in asignaturas:
                # Contar turnos en el horario
                turnos_asignados = HorarioSemanal.query.filter_by(
                    horario_general_id=horario_general.id,
                    asignatura_id=asignatura.id
                ).count()
                
                resultado.append({
                    'id': asignatura.id,
                    'codigo': asignatura.codigo,
                    'nombre': asignatura.nombre,
                    'profesor': f"{asignatura.profesor_rel.nombres} {asignatura.profesor_rel.apellidos}" if asignatura.profesor_rel else 'Sin asignar',
                    'horas_semanales': asignatura.horas_presenciales,
                    'turnos_semanales': turnos_asignados,
                    'color': asignatura.color,
                    'tipo_evaluacion': asignatura.tipo_evaluacion
                })
            
            return jsonify({
                'success': True,
                'tipo': 'estudiante',
                'asignaturas': resultado,
                'total_asignaturas': len(asignaturas),
                'horario_info': horario_general.to_dict()
            })
            
    except Exception as e:
        print(f"Error en obtener_mis_asignaturas: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/calendario-semanal', methods=['GET'])
@login_required
def obtener_calendario_semanal():
    """Obtener calendario semanal para el usuario actual"""
    try:
        # Obtener parámetros de filtro
        año_param = request.args.get('ano', type=int)
        semestre_param = request.args.get('semestre', type=int)
        
        semana_solicitada = request.args.get('semana', type=int)
        
        # Usar función helper para obtener horario
        horario_general = obtener_horario_por_filtros(año_param, semestre_param)
        
        if not horario_general:
            return jsonify({
                'success': False,
                'message': 'No hay horarios activos'
            })
        
        # Obtener semana actual
        hoy = date.today()
        
        # Calcular semana actual basada en fecha de inicio
        if hoy < horario_general.fecha_inicio:
            semana_actual = 1
        elif hoy > horario_general.fecha_fin:
            semana_actual = horario_general.semanas_totales
        else:
            dias_diferencia = (hoy - horario_general.fecha_inicio).days
            semana_actual = (dias_diferencia // 7) + 1
        
        # Si se solicita una semana específica, usar esa
        if semana_solicitada:
            semana_actual = semana_solicitada
        
        # Limitar a rango válido
        semana_actual = max(1, min(semana_actual, horario_general.semanas_totales))
        
        # Verificar si es semana de exámenes
        es_examen = semana_actual > (horario_general.semanas_totales - horario_general.semanas_examenes)
        
        # Obtener asignaciones de esta semana
        asignaciones = HorarioSemanal.query.filter_by(
            horario_general_id=horario_general.id,
            semana_numero=semana_actual
        ).filter(
            HorarioSemanal.asignatura_id.isnot(None)
        ).order_by(
            HorarioSemanal.dia_semana,
            HorarioSemanal.turno_id
        ).all()
        
        # Organizar por día
        calendario = []
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        
        for dia_num, dia_nombre in enumerate(dias):
            # Calcular fecha específica
            fecha_dia = horario_general.fecha_inicio + timedelta(
                days=((semana_actual - 1) * 7) + dia_num
            )
            
            # Verificar si hay clases este día
            clases_dia = []
            for asignacion in asignaciones:
                if asignacion.dia_semana == dia_num:
                    clases_dia.append({
                        'hora': f"{asignacion.turno.hora_inicio} - {asignacion.turno.hora_fin}",
                        'asignatura': asignacion.asignatura.codigo if asignacion.asignatura else '',
                        'nombre': asignacion.asignatura.nombre if asignacion.asignatura else '',
                        'profesor': f"{asignacion.profesor.nombres} {asignacion.profesor.apellidos}" if asignacion.profesor else '',
                        'aula': 'Por asignar',
                        'color': asignacion.color,
                        'es_examen': asignacion.es_examen
                    })
            
            calendario.append({
                'dia': dia_nombre,
                'fecha': fecha_dia.strftime('%d/%m/%Y'),
                'es_hoy': fecha_dia == hoy,
                'clases': clases_dia,
                'total_clases': len(clases_dia)
            })
        
        # Próximos eventos (ej: exámenes)
        proximos_eventos = []
        
        # Buscar exámenes en las próximas 2 semanas
        for semana_offset in range(0, 3):
            semana_check = semana_actual + semana_offset
            if semana_check > horario_general.semanas_totales:
                continue
            
            asignaciones_examen = HorarioSemanal.query.filter_by(
                horario_general_id=horario_general.id,
                semana_numero=semana_check,
                es_examen=True
            ).filter(
                HorarioSemanal.asignatura_id.isnot(None)
            ).all()
            
            for examen in asignaciones_examen:
                fecha_examen = horario_general.fecha_inicio + timedelta(
                    days=((semana_check - 1) * 7) + examen.dia_semana
                )
                
                if fecha_examen >= hoy:
                    proximos_eventos.append({
                        'tipo': 'EXAMEN',
                        'asignatura': examen.asignatura.codigo if examen.asignatura else '',
                        'nombre': examen.asignatura.nombre if examen.asignatura else '',
                        'fecha': fecha_examen.strftime('%d/%m/%Y'),
                        'dia': dias[examen.dia_semana],
                        'hora': f"{examen.turno.hora_inicio} - {examen.turno.hora_fin}",
                        'dias_faltantes': (fecha_examen - hoy).days
                    })
        
        return jsonify({
            'success': True,
            'semana_actual': semana_actual,
            'es_semana_examen': es_examen,
            'calendario': calendario,
            'proximos_eventos': sorted(proximos_eventos, key=lambda x: x['dias_faltantes'])[:5],
            'total_clases_semana': sum(dia['total_clases'] for dia in calendario),
            'hoy': hoy.strftime('%d/%m/%Y'),
            'horario_info': horario_general.to_dict()
        })
        
    except Exception as e:
        print(f"Error en obtener_calendario_semanal: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/estadisticas-personales', methods=['GET'])
@login_required
def obtener_estadisticas_personales():
    """Obtener estadísticas personales del usuario"""
    try:
        # Obtener parámetros de filtro
        año_param = request.args.get('ano', type=int)
        semestre_param = request.args.get('semestre', type=int)
        
        # Verificar si es profesor
        profesor = Profesor.query.filter(
            (Profesor.email == current_user.email) |
            (Profesor.nombres.ilike(f"%{current_user.username}%"))
        ).first()
        
        if profesor:
            # Estadísticas para profesor
            # Filtrar por año y semestre si se especifican
            query = Asignatura.query.filter_by(profesor_id=profesor.id)
            
            if año_param and semestre_param:
                query = query.filter_by(
                    año_academico=año_param,
                    periodo=semestre_param
                )
            
            total_asignaturas = query.count()
            
            total_horas_semanales = db.session.query(
                db.func.sum(Asignatura.horas_presenciales)
            ).filter_by(profesor_id=profesor.id)
            
            if año_param and semestre_param:
                total_horas_semanales = total_horas_semanales.filter_by(
                    año_academico=año_param,
                    periodo=semestre_param
                )
            
            total_horas_semanales = total_horas_semanales.scalar() or 0
            
            # Horas asignadas en horarios
            asignaciones_query = HorarioSemanal.query.filter_by(profesor_id=profesor.id)
            
            if año_param and semestre_param:
                # Obtener horario específico
                horario = obtener_horario_por_filtros(año_param, semestre_param)
                if horario:
                    asignaciones_query = asignaciones_query.filter_by(horario_general_id=horario.id)
            
            asignaciones = asignaciones_query.count()
            horas_asignadas = asignaciones * 1.5
            
            return jsonify({
                'success': True,
                'tipo_usuario': 'profesor',
                'estadisticas': {
                    'total_asignaturas': total_asignaturas,
                    'total_horas_semanales': total_horas_semanales,
                    'horas_asignadas': horas_asignadas,
                    'porcentaje_asignado': min(100, (horas_asignadas / total_horas_semanales * 100) if total_horas_semanales > 0 else 0),
                    'clases_semana': asignaciones,
                    'categoria': profesor.categoria_academica or 'No especificada'
                },
                'profesor': {
                    'nombre': f"{profesor.nombres} {profesor.apellidos}",
                    'email': profesor.email or current_user.email,
                    'telefono': profesor.telefono or 'No especificado'
                }
            })
        
        # Estadísticas para estudiante
        else:
            # Usar función helper para obtener horario
            horario_general = obtener_horario_por_filtros(año_param, semestre_param)
            
            if horario_general:
                total_clases = HorarioSemanal.query.filter_by(
                    horario_general_id=horario_general.id
                ).filter(
                    HorarioSemanal.asignatura_id.isnot(None)
                ).count()

                # CORRECCIÓN: Calcular HORAS SEMANALES, no totales del semestre
                # Cada turno = 1.5 horas, dividido entre semanas de clase

                total_horas_semestre = total_clases * 1.5
                semanas_clases = horario_general.semanas_clases

                # Horas SEMANALES promedio
                total_horas_semanales = round(total_horas_semestre / semanas_clases, 1) if semanas_clases > 0 else 0
                
                # Asignaturas únicas
                asignaturas_unicas = db.session.query(
                    db.func.count(db.distinct(HorarioSemanal.asignatura_id))
                ).filter_by(
                    horario_general_id=horario_general.id
                ).filter(
                    HorarioSemanal.asignatura_id.isnot(None)
                ).scalar() or 0
                
                return jsonify({
                    'success': True,
                    'tipo_usuario': 'estudiante',
                    'estadisticas': {
                        'total_asignaturas': asignaturas_unicas,
                        'total_clases_semana': round(total_clases / semanas_clases, 1) if semanas_clases > 0 else 0,
                        'total_horas_semanales': total_horas_semanales,  # CORREGIDO
                        'horas_promedio_dia': round(total_horas_semanales / 5, 1) if total_horas_semanales > 0 else 0,
                        'carrera': horario_general.carrera,
                        'año': horario_general.año_carrera,
                        'semestre': horario_general.semestre
                    },
                    'horario_info': {
                        'año_academico': horario_general.año_academico,
                        'fecha_inicio': horario_general.fecha_inicio.strftime('%d/%m/%Y'),
                        'fecha_fin': horario_general.fecha_fin.strftime('%d/%m/%Y'),
                        'semanas_totales': horario_general.semanas_totales,
                        'semanas_clases': semanas_clases
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'No hay horarios activos'
                })
                
    except Exception as e:
        print(f"Error en obtener_estadisticas_personales: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ========== RUTAS API ASIGNATURAS ==========

@app.route('/api/asignaturas', methods=['GET'])
@login_required
def get_asignaturas():
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    asignaturas = Asignatura.query.all()
    result = []
    for a in asignaturas:
        profesor_info = None
        if a.profesor_id:
            profesor = Profesor.query.get(a.profesor_id)
            if profesor:
                profesor_info = {
                    'id': profesor.id,
                    'codigo': profesor.codigo,
                    'nombres': profesor.nombres,
                    'apellidos': profesor.apellidos,
                    'nombre_completo': f"{profesor.nombres} {profesor.apellidos}"
                }
        
        result.append({
            'id': a.id,
            'codigo': a.codigo,
            'nombre': a.nombre,
            'descripcion': a.descripcion,
            'año_academico': a.año_academico,
            'periodo': a.periodo,
            'horas_presenciales': a.horas_presenciales,
            'horas_no_presenciales': a.horas_no_presenciales,
            'horas_totales': a.horas_totales,
            'tipo_evaluacion': a.tipo_evaluacion,
            'color': a.color,
            'profesor_id': a.profesor_id,
            'profesor': profesor_info
        })
    return jsonify(result)

@app.route('/api/asignaturas/<int:id>', methods=['GET'])
@login_required
def get_asignatura(id):
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    asignatura = Asignatura.query.get(id)
    
    if not asignatura:
        return jsonify({'error': 'Asignatura no encontrada'}), 404
    
    return jsonify({
        'id': asignatura.id,
        'codigo': asignatura.codigo,
        'nombre': asignatura.nombre,
        'descripcion': asignatura.descripcion,
        'año_academico': asignatura.año_academico,
        'periodo': asignatura.periodo,
        'horas_presenciales': asignatura.horas_presenciales,
        'horas_no_presenciales': asignatura.horas_no_presenciales,
        'horas_totales': asignatura.horas_totales,
        'tipo_evaluacion': asignatura.tipo_evaluacion,
        'color': asignatura.color,
        'profesor_id': asignatura.profesor_id
    })

@app.route('/api/asignaturas', methods=['POST'])
@login_required
def crear_asignatura():
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    data = request.get_json()
    
    if not all(k in data for k in ['codigo', 'nombre', 'año_academico', 'periodo']):
        return jsonify({'error': 'Faltan campos requeridos'}), 400
    
    if Asignatura.query.filter_by(codigo=data['codigo']).first():
        return jsonify({'error': 'El código ya existe'}), 400
    
    horas_presenciales = data.get('horas_presenciales', 0)
    horas_no_presenciales = data.get('horas_no_presenciales', 0)
    horas_totales = horas_presenciales + horas_no_presenciales
    
    nueva_asignatura = Asignatura(
        codigo=data['codigo'],
        nombre=data['nombre'],
        descripcion=data.get('descripcion', ''),
        año_academico=data['año_academico'],
        periodo=data['periodo'],
        horas_presenciales=horas_presenciales,
        horas_no_presenciales=horas_no_presenciales,
        horas_totales=horas_totales,
        tipo_evaluacion=data.get('tipo_evaluacion', 'EF'),
        color=data.get('color', '#3498db'),
        profesor_id=data.get('profesor_id')
    )
    
    try:
        db.session.add(nueva_asignatura)
        db.session.commit()
        return jsonify({'success': True, 'id': nueva_asignatura.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/asignaturas/<int:id>', methods=['PUT'])
@login_required
def actualizar_asignatura(id):
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    asignatura = Asignatura.query.get(id)
    
    if not asignatura:
        return jsonify({'error': 'Asignatura no encontrada'}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No se recibieron datos para actualizar'}), 400
    
    if 'codigo' in data:
        if data['codigo'] != asignatura.codigo and Asignatura.query.filter_by(codigo=data['codigo']).first():
            return jsonify({'error': 'El código ya está en uso por otra asignatura'}), 400
        asignatura.codigo = data['codigo']
    
    if 'nombre' in data:
        asignatura.nombre = data['nombre']
    
    if 'descripcion' in data:
        asignatura.descripcion = data['descripcion']
    
    if 'año_academico' in data:
        asignatura.año_academico = int(data['año_academico'])
    
    if 'periodo' in data:
        asignatura.periodo = int(data['periodo'])
    
    if 'horas_presenciales' in data:
        asignatura.horas_presenciales = int(data['horas_presenciales'])
    
    if 'horas_no_presenciales' in data:
        asignatura.horas_no_presenciales = int(data['horas_no_presenciales'])
    
    if 'tipo_evaluacion' in data:
        asignatura.tipo_evaluacion = data['tipo_evaluacion']
    
    if 'color' in data:
        asignatura.color = data['color']
    
    if 'profesor_id' in data:
        asignatura.profesor_id = data['profesor_id'] if data['profesor_id'] else None
    
    asignatura.horas_totales = asignatura.horas_presenciales + asignatura.horas_no_presenciales
    asignatura.fecha_creacion = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Asignatura actualizada exitosamente',
            'asignatura': {
                'id': asignatura.id,
                'codigo': asignatura.codigo,
                'nombre': asignatura.nombre,
                'año_academico': asignatura.año_academico,
                'periodo': asignatura.periodo,
                'horas_presenciales': asignatura.horas_presenciales,
                'horas_no_presenciales': asignatura.horas_no_presenciales,
                'horas_totales': asignatura.horas_totales,
                'tipo_evaluacion': asignatura.tipo_evaluacion,
                'color': asignatura.color,
                'profesor_id': asignatura.profesor_id
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al actualizar: {str(e)}'}), 500

@app.route('/api/asignaturas/<int:id>', methods=['DELETE'])
@login_required
def eliminar_asignatura(id):
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    asignatura = Asignatura.query.get_or_404(id)
    
    try:
        db.session.delete(asignatura)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ========== RUTAS API PROFESORES ==========

@app.route('/api/profesores', methods=['GET'])
@login_required
def get_profesores():
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    profesores = Profesor.query.all()
    result = []
    for p in profesores:
        result.append({
            'id': p.id,
            'codigo': p.codigo,
            'nombres': p.nombres,
            'apellidos': p.apellidos,
            'categoria_academica': p.categoria_academica,
            'categoria_cientifica': p.categoria_cientifica,
            'email': p.email,
            'telefono': p.telefono,
            'activo': p.activo
        })
    return jsonify(result)

@app.route('/api/profesores/<int:id>', methods=['GET'])
@login_required
def get_profesor(id):
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    profesor = Profesor.query.get(id)
    
    if not profesor:
        return jsonify({'error': 'Profesor no encontrado'}), 404
    
    return jsonify({
        'id': profesor.id,
        'codigo': profesor.codigo,
        'nombres': profesor.nombres,
        'apellidos': profesor.apellidos,
        'categoria_academica': profesor.categoria_academica,
        'categoria_cientifica': profesor.categoria_cientifica,
        'email': profesor.email,
        'telefono': profesor.telefono,
        'activo': profesor.activo
    })

@app.route('/api/profesores', methods=['POST'])
@login_required
def crear_profesor():
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    data = request.get_json()
    
    if not all(k in data for k in ['codigo', 'nombres', 'apellidos']):
        return jsonify({'error': 'Faltan campos requeridos'}), 400
    
    if Profesor.query.filter_by(codigo=data['codigo']).first():
        return jsonify({'error': 'El código ya existe'}), 400
    
    nuevo_profesor = Profesor(
        codigo=data['codigo'],
        nombres=data['nombres'],
        apellidos=data['apellidos'],
        categoria_academica=data.get('categoria_academica', ''),
        categoria_cientifica=data.get('categoria_cientifica', ''),
        email=data.get('email', ''),
        telefono=data.get('telefono', '')
    )
    
    try:
        db.session.add(nuevo_profesor)
        db.session.commit()
        return jsonify({'success': True, 'id': nuevo_profesor.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/profesores/<int:id>', methods=['PUT'])
@login_required
def actualizar_profesor(id):
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    profesor = Profesor.query.get(id)
    
    if not profesor:
        return jsonify({'error': 'Profesor no encontrado'}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No se recibieron datos para actualizar'}), 400
    
    if 'codigo' in data:
        if data['codigo'] != profesor.codigo and Profesor.query.filter_by(codigo=data['codigo']).first():
            return jsonify({'error': 'El código ya está en uso por otro profesor'}), 400
        profesor.codigo = data['codigo']
    
    if 'nombres' in data:
        profesor.nombres = data['nombres']
    
    if 'apellidos' in data:
        profesor.apellidos = data['apellidos']
    
    if 'categoria_academica' in data:
        profesor.categoria_academica = data['categoria_academica']
    
    if 'categoria_cientifica' in data:
        profesor.categoria_cientifica = data['categoria_cientifica']
    
    if 'email' in data:
        profesor.email = data['email']
    
    if 'telefono' in data:
        profesor.telefono = data['telefono']
    
    if 'activo' in data:
        profesor.activo = data['activo']
    
    profesor.fecha_creacion = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Profesor actualizado exitosamente',
            'profesor': {
                'id': profesor.id,
                'codigo': profesor.codigo,
                'nombres': profesor.nombres,
                'apellidos': profesor.apellidos,
                'categoria_academica': profesor.categoria_academica,
                'categoria_cientifica': profesor.categoria_cientifica,
                'email': profesor.email,
                'telefono': profesor.telefono,
                'activo': profesor.activo
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al actualizar: {str(e)}'}), 500

@app.route('/api/profesores/<int:id>', methods=['DELETE'])
@login_required
def eliminar_profesor(id):
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    profesor = Profesor.query.get_or_404(id)
    
    if profesor.asignaturas:
        return jsonify({'error': 'No se puede eliminar el profesor porque tiene asignaturas asignadas'}), 400
    
    try:
        db.session.delete(profesor)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/profesores/activos')
@login_required
def get_profesores_activos():
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    profesores = Profesor.query.filter_by(activo=True).all()
    result = []
    for p in profesores:
        result.append({
            'id': p.id,
            'codigo': p.codigo,
            'nombre_completo': f"{p.nombres} {p.apellidos}"
        })
    return jsonify(result)

@app.route('/api/asignaturas/por-profesor/<int:profesor_id>')
@login_required
def get_asignaturas_por_profesor(profesor_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    asignaturas = Asignatura.query.filter_by(profesor_id=profesor_id).all()
    result = []
    for a in asignaturas:
        result.append({
            'id': a.id,
            'codigo': a.codigo,
            'nombre': a.nombre,
            'año_academico': a.año_academico,
            'periodo': a.periodo,
            'color': a.color
        })
    return jsonify(result)

# ========== RUTAS API TURNOS ==========

@app.route('/api/turnos', methods=['GET'])
@login_required
def get_turnos():
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    turnos = Turno.query.order_by(Turno.seccion, Turno.orden).all()
    result = []
    for t in turnos:
        result.append({
            'id': t.id,
            'nombre': t.nombre,
            'hora_inicio': t.hora_inicio,
            'hora_fin': t.hora_fin,
            'duracion_minutos': t.duracion_minutos,
            'seccion': t.seccion,
            'orden': t.orden,
            'activo': t.activo
        })
    return jsonify(result)

@app.route('/api/turnos/actualizar-multiples', methods=['PUT'])
@login_required
def actualizar_turnos_multiples():
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    data = request.get_json()
    
    if 'turnos' not in data:
        return jsonify({'error': 'No se recibieron datos de turnos'}), 400
    
    try:
        for turno_data in data['turnos']:
            turno_id = turno_data.get('id')
            hora_inicio = turno_data.get('hora_inicio')
            hora_fin = turno_data.get('hora_fin')
            
            if not all([turno_id, hora_inicio, hora_fin]):
                continue
            
            turno = Turno.query.get(turno_id)
            if turno:
                turno.hora_inicio = hora_inicio
                turno.hora_fin = hora_fin
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Turnos actualizados exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========== RUTAS API HORARIOS (NUEVO) ==========

@app.route('/api/horarios', methods=['GET'])
@login_required
def get_horarios():
    """Obtener lista de horarios creados"""
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    horarios = HorarioGeneral.query.filter_by(activo=True).all()
    result = []
    for h in horarios:
        horario_dict = h.to_dict()
        # Contar asignaciones
        asignaciones_count = HorarioSemanal.query.filter_by(
            horario_general_id=h.id
        ).filter(HorarioSemanal.asignatura_id.isnot(None)).count()
        
        horario_dict['asignaciones_count'] = asignaciones_count
        horario_dict['slots_totales'] = h.semanas_totales * 5 * 6  # semanas * días * turnos
        result.append(horario_dict)
    
    return jsonify(result)

@app.route('/api/horarios/<int:id>', methods=['GET'])
@login_required
def get_horario(id):
    """Obtener un horario específico con sus asignaciones"""
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    horario = HorarioGeneral.query.get_or_404(id)
    
    # Obtener todas las asignaciones de este horario
    asignaciones = HorarioSemanal.query.filter_by(horario_general_id=id).all()
    
    # Obtener asignaturas disponibles para este año y semestre
    asignaturas_disponibles = Asignatura.query.filter_by(
        año_academico=horario.año_carrera,
        periodo=horario.semestre
    ).all()
    
    # Convertir asignaturas a dict
    asignaturas_dict = []
    for a in asignaturas_disponibles:
        profesor_nombre = None
        if a.profesor_rel:
            profesor_nombre = f"{a.profesor_rel.nombres} {a.profesor_rel.apellidos}"
        
        asignaturas_dict.append({
            'id': a.id,
            'codigo': a.codigo,
            'nombre': a.nombre,
            'color': a.color,
            'horas_presenciales': a.horas_presenciales,
            'profesor_nombre': profesor_nombre,
            'turnos_maximos': min(5, a.horas_presenciales // 1.5)  # Cada turno = 1.5 horas
        })
    
    # Obtener turnos ORDENADOS: Primero todas las mañanas, luego todas las tardes
    turnos_mañana = Turno.query.filter_by(seccion="mañana").order_by(Turno.orden).all()
    turnos_tarde = Turno.query.filter_by(seccion="tarde").order_by(Turno.orden).all()
    turnos_combinados = turnos_mañana + turnos_tarde
    
    return jsonify({
        'horario': horario.to_dict(),
        'asignaciones': [a.to_dict() for a in asignaciones],
        'asignaturas_disponibles': asignaturas_dict,
        'turnos': [{
            'id': t.id,
            'nombre': t.nombre,
            'hora_inicio': t.hora_inicio,
            'hora_fin': t.hora_fin,
            'duracion_minutos': t.duracion_minutos,
            'seccion': t.seccion,
            'orden': t.orden,
            'activo': t.activo
        } for t in turnos_combinados]
    })

@app.route('/api/horarios', methods=['POST'])
@login_required
def crear_horario():
    """Crear un nuevo horario (estructura vacía)"""
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    data = request.get_json()
    
    # Validaciones
    required_fields = ['titulo', 'año_academico', 'semestre', 'año_carrera', 'fecha_inicio', 'fecha_fin']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Faltan campos requeridos'}), 400
    
    # Calcular semanas si no se proporcionan
    fecha_inicio = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date()
    fecha_fin = datetime.strptime(data['fecha_fin'], '%Y-%m-%d').date()
    
    # Diferencia en semanas
    dias_diferencia = (fecha_fin - fecha_inicio).days
    semanas_calculadas = max(22, dias_diferencia // 7 + 1)
    
    # Crear horario general
    nuevo_horario = HorarioGeneral(
        titulo=data['titulo'],
        año_academico=data['año_academico'],
        semestre=data['semestre'],
        año_carrera=data['año_carrera'],
        carrera=data.get('carrera', 'INGENIERÍA INFORMÁTICA'),
        modalidad=data.get('modalidad', 'Diurno'),
        semanas_totales=data.get('semanas_totales', semanas_calculadas),
        semanas_clases=data.get('semanas_clases', semanas_calculadas - 3),
        semanas_examenes=data.get('semanas_examenes', 3),
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        creado_por=current_user.id
    )
    
    try:
        db.session.add(nuevo_horario)
        db.session.commit()
        
        # Crear estructura vacía de semanas
        semanas_totales = nuevo_horario.semanas_totales
        turnos = Turno.query.filter_by(activo=True).order_by(Turno.seccion, Turno.orden).all()
        
        # Calcular fechas para cada semana
        slots_creados = 0
        for semana in range(1, semanas_totales + 1):
            es_examen = (semana > semanas_totales - nuevo_horario.semanas_examenes)
            
            # Para cada día (Lunes a Viernes)
            for dia in range(5):  # 0=Lunes, 1=Martes, ..., 4=Viernes
                # Calcular fecha específica
                dias_a_sumar = (semana - 1) * 7 + dia
                fecha_especifica = fecha_inicio + timedelta(days=dias_a_sumar)
                
                # Para cada turno
                for turno in turnos:
                    slot = HorarioSemanal(
                        horario_general_id=nuevo_horario.id,
                        semana_numero=semana,
                        dia_semana=dia,
                        turno_id=turno.id,
                        es_examen=es_examen,
                        fecha_especifica=fecha_especifica
                    )
                    db.session.add(slot)
                    slots_creados += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'id': nuevo_horario.id,
            'message': f'Horario creado con {slots_creados} slots vacíos',
            'horario': nuevo_horario.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/horarios/<int:id>/asignar', methods=['POST'])
@login_required
def asignar_asignatura(id):
    """Asignar una asignatura a un slot específico (drag & drop)"""
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    data = request.get_json()
    
    # Validaciones
    required_fields = ['semana_numero', 'dia_semana', 'turno_id', 'asignatura_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Faltan campos requeridos'}), 400
    
    # Buscar el slot
    slot = HorarioSemanal.query.filter_by(
        horario_general_id=id,
        semana_numero=data['semana_numero'],
        dia_semana=data['dia_semana'],
        turno_id=data['turno_id']
    ).first()
    
    if not slot:
        return jsonify({'error': 'Slot no encontrado'}), 404
    
    # Si se quiere limpiar el slot (asignatura_id = null)
    if data.get('asignatura_id') is None:
        slot.asignatura_id = None
        slot.profesor_id = None
        slot.color = None
        
        try:
            db.session.commit()
            return jsonify({
                'success': True,
                'slot': slot.to_dict()
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    # Obtener asignatura
    asignatura = Asignatura.query.get(data['asignatura_id'])
    if not asignatura:
        return jsonify({'error': 'Asignatura no encontrada'}), 404
    
    # Validación 1: Verificar que el profesor no tenga conflicto en el mismo turno
    if asignatura.profesor_id:
        conflicto = HorarioSemanal.query.filter(
            HorarioSemanal.horario_general_id == id,
            HorarioSemanal.semana_numero == data['semana_numero'],
            HorarioSemanal.dia_semana == data['dia_semana'],
            HorarioSemanal.turno_id == data['turno_id'],
            HorarioSemanal.profesor_id == asignatura.profesor_id,
            HorarioSemanal.id != slot.id
        ).first()
        
        if conflicto:
            conflicto_info = "No especificado"
            if conflicto.asignatura:
                conflicto_info = conflicto.asignatura.nombre
            
            return jsonify({
                'error': 'Conflicto de profesor',
                'message': f'El profesor {asignatura.profesor_rel.nombres} ya tiene clase en este turno ({conflicto_info})'
            }), 400
    
    # Validación 2: Verificar horas máximas de la asignatura (3 horas = 2 turnos máximo por semana)
    if asignatura.horas_presenciales > 0:
        # Contar cuántos turnos ya tiene asignados esta asignatura en esta semana
        turnos_asignados = HorarioSemanal.query.filter(
            HorarioSemanal.horario_general_id == id,
            HorarioSemanal.semana_numero == data['semana_numero'],
            HorarioSemanal.asignatura_id == asignatura.id
        ).count()
        
        # Convertir horas a turnos (cada turno = 1.5 horas, mínimo 1 turno)
        turnos_permitidos = max(1, min(5, asignatura.horas_presenciales // 1.5))
        
        if turnos_asignados >= turnos_permitidos:
            return jsonify({
                'error': 'Límite de horas',
                'message': f'Esta asignatura ya tiene {turnos_asignados} turnos asignados esta semana (máximo permitido: {turnos_permitidos} turnos = {asignatura.horas_presenciales} horas)'
            }), 400
    
    # Validación 3: Verificar que la asignatura sea del mismo año y semestre
    horario = HorarioGeneral.query.get(id)
    if asignatura.año_academico != horario.año_carrera or asignatura.periodo != horario.semestre:
        return jsonify({
            'error': 'Asignatura no corresponde',
            'message': f'Esta asignatura es del año {asignatura.año_academico} semestre {asignatura.periodo}, pero el horario es del año {horario.año_carrera} semestre {horario.semestre}'
        }), 400
    
    # Si todo está bien, asignar
    slot.asignatura_id = asignatura.id
    slot.profesor_id = asignatura.profesor_id
    slot.color = asignatura.color
    
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'slot': slot.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/horarios/<int:id>/limpiar-slot', methods=['POST'])
@login_required
def limpiar_slot(id):
    """Limpiar un slot específico"""
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    data = request.get_json()
    
    slot = HorarioSemanal.query.filter_by(
        horario_general_id=id,
        semana_numero=data['semana_numero'],
        dia_semana=data['dia_semana'],
        turno_id=data['turno_id']
    ).first()
    
    if not slot:
        return jsonify({'error': 'Slot no encontrado'}), 404
    
    slot.asignatura_id = None
    slot.profesor_id = None
    slot.color = None
    
    try:
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/horarios/<int:id>/limpiar-todo', methods=['POST'])
@login_required
def limpiar_todo_horario(id):
    """Limpiar todas las asignaciones de un horario"""
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    try:
        HorarioSemanal.query.filter_by(horario_general_id=id).update({
            'asignatura_id': None,
            'profesor_id': None,
            'color': None
        })
        db.session.commit()
        return jsonify({'success': True, 'message': 'Horario limpiado completamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/horarios/<int:id>/generar-automatico', methods=['POST'])
@login_required
def generar_horario_automatico(id):
    """Generar horario automáticamente - SOLO MAÑANAS, NO VIERNES, NO EXÁMENES"""
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    from collections import defaultdict
    
    print(f"\n🎯 INICIANDO GENERACIÓN AUTOMÁTICA INTELIGENTE")
    
    # Obtener horario
    horario = HorarioGeneral.query.get_or_404(id)
    
    # Obtener asignaturas para este año y semestre
    asignaturas = Asignatura.query.filter_by(
        año_academico=horario.año_carrera,
        periodo=horario.semestre
    ).all()
    
    if not asignaturas:
        return jsonify({'error': 'No hay asignaturas para este año y semestre'}), 400
    
    # Obtener SOLO turnos de la MAÑANA
    turnos_mañana = Turno.query.filter_by(seccion="mañana").order_by(Turno.orden).all()
    
    if not turnos_mañana:
        return jsonify({'error': 'No hay turnos de mañana configurados'}), 400
    
    # Calcular semanas válidas (NO EXÁMENES)
    semanas_totales = horario.semanas_totales
    semanas_examenes = horario.semanas_examenes
    semanas_clases = semanas_totales - semanas_examenes
    
    print(f"📊 ESTADÍSTICAS INICIALES:")
    print(f"   • Asignaturas disponibles: {len(asignaturas)}")
    print(f"   • Semanas de clase: {semanas_clases}")
    print(f"   • Turnos mañana/día: {len(turnos_mañana)}")
    print(f"   • Días/semana (Lun-Jue): 4")
    
    # Limpiar SOLO slots de mañana, lunes a jueves, semanas de clase
    slots_a_limpiar = db.session.query(HorarioSemanal).join(Turno).filter(
        HorarioSemanal.horario_general_id == id,
        HorarioSemanal.dia_semana.in_([0, 1, 2, 3]),  # Solo Lunes(0) a Jueves(3)
        HorarioSemanal.semana_numero <= semanas_clases,  # Solo semanas de clase
        Turno.seccion == "mañana"
    ).all()
    
    for slot in slots_a_limpiar:
        slot.asignatura_id = None
        slot.profesor_id = None
        slot.color = None
    
    db.session.commit()
    print(f"🧹 Limpiados {len(slots_a_limpiar)} slots de mañana (Lun-Jue)")
    
    # ========== ALGORITMO INTELIGENTE ==========
    # 1. CALCULAR NECESIDADES REALES
    total_horas_semestrales = 0
    total_turnos_necesarios = 0
    asignaturas_con_info = []
    
    for asignatura in asignaturas:
        # Cada asignatura necesita (horas_presenciales / 1.5) turnos por SEMANA
        turnos_por_semana = max(1, math.ceil(asignatura.horas_presenciales / 1.5))
        
        # Limitar a máximo 2 turnos por semana por asignatura
        turnos_por_semana = min(turnos_por_semana, 2)
        
        # Total de turnos necesarios para el semestre
        turnos_totales = turnos_por_semana * semanas_clases
        
        # Limitar a un máximo total por asignatura
        turnos_totales = min(turnos_totales, 30)
        
        asignaturas_con_info.append({
            'id': asignatura.id,
            'codigo': asignatura.codigo,
            'nombre': asignatura.nombre,
            'horas_presenciales': asignatura.horas_presenciales,
            'profesor_id': asignatura.profesor_id,
            'color': asignatura.color,
            'turnos_por_semana': turnos_por_semana,
            'turnos_totales_necesarios': turnos_totales,
            'turnos_asignados': 0,
            'prioridad': asignatura.horas_presenciales  # Más horas = más prioridad
        })
        
        total_horas_semestrales += asignatura.horas_presenciales * semanas_clases
        total_turnos_necesarios += turnos_totales
    
    print(f"\n📈 CÁLCULO DE NECESIDADES:")
    print(f"   • Horas semestrales totales: {total_horas_semestrales}")
    print(f"   • Turnos necesarios totales: {total_turnos_necesarios}")
    
    # Calcular capacidad del sistema
    slots_disponibles = semanas_clases * 4 * len(turnos_mañana)  # semanas * días(Lun-Jue) * turnos_mañana
    print(f"   • Slots disponibles (Lun-Jue, mañana): {slots_disponibles}")
    
    # 2. ORDENAR POR PRIORIDAD (más horas primero)
    asignaturas_con_info.sort(key=lambda x: x['prioridad'], reverse=True)
    
    # 3. ASIGNACIÓN INTELIGENTE
    estadisticas = {
        'asignaturas_procesadas': 0,
        'turnos_asignados': 0,
        'intentos_fallidos': 0,
        'conflictos_profesor': 0,
        'slots_ocupados_por_dia': defaultdict(int),
        'slots_ocupados_por_semana': defaultdict(int)
    }
    
    # Control de profesores
    horario_profesor = defaultdict(set)  # {profesor_id: {(semana, dia, turno_id)}}
    
    print(f"\n🚀 INICIANDO ASIGNACIÓN...")
    
    # Para cada asignatura (por prioridad)
    for asig_info in asignaturas_con_info:
        if asig_info['turnos_asignados'] >= asig_info['turnos_totales_necesarios']:
            continue
        
        print(f"  📘 Procesando {asig_info['codigo']} ({asig_info['horas_presenciales']}h/semana)")
        
        # Intentar asignar los turnos que faltan
        turnos_faltantes = asig_info['turnos_totales_necesarios'] - asig_info['turnos_asignados']
        intentos = 0
        max_intentos = turnos_faltantes * 50  # Intentos proporcionales
        
        while turnos_faltantes > 0 and intentos < max_intentos:
            # Seleccionar semana aleatoria (solo semanas de clase)
            semana = random.randint(1, semanas_clases)
            
            # Seleccionar día: SOLO Lunes(0), Martes(1), Miércoles(2), Jueves(3)
            dia = random.randint(0, 3)
            
            # Seleccionar turno de mañana
            turno = random.choice(turnos_mañana)
            
            # Verificar si ya hay demasiados slots ocupados este día en esta semana
            if estadisticas['slots_ocupados_por_dia'][(semana, dia)] >= len(turnos_mañana) * 0.8:
                intentos += 1
                estadisticas['intentos_fallidos'] += 1
                continue
            
            # Buscar el slot
            slot = HorarioSemanal.query.filter_by(
                horario_general_id=id,
                semana_numero=semana,
                dia_semana=dia,
                turno_id=turno.id
            ).first()
            
            # Verificar slot válido
            if not slot or slot.asignatura_id or slot.es_examen:
                intentos += 1
                estadisticas['intentos_fallidos'] += 1
                continue
            
            # Verificar conflicto de profesor
            conflicto_profesor = False
            if asig_info['profesor_id']:
                clave_profesor = (semana, dia, turno.id)
                if clave_profesor in horario_profesor[asig_info['profesor_id']]:
                    intentos += 1
                    estadisticas['conflictos_profesor'] += 1
                    conflicto_profesor = True
                    continue
            
            # Verificar que la asignatura no tenga ya 2 turnos esta semana
            turnos_asig_esta_semana = HorarioSemanal.query.filter_by(
                horario_general_id=id,
                semana_numero=semana,
                asignatura_id=asig_info['id']
            ).count()
            
            if turnos_asig_esta_semana >= 2:  # Máximo 2 turnos por semana
                intentos += 1
                estadisticas['intentos_fallidos'] += 1
                continue
            
            # ¡ASIGNAR!
            slot.asignatura_id = asig_info['id']
            slot.profesor_id = asig_info['profesor_id']
            slot.color = asig_info['color']
            
            # Actualizar contadores
            asig_info['turnos_asignados'] += 1
            turnos_faltantes -= 1
            estadisticas['turnos_asignados'] += 1
            
            # Registrar en estadísticas
            estadisticas['slots_ocupados_por_dia'][(semana, dia)] += 1
            estadisticas['slots_ocupados_por_semana'][semana] += 1
            
            if asig_info['profesor_id']:
                horario_profesor[asig_info['profesor_id']].add((semana, dia, turno.id))
            
            # Commit periódico
            if estadisticas['turnos_asignados'] % 20 == 0:
                db.session.commit()
            
            print(f"    ✅ S{semana:02d} {['Lun','Mar','Mié','Jue'][dia]} {turno.nombre}")
            
            # Reiniciar contador de intentos si tuvo éxito
            intentos = 0
        
        estadisticas['asignaturas_procesadas'] += 1
        
        # Si no pudo asignar todos los turnos, continuar con la siguiente asignatura
        if turnos_faltantes > 0:
            print(f"    ⚠️  Solo asignó {asig_info['turnos_asignados']}/{asig_info['turnos_totales_necesarios']} turnos")
    
    # Commit final
    db.session.commit()
    
    print(f"\n✅ GENERACIÓN COMPLETADA")
    print(f"   • Turnos asignados: {estadisticas['turnos_asignados']}")
    print(f"   • Intentos fallidos: {estadisticas['intentos_fallidos']}")
    print(f"   • Conflictos profesor: {estadisticas['conflictos_profesor']}")
    
    # Calcular estadísticas finales
    porcentaje_ocupacion = (estadisticas['turnos_asignados'] / slots_disponibles * 100) if slots_disponibles > 0 else 0
    
    # Distribución por día
    distribucion_dia = {}
    dias_nombres = ['Lunes', 'Martes', 'Miércoles', 'Jueves']
    for dia in range(4):
        total_este_dia = sum(estadisticas['slots_ocupados_por_dia'].get((semana, dia), 0) 
                           for semana in range(1, semanas_clases + 1))
        distribucion_dia[dias_nombres[dia]] = total_este_dia
    
    return jsonify({
        'success': True,
        'message': f'✅ Horario generado automáticamente: {estadisticas["turnos_asignados"]} turnos asignados ({porcentaje_ocupacion:.1f}% de ocupación)',
        'estadisticas_detalladas': {
            'asignaturas_procesadas': estadisticas['asignaturas_procesadas'],
            'turnos_asignados': estadisticas['turnos_asignados'],
            'intentos_fallidos': estadisticas['intentos_fallidos'],
            'conflictos_profesor': estadisticas['conflictos_profesor'],
            'porcentaje_ocupacion': round(porcentaje_ocupacion, 1),
            'slots_disponibles': slots_disponibles,
            'distribucion_por_dia': distribucion_dia
        },
        'resumen_asignaturas': [{
            'codigo': a['codigo'],
            'horas_semana': a['horas_presenciales'],
            'turnos_necesarios': a['turnos_totales_necesarios'],
            'turnos_asignados': a['turnos_asignados']
        } for a in asignaturas_con_info]
    })

@app.route('/api/horarios/<int:id>/exportar', methods=['GET'])
@login_required
def exportar_horario(id):
    """Exportar horario a formato estructurado"""
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    horario = HorarioGeneral.query.get_or_404(id)
    
    # Obtener todas las asignaciones organizadas por semana
    asignaciones = HorarioSemanal.query.filter_by(
        horario_general_id=id
    ).order_by(
        HorarioSemanal.semana_numero,
        HorarioSemanal.dia_semana,
        HorarioSemanal.turno_id
    ).all()
    
    # Estructurar datos
    semanas_estructuradas = {}
    for slot in asignaciones:
        semana_num = slot.semana_numero
        if semana_num not in semanas_estructuradas:
            semanas_estructuradas[semana_num] = {
                'numero': semana_num,
                'es_examen': slot.es_examen,
                'fecha_inicio': None,
                'fecha_fin': None,
                'dias': {}
            }
        
        # Organizar por día
        dia_nombre = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'][slot.dia_semana]
        if dia_nombre not in semanas_estructuradas[semana_num]['dias']:
            semanas_estructuradas[semana_num]['dias'][dia_nombre] = {
                'turnos': {},
                'fecha': slot.fecha_especifica.isoformat() if slot.fecha_especifica else None
            }
        
        # Agregar turno
        turno_key = f"{slot.turno.nombre} ({slot.turno.hora_inicio}-{slot.turno.hora_fin})"
        semanas_estructuradas[semana_num]['dias'][dia_nombre]['turnos'][turno_key] = {
            'asignatura': slot.asignatura.nombre if slot.asignatura else None,
            'profesor': f"{slot.profesor.nombres} {slot.profesor.apellidos}" if slot.profesor else None,
            'color': slot.color
        }
    
    # Convertir a lista
    semanas_lista = []
    for semana_num in sorted(semanas_estructuradas.keys()):
        semana_data = semanas_estructuradas[semana_num]
        semanas_lista.append(semana_data)
    
    return jsonify({
        'horario': horario.to_dict(),
        'semanas': semanas_lista,
        'total_slots': len(asignaciones),
        'slots_ocupados': len([s for s in asignaciones if s.asignatura_id])
    })

@app.route('/api/horarios/<int:id>/estadisticas', methods=['GET'])
@login_required
def estadisticas_horario(id):
    """Obtener estadísticas del horario - VERSIÓN MEJORADA"""
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    # Contar slots
    total_slots = HorarioSemanal.query.filter_by(horario_general_id=id).count()
    slots_ocupados = HorarioSemanal.query.filter_by(
        horario_general_id=id
    ).filter(HorarioSemanal.asignatura_id.isnot(None)).count()
    
    # Obtener asignaturas únicas
    asignaturas_unicas = db.session.query(HorarioSemanal.asignatura_id).filter(
        HorarioSemanal.horario_general_id == id,
        HorarioSemanal.asignatura_id.isnot(None)
    ).distinct().count()
    
    # Obtener profesores únicos
    profesores_unicos = db.session.query(HorarioSemanal.profesor_id).filter(
        HorarioSemanal.horario_general_id == id,
        HorarioSemanal.profesor_id.isnot(None)
    ).distinct().count()
    
    # Detectar conflictos de profesor (versión optimizada)
    conflictos_detectados = 0
    if slots_ocupados > 0:
        # Buscar profesores con múltiples asignaciones en mismo horario
        subquery = db.session.query(
            HorarioSemanal.semana_numero,
            HorarioSemanal.dia_semana,
            HorarioSemanal.turno_id,
            HorarioSemanal.profesor_id
        ).filter(
            HorarioSemanal.horario_general_id == id,
            HorarioSemanal.profesor_id.isnot(None)
        ).group_by(
            HorarioSemanal.semana_numero,
            HorarioSemanal.dia_semana,
            HorarioSemanal.turno_id,
            HorarioSemanal.profesor_id
        ).having(db.func.count() > 1).subquery()
        
        conflictos_detectados = db.session.query(subquery).count()
    
    return jsonify({
        'total_slots': total_slots,
        'slots_ocupados': slots_ocupados,
        'porcentaje_ocupado': round((slots_ocupados / total_slots * 100) if total_slots > 0 else 0, 2),
        'asignaturas_unicas': asignaturas_unicas,
        'profesores_unicos': profesores_unicos,
        'conflictos_detectados': conflictos_detectados,
        'slots_por_semana': total_slots // 22 if total_slots > 0 else 0
    })

@app.route('/api/horarios/<int:id>/exportar-excel', methods=['GET'])
@login_required
def exportar_horario_excel(id):
    """Exportar horario a Excel"""
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    horario = HorarioGeneral.query.get_or_404(id)
    
    # Obtener todas las asignaciones
    asignaciones = HorarioSemanal.query.filter_by(
        horario_general_id=id
    ).order_by(
        HorarioSemanal.semana_numero,
        HorarioSemanal.dia_semana,
        HorarioSemanal.turno_id
    ).all()
    
    # Crear DataFrame
    data = []
    for slot in asignaciones:
        if slot.asignatura:
            data.append({
                'Semana': slot.semana_numero,
                'Día': ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'][slot.dia_semana],
                'Turno': slot.turno.nombre if slot.turno else '',
                'Hora': f"{slot.turno.hora_inicio if slot.turno else ''} - {slot.turno.hora_fin if slot.turno else ''}",
                'Código': slot.asignatura.codigo if slot.asignatura else '',
                'Asignatura': slot.asignatura.nombre if slot.asignatura else '',
                'Profesor': f"{slot.profesor.nombres} {slot.profesor.apellidos}" if slot.profesor else '',
                'Horas': slot.asignatura.horas_presenciales if slot.asignatura else '',
                'Tipo': 'EXAMEN' if slot.es_examen else 'CLASE'
            })
    
    if not data:
        return jsonify({'error': 'No hay datos para exportar'}), 400
    
    df = pd.DataFrame(data)
    
    # Crear archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Horario', index=False)
        
        # Ajustar anchos de columna
        worksheet = writer.sheets['Horario']
        for column in worksheet.columns:
            max_length = 0
            column = [cell for cell in column]
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 30)
            worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
    
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'horario_{horario.año_academico}_sem{horario.semestre}_año{horario.año_carrera}.xlsx'
    )

@app.route('/api/horarios/<int:id>/vista-semestral', methods=['GET'])
@login_required
def vista_semestral_horario(id):
    """Generar vista semestral completa del horario"""
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    horario = HorarioGeneral.query.get_or_404(id)
    
    # Estructurar datos por semana
    semanas_data = {}
    for semana in range(1, horario.semanas_totales + 1):
        es_examen = (semana > horario.semanas_totales - horario.semanas_examenes)
        
        semana_data = {
            'numero': semana,
            'es_examen': es_examen,
            'dias': {}
        }
        
        # Para cada día de la semana
        for dia in range(5):
            dia_nombre = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'][dia]
            semana_data['dias'][dia_nombre] = {
                'turnos': {}
            }
            
            # Para cada turno
            turnos = Turno.query.order_by(Turno.seccion, Turno.orden).all()
            for turno in turnos:
                # Buscar asignación
                asignacion = HorarioSemanal.query.filter_by(
                    horario_general_id=id,
                    semana_numero=semana,
                    dia_semana=dia,
                    turno_id=turno.id
                ).first()
                
                if asignacion and asignacion.asignatura:
                    semana_data['dias'][dia_nombre]['turnos'][turno.nombre] = {
                        'codigo': asignacion.asignatura.codigo,
                        'asignatura': asignacion.asignatura.nombre,
                        'profesor': f"{asignacion.profesor.nombres} {asignacion.profesor.apellidos}" if asignacion.profesor else '',
                        'color': asignacion.color
                    }
        
        semanas_data[f'Semana {semana}'] = semana_data
    
    return jsonify({
        'horario': horario.to_dict(),
        'semanas': semanas_data,
        'total_semanas': horario.semanas_totales,
        'semanas_clases': horario.semanas_clases,
        'semanas_examenes': horario.semanas_examenes
    })

@app.route('/api/horarios/<int:id>/vista-semestral-detallada', methods=['GET'])
@login_required
def vista_semestral_detallada(id):
    """Vista semestral detallada con formato de tabla"""
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    from datetime import timedelta
    
    horario = HorarioGeneral.query.get_or_404(id)
    
    # Obtener todos los turnos ordenados
    turnos = Turno.query.order_by(Turno.seccion, Turno.orden).all()
    
    # Obtener todas las asignaciones
    asignaciones = HorarioSemanal.query.filter_by(
        horario_general_id=id
    ).order_by(
        HorarioSemanal.semana_numero,
        HorarioSemanal.dia_semana,
        HorarioSemanal.turno_id
    ).all()
    
    # Organizar datos por semana
    semanas_data = []
    
    for semana_num in range(1, horario.semanas_totales + 1):
        es_examen = semana_num > horario.semanas_totales - horario.semanas_examenes
        
        # Calcular fechas de la semana (Lunes a Viernes)
        fecha_lunes = horario.fecha_inicio + timedelta(days=(semana_num - 1) * 7)
        fecha_viernes = fecha_lunes + timedelta(days=4)
        
        # Buscar fecha específica si existe en algún slot
        slot_lunes = next((a for a in asignaciones if a.semana_numero == semana_num and a.dia_semana == 0), None)
        if slot_lunes and slot_lunes.fecha_especifica:
            fecha_lunes = slot_lunes.fecha_especifica
            fecha_viernes = fecha_lunes + timedelta(days=4)
        
        semana_info = {
            'numero': semana_num,
            'es_examen': es_examen,
            'fecha_lunes': fecha_lunes.strftime('%d/%m/%Y'),
            'fecha_viernes': fecha_viernes.strftime('%d/%m/%Y'),
            'rango_fechas': f"{fecha_lunes.strftime('%d/%m/%Y')} - {fecha_viernes.strftime('%d/%m/%Y')}",
            'turnos': []
        }
        
        # Para cada turno
        for turno in turnos:
            turno_info = {
                'id': turno.id,
                'nombre': turno.nombre,
                'hora_inicio': turno.hora_inicio,
                'hora_fin': turno.hora_fin,
                'seccion': turno.seccion,
                'dias': {}
            }
            
            # Para cada día (Lunes a Viernes)
            dias_nombres = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
            for dia_num, dia_nombre in enumerate(dias_nombres):
                # Buscar asignación para este slot específico
                asignacion = next((a for a in asignaciones if 
                                 a.semana_numero == semana_num and 
                                 a.dia_semana == dia_num and 
                                 a.turno_id == turno.id), None)
                
                if asignacion and asignacion.asignatura:
                    turno_info['dias'][dia_nombre] = {
                        'asignatura_id': asignacion.asignatura_id,
                        'codigo': asignacion.asignatura.codigo,
                        'nombre': asignacion.asignatura.nombre,
                        'profesor': f"{asignacion.profesor.nombres} {asignacion.profesor.apellidos}" if asignacion.profesor else None,
                        'color': asignacion.color,
                        'ocupado': True
                    }
                else:
                    turno_info['dias'][dia_nombre] = {
                        'ocupado': False,
                        'es_viernes': dia_nombre == 'Viernes',
                        'es_examen': es_examen
                    }
            
            semana_info['turnos'].append(turno_info)
        
        semanas_data.append(semana_info)
    
    return jsonify({
        'success': True,
        'horario': horario.to_dict(),
        'semanas': semanas_data,
        'total_semanas': horario.semanas_totales,
        'semanas_clases': horario.semanas_clases,
        'semanas_examenes': horario.semanas_examenes,
        'turnos': [t.to_dict() for t in turnos]
    })

@app.route('/api/horarios/<int:id>/actualizar-fecha-semana', methods=['POST'])
@login_required
def actualizar_fecha_semana(id):
    """Actualizar fecha de inicio de una semana específica"""
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    data = request.get_json()
    
    required_fields = ['semana_numero', 'fecha_inicio']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Faltan campos requeridos'}), 400
    
    try:
        semana_numero = int(data['semana_numero'])
        fecha_inicio = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date()
        
        # Obtener horario
        horario = HorarioGeneral.query.get_or_404(id)
        
        # Actualizar todas las fechas de esa semana
        asignaciones_semana = HorarioSemanal.query.filter_by(
            horario_general_id=id,
            semana_numero=semana_numero
        ).all()
        
        for slot in asignaciones_semana:
            dias_a_sumar = slot.dia_semana
            slot.fecha_especifica = fecha_inicio + timedelta(days=dias_a_sumar)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Fechas de la semana {semana_numero} actualizadas correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/horarios/<int:id>', methods=['DELETE'])
@login_required
def eliminar_horario(id):
    """Eliminar un horario completo"""
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    horario = HorarioGeneral.query.get_or_404(id)
    
    try:
        # Eliminar primero las asignaciones semanales
        HorarioSemanal.query.filter_by(horario_general_id=id).delete()
        # Eliminar el horario general
        db.session.delete(horario)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Horario eliminado correctamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ========== RUTAS PARA ESTADÍSTICAS ==========

@app.route('/api/estadisticas')
@login_required
def get_estadisticas():
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    total_asignaturas = Asignatura.query.count()
    total_profesores = Profesor.query.count()
    total_turnos = Turno.query.count()
    total_horarios = HorarioGeneral.query.count()
    
    return jsonify({
        'asignaturas': total_asignaturas,
        'profesores': total_profesores,
        'turnos': total_turnos,
        'horarios': total_horarios
    })

@app.route('/api/status')
def api_status():
    return jsonify({
        'status': 'ok',
        'message': 'Sistema de Horarios funcionando',
        'version': '2.0.0',
        'modulos': ['autenticacion', 'asignaturas', 'profesores', 'turnos', 'horarios_drag_drop']
    })

# ========== PÁGINAS DE ADMIN ==========

@app.route('/admin/asignaturas')
@login_required
def admin_asignaturas():
    if current_user.role != 'admin':
        return redirect(url_for('dashboard'))
    return render_template('admin/asignaturas.html')

@app.route('/admin/profesores')
@login_required
def admin_profesores():
    if current_user.role != 'admin':
        return redirect(url_for('dashboard'))
    return render_template('admin/profesores.html')

@app.route('/admin/horarios')
@login_required
def admin_horarios():
    """Página principal de gestión de horarios"""
    if current_user.role != 'admin':
        return redirect(url_for('dashboard'))
    return render_template('admin/horarios.html')

@app.route('/admin/horarios/crear')
@login_required
def admin_crear_horario():
    """Página para crear nuevo horario"""
    if current_user.role != 'admin':
        return redirect(url_for('dashboard'))
    return render_template('admin/crear_horario.html')

@app.route('/admin/horarios/editar/<int:id>')
@login_required
def admin_editar_horario(id):
    """Página de editor drag & drop para horario específico"""
    if current_user.role != 'admin':
        return redirect(url_for('admin_horarios'))
    
    horario = HorarioGeneral.query.get(id)
    if not horario:
        return redirect(url_for('admin_horarios'))
    
    return render_template('admin/editar_horario.html', horario_id=id)

@app.route('/admin/turnos')
@login_required
def admin_turnos_page():
    if current_user.role != 'admin':
        return redirect(url_for('dashboard'))
    return render_template('admin/turnos.html')

# ========== CAMBIO DE CONTRASEÑA ==========

@app.route('/api/cambiar-password', methods=['POST'])
@login_required
def cambiar_password():
    """Permite al usuario autenticado cambiar su propia contraseña"""
    data = request.get_json()

    if not data or not all(k in data for k in ['password_actual', 'password_nuevo', 'password_confirmar']):
        return jsonify({'error': 'Faltan campos requeridos'}), 400

    if not check_password_hash(current_user.password, data['password_actual']):
        return jsonify({'error': 'La contraseña actual es incorrecta'}), 400

    if data['password_nuevo'] != data['password_confirmar']:
        return jsonify({'error': 'Las contraseñas nuevas no coinciden'}), 400

    if len(data['password_nuevo']) < 6:
        return jsonify({'error': 'La contraseña debe tener al menos 6 caracteres'}), 400

    try:
        current_user.password = generate_password_hash(data['password_nuevo'])
        db.session.commit()
        return jsonify({'success': True, 'message': 'Contraseña actualizada correctamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ========== GESTIÓN DE USUARIOS (ADMIN) ==========

@app.route('/api/admin/usuarios', methods=['GET'])
@login_required
def listar_usuarios():
    """Listar todos los usuarios (solo admin)"""
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403

    usuarios = Usuario.query.order_by(Usuario.fecha_registro.desc()).all()
    return jsonify([{
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'role': u.role,
        'activo': u.activo,
        'fecha_registro': u.fecha_registro.strftime('%d/%m/%Y %H:%M') if u.fecha_registro else None
    } for u in usuarios])

@app.route('/api/admin/usuarios', methods=['POST'])
@login_required
def crear_usuario():
    """Crear un nuevo usuario (solo admin)"""
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403

    data = request.get_json()

    if not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'error': 'Faltan campos requeridos'}), 400

    if len(data['password']) < 6:
        return jsonify({'error': 'La contraseña debe tener al menos 6 caracteres'}), 400

    if Usuario.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'El nombre de usuario ya existe'}), 400

    if Usuario.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'El email ya está registrado'}), 400

    # Solo admin puede asignar rol admin
    role = data.get('role', 'user')
    if role not in ['admin', 'user']:
        role = 'user'

    try:
        nuevo = Usuario(
            username=data['username'],
            email=data['email'],
            password=generate_password_hash(data['password']),
            role=role,
            activo=True
        )
        db.session.add(nuevo)
        db.session.commit()
        return jsonify({'success': True, 'id': nuevo.id, 'message': f'Usuario {nuevo.username} creado correctamente'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/usuarios/<int:id>', methods=['PUT'])
@login_required
def editar_usuario(id):
    """Editar un usuario (solo admin)"""
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403

    usuario = Usuario.query.get_or_404(id)
    data = request.get_json()

    if 'username' in data and data['username'] != usuario.username:
        if Usuario.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'El nombre de usuario ya existe'}), 400
        usuario.username = data['username']

    if 'email' in data and data['email'] != usuario.email:
        if Usuario.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'El email ya está registrado'}), 400
        usuario.email = data['email']

    if 'role' in data and data['role'] in ['admin', 'user']:
        # No permitir que el admin se quite su propio rol
        if usuario.id == current_user.id and data['role'] != 'admin':
            return jsonify({'error': 'No puedes cambiar tu propio rol'}), 400
        usuario.role = data['role']

    if 'activo' in data:
        # No permitir que el admin se desactive a sí mismo
        if usuario.id == current_user.id and not data['activo']:
            return jsonify({'error': 'No puedes desactivar tu propia cuenta'}), 400
        usuario.activo = data['activo']

    if 'password' in data and data['password']:
        if len(data['password']) < 6:
            return jsonify({'error': 'La contraseña debe tener al menos 6 caracteres'}), 400
        usuario.password = generate_password_hash(data['password'])

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Usuario actualizado correctamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/usuarios/<int:id>', methods=['DELETE'])
@login_required
def eliminar_usuario(id):
    """Eliminar un usuario (solo admin)"""
    if current_user.role != 'admin':
        return jsonify({'error': 'No autorizado'}), 403

    if id == current_user.id:
        return jsonify({'error': 'No puedes eliminar tu propia cuenta'}), 400

    usuario = Usuario.query.get_or_404(id)

    try:
        db.session.delete(usuario)
        db.session.commit()
        return jsonify({'success': True, 'message': f'Usuario {usuario.username} eliminado'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/admin/usuarios')
@login_required
def admin_usuarios_page():
    """Página de gestión de usuarios"""
    if current_user.role != 'admin':
        return redirect(url_for('dashboard'))
    return render_template('admin/usuarios.html')

# ========== REGISTRO PÚBLICO ==========

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    """Formulario de registro público — solo crea usuarios con rol 'user'"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        data = request.get_json()

        if not all(k in data for k in ['username', 'email', 'password']):
            return jsonify({'error': 'Faltan campos requeridos'}), 400

        if len(data['password']) < 6:
            return jsonify({'error': 'La contraseña debe tener al menos 6 caracteres'}), 400

        if Usuario.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'El nombre de usuario ya existe'}), 400

        if Usuario.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'El email ya está registrado'}), 400

        try:
            nuevo = Usuario(
                username=data['username'],
                email=data['email'],
                password=generate_password_hash(data['password']),
                role='user',
                activo=True
            )
            db.session.add(nuevo)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Cuenta creada correctamente'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    return render_template('registro.html')

# ========== INICIALIZACIÓN ==========

def inicializar_base_datos():
    """Inicializar BD y crear datos por defecto"""
    with app.app_context():
        # Crear todas las tablas (incluyendo las nuevas)
        db.create_all()
        
        # Crear turnos por defecto si no existen
        if Turno.query.count() == 0:
            turnos = [
                # Mañana
                Turno(nombre="Mañana 1", hora_inicio="08:15", hora_fin="09:45", 
                      duracion_minutos=90, seccion="mañana", orden=1),
                Turno(nombre="Mañana 2", hora_inicio="09:50", hora_fin="11:20", 
                      duracion_minutos=90, seccion="mañana", orden=2),
                Turno(nombre="Mañana 3", hora_inicio="11:35", hora_fin="13:05", 
                      duracion_minutos=90, seccion="mañana", orden=3),
                # Tarde
                Turno(nombre="Tarde 1", hora_inicio="13:10", hora_fin="14:40", 
                      duracion_minutos=90, seccion="tarde", orden=4),
                Turno(nombre="Tarde 2", hora_inicio="14:45", hora_fin="16:15", 
                      duracion_minutos=90, seccion="tarde", orden=5),
                Turno(nombre="Tarde 3", hora_inicio="16:30", hora_fin="18:00", 
                      duracion_minutos=90, seccion="tarde", orden=6),
            ]
            db.session.bulk_save_objects(turnos)
            db.session.commit()
            print("✅ Turnos creados por defecto")
        
        # Crear usuario administrador por defecto si no existe
        if not Usuario.query.filter_by(username='admin').first():
            admin = Usuario(
                username='admin',
                email='admin@horarios.edu',
                password=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            
            # Crear usuario normal de prueba
            user = Usuario(
                username='user',
                email='user@horarios.edu',
                password=generate_password_hash('user123'),
                role='user'
            )
            db.session.add(user)
            
            db.session.commit()
            print("✅ Usuarios por defecto creados")
            print("   ⚠️  Credenciales iniciales (cámbialas después del primer acceso):")
            print("   👤 Admin:  admin / admin123")
            print("   👤 Normal: user / user123")
        
        print("✅ Base de datos lista")

# ========== RUTAS FALTANTES PARA NAVEGACIÓN ==========

@app.route('/admin/horarios/lista')
@login_required
def lista_horarios():
    """Lista de horarios (alternativa)"""
    if current_user.role != 'admin':
        return redirect(url_for('dashboard'))
    return render_template('admin/horarios.html')

@app.route('/admin/volver-dashboard')
@login_required
def volver_al_dashboard():
    """Ruta específica para el botón 'Volver al Dashboard' - NUEVA"""
    if current_user.role != 'admin':
        return redirect(url_for('dashboard'))
    return redirect(url_for('dashboard'))

# ========== RUTA PARA MANEJAR ERROR 404 ==========

@app.errorhandler(404)
def pagina_no_encontrada(error):
    """Manejar errores 404 de manera elegante"""
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# ========== EJECUCIÓN ==========

if __name__ == '__main__':
    inicializar_base_datos()
    debug_mode = os.environ.get('DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode, port=5000, host='0.0.0.0')