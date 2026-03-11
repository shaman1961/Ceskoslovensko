import sys
import sqlite3
from PyQt6 import QtWidgets, uic


class CoffeeApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        
        # Подключение к базе данных
        self.conn = sqlite3.connect('coffee.sqlite')
        self.cursor = self.conn.cursor()
        
        # Загрузка данных
        self.load_coffee_data()
    
    def load_coffee_data(self):
        """Загружает данные о кофе из базы данных в таблицу"""
        self.cursor.execute('''
            SELECT id, sort_name, roast_degree, grind_type, 
                   taste_description, price, volume 
            FROM coffee
        ''')
        
        coffee_list = self.cursor.fetchall()
        
        # Устанавливаем количество строк
        self.tableWidget.setRowCount(len(coffee_list))
        
        # Заполняем таблицу
        for row_idx, coffee in enumerate(coffee_list):
            for col_idx, value in enumerate(coffee):
                item = QtWidgets.QTableWidgetItem(str(value))
                self.tableWidget.setItem(row_idx, col_idx, item)
        
        # Настройка таблицы
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.resizeColumnsToContents()
    
    def closeEvent(self, event):
        """Закрывает соединение с БД при закрытии приложения"""
        if self.conn:
            self.conn.close()
        event.accept()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = CoffeeApp()
    window.show()
    sys.exit(app.exec())
