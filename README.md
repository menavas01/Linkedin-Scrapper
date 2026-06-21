# LinkedIn AI Job Matcher

Este proyecto es un scraper inteligente de LinkedIn impulsado por Inteligencia Artificial Local (Ollama). Analiza tu currículum, determina los mejores roles para tu perfil, extrae las ofertas más recientes de LinkedIn de forma oculta y luego las evalúa para entregarte un Top 20 definitivo.

## 🚀 Características
- **Análisis de CV con IA**: Extrae habilidades, ubicación inferida y genera de 3 a 5 roles ideales de forma automática.
- **Workflow en 2 fases**: Permite al usuario revisar y editar los parámetros antes de hacer el scraping.
- **Scraper Inteligente (Stealth)**: Utiliza `Playwright` con modo stealth para evadir los bloqueos de bots de LinkedIn. Busca siempre las ofertas **más recientes**.
- **Scoring Personalizado**: Lee la descripción completa de la oferta y la cruza con el resumen de tu CV para darte un puntaje del 0 al 100 y una breve explicación de compatibilidad.
- **Privacidad Local**: Todos los datos (incluyendo el PDF de tu CV) se procesan de forma local mediante un LLM (Ollama). Nunca se envían a APIs externas ni a la nube de terceros.
- **Interfaz Glassmorphism**: Interfaz web moderna con "drag and drop" para subir archivos y feedback en tiempo real.

## 📋 Requisitos
1. **Python 3.10+**
2. **Ollama**: Debes tener Ollama instalado y ejecutándose en tu PC.
3. Modelo IA Local: Por defecto, el proyecto usa `qwen2.5:14b` (ideal para GPUs con 12GB de VRAM como una RTX 3060). Puedes descargar el modelo usando:
   ```bash
   ollama pull qwen2.5:14b
   ```
   *(Si deseas usar otro modelo como `llama3.1`, simplemente cambia la variable `OLLAMA_MODEL` en `llm_matcher.py`)*

## 🛠️ Instalación y Uso

1. Instala las dependencias de Python:
   ```bash
   pip install -r requirements.txt
   ```
2. Instala los navegadores de Playwright:
   ```bash
   playwright install chromium
   ```
3. Ejecuta el proyecto. La forma más fácil es usando el archivo `.bat` incluido:
   ```bash
   run.bat
   ```
   *Alternativamente, puedes correr `python main.py` directamente si ya tienes el entorno virtual activado.*

4. Abre tu navegador en `http://127.0.0.1:8000`.

## 🏗️ Estructura del Proyecto
- `main.py`: Servidor FastAPI y lógica de orquestación de las fases.
- `scraper.py`: Clase de extracción de datos en LinkedIn usando `playwright-stealth`.
- `cv_parser.py`: Herramienta para extraer el texto de PDFs usando `PyPDF2`.
- `llm_matcher.py`: Integración con LangChain y Ollama para análisis y scoring.
- `static/index.html`: La Interfaz de Usuario.
- `run.bat`: Script de inicio rápido para Windows.

## ⚠️ Aviso Legal
Este proyecto fue creado únicamente con **Fines Educativos**. El web scraping en plataformas como LinkedIn puede ir en contra de sus Términos de Servicio (ToS). Los creadores y contribuidores de este repositorio no se hacen responsables por el mal uso de esta herramienta, el bloqueo de direcciones IP o de cuentas de usuario. Úselo bajo su propia responsabilidad.
