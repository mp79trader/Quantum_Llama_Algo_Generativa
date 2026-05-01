# Guía de Interpretación del Sistema de Predicción de Futuros (AI)

Este sistema ha sido diseñado para replicar la profundidad analítica del "Stock Prediction AI" original, adaptado para el mercado de futuros (MNQ, ES, etc.). A continuación se explica qué información te da cada gráfico generado en la carpeta `outputs/plots`.

## 1. Análisis de Datos y Tendencias

### 📊 `correlation_matrix.png` (Mapa de Calor de Correlaciones)
*   **Qué muestra:** La relación matemática entre tu activo (ej. MNQ) y otros mercados clave: S&P 500 (ES), Oro (GC), Petróleo (CL) y el VIX (Miedo).
*   **Cómo leerlo:**
    *   **Rojo (cerca de 1.0):** Se mueven juntos. Si el S&P sube, el Nasdaq suele subir.
    *   **Azul (cerca de -1.0):** Se mueven inversamente. Si el VIX (miedo) sube, el mercado suele caer.
    *   **Uso:** Confirma que el mercado no se mueve en el vacío.

### 🌊 `fourier_analysis.png` (Transformada de Fourier)
*   **Qué muestra:** Descompone el precio en "ondas" o tendencias puras, eliminando el ruido del día a día.
*   **Cómo leerlo:**
    *   Las líneas suaves muestran la tendencia de largo, medio y corto plazo.
    *   **Uso:** Identificar la dirección real del mercado sin distraerse por la volatilidad de una sola vela.

### 📈 `arima_forecast.png` (Proyección Estadística)
*   **Qué muestra:** Una predicción basada puramente en estadística clásica (ARIMA), sin Inteligencia Artificial.
*   **Uso:** Sirve como "Línea Base". Si la IA (GAN) no supera a esta línea, entonces no está aprendiendo nada nuevo.

## 2. Ingeniería de Características (Feature Engineering)

### 🧠 `feature_importance.png` (Análisis XGBoost)
*   **Qué muestra:** Un ranking de qué indicadores son los más importantes para predecir el precio.
*   **Cómo leerlo:** Las barras más largas son las variables que más "mira" el modelo.
    *   Si `RSI` o `VIX` están arriba, el mercado es técnico/emocional.
    *   Si `Volume` está arriba, el mercado se mueve por flujo de dinero.

### 📉 `sentiment_analysis.png` (Precio vs Miedo/VIX)
*   **Qué muestra:** La comparación directa entre el precio del activo y el Índice de Volatilidad (VIX).
*   **Uso:** Detectar techos y suelos de mercado. Generalmente, cuando el VIX hace un pico máximo, el mercado hace un suelo (pánico máximo = oportunidad de compra).

## 3. Entrenamiento de la IA (GAN)

### 📉 `training_losses.png` (Generador vs Discriminador)
*   **Qué muestra:** La "batalla" entre las dos redes neuronales.
*   **Cómo leerlo:**
    *   No busques que el error llegue a cero.
    *   Busca **estabilidad**. Si una línea se dispara y la otra cae a cero, el entrenamiento falló (colapso modal). Lo ideal es que ambas oscilen en equilibrio.

### 📸 `snapshot_epoch_X.png` (Evolución del Aprendizaje)
*   **Qué muestra:** Cómo la IA intenta dibujar el precio futuro en diferentes etapas del entrenamiento.
*   **Uso:** Verás cómo al principio (Epoca 0) es una línea aleatoria, y cómo poco a poco empieza a copiar los patrones del mercado real.

## 4. Evolución del Aprendizaje (Time Travel)

El sistema ahora genera "instantáneas" en momentos clave para que veas cómo la IA va aprendiendo, tal como se muestra en el repositorio original:

*   **`prediction_epoch_1.png`:** El "bebé" IA. Verás una línea casi aleatoria o muy simple. Apenas está empezando a entender qué es un precio.
*   **`prediction_epoch_50.png`:** La "adolescencia". Ya debería seguir la tendencia general, aunque quizás falle en los picos exactos.
*   **`prediction_epoch_200.png`:** La "madurez". Si entrenas suficientes épocas, aquí verás un ajuste mucho más fino.
*   **`prediction_final.png`:** El resultado definitivo tras todo el entrenamiento.

### 🔮 `gaussian_process.png` (La Línea Base Probabilística)
*   **Qué muestra:** Una predicción basada en **Procesos Gaussianos**.
*   **La Clave:** Fíjate en el **área sombreada (naranja)**. Representa el intervalo de confianza (95%).
    *   Si el precio real se sale de la sombra, ocurrió algo "estadísticamente improbable" (cisne negro).
    *   Este gráfico es el "rival" a batir por la GAN.

## 5. Métricas Finales (En la Terminal)

*   **RMSE (Error Cuadrático Medio):** Cuánto se desvía el precio predicho del real (en puntos).
*   **MAPE (Error Porcentual):** El % de error promedio. Un MAPE bajo (ej. < 1-2%) es excelente para futuros.

---
**Nota:** Este sistema utiliza el VIX como proxy de "Sentimiento de Mercado" en lugar de noticias de Google Trends/Twitter, ya que ofrece una correlación matemática más robusta y accesible en tiempo real para trading profesional.
