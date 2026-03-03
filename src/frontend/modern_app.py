"""Frontend moderno con PySimpleGUI - UI profesional y responsive."""

import PySimpleGUI as sg
import threading
from datetime import datetime
from typing import Callable, Optional


class ModernVulnerabilityScannerUI:
    """GUI moderna basada en PySimpleGUI."""

    def __init__(
        self,
        title: str,
        version: str,
        on_scan_callback: Callable,
        on_config_change: Callable,
        logger_callback: Optional[Callable] = None,
    ):
        """Inicializar UI moderna.
        
        Args:
            title: Título de la ventana
            version: Versión de la aplicación
            on_scan_callback: Función para iniciar escaneo
            on_config_change: Función para guardar configuración
            logger_callback: Función para registrar eventos
        """
        self.title = title
        self.version = version
        self.on_scan = on_scan_callback
        self.on_config_change = on_config_change
        self.logger = logger_callback or print

        # Configurar tema
        sg.theme('DarkGrey13')
        
        self.window = None
        self.countdown_active = False
        self.countdown_remaining = 0

    def create_layout(self, config: dict) -> list:
        """Crear layout de la interfaz.
        
        Args:
            config: Diccionario de configuración
            
        Returns:
            Layout para PySimpleGUI
        """
        menubar = [
            ['&Archivo', ['&Salir']],
            ['&Herramientas', ['&Preferencias']],
            ['&Ayuda', ['&About']],
        ]

        layout = [
            [sg.Menu(menubar)],
            [
                sg.Text(
                    f'{self.title} v{self.version}',
                    font=('Arial', 14, 'bold'),
                    expand_x=True,
                    text_color='#00AA00'
                )
            ],
            [
                sg.Multiline(
                    size=(80, 20),
                    key='-LOG-',
                    disabled=True,
                    autoscroll=True,
                    background_color='#1a1a1a',
                    text_color='#00FF00',
                    font=('Courier', 9),
                    expand_x=True,
                    expand_y=True,
                )
            ],
            [
                sg.ProgressBar(100, orientation='h', key='-PROGRESS-', expand_x=True)
            ],
            [
                sg.Button('▶ Iniciar Escaneo', key='-SCAN-', size=(15, 1)),
                sg.Button('💾 Exportar PDF', key='-EXPORT-', disabled=True, size=(15, 1)),
                sg.Button('❌ Salir', key='-EXIT-', size=(15, 1)),
                sg.Checkbox(
                    'Auto-Iniciar',
                    default=config.get('auto_start', False),
                    key='-AUTO-START-',
                    tooltip='Iniciar escaneo automáticamente al abrir'
                ),
            ],
            [
                sg.Checkbox(
                    'Auto-Cerrar en',
                    default=config.get('auto_close_enabled', False),
                    key='-AUTO-CLOSE-',
                    tooltip='Cerrar aplicación automáticamente'
                ),
                sg.Spin(
                    (10, 600),
                    initial_value=config.get('auto_close_seconds', 60),
                    key='-AUTO-CLOSE-SECONDS-',
                    size=(5, 1),
                ),
                sg.Text('segundos'),
            ],
            [
                sg.StatusBar(
                    'Listo',
                    key='-STATUS-',
                    size=(80, 1),
                    relief=sg.RELIEF_SUNKEN,
                )
            ],
        ]

        return layout

    def show(self, config: dict) -> Optional[dict]:
        """Mostrar la ventana y manejar eventos.
        
        Args:
            config: Diccionario de configuración
            
        Returns:
            Configuración actualizada o None si se cerró
        """
        self.window = sg.Window(
            self.title,
            self.create_layout(config),
            size=(900, 700),
            location=(100, 100),
            finalize=True,
        )

        # Iniciar escaneo automático si está configurado
        if config.get('auto_start'):
            self.log('Iniciando escaneo automático...')
            threading.Thread(target=self.on_scan, daemon=True).start()

        while True:
            event, values = self.window.read(timeout=100)

            if event == sg.WINDOW_CLOSED or event == '-EXIT-' or event == '&Salir':
                break

            if event == '-SCAN-':
                self._handle_scan_click(values)

            if event == '-EXPORT-':
                self._handle_export_click()

            if event == '&About':
                self._show_about()

            if event == '&Preferencias':
                self._show_preferences(values)

            if event in ('-AUTO-START-', '-AUTO-CLOSE-', '-AUTO-CLOSE-SECONDS-'):
                self._update_config_from_ui(values, config)

            if self.countdown_active:
                self._update_countdown()

            self.window.refresh()

        self.window.close()
        return config

    def log(self, message: str) -> None:
        """Registrar mensaje en la UI.
        
        Args:
            message: Mensaje a registrar
        """
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_msg = f'[{timestamp}] {message}\n'
        
        if self.window:
            current = self.window['-LOG-'].get()
            self.window['-LOG-'].update(current + log_msg)
        
        self.logger(message)

    def set_status(self, message: str) -> None:
        """Actualizar barra de estado.
        
        Args:
            message: Mensaje de estado
        """
        if self.window:
            self.window['-STATUS-'].update(message)

    def set_progress(self, value: int) -> None:
        """Actualizar barra de progreso.
        
        Args:
            value: Valor del progreso (0-100)
        """
        if self.window:
            self.window['-PROGRESS-'].update(value)

    def enable_export(self, enabled: bool = True) -> None:
        """Habilitar/deshabilitar botón de exportar.
        
        Args:
            enabled: True para habilitar, False para deshabilitar
        """
        if self.window:
            self.window['-EXPORT-'].update(disabled=not enabled)

    def _handle_scan_click(self, values: dict) -> None:
        """Manejar clic en botón de escaneo."""
        self.window['-SCAN-'].update(disabled=True)
        self.window['-LOG-'].update('')
        self.set_progress(0)
        self.log('Iniciando escaneo...')
        
        threading.Thread(target=self.on_scan, daemon=True).start()

    def _handle_export_click(self) -> None:
        """Manejar clic en botón de exportar PDF."""
        self.log('Exportando PDF...')

    def _update_config_from_ui(self, values: dict, config: dict) -> None:
        """Actualizar configuración desde UI.
        
        Args:
            values: Valores actuales de la UI
            config: Diccionario de configuración
        """
        config['auto_start'] = values['-AUTO-START-']
        config['auto_close_enabled'] = values['-AUTO-CLOSE-']
        config['auto_close_seconds'] = int(values['-AUTO-CLOSE-SECONDS-'])
        self.on_config_change()
        self.set_status('Configuración guardada automáticamente')

    def _show_about(self) -> None:
        """Mostrar diálogo About."""
        sg.popup(
            f'{self.title} v{self.version}\n\n'
            'Escaner profesional de vulnerabilidades de sistemas\n\n'
            'Creado por: Synyster Rick\n'
            f'© {datetime.now().year} Derechos Reservados\n\n'
            'Licencia: Apache License 2.0',
            title='About',
            font=('Arial', 10),
        )

    def _show_preferences(self, values: dict) -> None:
        """Mostrar diálogo de preferencias."""
        pref_layout = [
            [sg.Text('Ajustes de preferencias')],
            [sg.Button('Cerrar', key='-CLOSE-PREF-')],
        ]
        
        pref_window = sg.Window('Preferencias', pref_layout)
        while True:
            event, _ = pref_window.read()
            if event in (sg.WINDOW_CLOSED, '-CLOSE-PREF-'):
                break
        pref_window.close()

    def _update_countdown(self) -> None:
        """Actualizar contador para auto-cerrar."""
        if self.countdown_active and self.countdown_remaining > 0:
            self.set_status(f'Cerrando en {self.countdown_remaining} segundos...')
            self.countdown_remaining -= 1
        elif self.countdown_active and self.countdown_remaining <= 0:
            self.countdown_active = False
