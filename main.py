# -*- coding: utf-8 -*-
"""
==========================================================
  TESDO — Red social de video (YouTube + TikTok)
==========================================================
  · Sin suscripciones         · Sin anuncios
  · 100% personalizable       · 10 idiomas
  · Sin pip install           · Crea sus archivos sola
  · Miniaturas personalizadas · Seguir / dejar de seguir
  · Reproductor integrado     · (usa ffmpeg si está instalado)
==========================================================
  Notas:
   - La vista previa de miniaturas NO bloquea la interfaz.
   - El reproductor interno reproduce VIDEO (sin audio), ya que
     tkinter no tiene soporte de audio sin librerías externas.
   - Si no hay ffmpeg en el PATH, el reproductor lo avisa y
     ofrece abrir el video con el programa externo del sistema.
==========================================================
"""

import os, sys, json, sqlite3, hashlib, datetime
import webbrowser, subprocess, shutil, base64
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser

# ffmpeg opcional (no es un paquete de Python, es un ejecutable del sistema)
FFMPEG = shutil.which("ffmpeg")


# ============================================================
#  RUTAS
# ============================================================
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATA_DIR    = os.path.join(BASE_DIR, "TesdoData")
MEDIA_DIR   = os.path.join(DATA_DIR, "media")
THUMBS_DIR  = os.path.join(DATA_DIR, "thumbs")
DB_PATH     = os.path.join(DATA_DIR, "tesdo.db")
CONFIG_PATH = os.path.join(DATA_DIR, "config.json")
README_PATH = os.path.join(DATA_DIR, "LEEME.txt")


def ensure_dirs():
    for d in (DATA_DIR, MEDIA_DIR, THUMBS_DIR):
        os.makedirs(d, exist_ok=True)
    if not os.path.exists(README_PATH):
        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write("TESDO — Carpeta de datos\n"
                    "========================\n\n"
                    "· tesdo.db    -> base de datos\n"
                    "· config.json -> preferencias\n"
                    "· media/      -> videos copiados\n"
                    "· thumbs/     -> miniaturas copiadas\n\n"
                    "Borra esta carpeta cuando quieras: se regenera sola.\n")


