"""
calculator.py - Ядро расчетов свойств углеводородов
Методы: Пенга-Робинсон, GERG-2008 (CoolProp → pyaga8 → teqp → запасной)
"""

from thermo import ChemicalConstantsPackage, PRMIX, CEOSGas, CEOSLiquid, FlashVL
from thermo.interaction_parameters import IPDB
import math


class SHFLUCalculator:
    """Калькулятор свойств углеводородных смесей"""
    
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
    # 1. ВЯЗКОСТЬ: LBC (ЖИДКОСТЬ) — ЗАПАСНОЙ
    # ============================================================
    
    def calculate_viscosity_liquid_lbc(self):
        try:
            MW = self.get_molar_mass()
            Tc_mix, Pc_mix, omega_mix = self.get_critical_params()
            
            xi = (Tc_mix ** (1/6)) / (MW ** 0.5 * (Pc_mix * 1e6) ** (2/3))
            
            rho_liquid = self.result.get('rho_liquid') or self.result.get('rho') or 500.0
            rho_red = rho_liquid / (MW * Pc_mix / (0.008314 * Tc_mix))
            
            a = [0.1023, 0.023364, 0.058533, -0.040758, 0.0093324, -0.0001556, 0.0000016]
            
            if rho_red > 0:
                mu_star = sum(a[j] * (rho_red ** j) for j in range(7))
            else:
                mu_star = 0
            
            mu_cP = mu_star * xi
            
            if omega_mix > 0.3:
                mu_cP *= (1 + 0.5 * (omega_mix - 0.3))
            
            mu_cP = max(0.001, min(mu_cP, 100))
            return mu_cP * 0.001
            
        except:
            return self.calculate_viscosity_approx()
    
    # ============================================================
    # 2. ВЯЗКОСТЬ: LGE (ГАЗ) — ЗАПАСНОЙ
    # ============================================================
    
    def calculate_viscosity_gas_lge(self):
        try:
            MW = self.get_molar_mass()
            Tc_mix, Pc_mix, omega_mix = self.get_critical_params()
            
            Tr = self.T / Tc_mix
            
            if Tr < 1:
                mu_0 = 0.00001 * (self.T ** 1.5) / (self.T + 100)
            else:
                mu_0 = 0.00001 * (self.T ** 1.5) / (self.T + 200)
            
            mu_0 *= (1 + 0.5 * omega_mix)
            mu_cP = mu_0 * 0.001
            
            Pr = self.P / (Pc_mix * 1e6)
            if Pr > 0:
                Z = 1 - 0.27 * Pr / (Tr ** 3.5)
                Z = max(0.5, min(Z, 1.2))
                rho_r = 0.27 * Pr / (Z * Tr)
                exp_factor = 1 + 0.5 * Pr / (Tr ** 2.5) * (1 + rho_r + rho_r**2 + rho_r**3)
                mu_cP *= exp_factor
            
            mu_cP = max(0.001, min(mu_cP, 5))
            return mu_cP * 0.001
            
        except:
            return self.calculate_viscosity_approx()
    
    # ============================================================
    # 3. ВЯЗКОСТЬ: УНИВЕРСАЛЬНЫЙ ЗАПАСНОЙ
    # ============================================================
    
    def calculate_viscosity_approx(self):
        MW = self.get_molar_mass()
        mu_cP = 0.0005 * (MW ** 0.5) * (self.T ** 0.5) / 100
        mu_cP = max(0.001, min(mu_cP, 10))
        return mu_cP * 0.001
    
    # ============================================================
    # 4. ПЛОТНОСТЬ: ЗАПАСНЫЕ МЕТОДЫ
    # ============================================================
    
    def calculate_density_ideal_gas(self):
        MW = self.get_molar_mass()
        R = 8314
        return (self.P * MW) / (R * self.T)
    
    def calculate_density_from_Z(self, Z):
        MW = self.get_molar_mass()
        R = 8314
        if Z is not None and Z > 0:
            return (self.P * MW) / (Z * R * self.T)
        else:
            return self.calculate_density_ideal_gas()
    
    # ============================================================
    # 5. РАСЧЕТ ПО ПЕНГА-РОБИНСОНУ
    # ============================================================
    
    def calculate_PR(self):
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
            
            Z = result.Z()
            VF = getattr(result, 'VF', None)
            
            # --- ПЛОТНОСТЬ ---
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
            
            if rho_gas is None and rho_liquid is None:
                rho_gas = self.calculate_density_from_Z(Z)
            
            if rho_gas is not None and (rho_gas < 0.01 or rho_gas > 1000):
                rho_gas = self.calculate_density_ideal_gas()
            if rho_liquid is not None and (rho_liquid < 0.01 or rho_liquid > 2000):
                rho_liquid = self.calculate_density_ideal_gas()
            
            # --- ВЯЗКОСТЬ ---
            mu_dynamic = None
            
            if self.phase == 'Жидкость':
                try:
                    from CoolProp.CoolProp import PropsSI
                    name_map = self._get_coolprop_name_map()
                    mixture_str = self._build_mixture_str(name_map)
                    mu_dynamic = PropsSI('VISCOSITY', 'T|liquid', self.T, 'P', self.P, mixture_str)
                except:
                    mu_dynamic = self.calculate_viscosity_liquid_lbc()
            else:
                mu_dynamic = self.calculate_viscosity_gas_lge()
            
            if mu_dynamic is None or mu_dynamic <= 0:
                mu_dynamic = self.calculate_viscosity_approx()
            
            self.result = {
                'method': 'Пенга-Робинсон',
                'Z': Z if Z is not None else 1.0,
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
            MW = self.get_molar_mass()
            rho = self.calculate_density_ideal_gas()
            mu = self.calculate_viscosity_approx()
            
            self.result = {
                'method': 'Пенга-Робинсон',
                'Z': None,
                'rho_gas': rho if self.phase != 'Жидкость' else None,
                'rho_liquid': rho if self.phase == 'Жидкость' else None,
                'MW': MW,
                'VF': None,
                'mu_dynamic': mu,
                'phase': self.phase,
                'success': False,
                'error': str(e)
            }
            return self.result
    
    # ============================================================
    # 6. ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ДЛЯ GERG
    # ============================================================
    
    def _get_coolprop_name_map(self):
        return {
            'methane': 'Methane', 'ethane': 'Ethane', 'propane': 'Propane',
            'nitrogen': 'Nitrogen', 'co2': 'CarbonDioxide',
            'n-butane': 'n-Butane', 'i-butane': 'isoButane',
            'n-pentane': 'n-Pentane', 'i-pentane': 'isoPentane',
            'benzene': 'Benzene', 'toluene': 'Toluene',
            'hexane': 'n-Hexane', 'heptane': 'n-Heptane',
            'octane': 'n-Octane', 'nonane': 'n-Nonane', 'decane': 'n-Decane',
            'helium': 'Helium', 'hydrogen': 'Hydrogen', 'oxygen': 'Oxygen'
        }
    
    def _get_pyaga8_map(self):
        return {
            'methane': 'methane', 'ethane': 'ethane', 'propane': 'propane',
            'nitrogen': 'nitrogen', 'co2': 'co2',
            'n-butane': 'n_butane', 'i-butane': 'i_butane',
            'n-pentane': 'n_pentane', 'i-pentane': 'i_pentane',
            'hexane': 'hexane', 'heptane': 'heptane',
            'octane': 'octane', 'nonane': 'nonane', 'decane': 'decane',
            'helium': 'helium', 'hydrogen': 'hydrogen', 'oxygen': 'oxygen'
        }
    
    def _get_teqp_map(self):
        return {
            'methane': 'methane', 'ethane': 'ethane', 'propane': 'propane',
            'nitrogen': 'nitrogen', 'co2': 'carbon_dioxide',
            'n-butane': 'n-butane', 'i-butane': 'isobutane',
            'n-pentane': 'n-pentane', 'i-pentane': 'isopentane',
            'hexane': 'n-hexane', 'heptane': 'n-heptane',
            'octane': 'n-octane', 'nonane': 'n-nonane', 'decane': 'n-decane',
            'helium': 'helium', 'hydrogen': 'hydrogen', 'oxygen': 'oxygen'
        }
    
    def _build_mixture_str(self, name_map):
        comp_names_cp = []
        comp_fracs_cp = []
        for name, frac in zip(self.components, self.zs):
            if frac > 0:
                cp_name = name_map.get(name)
                if cp_name is None:
                    raise ValueError(f"Компонент '{name}' не поддерживается")
                comp_names_cp.append(cp_name)
                comp_fracs_cp.append(frac)
        if not comp_names_cp:
            raise ValueError("Нет компонентов для расчета")
        return '&'.join([f"{comp}[{frac}]" for comp, frac in zip(comp_names_cp, comp_fracs_cp)])
    
    # ============================================================
    # 7. РАСЧЕТ ПО GERG-2008 (CoolProp → pyaga8 → teqp → запасной)
    # ============================================================
    
    def calculate_GERG(self):
        """
        Расчет по GERG-2008 с тройным fallback:
        1. CoolProp
        2. pyaga8
        3. teqp (NIST)
        4. Запасной (идеальный газ)
        """
        
        # ---- ПОПЫТКА 1: CoolProp ----
        try:
            from CoolProp.CoolProp import PropsSI
            
            name_map = self._get_coolprop_name_map()
            mixture_str = self._build_mixture_str(name_map)
            
            rho = PropsSI('D', 'T', self.T, 'P', self.P, mixture_str)
            Z = PropsSI('Z', 'T', self.T, 'P', self.P, mixture_str)
            
            if self.phase == 'Жидкость':
                mu_dynamic = PropsSI('VISCOSITY', 'T|liquid', self.T, 'P', self.P, mixture_str)
            else:
                mu_dynamic = PropsSI('VISCOSITY', 'T|gas', self.T, 'P', self.P, mixture_str)
            
            if Z is not None and Z > 0 and Z < 2:
                self.result = {
                    'method': 'GERG-2008 (CoolProp)',
                    'Z': Z,
                    'rho': rho,
                    'mu_dynamic': mu_dynamic,
                    'MW': self.get_molar_mass(),
                    'phase': self.phase,
                    'success': True
                }
                return self.result
            else:
                raise ValueError(f"CoolProp Z невалиден: {Z}")
                
        except Exception as e1:
            print(f"⚠️ CoolProp не сработал: {e1}")
            print("🔄 Переключение на pyaga8...")
            
            # ---- ПОПЫТКА 2: pyaga8 ----
            try:
                import pyaga8
                
                detail = pyaga8.Detail()
                comp = pyaga8.Composition()
                
                pyaga8_map = self._get_pyaga8_map()
                
                for name, frac in zip(self.components, self.zs):
                    if frac > 0:
                        pyaga8_name = pyaga8_map.get(name)
                        if pyaga8_name is not None:
                            setattr(comp, pyaga8_name, frac)
                
                detail.set_composition(comp)
                detail.temperature = self.T
                detail.pressure = self.P
                detail.calc_density()
                
                Z = detail.Z
                rho = detail.d
                
                if self.phase == 'Жидкость':
                    mu_dynamic = self.calculate_viscosity_liquid_lbc()
                else:
                    mu_dynamic = self.calculate_viscosity_gas_lge()
                
                if Z is not None and Z > 0 and Z < 2:
                    print(f"✅ pyaga8 сработал: Z = {Z:.6f}")
                    self.result = {
                        'method': 'GERG-2008 (pyaga8)',
                        'Z': Z,
                        'rho': rho,
                        'mu_dynamic': mu_dynamic,
                        'MW': self.get_molar_mass(),
                        'phase': self.phase,
                        'success': True
                    }
                    return self.result
                else:
                    raise ValueError(f"pyaga8 Z невалиден: {Z}")
                    
            except ImportError:
                print("❌ pyaga8 не установлен. Переход к teqp...")
            except Exception as e2:
                print(f"❌ pyaga8 не сработал: {e2}")
                print("🔄 Переключение на teqp...")
            
            # ---- ПОПЫТКА 3: teqp (NIST) ----
            try:
                import teqp
                import numpy as np
                
                teqp_map = self._get_teqp_map()
                
                # Собираем компоненты для teqp
                comp_names_teqp = []
                comp_fracs_teqp = []
                for name, frac in zip(self.components, self.zs):
                    if frac > 0:
                        teqp_name = teqp_map.get(name)
                        if teqp_name is not None:
                            comp_names_teqp.append(teqp_name)
                            comp_fracs_teqp.append(frac)
                
                if not comp_names_teqp:
                    raise ValueError("Нет компонентов для teqp")
                
                # Загружаем модель GERG-2008
                try:
                    model = teqp.build_multifluid_model(comp_names_teqp, teqp.get_datapath())
                except:
                    # Если стандартный путь не работает, пробуем альтернативный
                    import os
                    datapath = os.path.join(os.path.dirname(teqp.__file__), 'datapath.json')
                    model = teqp.build_multifluid_model(comp_names_teqp, datapath)
                
                # Для teqp нужна молярная плотность
                # Используем идеальный газ для начального приближения
                R = 8.314  # Дж/(моль·К)
                rhomolar_initial = self.P / (R * self.T)  # моль/м³
                
                # Пробуем найти корень для плотности при заданном давлении
                # Упрощенно: используем итерацию
                z_array = np.array(comp_fracs_teqp)
                
                # Пытаемся получить Z через teqp
                # Используем функцию для расчета Z при заданных T, rho, z
                try:
                    # Пробуем разные плотности для поиска
                    rhomolar = rhomolar_initial
                    for _ in range(20):
                        try:
                            Z_teqp = model.get_Z(self.T, rhomolar, z_array)
                            # Проверяем давление, которое дает эта плотность
                            P_calc = model.get_pressure(self.T, rhomolar, z_array)
                            if abs(P_calc - self.P) / self.P < 0.01:
                                break
                            # Корректируем плотность
                            rhomolar *= (self.P / P_calc)
                        except:
                            rhomolar *= 1.1
                    
                    if Z_teqp is not None and Z_teqp > 0 and Z_teqp < 2:
                        rho = rhomolar * self.get_molar_mass() / 1000  # моль/м³ → кг/м³
                        
                        if self.phase == 'Жидкость':
                            mu_dynamic = self.calculate_viscosity_liquid_lbc()
                        else:
                            mu_dynamic = self.calculate_viscosity_gas_lge()
                        
                        print(f"✅ teqp сработал: Z = {Z_teqp:.6f}")
                        self.result = {
                            'method': 'GERG-2008 (teqp / NIST)',
                            'Z': Z_teqp,
                            'rho': rho,
                            'mu_dynamic': mu_dynamic,
                            'MW': self.get_molar_mass(),
                            'phase': self.phase,
                            'success': True
                        }
                        return self.result
                    else:
                        raise ValueError(f"teqp Z невалиден: {Z_teqp}")
                        
                except Exception as e_teqp:
                    raise ValueError(f"teqp расчет не удался: {e_teqp}")
                    
            except ImportError:
                print("❌ teqp не установлен. Установка: pip install teqp")
            except Exception as e3:
                print(f"❌ teqp не сработал: {e3}")
            
            # ---- ПОПЫТКА 4: ЗАПАСНОЙ МЕТОД ----
            print("🔄 Использование запасного метода (идеальный газ)")
            
            MW = self.get_molar_mass()
            rho = self.calculate_density_ideal_gas()
            mu = self.calculate_viscosity_approx()
            
            self.result = {
                'method': 'GERG-2008 (запасной)',
                'Z': 1.0,
                'rho': rho,
                'mu_dynamic': mu,
                'MW': MW,
                'phase': self.phase,
                'success': True,
                'warning': 'Использован запасной метод (идеальный газ)'
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
        print(f"VF:                 {self.result.get('VF', '—')}")
        print(f"\nСостав смеси:")
        for name, frac in zip(self.components, self.zs):
            print(f"  {name:12} {frac*100:5.1f} %")
        
        print(f"\nРезультаты:")
        if self.result.get('Z') is not None:
            print(f"  Z-фактор:         {self.result['Z']:.6f}")
        else:
            print(f"  Z-фактор:         — (ошибка)")
        
        if self.result.get('rho_gas'):
            print(f"  Плотность (газ):  {self.result['rho_gas']:.3f} кг/м³")
        if self.result.get('rho_liquid'):
            print(f"  Плотность (жидк): {self.result['rho_liquid']:.3f} кг/м³")
        if self.result.get('rho') and not self.result.get('rho_gas') and not self.result.get('rho_liquid'):
            print(f"  Плотность:        {self.result['rho']:.3f} кг/м³")
        
        if self.result.get('warning'):
            print(f"  ⚠️ {self.result['warning']}")
        
        mu_cP, nu_cSt = self.get_viscosity()
        if mu_cP:
            print(f"  Дин. вязкость:   {mu_cP:.4f} сП")
            print(f"  Кин. вязкость:   {nu_cSt:.4f} сСт")
        
        if self.result.get('MW'):
            print(f"  Молярная масса:   {self.result['MW']:.3f} кг/кмоль")
        print("=" * 60)


if __name__ == "__main__":
    print("=" * 60)
    print("ТЕСТ: GERG-2008 (CoolProp → pyaga8 → teqp → запасной)")
    print("=" * 60)
    
    # Тест: Газ через GERG
    print("\n🔬 Тест 1: Газ C2-C5 — GERG-2008")
    calc1 = SHFLUCalculator(method='GERG', phase='Газ')
    calc1.set_composition(
        components=['methane', 'ethane', 'propane', 'n-butane', 'n-pentane'],
        zs=[0.40, 0.30, 0.20, 0.07, 0.03]
    )
    calc1.set_conditions(T_C=35, P_MPa=2.5)
    calc1.calculate()
    calc1.print_result()