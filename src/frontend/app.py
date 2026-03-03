"""GUI application for Vulnerability Scanner.

Provides a tkinter-based graphical user interface for system vulnerability scanning.
"""

import tkinter as tk
from tkinter import scrolledtext, ttk, filedialog
import threading
from datetime import datetime
from typing import List, Tuple
import socket
import os

from src import __version__
from src.config import ConfigManager
from src.logger import LoggerManager
from src.backend.scanner import VulnerabilityScanner
from src.backend.pdf_generator import PDFReportGenerator
from src.utils.helpers import detect_os, interpret_finding


class VulnerabilityScannerApp(tk.Tk):
    """Main GUI application for vulnerability scanning."""

    def __init__(self, version: str = __version__):
        """Initialize the application.
        
        Args:
            version: Application version string.
        """
        super().__init__()

        self.version = version
        self.config_mgr = ConfigManager()
        self.logger_mgr = LoggerManager()
        self.logger = self.logger_mgr.get_logger()

        self.os_name = detect_os()
        self.scanner = VulnerabilityScanner(
            nvd_api_key=self.config_mgr.get('NVD_API_KEY', '')
        )

        try:
            self.pdf_generator = PDFReportGenerator(version=version)
        except ImportError:
            self.pdf_generator = None
            self.logger.warning("reportlab not installed - PDF export disabled")

        self.findings: List[dict] = []
        self._setup_ui()
        self._setup_bindings()

        # Auto-start if configured
        if self.config_mgr.get('auto_start', False):
            self.after(1000, self.start_scan)

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        # Window title and size
        self.title(f"Vulnerability Scanner - v{self.version}")
        width = self.config_mgr['window']['width']
        height = self.config_mgr['window']['height']
        self.geometry(f"{width}x{height}")

        # Log area
        self.log_area = scrolledtext.ScrolledText(
            self,
            wrap=tk.WORD,
            font=("Courier", 9)
        )
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Progress bar
        self.progress = ttk.Progressbar(
            self,
            orient='horizontal',
            mode='indeterminate'
        )
        self.progress.pack(fill=tk.X, padx=10, pady=5)

        # Control buttons frame
        self._setup_control_buttons()

        # PDF folder selection
        self._setup_pdf_folder_frame()

        # Status bar
        self.status_bar = tk.Label(
            self,
            text="Listo",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Version label
        tk.Label(
            self,
            text=f"Versión: {self.version}",
            font=("Courier", 8)
        ).pack(anchor=tk.E, padx=10, pady=(0, 5))

    def _setup_control_buttons(self) -> None:
        """Set up control button frame."""
        ctrl = tk.Frame(self)
        ctrl.pack(fill=tk.X, pady=5, padx=5)

        # Scan button
        self.scan_btn = tk.Button(
            ctrl,
            text="Iniciar Escaneo",
            underline=8,
            command=self.start_scan
        )
        self.scan_btn.pack(side=tk.LEFT, padx=5)

        # Export button
        self.export_btn = tk.Button(
            ctrl,
            text="Exportar PDF",
            underline=9,
            command=self.export_report,
            state=tk.DISABLED
        )
        self.export_btn.pack(side=tk.LEFT, padx=5)

        # Settings button
        btn_settings = tk.Button(
            ctrl,
            text="Guardar Configuración",
            underline=0,
            command=self.save_config
        )
        btn_settings.pack(side=tk.LEFT, padx=5)

        # Exit button
        btn_exit = tk.Button(
            ctrl,
            text="Salir",
            underline=0,
            command=self.destroy
        )
        btn_exit.pack(side=tk.LEFT, padx=5)

        # Auto-start checkbox
        self.auto_start_var = tk.BooleanVar(
            value=self.config_mgr.get('auto_start', False)
        )
        tk.Checkbutton(
            ctrl,
            text="Auto-Iniciar",
            variable=self.auto_start_var,
            command=self._toggle_auto_start
        ).pack(side=tk.LEFT, padx=5)

        # Auto-close checkbox
        self.auto_close_var = tk.BooleanVar(
            value=self.config_mgr.get('auto_close_enabled', False)
        )
        tk.Checkbutton(
            ctrl,
            text="Auto-Cerrar",
            variable=self.auto_close_var,
            command=self._toggle_auto_close
        ).pack(side=tk.LEFT, padx=5)

        # Auto-close seconds spinbox
        self.auto_close_seconds_var = tk.IntVar(
            value=self.config_mgr.get('auto_close_seconds', 60)
        )
        self.auto_close_sb = tk.Spinbox(
            ctrl,
            from_=10,
            to=3600,
            increment=10,
            textvariable=self.auto_close_seconds_var,
            width=5,
            command=self._change_auto_close_seconds
        )
        self.auto_close_sb.pack(side=tk.LEFT, padx=2)
        tk.Label(ctrl, text="seg.").pack(side=tk.LEFT)

    def _setup_pdf_folder_frame(self) -> None:
        """Set up PDF folder selection frame."""
        pdf_frame = tk.Frame(self)
        pdf_frame.pack(fill=tk.X, pady=5, padx=5)

        tk.Label(pdf_frame, text="Carpeta PDF:").pack(side=tk.LEFT, padx=5)

        self.pdf_folder_var = tk.StringVar(
            value=self.config_mgr.get('pdf_folder', '')
        )
        tk.Entry(
            pdf_frame,
            textvariable=self.pdf_folder_var,
            width=50
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            pdf_frame,
            text="Seleccionar...",
            command=self._select_pdf_folder
        ).pack(side=tk.LEFT, padx=5)

    def _setup_bindings(self) -> None:
        """Set up keyboard shortcuts."""
        self.bind_all("<Alt-e>", lambda e: self.start_scan())
        self.bind_all("<Alt-p>", lambda e: self.export_report())
        self.bind_all("<Alt-g>", lambda e: self.save_config())
        self.bind_all("<Alt-s>", lambda e: self.destroy())

    def _toggle_auto_start(self) -> None:
        """Toggle auto-start setting."""
        self.config_mgr['auto_start'] = self.auto_start_var.get()

    def _toggle_auto_close(self) -> None:
        """Toggle auto-close setting."""
        self.config_mgr['auto_close_enabled'] = self.auto_close_var.get()

    def _change_auto_close_seconds(self) -> None:
        """Update auto-close seconds setting."""
        self.config_mgr['auto_close_seconds'] = self.auto_close_seconds_var.get()

    def _select_pdf_folder(self) -> None:
        """Select PDF output folder."""
        folder = filedialog.askdirectory()
        if folder:
            self.pdf_folder_var.set(folder)
            self.config_mgr['pdf_folder'] = folder
            self.update_status(f"Carpeta PDF: {folder}")

    def update_status(self, message: str) -> None:
        """Update status bar message.
        
        Args:
            message: Status message to display.
        """
        self.status_bar.config(text=message)

    def log(self, message: str) -> None:
        """Log message to UI and file.
        
        Args:
            message: Message to log.
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] {message}"

        self.log_area.insert(tk.END, log_line + '\n')
        self.log_area.see(tk.END)
        self.update_status(message)
        self.logger.info(message)

    def save_config(self) -> None:
        """Save configuration to file."""
        self.config_mgr.save()
        self.update_status("Configuración guardada.")
        self.logger.info("Configuration saved")

    def start_scan(self) -> None:
        """Start vulnerability scan."""
        if not self.scan_btn.cget('state') == tk.NORMAL:
            return

        self.scan_btn.config(state=tk.DISABLED)
        self.log_area.delete(1.0, tk.END)
        self.findings.clear()

        self.log(f"Iniciando escaneo en SO: {self.os_name}")
        self.progress.start(10)

        # Run scan in background thread
        thread = threading.Thread(target=self._run_scan, daemon=True)
        thread.start()

    def _run_scan(self) -> None:
        """Execute vulnerability scan (runs in background thread)."""
        try:
            # Get packages and scan
            packages = self.scanner.get_installed_packages(self.os_name)
            self.log(f"{len(packages)} paquetes detectados.")

            # Run all scans
            findings = self.scanner.run_full_scan(self.os_name)

            # Process findings
            for raw_finding in findings:
                finding, solution = interpret_finding(raw_finding)
                self.findings.append({
                    'raw': finding,
                    'simple': solution
                })
                self.log(finding)

            self.log(f"Escaneo completado. {len(self.findings)} problemas encontrados.")

            # Auto-export to PDF if folder configured
            pdf_folder = self.config_mgr.get('pdf_folder', '')
            if pdf_folder and self.pdf_generator:
                self._save_pdf_report(pdf_folder)
                self._schedule_auto_close()

        except Exception as e:
            self.log(f"Error durante escaneo: {str(e)}")
            self.logger.error(f"Scan error: {str(e)}")
        finally:
            self.progress.stop()
            self.scan_btn.config(state=tk.NORMAL)
            self.export_btn.config(state=tk.NORMAL)

    def _save_pdf_report(self, folder: str) -> None:
        """Save PDF report to specified folder.
        
        Args:
            folder: Path to output folder.
        """
        if not self.pdf_generator:
            return

        try:
            hostname = socket.gethostname()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"Reporte_vulnerabilidades_{hostname}_{timestamp}.pdf"
            filepath = os.path.join(folder, filename)

            self.pdf_generator.generate_report(
                self.findings,
                filepath,
                hostname=hostname
            )
            self.log(f"PDF guardado: {filepath}")
        except Exception as e:
            self.log(f"Error al generar PDF: {str(e)}")
            self.logger.error(f"PDF generation error: {str(e)}")

    def export_report(self) -> None:
        """Export scan results to PDF file."""
        if not self.pdf_generator:
            self.update_status("Exportación no disponible (reportlab no instalado)")
            return

        if not self.findings:
            self.update_status("No hay resultados para exportar")
            return

        default_filename = (
            f"Reporte_vulnerabilidades_"
            f"{socket.gethostname()}_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )

        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=default_filename,
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )

        if filepath:
            try:
                self._save_pdf_report(os.path.dirname(filepath))
                self.update_status(f"PDF exportado: {filepath}")
            except Exception as e:
                self.update_status(f"Error al exportar: {str(e)}")
                self.logger.error(f"Export error: {str(e)}")

    def _schedule_auto_close(self) -> None:
        """Schedule automatic window closure if enabled."""
        if self.config_mgr.get('auto_close_enabled', False):
            self.remaining_seconds = self.config_mgr.get('auto_close_seconds', 60)
            self._countdown()

    def _countdown(self) -> None:
        """Count down to auto-close."""
        if self.remaining_seconds > 0:
            self.update_status(
                f"Cierre automático en {self.remaining_seconds} segundos..."
            )
            self.remaining_seconds -= 1
            self.after(1000, self._countdown)
        else:
            self.destroy()
