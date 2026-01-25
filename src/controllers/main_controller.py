"""
Main Controller - Connects Model and View
"""
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QFont
from models import SyncModel
from views import MainWindow
from .workers import InventorySyncWorker, MainSyncWorker, PartnersSyncWorker, StatsDataWorker

import gspread
from gspread.cell import Cell
import pandas as pd


class SheetNamesWorker(QThread):
    """Worker thread to load sheet names without blocking UI"""
    finished_signal = pyqtSignal(list)
    
    def __init__(self, credentials_path, sheet_id):
        super().__init__()
        self.credentials_path = credentials_path
        self.sheet_id = sheet_id
    
    def run(self):
        try:
            gc = gspread.service_account(filename=self.credentials_path)
            sale_sheet = gc.open(self.sheet_id)
            sheet_names = [ws.title for ws in sale_sheet.worksheets()]
            self.finished_signal.emit(sheet_names)
        except Exception:
            self.finished_signal.emit([])


class SyncWorker(QThread):
    """
    Worker thread for synchronization to prevent UI blocking
    """
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, model, source, destination):
        super().__init__()
        self.model = model
        self.source = source
        self.destination = destination
    
    def run(self):
        """Run sync operation in background thread"""
        try:
            self.model.start_sync(self.source, self.destination)
        except Exception as e:
            self.finished.emit(False, str(e))


