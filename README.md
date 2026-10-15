# Tesdo

Tesdo es una red social que combina YouTube con TikTok 

## Caracteristicas

| Funcion | Descripción |
|---|---|
|  **Feed estilo TikTok** | Scroll vertical con tarjetas grandes |
|  **Biblioteca estilo YouTube** | Rejilla de 3 columnas ordenada por tendencias |
|  **Subir videos** | Archivo local **o** URL (MP4 directo) |
|  **Miniaturas personalizadas** | Sube tu propia portada (PNG / GIF / PPM) |
|  **Seguir usuarios** | Con contador de seguidores y pestaña "Siguiendo" |
|  **Reproductor integrado** | Usa `ffmpeg` si está disponible |
|  **Comentarios** | Ventana aparte con historial persistente |
|  **Likes** | Se recuerdan entre sesiones |
|  **Buscador** | Filtra por título, descripción o autor |
|  **10 idiomas** | ES · EN · FR · DE · IT · PT · RU · JA · ZH · AR |
|  **Personalización total** | Tema oscuro/claro, 7 colores preset + selector libre |
|  **Autocontenido** | Crea su carpeta `TesdoData/` sola al primer arranque |

## instalacion

### Requisitos

- ✅ **Python 3.14** (o superior)
- ✅ **`tkinter`** (viene con Python en Windows/macOS; en Linux: `sudo apt install python3-tk`)
- ❌ **Nada de `pip install`** — solo biblioteca estándar
- ⚙️ *(Opcional)* **`ffmpeg`** para el reproductor interno

## Estructura

```bash
Tesdo/
├── main.py            ← Todo el programa (un solo archivo)
├── README.md
└── TesdoData/         ← Se crea sola al primer arranque
    ├── tesdo.db       ← Base de datos SQLite (videos, comentarios, follows)
    ├── config.json    ← Preferencias (idioma, tema, color, usuario)
    ├── LEEME.txt
    ├── media/         ← Copias de videos subidos
    └── thumbs/        ← Copias de miniaturas subidas
```
