# Documentación de la Calculadora de Radioenlaces

## Resumen del Proyecto
La Calculadora de Radioenlaces es una herramienta desarrollada en Python diseñada para calcular parámetros críticos en el diseño y análisis de enlaces de comunicación punto a punto. Al proporcionar las coordenadas (latitud y longitud en grados decimales) del transmisor y receptor, junto con parámetros adicionales como frecuencia, alturas de antenas y factores ambientales, la calculadora genera métricas clave para garantizar un rendimiento óptimo del enlace. La herramienta se empaqueta como un ejecutable independiente (.exe) para facilitar su uso en sistemas Windows.

Esta documentación cubre las fórmulas teóricas, detalles de implementación e instrucciones para ejecutar la calculadora.

---

## Tabla de Contenidos
1. [Características](#características)
2. [Parámetros de Entrada](#parámetros-de-entrada)
3. [Parámetros de Salida y Fórmulas](#parámetros-de-salida-y-fórmulas)
4. [Requisitos del Sistema](#requisitos-del-sistema)
5. [Instalación y Configuración](#instalación-y-configuración)
6. [Instrucciones de Uso](#instrucciones-de-uso)
7. [Estructura del Código](#estructura-del-código)
8. [Creación del Ejecutable](#creación-del-ejecutable)
9. [Ejemplo de Uso](#ejemplo-de-uso)
10. [Limitaciones y Suposiciones](#limitaciones-y-suposiciones)
11. [Mejoras Futuras](#mejoras-futuras)

---

## Parámetros de Salida y Fórmulas
A continuación, se detallan las definiciones de los parámetros de salida, su importancia y las fórmulas utilizadas para calcularlos, presentadas en un formato optimizado para claridad y compatibilidad con renderizadores de Markdown.

### 1. Azimut
**Definición**: Dirección horizontal desde el transmisor hacia el receptor, medida en el sentido de las agujas del reloj desde el norte verdadero (0°) en grados.

**Fórmula**:
$$
\text{Azimut} = \arctan2\left(\sin(\Delta\lambda) \cos(\phi_2), \cos(\phi_1) \sin(\phi_2) - \sin(\phi_1) \cos(\phi_2) \cos(\Delta\lambda)\right) \cdot \frac{180}{\pi}
$$
**Variables**:
- $\phi_1, \lambda_1$: Latitud y longitud del transmisor (radianes).
- $\phi_2, \lambda_2$: Latitud y longitud del receptor (radianes).
- $\Delta\lambda = \lambda_2 - \lambda_1$: Diferencia en longitud.
- Normalizado a $[0, 360^\circ]$.

### 2. Ángulo de Elevación
**Definición**: Ángulo vertical de la línea de visión entre transmisor y receptor. Un valor negativo indica que el receptor está por debajo del transmisor.

**Fórmula**:
$$
\text{Ángulo de Elevación} = \arctan\left(\frac{h_2 - h_1}{d}\right) \cdot \frac{180}{\pi}
$$
**Variables**:
- $h_1$: Altura de la antena del transmisor (m).
- $h_2$: Altura de la antena del receptor (m).
- $d$: Distancia entre transmisor y receptor (m).

### 3. Despeje (Clearance)
**Definición**: Distancia desde el transmisor hasta el punto más crítico del trayecto con despeje mínimo, considerando terreno y obstáculos.

**Fórmula**: No calculada directamente; requiere datos de perfil del terreno (ej., modelo de elevación digital, DEM).
**Nota**: En esta versión, se asume entrada del usuario o datos externos.

### 4. Peor Fresnel (Worst Fresnel)
**Definición**: Fracción de la primera zona de Fresnel libre de obstrucciones. Un valor $< 1$ indica obstrucción parcial.

**Fórmulas**:
$$
r_1 = \sqrt{\frac{\lambda d_1 d_2}{d_1 + d_2}}
$$
$$
\text{Despeje Fresnel} = \frac{h_{\text{despeje}}}{r_1}
$$
**Variables**:
- $r_1$: Radio de la primera zona de Fresnel (m).
- $\lambda = \frac{c}{f}$: Longitud de onda (m), con $c = 3 \times 10^8 \, \text{m/s}$, $f$ en Hz.
- $d_1, d_2$: Distancias desde transmisor y receptor al punto de obstrucción (m).
- $h_{\text{despeje}}$: Altura de despeje sobre la obstrucción (m).
- Recomendado: $0.6$–$0.8$ para enlaces confiables.

### 5. Distancia
**Definición**: Distancia de gran círculo entre transmisor y receptor.

**Fórmulas** (Haversine):
$$
a = \sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1) \cos(\phi_2) \sin^2\left(\frac{\Delta\lambda}{2}\right)
$$
$$
d = R \cdot 2 \cdot \arctan2\left(\sqrt{a}, \sqrt{1-a}\right)
$$
**Variables**:
- $\Delta\phi = \phi_2 - \phi_1$, $\Delta\lambda = \lambda_2 - \lambda_1$.
- $R = 6371 \, \text{km}$: Radio medio de la Tierra.
- Salida en metros.

### 6. Espacio Libre (Pérdida por Espacio Libre)
**Definición**: Pérdida de señal debido a la propagación en espacio libre.

**Fórmula**:
$$
\text{FSL} = 20 \log_{10}(d) + 20 \log_{10}(f) + 20 \log_{10}\left(\frac{4\pi}{c}\right)
$$
**Variables**:
- $d$: Distancia (m).
- $f$: Frecuencia (Hz).
- $c = 3 \times 10^8 \, \text{m/s}$.
- Salida en dB.

### 7. Obstrucción (Pérdida por Obstrucción)
**Definición**: Pérdida adicional por terreno u obstáculos.

**Fórmula**: Depende del perfil del terreno; modelado con difracción de borde de cuchillo o modelos empíricos (ej., ITU-R P.526).
**Nota**: Versión básica asume entrada del usuario o $0 \, \text{dB}$.

### 8. Urbano (Pérdida Urbana)
**Definición**: Pérdida por estructuras urbanas.

**Fórmula**: Especificada por el usuario o modelada con modelos empíricos (ej., COST-231).
**Predeterminado**: $0 \, \text{dB}$ (sin áreas urbanas).

### 9. Bosque (Pérdida Forestal)
**Definición**: Pérdida por vegetación.

**Fórmula**: Especificada por el usuario o modelada con ITU-R P.833.
**Predeterminado**: $0 \, \text{dB}$ (sin áreas forestales).

### 10. Estadísticas (Margen Estadístico)
**Definición**: Margen para desvanecimientos, lluvia y otras variaciones.

**Fórmula**: Especificado por el usuario (ej., $10 \, \text{dB}$).
**Nota**: Sumado a las pérdidas totales.

### 11. Pérdidas (Pérdidas Totales)
**Definición**: Suma de todas las pérdidas del enlace.

**Fórmula**:
$$
\text{Pérdidas Totales} = \text{FSL} + \text{Pérdida por Obstrucción} + \text{Pérdida Urbana} + \text{Pérdida Forestal} + \text{Margen Estadístico}
$$
**Salida**: dB.

### 12. Campo E (Intensidad del Campo Eléctrico)
**Definición**: Intensidad del campo eléctrico en el receptor.

**Fórmula**:
$$
E = 20 \log_{10}\left(\frac{\sqrt{30 P_t G_t}}{d}\right) + 20 \log_{10}\left(\frac{c}{f}\right)
$$
**Variables**:
- $P_t$: Potencia del transmisor (W).
- $G_t$: Ganancia de la antena del transmisor (lineal).
- $d$: Distancia (m).
- $f$: Frecuencia (Hz).
- Salida en $\text{dB}\mu\text{V}/\text{m}$.

### 13. Nivel Rx (Potencia Recibida en dBm)
**Definición**: Potencia de la señal en el receptor.

**Fórmula**:
$$
P_r = P_t + G_t + G_r - \text{Pérdidas Totales}
$$
**Variables**:
- $P_t$: Potencia del transmisor (dBm).
- $G_t, G_r$: Ganancias de antenas (dBi).
- Salida en dBm.

### 14. Nivel Rx (Potencia Recibida en μV)
**Definición**: Potencia recibida en microvoltios.

**Fórmula**:
$$
V_r = 10^{\frac{P_r + 107}{20}}
$$
**Variables**:
- $P_r$: Potencia recibida (dBm).
- Salida en $\mu\text{V}$.

### 15. Rx Relativo (Nivel Rx Relativo)
**Definición**: Margen por encima de la sensibilidad del receptor.

**Fórmula**:
$$
\text{Rx Relativo} = P_r - P_{\text{sensibilidad}}
$$
**Variables**:
- $P_r$: Potencia recibida (dBm).
- $P_{\text{sensibilidad}}$: Sensibilidad del receptor (dBm).
- Salida en dB.

---

## Notas sobre Renderización
- Las fórmulas están escritas en LaTeX y envueltas en `$$` para ecuaciones en bloque, lo que garantiza una renderización clara en plataformas compatibles (ej., GitHub, VS Code con extensiones Markdown, o editores como Obsidian).
- Si las fórmulas no se renderizan correctamente, verifica que tu visor de Markdown soporte LaTeX. En GitHub, las ecuaciones LaTeX no se renderizan nativamente en `.md`, pero puedes usar un visor externo o convertir el archivo a HTML/PDF con herramientas como Pandoc.
- Para mejorar la legibilidad en entornos sin soporte LaTeX, considera generar un PDF con las fórmulas renderizadas usando herramientas como `pandoc` con `latex`.

Si necesitas que integre el resto del documento, modifique otras secciones, o genere un formato alternativo (ej., PDF con fórmulas renderizadas), por favor indícalo. También puedo proporcionar una versión sin LaTeX si prefieres un formato más simple para entornos sin soporte de ecuaciones.
