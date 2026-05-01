# 🦙 Quantum Llama: Algoritmo de Trading Generativo para Futuros

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-%23EE4C2C.svg?style=flat&logo=PyTorch&logoColor=white)](https://pytorch.org/)

**Quantum Llama** es un ecosistema avanzado de predicción y trading automático para mercados de futuros (MNQ, ES, MES, etc.) basado en **Redes Generativas Antagónicas (GAN)**. El sistema combina el poder de las redes recurrentes (LSTM) para capturar la memoria del mercado con redes convolucionales (CNN) para identificar patrones micro-estructurales.

---

## 🚀 Características Principales

- **Arquitectura Híbrida GAN:** Utiliza un Generador LSTM y un Discriminador CNN para modelar series temporales financieras complejas.
- **Ingeniería de Características Avanzada:**
    - Transformada de Fourier para descomposición de tendencias.
    - Análisis de Sentimiento Macro mediante modelos BERT (NLP). 
    - Autoencoders para extracción de características latentes.
    - Análisis de correlación intermercado (VIX, GC, CL).
- **Optimización Dinámica:** Implementa Aprendizaje por Refuerzo (PPO/Rainbow) para el ajuste dinámico de hiperparámetros.
- **Trading en Vivo:** Conectores nativos para **MetaTrader 5** y **NinjaTrader 8**.
- **Dashboard Interactivo:** Visualización en tiempo real de predicciones, señales de trading y métricas de salud del modelo.

---

## 📂 Estructura del Proyecto

```text
├── src/
│   ├── analysis/       # Backtesting y filtrado de mercado
│   ├── config/         # Configuración de símbolos y parámetros live
│   ├── data/           # Cargadores de datos y preprocesamiento
│   ├── features/       # Indicadores técnicos, Fourier y Autoencoders
│   ├── live/           # Conectores y lógica de ejecución en vivo
│   ├── models/         # Arquitecturas GAN (Generator, Discriminator)
│   ├── optimization/   # Agentes de Reinforcement Learning
│   └── utils/          # Visualización y generadores de dashboard
├── outputs/            # Modelos entrenados, plots y reportes
├── NinjaTrader/        # Scripts de conexión para NT8
├── train.py            # Script principal de entrenamiento
└── run.py              # Punto de entrada de la aplicación
```

---

## 🛠️ Instalación y Configuración

### Requisitos Previos

- Python 3.10 o superior.
- MetaTrader 5 (opcional para trading en vivo).
- NinjaTrader 8 (opcional para ejecución asistida).

### Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/mp79trader/Quantum_Llama_Algo_Generativa.git
   cd Quantum_Llama_Algo_Generativa
   ```

2. Crear un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Linux/macOS
   # o
   venv\Scripts\activate     # En Windows
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

---

## 📈 Flujo de Trabajo

### 1. Entrenamiento
El sistema requiere un entrenamiento previo para cada activo y temporalidad.
```bash
python train.py --symbol MNQ=F --timeframe 15m --epochs 200
```

### 2. Análisis y Verificación
Consulta los gráficos generados en `outputs/plots/` para verificar la convergencia del modelo:
- `training_losses.png`: Estabilidad de la competencia GAN.
- `prediction_final.png`: Ajuste del modelo sobre los datos de validación.
- `fourier_analysis.png`: Descomposición cíclica del precio.

### 3. Ejecución en Vivo
Configura el mapeo de símbolos en `src/config/symbols.json` y ejecuta:
```bash
python run.py
```
Selecciona la opción **4. Trading en Vivo** para iniciar la monitorización y ejecución automática.

---

## 🛡️ Descargo de Responsabilidad

El trading de futuros e instrumentos financieros conlleva un alto nivel de riesgo. **Quantum Llama** es una herramienta de investigación y apoyo; el usuario es el único responsable de las decisiones ejecutadas en cuentas reales. Resultados pasados no garantizan rendimientos futuros.

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - mira el archivo [LICENSE](LICENSE) para más detalles.

---
Desarrollado con ❤️ para la comunidad de trading algorítmico.
