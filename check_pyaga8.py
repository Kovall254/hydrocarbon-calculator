"""
check_pyaga8.py - Проверка атрибутов pyaga8
"""

import pyaga8

# Создаем объект
detail = pyaga8.Detail()

# Задаем состав
comp = pyaga8.Composition()
comp.methane = 0.80
comp.ethane = 0.12
comp.propane = 0.05
comp.nitrogen = 0.03

detail.set_composition(comp)
detail.temperature = 308.15  # 35°C
detail.pressure = 2.5e6      # 2.5 МПа

# Выполняем расчет
detail.calc_density()

# Выводим все атрибуты объекта
print("=" * 60)
print("ДОСТУПНЫЕ АТРИБУТЫ detail:")
print("=" * 60)

for attr in dir(detail):
    if not attr.startswith('_'):
        try:
            value = getattr(detail, attr)
            if not callable(value):
                print(f"  {attr}: {value}")
        except:
            pass

print("=" * 60)

# Проверяем конкретные атрибуты
print("\nПроверка конкретных атрибутов:")
print(f"  detail.d = {detail.d}")          # плотность
print(f"  detail.Z = {getattr(detail, 'Z', 'НЕТ')}")
print(f"  detail.molar_mass = {getattr(detail, 'molar_mass', 'НЕТ')}")
print(f"  detail.MW = {getattr(detail, 'MW', 'НЕТ')}")
print(f"  detail.molecular_weight = {getattr(detail, 'molecular_weight', 'НЕТ')}")
print(f"  detail.rho = {getattr(detail, 'rho', 'НЕТ')}")
print(f"  detail.density = {getattr(detail, 'density', 'НЕТ')}")
print(f"  detail.molar_mass = {getattr(detail, 'molar_mass', 'НЕТ')}")
print("=" * 60)