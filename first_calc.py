"""
first_calc.py - Расчет Z-фактора и плотности по Пенга-Робинсону
"""

from thermo import ChemicalConstantsPackage, PRMIX, CEOSGas, CEOSLiquid, FlashVL
from thermo.interaction_parameters import IPDB

print("=" * 60)
print("РАСЧЕТ ПО ПЕНГА-РОБИНСОНУ")
print("=" * 60)

# 1. Загружаем свойства компонентов
components = ['methane', 'ethane', 'propane']
constants, properties = ChemicalConstantsPackage.from_IDs(components)

# 2. Задаем состав (мольные доли)
zs = [0.80, 0.15, 0.05]  # метан, этан, пропан

# 3. Задаем условия (T=300K, P=2.5 МПа)
T = 300.0  # Кельвины
P = 2.5e6  # Паскали

# 4. Коэффициенты взаимодействия
kijs = IPDB.get_ip_asymmetric_matrix('ChemSep PR', constants.CASs, 'kij')

# 5. Настраиваем уравнение
eos_kwargs = {
    'Pcs': constants.Pcs,
    'Tcs': constants.Tcs,
    'omegas': constants.omegas,
    'kijs': kijs
}

# 6. Создаем газовую и жидкую фазу
gas = CEOSGas(PRMIX, eos_kwargs=eos_kwargs,
              HeatCapacityGases=properties.HeatCapacityGases)

liquid = CEOSLiquid(PRMIX, eos_kwargs=eos_kwargs,
                    HeatCapacityGases=properties.HeatCapacityGases)

# 7. Создаем flash-объект
flasher = FlashVL(constants, properties, liquid=liquid, gas=gas)

# 8. Выполняем flash-расчет
result = flasher.flash(T=T, P=P, zs=zs)

# 9. Вывод результатов
print(f"\nТемпература:       {T - 273.15:.1f} °C")
print(f"Давление:          {P/1e6:.3f} МПа")
print(f"\nСостав смеси:")
print(f"  Метан:           {zs[0]*100:.1f} %")
print(f"  Этан:            {zs[1]*100:.1f} %")
print(f"  Пропан:          {zs[2]*100:.1f} %")

print(f"\nРезультаты:")
print(f"  Z-фактор:        {result.Z():.6f}")

# Получаем плотности через фазы
# У result есть атрибуты gas и liquid
if hasattr(result, 'gas') and result.gas is not None:
    print(f"  Плотность (газ): {result.gas.rho_mass():.3f} кг/м³")
else:
    print("  Плотность (газ): — (однофазная область)")

if hasattr(result, 'liquid') and result.liquid is not None:
    print(f"  Плотность (жидк):{result.liquid.rho_mass():.3f} кг/м³")
else:
    print("  Плотность (жидк): — (однофазная область)")

print(f"  Молярная масса:  {result.MW():.3f} кг/кмоль")
print("=" * 60)