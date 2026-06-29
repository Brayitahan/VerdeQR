# Guía Avanzada de CSS — Frontend Notebook

> **Autor:** Asistente IA · **Formato:** Guía de estudio avanzada  
> **Público:** Desarrolladores frontend con experiencia básica en CSS  
> **Versión:** 1.0 — Junio 2026

---

# 1. CSS AVANZADO

---

## 1.1 CSS Grid Avanzado

### grid-template-areas — Nombres de Áreas

La propiedad `grid-template-areas` permite nombrar celdas de la cuadrícula y asignar elementos a ellas usando el nombre en `grid-area`. Es la forma más legible de definir layouts complejos.

```css
.layout {
  display: grid;
  grid-template-columns: 250px 1fr;
  grid-template-rows: auto 1fr auto;
  grid-template-areas:
    "header  header"
    "sidebar main"
    "footer  footer";
  min-height: 100vh;
}

.header  { grid-area: header; }
.sidebar { grid-area: sidebar; }
.main    { grid-area: main; }
.footer  { grid-area: footer; }
```

**Reglas clave:**
- Cada fila se define entre comillas, cada columna es un nombre separado por espacio.
- Usa un punto `.` para dejar una celda vacía.
- Los nombres deben ser contiguos en forma rectangular — no se permiten formas en L.

**Ejercicio:** Crea un layout de dashboard con: navbar superior, sidebar izquierdo, contenido principal, panel derecho de estadísticas y footer. Usa `grid-template-areas` con 3 columnas.

---

### auto-fill vs auto-fit — La Diferencia Exacta

Ambos trabajan con `repeat(auto-fill, ...)` o `repeat(auto-fit, ...)`. La diferencia es **qué pasa con el espacio sobrante**:

```css
/* auto-fill: CREA tracks vacíos para ocupar el espacio */
.grid-fill {
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
}

/* auto-fit: COLAPSA tracks vacíos a 0, el contenido se expande */
.grid-fit {
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}
```

- **auto-fill**: Genera tracks fantasma aunque no haya elementos. Útil cuando quieres mantener la estructura aunque falten ítems.
- **auto-fit**: Colapsa los tracks vacíos a 0. Los elementos existentes ocupan el espacio disponible. Es el más usado en la práctica.

**Ejercicio:** Crea dos grids de 6 tarjetas cada uno, uno con auto-fill y otro con auto-fit. Redimensiona el viewport y observa cómo se comportan cuando solo hay 4 tarjetas visibles.

---

### minmax() y fit-content()

**minmax(min, max):** Define un rango de tamaño para los tracks. El navegador elige dentro del rango según el espacio disponible.

```css
grid-template-columns: minmax(200px, 1fr) 2fr minmax(100px, 300px);
```

**Usos comunes:**
- `minmax(0, 1fr)` — Evita que el desbordamiento de contenido rompa el fr.
- `minmax(auto, 1fr)` — Mínimo el contenido máximo, máximo el espacio disponible.

**fit-content(valor):** Actúa como `min(max-content, max(min-content, valor))`. El track crece hasta el valor máximo que le asignes, pero no más que el contenido.

```css
.sidebar {
  grid-template-columns: fit-content(300px) 1fr;
}
/* La sidebar crece hasta 300px, pero se encoge si el contenido */
/* es más pequeño. Nunca se expande más allá del contenido + 300px */
```

---

### Grid Implícito vs Explícito

El **grid explícito** es el que declaras con `grid-template-columns` y `grid-template-rows`. El **grid implícito** son los tracks que el navegador crea automáticamente cuando colocas elementos fuera del explícito.

```css
.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);  /* Explícito: 3 columnas */
  grid-template-rows: 100px 100px;         /* Explícito: 2 filas */
  grid-auto-rows: 200px;                   /* Implícito: filas extra de 200px */
  grid-auto-columns: 100px;                /* Implícito: columnas extra de 100px */
  grid-auto-flow: row;                     /* Cómo se colocan: row (default), column, dense */
}
```

**Propiedades clave del implícito:**
- `grid-auto-rows`: Tamaño de filas implícitas.
- `grid-auto-columns`: Tamaño de columnas implícitas.
- `grid-auto-flow`: Dirección de auto-colocación. Con `dense`, rellena huecos automáticamente.

**Ejercicio:** Crea un grid de 3 columnas con 4 elementos. Asigna solo posiciones explícitas a los primeros 2. Observa cómo el navegador coloca los otros 2 en el grid implícito. Cambia `grid-auto-rows` y `grid-auto-flow: dense` para ver los efectos.

