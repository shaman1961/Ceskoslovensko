import sqlite3

# Создаем базу данных
conn = sqlite3.connect('coffee.sqlite')
cursor = conn.cursor()

# Создаем таблицу coffee
cursor.execute('''
    CREATE TABLE IF NOT EXISTS coffee (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sort_name TEXT NOT NULL,
        roast_degree TEXT NOT NULL,
        grind_type TEXT NOT NULL,
        taste_description TEXT,
        price INTEGER NOT NULL,
        volume INTEGER NOT NULL
    )
''')

# Добавляем тестовые данные
coffee_data = [
    ('Арабика Эфиопия', 'Средняя', 'В зернах', 'Фруктовый вкус с нотками ягод', 450, 250),
    ('Робуста Уганда', 'Темная', 'Молотый', 'Насыщенный вкус с горчинкой', 350, 250),
    ('Арабика Колумбия', 'Светлая', 'В зернах', 'Мягкий вкус с кислинкой', 520, 500),
    ('Эспрессо смесь', 'Темная', 'Молотый', 'Крепкий насыщенный вкус', 380, 250),
    ('Арабика Бразилия', 'Средняя', 'В зернах', 'Шоколадный вкус с ореховыми нотками', 480, 500),
    ('Капучино смесь', 'Средняя', 'Молотый', 'Сбалансированный мягкий вкус', 420, 250),
    ('Арабика Кения', 'Средняя', 'В зернах', 'Яркий вкус с винной кислинкой', 650, 250),
]

cursor.executemany('''
    INSERT INTO coffee (sort_name, roast_degree, grind_type, taste_description, price, volume)
    VALUES (?, ?, ?, ?, ?, ?)
''', coffee_data)

conn.commit()
conn.close()

print("База данных coffee.sqlite создана успешно!")
