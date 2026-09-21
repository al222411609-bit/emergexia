import { useId } from 'react'

/** Cruz médica con línea de pulso. `tone="light"` = cruz blanca sobre fondo rojo. */
export function LogoMark({ size = 40, tone = 'light' }) {
  const id = useId()
  const cross = tone === 'light' ? '#fff' : '#b3111f'
  const pulse = tone === 'light' ? '#b3111f' : '#fff'
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" aria-hidden="true">
      <defs>
        <clipPath id={id}>
          <path d="M23 6h18v17h17v18H41v17H23V41H6V23h17z" />
        </clipPath>
      </defs>
      <path
        fill={cross}
        stroke={cross}
        strokeLinejoin="round"
        strokeWidth="4"
        d="M23 6h18v17h17v18H41v17H23V41H6V23h17z"
      />
      <path
        d="M8 33h13l5-10 8 22 5-12h17"
        fill="none"
        stroke={pulse}
        strokeWidth="3.4"
        strokeLinecap="round"
        strokeLinejoin="round"
        clipPath={`url(#${id})`}
      />
    </svg>
  )
}

export function Logo({ size = 40, tone = 'light', className = '' }) {
  return (
    <div className={`logo ${tone} ${className}`}>
      <LogoMark size={size} tone={tone} />
      <span className="logo-text" style={{ fontSize: size * 0.72 }}>Emergexia</span>
    </div>
  )
}