---

### place-items, place-content, place-self

Son **shorthands** que combinan align (eje cruzado/columna) y justify (eje principal/fila):

| Propiedad | Shorthand de | Afecta a |
|-----------|-------------|----------|
| `place-items` | `align-items` + `justify-items` | Todos los ítems del contenedor |
| `place-content` | `align-content` + `justify-content` | El contenido del grid (espacio sobrante) |
| `place-self` | `align-self` + `justify-self` | Un ítem específico |

```css
.contenedor {
  display: grid;
  place-items: center;          /* Centra todo vertical y horizontalmente */
  place-content: space-evenly;  /* Distribuye el espacio sobrante */
}

.item-especial {
  place-self: start end;        /* align: start, justify: end */
}
```

**Ejercicio:** Crea un grid de 3×3. Centra todos los elementos con `place-items: center`. L haz que el elemento central use `place-self: stretch stretch` para que ocupe toda su celda.

---

### Grid Anidado

Un grid anidado es simplemente un elemento del grid que tiene `display: grid`. No hereda propiedades del padre — cada grid es independiente.

```css
.padre {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
}

.hijo {
  display: grid;
  grid-template-columns: subgrid; /* Experimental — hereda tracks del padre */
  gap: 10px;
}
```

**Nota:** `subgrid` funciona en Firefox y Chromium (2024+). Permite que los hijos del grid anidado se alineen con los tracks del grid padre. Sin `subgrid`, los grids anidados son independientes.

```css
/* Cards con imagen + texto, alineadas por subgrid */
.card-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
}

.card {
  display: grid;
  grid-template-rows: subgrid;
  grid-row: span 3; /* La card ocupa 3 filas del padre */
}
```

---

## 1.2 CSS Custom Properties (Variables)

### Definición y Uso Básico

Las Custom Properties se definen con doble guion `--` y se leen con `var()`:

```css
:root {
  --color-primario: #22c55e;
  --color-secundario: #3b82f6;
  --fuente-base: 16px;
  --espaciado: 1rem;
}

.boton {
  background: var(--color-primario);
  font-size: var(--fuente-base);
  padding: var(--espaciado) calc(var(--espaciado) * 2);
}
```

**Fallback:** El segundo argumento de `var()` se usa si la variable no está definida.

```css
.texto {
  color: var(--color-inexistente, #333); /* Usa #333 si --color-inexistente no existe */
}
```

---

### Variables en Media Queries

**Limitación importante:** Las custom properties **no funcionan dentro de** `@media` para el valor de la query misma. Ejemplo INCORRECTO:

```css
:root { --breakpoint: 768px; }
/* ❌ NO funciona: */
@media (min-width: var(--breakpoint)) { ... }
```

Pero sí funcionan **dentro** de los bloques de media query:

```css
:root {
  --gap: 2rem;
  --columnas: 3;
}

@media (max-width: 768px) {
  :root {
    --gap: 1rem;
    --columnas: 1;
  }
}

.grid {
  display: grid;
  grid-template-columns: repeat(var(--columnas), 1fr);
  gap: var(--gap);
}
```

---

### Temas Dinámicos (Dark Mode)

Las custom properties hacen trivial el cambio de temas:

```css
:root {
  --bg: #ffffff;
  --text: #1a1a1a;
  --surface: #f5f5f5;
  --border: #e0e0e0;
}

[data-theme="dark"] {
  --bg: #1a1a1a;
  --text: #e0e0e0;
  --surface: #2d2d2d;
  --border: #404040;
}

body {
  background: var(--bg);
  color: var(--text);
}

.card {
  background: var(--surface);
  border: 1px solid var(--border);
}
```

**Con JavaScript:**
```js
const toggle = document.getElementById('theme-toggle');
toggle.addEventListener('click', () => {
  const html = document.documentElement;
  const theme = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme); // Persistencia
});
```

**Ejercicio:** Construye un sistema de 3 temas (claro, oscuro, sepia) usando custom properties. Incluye colores de fondo, texto, enlaces y bordes. Añade un selector de temas con botones de radio.

---

## 1.3 Animaciones Avanzadas

### @keyframes con Múltiples Pasos

```css
@keyframes slide-in {
  0% {
    opacity: 0;
    transform: translateX(-100px) scale(0.8);
  }
  50% {
    opacity: 0.5;
    transform: translateX(20px) scale(1.05);
  }
  100% {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
}

.elemento {
  animation: slide-in 0.8s ease-out forwards;
}
```

