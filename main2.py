import sys
import sqlite3
from PyQt6 import QtWidgets, uic


class AddEditCoffeeForm(QtWidgets.QDialog):
    """Форма для добавления и редактирования кофе"""
    def __init__(self, coffee_id=None, parent=None):
        super().__init__(parent)
        uic.loadUi('addEditCoffeeForm.ui', self)
        
        self.coffee_id = coffee_id
        self.conn = sqlite3.connect('coffee.sqlite')
        self.cursor = self.conn.cursor()
        
        # Подключаем сигналы кнопок
        self.saveButton.clicked.connect(self.save)
        self.cancelButton.clicked.connect(self.reject)
        
        # Если передан ID - загружаем данные для редактирования
        if self.coffee_id:
            self.setWindowTitle("Редактирование кофе")
            self.titleLabel.setText("Редактирование кофе")
            self.load_coffee_data()
        else:
            self.setWindowTitle("Добавление кофе")
            self.titleLabel.setText("Добавление кофе")
    
    def load_coffee_data(self):
        """Загружает данные кофе для редактирования"""
        self.cursor.execute('''
            SELECT sort_name, roast_degree, grind_type, 
                   taste_description, price, volume 
            FROM coffee WHERE id = ?
        ''', (self.coffee_id,))
        
        coffee = self.cursor.fetchone()
        if coffee:
            self.sortNameEdit.setText(coffee[0])
            # Устанавливаем значения в ComboBox
            roast_index = self.roastDegreeCombo.findText(coffee[1])
            if roast_index >= 0:
                self.roastDegreeCombo.setCurrentIndex(roast_index)
            
            grind_index = self.grindTypeCombo.findText(coffee[2])
            if grind_index >= 0:
                self.grindTypeCombo.setCurrentIndex(grind_index)
            
            self.tasteDescriptionEdit.setText(coffee[3])
            self.priceSpin.setValue(coffee[4])
            self.volumeSpin.setValue(coffee[5])
    
    def save(self):
        """Сохраняет данные (добавление или редактирование)"""
        sort_name = self.sortNameEdit.text().strip()
        roast_degree = self.roastDegreeCombo.currentText()
        grind_type = self.grindTypeCombo.currentText()
        taste_description = self.tasteDescriptionEdit.toPlainText().strip()
        price = self.priceSpin.value()
        volume = self.volumeSpin.value()
        
        # Проверка обязательных полей
        if not sort_name:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Название сорта обязательно!")
            return
        
        if price <= 0:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Цена должна быть больше 0!")
            return
        
        if volume <= 0:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Объем должен быть больше 0!")
            return
        
        try:
            if self.coffee_id:
                # Обновление существующей записи
                self.cursor.execute('''
                    UPDATE coffee 
                    SET sort_name = ?, roast_degree = ?, grind_type = ?,
                        taste_description = ?, price = ?, volume = ?
                    WHERE id = ?
                ''', (sort_name, roast_degree, grind_type, taste_description, 
                      price, volume, self.coffee_id))
            else:
                # Добавление новой записи
                self.cursor.execute('''
                    INSERT INTO coffee (sort_name, roast_degree, grind_type, 
                                       taste_description, price, volume)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (sort_name, roast_degree, grind_type, taste_description, 
                      price, volume))
            
            self.conn.commit()
            QtWidgets.QMessageBox.information(self, "Успех", 
                "Кофе успешно добавлен!" if not self.coffee_id else "Кофе успешно обновлен!")
            self.accept()
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {str(e)}")
    
    def closeEvent(self, event):
        """Закрывает соединение с БД"""
        if self.conn:
            self.conn.close()
        event.accept()


class CoffeeApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        
        # Подключение к базе данных
        self.conn = sqlite3.connect('coffee.sqlite')
        self.cursor = self.conn.cursor()
        
        # Подключаем сигналы кнопок
        self.addButton.clicked.connect(self.add_coffee)
        self.editButton.clicked.connect(self.edit_coffee)
        self.deleteButton.clicked.connect(self.delete_coffee)
        
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
        self.tableWidget.setSelectionBehavior(QtWidgets.QTableWidget.SelectionBehavior.SelectRows)
        self.tableWidget.setSelectionMode(QtWidgets.QTableWidget.SelectionMode.SingleSelection)
    
    def add_coffee(self):
        """Открывает форму для добавления нового кофе"""
        dialog = AddEditCoffeeForm(parent=self)
        if dialog.exec() == 1:  # QDialog.DialogCode.Accepted
            self.load_coffee_data()  # Перезагружаем данные
    
    def edit_coffee(self):
        """Открывает форму для редактирования выбранного кофе"""
        current_row = self.tableWidget.currentRow()
        
        if current_row < 0:
            QtWidgets.QMessageBox.warning(self, "Внимание", 
                "Выберите запись для редактирования!")
            return
        
        # Получаем ID выбранной записи
        id_item = self.tableWidget.item(current_row, 0)
        if id_item:
            coffee_id = int(id_item.text())
            dialog = AddEditCoffeeForm(coffee_id=coffee_id, parent=self)
            if dialog.exec() == 1:  # QDialog.DialogCode.Accepted
                self.load_coffee_data()  # Перезагружаем данные
    
    def delete_coffee(self):
        """Удаляет выбранную запись о кофе"""
        current_row = self.tableWidget.currentRow()
        
        if current_row < 0:
            QtWidgets.QMessageBox.warning(self, "Внимание", 
                "Выберите запись для удаления!")
            return
        
        # Получаем ID выбранной записи
        id_item = self.tableWidget.item(current_row, 0)
        if id_item:
            coffee_id = int(id_item.text())
            
            # Подтверждение удаления
            reply = QtWidgets.QMessageBox.question(
                self, "Подтверждение",
                f"Вы действительно хотите удалить кофе с ID {coffee_id}?",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                QtWidgets.QMessageBox.StandardButton.No
            )
            
            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                try:
                    self.cursor.execute('DELETE FROM coffee WHERE id = ?', (coffee_id,))
                    self.conn.commit()
                    QtWidgets.QMessageBox.information(self, "Успех", "Запись удалена!")
                    self.load_coffee_data()
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении: {str(e)}")
    
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
