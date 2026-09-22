import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

/** Al arrancar, avisa en la terminal a qué backend apunta la página y si es el correcto. */
function backendCheck(target) {
  const port = new URL(target).port || '8000'
  return {
    name: 'emergexia-backend-check',
    configureServer(server) {
      server.httpServer?.once('listening', async () => {
        const say = (m) => console.log(`\n  ${m}\n`)
        try {
          const res = await fetch(`${target}/api/health`, { signal: AbortSignal.timeout(5000) })
          const h = await res.json()
          if (!('mongo_ready' in h)) {
            say(`⚠  El backend en ${target} es una versión ANTIGUA (sin MongoDB). Ciérralo y arranca el nuevo.`)
          } else if (!h.mongo_ready) {
            say(`⚠  Backend ${target} (v${h.version}) activo, pero SIN MongoDB: ${h.mongo_error}`)
          } else {
            say(`✔  Backend ${target} (v${h.version}) conectado a MongoDB · base '${h.database}'`)
          }
        } catch {
          say(`✖  No hay backend en ${target}. En la carpeta backend ejecuta: uvicorn app.main:app --reload --port ${port}`)
        }
      })
    },
  }
}

// En desarrollo, /api se reenvía al backend. Para cambiar de puerto:
//   VITE_API_TARGET=http://127.0.0.1:8010 npm run dev      (o ponlo en frontend/.env.local)
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const target = process.env.VITE_API_TARGET || env.VITE_API_TARGET || 'http://127.0.0.1:8000'
  return {
    plugins: [react(), backendCheck(target)],
    // strictPort: si 5173 está ocupado (otra copia vieja del frontend), falla en vez de saltar a otro puerto en silencio.
    server: { port: 5173, strictPort: true, proxy: { '/api': target } },
  }
})
