import sys
from PyQt6.QtWidgets import QApplication, QWidget, QProgressBar, QHBoxLayout, QPushButton, QVBoxLayout, QStyleFactory, QLabel
from PyQt6.QtCore import Qt

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Triple Progress Bars")
        self.resize(400, 200)

        # Create three progress bars
        self.progress_bar_top = QProgressBar(self)  # Top progress bar
        self.label_today = QLabel('I am here waiting for you')
        self.progress_bar1 = QProgressBar(self)    # Bottom left
        self.progress_bar2 = QProgressBar(self)    # Bottom right

        self.progress_bar_top.setStyleSheet("QProgressBar::chunk { background-color: #ef4444; } QProgressBar { border: 1px solid #ccc; }")
        self.progress_bar1.setStyleSheet("QProgressBar::chunk { background-color: #3b82f6; } QProgressBar { border: 1px solid #ccc; }")
        self.progress_bar2.setStyleSheet("QProgressBar::chunk { background-color: #10b981; } QProgressBar { border: 1px solid #ccc; }")

        # Set maximum values
        self.progress_bar_top.setMaximum(100)  # Top: full length 100
        self.progress_bar1.setMaximum(40)      # Bottom left: full length 40
        self.progress_bar2.setMaximum(60)      # Bottom right: full length 60
        
        # Set initial values
        self.progress_bar_top.setValue(0)
        self.progress_bar1.setValue(0)
        self.progress_bar2.setValue(0)
        self.progress_bar_top.setTextVisible(False)
        self.progress_bar1.setTextVisible(False)
        self.progress_bar2.setTextVisible(False)
        
        # Set widths
        self.progress_bar_top.setFixedWidth(400)   # Full window width
        self.progress_bar1.setFixedWidth(160)      # 40/100 * 400
        self.progress_bar2.setFixedWidth(240)      # 60/100 * 400
        
        # Create horizontal layout for bottom progress bars
        h_layout_bottom = QHBoxLayout()
        h_layout_bottom.addWidget(self.progress_bar1)
        h_layout_bottom.addWidget(self.progress_bar2)
        h_layout_bottom.setSpacing(0)  # No spacing between bottom progress bars
        h_layout_bottom.setContentsMargins(0, 0, 0, 0)  # No margins
        
        # Create horizontal layout for top progress bar
        h_layout_top = QHBoxLayout()
        h_layout_top.addWidget(self.progress_bar_top)
        h_layout_top.setContentsMargins(0, 0, 0, 0)  # No margins
        
        # Create main vertical layout
        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout_top)      # Top progress bar
        v_layout.addWidget(self.label_today)
        v_layout.addLayout(h_layout_bottom)   # Bottom progress bars
        v_layout.setSpacing(0)  # No spacing between top and bottom layouts
        v_layout.setContentsMargins(0, 0, 0, 0)  # No margins
        
        # Create button to simulate progress
        self.button = QPushButton("Update Progress", self)
        self.button.clicked.connect(self.update_progress)
        
        # Add button to main layout
        v_layout.addWidget(self.button)
        v_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.setLayout(v_layout)
        
        # Progress counter (percentage-based)
        self.progress_percent = 0

    def update_progress(self):
        self.progress_percent += 10
        if self.progress_percent > 100:
            self.progress_percent = 0
        # Scale progress to respective maximums
        self.progress_bar_top.setValue(self.progress_percent)
        self.progress_bar1.setValue(int(self.progress_percent * 40 / 100))
        self.progress_bar2.setValue(int(self.progress_percent * 60 / 100))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())