"""
calculator.py - Ядро расчетов свойств углеводородов
Метод: Пенга-Робинсон
Поддерживаемые компоненты: He, H2, O2, N2, CO2, C1-C10, бензол, толуол
Поддержка чистых сред (100% одного компонента)
Расчет влагосодержания (ppmV) и предупреждение о газогидратах
"""

from thermo import ChemicalConstantsPackage, PRMIX, CEOSGas, CEOSLiquid, FlashVL
from thermo.interaction_parameters import IPDB
import math


class SHFLUCalculator:
    """Калькулятор свойств углеводородных смесей (Пенга-Робинсон)"""
    
    def __init__(self, method='PR', phase='Газ'):
        self.method = method
        self.phase = phase
        self.components = []
        self.zs = []
        self.T = None
        self.P = None
        self.result = None
        self.is_pure = False
        
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
        self.is_pure = (len(components) == 1)
    
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
    # ВЯЗКОСТЬ ЖИДКОСТИ: LBC
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
    # ВЯЗКОСТЬ ГАЗА: LGE
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
    
    def calculate_viscosity_approx(self):
        MW = self.get_molar_mass()
        mu_cP = 0.0005 * (MW ** 0.5) * (self.T ** 0.5) / 100
        mu_cP = max(0.001, min(mu_cP, 10))
        return mu_cP * 0.001
    
    # ============================================================
    # ПЛОТНОСТЬ
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
    # ВЛАГОСОДЕРЖАНИЕ (ppmV) + ГИДРАТЫ
    # ============================================================
    
    def calculate_water_content(self):
        """
        Расчет влагосодержания в объемных ppm.
        Учитывает CO2 по упрощенному методу Маддокса.
        Возвращает: (water_ppm, warning)
        """
        T_C = self.T - 273.15
        P_MPa = self.P / 1e6
        
        # Мольная доля CO2
        y_co2 = 0.0
        for name, frac in zip(self.components, self.zs):
            if name == 'co2':
                y_co2 = frac
                break
        
        # Давление насыщения воды (или льда)
        if T_C >= 0:
            A, B, C = 8.07131, 1730.63, 233.426
            P_sat_mmHg = 10 ** (A - B / (C + T_C))
        else:
            A, B, C = 9.5041, 2663.5, 272.5
            P_sat_mmHg = 10 ** (A - B / (C + T_C))
        P_sat_MPa = P_sat_mmHg * 0.000133322
        
        # Влагосодержание сладкой части (Букачек) в lbm/MMscf
        log_B = -1713.66 / (273.15 + T_C) + 6.69449
        W_HC_lbm = 47484 * P_sat_MPa / P_MPa + (10 ** log_B)
        
        # Учет CO2 (упрощенный Маддокс: W_CO2 ~ 0.75 * W_HC)
        W_CO2_eff = 0.75 * W_HC_lbm
        W_total_lbm = (1 - y_co2) * W_HC_lbm + y_co2 * W_CO2_eff
        
        # Перевод lbm/MMscf → ppm (объемные)
        W_ppm = W_total_lbm * 1.96
        
        # Предупреждение о гидратах (только для газа)
        warning = None
        if self.phase == 'Газ':
            HFT = self.estimate_hydrate_formation_temperature()
            if HFT is not None and T_C < HFT + 2:
                warning = (f"⚠️ Возможно образование газогидратов. "
                           f"Температура гидратообразования ≈ {HFT:.1f} °C, "
                           f"фактическая T = {T_C:.1f} °C при P = {P_MPa:.1f} МПа.")
        
        return W_ppm, warning
    
    def estimate_hydrate_formation_temperature(self):
        """Оценка температуры гидратообразования (HFT) по упрощенной корреляции"""
        P_MPa = self.P / 1e6
        if P_MPa < 0.5:
            return None
        
        y_co2 = 0.0
        y_hydrate_formers = 0.0
        for name, frac in zip(self.components, self.zs):
            if name == 'co2':
                y_co2 = frac
            if name in ['methane', 'ethane', 'propane', 'n-butane', 'i-butane', 'co2']:
                y_hydrate_formers += frac
        
        if y_hydrate_formers < 0.01:
            return None
        
        HFT_CH4 = 8.9 * math.log(P_MPa) - 12.5
        HFT = HFT_CH4 - 0.5 * (y_co2 * 100)
        HFT = max(-20, min(HFT, 25))
        
        return HFT
    
    # ============================================================
    # ОСНОВНОЙ РАСЧЕТ ПО ПЕНГА-РОБИНСОНУ
    # ============================================================
    
    def calculate_PR(self):
        try:
            constants, properties = ChemicalConstantsPackage.from_IDs(self.components)
            
            if self.is_pure:
                kijs = None
            else:
                kijs = IPDB.get_ip_asymmetric_matrix('ChemSep PR', constants.CASs, 'kij')
            
            eos_kwargs = {
                'Pcs': constants.Pcs, 'Tcs': constants.Tcs,
                'omegas': constants.omegas
            }
            if kijs is not None:
                eos_kwargs['kijs'] = kijs
            
            gas = CEOSGas(PRMIX, eos_kwargs=eos_kwargs,
                         HeatCapacityGases=properties.HeatCapacityGases)
            liquid = CEOSLiquid(PRMIX, eos_kwargs=eos_kwargs,
                               HeatCapacityGases=properties.HeatCapacityGases)
            
            flasher = FlashVL(constants, properties, liquid=liquid, gas=gas)
            result = flasher.flash(T=self.T, P=self.P, zs=self.zs)
            
            Z = result.Z()
            VF = getattr(result, 'VF', None)
            
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
            
            if mu_dynamic is None or mu_dynamic <= 0:
                mu_dynamic = self.calculate_viscosity_approx()
            
            if self.is_pure:
                method_name = f'Пенга-Робинсон (чистый {self.components[0]})'
            else:
                method_name = 'Пенга-Робинсон'
            
            self.result = {
                'method': method_name,
                'Z': Z if Z is not None else None,
                'rho_gas': rho_gas,
                'rho_liquid': rho_liquid,
                'MW': self.get_molar_mass(),
                'VF': VF,
                'mu_dynamic': mu_dynamic,
                'phase': self.phase,
                'is_pure': self.is_pure,
                'success': True
            }
            
            water_ppm, water_warning = self.calculate_water_content()
            self.result['water_ppm'] = water_ppm
            self.result['water_warning'] = water_warning
            
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
                'is_pure': self.is_pure,
                'success': False,
                'error': str(e),
                'water_ppm': None,
                'water_warning': None
            }
            return self.result
    
    def calculate(self):
        return self.calculate_PR()
    
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
        print(f"Чистая среда:       {'Да' if self.is_pure else 'Нет'}")
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
        
        mu_cP, nu_cSt = self.get_viscosity()
        if mu_cP:
            print(f"  Дин. вязкость:   {mu_cP:.4f} сП")
            print(f"  Кин. вязкость:   {nu_cSt:.4f} сСт")
        
        if self.result.get('water_ppm') is not None:
            print(f"  Влагосодержание: {self.result['water_ppm']:.1f} ppmV")
        if self.result.get('water_warning'):
            print(f"  ⚠️ {self.result['water_warning']}")
        
        if self.result.get('MW'):
            print(f"  Молярная масса:   {self.result['MW']:.3f} кг/кмоль")
        print("=" * 60)


