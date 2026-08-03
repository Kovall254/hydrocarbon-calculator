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
        """
        method: 'PR' - Пенга-Робинсон, 'GERG' - GERG-2008
        phase: 'Газ' или 'Жидкость'
        """
        self.method = method
        self.phase = phase
        self.components = []
        self.zs = []
        self.T = None
        self.P = None
        self.result = None
        
        # Молярные массы компонентов (кг/кмоль)
        self.MW_map = {
            'methane': 16.043,
            'ethane': 30.070,
            'propane': 44.097,
            'nitrogen': 28.013,
            'co2': 44.010,
            'n-butane': 58.123,
            'i-butane': 58.123,
            'n-pentane': 72.151,
            'i-pentane': 72.151,
            'benzene': 78.114,
            'toluene': 92.141,
            'hexane': 86.178,
            'heptane': 100.205,
            'octane': 114.232,
            'nonane': 128.259,
            'decane': 142.286,
            'helium': 4.003,
            'hydrogen': 2.016,
            'oxygen': 32.000
        }
        
        # Ацентрические факторы
        self.omega_map = {
            'methane': 0.011,
            'ethane': 0.099,
            'propane': 0.152,
            'nitrogen': 0.037,
            'co2': 0.225,
            'n-butane': 0.200,
            'i-butane': 0.184,
            'n-pentane': 0.251,
            'i-pentane': 0.227,
            'benzene': 0.212,
            'toluene': 0.264,
            'hexane': 0.299,
            'heptane': 0.349,
            'octane': 0.398,
            'nonane': 0.443,
            'decane': 0.488,
            'helium': -0.365,
            'hydrogen': -0.220,
            'oxygen': 0.022
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
            'benzene': 562.16,
            'toluene': 591.80,
            'hexane': 507.60, 'heptane': 540.20,
            'octane': 568.70, 'nonane': 594.60, 'decane': 617.70,
            'helium': 5.20, 'hydrogen': 33.18, 'oxygen': 154.58
        }
        
        Pc_map = {
            'methane': 4.599, 'ethane': 4.872, 'propane': 4.248,
            'nitrogen': 3.398, 'co2': 7.377,
            'n-butane': 3.796, 'i-butane': 3.648,
            'n-pentane': 3.370, 'i-pentane': 3.380,
            'benzene': 4.898,
            'toluene': 4.108,
            'hexane': 3.010, 'heptane': 2.740,
            'octane': 2.490, 'nonane': 2.290, 'decane': 2.110,
            'helium': 0.227, 'hydrogen': 1.297, 'oxygen': 5.043
        }
        
        for name, frac in zip(self.components, self.zs):
            Tc_mix += frac * Tc_map.get(name, 500)
            Pc_mix += frac * Pc_map.get(name, 4.0)
            omega_mix += frac * self.omega_map.get(name, 0.2)
        
        return Tc_mix, Pc_mix, omega_mix
    
    def calculate_viscosity_gas(self):
        """Расчет вязкости газа по методу Лету-Уотсона (LBC)"""
        try:
            MW = self.get_molar_mass()
            Tc_mix, Pc_mix, omega_mix = self.get_critical_params()
            
            Tr = self.T / Tc_mix
            Pr = self.P / (Pc_mix * 1e6)
            
            xi = (Tc_mix ** (1/6)) / (MW ** 0.5 * (Pc_mix * 1e6) ** (2/3))
            
            if self.phase == 'Жидкость':
                rho_liquid = self.result.get('rho_liquid') or self.result.get('rho') or 1.0
            else:
                rho_liquid = self.result.get('rho_gas') or self.result.get('rho') or 1.0
            
            rho_red = rho_liquid / (MW * Pc_mix / (0.008314 * Tc_mix))
            
            a1, a2, a3, a4 = 0.1023, 0.023364, 0.058533, -0.040758
            a5, a6, a7 = 0.0093324, -0.0001556, 0.0000016
            
            if rho_red > 0:
                mu_star = (a1 + a2*rho_red + a3*rho_red**2 + a4*rho_red**3 + 
                          a5*rho_red**4 + a6*rho_red**5 + a7*rho_red**6)
            else:
                mu_star = 0
            
            mu_cP = mu_star * xi
            
            if omega_mix > 0.3:
                mu_cP *= (1 + 0.5 * (omega_mix - 0.3))
            
            if mu_cP < 0.001:
                mu_cP = 0.001
            if mu_cP > 10:
                mu_cP = 10
            
            return mu_cP * 0.001
            
        except:
            return self.calculate_viscosity_approx()
    
    def calculate_viscosity_approx(self):
        MW = self.get_molar_mass()
        mu_cP = 0.0005 * (MW ** 0.5) * (self.T ** 0.5) / 100
        if mu_cP < 0.001:
            mu_cP = 0.001
        if mu_cP > 10:
            mu_cP = 10
        return mu_cP * 0.001
    
    def calculate_PR(self):
        try:
            constants, properties = ChemicalConstantsPackage.from_IDs(self.components)
            
            kijs = IPDB.get_ip_asymmetric_matrix('ChemSep PR', constants.CASs, 'kij')
            
            eos_kwargs = {
                'Pcs': constants.Pcs,
                'Tcs': constants.Tcs,
                'omegas': constants.omegas,
                'kijs': kijs
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
            
            if self.phase == 'Жидкость':
                if hasattr(result, 'liquid') and result.liquid is not None:
                    try:
                        rho_liquid = result.liquid.rho_mass()
                        mu_dynamic = result.liquid.mu()
                    except:
                        pass
                if mu_dynamic is None and hasattr(result, 'gas') and result.gas is not None:
                    try:
                        rho_gas = result.gas.rho_mass()
                        mu_dynamic = result.gas.mu()
                    except:
                        pass
            else:
                if hasattr(result, 'gas') and result.gas is not None:
                    try:
                        rho_gas = result.gas.rho_mass()
                        mu_dynamic = result.gas.mu()
                    except:
                        pass
                if mu_dynamic is None and hasattr(result, 'liquid') and result.liquid is not None:
                    try:
                        rho_liquid = result.liquid.rho_mass()
                        mu_dynamic = result.liquid.mu()
                    except:
                        pass
            
            if mu_dynamic is None:
                self.result = {
                    'method': 'Пенга-Робинсон',
                    'Z': result.Z(),
                    'rho_gas': rho_gas,
                    'rho_liquid': rho_liquid,
                    'MW': self.get_molar_mass(),
                    'VF': VF,
                    'mu_dynamic': None,
                    'phase': self.phase,
                    'success': True
                }
                mu_dynamic = self.calculate_viscosity_gas()
            
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
            self.result = {
                'method': 'Пенга-Робинсон',
                'error': str(e),
                'success': False
            }
            return self.result
    
    def calculate_GERG(self):
        try:
            from CoolProp.CoolProp import PropsSI
            
            name_map = {
                'methane': 'Methane',
                'ethane': 'Ethane',
                'propane': 'Propane',
                'nitrogen': 'Nitrogen',
                'co2': 'CarbonDioxide',
                'n-butane': 'n-Butane',
                'i-butane': 'isoButane',
                'n-pentane': 'n-Pentane',
                'i-pentane': 'isoPentane',
                'benzene': 'Benzene',
                'toluene': 'Toluene',
                'hexane': 'n-Hexane',
                'heptane': 'n-Heptane',
                'octane': 'n-Octane',
                'nonane': 'n-Nonane',
                'decane': 'n-Decane',
                'helium': 'Helium',
                'hydrogen': 'Hydrogen',
                'oxygen': 'Oxygen'
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
                mu_dynamic = PropsSI('VISCOSITY', 'T', self.T, 'P', self.P, mixture_str)
            except:
                mu_dynamic = None
            
            MW = self.get_molar_mass()
            
            if mu_dynamic is None:
                self.result = {
                    'method': 'GERG-2008 (CoolProp)',
                    'Z': Z,
                    'rho': rho,
                    'mu_dynamic': None,
                    'MW': MW,
                    'phase': self.phase,
                    'success': True
                }
                mu_dynamic = self.calculate_viscosity_gas()
            
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
                'error': str(e),
                'success': False
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
            mu = self.calculate_viscosity_gas()
            self.result['mu_dynamic'] = mu
        
        if mu is None:
            return None, None
        
        mu_cP = mu * 1000
        rho = self.result.get('rho_gas') or self.result.get('rho_liquid') or self.result.get('rho') or 1.0
        nu_cSt = (mu / rho) * 1e6
        
        return mu_cP, nu_cSt
    
    def print_result(self):
        if not self.result or not self.result.get('success', False):
            print("❌ Ошибка расчета:", self.result.get('error', 'Неизвестная ошибка'))
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
        print(f"  Z-фактор:         {self.result['Z']:.6f}")
        
        if self.result.get('rho_gas') is not None:
            print(f"  Плотность (газ):  {self.result['rho_gas']:.3f} кг/м³")
        if self.result.get('rho_liquid') is not None:
            print(f"  Плотность (жидк): {self.result['rho_liquid']:.3f} кг/м³")
        if self.result.get('rho') is not None and self.result.get('rho_gas') is None and self.result.get('rho_liquid') is None:
            print(f"  Плотность:        {self.result['rho']:.3f} кг/м³")
        
        if self.result.get('VF') is not None:
            print(f"  Доля газа (об.):  {self.result['VF']*100:.2f} %")
        
        mu_cP, nu_cSt = self.get_viscosity()
        if mu_cP is not None:
            print(f"  Дин. вязкость:   {mu_cP:.4f} сП")
            print(f"  Кин. вязкость:   {nu_cSt:.4f} сСт")
        else:
            print(f"  Вязкость:        —")
        
        if 'MW' in self.result and self.result['MW'] is not None:
            print(f"  Молярная масса:   {self.result['MW']:.3f} кг/кмоль")
        print("=" * 60)


if __name__ == "__main__":
    print("=" * 60)
    print("КАЛЬКУЛЯТОР СВОЙСТВ УГЛЕВОДОРОДОВ (ТЕСТ)")
    print("=" * 60)
    
    # Тест для газа
    calc = SHFLUCalculator(method='PR', phase='Газ')
    calc.set_composition(
        components=['methane', 'ethane', 'propane', 'nitrogen', 'benzene', 'toluene'],
        zs=[0.70, 0.10, 0.05, 0.03, 0.07, 0.05]
    )
    calc.set_conditions(T_C=35, P_MPa=2.5)
    calc.calculate()
    calc.print_result()
    
    print("\n" + "=" * 60)
    
    # Тест для жидкости
    calc_liq = SHFLUCalculator(method='PR', phase='Жидкость')
    calc_liq.set_composition(
        components=['methane', 'ethane', 'propane', 'n-butane', 'hexane'],
        zs=[0.30, 0.20, 0.20, 0.15, 0.15]
    )
    calc_liq.set_conditions(T_C=25, P_MPa=0.5)
    calc_liq.calculate()
    calc_liq.print_result()