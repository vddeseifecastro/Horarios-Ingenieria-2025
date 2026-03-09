// dashboard-particles.js
// Partículas suaves para dashboards (no invasivas)

class DashboardParticles {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        
        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.grid = [];
        this.mouse = { x: 0, y: 0, radius: 80 };
        this.isActive = true;
        
        this.init();
        this.animate();
        this.setupEvents();
    }
    
    init() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        
        // Crear partículas sutiles
        const particleCount = Math.min(40, Math.floor((window.innerWidth * window.innerHeight) / 30000));
        
        for (let i = 0; i < particleCount; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * 0.3,
                vy: (Math.random() - 0.5) * 0.3,
                radius: Math.random() * 1.5 + 0.5,
                color: Math.random() > 0.7 ? '#00ffff' : '#4361ee',
                opacity: Math.random() * 0.2 + 0.1,
                pulse: Math.random() * Math.PI * 2
            });
        }
        
        // Crear grid de puntos sutiles
        this.createGrid();
    }
    
    createGrid() {
        const cols = Math.floor(this.canvas.width / 80);
        const rows = Math.floor(this.canvas.height / 80);
        const cellWidth = this.canvas.width / cols;
        const cellHeight = this.canvas.height / rows;
        
        this.grid = [];
        for (let i = 0; i < cols; i++) {
            for (let j = 0; j < rows; j++) {
                this.grid.push({
                    x: i * cellWidth + cellWidth / 2,
                    y: j * cellHeight + cellHeight / 2,
                    active: Math.random() > 0.8,
                    intensity: 0,
                    pulse: Math.random() * Math.PI * 2
                });
            }
        }
    }
    
    animate() {
        if (!this.isActive) return;
        
        // Fondo semi-transparente para efecto de rastro sutil
        this.ctx.fillStyle = 'rgba(10, 14, 23, 0.02)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Dibujar grid
        this.drawGrid();
        
        // Actualizar y dibujar partículas
        this.updateParticles();
        this.drawParticles();
        this.drawConnections();
        
        requestAnimationFrame(() => this.animate());
    }
    
    drawGrid() {
        this.grid.forEach(point => {
            point.pulse += 0.01;
            
            if (point.active) {
                point.intensity = Math.sin(point.pulse) * 0.3 + 0.4;
                
                this.ctx.save();
                this.ctx.fillStyle = `rgba(0, 255, 255, ${point.intensity * 0.05})`;
                this.ctx.beginPath();
                this.ctx.arc(point.x, point.y, 1, 0, Math.PI * 2);
                this.ctx.fill();
                this.ctx.restore();
            }
            
            if (Math.random() > 0.997) {
                point.active = !point.active;
            }
        });
    }
    
    updateParticles() {
        this.particles.forEach(p => {
            p.x += p.vx;
            p.y += p.vy;
            p.pulse += 0.02;
            p.opacity = 0.1 + Math.sin(p.pulse) * 0.1;
            
            // Rebote suave en bordes
            if (p.x < 0 || p.x > this.canvas.width) p.vx *= -0.9;
            if (p.y < 0 || p.y > this.canvas.height) p.vy *= -0.9;
            
            // Mantener dentro del canvas
            p.x = Math.max(0, Math.min(this.canvas.width, p.x));
            p.y = Math.max(0, Math.min(this.canvas.height, p.y));
            
            // Interacción sutil con mouse
            const dx = this.mouse.x - p.x;
            const dy = this.mouse.y - p.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance < this.mouse.radius) {
                const angle = Math.atan2(dy, dx);
                const force = (this.mouse.radius - distance) / this.mouse.radius;
                p.vx -= Math.cos(angle) * force * 0.2;
                p.vy -= Math.sin(angle) * force * 0.2;
                p.opacity = Math.min(0.4, p.opacity + 0.1);
            }
        });
    }
    
    drawParticles() {
        this.particles.forEach(p => {
            this.ctx.save();
            
            // Partícula con brillo sutil
            this.ctx.fillStyle = p.color;
            this.ctx.globalAlpha = p.opacity;
            
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            this.ctx.fill();
            
            this.ctx.restore();
        });
    }
    
    drawConnections() {
        this.ctx.strokeStyle = 'rgba(0, 255, 255, 0.03)';
        this.ctx.lineWidth = 0.5;
        
        for (let i = 0; i < this.particles.length; i++) {
            for (let j = i + 1; j < this.particles.length; j++) {
                const p1 = this.particles[i];
                const p2 = this.particles[j];
                
                const dx = p1.x - p2.x;
                const dy = p1.y - p2.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < 80) {
                    const opacity = 0.05 * (1 - distance/80);
                    
                    this.ctx.strokeStyle = `rgba(0, 255, 255, ${opacity})`;
                    this.ctx.beginPath();
                    this.ctx.moveTo(p1.x, p1.y);
                    this.ctx.lineTo(p2.x, p2.y);
                    this.ctx.stroke();
                }
            }
        }
    }
    
    setupEvents() {
        window.addEventListener('resize', () => {
            this.canvas.width = window.innerWidth;
            this.canvas.height = window.innerHeight;
            this.init();
        });
        
        this.canvas.addEventListener('mousemove', (e) => {
            const rect = this.canvas.getBoundingClientRect();
            this.mouse.x = e.clientX - rect.left;
            this.mouse.y = e.clientY - rect.top;
        });
        
        this.canvas.addEventListener('mouseleave', () => {
            this.mouse.x = 0;
            this.mouse.y = 0;
        });
        
        // Pausar partículas cuando el usuario está interactuando con formularios
        document.addEventListener('focusin', () => {
            this.isActive = false;
        });
        
        document.addEventListener('focusout', () => {
            setTimeout(() => {
                this.isActive = true;
            }, 100);
        });
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    // Solo inicializar si hay canvas
    if (document.getElementById('dashboard-bg')) {
        new DashboardParticles('dashboard-bg');
    }
});

