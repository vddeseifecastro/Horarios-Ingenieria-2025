// frontend/js/tech-particles.js
class TechParticles {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        
        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.grid = [];
        this.mouse = { x: 0, y: 0, radius: 100 };
        
        this.init();
        this.animate();
        this.setupEvents();
    }
    
    init() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        
        // Crear partículas de conexión tipo circuito
        const particleCount = 80;
        for (let i = 0; i < particleCount; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                radius: Math.random() * 2 + 0.5,
                color: i % 3 === 0 ? '#00ffff' : i % 3 === 1 ? '#4361ee' : '#3a0ca3',
                connections: [],
                pulse: Math.random() * Math.PI * 2
            });
        }
        
        // Crear grid de puntos para efecto matrix
        this.createGrid();
    }
    
    createGrid() {
        const cols = 40;
        const rows = 25;
        const cellWidth = this.canvas.width / cols;
        const cellHeight = this.canvas.height / rows;
        
        this.grid = [];
        for (let i = 0; i < cols; i++) {
            for (let j = 0; j < rows; j++) {
                this.grid.push({
                    x: i * cellWidth + cellWidth / 2,
                    y: j * cellHeight + cellHeight / 2,
                    active: Math.random() > 0.7,
                    intensity: 0,
                    char: this.getRandomTechChar()
                });
            }
        }
    }
    
    getRandomTechChar() {
        const chars = ['01', '◆', '■', '▲', '●', '⌘', '⎔', '⏣', '⏚', '⎶'];
        return chars[Math.floor(Math.random() * chars.length)];
    }
    
    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Fondo con gradiente sutil
        const gradient = this.ctx.createLinearGradient(0, 0, this.canvas.width, this.canvas.height);
        gradient.addColorStop(0, 'rgba(26, 26, 46, 0.8)');
        gradient.addColorStop(1, 'rgba(22, 33, 62, 0.9)');
        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Dibujar grid de puntos (estilo terminal)
        this.drawGrid();
        
        // Actualizar y dibujar partículas
        this.updateParticles();
        this.drawParticles();
        this.drawConnections();
        
        requestAnimationFrame(() => this.animate());
    }
    
    drawGrid() {
        this.grid.forEach(point => {
            if (point.active || Math.random() > 0.99) {
                point.intensity = Math.min(point.intensity + 0.1, 1);
                this.ctx.save();
                
                // Efecto brillo
                const glow = this.ctx.createRadialGradient(
                    point.x, point.y, 0,
                    point.x, point.y, 10
                );
                glow.addColorStop(0, `rgba(76, 201, 240, ${point.intensity * 0.3})`);
                glow.addColorStop(1, 'transparent');
                
                this.ctx.fillStyle = glow;
                this.ctx.fillRect(point.x - 10, point.y - 10, 20, 20);
                
                // Punto central
                this.ctx.fillStyle = `rgba(76, 201, 240, ${point.intensity})`;
                this.ctx.beginPath();
                this.ctx.arc(point.x, point.y, 1.5, 0, Math.PI * 2);
                this.ctx.fill();
                
                // Carácter tecnológico (aparece aleatoriamente)
                if (Math.random() > 0.95) {
                    this.ctx.fillStyle = `rgba(76, 201, 240, ${point.intensity * 0.7})`;
                    this.ctx.font = '10px monospace';
                    this.ctx.textAlign = 'center';
                    this.ctx.textBaseline = 'middle';
                    this.ctx.fillText(point.char, point.x, point.y - 15);
                }
                
                this.ctx.restore();
            }
            
            if (Math.random() > 0.995) {
                point.active = !point.active;
                point.char = this.getRandomTechChar();
            }
            
            if (!point.active && point.intensity > 0) {
                point.intensity = Math.max(point.intensity - 0.05, 0);
            }
        });
    }
    
    updateParticles() {
        this.particles.forEach(p => {
            p.x += p.vx;
            p.y += p.vy;
            p.pulse += 0.05;
            
            // Rebote en bordes
            if (p.x < 0 || p.x > this.canvas.width) p.vx *= -1;
            if (p.y < 0 || p.y > this.canvas.height) p.vy *= -1;
            
            // Mantener dentro del canvas
            p.x = Math.max(0, Math.min(this.canvas.width, p.x));
            p.y = Math.max(0, Math.min(this.canvas.height, p.y));
            
            // Interacción con mouse
            const dx = this.mouse.x - p.x;
            const dy = this.mouse.y - p.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance < this.mouse.radius) {
                const angle = Math.atan2(dy, dx);
                const force = (this.mouse.radius - distance) / this.mouse.radius;
                p.vx -= Math.cos(angle) * force * 0.5;
                p.vy -= Math.sin(angle) * force * 0.5;
            }
        });
    }
    
    drawParticles() {
        this.particles.forEach(p => {
            this.ctx.save();
            
            // Brillo pulsante
            const pulseSize = Math.sin(p.pulse) * 0.5 + 1;
            
            // Gradiente para partícula
            const gradient = this.ctx.createRadialGradient(
                p.x, p.y, 0,
                p.x, p.y, p.radius * 4
            );
            gradient.addColorStop(0, p.color);
            gradient.addColorStop(1, 'transparent');
            
            this.ctx.fillStyle = gradient;
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, p.radius * pulseSize * 2, 0, Math.PI * 2);
            this.ctx.fill();
            
            // Núcleo de la partícula
            this.ctx.fillStyle = p.color;
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, p.radius * pulseSize, 0, Math.PI * 2);
            this.ctx.fill();
            
            this.ctx.restore();
        });
    }
    
    drawConnections() {
        this.ctx.strokeStyle = 'rgba(76, 201, 240, 0.1)';
        this.ctx.lineWidth = 0.5;
        
        for (let i = 0; i < this.particles.length; i++) {
            for (let j = i + 1; j < this.particles.length; j++) {
                const p1 = this.particles[i];
                const p2 = this.particles[j];
                
                const dx = p1.x - p2.x;
                const dy = p1.y - p2.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < 100) {
                    // Línea con gradiente
                    const gradient = this.ctx.createLinearGradient(p1.x, p1.y, p2.x, p2.y);
                    gradient.addColorStop(0, `rgba(76, 201, 240, ${0.2 * (1 - distance/100)})`);
                    gradient.addColorStop(1, `rgba(67, 97, 238, ${0.2 * (1 - distance/100)})`);
                    
                    this.ctx.strokeStyle = gradient;
                    this.ctx.beginPath();
                    this.ctx.moveTo(p1.x, p1.y);
                    this.ctx.lineTo(p2.x, p2.y);
                    this.ctx.stroke();
                    
                    // Puntos de conexión
                    if (distance < 50) {
                        this.ctx.fillStyle = `rgba(76, 201, 240, ${0.3 * (1 - distance/50)})`;
                        this.ctx.beginPath();
                        this.ctx.arc((p1.x + p2.x) / 2, (p1.y + p2.y) / 2, 1, 0, Math.PI * 2);
                        this.ctx.fill();
                    }
                }
            }
        }
    }
    
    setupEvents() {
        window.addEventListener('resize', () => {
            this.canvas.width = window.innerWidth;
            this.canvas.height = window.innerHeight;
            this.createGrid();
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
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new TechParticles('particles-canvas');
});