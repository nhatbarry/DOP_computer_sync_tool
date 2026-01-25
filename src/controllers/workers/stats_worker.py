"""
Statistics Data Worker - Fetch data for statistics charts
"""
from PyQt5.QtCore import QThread, pyqtSignal
import gspread
import pandas as pd
import numpy as np


class StatsDataWorker(QThread):
    """Worker thread to load statistics data from Google Sheets"""
    finished_signal = pyqtSignal(list, list)  # buyers, order_counts
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
                        # Use get_all_values to handle duplicate headers
                        values = ws.get_all_values()
                        if values and len(values) > 1:
                            # Make column names unique by adding suffix for duplicates
                            headers = values[0]
                            unique_headers = []
                            seen = {}
                            for h in headers:
                                if h in seen:
                                    seen[h] += 1
                                    unique_headers.append(f"{h}_{seen[h]}")
                                else:
                                    seen[h] = 0
                                    unique_headers.append(h)
                            
                            df_temp = pd.DataFrame(values[1:], columns=unique_headers)
                            all_data.append(df_temp)
                    except Exception:
                        continue
                df = pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()
            else:
                worksheet = sale_sheet.worksheet(self.sheet_name)
                values = worksheet.get_all_values()
                if values and len(values) > 1:
                    headers = values[0]
                    unique_headers = []
                    seen = {}
                    for h in headers:
                        if h in seen:
                            seen[h] += 1
                            unique_headers.append(f"{h}_{seen[h]}")
                        else:
                            seen[h] = 0
                            unique_headers.append(h)
                    
                    df = pd.DataFrame(values[1:], columns=unique_headers)
                else:
                    df = pd.DataFrame()
            
            if df.empty:
                self.finished_signal.emit([], [])
                return
            
            # === DATA CLEANING (From notebook) ===
            
            # 1. Chuẩn hóa header (strip whitespace)
            df.columns = df.columns.str.strip()
            
            # 2. Xử lý số liệu (convert to numeric)
            cols_to_numeric = ['Chuyển khoản', 'COD']
            for col in cols_to_numeric:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.replace(',', '').str.replace('.', '')
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # 3. Xử lý Text (Người mua) - title case and strip
            if 'Người mua' in df.columns:
                df['Người mua'] = df['Người mua'].astype(str).str.title().str.strip()
            
            # 4. Forward Fill cho các cột (fill missing values)
            cols_to_ffill = ['Người mua', 'Ngày bán', 'Tên máy']
            for col in cols_to_ffill:
                if col in df.columns:
                    df[col] = df[col].replace(r'^\s*$', np.nan, regex=True).ffill()
            
            # 5. Reset Index
            df = df.reset_index(drop=True)
            
            # 6. Xóa dữ liệu thừa (dựa vào cột STT)
            if 'STT' in df.columns:
                condition = (df['STT'].isnull()) | (df['STT'].astype(str).str.strip() == '')
                cols_to_clean = ['Ngày bán', 'Người mua', 'Tên máy']
                valid_cols = [c for c in cols_to_clean if c in df.columns]
                df.loc[condition, valid_cols] = np.nan
            
            # 7. Remove rows with no 'Người mua'
            if 'Người mua' not in df.columns:
                self.error_signal.emit("Không tìm thấy cột 'Người mua'")
                return
            
            df = df.dropna(subset=['Người mua'])
            df = df[df['Người mua'].astype(str).str.strip() != '']
            
            if df.empty:
                self.finished_signal.emit([], [])
                return
            
            # Count values and sort in descending order (most orders first)
            df_result = df['Người mua'].value_counts().sort_values(ascending=False)
            buyers = list(df_result.index)
            order_counts = list(df_result.values)
            
            self.finished_signal.emit(buyers, order_counts)
            
        except Exception as e:
            self.error_signal.emit(str(e))