**Puntos clave:**
- Puedes usar tantos `%` como necesites (`0%`, `25%`, `50%`, `75%`, `100%`).
- `from` equivale a `0%`, `to` equivale a `100%`.
- Las propiedades que no se animan saltan al valor final.

---

### cubic-bezier() — Curvas Personalizadas

```css
.elemento {
  transition: transform 0.3s cubic-bezier(0.68, -0.55, 0.27, 1.55);
}
```

**Curvas predefinidas:**
- `ease`: `cubic-bezier(0.25, 0.1, 0.25, 1.0)` — inicio suave, final suave
- `ease-in`: `cubic-bezier(0.42, 0.0, 1.0, 1.0)` — lento al inicio
- `ease-out`: `cubic-bezier(0.0, 0.0, 0.58, 1.0)` — lento al final
- `ease-in-out`: `cubic-bezier(0.42, 0.0, 0.58, 1.0)` — lento en ambos extremos
- `linear`: `cubic-bezier(0.0, 0.0, 1.0, 1.0)` — velocidad constante

**Ejercicio:** Crea 4 cajas que se muevan de izquierda a derecha, cada una con una curva diferente (ease, ease-in, ease-out, cubic-bezier personalizada). Observa la diferencia.

---

### animation-fill-mode — ¿Qué pasa antes/después?

```css
.elemento {
  /* Valores: none | forwards | backwards | both */
  animation: fade-in 1s ease-in forwards;
}
```

- `none` (default): No aplica estilos antes ni después. El elemento vuelve a su estado original.
- `forwards`: Mantiene los estilos del último keyframe (`100%`) al terminar.
- `backwards`: Aplica los estilos del primer keyframe (`0%`) durante el delay.
- `both`: Combina forwards + backwards.

---

### animation-delay y animation-iteration-count

```css
.loading-dot {
  animation: bounce 0.6s ease-in-out infinite alternate;
}

.loading-dot:nth-child(2) { animation-delay: 0.2s; }
.loading-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  from { transform: translateY(0); }
  to   { transform: translateY(-20px); }
}
```

**Propiedades:**
- `animation-iteration-count: infinite | 3 | 2.5` — Número de repeticiones.
- `animation-direction: normal | reverse | alternate | alternate-reverse`.
- `animation-play-state: running | paused` — Pausar/reanudar.

---

### will-change — Optimización de Rendimiento

```css
.elemento {
  will-change: transform, opacity;
}
```

**Reglas de uso:**
- Usar solo en elementos que efectivamente van a animarse pronto.
- No aplicar en demasiados elementos — consume memoria GPU.
- El navegador prepara la capa de renderizado anticipadamente.
- Quitar con JS después de la animación si es posible.

```js
element.addEventListener('mouseenter', () => {
  element.style.willChange = 'transform';
});
element.addEventListener('animationend', () => {
  element.style.willChange = 'auto';
});
```

---

### Transiciones vs Animaciones — ¿Cuándo Usar Cada Una?

| Criterio | Transiciones | Animaciones |
|----------|-------------|-------------|
| Disparo | Cambio de estado (hover, focus, clase) | Inicio automático o con clase |
| Control | Inicio y fin | Múltiples pasos (keyframes) |
| Loop | No nativamente | Sí (`infinite`) |
| Pausa | No | Sí (`animation-play-state`) |
| Rebote | Con cubic-bezier | Con keyframes |
| Complejidad | Cambios simples | Secuencias complejas |

**Regla práctica:** Usa **transiciones** para micro-interacciones (hover en botones, focus en inputs, aparecer/desaparecer). Usa **animaciones** para secuencias coreografiadas (loading spinners, entradas de página, sliders automáticos).

---

## 1.4 Responsive Avanzado

### Container Queries (@container)

Las container queries permiten que un elemento responda al tamaño de su **contenedor padre**, no al viewport. Esto es revolucionario para componentes reutilizables.

```css
/* 1. Definir un context de contención */
.card-container {
  container-type: inline-size;
  container-name: card;
}

/* 2. Usar @container (equivalente a @media pero para el contenedor) */
@container card (min-width: 400px) {
  .card {
    display: grid;
    grid-template-columns: 200px 1fr;
  }
}

@container card (max-width: 399px) {
  .card {
    display: flex;
    flex-direction: column;
  }
}
```

