import platform
import subprocess
import os
import threading
import requests
import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
from tkinter.filedialog import asksaveasfilename, askdirectory
import socket
from datetime import datetime
import json

try:
    from src import __version__ as APP_VERSION
except Exception:
    APP_VERSION = "2.0.3"

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
except ImportError:
    raise ImportError("Necesitas instalar reportlab: pip install reportlab")

VERSION = APP_VERSION

CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "NVD_API_KEY": "",
    "window": {"width": 800, "height": 750},
    "auto_start": False,
    "auto_close_enabled": False,
    "auto_close_seconds": 60,
    "pdf_folder": ""
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, 'r') as f:
            cfg = json.load(f)
    except Exception:
        cfg = DEFAULT_CONFIG.copy()
    for k, v in DEFAULT_CONFIG.items():
        cfg.setdefault(k, v)
    for k, v in DEFAULT_CONFIG['window'].items():
        cfg.setdefault('window', {}).setdefault(k, v)
    return cfg

def save_config(cfg):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(cfg, f, indent=4)

global_config = load_config()
NVD_API_KEY = global_config.get('NVD_API_KEY', '')
NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/1.0"
FLAGS_NO_WINDOW = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0

def detect_os():
    return platform.system()

def interpret_finding(raw):
    if raw.startswith("[ERROR]"):
        comp = raw.replace("[ERROR] ", "")
        sol = f"No se pudo verificar '{comp}'. Revisa tu conexión y configuración de API."
        return raw, sol
    if raw.startswith("[CVE] Paquete"):
        parts = raw.split()
        count = parts[-3]
        pkg = parts[2]
        sol = f"Actualiza '{pkg}' a la última versión disponible para corregir {count} vulnerabilidades conocidas."
        return raw, sol
    if "/etc/passwd" in raw:
        sol = "Ejecuta 'chmod 644 /etc/passwd' para establecer permisos seguros en este archivo crítico."
        return raw, sol
    if "Servicio SSH corriendo" in raw:
        sol = "Revisa '/etc/ssh/sshd_config' y deshabilita servicios no necesarios. Considera usar claves SSH en lugar de contraseñas."
        return raw, sol
    if "RemoteRegistry activo" in raw:
        sol = "Deshabilita 'RemoteRegistry' en 'services.msc' si no es necesario para evitar accesos remotos no autorizados."
        return raw, sol
    if "Permisos en System32 revisados" in raw:
        sol = "Verifica manualmente los permisos de 'C:\\Windows\\System32' para asegurarte que solo usuarios autorizados tengan acceso."
        return raw, sol
    if raw.startswith("Usuario") and "sin contraseña" in raw:
        user = raw.split()[1]
        sol = f"Asigna una contraseña segura al usuario '{user}' usando 'passwd {user}' o deshabilita la cuenta si no es necesaria."
        return raw, sol
    return raw, "Investiga este hallazgo en la documentación oficial y aplica las medidas de seguridad recomendadas."

def generate_pdf(findings, filename):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=14, alignment=1, spaceAfter=12, textColor='#003366')
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Heading2'], fontSize=12, spaceAfter=6, textColor='#0066CC')
    finding_style = ParagraphStyle('Finding', parent=styles['BodyText'], fontSize=10, textColor='#990000', spaceAfter=6, leading=14)
    solution_style = ParagraphStyle('Solution', parent=styles['BodyText'], fontSize=10, textColor='#006600', leftIndent=20, spaceAfter=12, leading=14, backColor='#F0FFF0')
    normal_style = styles['Normal']
    content = []
    content.append(Paragraph(f"<b>Reporte de Seguridad</b>", title_style))
    content.append(Paragraph(f"Sistema: {socket.gethostname()}", subtitle_style))
    content.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", normal_style))
    content.append(Spacer(1, 24))
    if not findings:
        content.append(Paragraph("<b>Resultados:</b> No se encontraron vulnerabilidades.", normal_style))
    else:
        content.append(Paragraph(f"<b>Resultados:</b> Se encontraron {len(findings)} problemas de seguridad:", subtitle_style))
        content.append(Spacer(1, 12))
        for item in findings:
            raw, sol = item if isinstance(item, tuple) else (item.get('raw', ''), item.get('simple', 'Solución no especificada'))
            content.append(Paragraph(f"<b>Problema:</b> {raw}", finding_style))
            content.append(Paragraph(f"<b>Solución recomendada:</b> {sol}", solution_style))
            content.append(Spacer(1, 8))
    content.append(Spacer(1, 24))
    content.append(Paragraph(f"Generado por Vulnerability Scanner v{VERSION}", ParagraphStyle('Footer', parent=normal_style, fontSize=8, alignment=2)))
    doc.build(content)

def scan_software_vulns(packages):
    findings = []
    headers = {"apiKey": NVD_API_KEY} if NVD_API_KEY else {}
    for name, ver in packages:
        try:
            resp = requests.get(NVD_API_URL, params={"keyword": f"{name} {ver}"}, headers=headers, timeout=5)
            total = resp.json().get("totalResults", 0)
            if total > 0:
                findings.append(f"[CVE] Paquete {name} {ver}: {total} vulnerabilidades detectadas")
        except Exception:
            findings.append(f"[ERROR] {name} {ver}")
    return findings