class MainController:
    """
    Main controller managing interaction between Model and View
    """
    
    def __init__(self):
        self.model = SyncModel()
        self.view = MainWindow()
        
        font = QFont("Segoe UI", 9)
        QMessageBox().setFont(font)
        
        self.worker = None
        self.sheet_names_worker = None
        self.stats_data_worker = None
        self._connect_signals()
        self.view.destroyed.connect(self._save_current_data)
        self._load_saved_data()
        
    def _show_message(self, icon, title, text, buttons=QMessageBox.Ok):
        """Helper method to show message box with proper font"""
        msg = QMessageBox(self.view)
        msg.setIcon(icon)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStandardButtons(buttons)
        
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        msg.setFont(font)
        
        for button in msg.buttons():
            button.setFont(font)
        
        return msg.exec_()
    
    def _load_saved_data(self):
        """Load previously saved data"""
        saved_data = self.model.load_app_data()
        if saved_data:
            self.view.set_all_data(saved_data)
            self.view.add_status_message("Đã tải dữ liệu đã lưu")
    
    def _save_current_data(self):
        """Save current data before closing"""
        data = self.view.get_all_data()
        if self.model.save_app_data(data):
            return True
        return False
        
    def _connect_signals(self):
        """Connect view signals to controller methods"""
        self.view.sync_btn.clicked.connect(self.start_sync)
        self.view.settings_credentials_btn.clicked.connect(self.browse_credentials)
        self.view.inventory_sync_btn.clicked.connect(self.sync_inventory)
        self.view.inventory_add_10_btn.clicked.connect(self.add_10_inventory_rows)
        self.view.inventory_import_btn.clicked.connect(self.import_inventory_from_excel)
        self.view.inventory_export_btn.clicked.connect(self.export_inventory_to_excel)
        self.view.partners_add_btn.clicked.connect(self.add_partner_row)
        self.view.partners_sync_btn.clicked.connect(self.sync_partners)
        self.view.tab_widget.currentChanged.connect(self._on_tab_changed)
        self.view.stats_update_btn.clicked.connect(self._on_stats_update_clicked)
        self.model.sync_started.connect(self.on_sync_started)
        self.model.sync_progress.connect(self.on_sync_progress)
        self.model.sync_completed.connect(self.on_sync_completed)
        self.model.data_changed.connect(self.on_data_changed)
    
    def start_sync(self):
        """Handle sync button click"""
        sheet_may_ton = self.view.settings_sheet_id_may_ton.text().strip()
        sheet_don_hang = self.view.settings_sheet_id_don_hang.text().strip()
        credentials_path = self.view.settings_credentials.text().strip()
        
        if not sheet_may_ton or not sheet_don_hang:
            self._show_message(
                QMessageBox.Warning,
                "Thiếu thông tin",
                "Vui lòng nhập tên Sheet cho cả Máy Tồn và Đơn Hàng trong tab Thông Số."
            )
            return
        
        if not credentials_path:
            self._show_message(
                QMessageBox.Warning,
                "Thiếu thông tin",
                "Vui lòng chọn file Credentials trong tab Thông Số."
            )
            return
        
        self.main_sync_worker = MainSyncWorker(credentials_path, sheet_may_ton, sheet_don_hang)
        self.main_sync_worker.progress_signal.connect(self.view.update_progress)
        self.main_sync_worker.status_signal.connect(self.view.add_status_message)
        self.main_sync_worker.finished_signal.connect(self._on_main_sync_finished)
        self.view.enable_sync_button(False)
        self.main_sync_worker.start()
    
    def _on_main_sync_finished(self, success, message):
        """Handle main sync completion"""
        self.view.enable_sync_button(True)
        
        if success:
            self._show_message(
                QMessageBox.Information,
                "Thành công",
                message
            )
        else:
            self._show_message(
                QMessageBox.Critical,
                "Lỗi",
                message
            )
    
    def on_sync_started(self):
        """Handle sync started event"""
        self.view.update_progress(0, "Synchronization started")
    
    def on_sync_progress(self, progress, message):
        """Handle sync progress update"""
        self.view.update_progress(progress, message)
    
    def on_sync_completed(self, success, message):
        """Handle sync completion"""
        self.view.enable_sync_button(True)
        
        if success:
            self.view.update_progress(100, message)
            QMessageBox.information(
                self.view,
                "Success",
                message
            )
        else:
            QMessageBox.critical(
                self.view,
                "Error",
                f"Synchronization failed: {message}"
            )
        
        if self.worker:
            self.worker.quit()
            self.worker.wait()
            self.worker = None
    
    def on_data_changed(self, data):
        """Handle data change event from model"""
        pass
    
    def _on_tab_changed(self, index):
        """Handle tab change event"""
        if index == 3:
            self._load_sheet_names_to_stats()
    
    def _load_sheet_names_to_stats(self):
        """Load sheet names from Google Sheets to statistics tab"""
        credentials_path = self.view.settings_credentials.text().strip()
        sheet_don_hang = self.view.settings_sheet_id_don_hang.text().strip()
        
        if not credentials_path or not sheet_don_hang:
            return
        
        if self.sheet_names_worker and self.sheet_names_worker.isRunning():
            return
        
        self.sheet_names_worker = SheetNamesWorker(credentials_path, sheet_don_hang)
        self.sheet_names_worker.finished_signal.connect(self._on_sheet_names_loaded)
        self.sheet_names_worker.start()
    
    def _on_sheet_names_loaded(self, sheet_names):
        """Handle loaded sheet names"""
        self.view.stats_date_combo.clear()
        self.view.stats_date_combo.addItem("Tất cả")
        if sheet_names:
            self.view.stats_date_combo.addItems(sheet_names)
    
    def _on_stats_update_clicked(self):
        """Handle stats update button click - load data and update chart"""
        sheet_name = self.view.stats_date_combo.currentText()
        
        if not sheet_name:
            return
        
        credentials_path = self.view.settings_credentials.text().strip()
        sheet_don_hang = self.view.settings_sheet_id_don_hang.text().strip()
        
        if not credentials_path or not sheet_don_hang:
            self.view.stats_info_text.setText("⚠️ Vui lòng cấu hình đầy đủ thông tin ở tab Cài đặt")
            return
        
        if self.stats_data_worker and self.stats_data_worker.isRunning():
            return
        
        self.view.stats_info_text.setText("Đang tải dữ liệu...")
        
        self.stats_data_worker = StatsDataWorker(credentials_path, sheet_don_hang, sheet_name)
        self.stats_data_worker.finished_signal.connect(self._on_stats_data_loaded)
        self.stats_data_worker.error_signal.connect(self._on_stats_data_error)
        self.stats_data_worker.start()
    
    def _on_stats_data_loaded(self, buyers, order_counts):
        """Handle loaded stats data - update chart"""
        self.view.stats_canvas.update_chart(buyers, order_counts)
        
        total_orders = sum(order_counts)
        total_buyers = len(buyers)
        avg_orders = total_orders / total_buyers if total_buyers > 0 else 0
        
        # Tạo danh sách chi tiết từng người
        buyer_details = []
        for buyer, count in zip(buyers, order_counts):
            buyer_details.append(f"  • {buyer}: {count} máy")
        
        details_text = "\n".join(buyer_details) if buyer_details else "  Không có dữ liệu"
        
        info_text = f"""📊 THỐNG KÊ ĐỐI TÁC

👥 Số người mua: {total_buyers}
💻 Tổng máy: {total_orders}
📊 Trung bình: {avg_orders:.1f} máy/người

🏆 Nhiều nhất: {max(order_counts) if order_counts else 0} máy
📉 Ít nhất: {min(order_counts) if order_counts else 0} máy

━━━━━━━━━━━━━━━━━━━━━━━━
📋 CHI TIẾT TỪNG NGƯỜI:
{details_text}"""
        self.view.stats_info_text.setText(info_text)
    
    def _on_stats_data_error(self, error_msg):
        """Handle stats data error"""
        self.view.stats_info_text.setText(f"❌ Lỗi: {error_msg}")
    
    def browse_credentials(self):
        """Browse for credentials file"""
        file, _ = QFileDialog.getOpenFileName(
            self.view,
            "Chọn file Credentials",
            "",
            "JSON Files (*.json);;All Files (*.*)"
        )
        
        if file:
            self.view.settings_credentials.setText(file)
            self.view.status_text.append(f"✓ Đã chọn credentials: {file}")
    
    def sync_inventory(self):
        """Sync inventory data"""
        reply = self._show_message(
            QMessageBox.Question,
            "Xác nhận",
            "Bạn có chắc muốn đồng bộ dữ liệu kiểm hàng?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            credentials_path = self.view.settings_credentials.text()
            sheet_id_may_ton = self.view.settings_sheet_id_may_ton.text()
            
            if not credentials_path or not sheet_id_may_ton:
                self._show_message(
                    QMessageBox.Warning,
                    "Thiếu thông tin",
                    "Vui lòng nhập Credentials và Sheet ID Máy Tồn trong tab Thông Số."
                )
                return
            
            inventory_data = []
            for row in range(self.view.inventory_table.rowCount()):
                code_item = self.view.inventory_table.item(row, 0)
                if code_item and code_item.text().strip():
                    code = code_item.text().strip().upper()
                    ten_may = self.view.inventory_table.item(row, 1).text() if self.view.inventory_table.item(row, 1) else ""
                    tinh_trang = self.view.inventory_table.item(row, 2).text() if self.view.inventory_table.item(row, 2) else ""
                    vi_tri = self.view.inventory_table.item(row, 3).text() if self.view.inventory_table.item(row, 3) else ""
                    nhan_vien = self.view.inventory_table.item(row, 4).text() if self.view.inventory_table.item(row, 4) else ""
                    inventory_data.append((code, ten_may, tinh_trang, vi_tri, nhan_vien))
            
            if not inventory_data:
                self._show_message(
                    QMessageBox.Warning,
                    "Không có dữ liệu",
                    "Bảng kiểm hàng không có mã máy nào!"
                )
                return
            
            self.inventory_worker = InventorySyncWorker(credentials_path, sheet_id_may_ton, inventory_data)
            self.inventory_worker.progress_signal.connect(self.view.update_progress)
            self.inventory_worker.status_signal.connect(self.view.add_status_message)
            self.inventory_worker.finished_signal.connect(self._on_inventory_sync_finished)
            

            self.view.inventory_sync_btn.setEnabled(False)
            self.view.inventory_sync_btn.setText("Đang đồng bộ...")
            
            self.inventory_worker.start()
    
    def _on_inventory_sync_finished(self, success, message, total_matches, not_found_count, not_found_codes):
        """Handle inventory sync completion"""
        self.view.inventory_sync_btn.setEnabled(True)
        self.view.inventory_sync_btn.setText("Đồng Bộ")
        
        if success:
            msg_text = f"Đã đồng bộ {total_matches} mã máy!\n\n"
            msg_text += f"Tìm thấy: {total_matches} mã\n"
            msg_text += f"Không tìm thấy: {not_found_count} mã\n\n"
            if message:  # message chứa tên file CSV
                msg_text += f"File CSV đã được tạo: {message}"
            
            self._show_message(
                QMessageBox.Information,
                "Thành công",
                msg_text
            )
        else:
            self._show_message(
                QMessageBox.Critical,
                "Lỗi",
                message
            )
    
    def add_10_inventory_rows(self):
        """Add 10 empty rows to inventory table"""
        current_row_count = self.view.inventory_table.rowCount()
        
        for i in range(10):
            row_position = current_row_count + i
            self.view.inventory_table.insertRow(row_position)
            
            for col in range(5):
                item = QTableWidgetItem("")
                self.view.inventory_table.setItem(row_position, col, item)
        

        new_count = self.view.inventory_table.rowCount()
        self.view.inventory_status.setText(f"Tổng: {new_count} máy")
        self.view.status_text.append(f"✓ Đã thêm 10 hàng mới (Tổng: {new_count} hàng)")
    
    def import_inventory_from_excel(self):
        """Import inventory data from Excel file"""
        file, _ = QFileDialog.getOpenFileName(
            self.view,
            "Chọn file Excel",
            "",
            "Excel Files (*.xlsx *.xls);;All Files (*.*)"
        )
        
        if file:
            try:
                import pandas as pd
                df = pd.read_excel(file)
                
                self.view.inventory_table.setRowCount(0)
                

                for index, row in df.iterrows():
                    row_position = self.view.inventory_table.rowCount()
                    self.view.inventory_table.insertRow(row_position)
                    
                    for col in range(min(len(row), 5)):
                        value = str(row.iloc[col]) if pd.notna(row.iloc[col]) else ""
                        item = QTableWidgetItem(value)
                        self.view.inventory_table.setItem(row_position, col, item)
                
                row_count = self.view.inventory_table.rowCount()
                self.view.inventory_status.setText(f"Tổng: {row_count} máy")
                self.view.status_text.append(f"✓ Đã nhập {row_count} dòng từ Excel")
                
                self._show_message(
                    QMessageBox.Information,
                    "Thành công",
                    f"Đã nhập {row_count} dòng dữ liệu từ Excel!"
                )
            except Exception as e:
                self._show_message(
                    QMessageBox.Critical,
                    "Lỗi",
                    f"Không thể đọc file Excel: {str(e)}"
                )
    
    def export_inventory_to_excel(self):
        """Export inventory data to Excel file"""
        if self.view.inventory_table.rowCount() == 0:
            self._show_message(
                QMessageBox.Warning,
                "Cảnh báo",
                "Không có dữ liệu để xuất!"
            )
            return
        
        file, _ = QFileDialog.getSaveFileName(
            self.view,
            "Lưu file Excel",
            "inventory_export.xlsx",
            "Excel Files (*.xlsx);;All Files (*.*)"
        )
        
        if file:
            try:
                import pandas as pd
                
                data = []
                headers = ["Mã Máy", "Tên Máy", "Tình Trạng", "Vị Trí", "Nhân Viên"]
                
                for row in range(self.view.inventory_table.rowCount()):
                    row_data = []
                    for col in range(self.view.inventory_table.columnCount()):
                        item = self.view.inventory_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    if any(cell for cell in row_data):
                        data.append(row_data)
                
                df = pd.DataFrame(data, columns=headers)
                df.to_excel(file, index=False)
                
                self.view.status_text.append(f"✓ Đã xuất {len(data)} dòng sang Excel")
                
                self._show_message(
                    QMessageBox.Information,
                    "Thành công",
                    f"Đã xuất {len(data)} dòng dữ liệu ra file Excel!"
                )
            except Exception as e:
                self._show_message(
                    QMessageBox.Critical,
                    "Lỗi",
                    f"Không thể xuất file Excel: {str(e)}"
                )
    
    def add_partner_row(self):
        """Add 1 empty row to partners table"""
        current_row_count = self.view.partners_table.rowCount()
        
        self.view.partners_table.insertRow(current_row_count)
        
        for col in range(3):
            item = QTableWidgetItem("")
            self.view.partners_table.setItem(current_row_count, col, item)
        
        new_count = self.view.partners_table.rowCount()
        self.view.partners_status.setText(f"Tổng: {new_count} đối tác")
        self.view.status_text.append(f"✓ Đã thêm 1 hàng mới (Tổng: {new_count} hàng)")
    
    def sync_partners(self):
        """Sync partners data"""
        credentials_path = self.view.settings_credentials.text().strip()
        sheet_id = self.view.settings_sheet_id_may_ton.text().strip()  # Tạm dùng sheet máy tồn, có thể thêm sheet ID riêng cho đối tác
        
        if not credentials_path:
            self._show_message(
                QMessageBox.Warning,
                "Thiếu thông tin",
                "Vui lòng chọn file Credentials trong tab Thông Số."
            )
            return
        
        if not sheet_id:
            self._show_message(
                QMessageBox.Warning,
                "Thiếu thông tin",
                "Vui lòng nhập Sheet ID trong tab Thông Số."
            )
            return
        
        reply = self._show_message(
            QMessageBox.Question,
            "Xác nhận",
            "Bạn có chắc muốn đồng bộ dữ liệu đối tác?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            partners_data = []
            for row in range(self.view.partners_table.rowCount()):
                row_data = []
                for col in range(self.view.partners_table.columnCount()):
                    item = self.view.partners_table.item(row, col)
                    row_data.append(item.text() if item else "")
                if any(cell for cell in row_data):
                    partners_data.append(row_data)
            
            df = pd.DataFrame(partners_data, columns=['Tên', 'Link Drive', 'Ghi Chú'])
            
            self.partners_sync_worker = PartnersSyncWorker(credentials_path, sheet_id, df)
            self.partners_sync_worker.progress_signal.connect(self.view.update_progress)
            self.partners_sync_worker.status_signal.connect(self.view.add_status_message)
            self.partners_sync_worker.finished_signal.connect(self._on_partners_sync_finished)
            
            self.view.partners_sync_btn.setEnabled(False)
            
            self.partners_sync_worker.start()
    
    def _on_partners_sync_finished(self, success, message):
        """Handle partners sync completion"""
        self.view.partners_sync_btn.setEnabled(True)
        
        if success:
            self._show_message(
                QMessageBox.Information,
                "Thành công",
                message
            )
        else:
            self._show_message(
                QMessageBox.Critical,
                "Lỗi",
                message
            )
    
    def show(self):
        """Show the main window"""
        self.view.show()
    
    def run(self):
        """Run the application"""
        return self.view