# ============================================================
#  IDIOMAS (10)
# ============================================================
LANGUAGES = {
"es": {
 "feed":"Inicio","following":"Siguiendo","library":"Biblioteca","upload":"Subir",
 "settings":"Ajustes","search":"Buscar...","trending":"Tendencias",
 "video_title":"Título","video_desc":"Descripción","video_source":"Archivo o URL del video",
 "video_thumb":"Miniatura (PNG/GIF)","pick_file":"Elegir archivo","pick_image":"Elegir imagen",
 "copy_library":"Copiar a mi biblioteca","publish":"Publicar","cancel":"Cancelar","save":"Guardar",
 "language":"Idioma","theme":"Tema","dark":"Oscuro","light":"Claro","accent":"Color de acento",
 "username":"Nombre de usuario","likes":"Me gusta","views":"vistas","comments":"Comentarios",
 "open":"Abrir","delete":"Eliminar","no_videos":"Aún no hay videos. ¡Sé el primero!",
 "no_following":"Aún no sigues a nadie. Busca creadores y dale a Seguir.",
 "comment_ph":"Escribe un comentario...","send":"Enviar","published_ok":"¡Publicado con éxito!",
 "deleted_ok":"Video eliminado","confirm_delete":"¿Eliminar este video?",
 "saved_ok":"Ajustes guardados","error":"Error","fill_all":"Completa título y fuente",
 "file_missing":"El archivo no existe","tagline":"Sin suscripciones · Sin anuncios",
 "copied":"Enlace copiado","new_video":"Nuevo video","appearance":"Apariencia",
 "follow":"+ Seguir","unfollow":"✓ Siguiendo","cant_follow_self":"No puedes seguirte a ti mismo",
 "image_unsupported":"Formato de imagen no soportado. Usa PNG, GIF o PPM.",
 "thumb_ok":"Miniatura cargada","followers":"seguidores","self_suffix":"(tú)"
},
"en": {
 "feed":"Home","following":"Following","library":"Library","upload":"Upload",
 "settings":"Settings","search":"Search...","trending":"Trending",
 "video_title":"Title","video_desc":"Description","video_source":"Video file or URL",
 "video_thumb":"Thumbnail (PNG/GIF)","pick_file":"Pick file","pick_image":"Pick image",
 "copy_library":"Copy to my library","publish":"Publish","cancel":"Cancel","save":"Save",
 "language":"Language","theme":"Theme","dark":"Dark","light":"Light","accent":"Accent color",
 "username":"Username","likes":"Likes","views":"views","comments":"Comments",
 "open":"Open","delete":"Delete","no_videos":"No videos yet. Be the first!",
 "no_following":"You don't follow anyone yet. Find creators and hit Follow.",
 "comment_ph":"Write a comment...","send":"Send","published_ok":"Published successfully!",
 "deleted_ok":"Video deleted","confirm_delete":"Delete this video?",
 "saved_ok":"Settings saved","error":"Error","fill_all":"Fill title and source",
 "file_missing":"File not found","tagline":"No subscriptions · No ads",
 "copied":"Link copied","new_video":"New video","appearance":"Appearance",
 "follow":"+ Follow","unfollow":"✓ Following","cant_follow_self":"You can't follow yourself",
 "image_unsupported":"Unsupported image format. Use PNG, GIF or PPM.",
 "thumb_ok":"Thumbnail loaded","followers":"followers","self_suffix":"(you)"
},
"fr": {
 "feed":"Accueil","following":"Abonnements","library":"Bibliothèque","upload":"Publier",
 "settings":"Réglages","search":"Rechercher...","trending":"Tendances",
 "video_title":"Titre","video_desc":"Description","video_source":"Fichier ou URL vidéo",
 "video_thumb":"Miniature (PNG/GIF)","pick_file":"Choisir un fichier","pick_image":"Choisir une image",
 "copy_library":"Copier dans ma bibliothèque","publish":"Publier","cancel":"Annuler","save":"Enregistrer",
 "language":"Langue","theme":"Thème","dark":"Sombre","light":"Clair","accent":"Couleur d'accent",
 "username":"Nom d'utilisateur","likes":"J'aime","views":"vues","comments":"Commentaires",
 "open":"Ouvrir","delete":"Supprimer","no_videos":"Aucune vidéo. Soyez le premier !",
 "no_following":"Vous ne suivez personne. Trouvez des créateurs et Suivez.",
 "comment_ph":"Écrire un commentaire...","send":"Envoyer","published_ok":"Publié !",
 "deleted_ok":"Vidéo supprimée","confirm_delete":"Supprimer cette vidéo ?",
 "saved_ok":"Réglages enregistrés","error":"Erreur","fill_all":"Remplissez titre et source",
 "file_missing":"Fichier introuvable","tagline":"Sans abonnements · Sans pub",
 "copied":"Lien copié","new_video":"Nouvelle vidéo","appearance":"Apparence",
 "follow":"+ Suivre","unfollow":"✓ Abonné","cant_follow_self":"Vous ne pouvez pas vous suivre",
 "image_unsupported":"Format non supporté. Utilisez PNG, GIF ou PPM.",
 "thumb_ok":"Miniature chargée","followers":"abonnés","self_suffix":"(vous)"
},
"de": {
 "feed":"Start","following":"Abonniert","library":"Bibliothek","upload":"Hochladen",
 "settings":"Einstellungen","search":"Suchen...","trending":"Trends",
 "video_title":"Titel","video_desc":"Beschreibung","video_source":"Videodatei oder URL",
 "video_thumb":"Vorschaubild (PNG/GIF)","pick_file":"Datei wählen","pick_image":"Bild wählen",
 "copy_library":"In Bibliothek kopieren","publish":"Veröffentlichen","cancel":"Abbrechen","save":"Speichern",
 "language":"Sprache","theme":"Design","dark":"Dunkel","light":"Hell","accent":"Akzentfarbe",
 "username":"Benutzername","likes":"Likes","views":"Aufrufe","comments":"Kommentare",
 "open":"Öffnen","delete":"Löschen","no_videos":"Noch keine Videos. Sei der Erste!",
 "no_following":"Du folgst noch niemandem.",
 "comment_ph":"Kommentar schreiben...","send":"Senden","published_ok":"Veröffentlicht!",
 "deleted_ok":"Video gelöscht","confirm_delete":"Dieses Video löschen?",
 "saved_ok":"Einstellungen gespeichert","error":"Fehler","fill_all":"Titel und Quelle ausfüllen",
 "file_missing":"Datei nicht gefunden","tagline":"Keine Abos · Keine Werbung",
 "copied":"Link kopiert","new_video":"Neues Video","appearance":"Aussehen",
 "follow":"+ Folgen","unfollow":"✓ Abonniert","cant_follow_self":"Du kannst dir nicht selbst folgen",
 "image_unsupported":"Format nicht unterstützt. PNG, GIF oder PPM verwenden.",
 "thumb_ok":"Vorschaubild geladen","followers":"Follower","self_suffix":"(du)"
},
"it": {
 "feed":"Home","following":"Seguiti","library":"Libreria","upload":"Carica",
 "settings":"Impostazioni","search":"Cerca...","trending":"Di tendenza",
 "video_title":"Titolo","video_desc":"Descrizione","video_source":"File o URL video",
 "video_thumb":"Miniatura (PNG/GIF)","pick_file":"Scegli file","pick_image":"Scegli immagine",
 "copy_library":"Copia nella libreria","publish":"Pubblica","cancel":"Annulla","save":"Salva",
 "language":"Lingua","theme":"Tema","dark":"Scuro","light":"Chiaro","accent":"Colore accento",
 "username":"Nome utente","likes":"Mi piace","views":"visualizzazioni","comments":"Commenti",
 "open":"Apri","delete":"Elimina","no_videos":"Nessun video. Sii il primo!",
 "no_following":"Non segui nessuno. Trova creator e premi Segui.",
 "comment_ph":"Scrivi un commento...","send":"Invia","published_ok":"Pubblicato!",
 "deleted_ok":"Video eliminato","confirm_delete":"Eliminare questo video?",
 "saved_ok":"Impostazioni salvate","error":"Errore","fill_all":"Compila titolo e fonte",
 "file_missing":"File non trovato","tagline":"Senza abbonamenti · Senza pubblicità",
 "copied":"Link copiato","new_video":"Nuovo video","appearance":"Aspetto",
 "follow":"+ Segui","unfollow":"✓ Seguito","cant_follow_self":"Non puoi seguire te stesso",
 "image_unsupported":"Formato non supportato. Usa PNG, GIF o PPM.",
 "thumb_ok":"Miniatura caricata","followers":"follower","self_suffix":"(tu)"
},
"pt": {
 "feed":"Início","following":"Seguindo","library":"Biblioteca","upload":"Enviar",
 "settings":"Ajustes","search":"Pesquisar...","trending":"Em alta",
 "video_title":"Título","video_desc":"Descrição","video_source":"Arquivo ou URL do vídeo",
 "video_thumb":"Miniatura (PNG/GIF)","pick_file":"Escolher arquivo","pick_image":"Escolher imagem",
 "copy_library":"Copiar para biblioteca","publish":"Publicar","cancel":"Cancelar","save":"Salvar",
 "language":"Idioma","theme":"Tema","dark":"Escuro","light":"Claro","accent":"Cor de destaque",
 "username":"Nome de usuário","likes":"Curtidas","views":"visualizações","comments":"Comentários",
 "open":"Abrir","delete":"Excluir","no_videos":"Nenhum vídeo ainda. Seja o primeiro!",
 "no_following":"Você não segue ninguém ainda.",
 "comment_ph":"Escreva um comentário...","send":"Enviar","published_ok":"Publicado!",
 "deleted_ok":"Vídeo excluído","confirm_delete":"Excluir este vídeo?",
 "saved_ok":"Ajustes salvos","error":"Erro","fill_all":"Preencha título e fonte",
 "file_missing":"Arquivo não encontrado","tagline":"Sem assinaturas · Sem anúncios",
 "copied":"Link copiado","new_video":"Novo vídeo","appearance":"Aparência",
 "follow":"+ Seguir","unfollow":"✓ Seguindo","cant_follow_self":"Você não pode seguir a si mesmo",
 "image_unsupported":"Formato não suportado. Use PNG, GIF ou PPM.",
 "thumb_ok":"Miniatura carregada","followers":"seguidores","self_suffix":"(você)"
},
"ru": {
 "feed":"Главная","following":"Подписки","library":"Библиотека","upload":"Загрузить",
 "settings":"Настройки","search":"Поиск...","trending":"В тренде",
 "video_title":"Название","video_desc":"Описание","video_source":"Файл или URL видео",
 "video_thumb":"Миниатюра (PNG/GIF)","pick_file":"Выбрать файл","pick_image":"Выбрать изображение",
 "copy_library":"Копировать в библиотеку","publish":"Опубликовать","cancel":"Отмена","save":"Сохранить",
 "language":"Язык","theme":"Тема","dark":"Тёмная","light":"Светлая","accent":"Цвет акцента",
 "username":"Имя пользователя","likes":"Лайки","views":"просмотров","comments":"Комментарии",
 "open":"Открыть","delete":"Удалить","no_videos":"Пока нет видео. Будь первым!",
 "no_following":"Вы ни на кого не подписаны.",
 "comment_ph":"Написать комментарий...","send":"Отправить","published_ok":"Опубликовано!",
 "deleted_ok":"Видео удалено","confirm_delete":"Удалить это видео?",
 "saved_ok":"Настройки сохранены","error":"Ошибка","fill_all":"Заполните название и источник",
 "file_missing":"Файл не найден","tagline":"Без подписок · Без рекламы",
 "copied":"Ссылка скопирована","new_video":"Новое видео","appearance":"Внешний вид",
 "follow":"+ Подписаться","unfollow":"✓ Подписан","cant_follow_self":"Нельзя подписаться на себя",
 "image_unsupported":"Формат не поддерживается. Используйте PNG, GIF или PPM.",
 "thumb_ok":"Миниатюра загружена","followers":"подписчиков","self_suffix":"(вы)"
},
"ja": {
 "feed":"ホーム","following":"フォロー中","library":"ライブラリ","upload":"投稿",
 "settings":"設定","search":"検索...","trending":"トレンド",
 "video_title":"タイトル","video_desc":"説明","video_source":"動画ファイルまたはURL",
 "video_thumb":"サムネイル（PNG/GIF）","pick_file":"ファイルを選択","pick_image":"画像を選択",
 "copy_library":"ライブラリにコピー","publish":"公開","cancel":"キャンセル","save":"保存",
 "language":"言語","theme":"テーマ","dark":"ダーク","light":"ライト","accent":"アクセントカラー",
 "username":"ユーザー名","likes":"いいね","views":"回再生","comments":"コメント",
 "open":"開く","delete":"削除","no_videos":"動画がまだありません。最初の一人になろう！",
 "no_following":"まだ誰もフォローしていません。",
 "comment_ph":"コメントを書く...","send":"送信","published_ok":"公開しました！",
 "deleted_ok":"動画を削除しました","confirm_delete":"この動画を削除しますか？",
 "saved_ok":"設定を保存しました","error":"エラー","fill_all":"タイトルとソースを入力してください",
 "file_missing":"ファイルが見つかりません","tagline":"サブスクなし · 広告なし",
 "copied":"リンクをコピーしました","new_video":"新しい動画","appearance":"外観",
 "follow":"+ フォロー","unfollow":"✓ フォロー中","cant_follow_self":"自分をフォローできません",
 "image_unsupported":"未対応の形式です。PNG、GIF、PPMをご利用ください。",
 "thumb_ok":"サムネイルを読み込みました","followers":"フォロワー","self_suffix":"（あなた）"
},
"zh": {
 "feed":"首页","following":"关注","library":"媒体库","upload":"上传",
 "settings":"设置","search":"搜索...","trending":"热门",
 "video_title":"标题","video_desc":"描述","video_source":"视频文件或网址",
 "video_thumb":"缩略图（PNG/GIF）","pick_file":"选择文件","pick_image":"选择图片",
 "copy_library":"复制到媒体库","publish":"发布","cancel":"取消","save":"保存",
 "language":"语言","theme":"主题","dark":"深色","light":"浅色","accent":"强调色",
 "username":"用户名","likes":"点赞","views":"次观看","comments":"评论",
 "open":"打开","delete":"删除","no_videos":"还没有视频，来做第一个吧！",
 "no_following":"你还没有关注任何人。",
 "comment_ph":"写评论...","send":"发送","published_ok":"发布成功！",
 "deleted_ok":"视频已删除","confirm_delete":"删除这个视频？",
 "saved_ok":"设置已保存","error":"错误","fill_all":"请填写标题和来源",
 "file_missing":"找不到文件","tagline":"无订阅 · 无广告",
 "copied":"链接已复制","new_video":"新视频","appearance":"外观",
 "follow":"+ 关注","unfollow":"✓ 已关注","cant_follow_self":"不能关注自己",
 "image_unsupported":"不支持的图片格式。请使用 PNG、GIF 或 PPM。",
 "thumb_ok":"缩略图已加载","followers":"粉丝","self_suffix":"（你）"
},
"ar": {
 "feed":"الرئيسية","following":"المتابَعون","library":"المكتبة","upload":"رفع",
 "settings":"الإعدادات","search":"بحث...","trending":"الأكثر رواجًا",
 "video_title":"العنوان","video_desc":"الوصف","video_source":"ملف الفيديو أو الرابط",
 "video_thumb":"صورة مصغرة (PNG/GIF)","pick_file":"اختر ملفًا","pick_image":"اختر صورة",
 "copy_library":"انسخ إلى مكتبتي","publish":"نشر","cancel":"إلغاء","save":"حفظ",
 "language":"اللغة","theme":"المظهر","dark":"داكن","light":"فاتح","accent":"لون التمييز",
 "username":"اسم المستخدم","likes":"إعجابات","views":"مشاهدة","comments":"التعليقات",
 "open":"فتح","delete":"حذف","no_videos":"لا توجد فيديوهات بعد. كن الأول!",
 "no_following":"لا تتابع أحدًا بعد.",
 "comment_ph":"اكتب تعليقًا...","send":"إرسال","published_ok":"تم النشر بنجاح!",
 "deleted_ok":"تم حذف الفيديو","confirm_delete":"حذف هذا الفيديو؟",
 "saved_ok":"تم حفظ الإعدادات","error":"خطأ","fill_all":"املأ العنوان والمصدر",
 "file_missing":"الملف غير موجود","tagline":"بدون اشتراكات · بدون إعلانات",
 "copied":"تم نسخ الرابط","new_video":"فيديو جديد","appearance":"المظهر",
 "follow":"+ متابعة","unfollow":"✓ متابَع","cant_follow_self":"لا يمكنك متابعة نفسك",
 "image_unsupported":"صيغة غير مدعومة. استخدم PNG أو GIF أو PPM.",
 "thumb_ok":"تم تحميل الصورة المصغرة","followers":"متابع","self_suffix":"(أنت)"
},
}

