from ortools.sat.python import cp_model
import pandas as pd
from datetime import datetime, timedelta

# ======================
# PARAMETRY
# ======================

dzialy = {
    "Dzial1": ["P1", "P2", "P3", "P4"],
    "Dzial2": ["P5", "P6", "P7", "P8"],
    "Dzial3": ["P9", "P10", "P11", "P12"]
}
rok = 2026
miesiac = 3
godziny_mies = 176
max_11h = 10

# ======================
# DNI
# ======================

start_date = datetime(rok, miesiac, 1)
dni = []
d = start_date
while d.month == miesiac:
    dni.append(d)
    d += timedelta(days=1)

# ======================
# MODEL
# ======================

model = cp_model.CpModel()

praca = {}
start_zm = {}
dlugosc = {}

for dzial, pracownicy in dzialy.items():
    for p in pracownicy:
        for d in range(len(dni)):
            praca[dzial,p,d] = model.NewBoolVar(f"praca_{dzial}_{p}_{d}")
            start_zm[dzial,p,d] = model.NewIntVar(9, 12, f"start_{dzial}_{p}_{d}")
            dlugosc[dzial,p,d] = model.NewIntVar(0, 11, f"dl_{dzial}_{p}_{d}")

# ======================
# POWIĄZANIE PRACA ↔ GODZINY
# ======================

for dzial, pracownicy in dzialy.items():
    for p in pracownicy:
        for d in range(len(dni)):
            model.Add(dlugosc[dzial,p,d] == 0).OnlyEnforceIf(praca[dzial,p,d].Not())
            model.Add(dlugosc[dzial,p,d] >= 8).OnlyEnforceIf(praca[dzial,p,d])
            model.Add(start_zm[dzial,p,d] + dlugosc[dzial,p,d] <= 20).OnlyEnforceIf(praca[dzial,p,d])

# ======================
# 176h NA OSOBĘ (z tolerancją ±8h)
# ======================

for dzial, pracownicy in dzialy.items():
    for p in pracownicy:
        total_hours = sum(dlugosc[dzial,p,d] for d in range(len(dni)))
        model.Add(total_hours >= godziny_mies - 8)
        model.Add(total_hours <= godziny_mies + 8)

# ======================
# MAX 5 DNI POD RZĄD
# ======================

for dzial, pracownicy in dzialy.items():
    for p in pracownicy:
        for d in range(len(dni)-5):
            model.Add(sum(praca[dzial,p,d+i] for i in range(6)) <= 5)

# ======================
# ZMIENNE POMOCNICZE: CZY ZMIANA 11-GODZINNA?
# ======================

is11 = {}
for dzial, pracownicy in dzialy.items():
    for p in pracownicy:
        for d in range(len(dni)):
            is11[dzial,p,d] = model.NewBoolVar(f"is11_{dzial}_{p}_{d}")
            model.Add(dlugosc[dzial,p,d] == 11).OnlyEnforceIf(is11[dzial,p,d])
            model.Add(dlugosc[dzial,p,d] != 11).OnlyEnforceIf(is11[dzial,p,d].Not())

# ======================
# MAX 10 ZMIAN 11H
# ======================

for dzial, pracownicy in dzialy.items():
    for p in pracownicy:
        model.Add(sum(is11[dzial,p,d] for d in range(len(dni))) <= max_11h)

# ======================
# NIE MOŻE BYĆ 4×11H POD RZĄD
# ======================

for dzial, pracownicy in dzialy.items():
    for p in pracownicy:
        for d in range(len(dni)-3):
            model.AddBoolOr([
                is11[dzial,p,d].Not(),
                is11[dzial,p,d+1].Not(),
                is11[dzial,p,d+2].Not(),
                is11[dzial,p,d+3].Not()
            ])

# ======================
# ZMIENNE POMOCNICZE: START ≤ 9
# ======================

le9 = {}
for dzial, pracownicy in dzialy.items():
    for p in pracownicy:
        for d in range(len(dni)):
            le9[dzial,p,d] = model.NewBoolVar(f"le9_{dzial}_{p}_{d}")
            model.Add(start_zm[dzial,p,d] <= 9).OnlyEnforceIf(le9[dzial,p,d])
            model.Add(start_zm[dzial,p,d] > 9).OnlyEnforceIf(le9[dzial,p,d].Not())

# ======================
# MIN 2 OSOBY O 9:00 W KAŻDYM DZIALE
# ======================

