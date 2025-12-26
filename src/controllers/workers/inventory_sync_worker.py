"""
Inventory Sync Worker - Background thread for inventory synchronization
"""
from PyQt5.QtCore import QThread, pyqtSignal
import gspread
import csv
from datetime import datetime


class InventorySyncWorker(QThread):
    """
    Worker thread for inventory synchronization
    """
    progress_signal = pyqtSignal(int, str)
    status_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str, int, int, list)
    
    def __init__(self, credentials_path, sheet_id, inventory_data):
        super().__init__()
        self.credentials_path = credentials_path
        self.sheet_id = sheet_id
        self.inventory_data = inventory_data
    
    def run(self):
        """Run inventory sync in background"""
        try:
            self.status_signal.emit("Đang kết nối Google Sheets...")
            
            gc = gspread.service_account(filename=self.credentials_path)
            spreadsheet = gc.open(self.sheet_id)
            all_sheets = spreadsheet.worksheets()
            
            self.status_signal.emit(f"✓ Đã kết nối. Tìm thấy {len(all_sheets)} sheets")
            
            inventory_codes = [item[0] for item in self.inventory_data]
            
            self.status_signal.emit(f"Đang tìm kiếm {len(inventory_codes)} mã máy trong {len(all_sheets)} sheets...")
            
            total_matches = 0
            found_codes = set()
            
            for sheet_index, worksheet in enumerate(all_sheets):
                self.progress_signal.emit(
                    int((sheet_index / len(all_sheets)) * 100),
                    f"Đang xử lý sheet: {worksheet.title}"
                )
                
                try:
                    all_values = worksheet.get_all_values()
                    
                    if not all_values:
                        continue
                    
                    header_row = all_values[0]
                    ma_may_col_index = None
                    tinh_trang_col_index = None
                    kiem_hang_col_index = None
                    
                    for col_idx, header in enumerate(header_row):
                        header_lower = header.strip().lower()
                        if header_lower in ['mã máy', 'ma may', 'mã', 'code']:
                            ma_may_col_index = col_idx
                        elif header_lower in ['tình trạng', 'tinh trang', 'trạng thái', 'status']:
                            tinh_trang_col_index = col_idx
                        elif header_lower in ['kiểm hàng', 'kiem hang', 'kiểm tra', 'kiem tra', 'check']:
                            kiem_hang_col_index = col_idx
                    
                    if ma_may_col_index is None:
                        self.status_signal.emit(f"  ⚠ Sheet '{worksheet.title}': Không tìm thấy cột 'Mã máy'")
                        continue
                    
                    if tinh_trang_col_index is None:
                        self.status_signal.emit(f"  ⚠ Sheet '{worksheet.title}': Không tìm thấy cột 'Tình trạng'")
                        continue
                    
                    if kiem_hang_col_index is None:
                        self.status_signal.emit(f"  ⚠ Sheet '{worksheet.title}': Không tìm thấy cột 'Kiểm hàng'")
                        continue
                    
                    if len(all_values) > 1:
                        clear_range = f'{chr(65 + kiem_hang_col_index)}2:{chr(65 + kiem_hang_col_index)}{len(all_values)}'
                        try:
                            worksheet.batch_clear([clear_range])
                            self.status_signal.emit(f"  ✓ Đã xóa dữ liệu cột 'Kiểm hàng' trong sheet '{worksheet.title}'")
                        except Exception as e:
                            self.status_signal.emit(f"  ✗ Lỗi khi xóa cột 'Kiểm hàng' sheet '{worksheet.title}': {str(e)}")
                    
                    cells_to_update = []
                    
                    for row_idx, row_data in enumerate(all_values[1:], start=2):
                        if ma_may_col_index < len(row_data):
                            cell_value = row_data[ma_may_col_index].strip().upper()
                            
                            if cell_value in inventory_codes:
                                total_matches += 1
                                found_codes.add(cell_value)
                                
                                for code, ten_may, tinh_trang, vi_tri, nhan_vien in self.inventory_data:
                                    if code == cell_value:
                                        cells_to_update.append({
                                            'range': f'{chr(65 + tinh_trang_col_index)}{row_idx}',
                                            'values': [[tinh_trang]]
                                        })
                                        cells_to_update.append({
                                            'range': f'{chr(65 + kiem_hang_col_index)}{row_idx}',
                                            'values': [[nhan_vien if nhan_vien else 'Kiểm hàng lần 2']]
                                        })
                                        
                                        self.status_signal.emit(
                                            f"  ✓ '{cell_value}' - Sheet '{worksheet.title}', Hàng {row_idx}: "
                                            f"Cập nhật tình trạng '{tinh_trang}', nhân viên '{nhan_vien}'"
                                        )
                                        break
                    
                    if cells_to_update:
                        try:
                            worksheet.batch_update(cells_to_update)
                            self.status_signal.emit(f"  ✓ Đã cập nhật {len(cells_to_update)} cells trong sheet '{worksheet.title}'")
                        except Exception as e:
                            self.status_signal.emit(f"  ✗ Lỗi khi batch update sheet '{worksheet.title}': {str(e)}")
                
                except Exception as e:
                    self.status_signal.emit(f"  ✗ Lỗi khi xử lý sheet '{worksheet.title}': {str(e)}")
                    continue
            
            not_found_codes = [code for code in inventory_codes if code not in found_codes]
            
            csv_filename = ""
            if not_found_codes:
                csv_filename = f"ma_may_khong_tim_thay_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                try:
                    with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(['Mã Máy Không Tìm Thấy'])
                        for code in not_found_codes:
                            writer.writerow([code])
                    
                    self.status_signal.emit(f"⚠ Đã xuất {len(not_found_codes)} mã không tìm thấy ra file: {csv_filename}")
                except Exception as e:
                    self.status_signal.emit(f"✗ Lỗi khi xuất CSV: {str(e)}")
            
            self.progress_signal.emit(100, "Hoàn thành!")
            self.status_signal.emit(f"✓ Hoàn thành đồng bộ!")
            self.status_signal.emit(f"  - Tìm thấy: {total_matches} kết quả")
            self.status_signal.emit(f"  - Không tìm thấy: {len(not_found_codes)} mã máy")
            
            self.finished_signal.emit(True, csv_filename, total_matches, len(not_found_codes), not_found_codes)
            
        except FileNotFoundError:
            self.finished_signal.emit(False, "Không tìm thấy file credentials! Vui lòng kiểm tra đường dẫn.", 0, 0, [])
        except gspread.exceptions.SpreadsheetNotFound:
            self.finished_signal.emit(False, "Không tìm thấy Google Sheet! Vui lòng kiểm tra Sheet ID.", 0, 0, [])
        except Exception as e:
            self.finished_signal.emit(False, f"Đã xảy ra lỗi: {str(e)}", 0, 0, [])
