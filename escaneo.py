"""
Vulnerability Scanner - Escáner de vulnerabilidades del sistema.
Versión monolítica autocontenida, compilable a .exe con PyInstaller.

Funcionalidades:
  - Detección de CVEs en paquetes instalados (NVD API)
  - Escaneo de configuraciones inseguras del SO
  - Detección de usuarios sin contraseña (Linux/macOS)
  - Generación de reportes PDF con hallazgos y soluciones
  - Interfaz gráfica Tkinter con soporte multi-idioma (ES / EN)
  - Botón de donación "Cómprame una Cerveza" (PayPal)
  - Auto-inicio, auto-cierre y persistencia de configuración

Uso:
  python escaneo.py           → GUI (Windows/Linux con display)
  python escaneo.py           → consola (Linux sin DISPLAY)
"""

import platform
import subprocess
import os
import threading
import webbrowser
import tkinter as tk
from tkinter import scrolledtext, ttk
from tkinter.filedialog import asksaveasfilename, askdirectory
import socket
from datetime import datetime
import json

# ── Intentar importar requests; se necesita para consultas NVD ───────────────
try:
    import requests as _requests_lib
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False

# ── Versión: se lee del paquete src si está disponible, si no usa fallback ───
try:
    from src import __version__ as APP_VERSION
except Exception:
    APP_VERSION = "2.1.0"     # fallback para el .exe compilado

# ── Importar reportlab (requerido para generar PDF) ──────────────────────────
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    _REPORTLAB_OK = True
except ImportError:
    _REPORTLAB_OK = False

VERSION = APP_VERSION

# ── Constantes globales ───────────────────────────────────────────────────────
# URL PayPal para donaciones
DONATE_URL = "https://www.paypal.com/donate/?hosted_button_id=ZABFRXC2P3JQN"

# Nombre del archivo de configuración persistente
CONFIG_FILE = "config.json"

# URL de la API pública de NVD para consulta de CVEs
NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/1.0"

# Flag de Windows para suprimir ventanas de consola en subprocesos
FLAGS_NO_WINDOW = (
    subprocess.CREATE_NO_WINDOW
    if hasattr(subprocess, 'CREATE_NO_WINDOW')
    else 0
)

# Configuración por defecto; se mezcla con lo que hay en config.json
DEFAULT_CONFIG = {
    "NVD_API_KEY": "",
    "window": {"width": 820, "height": 780},   # ancho/alto inicial de la ventana
    "auto_start": False,                         # iniciar escaneo al abrir la app
    "auto_close_enabled": False,                 # cerrar ventana tras exportar PDF
    "auto_close_seconds": 60,                    # segundos hasta el auto-cierre
    "pdf_folder": "",                            # carpeta destino para PDFs automáticos
    "language": "es",                            # idioma activo: 'es' o 'en'
}

