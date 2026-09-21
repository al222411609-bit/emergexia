import { useEffect, useMemo, useRef } from 'react'
// Versión ligera de lottie-web: solo SVG, sin expresiones ni eval() (más pequeña y compatible con CSP).
import lottie from 'lottie-web/build/player/lottie_light'
import heartbeatData from '../assets/heartbeat.json'

const WHITE = [1, 1, 1, 1]

// Las capas "blur" usan el efecto Gaussian Blur, que la versión ligera no soporta:
// se descartan y el resplandor lo aporta el drop-shadow de CSS (.brand-ecg).
const withoutEffects = (data) => ({ ...data, layers: data.layers.filter((layer) => !layer.ef) })

/**
 * Animación Lottie del latido (src/assets/heartbeat.json).
 * El archivo original es azul marino; sobre el panel rojo se pinta de blanco.
 * Para ver los colores originales usa <Heartbeat recolor={false} />.
 */
function toWhite(data) {
  const copy = structuredClone(data)
  for (const layer of copy.layers) {
    for (const group of layer.shapes ?? []) {
      for (const item of group.it ?? []) {
        if (item.ty === 'st' && item.w?.k > 0) { item.c.k = WHITE; item.w.k = 8 } // línea del pulso (más fina)
        if (item.ty === 'fl') item.c.k = WHITE                  // punto brillante
      }
    }
    if (layer.nm === 'bg') layer.ks.o.k = 22                    // pista tenue detrás del pulso
  }
  return copy
}

export default function Heartbeat({ recolor = true, className = '' }) {
  const ref = useRef(null)
  const animationData = useMemo(() => {
    const base = withoutEffects(heartbeatData)
    return recolor ? toWhite(base) : base
  }, [recolor])

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

  return <div ref={ref} className={`brand-ecg ${className}`} aria-hidden="true" />
}
