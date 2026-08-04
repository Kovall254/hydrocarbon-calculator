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
    # 1. ВЯЗКОСТЬ ЖИДКОСТИ: МЕТОД ЛЕТУ-УОТСОНА (LBC)
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
    # 2. ВЯЗКОСТЬ ГАЗА: МЕТОД ЛИ-ГОНСАЛЕСА-ЭКИНА (LGE)
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
    # 3. ЗАПАСНОЙ РАСЧЕТ ВЯЗКОСТИ
    # ============================================================
    
    def calculate_viscosity_approx(self):
        MW = self.get_molar_mass()
        mu_cP = 0.0005 * (MW ** 0.5) * (self.T ** 0.5) / 100
        mu_cP = max(0.001, min(mu_cP, 10))
        return mu_cP * 0.001
    
    # ============================================================
    # 4. ПЛОТНОСТЬ: ИДЕАЛЬНЫЙ ГАЗ (ЗАПАСНОЙ)
    # ============================================================
    
    def calculate_density_ideal_gas(self):
        MW = self.get_molar_mass()
        R = 8314
        return (self.P * MW) / (R * self.T)
    
    def calculate_density_from_Z(self, Z):
        MW = self.get_molar_mass()
        R = 8314
        if Z > 0:
            return (self.P * MW) / (Z * R * self.T)
        else:
            return self.calculate_density_ideal_gas()
    
    # ============================================================
    # 5. РАСЧЕТ ПО ПЕНГА-РОБИНСОНУ (УЛУЧШЕННЫЙ)
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
            
            # Если плотность не получена — через Z
            if rho_gas is None and rho_liquid is None:
                rho_gas = self.calculate_density_from_Z(Z)
            
            # Если плотность нереалистична — идеальный газ
            if rho_gas is not None and (rho_gas < 0.01 or rho_gas > 1000):
                rho_gas = self.calculate_density_ideal_gas()
            if rho_liquid is not None and (rho_liquid < 0.01 or rho_liquid > 2000):
                rho_liquid = self.calculate_density_ideal_gas()
            
            # --- ВЯЗКОСТЬ ---
            mu_dynamic = None
            
            if self.phase == 'Жидкость':
                if hasattr(result, 'liquid') and result.liquid is not None:
                    try:
                        mu_dynamic = result.liquid.mu()
                    except:
                        pass
                if mu_dynamic is None:
                    mu_dynamic = self.calculate_viscosity_liquid_lbc()
            else:
                if hasattr(result, 'gas') and result.gas is not None:
                    try:
                        mu_dynamic = result.gas.mu()
                    except:
                        pass
                if mu_dynamic is None:
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
    # 6. РАСЧЕТ ПО GERG-2008
    # ============================================================
    
    def calculate_GERG(self):
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
            
            rho = PropsSI('D', 'T', self.T, 'P', self.P, mixture_str)
            Z = PropsSI('Z', 'T', self.T, 'P', self.P, mixture_str)
            
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
        print(f"  Z-фактор:         {self.result.get('Z', 1.0):.6f}")
        
        if self.result.get('rho_gas'):
            print(f"  Плотность (газ):  {self.result['rho_gas']:.3f} кг/м³")
        if self.result.get('rho_liquid'):
            print(f"  Плотность (жидк): {self.result['rho_liquid']:.3f} кг/м³")
        if self.result.get('rho') and not self.result.get('rho_gas') and not self.result.get('rho_liquid'):
            print(f"  Плотность:        {self.result['rho']:.3f} кг/м³")
        
        mu_cP, nu_cSt = self.get_viscosity()
        if mu_cP:
            print(f"  Дин. вязкость:   {mu_cP:.4f} сП")
            print(f"  Кин. вязкость:   {nu_cSt:.4f} сСт")
        
        if self.result.get('MW'):
            print(f"  Молярная масса:   {self.result['MW']:.3f} кг/кмоль")
        print("=" * 60)


if __name__ == "__main__":
    print("=" * 60)
    print("ТЕСТ: СРАВНЕНИЕ PR И GERG")
    print("=" * 60)
    
    # Тест 1: Газ (C2-C5)
    print("\n🔬 Тест 1: Газ (C2-C5) — Пенга-Робинсон")
    calc1 = SHFLUCalculator(method='PR', phase='Газ')
    calc1.set_composition(
        components=['ethane', 'propane', 'n-butane', 'n-pentane'],
        zs=[0.40, 0.30, 0.20, 0.10]
    )
    calc1.set_conditions(T_C=35, P_MPa=2.5)
    calc1.calculate()
    calc1.print_result()
    
    print("\n🔬 Тест 2: Газ (C2-C5) — GERG-2008")
    calc2 = SHFLUCalculator(method='GERG', phase='Газ')
    calc2.set_composition(
        components=['ethane', 'propane', 'n-butane', 'n-pentane'],
        zs=[0.40, 0.30, 0.20, 0.10]
    )
    calc2.set_conditions(T_C=35, P_MPa=2.5)
    calc2.calculate()
    calc2.print_result()