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

## Características
- Calcula parámetros esenciales de radioenlaces como azimut, ángulo de elevación, pérdidas por espacio libre y potencia recibida.
- Considera factores ambientales como pérdidas urbanas y forestales.
- Proporciona resultados detallados para la fiabilidad del enlace, incluyendo despeje de la zona de Fresnel y márgenes estadísticos.
- Interfaz de línea de comandos amigable para ingresar coordenadas y parámetros.
- Presenta resultados en un formato tabulado claro.
- Empaquetada como un .exe independiente para distribución y ejecución sencilla en Windows.

---

## Parámetros de Entrada
La calculadora requiere las siguientes entradas:
- **Coordenadas del Transmisor**: Latitud y longitud en grados decimales (ej., 40.7128, -74.0060).
- **Coordenadas del Receptor**: Latitud y longitud en grados decimales.
- **Frecuencia**: Frecuencia operativa del enlace en MHz (ej., 2400 MHz para 2.4 GHz).
- **Altura de la Antena del Transmisor**: Altura sobre el suelo en metros.
- **Altura de la Antena del Receptor**: Altura sobre el suelo en metros.
- **Potencia del Transmisor**: Potencia de salida en dBm.
- **Ganancias de Antenas**: Ganancia de las antenas del transmisor y receptor en dBi.
- **Factores Ambientales**:
  - Pérdida urbana (dB, predeterminado 0 para áreas no urbanas).
  - Pérdida forestal (dB, predeterminado 0 para áreas sin bosques).
- **Margen Estadístico**: Margen adicional para desvanecimientos, lluvia, etc., en dB (ej., 10 dB).
- **Sensibilidad del Receptor**: Nivel mínimo de señal que el receptor puede detectar, en dBm (ej., -90 dBm).

---

## Parámetros de Salida y Fórmulas
A continuación, se detallan las definiciones de los parámetros de salida, su importancia y las fórmulas utilizadas para calcularlos.

### 1. Azimut
**Definición**: La dirección horizontal desde el transmisor hacia el receptor, medida en el sentido de las agujas del reloj desde el norte verdadero (0°) en grados.
**Fórmula**:
\[
\text{Azimut} = \text{atan2}\left(\sin(\Delta \lambda) \cdot \cos(\phi_2), \cos(\phi_1) \cdot \sin(\phi_2) - \sin(\phi_1) \cdot \cos(\phi_2) \cdot \cos(\Delta \lambda)\right) \cdot \frac{180}{\pi}
\]
Donde:
- \(\phi_1, \lambda_1\): Latitud y longitud del transmisor (radianes).
- \(\phi_2, \lambda_2\): Latitud y longitud del receptor (radianes).
- \(\Delta \lambda = \lambda_2 - \lambda_1\): Diferencia en longitud.
- El resultado se normaliza a [0, 360°].

### 2. Ángulo de Elevación
**Definición**: El ángulo vertical de la línea de visión entre transmisor y receptor, considerando alturas de antenas y terreno. Un valor negativo indica que el receptor está por debajo del transmisor.
**Fórmula**:
\[
\text{Ángulo de Elevación} = \arctan\left(\frac{h_2 - h_1}{d}\right) \cdot \frac{180}{\pi}
\]
Donde:
- \(h_1\): Altura de la antena del transmisor (m).
- \(h_2\): Altura de la antena del receptor (m).
- \(d\): Distancia entre transmisor y receptor (m).

### 3. Despeje (Clearance)
**Definición**: La distancia desde el transmisor hasta el punto más crítico del trayecto donde el despeje es mínimo, considerando terreno y obstáculos.
**Fórmula**: Requiere datos de perfil del terreno (no calculado directamente en la versión básica; asume entrada del usuario o datos DEM externos).
**Nota**: En la práctica, requiere un modelo de elevación digital (DEM) para identificar el punto de despeje mínimo.

### 4. Peor Fresnel (Worst Fresnel)
**Definición**: La fracción de la primera zona de Fresnel libre de obstrucciones. Un valor < 1 indica obstrucción parcial.
**Fórmula**:
\[
r_n = \sqrt{\frac{\lambda \cdot d_1 \cdot d_2}{d_1 + d_2}}
\]
\[
\text{Despeje Fresnel} = \frac{h_{\text{despeje}}}{r_1}
\]
Donde:
- \(r_1\): Radio de la primera zona de Fresnel (m).
- \(\lambda\): Longitud de onda (m), \(\lambda = \frac{c}{f}\), \(c = 3 \times 10^8 \, \text{m/s}\), \(f\) en Hz.
- \(d_1, d_2\): Distancias desde el transmisor y receptor hasta el punto de obstrucción (m).
- \(h_{\text{despeje}}\): Altura de despeje sobre la obstrucción (m).
- Se recomienda un valor de 0.6–0.8 para enlaces confiables.

### 5. Distancia
**Definición**: La distancia de gran círculo entre transmisor y receptor.
**Fórmula** (Fórmula de Haversine):
\[
a = \sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1) \cdot \cos(\phi_2) \cdot \sin^2\left(\frac{\Delta \lambda}{2}\right)
\]
\[
d = R \cdot 2 \cdot \arctan2\left(\sqrt{a}, \sqrt{1-a}\right)
\]
Donde:
- \(\Delta \phi = \phi_2 - \phi_1\), \(\Delta \lambda = \lambda_2 - \lambda_1\).
- \(R = 6371 \, \text{km}\): Radio medio de la Tierra.
- Salida en metros.