LANGUAGE_NAMES = {
    "es":"Español","en":"English","fr":"Français","de":"Deutsch","it":"Italiano",
    "pt":"Português","ru":"Русский","ja":"日本語","zh":"中文","ar":"العربية",
}


# ============================================================
#  CONFIG
# ============================================================
DEFAULT_CONFIG = {
    "language":"es","theme":"dark","accent":"#FF2D55",
    "username":"Invitado","liked":[],
}

THEMES = {
    "dark": {"bg":"#0E0E12","panel":"#16161E","card":"#1D1D27","border":"#2A2A38",
             "text":"#F5F5F7","sub":"#9A9AAE","hover":"#23232F","input":"#12121A"},
    "light":{"bg":"#F2F2F6","panel":"#FFFFFF","card":"#FFFFFF","border":"#E0E0E8",
             "text":"#121218","sub":"#6B6B7B","hover":"#EFEFF4","input":"#F7F7FA"},
}


def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH,"r",encoding="utf-8") as f:
                cfg = json.load(f)
            for k,v in DEFAULT_CONFIG.items():
                cfg.setdefault(k,v)
            return cfg
        except Exception:
            pass
    save_config(DEFAULT_CONFIG)
    return dict(DEFAULT_CONFIG)


def save_config(cfg):
    with open(CONFIG_PATH,"w",encoding="utf-8") as f:
        json.dump(cfg,f,ensure_ascii=False,indent=2)


