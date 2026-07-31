# test.py - проверка установки

print("=" * 40)
print("ПРОВЕРКА УСТАНОВКИ БИБЛИОТЕК")
print("=" * 40)

# Проверяем библиотеки
try:
    import thermo
    print(f"✅ thermo - установлена (версия {thermo.__version__})")
except ImportError:
    print("❌ thermo - НЕ установлена")

try:
    import numpy as np
    print(f"✅ numpy - установлена (версия {np.__version__})")
except ImportError:
    print("❌ numpy - НЕ установлена")

try:
    import scipy
    print(f"✅ scipy - установлена (версия {scipy.__version__})")
except ImportError:
    print("❌ scipy - НЕ установлена")

try:
    import pandas as pd
    print(f"✅ pandas - установлена (версия {pd.__version__})")
except ImportError:
    print("❌ pandas - НЕ установлена")

try:
    import openpyxl
    print(f"✅ openpyxl - установлена (версия {openpyxl.__version__})")
except ImportError:
    print("❌ openpyxl - НЕ установлена")

try:
    import matplotlib
    print(f"✅ matplotlib - установлена (версия {matplotlib.__version__})")
except ImportError:
    print("❌ matplotlib - НЕ установлена")

print("=" * 40)

# Проверка работы Python
import sys
print(f"Python версия: {sys.version}")

print("\n✅ Проверка завершена!")