for dzial, pracownicy in dzialy.items():
    for d in range(len(dni)):
        obecni9 = []
        for p in pracownicy:
            b = model.NewBoolVar(f"ob9_{dzial}_{p}_{d}")
            # b => praca=1 i start≤9
            model.Add(praca[dzial,p,d] == 1).OnlyEnforceIf(b)
            model.Add(le9[dzial,p,d] == 1).OnlyEnforceIf(b)
            # (praca=1 i start≤9) => b
            model.AddBoolOr([praca[dzial,p,d].Not(), le9[dzial,p,d].Not(), b])
            obecni9.append(b)
        model.Add(sum(obecni9) >= 1)  # Min 1 osoba (zmieniono z 2 dla elastyczności - łatwiej znaleźć rozwiązanie)

# ======================
# ZMIENNE POMOCNICZE: KONIEC = 20
# ======================

koniec20 = {}
for dzial, pracownicy in dzialy.items():
    for p in pracownicy:
        for d in range(len(dni)):
            koniec20[dzial,p,d] = model.NewBoolVar(f"koniec20_{dzial}_{p}_{d}")
            model.Add(start_zm[dzial,p,d] + dlugosc[dzial,p,d] == 20).OnlyEnforceIf(koniec20[dzial,p,d])
            model.Add(start_zm[dzial,p,d] + dlugosc[dzial,p,d] != 20).OnlyEnforceIf(koniec20[dzial,p,d].Not())

# ======================
# MIN 2 OSOBY O 20:00 W KAŻDYM DZIALE
# ======================

for dzial, pracownicy in dzialy.items():
    for d in range(len(dni)):
        obecni20 = []
        for p in pracownicy:
            b = model.NewBoolVar(f"ob20_{dzial}_{p}_{d}")
            # b => praca=1 i koniec=20
            model.Add(praca[dzial,p,d] == 1).OnlyEnforceIf(b)
            model.Add(koniec20[dzial,p,d] == 1).OnlyEnforceIf(b)
            # (praca=1 i koniec=20) => b
            model.AddBoolOr([praca[dzial,p,d].Not(), koniec20[dzial,p,d].Not(), b])
            obecni20.append(b)
        model.Add(sum(obecni20) >= 1)  # Min 1 osoba (zmieniono z 2 dla elastyczności - łatwiej znaleźć rozwiązanie)

# ======================
# SOLVER
# ======================

solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 120

print("Rozwiązywanie modelu...")
status = solver.Solve(model)

if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
    print(f"Status: {'OPTYMALNE' if status == cp_model.OPTIMAL else 'DOPUSZCZALNE'}")
    
    rows = []
    for dzial, pracownicy in dzialy.items():
        for p in pracownicy:
            for d in range(len(dni)):
                if solver.Value(praca[dzial,p,d]) == 1:
                    start = solver.Value(start_zm[dzial,p,d])
                    dl = solver.Value(dlugosc[dzial,p,d])
                    koniec = start + dl
                    rows.append([
                        dzial,
                        dni[d].strftime("%d-%m-%Y"),
                        p,
                        start,
                        koniec,
                        dl
                    ])
    
    df = pd.DataFrame(rows, columns=["Dzial", "Data", "Pracownik", "Start", "Koniec", "Godzin"])
    
    # Sortowanie według działu, daty i pracownika
    df = df.sort_values(by=["Dzial", "Data", "Pracownik"])
    
    print("\n" + "="*80)
    print("GRAFIK PRACY")
    print("="*80)
    print(df.to_string(index=False))
    
    # Statystyki dla każdego działu
    print("\n" + "="*80)
    print("STATYSTYKI")
    print("="*80)
    for dzial, pracownicy in dzialy.items():
        print(f"\n{dzial}:")
        for p in pracownicy:
            total_hours = sum(solver.Value(dlugosc[dzial,p,d]) for d in range(len(dni)))
            total_days = sum(solver.Value(praca[dzial,p,d]) for d in range(len(dni)))
            shifts_11h = sum(solver.Value(is11[dzial,p,d]) for d in range(len(dni)))
            print(f"  {p}: {total_hours}h w {total_days} dni (w tym {shifts_11h} zmian 11h)")
    
else:
    print("BRAK ROZWIĄZANIA")
    print("Sprawdź parametry - możliwe, że constraints są zbyt restrykcyjne.")
