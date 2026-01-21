import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class Canvas(FigureCanvas):
    def __init__(self, parent):
        self.fig = Figure(figsize=(10, 6))
        self.ax = self.fig.add_subplot(111)
        
        super().__init__(self.fig)
        self.setParent(parent)
        
        self.ax.set_title('Chọn thời gian để xem biểu đồ')
        self.ax.set_xlabel('Ngày bán')
        self.ax.set_ylabel('Doanh thu')
    
    def update_chart(self, x_data, y1_data, y2_data, chart_type='bar'):
        """Update chart with new data"""
        self.ax.clear()
        
        if len(x_data) == 0:
            self.ax.set_title('Không có dữ liệu')
            self.draw()
            return
        
        x_pos = np.arange(len(x_data))
        width = 0.35
        
        if chart_type == 'Cột':
            self.ax.bar(x_pos - width/2, y1_data, width, label='Chuyển khoản', color='#3498db')
            self.ax.bar(x_pos + width/2, y2_data, width, label='COD', color='#e74c3c')
            self.ax.set_xticks(x_pos)
            self.ax.set_xticklabels(x_data, rotation=45, ha='right')
        elif chart_type == 'Đường':
            self.ax.plot(x_pos, y1_data, marker='o', label='Chuyển khoản', color='#3498db')
            self.ax.plot(x_pos, y2_data, marker='s', label='COD', color='#e74c3c')
            self.ax.set_xticks(x_pos)
            self.ax.set_xticklabels(x_data, rotation=45, ha='right')
        elif chart_type == 'Tròn':
            total_ck = sum(y1_data)
            total_cod = sum(y2_data)
            self.ax.pie([total_ck, total_cod], labels=['Chuyển khoản', 'COD'], 
                       colors=['#3498db', '#e74c3c'], autopct='%1.1f%%')
        elif chart_type == 'Thanh ngang':
            self.ax.barh(x_pos - width/2, y1_data, width, label='Chuyển khoản', color='#3498db')
            self.ax.barh(x_pos + width/2, y2_data, width, label='COD', color='#e74c3c')
            self.ax.set_yticks(x_pos)
            self.ax.set_yticklabels(x_data)
        
        self.ax.set_title('Doanh thu theo ngày')
        self.ax.set_xlabel('Ngày bán')
        self.ax.set_ylabel('Doanh thu (VNĐ)')
        self.ax.legend()
        
        self.fig.tight_layout()
        self.draw()