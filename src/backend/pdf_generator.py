"""PDF report generation module.

Generates professional security scan reports in PDF format.
"""

import socket
from datetime import datetime
from typing import List, Tuple, Union

from src import __version__

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class PDFReportGenerator:
    """Generate professional PDF security reports."""

    def __init__(self, version: str = __version__):
        """Initialize PDF report generator.
        
        Args:
            version: Application version for footer.
            
        Raises:
            ImportError: If reportlab is not installed.
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError(
                "reportlab is required. Install with: pip install reportlab"
            )
        self.version = version

    def generate_report(
        self,
        findings: List[Union[str, Tuple[str, str], dict]],
        output_path: str,
        hostname: str = None
    ) -> None:
        """Generate PDF report from findings.
        
        Args:
            findings: List of security findings (strings or tuples).
            output_path: Path where PDF will be saved.
            hostname: System hostname for report header (auto-detected if None).
            
        Raises:
            Exception: If PDF generation fails.
        """
        if hostname is None:
            try:
                hostname = socket.gethostname()
            except Exception:
                hostname = "Unknown"

        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=14,
            alignment=1,
            spaceAfter=12,
            textColor='#003366'
        )

        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=6,
            textColor='#0066CC'
        )

        finding_style = ParagraphStyle(
            'Finding',
            parent=styles['BodyText'],
            fontSize=10,
            textColor='#990000',
            spaceAfter=6,
            leading=14
        )

        solution_style = ParagraphStyle(
            'Solution',
            parent=styles['BodyText'],
            fontSize=10,
            textColor='#006600',
            leftIndent=20,
            spaceAfter=12,
            leading=14,
            backColor='#F0FFF0'
        )

        # Build content
        content = []

        content.append(Paragraph("<b>Reporte de Seguridad</b>", title_style))
        content.append(
            Paragraph(f"Sistema: {hostname}", subtitle_style)
        )
        content.append(
            Paragraph(
                f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                styles['Normal']
            )
        )
        content.append(Spacer(1, 24))

        # Results summary
        if not findings:
            content.append(
                Paragraph(
                    "<b>Resultados:</b> No se encontraron vulnerabilidades.",
                    styles['Normal']
                )
            )
        else:
            content.append(
                Paragraph(
                    f"<b>Resultados:</b> Se encontraron {len(findings)} "
                    "problemas de seguridad:",
                    subtitle_style
                )
            )
            content.append(Spacer(1, 12))

            # Add each finding
            for finding in findings:
                raw, solution = self._extract_finding_parts(finding)

                content.append(
                    Paragraph(f"<b>Problema:</b> {raw}", finding_style)
                )
                content.append(
                    Paragraph(
                        f"<b>Solución recomendada:</b> {solution}",
                        solution_style
                    )
                )
                content.append(Spacer(1, 8))

        # Footer
        content.append(Spacer(1, 24))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            alignment=2
        )
        content.append(
            Paragraph(
                f"Generado por Vulnerability Scanner v{self.version}",
                footer_style
            )
        )

        # Build PDF
        doc.build(content)

    @staticmethod
    def _extract_finding_parts(finding: Union[str, Tuple, dict]) -> Tuple[str, str]:
        """Extract raw finding and solution from various formats.
        
        Args:
            finding: Finding in string, tuple, or dict format.
            
        Returns:
            Tuple of (raw_finding, solution).
        """
        if isinstance(finding, tuple):
            return finding[0], finding[1] if len(finding) > 1 else "N/A"
        elif isinstance(finding, dict):
            return (
                finding.get('raw', ''),
                finding.get('simple', 'No solution provided')
            )
        else:
            return str(finding), "Investigate this finding"