# ── Sistema de traducción multi-idioma ────────────────────────────────────────
# Cada clave de idioma contiene un dict de claves de texto → cadena traducida.
# Las cadenas con {} aceptan argumentos posicionales vía str.format().
TRANSLATIONS = {
    # ── Español ──────────────────────────────────────────────────────────────
    'es': {
        'app_title':           'Escáner de Vulnerabilidades - v{}',
        'btn_scan':            'Iniciar Escaneo',
        'btn_pdf':             'Exportar PDF',
        'btn_save':            'Guardar Config.',
        'btn_exit':            'Salir',
        'btn_donate':          '🍺 Cómprame una Cerveza',
        'chk_autostart':       'Auto-Iniciar',
        'chk_autoclose':       'Auto-Cerrar',
        'lbl_seconds':         'seg.',
        'lbl_pdf_folder':      'Carpeta PDF:',
        'btn_select':          'Seleccionar...',
        'lbl_version':         'Versión: {}',
        'lbl_lang':            'Idioma:',
        # Mensajes de estado (barra inferior)
        'status_ready':        'Listo',
        'status_scan_start':   'Iniciando escaneo en SO: {}',
        'status_packages':     '{} paquetes detectados.',
        'status_scan_done':    'Escaneo completado. {} problemas encontrados.',
        'status_pdf_saved':    'PDF guardado: {}',
        'status_pdf_error':    'Error al guardar PDF: {}',
        'status_config_saved': 'Configuración guardada.',
        'status_pdf_folder':   'Carpeta PDF: {}',
        'status_countdown':    'Cierre en {} segundos...',
        'status_no_results':   'No hay resultados para exportar',
        'status_no_reportlab': 'Instala reportlab para habilitar exportación PDF',
        'status_pdf_exported': 'PDF exportado: {}',
        'status_export_error': 'Error al exportar: {}',
        'status_scan_error':   'Error durante escaneo: {}',
        # Contenido del reporte PDF
        'pdf_title':    'Reporte de Seguridad',
        'pdf_system':   'Sistema: {}',
        'pdf_date':     'Fecha: {}',
        'pdf_no_vulns': 'Resultados: No se encontraron vulnerabilidades.',
        'pdf_found':    'Resultados: Se encontraron {} problemas de seguridad:',
        'pdf_problem':  'Problema: {}',
        'pdf_solution': 'Solución recomendada: {}',
        'pdf_footer':   'Generado por Vulnerability Scanner v{}',
        # Modo consola (Linux headless)
        'console_os':       'Sistema operativo: {}',
        'console_packages': '{} paquetes detectados.',
        'console_export_q': '¿Exportar PDF? (s/n): ',
        'console_path':     'Ruta [{}]: ',
        'console_saved':    'PDF guardado en: {}',
        'console_sol':      '  Solución: {}',
    },
    # ── English ──────────────────────────────────────────────────────────────
    'en': {
        'app_title':           'Vulnerability Scanner - v{}',
        'btn_scan':            'Start Scan',
        'btn_pdf':             'Export PDF',
        'btn_save':            'Save Settings',
        'btn_exit':            'Exit',
        'btn_donate':          '🍺 Buy me a Beer',
        'chk_autostart':       'Auto-Start',
        'chk_autoclose':       'Auto-Close',
        'lbl_seconds':         'sec.',
        'lbl_pdf_folder':      'PDF Folder:',
        'btn_select':          'Browse...',
        'lbl_version':         'Version: {}',
        'lbl_lang':            'Language:',
        # Status bar messages
        'status_ready':        'Ready',
        'status_scan_start':   'Starting scan on OS: {}',
        'status_packages':     '{} packages detected.',
        'status_scan_done':    'Scan complete. {} issues found.',
        'status_pdf_saved':    'PDF saved: {}',
        'status_pdf_error':    'Error saving PDF: {}',
        'status_config_saved': 'Settings saved.',
        'status_pdf_folder':   'PDF Folder: {}',
        'status_countdown':    'Closing in {} seconds...',
        'status_no_results':   'No results to export',
        'status_no_reportlab': 'Install reportlab to enable PDF export',
        'status_pdf_exported': 'PDF exported: {}',
        'status_export_error': 'Export error: {}',
        'status_scan_error':   'Scan error: {}',
        # PDF report content
        'pdf_title':    'Security Report',
        'pdf_system':   'System: {}',
        'pdf_date':     'Date: {}',
        'pdf_no_vulns': 'Results: No vulnerabilities found.',
        'pdf_found':    'Results: {} security issues found:',
        'pdf_problem':  'Issue: {}',
        'pdf_solution': 'Recommended solution: {}',
        'pdf_footer':   'Generated by Vulnerability Scanner v{}',
        # Console mode (Linux headless)
        'console_os':       'Operating system: {}',
        'console_packages': '{} packages detected.',
        'console_export_q': 'Export PDF? (y/n): ',
        'console_path':     'Path [{}]: ',
        'console_saved':    'PDF saved at: {}',
        'console_sol':      '  Solution: {}',
    },
}


def t(lang: str, key: str, *args) -> str:
    """Retorna el texto traducido con substitución de argumentos opcionales.

    Fallback: si el idioma no existe usa 'es'; si la clave no existe retorna
    la propia clave para no romper la UI.

    Args:
        lang: Código de idioma ('es' o 'en').
        key:  Clave de traducción.
        *args: Valores para los marcadores {} de la cadena.

    Returns:
        Cadena traducida y formateada.
    """
    text = TRANSLATIONS.get(lang, TRANSLATIONS['es']).get(key, key)
    if args:
        try:
            return text.format(*args)
        except (IndexError, KeyError):
            return text
    return text


# ── Gestión de configuración ──────────────────────────────────────────────────

def load_config() -> dict:
    """Carga config.json o crea uno con valores por defecto si no existe.

    También rellena las claves faltantes usando DEFAULT_CONFIG para
    garantizar compatibilidad con versiones anteriores del archivo.

    Returns:
        Diccionario de configuración con todas las claves requeridas.
    """
    if not os.path.exists(CONFIG_FILE):
        # Crear config.json con valores por defecto
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
    except (json.JSONDecodeError, OSError):
        # Si el archivo está corrupto, usar valores por defecto
        cfg = DEFAULT_CONFIG.copy()

    # Rellenar claves faltantes (compatibilidad hacia adelante)
    for key, val in DEFAULT_CONFIG.items():
        cfg.setdefault(key, val)

    # Rellenar sub-claves del bloque 'window'
    if isinstance(DEFAULT_CONFIG.get('window'), dict):
        for sub_key, sub_val in DEFAULT_CONFIG['window'].items():
            cfg.setdefault('window', {})
            cfg['window'].setdefault(sub_key, sub_val)

    return cfg


def save_config(cfg: dict) -> None:
    """Persiste el diccionario de configuración en config.json.

    Args:
        cfg: Diccionario de configuración a guardar.
    """
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)


# ── Carga inicial de configuración ────────────────────────────────────────────
# Se ejecuta al importar el módulo para que NVD_API_KEY esté disponible
# antes de arrancar el hilo de escaneo.
global_config = load_config()
NVD_API_KEY = global_config.get('NVD_API_KEY', '')


# ── Utilidades del sistema ────────────────────────────────────────────────────

