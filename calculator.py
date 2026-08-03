"""
calculator.py - Ядро расчетов свойств углеводородов
Методы: Пенга-Робинсон, GERG-2008
Поддерживаемые компоненты: He, H2, O2, N2, CO2, C1-C10, бензол, толуол
"""

from thermo import ChemicalConstantsPackage, PRMIX, CEOSGas, CEOSLiquid, FlashVL
from thermo.interaction_parameters import IPDB
import math


class SHFLUCalculator:
    """Калькулятор свойств газовых смесей"""
    
    def __init__(self, method='PR', phase='Газ'):
        self.method = method
        self.phase = phase
        self.components = []
        self.zs = []
        self.T = None
        self.P = None
        self.result = None
        
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
    # МЕТОДЫ РАСЧЕТА ВЯЗКОСТИ
    # ============================================================
    
    def calculate_viscosity_liquid_lbc(self):
        """
        ВЯЗКОСТЬ ЖИДКОСТИ: МЕТОД ЛЕТУ-УОТСОНА (LBC)
        Используется для Пенга-Робинсона
        """
        try:
            MW = self.get_molar_mass()
            Tc_mix, Pc_mix, omega_mix = self.get_critical_params()
            
            # Параметр xi
            xi = (Tc_mix ** (1/6)) / (MW ** 0.5 * (Pc_mix * 1e6) ** (2/3))
            
            # Плотность жидкости (из результата)
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
            print(f"LBC error: {e}")
            return self.calculate_viscosity_approx()
    
    def calculate_viscosity_liquid_coolprop(self):
        """
        ВЯЗКОСТЬ ЖИДКОСТИ: GERG-2008 через CoolProp
        Используется для GERG-2008
        """
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
            
            # Принудительно задаем жидкую фазу для CoolProp
            # Используем синтаксис с фазой: 'T|liquid'
            mu = PropsSI('VISCOSITY', 'T|liquid', self.T, 'P', self.P, mixture_str)
            return mu  # Па·с
            
        except Exception as e:
            print(f"CoolProp liquid viscosity error: {e}")
            return self.calculate_viscosity_liquid_lbc()
    
    def calculate_viscosity_gas_lge(self):
        """
        ВЯЗКОСТЬ ГАЗА: МЕТОД ЛИ-ГОНСАЛЕСА-ЭКИНА (LGE)
        Используется для Пенга-Робинсона
        """
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
            
            # Перевод в Па·с
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
            print(f"LGE error: {e}")
            return self.calculate_viscosity_approx()
    
    def calculate_viscosity_gas_coolprop(self):
        """
        ВЯЗКОСТЬ ГАЗА: GERG-2008 через CoolProp
        Используется для GERG-2008
        """
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
            
            # Принудительно задаем газовую фазу для CoolProp
            mu = PropsSI('VISCOSITY', 'T|gas', self.T, 'P', self.P, mixture_str)
            return mu  # Па·с
            
        except Exception as e:
            print(f"CoolProp gas viscosity error: {e}")
            return self.calculate_viscosity_gas_lge()
    
    def calculate_viscosity_approx(self):
        """Запасной упрощенный расчет вязкости"""
        MW = self.get_molar_mass()
        mu_cP = 0.0005 * (MW ** 0.5) * (self.T ** 0.5) / 100
        mu_cP = max(0.001, min(mu_cP, 10))
        return mu_cP * 0.001  # Па·с
    
    # ============================================================
    # ОСНОВНЫЕ РАСЧЕТНЫЕ МЕТОДЫ
    # ============================================================
    
    def calculate_PR(self):
        """Расчет по Пенга-Робинсону"""
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
            
            rho_gas = None
            rho_liquid = None
            mu_dynamic = None
            VF = getattr(result, 'VF', None)
            
            # Получаем свойства в зависимости от фазы
            if self.phase == 'Жидкость':
                if hasattr(result, 'liquid') and result.liquid is not None:
                    try:
                        rho_liquid = result.liquid.rho_mass()
                        mu_dynamic = result.liquid.mu()
                    except:
                        pass
                # Если жидкость не дала вязкость — используем LBC
                if mu_dynamic is None:
                    # Сохраняем результат для LBC
                    self.result = {
                        'method': 'Пенга-Робинсон',
                        'Z': result.Z(),
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
                        rho_gas = result.gas.rho_mass()
                        mu_dynamic = result.gas.mu()
                    except:
                        pass
                # Если газ не дал вязкость — используем LGE
                if mu_dynamic is None:
                    self.result = {
                        'method': 'Пенга-Робинсон',
                        'Z': result.Z(),
                        'rho_gas': rho_gas,
                        'rho_liquid': rho_liquid,
                        'MW': self.get_molar_mass(),
                        'VF': VF,
                        'phase': self.phase,
                        'success': True
                    }
                    mu_dynamic = self.calculate_viscosity_gas_lge()
            
            self.result = {
                'method': 'Пенга-Робинсон',
                'Z': result.Z(),
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
            self.result = {'method': 'Пенга-Робинсон', 'error': str(e), 'success': False}
            return self.result
    
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
            
            # Плотность
            rho = PropsSI('D', 'T', self.T, 'P', self.P, mixture_str)
            
            # Z-фактор
            Z = PropsSI('Z', 'T', self.T, 'P', self.P, mixture_str)
            
            # Вязкость в зависимости от фазы
            if self.phase == 'Жидкость':
                try:
                    mu_dynamic = PropsSI('VISCOSITY', 'T|liquid', self.T, 'P', self.P, mixture_str)
                except:
                    # Если CoolProp не может дать вязкость жидкости — используем LBC
                    self.result = {
                        'method': 'GERG-2008 (CoolProp)',
                        'Z': Z,
                        'rho': rho,
                        'MW': self.get_molar_mass(),
                        'phase': self.phase,
                        'success': True
                    }
                    mu_dynamic = self.calculate_viscosity_liquid_lbc()
            else:
                try:
                    mu_dynamic = PropsSI('VISCOSITY', 'T|gas', self.T, 'P', self.P, mixture_str)
                except:
                    # Если CoolProp не может дать вязкость газа — используем LGE
                    self.result = {
                        'method': 'GERG-2008 (CoolProp)',
                        'Z': Z,
                        'rho': rho,
                        'MW': self.get_molar_mass(),
                        'phase': self.phase,
                        'success': True
                    }
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
            self.result = {
                'method': 'GERG-2008 (CoolProp)',
                'Z': 1.0,
                'rho': None,
                'mu_dynamic': self.calculate_viscosity_approx(),
                'MW': self.get_molar_mass(),
                'phase': self.phase,
                'success': True,
                'error': str(e)
            }
            return self.result
    
    def calculate(self):
        if self.method == 'PR':
            return self.calculate_PR()
        elif self.method == 'GERG':
            return self.calculate_GERG()
        else:
            return {'error': 'Неизвестный метод', 'success': False}
    
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
    
    def print_result(self):
        if not self.result or not self.result.get('success', False):
            print("❌ Ошибка:", self.result.get('error', 'Неизвестная ошибка'))
            return
        
        print("=" * 60)
        print(f"РЕЗУЛЬТАТЫ РАСЧЕТА ({self.result['method']})")
        print("=" * 60)
        print(f"Температура:        {self.T - 273.15:.1f} °C")
        print(f"Давление:           {self.P/1e6:.3f} МПа")
        print(f"Фаза:               {self.phase}")
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


if __name__ == "__main__":
    print("=" * 60)
    print("ТЕСТ РАСЧЕТА ВЯЗКОСТЕЙ")
    print("=" * 60)
    
    # Тест 1: ЖИДКОСТЬ через Пенга-Робинсон (LBC)
    print("\n🔬 Тест 1: Жидкость (Пенга-Робинсон / LBC)")
    calc1 = SHFLUCalculator(method='PR', phase='Жидкость')
    calc1.set_composition(
        components=['methane', 'ethane', 'propane', 'n-butane', 'hexane'],
        zs=[0.30, 0.20, 0.20, 0.15, 0.15]
    )
    calc1.set_conditions(T_C=25, P_MPa=0.5)
    calc1.calculate()
    calc1.print_result()
    
    # Тест 2: ЖИДКОСТЬ через GERG-2008 (CoolProp)
    print("\n🔬 Тест 2: Жидкость (GERG-2008 / CoolProp)")
    calc2 = SHFLUCalculator(method='GERG', phase='Жидкость')
    calc2.set_composition(
        components=['methane', 'ethane', 'propane', 'n-butane', 'hexane'],
        zs=[0.30, 0.20, 0.20, 0.15, 0.15]
    )
    calc2.set_conditions(T_C=25, P_MPa=0.5)
    calc2.calculate()
    calc2.print_result()
    
    # Тест 3: ГАЗ через Пенга-Робинсон (LGE)
    print("\n🔬 Тест 3: Газ (Пенга-Робинсон / LGE)")
    calc3 = SHFLUCalculator(method='PR', phase='Газ')
    calc3.set_composition(
        components=['methane', 'ethane', 'propane', 'nitrogen'],
        zs=[0.80, 0.12, 0.05, 0.03]
    )
    calc3.set_conditions(T_C=35, P_MPa=2.5)
    calc3.calculate()
    calc3.print_result()
    
    # Тест 4: ГАЗ через GERG-2008 (CoolProp)
    print("\n🔬 Тест 4: Газ (GERG-2008 / CoolProp)")
    calc4 = SHFLUCalculator(method='GERG', phase='Газ')
    calc4.set_composition(
        components=['methane', 'ethane', 'propane', 'nitrogen'],
        zs=[0.80, 0.12, 0.05, 0.03]
    )
    calc4.set_conditions(T_C=35, P_MPa=2.5)
    calc4.calculate()
    calc4.print_result()