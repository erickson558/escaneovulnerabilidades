"""Módulo GUI para Vulnerability Scanner (arquitectura modular).

Proporciona la interfaz gráfica Tkinter con soporte multi-idioma (ES/EN),
botón de donación, y thread safety para el escaneo en segundo plano.
"""

import tkinter as tk
from tkinter import scrolledtext, ttk, filedialog
import threading
import webbrowser
from datetime import datetime
from typing import List
import socket
import os

from src import __version__
from src.config import ConfigManager
from src.logger import LoggerManager
from src.backend.scanner import VulnerabilityScanner
from src.backend.pdf_generator import PDFReportGenerator
from src.utils.helpers import detect_os, interpret_finding
from src.i18n import get_text as _t, DONATE_URL


class VulnerabilityScannerApp(tk.Tk):
    """Aplicación GUI principal del escáner de vulnerabilidades.

    Organiza la interfaz en:
      - Área de log con scroll (zona principal)
      - Barra de progreso indeterminada
      - Frame de controles (botones, checkboxes, spinbox)
      - Frame de carpeta PDF
      - Frame inferior (idioma + botón donación)
      - Barra de estado y etiqueta de versión

    El escaneo corre en un hilo daemon; todas las actualizaciones de
    widgets se enrutan al hilo principal mediante self.after(0, …)
    para garantizar thread safety de Tkinter.
    """

    def __init__(self, version: str = __version__):
        """Inicializa la app, carga configuración y construye la UI.

        Args:
            version: Cadena de versión mostrada en el título y pie de página.
        """
        super().__init__()

        # ── Servicios ────────────────────────────────────────────────────────
        self.version    = version
        self.config_mgr = ConfigManager()
        self.logger_mgr = LoggerManager()
        self.logger     = self.logger_mgr.get_logger()
        self.os_name    = detect_os()

        # Idioma activo (se persiste en config.json)
        self.lang: str = self.config_mgr.get('language', 'es')

        # Escáner de vulnerabilidades con la API key configurada
        self.scanner = VulnerabilityScanner(
            nvd_api_key=self.config_mgr.get('NVD_API_KEY', '')
        )

        # Generador de PDF (opcional: puede no estar disponible si falta reportlab)
        try:
            self.pdf_generator = PDFReportGenerator(version=version)
        except ImportError:
            self.pdf_generator = None
            self.logger.warning("reportlab no instalado — exportación PDF deshabilitada")

        # Lista de hallazgos del último escaneo
        self.findings: List[dict] = []

        # Construir toda la interfaz
        self._setup_ui()

        # Interceptar cierre de ventana para limpieza ordenada
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Auto-inicio si está configurado
        if self.config_mgr.get('auto_start', False):
            self.after(1000, self.start_scan)

    # ── Construcción de la UI ─────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        """Crea y organiza todos los widgets de la ventana principal."""
        self.title(_t(self.lang, 'app_title', self.version))
        width  = self.config_mgr['window']['width']
        height = self.config_mgr['window']['height']
        self.geometry(f"{width}x{height}")
        self.minsize(700, 600)

        # Área de log con fuente monoespaciada para alinear columnas
        self.log_area = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, font=("Courier", 9)
        )
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Barra de progreso indeterminada (activa durante el escaneo)
        self.progress = ttk.Progressbar(
            self, orient='horizontal', mode='indeterminate'
        )
        self.progress.pack(fill=tk.X, padx=10, pady=5)

        # Frames individuales
        self._setup_control_buttons()
        self._setup_pdf_folder_frame()
        self._setup_bottom_frame()

        # Barra de estado (parte inferior de la ventana)
        self.status_bar = tk.Label(
            self, text=_t(self.lang, 'status_ready'),
            bd=1, relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Etiqueta de versión (esquina inferior derecha)
        self.version_lbl = tk.Label(
            self,
            text=_t(self.lang, 'lbl_version', self.version),
            font=("Courier", 8)
        )
        self.version_lbl.pack(anchor=tk.E, padx=10, pady=(0, 3))

    def _setup_control_buttons(self) -> None:
        """Crea el frame con botones de acción, checkboxes y spinbox."""
        ctrl = tk.Frame(self)
        ctrl.pack(fill=tk.X, pady=5, padx=5)

        # Botón Iniciar Escaneo (Alt+E)
        self.scan_btn = tk.Button(
            ctrl, text=_t(self.lang, 'btn_scan'),
            underline=8, command=self.start_scan
        )
        self.scan_btn.pack(side=tk.LEFT, padx=5)
        self.bind_all("<Alt-e>", lambda e: self.start_scan())

        # Botón Exportar PDF (Alt+P) — deshabilitado hasta que haya escaneo
        self.export_btn = tk.Button(
            ctrl, text=_t(self.lang, 'btn_pdf'),
            underline=9, command=self.export_report, state=tk.DISABLED
        )
        self.export_btn.pack(side=tk.LEFT, padx=5)
        self.bind_all("<Alt-p>", lambda e: self.export_report())

        # Botón Guardar Configuración (Alt+G)
        self.save_btn = tk.Button(
            ctrl, text=_t(self.lang, 'btn_save'),
            underline=0, command=self.save_config
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)
        self.bind_all("<Alt-g>", lambda e: self.save_config())

        # Botón Salir (Alt+S)
        self.exit_btn = tk.Button(
            ctrl, text=_t(self.lang, 'btn_exit'),
            underline=0, command=self._on_close
        )
        self.exit_btn.pack(side=tk.LEFT, padx=5)
        self.bind_all("<Alt-s>", lambda e: self._on_close())

        # Checkbox Auto-Iniciar
        self.auto_start_var = tk.BooleanVar(
            value=self.config_mgr.get('auto_start', False)
        )
        self.auto_start_chk = tk.Checkbutton(
            ctrl, text=_t(self.lang, 'chk_autostart'),
            variable=self.auto_start_var, command=self._toggle_auto_start
        )
        self.auto_start_chk.pack(side=tk.LEFT, padx=5)

        # Checkbox Auto-Cerrar
        self.auto_close_var = tk.BooleanVar(
            value=self.config_mgr.get('auto_close_enabled', False)
        )
        self.auto_close_chk = tk.Checkbutton(
            ctrl, text=_t(self.lang, 'chk_autoclose'),
            variable=self.auto_close_var, command=self._toggle_auto_close
        )
        self.auto_close_chk.pack(side=tk.LEFT, padx=5)

        # Spinbox de segundos — referencia en self para evitar GC del IntVar
        self.auto_close_seconds_var = tk.IntVar(
            value=self.config_mgr.get('auto_close_seconds', 60)
        )
        self.auto_close_sb = tk.Spinbox(
            ctrl, from_=10, to=3600, increment=10,
            textvariable=self.auto_close_seconds_var, width=5,
            command=self._change_auto_close_seconds
        )
        self.auto_close_sb.pack(side=tk.LEFT, padx=2)

        self.lbl_seconds = tk.Label(ctrl, text=_t(self.lang, 'lbl_seconds'))
        self.lbl_seconds.pack(side=tk.LEFT)

    def _setup_pdf_folder_frame(self) -> None:
        """Crea el frame de selección de carpeta de destino para los PDF."""
        pdf_frame = tk.Frame(self)
        pdf_frame.pack(fill=tk.X, pady=3, padx=5)

        self.lbl_pdf_folder = tk.Label(pdf_frame, text=_t(self.lang, 'lbl_pdf_folder'))
        self.lbl_pdf_folder.pack(side=tk.LEFT, padx=5)

        self.pdf_folder_var = tk.StringVar(
            value=self.config_mgr.get('pdf_folder', '')
        )
        tk.Entry(pdf_frame, textvariable=self.pdf_folder_var, width=50).pack(
            side=tk.LEFT, padx=5
        )

        self.select_btn = tk.Button(
            pdf_frame, text=_t(self.lang, 'btn_select'),
            command=self._select_pdf_folder
        )
        self.select_btn.pack(side=tk.LEFT, padx=5)

    def _setup_bottom_frame(self) -> None:
        """Crea el frame inferior con selector de idioma y botón de donación."""
        bottom = tk.Frame(self)
        bottom.pack(fill=tk.X, pady=3, padx=5)

        # Etiqueta + combobox de idioma
        self.lbl_lang = tk.Label(bottom, text=_t(self.lang, 'lbl_lang'))
        self.lbl_lang.pack(side=tk.LEFT, padx=5)

        self.lang_var = tk.StringVar(value=self.lang)
        self.lang_combo = ttk.Combobox(
            bottom, textvariable=self.lang_var,
            values=['es', 'en'], width=4, state='readonly'
        )
        self.lang_combo.pack(side=tk.LEFT, padx=2)
        self.lang_combo.bind('<<ComboboxSelected>>', self._on_lang_change)

        # Botón de donación PayPal (lado derecho del frame)
        self.donate_btn = tk.Button(
            bottom,
            text=_t(self.lang, 'btn_donate'),
            bg='#F5A623',
            fg='#000000',
            font=('TkDefaultFont', 9, 'bold'),
            relief=tk.RAISED,
            cursor='hand2',
            command=self._open_donate
        )
        self.donate_btn.pack(side=tk.RIGHT, padx=10)

    # ── Sistema multi-idioma ──────────────────────────────────────────────────

    def _on_lang_change(self, event=None) -> None:
        """Cambia el idioma activo y refresca todos los textos de la UI."""
        self.lang = self.lang_var.get()
        self.config_mgr['language'] = self.lang
        self._refresh_ui_texts()

    def _refresh_ui_texts(self) -> None:
        """Actualiza el texto de todos los widgets al idioma activo."""
        self.title(_t(self.lang, 'app_title', self.version))
        self.scan_btn.config(text=_t(self.lang, 'btn_scan'))
        self.export_btn.config(text=_t(self.lang, 'btn_pdf'))
        self.save_btn.config(text=_t(self.lang, 'btn_save'))
        self.exit_btn.config(text=_t(self.lang, 'btn_exit'))
        self.auto_start_chk.config(text=_t(self.lang, 'chk_autostart'))
        self.auto_close_chk.config(text=_t(self.lang, 'chk_autoclose'))
        self.lbl_seconds.config(text=_t(self.lang, 'lbl_seconds'))
        self.lbl_pdf_folder.config(text=_t(self.lang, 'lbl_pdf_folder'))
        self.select_btn.config(text=_t(self.lang, 'btn_select'))
        self.lbl_lang.config(text=_t(self.lang, 'lbl_lang'))
        self.donate_btn.config(text=_t(self.lang, 'btn_donate'))
        self.version_lbl.config(text=_t(self.lang, 'lbl_version', self.version))
        self.update_status(_t(self.lang, 'status_ready'))

    # ── Donación ──────────────────────────────────────────────────────────────

    def _open_donate(self) -> None:
        """Abre la página de donación PayPal en el navegador por defecto."""
        webbrowser.open(DONATE_URL)

    # ── Configuración ─────────────────────────────────────────────────────────

    def _toggle_auto_start(self) -> None:
        """Actualiza la configuración de auto-inicio desde el checkbox."""
        self.config_mgr['auto_start'] = self.auto_start_var.get()

    def _toggle_auto_close(self) -> None:
        """Actualiza la configuración de auto-cierre desde el checkbox."""
        self.config_mgr['auto_close_enabled'] = self.auto_close_var.get()

    def _change_auto_close_seconds(self) -> None:
        """Actualiza los segundos de auto-cierre desde el spinbox."""
        try:
            self.config_mgr['auto_close_seconds'] = int(self.auto_close_sb.get())
        except ValueError:
            pass  # Ignorar si el campo no es un número válido

    def _select_pdf_folder(self) -> None:
        """Abre diálogo para seleccionar la carpeta de destino de los PDF."""
        folder = filedialog.askdirectory()
        if folder:
            self.pdf_folder_var.set(folder)
            self.config_mgr['pdf_folder'] = folder
            self.update_status(_t(self.lang, 'status_pdf_folder', folder))

    def _on_close(self) -> None:
        """Cierra la aplicación de forma ordenada."""
        self.destroy()

    def update_status(self, message: str) -> None:
        """Actualiza el texto de la barra de estado.

        Args:
            message: Texto a mostrar en la barra inferior.
        """
        self.status_bar.config(text=message)

    def log(self, message: str) -> None:
        """Escribe un mensaje en el área de log, barra de estado y logger.

        THREAD SAFETY: llamar siempre via self.after(0, self.log, msg)
        desde hilos de fondo para que Tkinter lo procese en el hilo principal.

        Args:
            message: Mensaje a registrar.
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line  = f"[{timestamp}] {message}"
        self.log_area.insert(tk.END, log_line + '\n')
        self.log_area.see(tk.END)
        self.update_status(message)
        self.logger.info(message)

    def save_config(self) -> None:
        """Sincroniza los valores de la GUI a config_mgr y guarda en disco."""
        self.config_mgr['pdf_folder'] = self.pdf_folder_var.get()
        self.config_mgr['language']   = self.lang
        try:
            self.config_mgr['auto_close_seconds'] = int(self.auto_close_sb.get())
        except ValueError:
            pass
        self.config_mgr.save()
        self.update_status(_t(self.lang, 'status_config_saved'))
        self.logger.info("Configuración guardada")

    # ── Escaneo ───────────────────────────────────────────────────────────────

    def start_scan(self) -> None:
        """Inicia el escaneo en un hilo daemon de fondo.

        Desactiva el botón de escaneo para evitar ejecuciones concurrentes
        y limpia el área de log antes de comenzar.
        """
        if self.scan_btn.cget('state') != tk.NORMAL:
            return  # Ya hay un escaneo en curso

        self.scan_btn.config(state=tk.DISABLED)
        self.log_area.delete(1.0, tk.END)
        self.findings.clear()
        self.log(_t(self.lang, 'status_scan_start', self.os_name))
        self.progress.start(10)

        threading.Thread(target=self._run_scan, daemon=True).start()

    def _run_scan(self) -> None:
        """Ejecuta todos los escaneos en el hilo de fondo.

        THREAD SAFETY: Todas las actualizaciones de widgets se delegan
        al hilo principal via self.after(0, …).
        """
        try:
            # Detectar paquetes instalados
            packages = self.scanner.get_installed_packages(self.os_name)
            self.after(0, self.log, _t(self.lang, 'status_packages', len(packages)))

            # Ejecutar los tres escaneos (CVE, configs, contraseñas)
            findings_raw = self.scanner.run_full_scan(self.os_name)

            for raw_finding in findings_raw:
                finding, solution = interpret_finding(raw_finding)
                self.findings.append({'raw': finding, 'simple': solution})
                self.after(0, self.log, finding)

            self.after(
                0, self.log,
                _t(self.lang, 'status_scan_done', len(self.findings))
            )

            # Auto-exportar si hay carpeta configurada y reportlab disponible
            pdf_folder = self.config_mgr.get('pdf_folder', '')
            if pdf_folder and self.pdf_generator:
                self.after(0, self._save_pdf_report, pdf_folder)
                self.after(0, self._schedule_auto_close)
            else:
                self.after(0, self._scan_finished)

        except Exception as e:
            self.after(0, self.log, _t(self.lang, 'status_scan_error', str(e)))
            self.logger.error(f"Error de escaneo: {e}")
            self.after(0, self._scan_finished)

    def _scan_finished(self) -> None:
        """Restaura la UI al estado 'listo' tras el escaneo."""
        self.progress.stop()
        self.scan_btn.config(state=tk.NORMAL)
        self.export_btn.config(state=tk.NORMAL)

    def _save_pdf_report(self, folder: str, output_path: str = None) -> None:
        """Guarda el reporte PDF en el path indicado o genera uno automático.

        Args:
            folder:      Carpeta de destino (usada si output_path es None).
            output_path: Ruta completa del archivo; si se provee, se usa tal cual.
        """
        if not self.pdf_generator:
            return

        if output_path is None:
            # Generar nombre automático con hostname y timestamp
            hostname  = socket.gethostname()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename  = f"Reporte_vulnerabilidades_{hostname}_{timestamp}.pdf"
            output_path = os.path.join(folder, filename)

        try:
            self.pdf_generator.generate_report(
                self.findings,
                output_path,
                hostname=socket.gethostname()
            )
            self.log(_t(self.lang, 'status_pdf_saved', output_path))
        except Exception as e:
            self.log(_t(self.lang, 'status_pdf_error', str(e)))
            self.logger.error(f"Error generando PDF: {e}")
        finally:
            self._scan_finished()

    def export_report(self) -> None:
        """Exporta el reporte PDF con un diálogo de guardado manual.

        Usa exactamente el path que el usuario selecciona en el diálogo;
        no regenera el nombre del archivo.
        """
        if not self.pdf_generator:
            self.update_status(_t(self.lang, 'status_no_reportlab'))
            return

        if not self.findings:
            self.update_status(_t(self.lang, 'status_no_results'))
            return

        default_filename = (
            f"Reporte_vulnerabilidades_{socket.gethostname()}"
            f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )

        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=default_filename,
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )

        if filepath:
            try:
                # Usar el filepath completo elegido por el usuario
                self.pdf_generator.generate_report(
                    self.findings,
                    filepath,
                    hostname=socket.gethostname()
                )
                self.update_status(_t(self.lang, 'status_pdf_exported', filepath))
                self._schedule_auto_close()
            except Exception as e:
                self.update_status(_t(self.lang, 'status_export_error', str(e)))
                self.logger.error(f"Error exportando PDF: {e}")

    # ── Auto-cierre ───────────────────────────────────────────────────────────

    def _schedule_auto_close(self) -> None:
        """Programa el cierre automático de la ventana si está configurado."""
        if self.config_mgr.get('auto_close_enabled', False):
            self.remaining_seconds = self.config_mgr.get('auto_close_seconds', 60)
            self._countdown()

    def _countdown(self) -> None:
        """Cuenta regresiva hasta el auto-cierre de la ventana."""
        if self.remaining_seconds > 0:
            self.update_status(
                _t(self.lang, 'status_countdown', self.remaining_seconds)
            )
            self.remaining_seconds -= 1
            self.after(1000, self._countdown)
        else:
            self._on_close()