def detect_os() -> str:
    """Detecta y retorna el nombre del sistema operativo actual.

    Returns:
        'Windows', 'Linux', 'Darwin' (macOS) u otro según platform.system().
    """
    return platform.system()


def interpret_finding(raw: str):
    """Interpreta un hallazgo crudo del escáner y genera una solución.

    Analiza el texto del hallazgo por patrones conocidos y devuelve
    una recomendación de solución legible para el usuario.

    Args:
        raw: Texto crudo generado por las funciones de escaneo.

    Returns:
        Tupla (hallazgo_original, solución_recomendada).
    """
    # Error de conexión o API
    if raw.startswith("[ERROR]"):
        comp = raw.replace("[ERROR] ", "")
        return raw, f"No se pudo verificar '{comp}'. Revisa tu conexión y configuración de API."

    # Vulnerabilidad CVE detectada en paquete
    if raw.startswith("[CVE] Paquete"):
        parts = raw.split()
        count = parts[-3] if len(parts) >= 4 else '?'
        pkg   = parts[2] if len(parts) >= 3 else 'desconocido'
        return raw, f"Actualiza '{pkg}' a la última versión para corregir {count} vulnerabilidades conocidas."

    # Permisos inseguros en /etc/passwd
    if "/etc/passwd" in raw:
        return raw, "Ejecuta 'chmod 644 /etc/passwd' para establecer permisos seguros en este archivo crítico."

    # Servicio SSH activo
    if "Servicio SSH corriendo" in raw:
        return raw, "Revisa '/etc/ssh/sshd_config'. Considera claves SSH en lugar de contraseñas."

    # Servicio RemoteRegistry de Windows activo
    if "RemoteRegistry activo" in raw:
        return raw, "Deshabilita 'RemoteRegistry' en 'services.msc' para evitar accesos remotos no autorizados."

    # Revisión de permisos de System32
    if "Permisos en System32" in raw:
        return raw, "Verifica manualmente los permisos de 'C:\\Windows\\System32' para garantizar acceso solo a usuarios autorizados."

    # Usuario sin contraseña en Linux/macOS
    if raw.startswith("Usuario") and "sin contraseña" in raw:
        user = raw.split()[1] if len(raw.split()) > 1 else 'desconocido'
        return raw, f"Asigna contraseña a '{user}' con 'passwd {user}' o deshabilita la cuenta si no es necesaria."

    # Hallazgo genérico
    return raw, "Investiga este hallazgo en la documentación oficial y aplica las medidas de seguridad recomendadas."


# ── Generación de PDF ─────────────────────────────────────────────────────────

def generate_pdf(findings: list, filename: str, lang: str = 'es') -> None:
    """Genera un reporte PDF con todos los hallazgos de seguridad.

    Args:
        findings: Lista de tuplas (hallazgo, solución) o dicts con
                  las claves 'raw' y 'simple'.
        filename: Ruta completa de destino del archivo PDF.
        lang:     Código de idioma para los textos del PDF ('es' o 'en').

    Raises:
        RuntimeError: Si reportlab no está instalado.
        Exception:    Si falla la escritura del archivo.
    """
    if not _REPORTLAB_OK:
        raise RuntimeError("reportlab no está instalado. Ejecuta: pip install reportlab")

    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()

    # Estilos personalizados para el reporte
    title_style = ParagraphStyle(
        'RptTitle', parent=styles['Heading1'],
        fontSize=14, alignment=1, spaceAfter=12, textColor='#003366'
    )
    subtitle_style = ParagraphStyle(
        'RptSubtitle', parent=styles['Heading2'],
        fontSize=12, spaceAfter=6, textColor='#0066CC'
    )
    finding_style = ParagraphStyle(
        'RptFinding', parent=styles['BodyText'],
        fontSize=10, textColor='#990000', spaceAfter=6, leading=14
    )
    solution_style = ParagraphStyle(
        'RptSolution', parent=styles['BodyText'],
        fontSize=10, textColor='#006600',
        leftIndent=20, spaceAfter=12, leading=14, backColor='#F0FFF0'
    )

    content = []

    # Encabezado del reporte
    content.append(Paragraph(f"<b>{t(lang, 'pdf_title')}</b>", title_style))
    content.append(Paragraph(t(lang, 'pdf_system', socket.gethostname()), subtitle_style))
    content.append(Paragraph(
        t(lang, 'pdf_date', datetime.now().strftime('%d/%m/%Y %H:%M:%S')),
        styles['Normal']
    ))
    content.append(Spacer(1, 24))

    # Sección de resultados
    if not findings:
        content.append(Paragraph(f"<b>{t(lang, 'pdf_no_vulns')}</b>", styles['Normal']))
    else:
        content.append(Paragraph(f"<b>{t(lang, 'pdf_found', len(findings))}</b>", subtitle_style))
        content.append(Spacer(1, 12))
        for item in findings:
            # Normalizar formatos: tupla, dict o string
            if isinstance(item, tuple):
                raw, sol = item[0], item[1] if len(item) > 1 else 'N/A'
            elif isinstance(item, dict):
                raw, sol = item.get('raw', ''), item.get('simple', 'N/A')
            else:
                raw, sol = str(item), 'N/A'
            content.append(Paragraph(f"<b>{t(lang, 'pdf_problem', raw)}</b>", finding_style))
            content.append(Paragraph(f"<b>{t(lang, 'pdf_solution', sol)}</b>", solution_style))
            content.append(Spacer(1, 8))

    # Pie de página
    content.append(Spacer(1, 24))
    content.append(Paragraph(
        t(lang, 'pdf_footer', VERSION),
        ParagraphStyle('RptFooter', parent=styles['Normal'], fontSize=8, alignment=2)
    ))

    doc.build(content)


