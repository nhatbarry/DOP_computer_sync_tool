"""
Main Sync Worker - Background thread for main synchronization (Sale data to Stock sheets)
"""
from PyQt5.QtCore import QThread, pyqtSignal
import gspread
from gspread.cell import Cell
import pandas as pd


class MainSyncWorker(QThread):
    """
    Worker thread for main synchronization (Sale data to Stock sheets)
    """
    progress_signal = pyqtSignal(int, str)
    status_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    
    def __init__(self, credentials_path, sheet_may_ton, sheet_don_hang):
        super().__init__()
        self.credentials_path = credentials_path
        self.sheet_may_ton = sheet_may_ton
        self.sheet_don_hang = sheet_don_hang
    
    def run(self):
        """Run main sync in background"""
        try:
            self.status_signal.emit("Đang kết nối Google Sheets...")
            
            gc = gspread.service_account(filename=self.credentials_path)
            stock_sheet = gc.open(self.sheet_may_ton)
            sale_sheet = gc.open(self.sheet_don_hang)
            
            list_stock_sheets = stock_sheet.worksheets()
            list_sale_sheets = sale_sheet.worksheets()
            
            self.status_signal.emit(f"✓ Đã kết nối. Tìm thấy {len(list_sale_sheets)} sheet đơn hàng và {len(list_stock_sheets)} sheet máy tồn")
            
            com_id_header = 'mã máy'
            cod_header = 'cod'
            bank_header = 'chuyển khoản'
            
            data = []
            
            self.status_signal.emit("Đang quét dữ liệu đơn hàng...")
            
            for idx, sheet in enumerate(list_sale_sheets):
                self.progress_signal.emit(
                    int((idx / len(list_sale_sheets)) * 50),
                    f"Đang quét sheet đơn hàng: {sheet.title}"
                )
                
                try:
                    values = sheet.get_all_values()
                    if not values:
                        continue
                    
                    df = pd.DataFrame(values[1:], columns=values[0])
                    df.columns = df.columns.str.strip().str.lower()
                    
                    if com_id_header not in df.columns:
                        self.status_signal.emit(f"  ⚠ Sheet '{sheet.title}': Không có cột 'Mã máy'")
                        continue
                    
                    df[com_id_header] = df[com_id_header].astype(str).str.strip().str.upper()
                    
                    if bank_header in df.columns:
                        df[bank_header] = pd.to_numeric(df[bank_header], errors='coerce').fillna(0)
                    else:
                        df[bank_header] = 0
                    
                    if cod_header in df.columns:
                        df[cod_header] = pd.to_numeric(df[cod_header], errors='coerce').fillna(0)
                    else:
                        df[cod_header] = 0
                    
                    for index, row in df.iterrows():
                        ma = str(row[com_id_header]).strip().upper()
                        if not ma:
                            continue
                        
                        money_bank = row[bank_header]
                        money_cod = row[cod_header]
                        total_price = money_bank + money_cod
                        
                        data.append([ma, total_price, money_bank, money_cod, sheet.title])
                
                except Exception as e:
                    self.status_signal.emit(f"  ✗ Lỗi khi xử lý sheet '{sheet.title}': {str(e)}")
                    continue
            
            data_df = pd.DataFrame(data, columns=['mã máy', 'giá', 'chuyển khoản', 'cod', 'sheet_name'])
            data_df.drop_duplicates(subset=['mã máy'], keep='last', inplace=True)
            
            self.status_signal.emit(f"✓ Đã tìm thấy {len(data_df)} đơn hàng")
            
            self.status_signal.emit("Đang cập nhật vào file máy tồn...")
            
            sale_kw = 'sale'
            code_kw = 'mã máy'
            price_kw = 'giá bán'
            
            total_updated = 0
            
            for idx, sheet in enumerate(list_stock_sheets):
                self.progress_signal.emit(
                    50 + int((idx / len(list_stock_sheets)) * 50),
                    f"Đang cập nhật sheet: {sheet.title}"
                )
                
                try:
                    header = sheet.row_values(1)
                    clean_header = [str(h).strip().lower() for h in header]
                    
                    try:
                        sale_idx = clean_header.index(sale_kw) + 1
                        lap_code_idx = clean_header.index(code_kw) + 1
                        price_idx = clean_header.index(price_kw) + 1
                    except ValueError:
                        self.status_signal.emit(f"  ⚠ Sheet '{sheet.title}': Thiếu cột Sale/Mã máy/Giá bán. Bỏ qua.")
                        continue
                    
                    customer_idx = None
                    try:
                        for cust_kw in ['khách mua', 'khach mua', 'customer', 'buyer']:
                            if cust_kw in clean_header:
                                customer_idx = clean_header.index(cust_kw) + 1
                                break
                    except ValueError:
                        pass
                    
                    code_list_raw = sheet.col_values(lap_code_idx)
                    cells_to_update = []
                    
                    for i, code_val in enumerate(code_list_raw):
                        current_code = str(code_val).strip().upper()
                        
                        if current_code in data_df['mã máy'].values:
                            real_row = i + 1
                            row_data = data_df.loc[data_df['mã máy'] == current_code].iloc[0]
                            price_val = row_data['giá']
                            cod_val = row_data['cod']
                            bank_val = row_data['chuyển khoản']
                            sheet_name = row_data['sheet_name']
                            
                            if cod_val == 0 and bank_val == 0:
                                cells_to_update.append(Cell(real_row, sale_idx, 'Available'))
                                cells_to_update.append(Cell(real_row, price_idx, ''))
                            else:
                                cells_to_update.append(Cell(real_row, sale_idx, 'SOLD'))
                                cells_to_update.append(Cell(real_row, price_idx, float(price_val)))
                            
                            if customer_idx:
                                cells_to_update.append(Cell(real_row, customer_idx, sheet_name))
                    
                    if cells_to_update:
                        self.status_signal.emit(f"  ⚡ Đang cập nhật {len(cells_to_update)} ô tại '{sheet.title}'...")
                        sheet.update_cells(cells_to_update, value_input_option='USER_ENTERED')
                        total_updated += len(cells_to_update)
                
                except Exception as e:
                    self.status_signal.emit(f"  ✗ Lỗi khi xử lý sheet '{sheet.title}': {str(e)}")
                    continue
            
            self.progress_signal.emit(100, "Hoàn thành!")
            self.status_signal.emit(f"✅ Hoàn thành! Đã cập nhật {total_updated} ô")
            
            self.finished_signal.emit(True, f"Đồng bộ thành công! Cập nhật {total_updated} ô từ {len(data_df)} đơn hàng.")
            
        except FileNotFoundError:
            self.finished_signal.emit(False, "Không tìm thấy file credentials! Vui lòng kiểm tra đường dẫn.")
        except gspread.exceptions.SpreadsheetNotFound as e:
            self.finished_signal.emit(False, f"Không tìm thấy Google Sheet! Vui lòng kiểm tra tên sheet: {str(e)}")
        except Exception as e:
            self.finished_signal.emit(False, f"Đã xảy ra lỗi: {str(e)}")
