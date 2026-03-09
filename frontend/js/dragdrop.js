class HorarioDragDrop {
    constructor(containerId, horarioId) {
        this.container = document.getElementById(containerId);
        this.horarioId = horarioId;
        this.asignaturas = [];
        this.semanas = [];
        this.turnos = [];
        this.dragItem = null;
        
        this.init();
    }
    
    async init() {
        await this.cargarDatos();
        this.renderizarCalendario();
        this.configurarDragDrop();
    }
    
    async cargarDatos() {
        try {
            // Cargar asignaturas
            const asignaturasRes = await fetch('/api/asignaturas');
            this.asignaturas = await asignaturasRes.json();
            
            // Cargar horario
            const horarioRes = await fetch(`/api/horario/${this.horarioId}`);
            const data = await horarioRes.json();
            this.horario = data.horario;
            this.semanas = data.semanas;
            
            // Cargar turnos
            const turnosRes = await fetch('/api/turnos');
            this.turnos = await turnosRes.json();
            
        } catch (error) {
            console.error('Error cargando datos:', error);
        }
    }
    
    renderizarCalendario() {
        this.container.innerHTML = '';
        
        // Crear toolbar
        const toolbar = this.crearToolbar();
        this.container.appendChild(toolbar);
        
        // Crear selector de semanas
        const semanaSelector = this.crearSelectorSemanas();
        this.container.appendChild(semanaSelector);
        
        // Crear vista de calendario
        const calendario = this.crearCalendario();
        this.container.appendChild(calendario);
        
        // Crear panel de asignaturas
        const panelAsignaturas = this.crearPanelAsignaturas();
        this.container.appendChild(panelAsignaturas);
        
        // Crear panel de conflictos
        const panelConflictos = this.crearPanelConflictos();
        this.container.appendChild(panelConflictos);
    }
    
    crearToolbar() {
        const toolbar = document.createElement('div');
        toolbar.className = 'toolbar';
        
        toolbar.innerHTML = `
            <h3>${this.horario.nombre}</h3>
            <div class="toolbar-actions">
                <button class="btn-secondary" onclick="guardarHorario()">
                    <i class="fas fa-save"></i> Guardar
                </button>
                <button class="btn-secondary" onclick="generarDistribucionAutomatica()">
                    <i class="fas fa-robot"></i> Distribuir Automático
                </button>
                <button class="btn-secondary" onclick="limpiarHorario()">
                    <i class="fas fa-trash-alt"></i> Limpiar
                </button>
                <button class="btn-primary" onclick="exportarExcel()">
                    <i class="fas fa-file-excel"></i> Exportar Excel
                </button>
            </div>
        `;
        
        return toolbar;
    }
    
    crearSelectorSemanas() {
        const selector = document.createElement('div');
        selector.className = 'semana-selector';
        
        const semanasHTML = Array.from({length: this.horario.semanas_totales}, (_, i) => {
            const semana = i + 1;
            const tipo = semana <= this.horario.semanas_clases ? 'clases' : 'examenes';
            return `
                <div class="semana-item ${tipo}" onclick="mostrarSemana(${semana})">
                    <span>Sem ${semana}</span>
                    ${tipo === 'examenes' ? '<i class="fas fa-file-alt"></i>' : ''}
                </div>
            `;
        }).join('');
        
        selector.innerHTML = `
            <div class="selector-header">
                <h4>Navegación de Semanas</h4>
                <div class="semana-info">
                    <span class="badge clases">Clases: ${this.horario.semanas_clases}</span>
                    <span class="badge examenes">Exámenes: ${this.horario.semanas_examenes}</span>
                </div>
            </div>
            <div class="semanas-grid">
                ${semanasHTML}
            </div>
        `;
        
        return selector;
    }
    
    crearCalendario() {
        const calendario = document.createElement('div');
        calendario.className = 'calendario-horario';
        calendario.id = 'calendario-horario';
        
        // Filtrar solo semanas de clases para el calendario
        const semanasClases = Array.from(
            {length: this.horario.semanas_clases}, 
            (_, i) => i + 1
        );
        
        semanasClases.forEach(semana => {
            const semanaElement = this.crearSemana(semana);
            calendario.appendChild(semanaElement);
        });
        
        return calendario;
    }
    
    crearSemana(semana) {
        const semanaElement = document.createElement('div');
        semanaElement.className = 'semana-calendario';
        semanaElement.dataset.semana = semana;
        
        const header = document.createElement('div');
        header.className = 'semana-header';
        
        // Calcular fechas
        const fechaInicio = new Date(this.horario.fecha_inicio);
        const inicioSemana = new Date(fechaInicio);
        inicioSemana.setDate(fechaInicio.getDate() + (semana - 1) * 7);
        
        const finSemana = new Date(inicioSemana);
        finSemana.setDate(inicioSemana.getDate() + 4); // Solo lunes-viernes
        
        header.innerHTML = `
            <h4>Semana ${semana}</h4>
            <p>${inicioSemana.toLocaleDateString()} - ${finSemana.toLocaleDateString()}</p>
        `;
        
        semanaElement.appendChild(header);
        
        // Crear días de la semana
        const diasGrid = document.createElement('div');
        diasGrid.className = 'dias-grid';
        
        ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'].forEach((dia, index) => {
            const diaElement = this.crearDia(semana, index + 1, dia);
            diasGrid.appendChild(diaElement);
        });
        
        semanaElement.appendChild(diasGrid);
        
        return semanaElement;
    }
    
    crearDia(semana, diaNumero, diaNombre) {
        const diaElement = document.createElement('div');
        diaElement.className = 'dia-calendario';
        diaElement.dataset.semana = semana;
        diaElement.dataset.dia = diaNumero;
        
        const header = document.createElement('div');
        header.className = 'dia-header';
        header.innerHTML = `<h5>${diaNombre}</h5>`;
        diaElement.appendChild(header);
        
        // Crear turnos
        const turnosContainer = document.createElement('div');
        turnosContainer.className = 'turnos-container';
        
        this.turnos.forEach(turno => {
            const turnoElement = this.crearTurno(semana, diaNumero, turno);
            turnosContainer.appendChild(turnoElement);
        });
        
        diaElement.appendChild(turnosContainer);
        
        return diaElement;
    }
    
    crearTurno(semana, dia, turno) {
        const turnoElement = document.createElement('div');
        turnoElement.className = 'turno-slot';
        turnoElement.dataset.semana = semana;
        turnoElement.dataset.dia = dia;
        turnoElement.dataset.turno = turno.id;
        
        // Verificar si hay asignatura en este turno
        const asignatura = this.obtenerAsignatura(semana, dia, turno.id);
        
        if (asignatura) {
            if (asignatura.tipo === 'examen') {
                turnoElement.className += ' turno-examen';
                turnoElement.innerHTML = `
                    <div class="examen-content">
                        <i class="fas fa-file-alt"></i>
                        <span>${asignatura.nombre}</span>
                    </div>
                `;
            } else {
                turnoElement.className += ' turno-asignatura';
                turnoElement.style.backgroundColor = asignatura.color + '20';
                turnoElement.style.borderLeft = `4px solid ${asignatura.color}`;
                
                turnoElement.innerHTML = `
                    <div class="asignatura-content">
                        <div class="asignatura-header">
                            <span class="codigo">${asignatura.codigo}</span>
                            <button class="btn-remove" onclick="removerAsignatura(${semana}, ${dia}, ${turno.id})">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                        <span class="nombre">${asignatura.nombre}</span>
                        <div class="asignatura-footer">
                            <span class="profesor">${asignatura.profesor}</span>
                            <span class="hora">${turno.hora_inicio} - ${turno.hora_fin}</span>
                        </div>
                    </div>
                `;
            }
        } else {
            turnoElement.className += ' turno-vacio';
            turnoElement.innerHTML = `
                <div class="turno-vacio-content">
                    <i class="fas fa-plus"></i>
                    <span>${turno.hora_inicio} - ${turno.hora_fin}</span>
                </div>
            `;
        }
        
        return turnoElement;
    }
    
    crearPanelAsignaturas() {
        const panel = document.createElement('div');
        panel.className = 'panel-asignaturas';
        
        // Agrupar asignaturas por año
        const asignaturasPorAño = {};
        this.asignaturas.forEach(asig => {
            if (!asignaturasPorAño[asig.año]) {
                asignaturasPorAño[asig.año] = [];
            }
            asignaturasPorAño[asig.año].push(asig);
        });
        
        let asignaturasHTML = '';
        for (const [año, asignaturas] of Object.entries(asignaturasPorAño)) {
            asignaturasHTML += `
                <div class="año-group">
                    <h5>Año ${año}</h5>
                    <div class="asignaturas-grid">
                        ${asignaturas.map(asig => `
                            <div class="asignatura-draggable" 
                                 draggable="true"
                                 data-id="${asig.id}"
                                 style="border-left-color: ${asig.color}">
                                <div class="asignatura-info">
                                    <span class="codigo">${asig.codigo}</span>
                                    <span class="nombre">${asig.nombre}</span>
                                </div>
                                <div class="asignatura-meta">
                                    <span class="profesor">${asig.profesor || 'Sin asignar'}</span>
                                    <span class="horas">${asig.horas_totales}h</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        panel.innerHTML = `
            <div class="panel-header">
                <h4><i class="fas fa-book"></i> Asignaturas Disponibles</h4>
                <p>Arrastra y suelta en los turnos</p>
            </div>
            <div class="panel-body">
                ${asignaturasHTML}
            </div>
        `;
        
        return panel;
    }
    
    crearPanelConflictos() {
        const panel = document.createElement('div');
        panel.className = 'panel-conflictos';
        panel.id = 'panel-conflictos';
        
        panel.innerHTML = `
            <div class="panel-header">
                <h4><i class="fas fa-exclamation-triangle"></i> Conflictos Detectados</h4>
            </div>
            <div class="panel-body" id="conflictos-body">
                <div class="no-conflictos">
                    <i class="fas fa-check-circle"></i>
                    <p>No hay conflictos detectados</p>
                </div>
            </div>
        `;
        
        return panel;
    }
    
    configurarDragDrop() {
        // Configurar elementos draggables (asignaturas)
        const draggables = document.querySelectorAll('.asignatura-draggable');
        draggables.forEach(draggable => {
            draggable.addEventListener('dragstart', this.handleDragStart.bind(this));
        });
        
        // Configurar drop targets (turnos)
        const dropTargets = document.querySelectorAll('.turno-slot');
        dropTargets.forEach(target => {
            target.addEventListener('dragover', this.handleDragOver.bind(this));
            target.addEventListener('dragenter', this.handleDragEnter.bind(this));
            target.addEventListener('dragleave', this.handleDragLeave.bind(this));
            target.addEventListener('drop', this.handleDrop.bind(this));
        });
    }
    
    handleDragStart(e) {
        this.dragItem = {
            id: e.target.dataset.id,
            element: e.target
        };
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', e.target.dataset.id);
        e.target.classList.add('dragging');
    }
    
    handleDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
    }
    
    handleDragEnter(e) {
        e.target.classList.add('drag-over');
    }
    
    handleDragLeave(e) {
        e.target.classList.remove('drag-over');
    }
    
    async handleDrop(e) {
        e.preventDefault();
        e.target.classList.remove('drag-over');
        
        const asignaturaId = e.dataTransfer.getData('text/plain');
        const semana = e.target.dataset.semana || e.target.closest('[data-semana]').dataset.semana;
        const dia = e.target.dataset.dia || e.target.closest('[data-dia]').dataset.dia;
        const turno = e.target.dataset.turno || e.target.closest('[data-turno]').dataset.turno;
        
        if (!asignaturaId || !semana || !dia || !turno) return;
        
        // Enviar al servidor
        try {
            const response = await fetch(`/api/horario/${this.horarioId}/asignar`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    semana: parseInt(semana),
                    dia: parseInt(dia),
                    turno: parseInt(turno),
                    asignatura_id: parseInt(asignaturaId)
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Actualizar vista
                this.actualizarTurno(semana, dia, turno, asignaturaId);
                
                // Mostrar conflictos si los hay
                if (result.conflictos && result.conflictos.length > 0) {
                    this.mostrarConflictos(result.conflictos);
                } else {
                    this.ocultarConflictos();
                }
                
                // Mostrar notificación
                this.mostrarNotificacion('Asignatura asignada correctamente', 'success');
            }
            
        } catch (error) {
            console.error('Error asignando asignatura:', error);
            this.mostrarNotificacion('Error asignando asignatura', 'error');
        }
    }
    
    obtenerAsignatura(semana, dia, turno) {
        if (this.semanas[semana] && 
            this.semanas[semana][dia] && 
            this.semanas[semana][dia][turno]) {
            return this.semanas[semana][dia][turno];
        }
        return null;
    }
    
    actualizarTurno(semana, dia, turno, asignaturaId) {
        const asignatura = this.asignaturas.find(a => a.id == asignaturaId);
        const turnoElement = document.querySelector(
            `.turno-slot[data-semana="${semana}"][data-dia="${dia}"][data-turno="${turno}"]`
        );
        
        if (turnoElement && asignatura) {
            // Actualizar vista del turno
            const turnoData = this.turnos.find(t => t.id == turno);
            turnoElement.className = 'turno-slot turno-asignatura';
            turnoElement.style.backgroundColor = asignatura.color + '20';
            turnoElement.style.borderLeft = `4px solid ${asignatura.color}`;
            
            turnoElement.innerHTML = `
                <div class="asignatura-content">
                    <div class="asignatura-header">
                        <span class="codigo">${asignatura.codigo}</span>
                        <button class="btn-remove" onclick="removerAsignatura(${semana}, ${dia}, ${turno})">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <span class="nombre">${asignatura.nombre}</span>
                    <div class="asignatura-footer">
                        <span class="profesor">${asignatura.profesor || 'Sin asignar'}</span>
                        <span class="hora">${turnoData.hora_inicio} - ${turnoData.hora_fin}</span>
                    </div>
                </div>
            `;
            
            // Actualizar datos en memoria
            if (!this.semanas[semana]) this.semanas[semana] = {};
            if (!this.semanas[semana][dia]) this.semanas[semana][dia] = {};
            
            this.semanas[semana][dia][turno] = {
                tipo: 'asignatura',
                id: asignatura.id,
                codigo: asignatura.codigo,
                nombre: asignatura.nombre,
                color: asignatura.color,
                profesor: asignatura.profesor || 'Sin asignar'
            };
        }
    }
    
    mostrarConflictos(conflictos) {
        const panelBody = document.getElementById('conflictos-body');
        
        if (conflictos.length === 0) {
            panelBody.innerHTML = `
                <div class="no-conflictos">
                    <i class="fas fa-check-circle"></i>
                    <p>No hay conflictos detectados</p>
                </div>
            `;
            return;
        }
        
        let conflictosHTML = '';
        conflictos.forEach(conflicto => {
            conflictosHTML += `
                <div class="conflicto-item">
                    <div class="conflicto-header">
                        <i class="fas fa-exclamation-triangle"></i>
                        <span>${conflicto.mensaje}</span>
                    </div>
                    <div class="conflicto-body">
                        ${conflicto.profesores.map(p => `
                            <div class="profesor-conflicto">
                                <span class="nombre">${p.profesor_nombre}</span>
                                <span class="asignatura">${p.asignatura} (Año ${p.año})</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        });
        
        panelBody.innerHTML = conflictosHTML;
        
        // Mostrar panel si está oculto
        document.querySelector('.panel-conflictos').style.display = 'block';
    }
    
    ocultarConflictos() {
        const panelBody = document.getElementById('conflictos-body');
        panelBody.innerHTML = `
            <div class="no-conflictos">
                <i class="fas fa-check-circle"></i>
                <p>No hay conflictos detectados</p>
            </div>
        `;
    }
    
    mostrarNotificacion(mensaje, tipo = 'info') {
        const notificacion = document.createElement('div');
        notificacion.className = `notificacion ${tipo}`;
        notificacion.innerHTML = `
            <i class="fas fa-${tipo === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            <span>${mensaje}</span>
        `;
        
        document.body.appendChild(notificacion);
        
        setTimeout(() => {
            notificacion.classList.add('show');
        }, 10);
        
        setTimeout(() => {
            notificacion.classList.remove('show');
            setTimeout(() => {
                notificacion.remove();
            }, 300);
        }, 3000);
    }
}