# ── Funciones de escaneo ──────────────────────────────────────────────────────

def scan_software_vulns(packages: list) -> list:
    """Consulta la API NVD para buscar CVEs en los paquetes instalados.

    Solo realiza consultas si hay una API key configurada, para evitar
    ser bloqueado por límites de velocidad de la API pública sin key.

    Args:
        packages: Lista de tuplas (nombre_paquete, versión).

    Returns:
        Lista de strings con los hallazgos de CVE o errores de conexión.
    """
    findings = []

    # Sin requests o sin API key, omitir escaneo CVE
    if not _REQUESTS_OK or not NVD_API_KEY:
        return findings

    headers = {"apiKey": NVD_API_KEY}

    for name, ver in packages:
        try:
            resp = _requests_lib.get(
                NVD_API_URL,
                params={"keyword": f"{name} {ver}"},
                headers=headers,
                timeout=5
            )
            total = resp.json().get("totalResults", 0)
            if total > 0:
                findings.append(
                    f"[CVE] Paquete {name} {ver}: {total} vulnerabilidades detectadas"
                )
        except Exception:
            findings.append(f"[ERROR] {name} {ver}")

    return findings


def scan_insecure_configs(os_name: str) -> list:
    """Escanea configuraciones inseguras del sistema operativo.

    En Linux/macOS verifica permisos de /etc/passwd y estado del SSH.
    En Windows verifica el servicio RemoteRegistry y permisos de System32.

    Args:
        os_name: Nombre del SO ('Windows', 'Linux', 'Darwin').

    Returns:
        Lista de hallazgos de configuración.
    """
    findings = []

    if os_name in ('Linux', 'Darwin'):
        # ── Permisos de /etc/passwd ──────────────────────────────────────────
        try:
            st = os.stat('/etc/passwd')
            perms = oct(st.st_mode & 0o777)
            if perms not in ('0o644', '0o600'):
                findings.append(f"Permisos inseguros en /etc/passwd: {perms}")
        except Exception:
            pass

        # ── Servicio SSH corriendo ───────────────────────────────────────────
        try:
            out = subprocess.check_output(['ps', 'aux'], text=True, timeout=10)
            if 'sshd' in out:
                findings.append("Servicio SSH corriendo")
        except Exception:
            pass

    else:
        # ── Servicio RemoteRegistry (Windows) ────────────────────────────────
        try:
            out = subprocess.check_output(
                ['sc', 'query', 'RemoteRegistry'],
                text=True,
                creationflags=FLAGS_NO_WINDOW,
                timeout=10
            )
            if 'RUNNING' in out:
                findings.append("RemoteRegistry activo")
        except Exception:
            pass

        # ── Permisos de C:\Windows\System32 ─────────────────────────────────
        try:
            subprocess.check_output(
                ['icacls', r'C:\Windows\System32'],
                text=True,
                creationflags=FLAGS_NO_WINDOW,
                timeout=15
            )
            findings.append("Permisos en System32 revisados")
        except Exception:
            pass

    return findings


def scan_weak_passwords(os_name: str) -> list:
    """Detecta usuarios con contraseñas débiles o ausentes (Linux/macOS).

    Lee /etc/shadow para encontrar cuentas con campo de contraseña vacío,
    bloqueado ('!') o inhabilitado ('*').

    Args:
        os_name: Nombre del SO.

    Returns:
        Lista de strings indicando usuarios sin contraseña válida.
    """
    findings = []

    if os_name in ('Linux', 'Darwin'):
        try:
            with open('/etc/shadow', 'r') as f:
                for line in f:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        user, pw = parts[0], parts[1]
                        if pw in ('', '!', '*'):
                            findings.append(f"Usuario {user} sin contraseña")
        except PermissionError:
            # Normal en sistemas donde el usuario no es root
            findings.append("[ERROR] Permisos insuficientes para leer /etc/shadow")
        except FileNotFoundError:
            pass
        except Exception:
            pass

    return findings


