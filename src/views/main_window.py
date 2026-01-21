"""
Main Window View - PyQt5 Implementation
"""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QProgressBar, QTextEdit,
                             QFrame, QSizeGrip, QLineEdit, QFileDialog,
                             QTabWidget, QTableWidget, QTableWidgetItem,
                             QHeaderView, QComboBox, QCheckBox, QSpinBox,
                             QGroupBox, QFormLayout, QScrollArea)
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation, QSize, QSettings
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette
from .ui_styles import Styles

from .canvas import Canvas


class MainWindow(QMainWindow):
    """
    Main application window with modern UI and 4 tabs
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DOP Computer Sync Tool")
        self.setMinimumSize(QSize(1200, 800))
        
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.dragPos = QPoint()
        
        self.settings = QSettings("DOP", "ComputerSyncTool")
        
        self._setup_ui()
        
    def closeEvent(self, event):
        """Handle window close event to save data"""
        event.accept()
        
    def _setup_ui(self):
        """Setup the user interface"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.bg_frame = QFrame()
        self.bg_frame.setObjectName("bg_frame")
        bg_layout = QVBoxLayout(self.bg_frame)
        bg_layout.setContentsMargins(0, 0, 0, 0)
        
        main_layout.addWidget(self.bg_frame)
        
        self._create_content(bg_layout)
        
        self._apply_styles()
        
    def _create_content(self, parent_layout):
        """Create main content area"""
        title_bar = self._create_title_bar()
        parent_layout.addWidget(title_bar)
        
        self.content_frame = QFrame()
        self.content_frame.setObjectName("content_frame")
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("main_tabs")
        self.tab_widget.setTabPosition(QTabWidget.North)
        
        self.tab_settings = self._create_settings_tab()
        self.tab_widget.addTab(self.tab_settings, "Thông Số")
        
        self.tab_inventory = self._create_inventory_tab()
        self.tab_widget.addTab(self.tab_inventory, "Kiểm Hàng")
        
        self.tab_partners = self._create_partners_tab()
        self.tab_widget.addTab(self.tab_partners, "Đối Tác")

        self.tab_statistics = self._create_statistics_tab()
        self.tab_widget.addTab(self.tab_statistics, 'Thống kê')
        
        content_layout.addWidget(self.tab_widget)
        
        parent_layout.addWidget(self.content_frame)
        
        self.size_grip = QSizeGrip(self.bg_frame)
        self.size_grip.setFixedSize(20, 20)
    
    def _create_settings_tab(self):
        """Create Settings/Parameters tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("scroll_area")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        general_group = QGroupBox("Cài Đặt Chung")
        general_group.setObjectName("settings_group")
        general_layout = QFormLayout(general_group)
        
        self.settings_app_name = QLineEdit()
        self.settings_app_name.setObjectName("settings_input")
        self.settings_app_name.setText("DOP Computer Sync Tool")
        general_layout.addRow("Tên ứng dụng:", self.settings_app_name)
        
        self.settings_theme = QComboBox()
        self.settings_theme.setObjectName("settings_combo")
        self.settings_theme.addItems(["Dark Theme", "Light Theme", "Auto"])
        general_layout.addRow("Giao diện:", self.settings_theme)
        
        scroll_layout.addWidget(general_group)
        
        sheets_group = QGroupBox("Cài Đặt Google Sheets")
        sheets_group.setObjectName("settings_group")
        sheets_layout = QFormLayout(sheets_group)
        
        self.settings_sheet_id_may_ton = QLineEdit()
        self.settings_sheet_id_may_ton.setObjectName("settings_input")
        self.settings_sheet_id_may_ton.setPlaceholderText("Nhập Sheet ID Máy Tồn...")
        sheets_layout.addRow("Sheet Máy Tồn:", self.settings_sheet_id_may_ton)
        
        self.settings_sheet_id_don_hang = QLineEdit()
        self.settings_sheet_id_don_hang.setObjectName("settings_input")
        self.settings_sheet_id_don_hang.setPlaceholderText("Nhập Sheet ID Đơn Hàng...")
        sheets_layout.addRow("Sheet Đơn Hàng:", self.settings_sheet_id_don_hang)
        
        self.settings_credentials = QLineEdit()
        self.settings_credentials.setObjectName("settings_input")
        self.settings_credentials.setPlaceholderText("Chọn file credentials.json...")
        self.settings_credentials_btn = QPushButton("Browse")
        self.settings_credentials_btn.setObjectName("browse_btn")
        self.settings_credentials_btn.setMaximumWidth(100)
        
        cred_layout_h = QHBoxLayout()
        cred_layout_h.addWidget(self.settings_credentials)
        cred_layout_h.addWidget(self.settings_credentials_btn)
        sheets_layout.addRow("Credentials:", cred_layout_h)
        
        scroll_layout.addWidget(sheets_group)
        
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        sync_section = QGroupBox("Đồng Bộ Dữ Liệu")
        sync_section.setObjectName("settings_group")
        sync_section_layout = QVBoxLayout(sync_section)
        
        self.sync_btn = QPushButton("Bắt Đầu Đồng Bộ")
        self.sync_btn.setObjectName("sync_btn")
        self.sync_btn.setMinimumHeight(45)
        sync_section_layout.addWidget(self.sync_btn)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progress_bar")
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        sync_section_layout.addWidget(self.progress_bar)
        
        self.status_text = QTextEdit()
        self.status_text.setObjectName("status_text")
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(150)
        self.status_text.setPlaceholderText("Log đồng bộ sẽ hiển thị ở đây...")
        sync_section_layout.addWidget(self.status_text)
        
        layout.addWidget(sync_section)
        
        return tab
    
    def _create_inventory_tab(self):
        """Create Inventory Check tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        title = QLabel("Danh Sách Kiểm Hàng")
        title.setObjectName("tab_title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        toolbar = QHBoxLayout()
        
        self.inventory_sync_btn = QPushButton("Đồng Bộ")
        self.inventory_sync_btn.setObjectName("action_btn")
        self.inventory_sync_btn.setMinimumWidth(150)
        toolbar.addWidget(self.inventory_sync_btn)
        
        self.inventory_add_10_btn = QPushButton("Thêm 10 Hàng")
        self.inventory_add_10_btn.setObjectName("action_btn")
        self.inventory_add_10_btn.setMinimumWidth(150)
        toolbar.addWidget(self.inventory_add_10_btn)
        
        self.inventory_import_btn = QPushButton("Nhập từ Excel")
        self.inventory_import_btn.setObjectName("action_btn")
        self.inventory_import_btn.setMinimumWidth(150)
        toolbar.addWidget(self.inventory_import_btn)
        
        self.inventory_export_btn = QPushButton("Xuất sang Excel")
        self.inventory_export_btn.setObjectName("action_btn")
        self.inventory_export_btn.setMinimumWidth(150)
        toolbar.addWidget(self.inventory_export_btn)
        
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        self.inventory_table = QTableWidget()
        self.inventory_table.setObjectName("data_table")
        self.inventory_table.setColumnCount(5)
        self.inventory_table.setHorizontalHeaderLabels([
            "Mã Máy", "Tên Máy", "Tình Trạng", "Vị Trí", "Nhân Viên"
        ])
        self.inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.inventory_table.setAlternatingRowColors(True)
        self.inventory_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.inventory_table.setEditTriggers(QTableWidget.AllEditTriggers)
        
        self.inventory_table.setRowCount(0)
        
        layout.addWidget(self.inventory_table)
        
        status_layout = QHBoxLayout()
        self.inventory_status = QLabel("Tổng: 0 máy")
        self.inventory_status.setObjectName("status_label")
        status_layout.addWidget(self.inventory_status)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        return tab
    
    def _create_partners_tab(self):
        """Create Partners tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        title = QLabel("Danh Sách Đối Tác")
        title.setObjectName("tab_title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        toolbar = QHBoxLayout()
        
        self.partners_sync_btn = QPushButton("Đồng Bộ")
        self.partners_sync_btn.setObjectName("action_btn")
        self.partners_sync_btn.setMinimumWidth(150)
        toolbar.addWidget(self.partners_sync_btn)
        
        self.partners_add_btn = QPushButton("Thêm 1 Hàng")
        self.partners_add_btn.setObjectName("action_btn")
        self.partners_add_btn.setMinimumWidth(150)
        toolbar.addWidget(self.partners_add_btn)
        toolbar.addWidget(self.partners_sync_btn)
        
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        self.partners_table = QTableWidget()
        self.partners_table.setObjectName("data_table")
        self.partners_table.setColumnCount(3)
        self.partners_table.setHorizontalHeaderLabels([
            "Tên", "Link Drive", "Ghi Chú"
        ])
        self.partners_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.partners_table.setAlternatingRowColors(True)
        self.partners_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.partners_table.setEditTriggers(QTableWidget.AllEditTriggers)
        
        self.partners_table.setRowCount(0)
        
        layout.addWidget(self.partners_table)
        
        status_layout = QHBoxLayout()
        self.partners_status = QLabel("Tổng: 0 đối tác")
        self.partners_status.setObjectName("status_label")
        status_layout.addWidget(self.partners_status)
        status_layout.addStretch()
        
        layout.addLayout(status_layout)
        
        return tab
    
    def _create_statistics_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        title = QLabel("Thống kê")
        title.setObjectName("tab_title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        controls_layout = QHBoxLayout()
        
        date_label = QLabel("Thời gian:")
        controls_layout.addWidget(date_label)
        
        self.stats_date_combo = QComboBox()
        self.stats_date_combo.setObjectName("settings_combo")
        self.stats_date_combo.addItems(["Tất cả"])
        self.stats_date_combo.setMinimumWidth(150)
        controls_layout.addWidget(self.stats_date_combo)
        
        controls_layout.addSpacing(20)
        
        chart_type_label = QLabel("Loại biểu đồ:")
        controls_layout.addWidget(chart_type_label)
        
        self.stats_chart_type_combo = QComboBox()
        self.stats_chart_type_combo.setObjectName("settings_combo")
        self.stats_chart_type_combo.addItems(["Cột", "Đường", "Tròn", "Thanh ngang"])
        self.stats_chart_type_combo.setMinimumWidth(150)
        controls_layout.addWidget(self.stats_chart_type_combo)
        
        controls_layout.addSpacing(20)
        
        value_label = QLabel("Giá trị:")
        controls_layout.addWidget(value_label)
        
        self.stats_value_combo = QComboBox()
        self.stats_value_combo.setObjectName("settings_combo")
        self.stats_value_combo.addItems(["Doanh thu", "Số lượng bán", "Tồn kho", "Đối tác", "Nhân viên"])
        self.stats_value_combo.setMinimumWidth(150)
        controls_layout.addWidget(self.stats_value_combo)
        
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        content_layout = QHBoxLayout()
        
        self.stats_canvas = Canvas(self)
        content_layout.addWidget(self.stats_canvas, stretch=7)
        
        stats_info_group = QGroupBox("Thông tin thống kê")
        stats_info_group.setObjectName("settings_group")
        stats_info_layout = QVBoxLayout(stats_info_group)
        
        self.stats_info_text = QTextEdit()
        self.stats_info_text.setObjectName("status_text")
        self.stats_info_text.setReadOnly(True)
        self.stats_info_text.setMaximumWidth(300)
        self.stats_info_text.setPlaceholderText("Thông tin chi tiết sẽ hiển thị ở đây...")
        stats_info_layout.addWidget(self.stats_info_text)
        
        content_layout.addWidget(stats_info_group, stretch=3)
        
        layout.addLayout(content_layout)
        
        return tab
        
    def _create_title_bar(self):
        """Create custom title bar"""
        title_bar = QFrame()
        title_bar.setObjectName("title_bar")
        title_bar.setMaximumHeight(50)
        title_bar.setMinimumHeight(50)
        
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        
        self.window_title = QLabel("DOP Computer Sync Tool")
        self.window_title.setObjectName("window_title")
        title_layout.addWidget(self.window_title)
        
        title_layout.addStretch()
        
        self.minimize_btn = QPushButton("—")
        self.minimize_btn.setObjectName("title_btn")
        self.minimize_btn.setMaximumSize(40, 30)
        self.minimize_btn.clicked.connect(self.showMinimized)
        title_layout.addWidget(self.minimize_btn)
        
        self.maximize_btn = QPushButton("☐")
        self.maximize_btn.setObjectName("title_btn")
        self.maximize_btn.setMaximumSize(40, 30)
        self.maximize_btn.clicked.connect(self.toggle_maximize_restore)
        title_layout.addWidget(self.maximize_btn)
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("close_btn")
        self.close_btn.setMaximumSize(40, 30)
        self.close_btn.clicked.connect(self.close)
        title_layout.addWidget(self.close_btn)
        
        return title_bar
    
    def _apply_styles(self):
        """Apply stylesheet to the window"""
        self.setStyleSheet(Styles.get_stylesheet())
    
    def toggle_maximize_restore(self):
        """Toggle between maximized and normal state"""
        if self.isMaximized():
            self.showNormal()
            self.maximize_btn.setText("☐")
        else:
            self.showMaximized()
            self.maximize_btn.setText("❐")
    
    def mousePressEvent(self, event):
        """Handle mouse press for window dragging"""
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for window dragging"""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.dragPos)
            event.accept()
    
    def update_progress(self, value, message=""):
        """Update progress bar and status"""
        self.progress_bar.setValue(value)
        if message:
            self.add_status_message(message)
    
    def add_status_message(self, message):
        """Add message to status text"""
        self.status_text.append(message)
    
    def enable_sync_button(self, enabled=True):
        """Enable or disable sync button"""
        self.sync_btn.setEnabled(enabled)
        if enabled:
            self.sync_btn.setText("Bắt Đầu Đồng Bộ")
        else:
            self.sync_btn.setText("Đang Đồng Bộ...")    
    def get_all_data(self):
        """Get all data from tables and settings"""
        data = {
            "inventory": [],
            "partners": [],
            "settings": {}
        }
        
        for row in range(self.inventory_table.rowCount()):
            row_data = []
            for col in range(self.inventory_table.columnCount()):
                item = self.inventory_table.item(row, col)
                row_data.append(item.text() if item else "")
            if any(cell for cell in row_data):
                data["inventory"].append(row_data)
        
        for row in range(self.partners_table.rowCount()):
            row_data = []
            for col in range(self.partners_table.columnCount()):
                item = self.partners_table.item(row, col)
                row_data.append(item.text() if item else "")
            if any(cell for cell in row_data):
                data["partners"].append(row_data)
        
        data["settings"]["app_name"] = self.settings_app_name.text()
        data["settings"]["theme"] = self.settings_theme.currentText()
        data["settings"]["sheet_id_may_ton"] = self.settings_sheet_id_may_ton.text()
        data["settings"]["sheet_id_don_hang"] = self.settings_sheet_id_don_hang.text()
        data["settings"]["credentials"] = self.settings_credentials.text()
        
        return data
    
    def set_all_data(self, data):
        """Set all data to tables and settings"""
        if not data:
            return
        
        if "inventory" in data:
            self.inventory_table.setRowCount(0)
            for row_data in data["inventory"]:
                row = self.inventory_table.rowCount()
                self.inventory_table.insertRow(row)
                for col, value in enumerate(row_data):
                    self.inventory_table.setItem(row, col, QTableWidgetItem(str(value)))
        
        if "partners" in data:
            self.partners_table.setRowCount(0)
            for row_data in data["partners"]:
                row = self.partners_table.rowCount()
                self.partners_table.insertRow(row)
                for col, value in enumerate(row_data):
                    self.partners_table.setItem(row, col, QTableWidgetItem(str(value)))
        
        if "settings" in data:
            settings = data["settings"]
            if "app_name" in settings:
                self.settings_app_name.setText(settings["app_name"])
            if "theme" in settings:
                index = self.settings_theme.findText(settings["theme"])
                if index >= 0:
                    self.settings_theme.setCurrentIndex(index)
            if "sheet_id_may_ton" in settings:
                self.settings_sheet_id_may_ton.setText(settings["sheet_id_may_ton"])
            if "sheet_id_don_hang" in settings:
                self.settings_sheet_id_don_hang.setText(settings["sheet_id_don_hang"])
            if "credentials" in settings:
                self.settings_credentials.setText(settings["credentials"])