**Propiedades:**
- `container-type`: `inline-size` (solo ancho), `size` (ancho+alto), `normal` (no establece contención).
- `container-name`: Nombre para referenciar en `@container`.
- `container`: Shorthand de `container-name` + `container-type`.

**Ejercicio:** Crea un componente "tarjeta de producto" que se muestre horizontal (imagen + info lado a lado) cuando el contenedor tenga más de 500px, y vertical cuando tenga menos. Coloca 3 instancias del mismo componente en diferentes tamaños de contenedor.

---

### clamp() Profundo

`clamp(MIN, PREFERIDO, MAX)` es la función más útil para diseño responsive fluido:

```css
/* Tipografía fluida */
h1 {
  font-size: clamp(2rem, 5vw + 1rem, 4rem);
}

/* Margen fluido */
.container {
  padding-inline: clamp(1rem, 3vw, 4rem);
}

/* Grid fluido */
.grid {
  grid-template-columns: repeat(auto-fit, minmax(clamp(200px, 30%, 400px), 1fr));
}
```

**Fórmula recomendada para tipografía:**
```css
/* Calculadora: https://clamp.vittorio.cc/ */
h1 { font-size: clamp(2rem, 1.5rem + 2vw, 4rem); }
h2 { font-size: clamp(1.5rem, 1.2rem + 1.5vw, 3rem); }
p  { font-size: clamp(1rem, 0.9rem + 0.5vw, 1.25rem); }
```

**Ventajas:**
- Sin breakpoints para cambios graduales.
- Combina unidades relativas y absolutas.
- El navegador resuelve el valor ideal dentro del rango.

---

### Mobile-First vs Desktop-First

| Enfoque | Media Queries | Ventaja |
|---------|---------------|---------|
| **Mobile-first** | `min-width` | Progresivo, base mobile, se expande |
| **Desktop-first** | `max-width` | Base desktop, se contrae |

**Mobile-first (recomendado):**
```css
/* Base: móvil */
.layout { display: flex; flex-direction: column; gap: 1rem; }

/* Tablet+ */
@media (min-width: 768px) {
  .layout { display: grid; grid-template-columns: 1fr 2fr; }
}

/* Desktop+ */
@media (min-width: 1200px) {
  .layout { grid-template-columns: 1fr 3fr 1fr; }
}
```

**Desktop-first:**
```css
/* Base: desktop */
.layout { display: grid; grid-template-columns: 1fr 3fr 1fr; gap: 2rem; }

/* Tablet */
@media (max-width: 1199px) {
  .layout { grid-template-columns: 1fr 2fr; }
}

/* Móvil */
@media (max-width: 767px) {
  .layout { display: flex; flex-direction: column; }
}
```

**¿Cuál elegir?** Mobile-first es el estándar de la industria. Produce CSS más limpio, se alinea con el crecimiento del tráfico móvil, y fuerza decisiones de diseño progresivas.

---

## 1.5 Frameworks CSS

### Tailwind CSS vs Bootstrap vs CSS Propio

| Criterio | Tailwind CSS | Bootstrap | CSS Propio |
|----------|-------------|-----------|------------|
| Filosofía | Utility-first | Component-based | Artesanal |
| Curva de aprendizaje | Media (aprender clases) | Baja | Alta (dominar CSS) |
| Personalización | Alta (config) | Media (SASS vars) | Total |
| Tamaño (prod) | Muy pequeño (purga) | Mediano | El que escribas |
| Prototipado | Rápido | Rápidísimo | Lento |
| Consistencia | Garantizada | Garantizada | Bajo disciplina |
| Bundle JS | No | Sí (Bootstrap JS) | No |
| Mantenibilidad | Debate abierto | Buena | Depende del equipo |

**Ejemplo Tailwind:**
```html
<div class="flex items-center gap-4 p-4 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow">
  <img class="w-12 h-12 rounded-full object-cover" src="avatar.jpg" alt="">
  <div>
    <h3 class="text-lg font-semibold text-gray-900">Juan Pérez</h3>
    <p class="text-sm text-gray-500">Desarrollador Frontend</p>
  </div>
</div>
```

**Ejemplo Bootstrap:**
```html
<div class="card shadow-sm">
  <div class="card-body d-flex align-items-center gap-3">
    <img src="avatar.jpg" class="rounded-circle" width="48" height="48" alt="">
    <div>
      <h5 class="card-title mb-0">Juan Pérez</h5>
      <p class="card-text text-muted">Desarrollador Frontend</p>
    </div>
  </div>
</div>
```

