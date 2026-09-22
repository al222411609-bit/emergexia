/**
 * Reconocimiento facial en el navegador con face-api.js (https://github.com/justadudewhohacks/face-api.js).
 *
 * IMPORTANTE — instalación manual de los modelos:
 * face-api.js necesita unos archivos de modelo (pesos ya entrenados) que NO vienen en este
 * repositorio porque pesan varios MB. Descárgalos una sola vez desde:
 *   https://github.com/justadudewhohacks/face-api.js/tree/master/weights
 * y copia TODOS los archivos de esa carpeta a:
 *   frontend/public/models/
 * (deben quedar como frontend/public/models/tiny_face_detector_model-weights_manifest.json, etc.)
 *
 * También hay que cargar el script de face-api.js. Ya se agregó en index.html vía CDN
 * (https://cdn.jsdelivr.net/npm/face-api.js@0.22.2/dist/face-api.min.js), así que no hace falta
 * instalar nada con npm.
 *
 * Umbral de coincidencia: face-api.js recomienda 0.6 de distancia euclidiana como límite entre
 * "misma persona" / "personas distintas". Aquí usamos 0.55 para ser un poco más estrictos,
 * dado que es un sistema de emergencias.
 */

const MODELS_URL = '/models'
export const MATCH_THRESHOLD = 0.55

let modelsPromise = null

function faceapi() {
  if (!window.faceapi) {
    throw new Error(
      'No se pudo cargar face-api.js (revisa tu conexión a internet o que el <script> siga en index.html).',
    )
  }
  return window.faceapi
}

/** Carga los modelos una sola vez (memoiza la promesa). Lanza un error explicativo si faltan los pesos. */
export function loadFaceModels() {
  if (!modelsPromise) {
    const fa = faceapi()
    modelsPromise = Promise.all([
      fa.nets.tinyFaceDetector.loadFromUri(MODELS_URL),
      fa.nets.faceLandmark68Net.loadFromUri(MODELS_URL),
      fa.nets.faceRecognitionNet.loadFromUri(MODELS_URL),
    ]).catch((err) => {
      modelsPromise = null
      throw new Error(
        'Faltan los archivos de modelo de reconocimiento facial en frontend/public/models/. ' +
        'Descárgalos de https://github.com/justadudewhohacks/face-api.js/tree/master/weights ' +
        `(detalle técnico: ${err?.message || err})`,
      )
    })
  }
  return modelsPromise
}

/**
 * Detecta una sola cara en una imagen/video/canvas y devuelve su "descriptor" (vector de 128
 * números que representa el rostro). Devuelve null si no se detectó ninguna cara.
 */
export async function getFaceDescriptor(mediaElement) {
  await loadFaceModels()
  const fa = faceapi()
  const result = await fa
    .detectSingleFace(mediaElement, new fa.TinyFaceDetectorOptions())
    .withFaceLandmarks()
    .withFaceDescriptor()
  return result?.descriptor ?? null
}

/** Carga una foto en base64 (data URL) en un <img> oculto en memoria, para poder analizarla. */
export function dataUrlToImage(dataUrl) {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => resolve(img)
    img.onerror = () => reject(new Error('No se pudo leer la fotografía.'))
    img.src = dataUrl
  })
}

/** Distancia euclidiana entre dos descriptores; entre más chica, más se parecen las caras. */
export function faceDistance(descriptorA, descriptorB) {
  return faceapi().euclideanDistance(descriptorA, descriptorB)
}

/** true si la distancia está por debajo del umbral de "misma persona". */
export function isSamePerson(distance) {
  return distance <= MATCH_THRESHOLD
}