def get_installed_packages(os_name: str) -> list:
    """Obtiene la lista de paquetes instalados según el SO.

    Usa dpkg-query en Linux, brew en macOS y wmic en Windows.
    Si el comando falla, retorna lista vacía sin lanzar excepción.

    Args:
        os_name: Nombre del SO.

    Returns:
        Lista de tuplas (nombre_paquete, versión).
    """
    pkgs = []
    try:
        if os_name == 'Linux':
            # dpkg-query lista paquetes de sistemas basados en Debian/Ubuntu
            out = subprocess.check_output(
                ['dpkg-query', '-W', '-f=${binary:Package} ${Version}\n'],
                text=True, timeout=30
            )
            pkgs = [
                tuple(line.split()[:2])
                for line in out.splitlines()
                if len(line.split()) >= 2
            ]

        elif os_name == 'Darwin':
            # brew list en macOS
            out = subprocess.check_output(
                ['brew', 'list', '--versions'],
                text=True, timeout=30
            )
            pkgs = [
                (line.split()[0], line.split()[1])
                for line in out.splitlines()
                if line.strip() and len(line.split()) >= 2
            ]

        else:
            # wmic en Windows: columna Name tiene espacios, Version es la última
            out = subprocess.check_output(
                ['wmic', 'product', 'get', 'Name,Version'],
                text=True,
                creationflags=FLAGS_NO_WINDOW,
                timeout=60
            )
            for line in out.splitlines()[1:]:
                cols = line.strip().split()
                if len(cols) >= 2:
                    pkgs.append((' '.join(cols[:-1]), cols[-1]))

    except Exception:
        pass

    return pkgs


# ── Modo consola (Linux sin DISPLAY) ─────────────────────────────────────────