// Funciones globales
async function removerAsignatura(semana, dia, turno) {
    try {
        const response = await fetch(`/api/horario/${window.horarioId}/asignar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                semana: semana,
                dia: dia,
                turno: turno
                // Sin asignatura_id para eliminar
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Recargar vista
            window.horarioDD.actualizarTurnoVacio(semana, dia, turno);
            
            if (result.conflictos && result.conflictos.length > 0) {
                window.horarioDD.mostrarConflictos(result.conflictos);
            } else {
                window.horarioDD.ocultarConflictos();
            }
            
            window.horarioDD.mostrarNotificacion('Asignatura removida', 'success');
        }
        
    } catch (error) {
        console.error('Error removiendo asignatura:', error);
        window.horarioDD.mostrarNotificacion('Error removiendo asignatura', 'error');
    }
}

async function guardarHorario() {
    // Implementar guardado completo del horario
    window.horarioDD.mostrarNotificacion('Horario guardado correctamente', 'success');
}

async function generarDistribucionAutomatica() {
    // Implementar distribución automática
    window.horarioDD.mostrarNotificacion('Distribuyendo automáticamente...', 'info');
}

async function limpiarHorario() {
    if (confirm('¿Estás seguro de que quieres limpiar todo el horario?')) {
        // Implementar limpieza
        window.horarioDD.mostrarNotificacion('Horario limpiado', 'info');
    }
}

async function exportarExcel() {
    try {
        const response = await fetch(`/api/exportar_excel/${window.horarioId}`);
        const blob = await response.blob();
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `horario_${window.horarioId}.xlsx`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        window.horarioDD.mostrarNotificacion('Excel exportado correctamente', 'success');
    } catch (error) {
        console.error('Error exportando Excel:', error);
        window.horarioDD.mostrarNotificacion('Error exportando Excel', 'error');
    }
}

function mostrarSemana(semana) {
    const semanaElement = document.querySelector(`.semana-calendario[data-semana="${semana}"]`);
    if (semanaElement) {
        semanaElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar drag & drop si estamos en la página de horarios
    if (document.getElementById('calendario-container') && window.horarioId) {
        window.horarioDD = new HorarioDragDrop('calendario-container', window.horarioId);
    }
});