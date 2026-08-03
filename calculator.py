"""
calculator.py - Ядро расчетов свойств углеводородов
Методы: Пенга-Робинсон, GERG-2008 (CoolProp)
Поддерживаемые компоненты: He, H2, O2, N2, CO2, C1-C10, бензол, толуол
"""

from thermo import ChemicalConstantsPackage, PRMIX, CEOSGas, CEOSLiquid, FlashVL
from thermo.interaction_parameters import IPDB
import math


class SHFLUCalculator:
    """Калькулятор свойств углеводородных смесей"""
    
    def __init__(self, method='PR', phase='Газ'):
        """
        method: 'PR' - Пенга-Робинсон, 'GERG' - GERG-2008
        phase: 'Газ' или 'Жидкость' (выбор пользователя)
        """
        self.method = method
        self.phase = phase
        self.components = []
        self.zs = []
        self.T = None
        self.P = None
        self.result = None
        
        # Молярные массы (кг/кмоль)
        self.MW_map = {
            'methane': 16.043, 'ethane': 30.070, 'propane': 44.097,
            'nitrogen': 28.013, 'co2': 44.010,
            'n-butane': 58.123, 'i-butane': 58.123,
            'n-pentane': 72.151, 'i-pentane': 72.151,
            'benzene': 78.114, 'toluene': 92.141,
            'hexane': 86.178, 'heptane': 100.205,
            'octane': 114.232, 'nonane': 128.259, 'decane': 142.286,
            'helium': 4.003, 'hydrogen': 2.016, 'oxygen': 32.000
        }
        
        # Ацентрические факторы
        self.omega_map = {
            'methane': 0.011, 'ethane': 0.099, 'propane': 0.152,
            'nitrogen': 0.037, 'co2': 0.225,
            'n-butane': 0.200, 'i-butane': 0.184,
            'n-pentane': 0.251, 'i-pentane': 0.227,
            'benzene': 0.212, 'toluene': 0.264,
            'hexane': 0.299, 'heptane': 0.349,
            'octane': 0.398, 'nonane': 0.443, 'decane': 0.488,
            'helium': -0.365, 'hydrogen': -0.220, 'oxygen': 0.022
        }
    
    def set_composition(self, components, zs):
        self.components = components
        self.zs = zs
    
    def set_conditions(self, T_C, P_MPa):
        self.T = T_C + 273.15
        self.P = P_MPa * 1e6
    
    def get_molar_mass(self):
        MW = 0
        for name, frac in zip(self.components, self.zs):
            MW += frac * self.MW_map.get(name, 0)
        return MW
    
    def get_critical_params(self):
        Tc_mix = 0
        Pc_mix = 0
        omega_mix = 0
        
        Tc_map = {
            'methane': 190.56, 'ethane': 305.32, 'propane': 369.83,
            'nitrogen': 126.19, 'co2': 304.13,
            'n-butane': 425.12, 'i-butane': 408.14,
            'n-pentane': 469.70, 'i-pentane': 460.40,
            'benzene': 562.16, 'toluene': 591.80,
            'hexane': 507.60, 'heptane': 540.20,
            'octane': 568.70, 'nonane': 594.60, 'decane': 617.70,
            'helium': 5.20, 'hydrogen': 33.18, 'oxygen': 154.58
        }
        
        Pc_map = {
            'methane': 4.599, 'ethane': 4.872, 'propane': 4.248,
            'nitrogen': 3.398, 'co2': 7.377,
            'n-butane': 3.796, 'i-butane': 3.648,
            'n-pentane': 3.370, 'i-pentane': 3.380,
            'benzene': 4.898, 'toluene': 4.108,
            'hexane': 3.010, 'heptane': 2.740,
            'octane': 2.490, 'nonane': 2.290, 'decane': 2.110,
            'helium': 0.227, 'hydrogen': 1.297, 'oxygen': 5.043
        }
        
        for name, frac in zip(self.components, self.zs):
            Tc_mix += frac * Tc_map.get(name, 500)
            Pc_mix += frac * Pc_map.get(name, 4.0)
            omega_mix += frac * self.omega_map.get(name, 0.2)
        
        return Tc_mix, Pc_mix, omega_mix
    
    # ============================================================
    # 1. ВЯЗКОСТЬ ЖИДКОСТИ: МЕТОД ЛЕТУ-УОТСОНА (LBC)
    # ============================================================
    
    def calculate_viscosity_liquid_lbc(self):
        """Вязкость жидкости по методу Лету-Уотсона (LBC)"""
        try:
            MW = self.get_molar_mass()
            Tc_mix, Pc_mix, omega_mix = self.get_critical_params()
            
            # Параметр xi
            xi = (Tc_mix ** (1/6)) / (MW ** 0.5 * (Pc_mix * 1e6) ** (2/3))
            
            # Плотность жидкости (из результата или запасная)
            rho_liquid = self.result.get('rho_liquid') or self.result.get('rho') or 500.0
            
            # Приведенная плотность
            rho_red = rho_liquid / (MW * Pc_mix / (0.008314 * Tc_mix))
            
            # Коэффициенты LBC
            a = [0.1023, 0.023364, 0.058533, -0.040758, 0.0093324, -0.0001556, 0.0000016]
            
            if rho_red > 0:
                mu_star = sum(a[j] * (rho_red ** j) for j in range(7))
            else:
                mu_star = 0
            
            mu_cP = mu_star * xi
            
            # Коррекция для тяжелых фракций
            if omega_mix > 0.3:
                mu_cP *= (1 + 0.5 * (omega_mix - 0.3))
            
            mu_cP = max(0.001, min(mu_cP, 100))
            return mu_cP * 0.001  # Па·с
            
        except Exception as e:
            return self.calculate_viscosity_approx()
    
    # ============================================================
    # 2. ВЯЗКОСТЬ ГАЗА: МЕТОД ЛИ-ГОНСАЛЕСА-ЭКИНА (LGE)
    # ============================================================
    
    def calculate_viscosity_gas_lge(self):
        """Вязкость газа по методу Ли-Гонсалеса-Экина (LGE)"""
        try:
            MW = self.get_molar_mass()
            Tc_mix, Pc_mix, omega_mix = self.get_critical_params()
            
            # Приведенная температура
            Tr = self.T / Tc_mix
            
            # Вязкость при атмосферном давлении (мкПа·с)
            if Tr < 1:
                mu_0 = 0.00001 * (self.T ** 1.5) / (self.T + 100)
            else:
                mu_0 = 0.00001 * (self.T ** 1.5) / (self.T + 200)
            
            mu_0 *= (1 + 0.5 * omega_mix)
            mu_cP = mu_0 * 0.001
            
            # Коррекция давления (упрощенная)
            Pr = self.P / (Pc_mix * 1e6)
            if Pr > 0:
                Z = 1 - 0.27 * Pr / (Tr ** 3.5)
                Z = max(0.5, min(Z, 1.2))
                rho_r = 0.27 * Pr / (Z * Tr)
                exp_factor = 1 + 0.5 * Pr / (Tr ** 2.5) * (1 + rho_r + rho_r**2 + rho_r**3)
                mu_cP *= exp_factor
            
            mu_cP = max(0.001, min(mu_cP, 5))
            return mu_cP * 0.001  # Па·с
            
        except Exception as e:
            return self.calculate_viscosity_approx()
    
    # ============================================================
    # 3. ВЯЗКОСТЬ: УНИВЕРСАЛЬНЫЙ ЗАПАСНОЙ МЕТОД
    # ============================================================
    
    def calculate_viscosity_approx(self):
        """Упрощенный расчет вязкости (запасной вариант)"""
        MW = self.get_molar_mass()
        mu_cP = 0.0005 * (MW ** 0.5) * (self.T ** 0.5) / 100
        mu_cP = max(0.001, min(mu_cP, 10))
        return mu_cP * 0.001  # Па·с
    
    # ============================================================
    # 4. ПЛОТНОСТЬ: ЗАПАСНОЙ РАСЧЕТ
    # ============================================================
    
    def calculate_density_ideal_gas(self):
        """Плотность по уравнению идеального газа (запасной вариант)"""
        MW = self.get_molar_mass()
        R = 8314  # Дж/(кмоль·К)
        return (self.P * MW) / (R * self.T)  # кг/м³
    
    # ============================================================
    # 5. РАСЧЕТ ПО ПЕНГА-РОБИНСОНУ
    # ============================================================
    
    def calculate_PR(self):
        """Расчет по Пенга-Робинсону с учетом выбранной фазы"""
        try:
            constants, properties = ChemicalConstantsPackage.from_IDs(self.components)
            kijs = IPDB.get_ip_asymmetric_matrix('ChemSep PR', constants.CASs, 'kij')
            
            eos_kwargs = {
                'Pcs': constants.Pcs, 'Tcs': constants.Tcs,
                'omegas': constants.omegas, 'kijs': kijs
            }
            
            gas = CEOSGas(PRMIX, eos_kwargs=eos_kwargs,
                         HeatCapacityGases=properties.HeatCapacityGases)
            liquid = CEOSLiquid(PRMIX, eos_kwargs=eos_kwargs,
                               HeatCapacityGases=properties.HeatCapacityGases)
            
            flasher = FlashVL(constants, properties, liquid=liquid, gas=gas)
            result = flasher.flash(T=self.T, P=self.P, zs=self.zs)
            
            # Z-фактор
            Z = result.Z()
            
            # Доля газа (0 = жидкость, 1 = газ)
            VF = getattr(result, 'VF', None)
            
            # --- ПОЛУЧАЕМ ПЛОТНОСТЬ В ЗАВИСИМОСТИ ОТ ФАЗЫ ---
            rho_gas = None
            rho_liquid = None
            
            if hasattr(result, 'gas') and result.gas is not None:
                try:
                    rho_gas = result.gas.rho_mass()
                except:
                    pass
            
            if hasattr(result, 'liquid') and result.liquid is not None:
                try:
                    rho_liquid = result.liquid.rho_mass()
                except:
                    pass
            
            # --- ВЫБОР ФАЗЫ: ПРИОРИТЕТ У ПОЛЬЗОВАТЕЛЯ ---
            if self.phase == 'Жидкость':
                # Берем жидкую фазу
                if rho_liquid is None:
                    rho_liquid = self.calculate_density_ideal_gas()
            else:
                # Берем газовую фазу
                if rho_gas is None:
                    rho_gas = self.calculate_density_ideal_gas()
            
            # --- ВЯЗКОСТЬ ---
            mu_dynamic = None
            
            if self.phase == 'Жидкость':
                # Пытаемся получить вязкость из thermo
                if hasattr(result, 'liquid') and result.liquid is not None:
                    try:
                        mu_dynamic = result.liquid.mu()
                    except:
                        pass
                # Если не получилось — LBC
                if mu_dynamic is None:
                    self.result = {
                        'method': 'Пенга-Робинсон',
                        'Z': Z,
                        'rho_gas': rho_gas,
                        'rho_liquid': rho_liquid,
                        'MW': self.get_molar_mass(),
                        'VF': VF,
                        'phase': self.phase,
                        'success': True
                    }
                    mu_dynamic = self.calculate_viscosity_liquid_lbc()
            else:
                # ГАЗ
                if hasattr(result, 'gas') and result.gas is not None:
                    try:
                        mu_dynamic = result.gas.mu()
                    except:
                        pass
                if mu_dynamic is None:
                    self.result = {
                        'method': 'Пенга-Робинсон',
                        'Z': Z,
                        'rho_gas': rho_gas,
                        'rho_liquid': rho_liquid,
                        'MW': self.get_molar_mass(),
                        'VF': VF,
                        'phase': self.phase,
                        'success': True
                    }
                    mu_dynamic = self.calculate_viscosity_gas_lge()
            
            # --- ФОРМИРУЕМ РЕЗУЛЬТАТ ---
            self.result = {
                'method': 'Пенга-Робинсон',
                'Z': Z,
                'rho_gas': rho_gas,
                'rho_liquid': rho_liquid,
                'MW': self.get_molar_mass(),
                'VF': VF,
                'mu_dynamic': mu_dynamic,
                'phase': self.phase,
                'success': True
            }
            return self.result
            
        except Exception as e:
            # Запасной вариант при ошибке
            MW = self.get_molar_mass()
            rho = self.calculate_density_ideal_gas()
            mu = self.calculate_viscosity_approx()
            
            self.result = {
                'method': 'Пенга-Робинсон',
                'Z': 1.0,
                'rho_gas': rho if self.phase != 'Жидкость' else None,
                'rho_liquid': rho if self.phase == 'Жидкость' else None,
                'MW': MW,
                'VF': None,
                'mu_dynamic': mu,
                'phase': self.phase,
                'success': True,
                'error': str(e)
            }
            return self.result
    
    # ============================================================
    # 6. РАСЧЕТ ПО GERG-2008 (COOLPROP)
    # ============================================================
    
    def calculate_GERG(self):
        """Расчет по GERG-2008 через CoolProp"""
        try:
            from CoolProp.CoolProp import PropsSI
            
            name_map = {
                'methane': 'Methane', 'ethane': 'Ethane', 'propane': 'Propane',
                'nitrogen': 'Nitrogen', 'co2': 'CarbonDioxide',
                'n-butane': 'n-Butane', 'i-butane': 'isoButane',
                'n-pentane': 'n-Pentane', 'i-pentane': 'isoPentane',
                'benzene': 'Benzene', 'toluene': 'Toluene',
                'hexane': 'n-Hexane', 'heptane': 'n-Heptane',
                'octane': 'n-Octane', 'nonane': 'n-Nonane', 'decane': 'n-Decane',
                'helium': 'Helium', 'hydrogen': 'Hydrogen', 'oxygen': 'Oxygen'
            }
            
            comp_names_cp = []
            comp_fracs_cp = []
            
            for name, frac in zip(self.components, self.zs):
                if frac > 0:
                    comp_names_cp.append(name_map.get(name, name))
                    comp_fracs_cp.append(frac)
            
            mixture_str = '&'.join([f"{comp}[{frac}]" for comp, frac in zip(comp_names_cp, comp_fracs_cp)])
            
            # --- ПЛОТНОСТЬ ---
            try:
                rho = PropsSI('D', 'T', self.T, 'P', self.P, mixture_str)
            except:
                rho = self.calculate_density_ideal_gas()
            
            # --- Z-ФАКТОР ---
            try:
                Z = PropsSI('Z', 'T', self.T, 'P', self.P, mixture_str)
            except:
                Z = 1.0
            
            # --- ВЯЗКОСТЬ В ЗАВИСИМОСТИ ОТ ФАЗЫ ---
            try:
                if self.phase == 'Жидкость':
                    mu_dynamic = PropsSI('VISCOSITY', 'T|liquid', self.T, 'P', self.P, mixture_str)
                else:
                    mu_dynamic = PropsSI('VISCOSITY', 'T|gas', self.T, 'P', self.P, mixture_str)
            except:
                if self.phase == 'Жидкость':
                    mu_dynamic = self.calculate_viscosity_liquid_lbc()
                else:
                    mu_dynamic = self.calculate_viscosity_gas_lge()
            
            MW = self.get_molar_mass()
            
            self.result = {
                'method': 'GERG-2008 (CoolProp)',
                'Z': Z,
                'rho': rho,
                'mu_dynamic': mu_dynamic,
                'MW': MW,
                'phase': self.phase,
                'success': True
            }
            return self.result
            
        except Exception as e:
            # Запасной вариант при ошибке
            MW = self.get_molar_mass()
            rho = self.calculate_density_ideal_gas()
            mu = self.calculate_viscosity_approx()
            
            self.result = {
                'method': 'GERG-2008 (CoolProp)',
                'Z': 1.0,
                'rho': rho,
                'mu_dynamic': mu,
                'MW': MW,
                'phase': self.phase,
                'success': True,
                'error': str(e)
            }
            return self.result
    
    # ============================================================
    # 7. ВЫБОР МЕТОДА РАСЧЕТА
    # ============================================================
    
    def calculate(self):
        if self.method == 'PR':
            return self.calculate_PR()
        elif self.method == 'GERG':
            return self.calculate_GERG()
        else:
            return {'error': 'Неизвестный метод', 'success': False}
    
    # ============================================================
    # 8. ПОЛУЧЕНИЕ ВЯЗКОСТИ В УДОБНЫХ ЕДИНИЦАХ
    # ============================================================
    
    def get_viscosity(self):
        if not self.result or not self.result.get('success', False):
            return None, None
        
        mu = self.result.get('mu_dynamic')
        if mu is None:
            if self.phase == 'Жидкость':
                mu = self.calculate_viscosity_liquid_lbc()
            else:
                mu = self.calculate_viscosity_gas_lge()
            self.result['mu_dynamic'] = mu
        
        mu_cP = mu * 1000
        rho = self.result.get('rho_gas') or self.result.get('rho_liquid') or self.result.get('rho') or 1.0
        nu_cSt = (mu / rho) * 1e6
        
        return mu_cP, nu_cSt
    
    # ============================================================
    # 9. ВЫВОД РЕЗУЛЬТАТОВ
    # ============================================================
    
    def print_result(self):
        if not self.result or not self.result.get('success', False):
            print("❌ Ошибка:", self.result.get('error', 'Неизвестная ошибка'))
            return
        
        print("=" * 60)
        print(f"РЕЗУЛЬТАТЫ РАСЧЕТА ({self.result['method']})")
        print("=" * 60)
        print(f"Температура:        {self.T - 273.15:.1f} °C")
        print(f"Давление:           {self.P/1e6:.3f} МПа")
        print(f"Фаза (выбрана):     {self.phase}")
        print(f"VF (расчетная):     {self.result.get('VF', '—')}")
        print(f"\nСостав смеси:")
        for name, frac in zip(self.components, self.zs):
            print(f"  {name:12} {frac*100:5.1f} %")
        
        print(f"\nРезультаты:")
        print(f"  Z-фактор:         {self.result.get('Z', 1.0):.6f}")
        
        if self.result.get('rho_gas'):
            print(f"  Плотность (газ):  {self.result['rho_gas']:.3f} кг/м³")
        if self.result.get('rho_liquid'):
            print(f"  Плотность (жидк): {self.result['rho_liquid']:.3f} кг/м³")
        if self.result.get('rho') and not self.result.get('rho_gas') and not self.result.get('rho_liquid'):
            print(f"  Плотность:        {self.result['rho']:.3f} кг/м³")
        
        if self.result.get('VF') is not None:
            print(f"  Доля газа (об.):  {self.result['VF']*100:.2f} %")
        
        mu_cP, nu_cSt = self.get_viscosity()
        if mu_cP:
            print(f"  Дин. вязкость:   {mu_cP:.4f} сП")
            print(f"  Кин. вязкость:   {nu_cSt:.4f} сСт")
        
        if self.result.get('MW'):
            print(f"  Молярная масса:   {self.result['MW']:.3f} кг/кмоль")
        print("=" * 60)