**Ejemplo CSS propio:**
```html
<div class="profile-card">
  <img class="profile-card__avatar" src="avatar.jpg" alt="">
  <div class="profile-card__info">
    <h3 class="profile-card__name">Juan Pérez</h3>
    <p class="profile-card__role">Desarrollador Frontend</p>
  </div>
</div>
```
```css
.profile-card {
  display: flex; align-items: center; gap: 1rem;
  padding: 1rem; background: #fff; border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transition: box-shadow 0.2s;
}
.profile-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.12); }
.profile-card__avatar { width: 48px; height: 48px; border-radius: 50%; object-fit: cover; }
.profile-card__name { font-size: 1.125rem; font-weight: 600; color: #111; }
.profile-card__role { font-size: 0.875rem; color: #666; }
```

---

### Utility-First vs Component-Based

**Utility-first (Tailwind):**
- Ventajas: No inventas nombres de clases, tamaño en producción mínimo, consistente, no hay conflictos CSS.
- Desventajas: HTML verboso, curva de aprendizaje de las clases, puede sentirse "feo" al inicio.

**Component-based (Bootstrap, Material UI):**
- Ventajas: HTML limpio y semántico, componentes pre-diseñados, ideal para prototipado.
- Desventajas: Personalización limitada, sitios "iguales", bundle grande si no se purga.

**¿Cuál usar?** Utility-first para proyectos con diseño único y personalizado. Component-based para prototipos rápidos o productos con diseño estándar. CSS propio para equipos pequeños que quieren control total sin dependencias.

---

# 2. HERRAMIENTAS Y ECOSISTEMA

---

## 2.1 npm y package.json

### Comandos Esenciales

```bash
npm init -y                  # Crea package.json con valores por defecto
npm install <paquete>        # Instala en dependencies (--save es implícito)
npm i -D <paquete>           # Instala en devDependencies
npm uninstall <paquete>      # Desinstala
npm run <script>             # Ejecuta script del package.json
npx <comando>                # Ejecuta binario sin instalarlo globalmente
```

### package.json — Estructura Típica

```json
{
  "name": "mi-proyecto",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext .js,.jsx",
    "format": "prettier --write .",
    "prepare": "husky"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "eslint": "^8.56.0",
    "prettier": "^3.1.0",
    "husky": "^9.0.0",
    "lint-staged": "^15.0.0"
  },
  "lint-staged": {
    "*.{js,jsx}": ["eslint --fix", "prettier --write"],
    "*.css": ["prettier --write"]
  }
}
```

### npm vs yarn vs pnpm

| Característica | npm | yarn | pnpm |
|---------------|-----|------|------|
| Instalación | Lenta (legacy) | Rápida | Muy rápida |
| Disco | Duplicado | Duplicado | Hard links (eficiente) |
| Lockfile | package-lock.json | yarn.lock | pnpm-lock.yaml |
| Plug\'n\'Play | No | Sí (PnP) | Sí (store) |
| Monorepos | Workspaces | Workspaces | Built-in (poderoso) |
| Popularidad | Estándar | Alta | Creciendo |

**Recomendación:** Usa pnpm para proyectos nuevos (ahorra espacio, más rápido, estricto). Usa npm si trabajas en equipo (estándar). Usa yarn si ya estás en un proyecto existente con yarn.

---

## 2.2 Bundlers

### ¿Qué Hace un Bundler?

Un **bundler** (empaquetador) toma múltiples archivos JS, CSS, imágenes, fuentes, etc., y los combina en uno o pocos archivos optimizados para producción. También:

1. **Resuelve dependencias**: Convierte imports/requires en un grafo de dependencias.
2. **Transpila**: Convierte JS moderno a compatible, SCSS a CSS, JSX a JS.
3. **Optimiza**: Minifica, tree-shakes (elimina código muerto), divide código (code splitting).
4. **Sirve en desarrollo**: Hot Module Replacement (HMR) — cambias código, se refleja al instante.

### Vite — El Estándar Moderno

**Ventajas:**
- Usa ES modules nativos en desarrollo (sin bundling en caliente).
- HMR instantáneo independientemente del tamaño del proyecto.
- Configuración mínima (cero config para proyectos vanilla).
- Construcción con Rollup para producción (optimizado).

```bash
npm create vite@latest mi-proyecto -- --template vanilla
npm create vite@latest mi-proyecto -- --template react
```

