import { useEffect, useMemo, useRef } from 'react'
// Versión ligera de lottie-web: solo SVG, sin expresiones ni eval() (más pequeña y compatible con CSP).
import lottie from 'lottie-web/build/player/lottie_light'
import heartbeatData from '../assets/heartbeat.json'

// Las capas "blur" usan el efecto Gaussian Blur, que la versión ligera no soporta:
// se descartan y el resplandor lo aporta drop-shadow en CSS.
const withoutEffects = (data) => ({ ...data, layers: data.layers.filter((layer) => !layer.ef) })

// Solo la línea del pulso y el punto que la recorre, sin la pista de fondo:
// pensado para espacios pequeños, como el logo.
const onlyPulse = (data) => ({ ...data, layers: data.layers.filter((layer) => layer.nm !== 'bg') })

function hexToUnitRgba(hex) {
  const h = hex.replace('#', '')
  const full = h.length === 3 ? h.split('').map((c) => c + c).join('') : h
  const int = parseInt(full, 16)
  return [((int >> 16) & 255) / 255, ((int >> 8) & 255) / 255, (int & 255) / 255, 1]
}

/** El archivo original es azul marino; lo repintamos al color de marca que toque. */
function recolor(data, hex) {
  const rgba = hexToUnitRgba(hex)
  const copy = structuredClone(data)
  for (const layer of copy.layers) {
    for (const group of layer.shapes ?? []) {
      for (const item of group.it ?? []) {
        if (item.ty === 'st' && item.w?.k > 0) { item.c.k = rgba; item.w.k = 8 } // línea del pulso (más fina)
        if (item.ty === 'fl') item.c.k = rgba                    // punto brillante
      }
    }
    if (layer.nm === 'bg') layer.ks.o.k = 22                     // pista tenue detrás del pulso
  }
  return copy
}

/**
 * Animación Lottie del latido (src/assets/heartbeat.json), reutilizada en el fondo
 * del login, dentro del logo y en la pantalla de carga/error.
 *
 * - `color`: repinta todo el trazo a ese color (blanco, rojo de marca, etc).
 *   Sin él se muestran los colores originales del archivo.
 * - `minimal`: quita la pista de fondo; solo queda la línea y el punto que la recorre.
 * - `className`: el consumidor decide cómo se posiciona (esta pieza no impone layout).
 */
export default function Heartbeat({ color, minimal = false, className = '' }) {
  const ref = useRef(null)
  const animationData = useMemo(() => {
    let data = withoutEffects(heartbeatData)
    if (minimal) data = onlyPulse(data)
    return color ? recolor(data, color) : data
  }, [color, minimal])

  useEffect(() => {
    const anim = lottie.loadAnimation({
      container: ref.current,
      renderer: 'svg',
      loop: true,
      autoplay: true,
      animationData,
      rendererSettings: { preserveAspectRatio: 'none' },
    })
    return () => anim.destroy()
  }, [animationData])

  return <div ref={ref} className={className} aria-hidden="true" />
}
