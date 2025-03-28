import xml.etree.ElementTree as ET
from typing import Dict, List, Set


def calculate_total_cost(sections: Dict) -> float:
    """Вычисляет общую стоимость сметы на основе данных из структуры"""
    total = 0.0

    for section in sections.values():
        if isinstance(section, list):  # Проверяем, что это список работ
            for work in section:
                total += work['price']  # Добавляем стоимость работы

                # Добавляем стоимость всех материалов
                for material in work['materials']:
                    total += material['price']

    return round(total, 2)


def extract_sections_works_units_prices_and_materials(xml_file: str) -> Dict:
    """
    Извлекает из XML-файла сметы:
    - названия разделов
    - работы (с кодом ФЕР) с ценами
    - материалы (с кодом ФССЦ) с ценами
    - все цены
    - общую стоимость сметы
    """
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        result = {}
        current_section = None
        last_work = None

        # Счетчики для тестов
        total_positions = 0
        total_fer = 0
        total_fssc = 0
        total_fsem = 0
        total_chapters = 0
        calculated_total_from_prices = 0.0
        unique_units = set()  # Для теста уникальных единиц измерения

        for elem in root.iter():
            if elem.tag == 'Chapter' and 'Caption' in elem.attrib:
                section_name = elem.get('Caption')
                if section_name not in result:
                    result[section_name] = []
                current_section = section_name
                total_chapters += 1

            elif elem.tag == 'Position' and 'Caption' in elem.attrib:
                position_code = elem.get('Code', '')
                units = elem.get('Units', '')
                position_data = {
                    'caption': elem.get('Caption'),
                    'units': units,
                    'code': position_code
                }

                # Для теста уникальных единиц измерения
                if units:
                    unique_units.add(units.strip().lower())

                # Обработка работ (ФЕР)
                if position_code.startswith('ФЕР'):
                    total_fer += 1
                    if not position_code.startswith('ФСЭМ'):
                        total_positions += 1

                    price_base = elem.find('.//PriceBase')
                    if price_base is not None:
                        price = sum(
                            float(price_base.get(attr, '0').replace(',', '.'))
                            for attr in ['PZ', 'OZ', 'EM', 'ZM', 'MT']
                        )
                        position_data['price'] = price
                        calculated_total_from_prices += price

                    if current_section:
                        position_data['materials'] = []
                        result[current_section].append(position_data)
                        last_work = position_data

                # Обработка материалов (ФССЦ)
                elif position_code.startswith('ФССЦ'):
                    total_fssc += 1
                    if not position_code.startswith('ФСЭМ'):
                        total_positions += 1

                    if last_work:
                        price_base = elem.find('.//PriceBase')
                        material_price = 0.0
                        if price_base is not None:
                            material_price = float(price_base.get('PZ', '0').replace(',', '.'))
                            calculated_total_from_prices += material_price

                        material = {
                            'name': position_data['caption'],
                            'units': position_data['units'],
                            'price': material_price
                        }
                        last_work['materials'].append(material)

                # Обработка ФСЭМ (учитываем только для статистики)
                elif position_code.startswith('ФСЭМ'):
                    total_fsem += 1

        # Добавляем общую стоимость в результат
        result['total_cost'] = calculate_total_cost(result)

        # Добавляем статистику для тестов
        result['_stats'] = {
            'total_positions': total_positions,
            'total_fer': total_fer,
            'total_fssc': total_fssc,
            'total_fsem': total_fsem,
            'total_chapters': total_chapters,
            'calculated_total_from_prices': round(calculated_total_from_prices, 2),
            'unique_units_count': len(unique_units),
            'unique_units': unique_units
        }

        return result

    except ET.ParseError as e:
        print(f"Ошибка парсинга XML: {e}")
        return {}
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return {}


