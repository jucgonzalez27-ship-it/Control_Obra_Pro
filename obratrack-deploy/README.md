# ObraTrack — Control Operativo de Obra

## Instalación local

1. Instalar Node.js desde https://nodejs.org (versión LTS)
2. Abrir terminal en esta carpeta
3. Ejecutar: npm install
4. Ejecutar: npm run dev
5. Abrir http://localhost:5173

## Despliegue en Vercel (URL pública)

### Opción A — Desde GitHub (recomendado)
1. Crear cuenta en https://github.com
2. Crear repositorio nuevo llamado "obratrack"
3. Subir todos estos archivos al repositorio
4. Ir a https://vercel.com y crear cuenta con GitHub
5. Clic en "New Project" → importar el repositorio "obratrack"
6. Clic en "Deploy" — listo, tendrás una URL como obratrack.vercel.app

### Opción B — Drag & Drop en Vercel
1. Ejecutar: npm run build
2. Ir a https://vercel.com/new
3. Arrastrar la carpeta "dist" que se genera
4. URL lista en 30 segundos

## Estructura del proyecto
```
obratrack/
├── index.html          ← entrada de la app
├── package.json        ← dependencias
├── vite.config.js      ← configuración
└── src/
    ├── main.jsx        ← punto de inicio React
    └── App.jsx         ← toda la lógica de ObraTrack
```

## Tecnologías
- React 18
- Vite
- Recharts (gráficos)
- CSS-in-JS inline styles
