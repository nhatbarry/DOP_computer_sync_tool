import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class Canvas(FigureCanvas):
    def __init__(self, parent):
        self.fig = Figure(figsize=(10, 20))
        self.ax = self.fig.add_subplot(111)
        
        super().__init__(self.fig)
        self.setParent(parent)
        
        self.ax.set_title('Chọn sheet để xem biểu đồ')
        self.ax.set_xlabel('Số lượng')
        self.ax.set_ylabel('Tên người mua')
    
    def update_chart(self, buyers, order_counts):
        """Update chart with buyer order counts (horizontal bar chart like notebook)"""
        self.ax.clear()
        
        if len(buyers) == 0:
            self.ax.set_title('Không có dữ liệu')
            self.draw()
            return
        
        # Dynamically adjust figure height based on number of buyers
        # Each buyer needs about 0.4 inches of height
        min_height = 6  # Minimum height
        calculated_height = max(min_height, len(buyers) * 0.4)
        
        # Update figure size
        self.fig.set_size_inches(10, calculated_height)
        
        # Create horizontal bar chart like in notebook
        self.ax.barh(buyers, order_counts, color='skyblue')
        
        self.ax.set_title('Số lượng máy theo Người mua', pad=10)
        self.ax.set_xlabel('Số lượng')
        self.ax.set_ylabel('Tên người mua')
        self.ax.grid(axis='x', linestyle='--', alpha=0.7)
        
        self.fig.tight_layout(pad=1.5)
        self.draw()
        
        # Update minimum size for scroll area
        self.setMinimumHeight(int(calculated_height * 100))