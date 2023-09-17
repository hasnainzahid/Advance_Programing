import io
import sys
import pandas as pd
import matplotlib.pyplot as plt
import requests  # Import the 'requests' library to fetch data from a URL
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QListWidget,
    QTableWidget, QTableWidgetItem, QAction, QLabel, QComboBox, QFileDialog, QInputDialog
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class DataVisualizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.details_table = None
        self.menu_data = None
        self.selected_item = None
        self.initUI()

    def initUI(self):
        # Set up the main application window
        self.setWindowTitle('McDonald\'s Menu Data Visualizer')
        self.setGeometry(100, 100, 1000, 800)

        # Create central widget and set the main layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # Create widgets
        load_data_button = QPushButton('Load Data')
        load_data_button.clicked.connect(self.load_data)
        
        load_data_url_button = QPushButton('Load Data from URL')
        load_data_url_button.clicked.connect(self.load_data_url)

        self.menu_list_widget = QListWidget()
        self.menu_list_widget.itemClicked.connect(self.display_item_details)

        # Create the details table
        self.details_table = QTableWidget()
        self.details_table.setColumnCount(13)
        self.details_table.setHorizontalHeaderLabels(["Item", "Calories", "Calories from Fat", "Total Fat (g)",
                                                      "Saturated Fat (g)", "Trans Fat (g)", "Cholesterol (mg)",
                                                      "Sodium (mg)", "Carbs (g)", "Fiber (g)", "Sugars (g)",
                                                      "Protein (g)", "Weight Watchers Pnts"])

        # Matplotlib chart
        self.figure, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)
        self.ax.set_title('Calories Comparison')

        # Combo box for chart type
        chart_type_label = QLabel('Select Chart Type:')
        chart_types = ['Bar Chart', 'Pie Chart']
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(chart_types)
        self.chart_type_combo.currentIndexChanged.connect(self.display_calories_comparison)

        # Add widgets to layout
        layout.addWidget(load_data_button)
        layout.addWidget(load_data_url_button)
        layout.addWidget(self.menu_list_widget)
        layout.addWidget(self.details_table)
        layout.addWidget(chart_type_label)
        layout.addWidget(self.chart_type_combo)
        layout.addWidget(self.canvas)

        central_widget.setLayout(layout)

        # Create a status bar and add it to the main window
        self.status_bar = self.statusBar()

        # Create a menu bar
        menubar = self.menuBar()

        # Create a file menu
        file_menu = menubar.addMenu('File')

        # Add actions
        save_action = QAction('Save Data', self)
        save_action.triggered.connect(self.save_data)
        file_menu.addAction(save_action)

        export_action = QAction('Export Graph', self)
        export_action.triggered.connect(self.export_graph)
        file_menu.addAction(export_action)

        clear_action = QAction('Clear Data and Graph', self)
        clear_action.triggered.connect(self.clear_data)
        file_menu.addAction(clear_action)

    def load_data(self):
        try:
            # Open a file dialog to select a local CSV file for data loading
            file_path, _ = QFileDialog.getOpenFileName(self, "Load Data", "", "CSV Files (*.csv);;All Files (*)")
            if file_path:
                # Read the CSV file into a pandas DataFrame
                self.menu_data = pd.read_csv(file_path)
                self.update_status_bar('Data loaded successfully!')
                self.display_menu_items()
            else:
                self.update_status_bar('Load operation canceled.')
        except Exception as e:
            self.update_status_bar(f'Error loading data: {str(e)}')

    def load_data_url(self):
        url, ok = QInputDialog.getText(self, 'Load Data from URL', 'Enter URL:')
        if ok and url:
            try:
                # Fetch data from the provided URL
                response = requests.get(url)
                if response.status_code == 200:
                    # Read the CSV content from the response into a pandas DataFrame
                    content = response.content.decode('utf-8')
                    self.menu_data = pd.read_csv(io.StringIO(content))
                    self.update_status_bar('Data loaded successfully from URL!')
                    self.display_menu_items()
                else:
                    self.update_status_bar('Failed to fetch data from URL.')
            except Exception as e:
                self.update_status_bar(f'Error loading data from URL: {str(e)}')
        else:
            self.update_status_bar('URL input canceled.')

    def display_menu_items(self):
        if self.menu_data is not None:
            items = self.menu_data['Item'].tolist()
            self.menu_list_widget.addItems(items)
        else:
            self.update_status_bar('Please load data first.')

    def display_item_details(self, item):
        if self.menu_data is not None:
            self.selected_item = item.text()
            item_details = self.menu_data[self.menu_data['Item'] == self.selected_item]
            self.display_details_in_table(item_details)
            self.display_calories_comparison()
        else:
            self.update_status_bar('Please load data first.')

    def display_details_in_table(self, item_details):
        self.details_table.setRowCount(0)
        if item_details.empty:
            return
        row_position = 0
        for _, row in item_details.iterrows():
            self.details_table.insertRow(row_position)
            for col_index, header in enumerate(item_details.columns):
                value = str(row[header])
                item = QTableWidgetItem(value)
                self.details_table.setItem(row_position, col_index, item)
            row_position += 1

    def display_calories_comparison(self):
        if self.menu_data is not None and self.selected_item is not None:
            selected_calories = self.menu_data[self.menu_data['Item'] == self.selected_item]['Calories'].values[0]
            other_items = self.menu_data[self.menu_data['Item'] != self.selected_item]
            other_calories = other_items['Calories']

        self.ax.clear()

        if self.chart_type_combo.currentText() == 'Bar Chart':
            labels = ['Selected Item', 'Other Items']
            x = range(len(labels))
            heights = [selected_calories, other_calories.mean()]
            self.ax.bar(x, heights, tick_label=labels)
            self.ax.set_ylabel('Calories')
            self.ax.set_title('Calories Comparison')

        elif self.chart_type_combo.currentText() == 'Pie Chart':
            labels = [self.selected_item, 'Other Items']
            sizes = [selected_calories, other_calories.mean()]
            explode = (0.1, 0)  # explode the 1st slice (i.e., 'Selected Item')
            self.ax.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                        shadow=True, startangle=140)
            self.ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            self.ax.set_title('Calories Comparison')
            self.ax.set_ylabel('Calories')

        self.canvas.draw()

    def update_status_bar(self, message):
        self.status_bar.showMessage(message)

    def save_data(self):
        if self.menu_data is not None:
            try:
                options = QFileDialog.Options()
                file_path, _ = QFileDialog.getSaveFileName(self, "Save Data", "", "CSV Files (*.csv);;All Files (*)",
                                                           options=options)
                if file_path:
                    self.menu_data.to_csv(file_path, index=False)
                    self.update_status_bar('Data saved successfully!')
                else:
                    self.update_status_bar('Save operation canceled.')
            except Exception as e:
                self.update_status_bar(f'Error while saving data: {str(e)}')
        else:
            self.update_status_bar('No data to save. Please load data first.')

    def export_graph(self):
        if self.menu_data is not None and self.selected_item is not None:
            try:
                options = QFileDialog.Options()
                file_path, _ = QFileDialog.getSaveFileName(self, "Export Graph", "", "PNG Files (*.png);;All Files (*)",
                                                           options=options)
                if file_path:
                    self.canvas.print_png(file_path)
                    self.update_status_bar('Graph exported successfully!')
                else:
                    self.update_status_bar('Export operation canceled.')
            except Exception as e:
                self.update_status_bar(f'Error while exporting graph: {str(e)}')
        else:
            self.update_status_bar('No data or graph to export. Please load data and select an item first.')

    def clear_data(self):
        self.menu_data = None
        self.menu_list_widget.clear()
        self.details_table.setRowCount(0)
        self.ax.clear()
        self.canvas.draw()
        self.update_status_bar('Data and Graph cleared successfully!')


if __name__ == '__main__':
    # Initialize the PyQt application and display the main window
    app = QApplication(sys.argv)
    window = DataVisualizerApp()
    window.show()
    sys.exit(app.exec_())