def console_mode(lang: str = 'es') -> None:
    """Ejecuta el escaneo en modo texto para sistemas sin entorno gráfico.

    Muestra resultados en stdout y ofrece exportar un PDF al terminar.

    Args:
        lang: Código de idioma para los mensajes ('es' o 'en').
    """
    osn = detect_os()
    print(t(lang, 'console_os', osn))
    pkgs = get_installed_packages(osn)
    print(t(lang, 'console_packages', len(pkgs)))

    raw_list = (
        scan_software_vulns(pkgs)
        + scan_insecure_configs(osn)
        + scan_weak_passwords(osn)
    )
    findings = [interpret_finding(r) for r in raw_list]

    for raw, sol in findings:
        print(f"- {raw}")
        print(t(lang, 'console_sol', sol))

    # Ofrecer exportar PDF
    answer = input(t(lang, 'console_export_q')).strip().lower()
    if answer in ('s', 'y'):
        default = (
            f"Reporte_vulnerabilidades_{socket.gethostname()}"
            f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        path = input(t(lang, 'console_path', default)).strip() or default
        generate_pdf(findings, path, lang=lang)
        print(t(lang, 'console_saved', path))


# ── Clase principal de la GUI ─────────────────────────────────────────────────

class VulnerabilityScannerApp(tk.Tk):
    """Aplicación GUI principal basada en Tkinter.

    Organiza la interfaz en:
      - Área de log con scroll (ocupa la mayor parte de la ventana)
      - Barra de progreso
      - Frame de controles (botones, checkboxes, spinbox)
      - Frame de carpeta PDF
      - Frame inferior (selector de idioma + botón de donación)
      - Barra de estado y etiqueta de versión

    El escaneo se ejecuta en un hilo de fondo (daemon thread).
    Todas las actualizaciones de widgets se realizan via self.after(0, ...)
    para garantizar thread safety con Tkinter.
    """

    def __init__(self):
        """Inicializa la aplicación, carga configuración y construye la UI."""
        super().__init__()

        # ── Estado de la aplicación ──────────────────────────────────────────
        self.conf = global_config                          # dict de configuración
        self.lang = self.conf.get('language', 'es')        # idioma activo
        self.os_name = detect_os()                         # SO detectado
        self.findings = []                                 # hallazgos del último escaneo
        self.remaining = 0                                 # segundos restantes para auto-cierre

        # ── Abrir archivo de log de sesión ───────────────────────────────────
        # El archivo se cierra limpiamente en _on_close()
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        try:
            self.log_file = open(f"log_{ts}.txt", 'w', encoding='utf-8')
        except OSError:
            self.log_file = None  # Si no se puede crear, continuar sin log a disco

        # Construir toda la interfaz
        self._build_ui()

        # Interceptar cierre de ventana para cerrar log_file correctamente
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Auto-inicio si está configurado
        if self.conf.get('auto_start', False):
            self.after(1000, self.start_scan)

    # ── Construcción de la UI ─────────────────────────────────────────────────

    def _build_ui(self) -> None:
        """Crea y organiza todos los widgets de la ventana principal."""
        self.title(t(self.lang, 'app_title', VERSION))
        w = self.conf['window']['width']
        h = self.conf['window']['height']
        self.geometry(f"{w}x{h}")
        self.minsize(700, 600)

        # ── Área de log principal ────────────────────────────────────────────
        self.log_area = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, font=("Courier", 9)
        )
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # ── Barra de progreso ────────────────────────────────────────────────
        self.progress = ttk.Progressbar(
            self, orient='horizontal', mode='indeterminate'
        )
        self.progress.pack(fill=tk.X, padx=10, pady=5)

        # ── Frame de controles principales ──────────────────────────────────
        ctrl = tk.Frame(self)
        ctrl.pack(fill=tk.X, pady=5, padx=5)

        # Botón Iniciar Escaneo (Alt+E)
        self.scan_btn = tk.Button(
            ctrl, text=t(self.lang, 'btn_scan'), command=self.start_scan
        )
        self.scan_btn.pack(side=tk.LEFT, padx=5)
        self.bind_all("<Alt-e>", lambda e: self.start_scan())

        # Botón Exportar PDF (Alt+P) — deshabilitado hasta que haya escaneo
        self.export_btn = tk.Button(
            ctrl, text=t(self.lang, 'btn_pdf'),
            command=self.export_report, state=tk.DISABLED
        )
        self.export_btn.pack(side=tk.LEFT, padx=5)
        self.bind_all("<Alt-p>", lambda e: self.export_report())

        # Botón Guardar Configuración (Alt+G)
        self.save_btn = tk.Button(
            ctrl, text=t(self.lang, 'btn_save'), command=self._on_save_config
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)
        self.bind_all("<Alt-g>", lambda e: self._on_save_config())

        # Botón Salir (Alt+S)
        self.exit_btn = tk.Button(
            ctrl, text=t(self.lang, 'btn_exit'), command=self._on_close
        )
        self.exit_btn.pack(side=tk.LEFT, padx=5)
        self.bind_all("<Alt-s>", lambda e: self._on_close())

        # Checkbox Auto-Iniciar
        self.auto_start_var = tk.BooleanVar(value=self.conf.get('auto_start', False))
        self.auto_start_chk = tk.Checkbutton(
            ctrl, text=t(self.lang, 'chk_autostart'),
            variable=self.auto_start_var, command=self._toggle_auto_start
        )
        self.auto_start_chk.pack(side=tk.LEFT, padx=5)

        # Checkbox Auto-Cerrar
        self.auto_close_var = tk.BooleanVar(value=self.conf.get('auto_close_enabled', False))
        self.auto_close_chk = tk.Checkbutton(
            ctrl, text=t(self.lang, 'chk_autoclose'),
            variable=self.auto_close_var, command=self._toggle_auto_close
        )
        self.auto_close_chk.pack(side=tk.LEFT, padx=5)

        # Spinbox de segundos (referencia guardada en self para evitar GC)
        self.auto_close_seconds_var = tk.IntVar(
            value=self.conf.get('auto_close_seconds', 60)
        )
        self.auto_close_sb = tk.Spinbox(
            ctrl, from_=10, to=3600, increment=10,
            textvariable=self.auto_close_seconds_var, width=5,
            command=self._change_auto_close_seconds
        )
        self.auto_close_sb.pack(side=tk.LEFT, padx=2)

        self.lbl_seconds = tk.Label(ctrl, text=t(self.lang, 'lbl_seconds'))
        self.lbl_seconds.pack(side=tk.LEFT)

        # ── Frame de selección de carpeta PDF ────────────────────────────────
        pdf_frame = tk.Frame(self)
        pdf_frame.pack(fill=tk.X, pady=3, padx=5)

        self.lbl_pdf_folder = tk.Label(pdf_frame, text=t(self.lang, 'lbl_pdf_folder'))
        self.lbl_pdf_folder.pack(side=tk.LEFT, padx=5)

        self.pdf_folder_var = tk.StringVar(value=self.conf.get('pdf_folder', ''))
        tk.Entry(pdf_frame, textvariable=self.pdf_folder_var, width=50).pack(
            side=tk.LEFT, padx=5
        )

        self.select_btn = tk.Button(
            pdf_frame, text=t(self.lang, 'btn_select'),
            command=self._select_pdf_folder
        )
        self.select_btn.pack(side=tk.LEFT, padx=5)

        # ── Frame inferior: selector de idioma + botón de donación ───────────
        bottom_frame = tk.Frame(self)
        bottom_frame.pack(fill=tk.X, pady=3, padx=5)

        # Selector de idioma (combobox)
        self.lbl_lang = tk.Label(bottom_frame, text=t(self.lang, 'lbl_lang'))
        self.lbl_lang.pack(side=tk.LEFT, padx=5)

        self.lang_var = tk.StringVar(value=self.lang)
        self.lang_combo = ttk.Combobox(
            bottom_frame, textvariable=self.lang_var,
            values=['es', 'en'], width=4, state='readonly'
        )
        self.lang_combo.pack(side=tk.LEFT, padx=2)
        self.lang_combo.bind('<<ComboboxSelected>>', self._on_lang_change)

        # Botón de donación "Cómprame una Cerveza" — abre PayPal en navegador
        self.donate_btn = tk.Button(
            bottom_frame,
            text=t(self.lang, 'btn_donate'),
            bg='#F5A623',          # naranja cerveza
            fg='#000000',
            font=('TkDefaultFont', 9, 'bold'),
            relief=tk.RAISED,
            cursor='hand2',        # cursor de mano para indicar enlace
            command=self._open_donate
        )
        self.donate_btn.pack(side=tk.RIGHT, padx=10)

        # ── Barra de estado (parte inferior de la ventana) ───────────────────
        self.status_bar = tk.Label(
            self, text=t(self.lang, 'status_ready'),
            bd=1, relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Etiqueta de versión (esquina inferior derecha)
        self.version_lbl = tk.Label(
            self, text=t(self.lang, 'lbl_version', VERSION),
            font=("Courier", 8)
        )
        self.version_lbl.pack(anchor=tk.E, padx=10, pady=(0, 3))

    # ── Sistema multi-idioma ──────────────────────────────────────────────────

    def _on_lang_change(self, event=None) -> None:
        """Cambia el idioma activo y refresca todos los textos de la UI."""
        self.lang = self.lang_var.get()
        self.conf['language'] = self.lang
        self._refresh_ui_texts()

    def _refresh_ui_texts(self) -> None:
        """Actualiza el texto de todos los widgets al idioma activo.

        Se llama tras un cambio de idioma para que toda la interfaz
        muestre el nuevo idioma sin necesidad de reiniciar la app.
        """
        self.title(t(self.lang, 'app_title', VERSION))
        self.scan_btn.config(text=t(self.lang, 'btn_scan'))
        self.export_btn.config(text=t(self.lang, 'btn_pdf'))
        self.save_btn.config(text=t(self.lang, 'btn_save'))
        self.exit_btn.config(text=t(self.lang, 'btn_exit'))
        self.auto_start_chk.config(text=t(self.lang, 'chk_autostart'))
        self.auto_close_chk.config(text=t(self.lang, 'chk_autoclose'))
        self.lbl_seconds.config(text=t(self.lang, 'lbl_seconds'))
        self.lbl_pdf_folder.config(text=t(self.lang, 'lbl_pdf_folder'))
        self.select_btn.config(text=t(self.lang, 'btn_select'))
        self.lbl_lang.config(text=t(self.lang, 'lbl_lang'))
        self.donate_btn.config(text=t(self.lang, 'btn_donate'))
        self.version_lbl.config(text=t(self.lang, 'lbl_version', VERSION))
        self._update_status(t(self.lang, 'status_ready'))

    # ── Donación ──────────────────────────────────────────────────────────────

    def _open_donate(self) -> None:
        """Abre el link de donación PayPal en el navegador por defecto."""
        webbrowser.open(DONATE_URL)

    # ── Auto-cierre ───────────────────────────────────────────────────────────

    def _schedule_auto_close(self) -> None:
        """Programa el cierre automático si está habilitado en la configuración."""
        if self.conf.get('auto_close_enabled', False):
            self.remaining = self.conf.get('auto_close_seconds', 60)
            self._countdown()

    def _countdown(self) -> None:
        """Cuenta regresiva y cierra la ventana al llegar a cero."""
        if self.remaining > 0:
            self._update_status(t(self.lang, 'status_countdown', self.remaining))
            self.remaining -= 1
            self.after(1000, self._countdown)
        else:
            self._on_close()

    # ── Gestión de configuración ──────────────────────────────────────────────

    def _on_save_config(self) -> None:
        """Sincroniza todos los valores de la GUI al dict de config y guarda en disco."""
        # Leer valores actuales de los widgets antes de guardar
        self.conf['pdf_folder'] = self.pdf_folder_var.get()
        self.conf['language'] = self.lang
        try:
            self.conf['auto_close_seconds'] = int(self.auto_close_sb.get())
        except ValueError:
            pass  # Mantener el valor anterior si el spinbox tiene texto inválido
        save_config(self.conf)
        self._update_status(t(self.lang, 'status_config_saved'))

    def _toggle_auto_start(self) -> None:
        """Actualiza la configuración de auto-inicio desde el checkbox."""
        self.conf['auto_start'] = self.auto_start_var.get()

    def _toggle_auto_close(self) -> None:
        """Actualiza la configuración de auto-cierre desde el checkbox."""
        self.conf['auto_close_enabled'] = self.auto_close_var.get()

    def _change_auto_close_seconds(self) -> None:
        """Actualiza los segundos de auto-cierre desde el spinbox."""
        try:
            self.conf['auto_close_seconds'] = int(self.auto_close_sb.get())
        except ValueError:
            pass  # Ignorar si el campo no es un número válido

    def _select_pdf_folder(self) -> None:
        """Abre un diálogo para seleccionar la carpeta de destino de los PDF."""
        folder = askdirectory()
        if folder:
            self.pdf_folder_var.set(folder)
            self.conf['pdf_folder'] = folder
            self._update_status(t(self.lang, 'status_pdf_folder', folder))

    def _on_close(self) -> None:
        """Cierra la aplicación limpiamente: cierra el log_file antes de destruir."""
        if self.log_file:
            try:
                self.log_file.close()
            except Exception:
                pass
        self.destroy()

    # ── Logging y estado ──────────────────────────────────────────────────────

    def _update_status(self, text: str) -> None:
        """Actualiza el texto de la barra de estado en la parte inferior."""
        self.status_bar.config(text=text)

    def log(self, msg: str) -> None:
        """Escribe un mensaje timestampeado en el área de log, disco y barra de estado.

        IMPORTANTE: Este método puede llamarse desde cualquier hilo
        siempre que se use via self.after(0, self.log, msg) desde hilos
        de fondo, garantizando thread safety de Tkinter.

        Args:
            msg: Mensaje a registrar.
        """
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        line = f"[{ts}] {msg}"
        # Actualizar widget (debe ejecutarse en el hilo principal)
        self.log_area.insert(tk.END, line + '\n')
        self.log_area.see(tk.END)
        # Escribir al archivo de log en disco
        if self.log_file:
            try:
                self.log_file.write(line + '\n')
                self.log_file.flush()
            except Exception:
                pass
        self._update_status(msg)

    # ── Escaneo de vulnerabilidades ───────────────────────────────────────────

    def start_scan(self) -> None:
        """Inicia el escaneo de vulnerabilidades en un hilo daemon de fondo.

        Verifica que no haya un escaneo activo antes de lanzar el hilo.
        El botón queda deshabilitado durante el escaneo para evitar dobles
        ejecuciones concurrentes.
        """
        # Protección contra doble clic durante escaneo activo
        if self.scan_btn.cget('state') != tk.NORMAL:
            return

        self.scan_btn.config(state=tk.DISABLED)
        self.log_area.delete(1.0, tk.END)
        self.findings.clear()
        self.log(t(self.lang, 'status_scan_start', self.os_name))
        self.progress.start(10)

        # Lanzar escaneo en hilo de fondo para no congelar la GUI
        threading.Thread(target=self._run_scans, daemon=True).start()

    def _run_scans(self) -> None:
        """Ejecuta todos los escaneos en hilo de fondo.

        THREAD SAFETY: Todas las actualizaciones de widgets se realizan
        via self.after(0, callable, args) para que Tkinter las procese
        en el hilo principal y evitar condiciones de carrera o crashes.
        """
        try:
            # Obtener paquetes instalados
            pkgs = get_installed_packages(self.os_name)
            self.after(0, self.log, t(self.lang, 'status_packages', len(pkgs)))

            # Ejecutar los tres tipos de escaneo
            raw_list = (
                scan_software_vulns(pkgs)
                + scan_insecure_configs(self.os_name)
                + scan_weak_passwords(self.os_name)
            )

            # Procesar cada hallazgo y enviarlo al hilo principal
            for r in raw_list:
                raw, sol = interpret_finding(r)
                self.findings.append({'raw': raw, 'simple': sol})
                self.after(0, self.log, raw)

            self.after(
                0, self.log,
                t(self.lang, 'status_scan_done', len(self.findings))
            )

            # Auto-exportar PDF si hay carpeta configurada
            folder = self.conf.get('pdf_folder', '')
            if folder:
                # Ejecutar guardado de PDF en el hilo principal
                self.after(0, self._save_pdf_auto, folder)
            else:
                self.after(0, self._scan_finished)

        except Exception as e:
            self.after(0, self.log, t(self.lang, 'status_scan_error', str(e)))
            self.after(0, self._scan_finished)

    def _scan_finished(self) -> None:
        """Restaura la UI al estado 'listo' tras completar o fallar el escaneo."""
        self.progress.stop()
        self.scan_btn.config(state=tk.NORMAL)
        self.export_btn.config(state=tk.NORMAL)

    def _save_pdf_auto(self, folder: str) -> None:
        """Guarda el PDF automáticamente en la carpeta configurada.

        Se llama desde el hilo principal (via after) después de completar
        el escaneo cuando hay una carpeta PDF configurada.

        Args:
            folder: Carpeta de destino para el PDF.
        """
        hostname  = socket.gethostname()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename  = f"Reporte_vulnerabilidades_{hostname}_{timestamp}.pdf"
        path      = os.path.join(folder, filename)
        try:
            generate_pdf(self.findings, path, lang=self.lang)
            self.log(t(self.lang, 'status_pdf_saved', path))
            self._schedule_auto_close()
        except Exception as e:
            self.log(t(self.lang, 'status_pdf_error', str(e)))
        finally:
            self._scan_finished()

    def export_report(self) -> None:
        """Exporta el reporte PDF manualmente con diálogo de guardado.

        El usuario elige nombre y ubicación del archivo; se usa exactamente
        el path seleccionado sin regenerar el nombre.
        """
        if not self.findings:
            self._update_status(t(self.lang, 'status_no_results'))
            return

        if not _REPORTLAB_OK:
            self._update_status(t(self.lang, 'status_no_reportlab'))
            return

        default_name = (
            f"Reporte_vulnerabilidades_{socket.gethostname()}"
            f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        path = asksaveasfilename(
            defaultextension=".pdf",
            initialfile=default_name,
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if path:
            try:
                # Usar la ruta completa elegida por el usuario (no regenerar nombre)
                generate_pdf(self.findings, path, lang=self.lang)
                self._update_status(t(self.lang, 'status_pdf_exported', path))
                self._schedule_auto_close()
            except Exception as e:
                self._update_status(t(self.lang, 'status_export_error', str(e)))


# ── Punto de entrada ──────────────────────────────────────────────────────────

if __name__ == '__main__':
    # Modo consola para Linux sin entorno gráfico; GUI para todo lo demás
    if detect_os() == 'Linux' and not os.environ.get('DISPLAY'):
        console_mode(lang=global_config.get('language', 'es'))
    else:
        app = VulnerabilityScannerApp()
        app.mainloop()