def run_tests(sections: Dict) -> None:
    """Запускает тесты для проверки данных сметы"""
    if not sections or '_stats' not in sections:
        print("Ошибка: Невозможно выполнить тесты - данные сметы не загружены")
        return

    stats = sections['_stats']

    print("\n=== ТЕСТЫ ===")

    # Тест 1: Количество Position (без ФСЭМ) = ФЕР + ФССЦ
    print(
        f"\nТест 1: Общее количество Position (без ФСЭМ) ({stats['total_positions']}) == ФЕР ({stats['total_fer']}) + ФССЦ ({stats['total_fssc']})")
    print(f"ФСЭМ не учитывается (найдено {stats['total_fsem']})")
    if stats['total_positions'] == stats['total_fer'] + stats['total_fssc']:
        print("✅ Успех: Количество Position (без ФСЭМ) совпадает с суммой ФЕР и ФССЦ")
    else:
        print(f"❌ Ошибка: {stats['total_positions']} != {stats['total_fer']} + {stats['total_fssc']}")

    # Тест 2: Количество разделов Chapter
    print(f"\nТест 2: Количество разделов Chapter: {stats['total_chapters']}")
    print(
        f"Фактическое количество разделов в данных: {len([k for k in sections.keys() if k not in ['total_cost', '_stats']])}")
    if stats['total_chapters'] == len([k for k in sections.keys() if k not in ['total_cost', '_stats']]):
        print("✅ Успех: Количество Chapter совпадает с количеством разделов в данных")
    else:
        print("❌ Ошибка: Количество Chapter не совпадает с количеством разделов в данных")

    # Тест 3: Проверка количества работ ФЕР
    print(f"\nТест 3: Количество работ ФЕР: {stats['total_fer']}")
    actual_fer = sum(len(works) for section, works in sections.items()
                     if section not in ['total_cost', '_stats'])
    print(f"Фактическое количество работ в данных: {actual_fer}")
    if stats['total_fer'] == actual_fer:
        print("✅ Успех: Количество работ ФЕР совпадает")
    else:
        print("❌ Ошибка: Количество работ ФЕР не совпадает")

    # Тест 4: Проверка количества материалов ФССЦ
    print(f"\nТест 4: Количество материалов ФССЦ: {stats['total_fssc']}")
    actual_fssc = sum(len(work['materials'])
                      for section, works in sections.items()
                      if section not in ['total_cost', '_stats']
                      for work in works)
    print(f"Фактическое количество материалов в данных: {actual_fssc}")
    if stats['total_fssc'] == actual_fssc:
        print("✅ Успех: Количество материалов ФССЦ совпадает")
    else:
        print("❌ Ошибка: Количество материалов ФССЦ не совпадает")

    # Тест 5: Проверка общей стоимости сметы
    print(f"\nТест 5: Проверка общей стоимости сметы")
    print(f"Сумма из PriceBase (ФЕР+ФССЦ): {stats['calculated_total_from_prices']:.2f}")
    print(f"Общая стоимость из структуры: {sections['total_cost']:.2f}")
    if abs(stats['calculated_total_from_prices'] - sections['total_cost']) < 0.01:
        print("✅ Успех: Общая стоимость совпадает с суммой из PriceBase")
    else:
        print("❌ Ошибка: Общая стоимость не совпадает с суммой из PriceBase")

    # Тест 6: Проверка уникальных единиц измерения
    print(f"\nТест 6: Проверка уникальных единиц измерения")
    print(f"Найдено уникальных единиц измерения: {stats['unique_units_count']}")
    print("Список уникальных единиц измерения:")
    for i, unit in enumerate(sorted(stats['unique_units']), 1):
        print(f"  {i}. {unit}")

    # Тест 7: Проверка наличия пустых единиц измерения
    print(f"\nТест 7: Проверка на отсутствие пустых единиц измерения")
    has_empty_units = any(work['units'].strip() == ''
                          for section in sections.values()
                          if isinstance(section, list)
                          for work in section)
    if not has_empty_units:
        print("✅ Успех: Пустые единицы измерения отсутствуют")
    else:
        print("❌ Ошибка: Найдены пустые единицы измерения")


if __name__ == "__main__":
    xml_file_path = "376-УКС_С Раздел ПД № 11 02-01-02 АР.xml"
    sections = extract_sections_works_units_prices_and_materials(xml_file_path)

    print("Полная структура сметы с ценами:")
    for section_name, works in sections.items():
        if section_name in ['total_cost', '_stats']:
            continue

        print(f"\nРаздел: {section_name}")
        for i, work in enumerate(works, 1):
            print(f"  {i}. {work['caption']} [{work['units']}] - {work['price']:.2f}")
            if work['materials']:
                print("    Материалы:")
                for j, material in enumerate(work['materials'], 1):
                    print(f"      {j}. {material['name']} [{material['units']}] - {material['price']:.2f}")

    print(f"\nОбщая стоимость сметы: {sections['total_cost']:.2f}")

    # Запуск тестов
    run_tests(sections)