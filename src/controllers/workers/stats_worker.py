"""
Statistics Data Worker - Fetch data for statistics charts
"""
from PyQt5.QtCore import QThread, pyqtSignal
import gspread
import pandas as pd


class StatsDataWorker(QThread):
    """Worker thread to load statistics data from Google Sheets"""
    finished_signal = pyqtSignal(list, list, list, float, float)
    error_signal = pyqtSignal(str)
    
    def __init__(self, credentials_path, sheet_id, sheet_name):
        super().__init__()
        self.credentials_path = credentials_path
        self.sheet_id = sheet_id
        self.sheet_name = sheet_name
    
    def run(self):
        try:
            gc = gspread.service_account(filename=self.credentials_path)
            sale_sheet = gc.open(self.sheet_id)
            
            if self.sheet_name == "Tất cả":
                all_data = []
                for ws in sale_sheet.worksheets():
                    try:
                        data = ws.get_all_records()
                        if data:
                            all_data.extend(data)
                    except Exception:
                        continue
                df = pd.DataFrame(all_data)
            else:
                worksheet = sale_sheet.worksheet(self.sheet_name)
                data = worksheet.get_all_records()
                df = pd.DataFrame(data)
            
            if df.empty:
                self.finished_signal.emit([], [], [], 0, 0)
                return
            
            if 'Chuyển khoản' not in df.columns or 'COD' not in df.columns:
                self.error_signal.emit("Không tìm thấy cột 'Chuyển khoản' hoặc 'COD'")
                return
            
            df['Chuyển khoản'] = pd.to_numeric(df['Chuyển khoản'], errors='coerce').fillna(0)
            df['COD'] = pd.to_numeric(df['COD'], errors='coerce').fillna(0)
            
            if 'Ngày bán' in df.columns:
                df = df[df['Ngày bán'].astype(str).str.strip() != '']
                df = df.dropna(subset=['Ngày bán'])
                
                if df.empty:
                    self.finished_signal.emit([], [], [], 0, 0)
                    return
                
                df_result = df.groupby('Ngày bán')[['Chuyển khoản', 'COD']].sum()
                x_data = list(df_result.index)
                y1_data = list(df_result['Chuyển khoản'])
                y2_data = list(df_result['COD'])
            else:
                x_data = ['Tổng']
                y1_data = [df['Chuyển khoản'].sum()]
                y2_data = [df['COD'].sum()]
            
            total_ck = sum(y1_data)
            total_cod = sum(y2_data)
            
            self.finished_signal.emit(x_data, y1_data, y2_data, total_ck, total_cod)
            
        except Exception as e:
            self.error_signal.emit(str(e))