### 6. Espacio Libre (Pérdida por Espacio Libre)
**Definición**: Pérdida de señal debido a la propagación en espacio libre.
**Fórmula**:
\[
\text{FSL} = 20 \cdot \log_{10}(d) + 20 \cdot \log_{10}(f) + 20 \cdot \log_{10}\left(\frac{4\pi}{c}\right)
\]
Donde:
- \(d\): Distancia (m).
- \(f\): Frecuencia (Hz).
- \(c = 3 \times 10^8 \, \text{m/s}\).
- Salida en dB.

### 7. Obstrucción (Pérdida por Obstrucción)
**Definición**: Pérdida adicional debido a terreno u obstáculos.
**Fórmula**: Depende del perfil del terreno; típicamente modelado con difracción de borde de cuchillo o modelos empíricos (ej., ITU-R P.526).
**Nota**: La versión básica asume entrada del usuario o cero si no hay obstrucciones.

### 8. Urbano (Pérdida Urbana)
**Definición**: Pérdida debido a estructuras urbanas.
**Fórmula**: Especificada por el usuario o modelada con modelos empíricos (ej., COST-231).
**Predeterminado**: 0 dB (sin áreas urbanas).

### 9. Bosque (Pérdida Forestal)
**Definición**: Pérdida debido a vegetación.
**Fórmula**: Especificada por el usuario o modelada con ITU-R P.833.
**Predeterminado**: 0 dB (sin áreas forestales).

### 10. Estadísticas (Margen Estadístico)
**Definición**: Margen adicional para desvanecimientos, lluvia y otras variaciones.
**Fórmula**: Especificado por el usuario (ej., 10 dB).
**Nota**: Se suma a las pérdidas totales.

### 11. Pérdidas (Pérdidas Totales)
**Definición**: Suma de todas las pérdidas que afectan el enlace.
**Fórmula**:
\[
\text{Pérdidas Totales} = \text{FSL} + \text{Pérdida por Obstrucción} + \text{Pérdida Urbana} + \text{Pérdida Forestal} + \text{Margen Estadístico}
\]
Salida en dB.

### 12. Campo E (Intensidad del Campo Eléctrico)
**Definición**: Intensidad del campo eléctrico en el receptor.
**Fórmula**:
\[
E = 20 \cdot \log_{10}\left(\frac{\sqrt{30 \cdot P_t \cdot G_t}}{d}\right) + 20 \cdot \log_{10}\left(\frac{c}{f}\right)
\]
Donde:
- \(P_t\): Potencia del transmisor (W).
- \(G_t\): Ganancia de la antena del transmisor (lineal).
- \(d\): Distancia (m).
- \(f\): Frecuencia (Hz).
- Salida en dBμV/m.

### 13. Nivel Rx (Potencia Recibida en dBm)
**Definición**: Potencia de la señal en el receptor.
**Fórmula**:
\[
P_r = P_t + G_t + G_r - \text{Pérdidas Totales}
\]
Donde:
- \(P_t\): Potencia del transmisor (dBm).
- \(G_t, G_r\): Ganancias de las antenas del transmisor y receptor (dBi).
- Salida en dBm.

### 14. Nivel Rx (Potencia Recibida en μV)
**Definición**: Potencia recibida en microvoltios.
**Fórmula**:
\[
V_r = 10^{\frac{P_r + 107}{20}}
\]
Donde:
- \(P_r\): Potencia recibida (dBm).
- Salida en μV.

### 15. Rx Relativo (Nivel Rx Relativo)
**Definición**: Margen por encima de la sensibilidad del receptor.
**Fórmula**:
\[
\text{Rx Relativo} = P_r - P_{\text{sensibilidad}}
\]
Donde:
- \(P_r\): Potencia recibida (dBm).
- \(P_{\text{sensibilidad}}\): Sensibilidad del receptor (dBm).
- Salida en dB.

---

## Requisitos del Sistema
- **Sistema Operativo**: Windows 10 o superior (para .exe).
- **Versión de Python**: Python 3.8+ (para desarrollo).
- **Dependencias**:
  - `math` (biblioteca estándar)
  - `tabulate` (para salida formateada)
  - `pyinstaller` (para crear .exe)
- **Hardware**: Requisitos mínimos (1 GB RAM, 100 MB de almacenamiento).

---

## Instalación y Configuración
Una forma fácil de usar la calculadora es ejecutar el archivo `RadioLinkCalculator.exe` incluido en la carpeta del proyecto, lo que no requiere instalación de Python ni dependencias. Para usuarios que deseen modificar el código o desarrollarlo, sigue estos pasos:

1. **Instalar Python** (si se desea desarrollar o modificar el código):
   - Descarga e instala Python 3.8+ desde [python.org](https://www.python.org/downloads/).
   - Asegúrate de que `pip` esté instalado.
2. **Instalar Dependencias**:
   ```bash
   pip install tabulate pyinstaller