def scan_insecure_configs(os_name):
    findings = []
    if os_name in ('Linux', 'Darwin'):
        try:
            st = os.stat('/etc/passwd')
            perms = oct(st.st_mode & 0o777)
            if perms not in ('0o644', '0o600'):
                findings.append(f"Permisos inseguros en /etc/passwd: {perms}")
        except Exception:
            pass
        try:
            out = subprocess.check_output(['ps', 'aux'], text=True)
            if 'sshd' in out:
                findings.append("Servicio SSH corriendo")
        except Exception:
            pass
    else:
        try:
            out = subprocess.check_output(['sc', 'query', 'RemoteRegistry'], text=True, creationflags=FLAGS_NO_WINDOW)
            if 'RUNNING' in out:
                findings.append("RemoteRegistry activo")
        except Exception:
            pass
        try:
            subprocess.check_output(['icacls', r'C:\Windows\System32'], text=True, creationflags=FLAGS_NO_WINDOW)
            findings.append("Permisos en System32 revisados")
        except Exception:
            pass
    return findings

def scan_weak_passwords(os_name):
    findings = []
    if os_name in ('Linux', 'Darwin'):
        try:
            with open('/etc/shadow') as f:
                for line in f:
                    user, pw = line.split(':')[:2]
                    if pw in ('', '!', '*'):
                        findings.append(f"Usuario {user} sin contraseña")
        except Exception:
            pass
    return findings

def get_installed_packages(os_name):
    pkgs = []
    try:
        if os_name == 'Linux':
            out = subprocess.check_output(['dpkg-query', '-W', '-f=${binary:Package} ${Version}\n'], text=True)
            pkgs = [tuple(line.split()[:2]) for line in out.splitlines()]
        elif os_name == 'Darwin':
            out = subprocess.check_output(['brew', 'list', '--versions'], text=True)
            pkgs = [(line.split()[0], line.split()[1]) for line in out.splitlines()]
        else:
            out = subprocess.check_output(['wmic', 'product', 'get', 'Name,Version'], text=True, creationflags=FLAGS_NO_WINDOW)
            for line in out.splitlines()[1:]:
                cols = line.strip().split()
                if len(cols) >= 2:
                    name = ' '.join(cols[:-1])
                    ver = cols[-1]
                    pkgs.append((name, ver))
    except Exception:
        pass
    return pkgs

def console_mode():
    osn = detect_os()
    print(f"Sistema operativo: {osn}")
    pkgs = get_installed_packages(osn)
    print(f"{len(pkgs)} paquetes detectados.")
    raw_list = scan_software_vulns(pkgs) + scan_insecure_configs(osn) + scan_weak_passwords(osn)
    findings = [interpret_finding(r) for r in raw_list]
    for raw, sol in findings:
        print(f"- {raw}\n  Solución: {sol}\n")
    if input('¿Exportar PDF? (s/n): ').lower() == 's':
        default = f"Reporte_vulnerabilidades_{socket.gethostname()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        path = input(f"Ruta [{default}]: ") or default
        generate_pdf(findings, path)
        print(f"PDF guardado en: {path}")

class VulnerabilityScannerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.conf = global_config
        self.title(f"Vulnerability Scanner - v{VERSION}")
        w, h = self.conf['window']['width'], self.conf['window']['height']
        self.geometry(f"{w}x{h}")
        self.os_name = detect_os()
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = open(f"log_{ts}.txt", 'w')
        self.findings = []

        self.log_area = scrolledtext.ScrolledText(self, wrap=tk.WORD)
        self.log_area.pack(fill=tk.BOTH, expand=True)
        self.progress = ttk.Progressbar(self, orient='horizontal', mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=10, pady=5)

        ctrl = tk.Frame(self)
        ctrl.pack(fill=tk.X, pady=5)

        self.scan_btn = tk.Button(ctrl, text="Iniciar Escaneo", underline=8, command=self.start_scan)
        self.scan_btn.pack(side=tk.LEFT, padx=5)
        self.bind_all("<Alt-e>", lambda e: self.start_scan())

        self.export_btn = tk.Button(ctrl, text="Exportar PDF", underline=9, command=self.export_report, state=tk.DISABLED)
        self.export_btn.pack(side=tk.LEFT, padx=5)
        self.bind_all("<Alt-p>", lambda e: self.export_report())

        btn_save = tk.Button(ctrl, text="Guardar Configuración", underline=0, command=self.on_save_config)
        btn_save.pack(side=tk.LEFT, padx=5)
        self.bind_all("<Alt-g>", lambda e: self.on_save_config())

        btn_exit = tk.Button(ctrl, text="Salir", underline=0, command=self.destroy)
        btn_exit.pack(side=tk.LEFT, padx=5)
        self.bind_all("<Alt-s>", lambda e: self.destroy())

        self.auto_start_var = tk.BooleanVar(value=self.conf['auto_start'])
        tk.Checkbutton(ctrl, text="Auto-Iniciar", variable=self.auto_start_var, command=self.toggle_auto_start).pack(side=tk.LEFT, padx=5)

        self.auto_close_var = tk.BooleanVar(value=self.conf['auto_close_enabled'])
        tk.Checkbutton(ctrl, text="Auto-Cerrar", variable=self.auto_close_var, command=self.toggle_auto_close).pack(side=tk.LEFT, padx=5)

        self.auto_close_sb = tk.Spinbox(ctrl, from_=10, to=3600, increment=10,
                                        textvariable=tk.IntVar(value=self.conf['auto_close_seconds']), width=5,
                                        command=self.change_auto_close_seconds)
        self.auto_close_sb.pack(side=tk.LEFT, padx=2)
        tk.Label(ctrl, text="segundos").pack(side=tk.LEFT)

        pdf_frame = tk.Frame(self)
        pdf_frame.pack(fill=tk.X, pady=5)
        tk.Label(pdf_frame, text="Carpeta PDF:").pack(side=tk.LEFT, padx=5)
        self.pdf_folder_var = tk.StringVar(value=self.conf.get('pdf_folder', ''))
        tk.Entry(pdf_frame, textvariable=self.pdf_folder_var, width=50).pack(side=tk.LEFT, padx=5)
        tk.Button(pdf_frame, text="Seleccionar...", command=self.select_pdf_folder).pack(side=tk.LEFT, padx=5)

        self.status_bar = tk.Label(self, text="Listo", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        tk.Label(self, text=f"Versión: {VERSION}").pack(anchor=tk.E, padx=10, pady=(0, 5))

        if self.conf['auto_start']:
            self.after(1000, self.start_scan)

    def schedule_auto_close(self):
        if self.conf['auto_close_enabled']:
            self.remaining = self.conf['auto_close_seconds']
            self.countdown()

    def countdown(self):
        if self.remaining > 0:
            self.update_status(f"Cierre en {self.remaining} segundos...")
            self.remaining -= 1
            self.after(1000, self.countdown)
        else:
            self.destroy()

    def update_status(self, text):
        self.status_bar.config(text=text)

    def on_save_config(self):
        save_config(self.conf)
        self.update_status("Configuración guardada.")

    def log(self, msg):
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        line = f"[{ts}] {msg}"
        self.log_area.insert(tk.END, line + '\n')
        self.log_area.see(tk.END)
        self.log_file.write(line + '\n')
        self.log_file.flush()
        self.update_status(msg)

    def toggle_auto_start(self):
        self.conf['auto_start'] = self.auto_start_var.get()

    def toggle_auto_close(self):
        self.conf['auto_close_enabled'] = self.auto_close_var.get()

    def change_auto_close_seconds(self):
        self.conf['auto_close_seconds'] = int(self.auto_close_sb.get())

    def select_pdf_folder(self):
        folder = askdirectory()
        if folder:
            self.pdf_folder_var.set(folder)
            self.conf['pdf_folder'] = folder
            self.update_status(f"Carpeta PDF: {folder}")

    def start_scan(self):
        self.scan_btn.config(state=tk.DISABLED)
        self.log_area.delete(1.0, tk.END)
        self.findings.clear()
        self.log(f"Iniciando escaneo en SO: {self.os_name}")
        self.progress.start(10)
        threading.Thread(target=self.run_scans, daemon=True).start()

    def run_scans(self):
        pkgs = get_installed_packages(self.os_name)
        self.log(f"{len(pkgs)} paquetes detectados.")
        raw_list = scan_software_vulns(pkgs) + scan_insecure_configs(self.os_name) + scan_weak_passwords(self.os_name)
        for r in raw_list:
            raw, sol = interpret_finding(r)
            self.findings.append({'raw': raw, 'simple': sol})
            self.log(raw)
        self.progress.stop()
        self.log("Escaneo completado.")
        self.scan_btn.config(state=tk.NORMAL)
        folder = self.conf.get('pdf_folder')
        if folder:
            filename = f"Reporte_vulnerabilidades_{socket.gethostname()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            path = os.path.join(folder, filename)
            try:
                generate_pdf(self.findings, path)
                self.log(f"PDF guardado: {path}")
                self.schedule_auto_close()
            except Exception as e:
                self.log(f"Error al guardar PDF: {e}")
        self.export_btn.config(state=tk.NORMAL)

    def export_report(self):
        default = f"Reporte_vulnerabilidades_{socket.gethostname()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        path = asksaveasfilename(defaultextension=".pdf", initialfile=default, filetypes=[("PDF files", "*.pdf")])
        if path:
            try:
                generate_pdf(self.findings, path)
                self.update_status(f"PDF guardado: {path}")
                self.schedule_auto_close()
            except Exception as e:
                self.update_status(f"Error al generar PDF: {e}")

if __name__ == '__main__':
    if detect_os() == 'Linux' and not os.environ.get('DISPLAY'):
        console_mode()
    else:
        app = VulnerabilityScannerApp()
        app.mainloop()