**Configuración típica (vite.config.js):**
```js
import { defineConfig } from 'vite';

export default defineConfig({
  root: '.',
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'esbuild',
    rollupOptions: {
      output: {
        manualChunks: { vendor: ['react', 'react-dom'] }
      }
    }
  },
  server: {
    port: 3000,
    open: true
  }
});
```

### Webpack — Concepto General

Webpack fue el estándar antes de Vite. Su configuración es verbosa pero increíblemente flexible:

```js
const path = require('path');

module.exports = {
  entry: './src/index.js',
  output: { path: path.resolve(__dirname, 'dist'), filename: 'bundle.js' },
  module: {
    rules: [
      { test: /\.jsx?$/, exclude: /node_modules/, use: 'babel-loader' },
      { test: /\.css$/, use: ['style-loader', 'css-loader'] }
    ]
  },
  plugins: [new HtmlWebpackPlugin({ template: './src/index.html' })],
  devServer: { port: 3000, hot: true }
};
```

### Desarrollo vs Producción — Diferencias Clave

| Aspecto | Desarrollo | Producción |
|---------|-----------|------------|
| Source maps | Sí (completos) | Opcional (o ninguno) |
| Minificación | No | Sí (esbuild/Terser) |
| HMR | Sí | No |
| Tree-shaking | No | Sí |
| Code splitting | No | Sí |
| Cache busting | No | Hashes en archivos |
| Tiempo de build | Segundos | Minutos (grandes proyectos) |

---

## 2.3 Linters y Formatters

### ESLint — Reglas y Configuración

ESLint analiza el código JS/JSX/TS en busca de errores, malas prácticas e inconsistencias de estilo.

```bash
npm i -D eslint
npx eslint --init  # Configuración guiada
```

**Configuración (.eslintrc.json o eslint.config.js):**
```json
{
  "env": { "browser": true, "es2022": true },
  "extends": [
    "eslint:recommended",
    "plugin:react/recommended"
  ],
  "rules": {
    "no-unused-vars": "warn",
    "no-console": "warn",
    "react/prop-types": "error",
    "semi": ["error", "always"]
    // "off" | "warn" | "error"
  }
}
```

### Prettier — Formateo Automático

Prettier elimina las discusiones de estilo formateando automáticamente el código.

```bash
npm i -D prettier
```

**Configuración (.prettierrc):**
```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "all",
  "printWidth": 100,
  "bracketSpacing": true,
  "arrowParens": "always"
}
```

**Integración VSCode:** Instalar extensión Prettier, configurar como formateador por defecto:
```json
// settings.json
{
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.formatOnSave": true
}
```

### Husky + lint-staged — Git Hooks Automáticos

Ejecuta linters y formateadores antes de cada commit:

```bash
npm i -D husky lint-staged
npx husky init
```

Esto crea `.husky/pre-commit`. Modifícalo para que ejecute:
```bash
# .husky/pre-commit
npx lint-staged
```

Con `lint-staged` configurado en `package.json` (ver sección 2.1), solo revisa los archivos modificados en el commit, no todo el proyecto. Así los commits son rápidos y siempre pasan por el lint.

---

## 2.4 React — Conceptos Básicos

### Componentes Funcionales y JSX

```jsx
function Saludo({ nombre, edad }) {
  return (
    <div className="saludo">
      <h1>Hola, {nombre}!</h1>
      {edad >= 18 && <p>Eres mayor de edad</p>}
    </div>
  );
}
```

**JSX**: Sintaxis similar a HTML que se transpila a `React.createElement()`. Reglas:
- `class` → `className`
- `for` → `htmlFor`
- Atributos en camelCase (`onClick`, `onChange`)
- Las expresiones van entre `{}`

### Props y State

```jsx
import { useState } from 'react';

function Contador({ valorInicial = 0 }) {
  // Props: datos que vienen del padre (inmutables)
  // State: datos internos (mutables con setter)
  const [contador, setContador] = useState(valorInicial);

  return (
    <div>
      <p>Valor: {contador}</p>
      <button onClick={() => setContador(c => c + 1)}>+1</button>
    </div>
  );
}
```

### useEffect — Efectos Secundarios

```jsx
import { useState, useEffect } from 'react';

function DatosUsuario({ userId }) {
  const [usuario, setUsuario] = useState(null);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    async function fetchUsuario() {
      setCargando(true);
      const res = await fetch(`/api/usuarios/${userId}`);
      const data = await res.json();
      setUsuario(data);
      setCargando(false);
    }
    fetchUsuario();
  }, [userId]); // Solo se re-ejecuta si userId cambia

  if (cargando) return <p>Cargando...</p>;
  return <h2>{usuario.nombre}</h2>;
}
```