if __name__ == "__main__":
    print("=" * 60)
    print("ТЕСТ: ПЕНГА-РОБИНСОН + ВЛАГОСОДЕРЖАНИЕ")
    print("=" * 60)
    
    print("\n🔬 Тест 1: Смесь с CO2 (газ)")
    calc1 = SHFLUCalculator(method='PR', phase='Газ')
    calc1.set_composition(
        components=['methane', 'ethane', 'propane', 'co2'],
        zs=[0.80, 0.10, 0.05, 0.05]
    )
    calc1.set_conditions(T_C=35, P_MPa=5.0)
    calc1.calculate()
    calc1.print_result()
    
    print("\n🔬 Тест 2: Чистый метан (газ)")
    calc2 = SHFLUCalculator(method='PR', phase='Газ')
    calc2.set_composition(components=['methane'], zs=[1.0])
    calc2.set_conditions(T_C=20, P_MPa=8.0)
    calc2.calculate()
    calc2.print_result()
    
    print("\n🔬 Тест 3: Газ при -10°C, 8 МПа (риск гидратов)")
    calc3 = SHFLUCalculator(method='PR', phase='Газ')
    calc3.set_composition(
        components=['methane', 'ethane', 'co2'],
        zs=[0.90, 0.05, 0.05]
    )
    calc3.set_conditions(T_C=-10, P_MPa=8.0)
    calc3.calculate()
    calc3.print_result()