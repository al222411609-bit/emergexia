import { useId } from 'react'

const CROSS_PATH = 'M23 6h18v17h17v18H41v17H23V41H6V23h17z'
const PULSE_PATH = 'M8 33h13l5-10 8 22 5-12h17'

/**
 * Cruz médica con un barrido de pulso animado por dentro.
 * Todo vive en un único <svg> (sin Lottie ni recortes sobre elementos HTML), así
 * que se ve igual de bien a 20px que a 80px y no depende de medir contenedores.
 * `tone="light"` = cruz blanca sobre fondo rojo (barra lateral, login).
 * `animated={false}` deja el trazo del pulso fijo, sin barrido.
 */
export function LogoMark({ size = 40, tone = 'light', animated = true }) {
  const clipId = useId()
  const cross = tone === 'light' ? '#fff' : '#b3111f'
  const pulse = tone === 'light' ? '#b3111f' : '#fff'

  return (
    <svg width={size} height={size} viewBox="0 0 64 64" aria-hidden="true" className="logo-mark">
      <defs>
        <clipPath id={clipId}>
          <path d={CROSS_PATH} />
        </clipPath>
      </defs>
      <path fill={cross} stroke={cross} strokeLinejoin="round" strokeWidth="4" d={CROSS_PATH} />
      <g clipPath={`url(#${clipId})`}>
        {/* Trazo base, tenue: el contorno del pulso siempre visible. */}
        <path d={PULSE_PATH} fill="none" stroke={pulse} strokeOpacity=".32" strokeWidth="3.4"
              strokeLinecap="round" strokeLinejoin="round" />
        {/* Segmento brillante que recorre el mismo trazo en bucle. `pathLength="100"`
            normaliza el largo real del path a 100 unidades, para que el dasharray
            funcione igual sin importar el tamaño del logo. */}
        {animated && (
          <path
            className="logo-pulse-sweep"
            d={PULSE_PATH}
            fill="none"
            stroke={pulse}
            strokeWidth="3.4"
            strokeLinecap="round"
            strokeLinejoin="round"
            pathLength="100"
          />
        )}
      </g>
    </svg>
  )
}

export function Logo({ size = 40, tone = 'light', className = '', animated = true }) {
  return (
    <div className={`logo ${tone} ${className}`}>
      <LogoMark size={size} tone={tone} animated={animated} />
      <span className="logo-text" style={{ fontSize: size * 0.72 }}>Emergexia</span>
    </div>
  )
}