# ============================================================
#  BASE DE DATOS
# ============================================================
def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    con = db()
    con.executescript("""
        CREATE TABLE IF NOT EXISTS videos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            description TEXT DEFAULT '',
            source      TEXT DEFAULT '',
            thumbnail   TEXT DEFAULT '',
            author      TEXT DEFAULT 'Invitado',
            likes       INTEGER DEFAULT 0,
            views       INTEGER DEFAULT 0,
            created     TEXT
        );
        CREATE TABLE IF NOT EXISTS comments (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id INTEGER,
            author   TEXT,
            text     TEXT,
            created  TEXT
        );
        CREATE TABLE IF NOT EXISTS follows (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            follower  TEXT,
            following TEXT,
            created   TEXT,
            UNIQUE(follower, following)
        );
    """)
    # Migración para bases de datos antiguas
    try:
        con.execute("ALTER TABLE videos ADD COLUMN thumbnail TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    con.commit()

    n = con.execute("SELECT COUNT(*) FROM videos").fetchone()[0]
    if n == 0:
        demo = [
            ("Bienvenido a Tesdo",
             "La red social de video sin suscripciones y sin anuncios.",
             "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
             "", "Tesdo Oficial"),
            ("Elephants Dream — corto libre",
             "Un clásico del cine abierto para probar el reproductor.",
             "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
             "", "Tesdo Cine"),
            ("For Bigger Blazes",
             "Demo de video corto, estilo feed vertical.",
             "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
             "", "Tesdo Studio"),
            ("Mi primer video",
             "Edita o elimina este ejemplo y publica el tuyo.",
             "", "", "Invitado"),
        ]
        now = datetime.datetime.now().isoformat(timespec="seconds")
        for title,desc,src,thumb,author in demo:
            con.execute("INSERT INTO videos (title,description,source,thumbnail,author,likes,views,created)"
                        " VALUES (?,?,?,?,?,?,?,?)",
                        (title,desc,src,thumb,author,0,0,now))
        con.commit()
    con.close()


# ============================================================
#  UTILIDADES
# ============================================================
def poster_color(seed: str) -> str:
    h = int(hashlib.md5(seed.encode("utf-8")).hexdigest(),16)
    r = 35 + (h % 130); g = 35 + ((h>>9) % 130); b = 35 + ((h>>18) % 130)
    return f"#{r:02x}{g:02x}{b:02x}"


def open_source(src: str):
    if not src: raise FileNotFoundError
    if src.startswith(("http://","https://")):
        webbrowser.open(src); return
    if not os.path.exists(src): raise FileNotFoundError
    if sys.platform.startswith("win"): os.startfile(src)          # noqa
    elif sys.platform == "darwin": subprocess.Popen(["open", src])
    else: subprocess.Popen(["xdg-open", src])


def load_thumbnail(path, max_width=780, max_height=None):
    """Carga una imagen con tk.PhotoImage. Devuelve None si falla o no existe.
    Reduce manteniendo aspecto según max_width y (opcional) max_height."""
    if not path or not os.path.exists(path):
        return None
    try:
        img = tk.PhotoImage(file=path)
    except Exception:
        return None
    w, h = img.width(), img.height()
    fx = max(1, int(w / max_width)) if w > max_width else 1
    fy = max(1, int(h / max_height)) if (max_height and h > max_height) else 1
    f = max(fx, fy)
    if f > 1:
        img = img.subsample(f, f)
    return img


# ============================================================
#  REPRODUCTOR INTEGRADO (ffmpeg opcional)
# ============================================================
class VideoPlayer(tk.Toplevel):
    W, H = 640, 360
    FPS = 15

    def __init__(self, master, row, app):
        super().__init__(master)
        self.row = row
        self.app = app
        self.proc = None
        self.playing = False
        self._job = None
        self._closing = False

        self.title(f'Tesdo · {row["title"]}')
        self.geometry("720x660")
        self.configure(bg=app.theme["bg"])
        self.transient(master)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<Escape>", lambda e: self._on_close())

        th = app.theme

        wrap = tk.Frame(self, bg="#000", width=self.W, height=self.H)
        wrap.pack(pady=(14, 8))
        wrap.pack_propagate(False)

        self.video_lbl = tk.Label(wrap, bg="#000", fg="#fff")
        self.video_lbl.pack(fill="both", expand=True)

        self.status = tk.Label(self, text="", bg=th["bg"], fg=th["sub"],
                               font=("Segoe UI", 9))
        self.status.pack()

        ctrl = tk.Frame(self, bg=th["bg"])
        ctrl.pack(fill="x", padx=20, pady=10)

        self.btn_play = tk.Button(ctrl, text="⏸  Pausa", command=self._toggle,
                                  bg=app.accent, fg="#fff", relief="flat", bd=0,
                                  font=("Segoe UI", 10, "bold"), padx=16,
                                  cursor="hand2",
                                  activebackground=app.accent, activeforeground="#fff")
        self.btn_play.pack(side="left", ipady=6)

        tk.Button(ctrl, text="⏹  Detener", command=self._stop,
                  bg=th["hover"], fg=th["text"], relief="flat", bd=0,
                  font=("Segoe UI", 10, "bold"), padx=16, cursor="hand2"
                  ).pack(side="left", padx=6, ipady=6)

        tk.Button(ctrl, text="↗  Abrir externo", command=self._open_external,
                  bg=th["hover"], fg=th["text"], relief="flat", bd=0,
                  font=("Segoe UI", 10), padx=14, cursor="hand2"
                  ).pack(side="right", ipady=6)

        info = tk.Frame(self, bg=th["bg"])
        info.pack(fill="x", padx=20, pady=(0, 16))
        tk.Label(info, text=row["title"], bg=th["bg"], fg=th["text"],
                 font=("Segoe UI", 13, "bold"), wraplength=660,
                 justify="left", anchor="w").pack(fill="x")
        tk.Label(info, text=row["author"], bg=th["bg"], fg=th["sub"],
                 font=("Segoe UI", 9)).pack(anchor="w")
        if row["description"]:
            tk.Label(info, text=row["description"], bg=th["bg"], fg=th["text"],
                     font=("Segoe UI", 10), wraplength=660,
                     justify="left", anchor="w").pack(fill="x", pady=(6, 0))

        self._show_placeholder()
        self.after(120, self._start)

    def _show_placeholder(self):
        img = load_thumbnail(self.row["thumbnail"], self.W, self.H)
        if img is not None:
            self.video_lbl.configure(image=img, text="")
            self.video_lbl.image = img
        else:
            col = poster_color(self.row["title"])
            self.video_lbl.configure(bg=col, text="▶  " + self.row["title"],
                                     fg="#fff", font=("Segoe UI", 18, "bold"),
                                     wraplength=self.W - 40, justify="center")

    def _msg(self, text):
        self.video_lbl.configure(image="", text=text, bg="#000", fg="#fff",
                                 font=("Segoe UI", 11), wraplength=self.W - 60,
                                 justify="center")
        self.video_lbl.image = None

    def _start(self):
        if self._closing:
            return
        if not FFMPEG:
            self._msg("⚠  No se encontró ffmpeg en el sistema.\n\n"
                      "Para reproducir dentro de la app instala ffmpeg\n"
                      "y asegúrate de que está en el PATH.\n\n"
                      "(Mientras tanto puedes usar 'Abrir externo'.)")
            self.status.configure(text="ffmpeg no disponible")
            return

        src = self.row["source"]
        if not src:
            self._msg("Este video no tiene fuente reproducible.")
            return

        is_url = src.startswith(("http://", "https://"))
        if is_url and any(d in src.lower() for d in
                          ("youtube.com", "youtu.be", "tiktok.com", "vimeo.com")):
            self._msg("Para YouTube/TikTok/Vimeo hace falta yt-dlp\n"
                      "(no incluido). Usa 'Abrir externo'.")
            return
        if not is_url and not os.path.exists(src):
            self._msg("El archivo local no existe.")
            return

        vf = (f"scale={self.W}:{self.H}:force_original_aspect_ratio=decrease,"
              f"pad={self.W}:{self.H}:(ow-iw)/2:(oh-ih)/2:black")

        cmd = [FFMPEG, "-loglevel", "error", "-i", src,
               "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-vf", vf, "-r", str(self.FPS), "-an", "-"]

        kw = {}
        if sys.platform == "win32":
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            kw["startupinfo"] = si
            kw["creationflags"] = subprocess.CREATE_NO_WINDOW
        try:
            self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                         stderr=subprocess.DEVNULL, **kw)
        except FileNotFoundError:
            self._msg("No se encontró ffmpeg.")
            return

        self.playing = True
        self.status.configure(text=f"Reproduciendo · {self.FPS} fps · sin audio")
        self._next_frame()

    def _next_frame(self):
        if not self.playing or self._closing or self.proc is None:
            return
        size = self.W * self.H * 3
        try:
            raw = self.proc.stdout.read(size)
        except Exception:
            raw = None
        if not raw or len(raw) < size:
            self.playing = False
            self.status.configure(text="Fin del video")
            return

        header = f"P6\n{self.W} {self.H}\n255\n".encode("ascii")
        b64 = base64.b64encode(header + raw)
        try:
            img = tk.PhotoImage(data=b64)
            self.video_lbl.configure(image=img, text="", bg="#000")
            self.video_lbl.image = img
        except Exception as ex:
            print("Frame error:", ex)
        self._job = self.after(int(1000 / self.FPS), self._next_frame)

    def _toggle(self):
        if self.proc is None:
            return
        if self.playing:
            self.playing = False
            if self._job:
                try: self.after_cancel(self._job)
                except Exception: pass
            self.btn_play.configure(text="▶  Reanudar")
            self.status.configure(text="Pausado")
        else:
            self.playing = True
            self.btn_play.configure(text="⏸  Pausa")
            self.status.configure(text=f"Reproduciendo · {self.FPS} fps · sin audio")
            self._next_frame()

    def _stop(self):
        self.playing = False
        if self._job:
            try: self.after_cancel(self._job)
            except Exception: pass
            self._job = None
        if self.proc:
            try: self.proc.terminate()
            except Exception: pass
            try: self.proc.wait(timeout=2)
            except Exception: pass
            self.proc = None
        self.status.configure(text="Detenido")

    def _open_external(self):
        try:
            open_source(self.row["source"])
        except FileNotFoundError:
            messagebox.showerror(self.app.t("error"), self.app.t("file_missing"))

    def _on_close(self):
        self._closing = True
        self.playing = False
        if self._job:
            try: self.after_cancel(self._job)
            except Exception: pass
        if self.proc:
            try: self.proc.terminate()
            except Exception: pass
            try: self.proc.wait(timeout=2)
            except Exception: pass
        self.destroy()


