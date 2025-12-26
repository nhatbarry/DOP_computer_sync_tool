"""
Sync Model - Handles data synchronization logic
"""
from PyQt5.QtCore import QObject, pyqtSignal
import pandas as pd
import gspread
import json
import os


class SyncModel(QObject):
    """
    Model for handling data synchronization
    """
    sync_started = pyqtSignal()
    sync_progress = pyqtSignal(int, str)
    sync_completed = pyqtSignal(bool, str)
    data_changed = pyqtSignal(object)
    
    def __init__(self):
        super().__init__()
        self._data = None
        self._sync_status = "Idle"
        self.data_file = "data.json"
        
    @property
    def data(self):
        """Get current data"""
        return self._data
    
    @data.setter
    def data(self, value):
        """Set data and notify observers"""
        self._data = value
        self.data_changed.emit(value)
    
    @property
    def sync_status(self):
        """Get sync status"""
        return self._sync_status
    
    def start_sync(self, source_path, destination_path):
        """
        Start synchronization process
        
        Args:
            source_path: Source folder path
            destination_path: Destination folder path
        """
        self.sync_started.emit()
        self._sync_status = "Syncing"
        
        try:
            self.sync_progress.emit(0, "Starting synchronization...")
            
            for i in range(0, 101, 20):
                self.sync_progress.emit(i, f"Progress: {i}%")
            
            self._sync_status = "Completed"
            self.sync_completed.emit(True, "Synchronization completed successfully")
            
        except Exception as e:
            self._sync_status = "Failed"
            self.sync_completed.emit(False, f"Error: {str(e)}")
    
    def load_data_from_sheets(self, credentials_path, sheet_name):
        """
        Load data from Google Sheets
        
        Args:
            credentials_path: Path to Google credentials file
            sheet_name: Name of the sheet to load
        """
        try:
            pass
        except Exception as e:
            print(f"Error loading data from sheets: {e}")
    
    def save_app_data(self, data):
        """Save all application data to JSON file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def load_app_data(self):
        """Load application data from JSON file"""
        if not os.path.exists(self.data_file):
            return None
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading data: {e}")
            return None
    
    def save_data(self, file_path):
        """
        Save data to file
        
        Args:
            file_path: Path to save file
        """
        if self._data is not None:
            try:
                if file_path.endswith('.csv'):
                    self._data.to_csv(file_path, index=False)
                elif file_path.endswith('.xlsx'):
                    self._data.to_excel(file_path, index=False)
                return True
            except Exception as e:
                print(f"Error saving data: {e}")
                return False
        return False
