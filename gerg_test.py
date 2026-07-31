"""
gerg_test.py - Расчет Z-фактора и плотности по GERG-2008
"""

import pyaga8

print("=" * 60)
print("РАСЧЕТ ПО GERG-2008")
print("=" * 60)

# 1. Создаем объект
detail = pyaga8.Detail()

# 2. Задаем состав (мольные доли)
comp = pyaga8.Composition()
comp.methane = 0.80
comp.ethane = 0.15
comp.propane = 0.05

# 3. Задаем условия
T = 300.0      # Кельвины
P = 2.5e6      # Паскали

# 4. Передаем данные
detail.set_composition(comp)
detail.temperature = T
detail.pressure = P

# 5. Расчет
detail.calc_density()

# 6. Результаты
print(f"\nТемпература:       {T - 273.15:.1f} °C")
print(f"Давление:          {P/1e6:.3f} МПа")
print(f"\nСостав смеси:")
print(f"  Метан:           {comp.methane*100:.1f} %")
print(f"  Этан:            {comp.ethane*100:.1f} %")
print(f"  Пропан:          {comp.propane*100:.1f} %")
print(f"\nРезультаты:")
print(f"  Z-фактор:        {detail.Z:.6f}")
print(f"  Плотность:       {detail.d:.3f} кг/м³")
print("=" * 60)