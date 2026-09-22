import { Component } from 'react'
import BrandLoader from './BrandLoader.jsx'

/**
 * Red de seguridad para errores de renderizado que React no puede recuperar solo.
 * Sin esto, un error inesperado deja la pantalla en blanco; con esto, el usuario
 * ve la misma pantalla roja de "algo salió mal" con un botón para reintentar.
 */
export default class ErrorBoundary extends Component {
  state = { error: null }

  static getDerivedStateFromError(error) {
    return { error }
  }

  componentDidCatch(error, info) {
    // eslint-disable-next-line no-console
    console.error('Error no controlado en la interfaz:', error, info?.componentStack)
  }

  render() {
    if (this.state.error) {
      return (
        <BrandLoader
          mode="error"
          message="La página no pudo cargar"
          detail="Ocurrió un error inesperado. Intenta recargar; si el problema sigue, revisa la consola del navegador."
          onRetry={() => window.location.reload()}
        />
      )
    }
    return this.props.children
  }
}