### ¿Por Qué React y No JS Vanilla?

| Escenario | JS Vanilla | React |
|-----------|-----------|-------|
| 3 botones y un contador | Bien | Overkill |
| Dashboard con 20 componentes | Infierno de DOM | Organizado |
| Estado compartido (user, theme) | Global vars frágiles | Context/State management |
| Actualizaciones en tiempo real | Reflow manual | Virtual DOM eficiente |
| Equipo de 5+ personas | Sin estructura | Componentes predecibles |
| SEO/SSR | Posible | Next.js lo resuelve |

**Regla práctica:** Usa React cuando el estado de la UI es complejo (múltiples componentes que cambian según datos). Usa JS vanilla para páginas estáticas o micro-interacciones.

---

# 3. RENDIMIENTO FRONTEND

---

## 3.1 Core Web Vitals

Son las métricas que Google usa para medir la experiencia de usuario:

| Métrica | Qué Mide | Bueno | Malo | Cómo Mejorar |
|---------|----------|-------|------|--------------|
| **LCP** (Largest Contentful Paint) | Tiempo de carga del elemento más grande | < 2.5s | > 4s | Optimizar imágenes, server-side rendering, CDN |
| **FID** (First Input Delay) | Tiempo de respuesta al primer clic/toque | < 100ms | > 300ms | Code splitting, lazy loading JS, eliminar bloqueantes |
| **CLS** (Cumulative Layout Shift) | Estabilidad visual (elementos que se mueven) | < 0.1 | > 0.25 | Dimensiones explícitas en imágenes, fuentes con fallback |

```html
<!-- Prevenir CLS: Siempre dar dimensiones a imágenes -->
<img src="hero.jpg" alt="" width="800" height="450" style="aspect-ratio: 16/9">
```

---

## 3.2 Lazy Loading

Carga diferida de recursos que no están visibles inmediatamente:

```html
<!-- Imágenes: loading="lazy" (nativo, soporte moderno) -->
<img src="galeria/foto-10.jpg" loading="lazy" alt="">

<!-- Iframes: loading="lazy" -->
<iframe src="mapa.html" loading="lazy"></iframe>

<!-- Intersection Observer (alternativa + control) -->
<script>
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const img = entry.target;
      img.src = img.dataset.src;
      observer.unobserve(img);
    }
  });
});

document.querySelectorAll('img[data-src]').forEach(img => observer.observe(img));
</script>
```

---

## 3.3 Defer vs Async

```html
<!-- ❌ Bloquea el renderizado -->
<script src="app.js"></script>

<!-- ✅ No bloquea, ejecuta en cuanto descarga (orden no garantizado) -->
<script async src="analytics.js"></script>

<!-- ✅ No bloquea, ejecuta cuando el DOM está listo (orden respetado) -->
<script defer src="app.js"></script>
```

| Atributo | Orden | Cuándo ejecuta | Ideal para |
|----------|-------|---------------|------------|
| (ninguno) | Secuencial | Inmediatamente al descargar | Scripts pequeños y críticos |
| `async` | No garantizado | En cuanto termina la descarga | Analytics, scripts independientes |
| `defer` | Garantizado (orden HTML) | Cuando el DOM está listo (DOMContentLoaded) | Scripts que dependen del DOM |

---

## 3.4 Minificación y Compresión

**Minificación:** Elimina espacios, comentarios, renombra variables. Reduce ~60% el tamaño.

```bash
# Herramientas
npx terser archivo.js -o archivo.min.js
npx cssnano estilos.css > estilos.min.css
# Vite y Webpack lo hacen automáticamente en build
```

**Compresión (servidor):**
- **Gzip**: Estándar, ~70% reducción.
- **Brotli**: Moderno, mejor ratio (~80%), soportado por todos los navegadores modernos.

```nginx
# Nginx
gzip on;
brotli on;
```

**Con Vite:** Minificación con esbuild (rápido) o terser (más completo). Compresión se configura en el servidor.

---

## 3.5 Service Workers (Concepto)

Un **Service Worker** es un script que el navegador ejecuta en segundo plano, independiente de la página. Permite:

- **Estrategias de caché** (offline-first, network-first, stale-while-revalidate)
- **Notificaciones push**
- **Sincronización en segundo plano**

