"""Helper functions for Vulnerability Scanner."""

import platform
import socket
from typing import Tuple


def detect_os() -> str:
    """Detect the operating system.
    
    Returns:
        Operating system name (Windows, Linux, Darwin, etc.).
    """
    return platform.system()


def get_hostname() -> str:
    """Get system hostname.
    
    Returns:
        Hostname of the system.
    """
    try:
        return socket.gethostname()
    except Exception:
        return "Unknown"


def interpret_finding(raw: str) -> Tuple[str, str]:
    """Interpret and provide solutions for security findings.
    
    Args:
        raw: Raw finding string from scanner.
        
    Returns:
        Tuple of (finding, solution).
    """
    if raw.startswith("[ERROR]"):
        comp = raw.replace("[ERROR] ", "")
        sol = f"No se pudo verificar '{comp}'. Revisa tu conexión y configuración de API."
        return raw, sol

    if raw.startswith("[CVE] Paquete"):
        parts = raw.split()
        count = parts[-3] if len(parts) > 3 else "?"
        pkg = parts[2] if len(parts) > 2 else "?"
        sol = f"Actualiza '{pkg}' a la última versión disponible para corregir {count} vulnerabilidades."
        return raw, sol

    if "/etc/passwd" in raw:
        sol = "Ejecuta 'chmod 644 /etc/passwd' para establecer permisos seguros."
        return raw, sol

    if "Servicio SSH corriendo" in raw:
        sol = "Revisa '/etc/ssh/sshd_config'. Considera usar claves SSH en lugar de contraseñas."
        return raw, sol

    if "RemoteRegistry activo" in raw:
        sol = "Deshabilita 'RemoteRegistry' en 'services.msc' si no es necesario."
        return raw, sol

    if "Permisos en System32" in raw:
        sol = "Verifica manualmente los permisos de 'C:\\Windows\\System32'."
        return raw, sol

    if raw.startswith("Usuario") and "sin contraseña" in raw:
        user = raw.split()[1] if len(raw.split()) > 1 else "unknown"
        sol = f"Asigna una contraseña segura al usuario '{user}'."
        return raw, sol

    return raw, "Investiga este hallazgo en documentación oficial y aplica medidas recomendadas."