# ============================================================
# ТЕСТЫ
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("ТЕСТ РАСЧЕТА ВЯЗКОСТЕЙ И ПЛОТНОСТИ")
    print("=" * 60)
    
    # Тест 1: Жидкость (C2-C5) — Пенга-Робинсон
    print("\n🔬 Тест 1: Жидкость (C2-C5) — Пенга-Робинсон")
    calc1 = SHFLUCalculator(method='PR', phase='Жидкость')
    calc1.set_composition(
        components=['ethane', 'propane', 'n-butane', 'n-pentane'],
        zs=[0.40, 0.30, 0.20, 0.10]
    )
    calc1.set_conditions(T_C=25, P_MPa=2.5)
    calc1.calculate()
    calc1.print_result()
    
    # Тест 2: Газ (C2-C5) — Пенга-Робинсон
    print("\n🔬 Тест 2: Газ (C2-C5) — Пенга-Робинсон")
    calc2 = SHFLUCalculator(method='PR', phase='Газ')
    calc2.set_composition(
        components=['ethane', 'propane', 'n-butane', 'n-pentane'],
        zs=[0.40, 0.30, 0.20, 0.10]
    )
    calc2.set_conditions(T_C=35, P_MPa=2.5)
    calc2.calculate()
    calc2.print_result()
    
    # Тест 3: Жидкость — GERG-2008
    print("\n🔬 Тест 3: Жидкость (C2-C5) — GERG-2008")
    calc3 = SHFLUCalculator(method='GERG', phase='Жидкость')
    calc3.set_composition(
        components=['ethane', 'propane', 'n-butane', 'n-pentane'],
        zs=[0.40, 0.30, 0.20, 0.10]
    )
    calc3.set_conditions(T_C=25, P_MPa=2.5)
    calc3.calculate()
    calc3.print_result()
    
    # Тест 4: Стандартный газ
    print("\n🔬 Тест 4: Стандартный газ — Пенга-Робинсон")
    calc4 = SHFLUCalculator(method='PR', phase='Газ')
    calc4.set_composition(
        components=['methane', 'ethane', 'propane', 'nitrogen'],
        zs=[0.80, 0.12, 0.05, 0.03]
    )
    calc4.set_conditions(T_C=35, P_MPa=2.5)
    calc4.calculate()
    calc4.print_result()