```js
// service-worker.js — Estrategia Cache First
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((cacheResponse) => {
      return cacheResponse || fetch(event.request);
    })
  );
});
```

```js
// Registro en la página
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');
}
```

---

# 4. ACCESIBILIDAD (a11y)

---

## 4.1 Roles ARIA

Los roles ARIA (`role`) describen el propósito de un elemento para tecnologías asistivas:

```html
<!-- Roles semánticos -->
<div role="navigation">...</div>
<div role="banner">...</div>
<div role="main">...</div>
<div role="complementary">...</div>

<!-- Mejor: usar elementos HTML5 semánticos en lugar de divs -->
<nav>...</nav>
<header>...</header>
<main>...</main>
<aside>...</aside>

<!-- Roles para widgets -->
<button role="tab">Pestaña 1</button>
<div role="tabpanel">...</div>
<div role="alert">Error al guardar</div>
```

**Principio:** No uses ARIA cuando los elementos HTML nativos ya tienen semántica implícita. `<button>` ya es un botón, no necesitas `role="button"`.

---

## 4.2 Navegación por Teclado

```css
/* Siempre visible, nunca outline: none sin alternativa */
:focus-visible {
  outline: 2px solid var(--color-primario);
  outline-offset: 2px;
}

/* Para elementos personalizados (div como botón) */
.custom-button:focus-visible {
  box-shadow: 0 0 0 3px var(--color-primario);
}
```

**Reglas de navegación:**
- Todos los elementos interactivos deben ser accesibles por tabulación.
- `tabindex="0"` hace un elemento focusable (en orden natural).
- `tabindex="-1"` lo hace focusable solo con JS (`.focus()`).
- Usa `aria-label` para dar nombres a elementos sin texto visible.

```html
<button aria-label="Cerrar ventana" onclick="closeModal()">
  ✕
</button>
```

---

## 4.3 Contraste WCAG

| Nivel | Ratio de contraste | Para |
|-------|-------------------|------|
| AA (mínimo) | 4.5:1 | Texto normal |
| AA | 3:1 | Texto grande (>18px bold o >24px) |
| AAA (reforzado) | 7:1 | Texto normal |

```css
/* Verificación con JS */
function checkContrast(foreground, background) {
  // Usar librería: https://webaim.org/resources/contrastchecker/
  const ratio = getContrastRatio(foreground, background);
  console.log(ratio >= 4.5 ? '✅ Pasa AA' : '❌ No pasa AA');
}
```

**Herramientas:** WebAIM Contrast Checker, axe DevTools, Lighthouse.

---

## 4.4 Lectores de Pantalla

**Prácticas esenciales:**
- Texto alternativo en imágenes: `alt` descriptivo (no "imagen", sino "Gráfico de crecimiento de ventas 2025").
- Encabezados jerárquicos: `h1` → `h2` → `h3`, sin saltos.
- Formularios con `<label>` asociado:

```html
<!-- ✅ Correcto -->
<label for="email">Correo electrónico</label>
<input type="email" id="email" name="email" required>

<!-- ✅ También correcto (aria-label) -->
<input type="email" aria-label="Correo electrónico" required>
```

- Estados dinámicos con `aria-live`:

```html
<div aria-live="polite" id="notificaciones">
  <!-- Los cambios aquí se anuncian automáticamente -->
</div>
```

- Skip to content (salto de navegación):

```html
<a href="#main-content" class="skip-link">Saltar al contenido principal</a>
```

---

# Recursos y Enlaces

**Documentación oficial:**
- CSS Grid: https://developer.mozilla.org/es/docs/Web/CSS/CSS_Grid_Layout
- Custom Properties: https://developer.mozilla.org/es/docs/Web/CSS/--*
- Container Queries: https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_containment/Container_queries
- WCAG 2.2: https://www.w3.org/TR/WCAG22/
- Core Web Vitals: https://web.dev/vitals/

**Herramientas:**
- Can I Use: https://caniuse.com
- CSS Grid Generator: https://cssgridgenerator.io
- Clamp Calculator: https://clamp.vittorio.cc
- WebAIM Contrast: https://webaim.org/resources/contrastchecker/
- axe DevTools (extensión Chrome/Firefox): https://www.deque.com/axe/

---

> **Fin de la guía.** Este documento cubre ~95% de los temas avanzados de CSS y frontend que un desarrollador senior debe conocer. Estudia los conceptos, completa los ejercicios y consulta la documentación oficial para profundizar.