// Función para crear elementos decorativos
function createDashboardDecorations() {
    // Crear elementos decorativos flotantes
    const container = document.querySelector('.dashboard-container') || document.body;
    
    if (!container.querySelector('.dashboard-decorations')) {
        const decorations = document.createElement('div');
        decorations.className = 'dashboard-decorations';
        decorations.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
            overflow: hidden;
        `;
        
        container.appendChild(decorations);
        
        // Crear elementos decorativos
        const icons = ['◇', '◆', '○', '□', '△', '▽', '☆', '✦'];
        
        for (let i = 0; i < 15; i++) {
            const icon = document.createElement('div');
            icon.textContent = icons[Math.floor(Math.random() * icons.length)];
            icon.style.cssText = `
                position: absolute;
                font-size: ${Math.random() * 1 + 0.8}rem;
                color: rgba(0, 255, 255, ${Math.random() * 0.1 + 0.05});
                top: ${Math.random() * 100}%;
                left: ${Math.random() * 100}%;
                animation: floatDecoration ${20 + Math.random() * 20}s infinite linear;
                opacity: 0;
            `;
            
            decorations.appendChild(icon);
        }
        
        // Agregar animación CSS
        const style = document.createElement('style');
        style.textContent = `
            @keyframes floatDecoration {
                0% {
                    transform: translateY(100vh) translateX(0) rotate(0deg);
                    opacity: 0;
                }
                10% {
                    opacity: ${Math.random() * 0.3 + 0.1};
                }
                90% {
                    opacity: ${Math.random() * 0.3 + 0.1};
                }
                100% {
                    transform: translateY(-100px) translateX(${Math.random() * 200 - 100}px) rotate(${Math.random() * 360}deg);
                    opacity: 0;
                }
            }
        `;
        
        document.head.appendChild(style);
    }
}

// Inicializar decoraciones después de un delay
setTimeout(createDashboardDecorations, 1000);