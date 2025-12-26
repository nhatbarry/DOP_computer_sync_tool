"""
Partners Sync Worker - Background thread for partners data synchronization
"""
from PyQt5.QtCore import QThread, pyqtSignal
from gspread.cell import Cell
import gspread
import pandas as pd


class PartnersSyncWorker(QThread):
    """
    Worker thread for partners synchronization
    """
    progress_signal = pyqtSignal(int, str)
    status_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    
    def __init__(self, credentials_path, sheet_may_ton_id, partners_data):
        super().__init__()
        self.credentials_path = credentials_path
        self.sheet_may_ton_id = sheet_may_ton_id
        self.partners_data = partners_data
    
    def run(self):
        """Run partners sync in background"""
        try:
            self.status_signal.emit("Đang kết nối Google Sheets...")
            self.progress_signal.emit(10, "Đang kết nối...")
            
            gc = gspread.service_account(filename=self.credentials_path)
            
            id_header = 'mã máy'
            price_header = 'giá sửa'
            type_pin_header = 'type pin'
            
            data_dict = {}
            
            self.status_signal.emit("Đang thu thập dữ liệu từ các đối tác...")
            total_partners = len(self.partners_data)
            
            for idx, row in self.partners_data.iterrows():
                partner_name = row['Tên']
                link_drive = row['Link Drive']
                ghi_chu = row['Ghi Chú'].strip().lower() if pd.notna(row['Ghi Chú']) else ""
                
                if not link_drive:
                    self.status_signal.emit(f"  ⚠ Bỏ qua '{partner_name}': Thiếu link drive")
                    continue
                
                self.progress_signal.emit(
                    10 + int((idx / total_partners) * 40),
                    f"Đang xử lý đối tác: {partner_name}"
                )
                
                try:
                    partner_sheet = gc.open(link_drive)
                    list_partner_sheets = partner_sheet.worksheets()
                    
                    self.status_signal.emit(f"  → Đang quét {len(list_partner_sheets)} sheet từ '{partner_name}'")
                    
                    for sheet in list_partner_sheets:
                        sheet_data = sheet.get_all_values()
                        if not sheet_data:
                            continue
                        
                        df = pd.DataFrame(sheet_data[1:], columns=sheet_data[0])
                        df.columns = df.columns.str.lower().str.strip()
                        
                        if id_header not in df.columns or price_header not in df.columns:
                            continue
                        
                        df[id_header] = df[id_header].astype(str).str.strip().str.upper()
                        df[price_header] = pd.to_numeric(df[price_header], errors='coerce').fillna(0)
                        
                        for _, data_row in df.iterrows():
                            machine_id = data_row[id_header]
                            price = data_row[price_header]
                            
                            if not machine_id or price <= 0:
                                continue
                            
                            if ghi_chu == 'màn':
                                target_column = 'màn'
                            elif type_pin_header in df.columns and pd.notna(data_row.get(type_pin_header)) and str(data_row.get(type_pin_header)).strip():
                                target_column = 'pin'
                            else:
                                target_column = 'sửa'
                            
                            if machine_id not in data_dict:
                                data_dict[machine_id] = {}
                            
                            if target_column in data_dict[machine_id]:
                                data_dict[machine_id][target_column] += price
                            else:
                                data_dict[machine_id][target_column] = price
                    
                    self.status_signal.emit(f"  ✓ Đã xử lý xong '{partner_name}'")
                    
                except Exception as e:
                    self.status_signal.emit(f"  ✗ Lỗi khi xử lý '{partner_name}': {str(e)}")
                    continue
            
            if not data_dict:
                self.finished_signal.emit(False, "Không tìm thấy dữ liệu nào từ các đối tác!")
                return
            
            self.status_signal.emit(f"✓ Đã thu thập {len(data_dict)} mã máy từ {total_partners} đối tác")
            
            self.status_signal.emit("Đang cập nhật vào file máy tồn...")
            self.progress_signal.emit(50, "Đang cập nhật file máy tồn...")
            
            stock_sheet = gc.open(self.sheet_may_ton_id)
            list_stock_sheets = stock_sheet.worksheets()
            
            total_updated = 0
            
            for sheet_idx, worksheet in enumerate(list_stock_sheets):
                self.progress_signal.emit(
                    50 + int((sheet_idx / len(list_stock_sheets)) * 50),
                    f"Đang cập nhật sheet: {worksheet.title}"
                )
                
                try:
                    header = worksheet.row_values(1)
                    clean_header = [str(h).strip().lower() for h in header]
                    
                    if id_header not in clean_header:
                        self.status_signal.emit(f"  ⚠ Sheet '{worksheet.title}': Không có cột 'Mã máy'")
                        continue
                    
                    ma_may_col_idx = clean_header.index(id_header) + 1
                    code_list = worksheet.col_values(ma_may_col_idx)
                    cells_to_update = []
                    
                    for i, code_val in enumerate(code_list):
                        current_code = str(code_val).strip().upper()
                        
                        if current_code in data_dict:
                            real_row = i + 1
                            
                            for target_col, price_value in data_dict[current_code].items():
                                if target_col in clean_header:
                                    col_idx = clean_header.index(target_col) + 1
                                    cells_to_update.append(Cell(real_row, col_idx, float(price_value)))
                                    
                                    self.status_signal.emit(
                                        f"  ✓ '{current_code}' → Cột '{target_col}': {price_value:,.0f}đ"
                                    )
                    
                    if cells_to_update:
                        self.status_signal.emit(f"  ⚡ Đang cập nhật {len(cells_to_update)} ô tại '{worksheet.title}'...")
                        worksheet.update_cells(cells_to_update, value_input_option='USER_ENTERED')
                        total_updated += len(cells_to_update)
                    
                except Exception as e:
                    self.status_signal.emit(f"  ✗ Lỗi khi xử lý sheet '{worksheet.title}': {str(e)}")
                    continue
            
            self.progress_signal.emit(100, "Hoàn thành!")
            self.status_signal.emit(f"✅ Hoàn thành! Đã cập nhật {total_updated} ô")
            
            self.finished_signal.emit(
                True, 
                f"Đồng bộ thành công! Cập nhật {total_updated} ô từ {len(data_dict)} mã máy."
            )
            
        except FileNotFoundError:
            self.finished_signal.emit(False, "Không tìm thấy file credentials! Vui lòng kiểm tra đường dẫn.")
        except gspread.exceptions.SpreadsheetNotFound as e:
            self.finished_signal.emit(False, f"Không tìm thấy Google Sheet! {str(e)}")
        except Exception as e:
            self.finished_signal.emit(False, f"Đã xảy ra lỗi: {str(e)}")