# ============================================================
#  APLICACIÓN
# ============================================================
class TesdoApp:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.cfg = load_config()
        self.theme = THEMES[self.cfg["theme"]]
        self.accent = self.cfg["accent"]
        self.view = "feed"
        self.search_text = ""
        self._img_refs = []

        self.root.title("Tesdo")
        self.root.geometry("1180x760")
        self.root.minsize(940, 620)
        self.root.configure(bg=self.theme["bg"])
        self._setup_ttk()
        self.build_ui()

    def t(self, key):
        return LANGUAGES.get(self.cfg["language"], LANGUAGES["es"]).get(key, key)

    def _setup_ttk(self):
        st = ttk.Style()
        try: st.theme_use("clam")
        except tk.TclError: pass

    # ---------- UI ----------
    def build_ui(self):
        self.root.unbind_all("<MouseWheel>")
        for w in self.root.winfo_children(): w.destroy()

        self.theme = THEMES[self.cfg["theme"]]
        self.accent = self.cfg["accent"]
        th = self.theme
        self.root.configure(bg=th["bg"])

        side = tk.Frame(self.root, bg=th["panel"], width=230)
        side.pack(side="left", fill="y"); side.pack_propagate(False)

        logo = tk.Frame(side, bg=th["panel"])
        logo.pack(fill="x", pady=(22,6), padx=20)
        tk.Label(logo, text="TESDO", bg=th["panel"], fg=self.accent,
                 font=("Segoe UI",24,"bold")).pack(anchor="w")
        tk.Label(logo, text=self.t("tagline"), bg=th["panel"], fg=th["sub"],
                 font=("Segoe UI",8)).pack(anchor="w")

        tk.Frame(side, bg=th["border"], height=1).pack(fill="x", pady=14, padx=16)

        for key in ("feed","following","library","upload","settings"):
            self._nav_button(side, key, self.t(key))

        bottom = tk.Frame(side, bg=th["panel"])
        bottom.pack(side="bottom", fill="x", pady=18, padx=18)
        tk.Frame(bottom, bg=th["border"], height=1).pack(fill="x", pady=(0,12))
        tk.Label(bottom, text="● " + self.cfg["username"], bg=th["panel"],
                 fg=th["sub"], font=("Segoe UI",9)).pack(anchor="w")

        self.content = tk.Frame(self.root, bg=th["bg"])
        self.content.pack(side="left", fill="both", expand=True)
        self.render_view()

    def _nav_button(self, parent, key, text):
        th = self.theme
        active = (self.view == key)
        bg = th["hover"] if active else th["panel"]
        fg = self.accent if active else th["text"]
        b = tk.Label(parent, text="   "+text, bg=bg, fg=fg, anchor="w",
                     font=("Segoe UI",11,"bold" if active else "normal"),
                     padx=10, pady=10, cursor="hand2")
        b.pack(fill="x", padx=12, pady=2)
        b.bind("<Enter>", lambda e: b.configure(bg=th["hover"]) if not active else None)
        b.bind("<Leave>", lambda e: b.configure(bg=th["panel"]) if not active else None)
        b.bind("<Button-1>", lambda e: self.go(key))

    def go(self, key):
        self.view = key
        self.build_ui()

    def render_view(self):
        for w in self.content.winfo_children(): w.destroy()
        self._img_refs.clear()
        if self.view == "feed":        self.view_feed()
        elif self.view == "following": self.view_following()
        elif self.view == "library":   self.view_library()
        elif self.view == "upload":    self.view_upload()
        elif self.view == "settings":  self.view_settings()

    def header(self, title):
        th = self.theme
        head = tk.Frame(self.content, bg=th["bg"])
        head.pack(fill="x", padx=28, pady=(24,10))
        tk.Label(head, text=title, bg=th["bg"], fg=th["text"],
                 font=("Segoe UI",20,"bold")).pack(side="left")
        box = tk.Frame(head, bg=th["input"], highlightthickness=1,
                       highlightbackground=th["border"])
        box.pack(side="right")
        entry = tk.Entry(box, bg=th["input"], fg=th["text"],
                         insertbackground=th["text"], relief="flat",
                         width=28, font=("Segoe UI",10))
        entry.pack(padx=10, pady=6)
        entry.insert(0, self.search_text)
        entry.bind("<KeyRelease>", lambda e: self._on_search(entry.get()))
        if not self.search_text:
            ph = tk.Label(box, text=self.t("search"), bg=th["input"],
                          fg=th["sub"], font=("Segoe UI",10))
            ph.place(x=10, y=6)
            entry.bind("<FocusIn>", lambda e: ph.destroy())
        return head

    def _on_search(self, text):
        self.search_text = text
        self.render_view()

    def scroll_area(self):
        th = self.theme
        outer = tk.Frame(self.content, bg=th["bg"])
        outer.pack(fill="both", expand=True, padx=20, pady=(0,16))
        canvas = tk.Canvas(outer, bg=th["bg"], highlightthickness=0, bd=0)
        vsb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(canvas, bg=th["bg"])
        win = canvas.create_window((0,0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfigure(win, width=e.width))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
        return inner

    # ========================================================
    #  VISTAS
    # ========================================================
    def view_feed(self):
        self.header(self.t("feed"))
        area = self.scroll_area()
        rows = self.fetch_videos(order="recent")
        if not rows: self.empty_state(area, self.t("no_videos")); return
        for r in rows:
            self.video_card(area, r, big=True)

    def view_following(self):
        self.header(self.t("following"))
        area = self.scroll_area()
        rows = self.fetch_followed_videos()
        if not rows: self.empty_state(area, self.t("no_following")); return
        for r in rows:
            self.video_card(area, r, big=True)

    def view_library(self):
        self.header(self.t("library"))
        area = self.scroll_area()
        rows = self.fetch_videos(order="trending")
        if not rows: self.empty_state(area, self.t("no_videos")); return
        grid = tk.Frame(area, bg=self.theme["bg"])
        grid.pack(fill="both", expand=True)
        for i in range(3):
            grid.columnconfigure(i, weight=1, uniform="col")
        for idx, r in enumerate(rows):
            self.grid_card(grid, r, idx//3, idx%3)

    # ---------- tarjetas ----------
    def video_card(self, parent, row, big=True):
        th = self.theme
        card = tk.Frame(parent, bg=th["card"], highlightthickness=1,
                        highlightbackground=th["border"])
        card.pack(fill="x", pady=8, padx=6)

        col = poster_color(row["title"])
        poster = tk.Frame(card, bg=col)
        poster.pack(fill="x")

        img = load_thumbnail(row["thumbnail"], 780, 240)
        if img is not None:
            self._img_refs.append(img)
            tk.Label(poster, image=img, bg=col, bd=0).pack(fill="x")
        else:
            poster.configure(height=230)
            poster.pack_propagate(False)
            tk.Label(poster, text="▶", bg=col, fg="#ffffff",
                     font=("Segoe UI",34)).pack(expand=True)
            tk.Label(poster, text=row["title"], bg=col, fg="#ffffff",
                     font=("Segoe UI",13,"bold"), wraplength=760,
                     justify="center").pack(pady=(0,26))

        info = tk.Frame(card, bg=th["card"])
        info.pack(fill="x", padx=16, pady=12)

        author_row = tk.Frame(info, bg=th["card"])
        author_row.pack(fill="x")

        is_self = (row["author"] == self.cfg["username"])
        followers = self.count_followers(row["author"])
        author_txt = row["author"]
        if is_self: author_txt += "  " + self.t("self_suffix")
        tk.Label(author_row,
                 text=f'{author_txt}  ·  {row["views"]} {self.t("views")}  ·  {followers} {self.t("followers")}',
                 bg=th["card"], fg=th["sub"],
                 font=("Segoe UI",9)).pack(side="left")

        if not is_self:
            self._follow_button(author_row, row["author"])

        if row["description"]:
            tk.Label(info, text=row["description"], bg=th["card"], fg=th["text"],
                     font=("Segoe UI",10), wraplength=780,
                     justify="left").pack(anchor="w", pady=(6,0))

        bar = tk.Frame(card, bg=th["card"])
        bar.pack(fill="x", padx=16, pady=(0,14))

        liked = row["id"] in self.cfg.get("liked", [])
        like_txt = ("♥ " if liked else "♡ ") + str(row["likes"])
        self.pill(bar, like_txt, lambda: self.toggle_like(row["id"]),
                  color=self.accent if liked else None)
        self.pill(bar, "💬 " + str(self.count_comments(row["id"])),
                  lambda: self.open_comments(row["id"]))
        self.pill(bar, "▶ " + self.t("open"), lambda: self.play(row["id"]))
        self.pill(bar, "🔗", lambda: self.share(row))
        if is_self:
            self.pill(bar, self.t("delete"), lambda: self.delete_video(row["id"]))

    def _follow_button(self, parent, username):
        th = self.theme
        following = self.is_following(username)
        txt = self.t("unfollow") if following else self.t("follow")
        bg  = th["hover"] if following else self.accent
        fg  = th["text"] if following else "#fff"
        b = tk.Label(parent, text=txt, bg=bg, fg=fg,
                     font=("Segoe UI",9,"bold"), padx=10, pady=4, cursor="hand2")
        b.pack(side="right")
        b.bind("<Button-1>", lambda e: self.toggle_follow(username))

    def grid_card(self, parent, row, r, c):
        th = self.theme
        card = tk.Frame(parent, bg=th["card"], highlightthickness=1,
                        highlightbackground=th["border"])
        card.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")

        col = poster_color(row["title"])
        poster = tk.Frame(card, bg=col, height=140)
        poster.pack(fill="x"); poster.pack_propagate(False)

        img = load_thumbnail(row["thumbnail"], 260, 140)
        if img is not None:
            self._img_refs.append(img)
            tk.Label(poster, image=img, bg=col, bd=0).pack(expand=True)
        else:
            tk.Label(poster, text="▶", bg=col, fg="#fff",
                     font=("Segoe UI",22)).pack(expand=True)

        body = tk.Frame(card, bg=th["card"])
        body.pack(fill="both", expand=True, padx=10, pady=8)
        tk.Label(body, text=row["title"], bg=th["card"], fg=th["text"],
                 font=("Segoe UI",10,"bold"), wraplength=220,
                 justify="left", anchor="w").pack(fill="x")
        tk.Label(body, text=row["author"], bg=th["card"], fg=th["sub"],
                 font=("Segoe UI",8)).pack(anchor="w", pady=(2,0))
        tk.Label(body, text=f'{row["views"]} {self.t("views")} · ♥ {row["likes"]}',
                 bg=th["card"], fg=th["sub"], font=("Segoe UI",8)).pack(anchor="w")

        tk.Button(body, text=self.t("open"), command=lambda: self.play(row["id"]),
                  bg=self.accent, fg="#fff", relief="flat", bd=0,
                  font=("Segoe UI",9,"bold"), cursor="hand2",
                  activebackground=self.accent, activeforeground="#fff"
                  ).pack(fill="x", pady=(8,0))

    def pill(self, parent, text, cmd, color=None):
        th = self.theme
        fg = color if color else th["text"]
        b = tk.Label(parent, text=text, bg=th["hover"], fg=fg,
                     font=("Segoe UI",9,"bold"), padx=12, pady=6, cursor="hand2")
        b.pack(side="left", padx=(0,8))
        b.bind("<Button-1>", lambda e: cmd())
        b.bind("<Enter>", lambda e: b.configure(bg=th["border"]))
        b.bind("<Leave>", lambda e: b.configure(bg=th["hover"]))

    def empty_state(self, parent, text):
        th = self.theme
        box = tk.Frame(parent, bg=th["bg"])
        box.pack(expand=True, pady=80)
        tk.Label(box, text="🎬", bg=th["bg"], fg=th["sub"],
                 font=("Segoe UI",40)).pack()
        tk.Label(box, text=text, bg=th["bg"], fg=th["sub"],
                 font=("Segoe UI",12), wraplength=420,
                 justify="center").pack(pady=10)

    # ========================================================
    #  SUBIR VIDEO (+ miniatura, sin bloqueos)
    # ========================================================
    def view_upload(self):
        th = self.theme
        self.header(self.t("upload"))
        wrap = tk.Frame(self.content, bg=th["bg"])
        wrap.pack(fill="both", expand=True, padx=40, pady=10)
        card = tk.Frame(wrap, bg=th["card"], highlightthickness=1,
                        highlightbackground=th["border"])
        card.pack(fill="x")
        inner = tk.Frame(card, bg=th["card"])
        inner.pack(fill="x", padx=28, pady=24)

        tk.Label(inner, text=self.t("new_video"), bg=th["card"], fg=th["text"],
                 font=("Segoe UI",15,"bold")).pack(anchor="w", pady=(0,18))

        # Título
        tk.Label(inner, text=self.t("video_title"), bg=th["card"], fg=th["sub"],
                 font=("Segoe UI",9,"bold")).pack(anchor="w")
        e_title = tk.Entry(inner, bg=th["input"], fg=th["text"], relief="flat",
                           insertbackground=th["text"], font=("Segoe UI",11))
        e_title.pack(fill="x", ipady=8, pady=(4,16))

        # Descripción
        tk.Label(inner, text=self.t("video_desc"), bg=th["card"], fg=th["sub"],
                 font=("Segoe UI",9,"bold")).pack(anchor="w")
        e_desc = tk.Text(inner, bg=th["input"], fg=th["text"], relief="flat",
                         insertbackground=th["text"], height=3,
                         font=("Segoe UI",10), wrap="word")
        e_desc.pack(fill="x", pady=(4,16))

        # Fuente de video
        tk.Label(inner, text=self.t("video_source"), bg=th["card"], fg=th["sub"],
                 font=("Segoe UI",9,"bold")).pack(anchor="w")
        src_row = tk.Frame(inner, bg=th["card"])
        src_row.pack(fill="x", pady=(4,6))
        e_src = tk.Entry(src_row, bg=th["input"], fg=th["text"], relief="flat",
                         insertbackground=th["text"], font=("Segoe UI",10))
        e_src.pack(side="left", fill="x", expand=True, ipady=8)
        tk.Button(src_row, text=self.t("pick_file"),
                  command=lambda: self.pick_video(e_src),
                  bg=th["hover"], fg=th["text"], relief="flat", bd=0,
                  font=("Segoe UI",9,"bold"), padx=14, cursor="hand2"
                  ).pack(side="left", padx=(8,0), ipady=7)

        # Miniatura
        tk.Label(inner, text=self.t("video_thumb"), bg=th["card"], fg=th["sub"],
                 font=("Segoe UI",9,"bold")).pack(anchor="w", pady=(14,0))
        thumb_row = tk.Frame(inner, bg=th["card"])
        thumb_row.pack(fill="x", pady=(4,6))

        e_thumb = tk.Entry(thumb_row, bg=th["input"], fg=th["text"], relief="flat",
                           insertbackground=th["text"], font=("Segoe UI",10))
        e_thumb.pack(side="left", fill="x", expand=True, ipady=8)

        # Contenedor de vista previa con altura fija
        prev_wrap = tk.Frame(inner, bg=th["card"], height=170)
        prev_wrap.pack(fill="x", pady=(10, 8))
        prev_wrap.pack_propagate(False)

        thumb_preview_lbl = tk.Label(prev_wrap, bg=th["card"], fg=th["sub"],
                                     font=("Segoe UI",9), anchor="w", justify="left")
        thumb_preview_lbl.pack(anchor="w")

        # Vista previa robusta y NO bloqueante
        def update_preview(*_):
            if not thumb_preview_lbl.winfo_exists():
                return
            path = e_thumb.get().strip()
            thumb_preview_lbl.configure(image="", text="")
            thumb_preview_lbl.image = None
            if not path:
                return
            if not os.path.exists(path):
                thumb_preview_lbl.configure(text="⚠ " + self.t("file_missing"))
                return
            try:
                mb = os.path.getsize(path) / (1024 * 1024)
            except OSError:
                mb = 0
            if mb > 8:
                thumb_preview_lbl.configure(
                    text=f"⚠ Imagen muy grande ({mb:.1f} MB). Se subirá igual, "
                         f"pero sin vista previa. Reduce a 1280×720.")
                return
            try:
                img = load_thumbnail(path, 260, 150)
            except Exception as ex:
                img = None
                print("Preview error:", ex)
            if img is None:
                thumb_preview_lbl.configure(text="⚠ " + self.t("image_unsupported"))
            else:
                thumb_preview_lbl.configure(image=img)
                thumb_preview_lbl.image = img

        def pick_image():
            try:
                path = filedialog.askopenfilename(
                    title=self.t("pick_image"),
                    filetypes=[
                        ("Imágenes soportadas (PNG/GIF/PPM)", "*.png *.gif *.ppm *.pgm"),
                        ("Otras imágenes (sin vista previa)", "*.jpg *.jpeg *.bmp *.webp"),
                        ("Todos", "*.*"),
                    ])
            except Exception as ex:
                messagebox.showerror(self.t("error"), str(ex))
                return
            if not path:
                return
            e_thumb.delete(0, "end")
            e_thumb.insert(0, path)
            # Cargar después de cerrar el diálogo para no bloquear
            self.root.after(80, update_preview)

        tk.Button(thumb_row, text=self.t("pick_image"), command=pick_image,
                  bg=th["hover"], fg=th["text"], relief="flat", bd=0,
                  font=("Segoe UI",9,"bold"), padx=14, cursor="hand2"
                  ).pack(side="left", padx=(8,0), ipady=7)

        e_thumb.bind("<Return>", update_preview)
        e_thumb.bind("<FocusOut>", update_preview)

        copy_var = tk.BooleanVar(value=False)
        tk.Checkbutton(inner, text=self.t("copy_library"), variable=copy_var,
                       bg=th["card"], fg=th["sub"], selectcolor=th["input"],
                       activebackground=th["card"], activeforeground=th["text"],
                       font=("Segoe UI",9), bd=0, highlightthickness=0
                       ).pack(anchor="w", pady=(4,14))

        actions = tk.Frame(inner, bg=th["card"])
        actions.pack(fill="x")
        tk.Button(actions, text=self.t("publish"),
                  command=lambda: self.publish(e_title, e_desc, e_src, e_thumb, copy_var),
                  bg=self.accent, fg="#fff", relief="flat", bd=0,
                  font=("Segoe UI",11,"bold"), padx=26, cursor="hand2",
                  activebackground=self.accent, activeforeground="#fff"
                  ).pack(side="left", ipady=9)
        tk.Button(actions, text=self.t("cancel"), command=lambda: self.go("feed"),
                  bg=th["hover"], fg=th["text"], relief="flat", bd=0,
                  font=("Segoe UI",10), padx=20, cursor="hand2"
                  ).pack(side="left", padx=10, ipady=9)

    def pick_video(self, entry):
        path = filedialog.askopenfilename(
            title=self.t("pick_file"),
            filetypes=[("Video","*.mp4 *.mkv *.avi *.mov *.webm *.m4v *.wmv"),
                       ("Todos","*.*")])
        if path:
            entry.delete(0,"end"); entry.insert(0, path)

    def publish(self, e_title, e_desc, e_src, e_thumb, copy_var):
        title = e_title.get().strip()
        desc  = e_desc.get("1.0","end").strip()
        src   = e_src.get().strip()
        thumb = e_thumb.get().strip()

        if not title or not src:
            messagebox.showerror(self.t("error"), self.t("fill_all")); return
        is_url = src.startswith(("http://","https://"))
        if not is_url and not os.path.exists(src):
            messagebox.showerror(self.t("error"), self.t("file_missing")); return

        if thumb:
            if not os.path.exists(thumb):
                messagebox.showerror(self.t("error"), self.t("file_missing")); return
            if load_thumbnail(thumb, 100, 100) is None:
                messagebox.showerror(self.t("error"), self.t("image_unsupported")); return

        if copy_var.get() and not is_url:
            try:
                name = f"{int(datetime.datetime.now().timestamp())}_{os.path.basename(src)}"
                dst = os.path.join(MEDIA_DIR, name)
                shutil.copy2(src, dst); src = dst
            except Exception as ex:
                messagebox.showwarning(self.t("error"), str(ex))

        if thumb:
            try:
                tname = f"{int(datetime.datetime.now().timestamp())}_{os.path.basename(thumb)}"
                tdst = os.path.join(THUMBS_DIR, tname)
                shutil.copy2(thumb, tdst); thumb = tdst
            except Exception as ex:
                messagebox.showwarning(self.t("error"), str(ex))

        con = db()
        con.execute("INSERT INTO videos "
                    "(title,description,source,thumbnail,author,likes,views,created) "
                    "VALUES (?,?,?,?,?,?,?,?)",
                    (title, desc, src, thumb, self.cfg["username"], 0, 0,
                     datetime.datetime.now().isoformat(timespec="seconds")))
        con.commit(); con.close()

        messagebox.showinfo("Tesdo", self.t("published_ok"))
        self.go("feed")

    # ========================================================
    #  AJUSTES
    # ========================================================
    def view_settings(self):
        th = self.theme
        self.header(self.t("settings"))
        wrap = tk.Frame(self.content, bg=th["bg"])
        wrap.pack(fill="both", expand=True, padx=40, pady=10)
        card = tk.Frame(wrap, bg=th["card"], highlightthickness=1,
                        highlightbackground=th["border"])
        card.pack(fill="x")
        inner = tk.Frame(card, bg=th["card"])
        inner.pack(fill="x", padx=28, pady=24)

        tk.Label(inner, text=self.t("appearance"), bg=th["card"], fg=th["text"],
                 font=("Segoe UI",15,"bold")).pack(anchor="w", pady=(0,18))

        tk.Label(inner, text=self.t("username"), bg=th["card"], fg=th["sub"],
                 font=("Segoe UI",9,"bold")).pack(anchor="w")
        e_user = tk.Entry(inner, bg=th["input"], fg=th["text"], relief="flat",
                          insertbackground=th["text"], font=("Segoe UI",11))
        e_user.insert(0, self.cfg["username"])
        e_user.pack(fill="x", ipady=8, pady=(4,18))

        tk.Label(inner, text=self.t("language"), bg=th["card"], fg=th["sub"],
                 font=("Segoe UI",9,"bold")).pack(anchor="w")
        lang_box = ttk.Combobox(inner, state="readonly",
                                values=[f"{LANGUAGE_NAMES[k]}  ({k})" for k in LANGUAGES])
        keys = list(LANGUAGES.keys())
        lang_box.current(keys.index(self.cfg["language"]))
        lang_box.pack(fill="x", pady=(4,18), ipady=5)

        tk.Label(inner, text=self.t("theme"), bg=th["card"], fg=th["sub"],
                 font=("Segoe UI",9,"bold")).pack(anchor="w")
        theme_var = tk.StringVar(value=self.cfg["theme"])
        trow = tk.Frame(inner, bg=th["card"]); trow.pack(anchor="w", pady=(4,18))
        for val, lab in (("dark", self.t("dark")), ("light", self.t("light"))):
            tk.Radiobutton(trow, text=lab, variable=theme_var, value=val,
                           bg=th["card"], fg=th["text"], selectcolor=th["input"],
                           activebackground=th["card"], activeforeground=th["text"],
                           font=("Segoe UI",10), bd=0, highlightthickness=0
                           ).pack(side="left", padx=(0,20))

        tk.Label(inner, text=self.t("accent"), bg=th["card"], fg=th["sub"],
                 font=("Segoe UI",9,"bold")).pack(anchor="w")
        arow = tk.Frame(inner, bg=th["card"]); arow.pack(anchor="w", pady=(4,22))
        swatch = tk.Label(arow, text="      ", bg=self.accent, cursor="hand2")
        swatch.pack(side="left", ipady=8)
        accent_holder = {"v": self.accent}

        def choose_color():
            c = colorchooser.askcolor(color=accent_holder["v"], title=self.t("accent"))
            if c and c[1]:
                accent_holder["v"] = c[1]; swatch.configure(bg=c[1])
        swatch.bind("<Button-1>", lambda e: choose_color())

        for preset in ("#FF2D55","#00C2A8","#3B82F6","#F59E0B",
                       "#A855F7","#22C55E","#EF4444"):
            p = tk.Label(arow, text="   ", bg=preset, cursor="hand2")
            p.pack(side="left", padx=4, ipady=8)
            p.bind("<Button-1>",
                   lambda e, c=preset: (accent_holder.update({"v":c}),
                                        swatch.configure(bg=c)))

        def save_all():
            self.cfg["language"] = keys[lang_box.current()]
            self.cfg["theme"]    = theme_var.get()
            self.cfg["accent"]   = accent_holder["v"]
            self.cfg["username"] = e_user.get().strip() or "Invitado"
            save_config(self.cfg)
            self.build_ui()
            messagebox.showinfo("Tesdo", self.t("saved_ok"))

        tk.Button(inner, text=self.t("save"), command=save_all,
                  bg=self.accent, fg="#fff", relief="flat", bd=0,
                  font=("Segoe UI",11,"bold"), padx=30, cursor="hand2",
                  activebackground=self.accent, activeforeground="#fff"
                  ).pack(anchor="w", ipady=9)

        info = tk.Frame(wrap, bg=th["bg"]); info.pack(fill="x", pady=18)
        tk.Label(info, text=f"Tesdo · {self.t('tagline')}", bg=th["bg"],
                 fg=th["sub"], font=("Segoe UI",9)).pack(anchor="w")
        tk.Label(info, text=f"📁 {DATA_DIR}", bg=th["bg"], fg=th["sub"],
                 font=("Segoe UI",8)).pack(anchor="w", pady=(4,0))
        reproductor_txt = ("Reproductor interno: ffmpeg detectado ✓"
                           if FFMPEG else
                           "Reproductor interno: ffmpeg NO encontrado (usará "
                           "reproductor externo)")
        tk.Label(info, text=reproductor_txt, bg=th["bg"], fg=th["sub"],
                 font=("Segoe UI",8)).pack(anchor="w", pady=(4,0))

    # ========================================================
    #  DATOS
    # ========================================================
    def fetch_videos(self, order="recent"):
        con = db()
        q = "SELECT * FROM videos"; params = ()
        if self.search_text.strip():
            q += " WHERE title LIKE ? OR description LIKE ? OR author LIKE ?"
            like = "%" + self.search_text.strip() + "%"
            params = (like, like, like)
        q += " ORDER BY views DESC, id DESC" if order == "trending" else " ORDER BY id DESC"
        rows = con.execute(q, params).fetchall(); con.close(); return rows

    def fetch_followed_videos(self):
        con = db()
        q = ("SELECT v.* FROM videos v INNER JOIN follows f ON v.author = f.following "
             "WHERE f.follower = ?")
        params = [self.cfg["username"]]
        if self.search_text.strip():
            q += " AND (v.title LIKE ? OR v.description LIKE ?)"
            like = "%" + self.search_text.strip() + "%"
            params += [like, like]
        q += " ORDER BY v.id DESC"
        rows = con.execute(q, params).fetchall(); con.close(); return rows

    def count_comments(self, vid):
        con = db()
        n = con.execute("SELECT COUNT(*) FROM comments WHERE video_id=?", (vid,)).fetchone()[0]
        con.close(); return n

    def count_followers(self, username):
        con = db()
        n = con.execute("SELECT COUNT(*) FROM follows WHERE following=?", (username,)).fetchone()[0]
        con.close(); return n

    def is_following(self, username):
        if username == self.cfg["username"]:
            return False
        con = db()
        r = con.execute("SELECT 1 FROM follows WHERE follower=? AND following=?",
                        (self.cfg["username"], username)).fetchone()
        con.close(); return r is not None

    def toggle_follow(self, username):
        if username == self.cfg["username"]:
            messagebox.showinfo("Tesdo", self.t("cant_follow_self")); return
        con = db()
        if self.is_following(username):
            con.execute("DELETE FROM follows WHERE follower=? AND following=?",
                        (self.cfg["username"], username))
        else:
            con.execute("INSERT OR IGNORE INTO follows (follower,following,created) VALUES (?,?,?)",
                        (self.cfg["username"], username,
                         datetime.datetime.now().isoformat(timespec="seconds")))
        con.commit(); con.close()
        self.render_view()

    def toggle_like(self, vid):
        con = db()
        liked = self.cfg.setdefault("liked", [])
        if vid in liked:
            liked.remove(vid)
            con.execute("UPDATE videos SET likes=MAX(0,likes-1) WHERE id=?", (vid,))
        else:
            liked.append(vid)
            con.execute("UPDATE videos SET likes=likes+1 WHERE id=?", (vid,))
        con.commit(); con.close()
        save_config(self.cfg); self.render_view()

    def play(self, vid):
        con = db()
        row = con.execute("SELECT * FROM videos WHERE id=?", (vid,)).fetchone()
        if row:
            con.execute("UPDATE videos SET views=views+1 WHERE id=?", (vid,))
            con.commit()
        con.close()
        if not row:
            return
        VideoPlayer(self.root, row, self)

    def share(self, row):
        self.root.clipboard_clear(); self.root.clipboard_append(row["source"] or row["title"])
        messagebox.showinfo("Tesdo", self.t("copied"))

    def delete_video(self, vid):
        if not messagebox.askyesno("Tesdo", self.t("confirm_delete")): return
        con = db()
        con.execute("DELETE FROM videos WHERE id=?", (vid,))
        con.execute("DELETE FROM comments WHERE video_id=?", (vid,))
        con.commit(); con.close()
        self.render_view()

    # ---------- comentarios ----------
    def open_comments(self, vid):
        th = self.theme
        con = db()
        video = con.execute("SELECT * FROM videos WHERE id=?", (vid,)).fetchone()
        con.close()
        if not video: return

        win = tk.Toplevel(self.root)
        win.title(f'{self.t("comments")} · {video["title"]}')
        win.geometry("520x560"); win.configure(bg=th["bg"])
        win.transient(self.root)

        tk.Label(win, text=video["title"], bg=th["bg"], fg=th["text"],
                 font=("Segoe UI",13,"bold"), wraplength=470,
                 justify="left").pack(anchor="w", padx=20, pady=(18,4))
        tk.Label(win, text=video["author"], bg=th["bg"], fg=th["sub"],
                 font=("Segoe UI",9)).pack(anchor="w", padx=20)
        tk.Frame(win, bg=th["border"], height=1).pack(fill="x", padx=20, pady=12)

        listbox = tk.Listbox(win, bg=th["card"], fg=th["text"], relief="flat",
                             highlightthickness=0, font=("Segoe UI",10),
                             selectbackground=th["hover"], activestyle="none")
        listbox.pack(fill="both", expand=True, padx=20)

        def reload_comments():
            listbox.delete(0,"end")
            con = db()
            rows = con.execute("SELECT * FROM comments WHERE video_id=? ORDER BY id DESC",
                               (vid,)).fetchall()
            con.close()
            if not rows:
                listbox.insert("end", "   " + self.t("no_videos"))
            for r in rows:
                listbox.insert("end", f'  {r["author"]}:  {r["text"]}')
        reload_comments()

        entry_row = tk.Frame(win, bg=th["bg"]); entry_row.pack(fill="x", padx=20, pady=14)
        e = tk.Entry(entry_row, bg=th["input"], fg=th["text"], relief="flat",
                     insertbackground=th["text"], font=("Segoe UI",10))
        e.pack(side="left", fill="x", expand=True, ipady=8)

        def send_comment(_=None):
            text = e.get().strip()
            if not text: return
            con = db()
            con.execute("INSERT INTO comments (video_id,author,text,created) VALUES (?,?,?,?)",
                        (vid, self.cfg["username"], text,
                         datetime.datetime.now().isoformat(timespec="seconds")))
            con.commit(); con.close()
            e.delete(0,"end"); reload_comments()
        e.bind("<Return>", send_comment)

        tk.Button(entry_row, text=self.t("send"), command=send_comment,
                  bg=self.accent, fg="#fff", relief="flat", bd=0,
                  font=("Segoe UI",10,"bold"), padx=18, cursor="hand2",
                  activebackground=self.accent, activeforeground="#fff"
                  ).pack(side="left", padx=(8,0), ipady=8)


# ============================================================
#  ARRANQUE
# ============================================================
def main():
    ensure_dirs()
    init_db()
    root = tk.Tk()
    try: root.call("tk", "scaling", 1.15)
    except tk.TclError: pass
    TesdoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
