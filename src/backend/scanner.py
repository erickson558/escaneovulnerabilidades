"""Vulnerability scanner module for system security analysis.

This module provides functionality to scan for software vulnerabilities,
insecure configurations, and weak passwords across different operating systems.
"""

import subprocess
import os
from typing import List, Tuple, Optional
from datetime import datetime


class VulnerabilityScanner:
    """Scanner for system vulnerabilities and security issues."""

    # Platform-specific flags
    FLAGS_NO_WINDOW = (
        subprocess.CREATE_NO_WINDOW 
        if hasattr(subprocess, 'CREATE_NO_WINDOW') 
        else 0
    )

    def __init__(self, nvd_api_key: str = "", timeout: int = 5):
        """Initialize vulnerability scanner.
        
        Args:
            nvd_api_key: NVD API key for CVE lookups (optional).
            timeout: Request timeout in seconds.
        """
        self.nvd_api_key = nvd_api_key
        self.timeout = timeout
        self.nvd_api_url = "https://services.nvd.nist.gov/rest/json/cves/1.0"

    def scan_software_vulnerabilities(
        self, 
        packages: List[Tuple[str, str]]
    ) -> List[str]:
        """Scan installed packages for known vulnerabilities via NVD.
        
        Args:
            packages: List of (name, version) tuples.
            
        Returns:
            List of vulnerability findings.
        """
        findings = []
        
        if not self.nvd_api_key:
            return findings

        try:
            import requests
        except ImportError:
            return ["[ERROR] requests library not installed"]

        headers = {"apiKey": self.nvd_api_key}

        for name, version in packages:
            try:
                response = requests.get(
                    self.nvd_api_url,
                    params={"keyword": f"{name} {version}"},
                    headers=headers,
                    timeout=self.timeout
                )
                total = response.json().get("totalResults", 0)
                
                if total > 0:
                    findings.append(
                        f"[CVE] Paquete {name} {version}: {total} vulnerabilidades"
                    )
            except requests.RequestException:
                findings.append(f"[ERROR] {name} {version}")
            except Exception:
                findings.append(f"[ERROR] {name} {version}")

        return findings

    def scan_insecure_configurations(self, os_name: str) -> List[str]:
        """Scan for insecure system configurations.
        
        Args:
            os_name: Operating system name (Linux, Darwin, Windows, etc.).
            
        Returns:
            List of configuration issues found.
        """
        findings = []

        if os_name in ('Linux', 'Darwin'):
            findings.extend(self._scan_unix_configs())
        else:
            findings.extend(self._scan_windows_configs())

        return findings

    def _scan_unix_configs(self) -> List[str]:
        """Scan Unix/Linux system configurations.
        
        Returns:
            List of Unix-specific security findings.
        """
        findings = []

        # Check /etc/passwd permissions
        try:
            st = os.stat('/etc/passwd')
            perms = oct(st.st_mode & 0o777)
            if perms not in ('0o644', '0o600'):
                findings.append(f"Permisos inseguros en /etc/passwd: {perms}")
        except Exception:
            pass

        # Check SSH service
        try:
            output = subprocess.check_output(['ps', 'aux'], text=True)
            if 'sshd' in output:
                findings.append("Servicio SSH corriendo")
        except Exception:
            pass

        return findings

    def _scan_windows_configs(self) -> List[str]:
        """Scan Windows system configurations.
        
        Returns:
            List of Windows-specific security findings.
        """
        findings = []

        # Check RemoteRegistry service
        try:
            output = subprocess.check_output(
                ['sc', 'query', 'RemoteRegistry'],
                text=True,
                creationflags=self.FLAGS_NO_WINDOW
            )
            if 'RUNNING' in output:
                findings.append("RemoteRegistry activo")
        except Exception:
            pass

        # Check System32 permissions
        try:
            subprocess.check_output(
                ['icacls', r'C:\Windows\System32'],
                text=True,
                creationflags=self.FLAGS_NO_WINDOW
            )
            findings.append("Permisos en System32 revisados")
        except Exception:
            pass

        return findings

    def scan_weak_passwords(self, os_name: str) -> List[str]:
        """Scan for accounts with weak or missing passwords.
        
        Args:
            os_name: Operating system name.
            
        Returns:
            List of accounts with weak password issues.
        """
        findings = []

        if os_name in ('Linux', 'Darwin'):
            try:
                with open('/etc/shadow', 'r') as f:
                    for line in f:
                        try:
                            user, password_field = line.split(':')[:2]
                            if password_field in ('', '!', '*'):
                                findings.append(f"Usuario {user} sin contraseña")
                        except ValueError:
                            continue
            except PermissionError:
                findings.append("[ERROR] Permisos insuficientes para leer /etc/shadow")
            except Exception:
                pass

        return findings

    def get_installed_packages(self, os_name: str) -> List[Tuple[str, str]]:
        """Get list of installed packages for the system.
        
        Args:
            os_name: Operating system name.
            
        Returns:
            List of (package_name, version) tuples.
        """
        packages = []

        try:
            if os_name == 'Linux':
                packages = self._get_linux_packages()
            elif os_name == 'Darwin':
                packages = self._get_macos_packages()
            else:
                packages = self._get_windows_packages()
        except Exception:
            pass

        return packages

    def _get_linux_packages(self) -> List[Tuple[str, str]]:
        """Get installed packages on Linux.
        
        Returns:
            List of Linux packages.
        """
        try:
            output = subprocess.check_output(
                ['dpkg-query', '-W', '-f=${binary:Package} ${Version}\n'],
                text=True
            )
            packages = [
                tuple(line.split()[:2]) 
                for line in output.splitlines() 
                if line.strip()
            ]
            return packages
        except Exception:
            return []

    def _get_macos_packages(self) -> List[Tuple[str, str]]:
        """Get installed packages on macOS.
        
        Returns:
            List of macOS packages.
        """
        try:
            output = subprocess.check_output(
                ['brew', 'list', '--versions'],
                text=True
            )
            packages = [
                (line.split()[0], line.split()[1])
                for line in output.splitlines()
                if line.strip()
            ]
            return packages
        except Exception:
            return []

    def _get_windows_packages(self) -> List[Tuple[str, str]]:
        """Get installed packages on Windows.
        
        Returns:
            List of Windows packages.
        """
        try:
            output = subprocess.check_output(
                ['wmic', 'product', 'get', 'Name,Version'],
                text=True,
                creationflags=self.FLAGS_NO_WINDOW
            )
            packages = []
            for line in output.splitlines()[1:]:
                cols = line.strip().split()
                if len(cols) >= 2:
                    name = ' '.join(cols[:-1])
                    version = cols[-1]
                    packages.append((name, version))
            return packages
        except Exception:
            return []

    def run_full_scan(self, os_name: str) -> List[str]:
        """Run all security scans.
        
        Args:
            os_name: Operating system name.
            
        Returns:
            List of all findings from all scan types.
        """
        findings = []

        # Get packages and scan vulnerabilities
        packages = self.get_installed_packages(os_name)
        findings.extend(self.scan_software_vulnerabilities(packages))

        # Scan configurations and weak passwords
        findings.extend(self.scan_insecure_configurations(os_name))
        findings.extend(self.scan_weak_passwords(os_name))

        return findings
