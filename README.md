# Установка и настройка PostgreSQL для проекта

## 1. Установка PostgreSQL 14.17

1. Скачайте PostgreSQL 14.17 с официального сайта:
   [PostgreSQL 14.17](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads)

2. Установите PostgreSQL, следуя инструкциям установщика.

## 2. Создание базы данных и пользователя

После установки создайте базу данных и пользователя с следующими параметрами (они используются в скриптах проекта):

- "dbname": "postgres",
- "user": "postgres",
- "password": "qwerty123!",
- "host": "localhost",
- "port": "5432"

## 3. База данных из дампа

Используйте файл `dump.sql` для создания структуры базы данных и таблиц.

Вы можете выполнить дамп через:

- DBeaver (импорт SQL-скрипта)

## 4. Структура базы данных

Основные таблицы:

- objects - объекты

- object_estimates - объектные сметы

- local_estimates - локальные сметы

- sections - разделы

- work - работы

- materials - материалы

Схема отношений между таблицами представлена в SQL-дампе.

## 5. Рекомендуемые инструменты

Для удобного управления базой данных рекомендуется использовать [DBeaver](https://dbeaver.io/).

## 6. Скрипты, использующие эту базу данных

- files_parsing.py

- parsing_object_smeta.py

- db_q_2.py

# Файлы проекта (скрипты)

# File Type Identifier (`type_opr.py`)

Этот скрипт определяет тип файла по его сигнатуре (первым байтам содержимого).

## Поддерживаемые форматы
- **GGE** (файлы с сигнатурой `GGE ` или XML-файлы с расширением `.gge`)
- **XLSX** (файлы Microsoft Excel, сигнатура `PK\x03\x04`)
- **XLS** (старый формат Excel, сигнатура `\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1`)
- **XML** (файлы, начинающиеся с `<?xml `)
- Другие файлы будут помечены как "Неизвестный формат"

# Парсер объектных смет `parsing_object_smeta.py`

![Python](https://img.shields.io/badge/Python-3.6%2B-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13%2B-blue)
![Pandas](https://img.shields.io/badge/Pandas-1.0%2B-orange)

Скрипт для автоматического парсинга Excel-файлов с объектными сметами и сохранения данных в PostgreSQL.

## 🛠 Функциональность
- Автоматическое извлечение данных из Excel-файлов смет:
  - Название объекта строительства
  - Наименование объектной сметы
  - Сметная стоимость (с автоматическим преобразованием в числовой формат)
  - Список локальных смет
- Валидация и преобразование данных
- Сохранение в реляционную БД PostgreSQL

## ⚠️ Ограничения
1. Формат Excel-файлов должен соответствовать ожидаемой структуре

2. Для работы требуется точное совпадение ключевых фраз:

- "на строительство"

- "(объектная смета)"

- "Сметная стоимость"

- "Локальные сметы (расчеты)"

3. Поддерживаются только файлы .xlsx (Excel 2007+)

# XML Parser для смет в PostgreSQL `parsing_xml_db.py`

Скрипт для парсинга XML-файлов смет и сохранения данных в PostgreSQL.

## Функциональность

- Парсинг XML-файлов смет
- Сохранение данных в PostgreSQL:
  - Разделы сметы
  - Работы (ФЕР/ТЕР)
    - стоимость работы
    - ед-изм
  - Материалы (ФССЦ/ТССЦ)
      - стоимость работы
      - ед-изм
  - Общая стоимость сметы
- Валидация данных и тестирование

## Обработка ошибок

Скрипт обрабатывает:

- Ошибки парсинга XML

- Ошибки подключения к БД

- Ошибки целостности данных

Все операции с БД выполняются в транзакциях с откатом при ошибках.

# Обработчик строительных смет `files_parsing.py`

Программа для обработки объектных и локальных строительных смет в различных форматах (XLSX, XML и др.) с сохранением данных в PostgreSQL.

## Функционал

- Загрузка файлов через интерфейс (перетаскивание или выбор в диалоге)
- Определение типа файла (XLSX, XML и др.)
- Обработка объектных смет (XLSX)
- Обработка локальных смет (XML)
- Хранение данных в PostgreSQL
- Просмотр списка необработанных смет

## Использование

Вкладка "Объектные сметы":

Перетащите или выберите файл объектной сметы (XLSX)

Нажмите "Обработать объектную смету"

Вкладка "Локальные сметы":

Выберите смету из списка

Перетащите или выберите XML файл локальной сметы

Нажмите "Обработать локальную смету"

## Структура проекта

- files_parsing.py - основной файл с GUI интерфейсом

- parsing_object_smeta.py - обработка объектных смет (XLSX)

- parsing_xml_db.py - обработка XML смет

- type_opr.py - определение типа файла

# Запросы

# SQL-запросы для анализа данных смет

Файл `request_1.sql` содержит два SQL-запроса для анализа данных из базы данных сметных расчетов.

## Запрос 1.1: Анализ работ

```sql
SELECT 
    w.name_work AS work_name,
    COUNT(*) AS total_occurrences,
    COUNT(DISTINCT le.id) AS distinct_estimates_count
FROM 
    work w
JOIN 
    sections s ON w.local_section_id = s.id
JOIN 
    local_estimates le ON s.estimate_id = le.id
GROUP BY 
    w.name_work
ORDER BY 
    total_occurrences DESC;
```

### Назначение:

Анализирует частоту использования различных видов работ в сметах.

### Возвращаемые данные:

- work_name - название работы

- total_occurrences - общее количество упоминаний работы

- distinct_estimates_count - количество уникальных смет, где встречается эта работа

Сортировка: по убыванию общего количества упоминаний.

## Запрос 1.2: Анализ материалов

```sql

SELECT 
    m.name_material AS material_name,
    COUNT(*) AS total_occurrences,
    COUNT(DISTINCT le.id) AS distinct_estimates_count
FROM 
    materials m
JOIN 
    work w ON m.work_id = w.id
JOIN 
    sections s ON w.local_section_id = s.id
JOIN 
    local_estimates le ON s.estimate_id = le.id
GROUP BY 
    m.name_material
ORDER BY 
    total_occurrences DESC;
```

### Назначение:

Анализирует частоту использования различных материалов в сметах.

### Возвращаемые данные:

- material_name - название материала

- total_occurrences - общее количество упоминаний материала

- distinct_estimates_count - количество уникальных смет, где встречается этот материал

Сортировка: по убыванию общего количества упоминаний.

# Запрос 2. Скрипт для расчета процентов АР и КР в сметах `db_q_2.py`

## Назначение

Скрипт `db_q_2.py` выполняет запрос к PostgreSQL базе данных для расчета процентного соотношения стоимости:

- Архитектурных решений (АР)
- Конструктивных решений (КР)
к общей стоимости объектов.

## Логика работы

- Скрипт подключается к базе данных PostgreSQL

- Выполняет сложный SQL-запрос, который:

- Считает сумму стоимостей АР по каждому объекту

- Считает сумму стоимостей КР по каждому объекту

- Рассчитывает общую стоимость каждого объекта

- Вычисляет процентное соотношение АР и КР к общей стоимости

- Выводит результаты в виде таблицы

## Особенности запроса

Запрос использует:

- CTE (Common Table Expressions) для промежуточных расчетов

- ILIKE для поиска по шаблонам в названиях смет

- NULLIF для избежания деления на ноль

- Округление результатов до 2 знаков после запятой

## Категории смет

1. Архитектурные решения (АР):

- Архитектурные решения

- Кровля и кладка

- Витражи

- Отделочные работы

2. Конструктивные решения (КР):

- Конструктивные решения

- Конструкции железобетонные

- Конструктивные и объемно-планировочные решения

- Конструкции металлические

- Железобетонные,металлические конструкции

- Конструкции деревянные

- Железобетонные конструкции

# ДОП Папка (для тестирование парсинга xml)

Этот скрипт предназначен для парсинга XML-файлов смет и проверки корректности их структуры.

## Содержание папки

В папке находится файл `parsing_xml.py` - скрипт для тестирования парсинга XML-смет.

## Описание скрипта parsing_xml.py

Скрипт выполняет следующие функции:

1. Извлекает из XML-файла сметы:
   - Названия разделов
   - Работы (с кодом ФЕР/ТЕР) с ценами
   - Материалы (с кодом ФССЦ/ТССЦ) с ценами
   - Все цены
   - Общую стоимость сметы

2. Проводит автоматические тесты для проверки:
   - Корректности количества позиций
   - Соответствия количества работ и материалов
   - Правильности расчета общей стоимости
   - Наличия и уникальности единиц измерения

### Основные функции

- `extract_sections_works_units_prices_and_materials(xml_file: str) -> Dict` - основной парсер XML
- `calculate_total_cost(sections: Dict) -> float` - вычисляет общую стоимость сметы
- `run_tests(sections: Dict) -> None` - запускает тесты для проверки данных
