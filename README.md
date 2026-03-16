# Automatyczne Układanie Grafiku Pracowników

Narzędzie do automatycznego generowania grafików pracy dla pracowników firmy z wykorzystaniem algorytmów optymalizacyjnych (Google OR-Tools).

## Funkcjonalność

- **3 działy po 4 pracowników** (12 osób całkowicie)
- **Automatyczne układanie grafiku** na dowolny miesiąc
- **Wymagania pracownicze:**
  - 176 godzin pracy na miesiąc na osobę (z tolerancją ±8h dla elastyczności)
  - Maksymalnie 5 dni pracy pod rząd
  - Maksymalnie 10 zmian 11-godzinnych w miesiącu
  - Brak możliwości 4 zmian 11-godzinnych pod rząd
- **Wymagania firmowe:**
  - Minimum 1 osoba w każdym dziale o godzinie 9:00
  - Minimum 1 osoba w każdym dziale o godzinie 20:00
- **Zmiany:** 
  - Start: między 9:00 a 12:00
  - Długość: 8-11 godzin
  - Koniec: maksymalnie o 20:00

## Instalacja

1. Zainstaluj wymagane biblioteki:
```bash
pip install -r requirements.txt
```

## Użycie

```bash
python scheduler.py
```

Program wygeneruje grafik dla marca 2026 roku i wyświetli:
- Pełny grafik z podziałem na działy, daty, pracowników, godziny rozpoczęcia i zakończenia zmian
- Statystyki dla każdego pracownika (łączna liczba godzin, dni roboczych, zmian 11-godzinnych)

## Dostosowanie Parametrów

W pliku `scheduler.py` możesz zmienić następujące parametry:

```python
# Struktura działów i pracowników
dzialy = {
    "Dzial1": ["P1", "P2", "P3", "P4"],
    "Dzial2": ["P5", "P6", "P7", "P8"],
    "Dzial3": ["P9", "P10", "P11", "P12"]
}

# Okres
rok = 2026
miesiac = 3

# Wymagania
godziny_mies = 176  # Wymagane godziny pracy na miesiąc
max_11h = 10        # Maksymalna liczba zmian 11-godzinnych
```

## Planowane Rozszerzenia

- [ ] Obsługa urlopów (dni wolne dla wybranych pracowników)
- [ ] Obsługa pracy w niedziele
- [ ] Dni z większą obsadą (więcej pracowników w wybranych dniach)
- [ ] Różne wymagania godzinowe dla różnych działów
- [ ] Eksport grafiku do pliku Excel lub PDF
- [ ] Interfejs graficzny (GUI)

## Wymagania Systemowe

- Python 3.7 lub nowszy
- Google OR-Tools
- Pandas

## Jak Działa?

Program wykorzystuje **Constraint Programming** (programowanie z ograniczeniami) z biblioteki Google OR-Tools. Model matematyczny definiuje:

1. **Zmienne decyzyjne:**
   - Czy pracownik pracuje danego dnia
   - Godzina rozpoczęcia zmiany
   - Długość zmiany

2. **Ograniczenia (constraints):**
   - Łączna liczba godzin
   - Maksymalna liczba dni pod rząd
   - Minimalna obsada w kluczowych godzinach
   - Limity zmian długich

3. **Solver** znajduje rozwiązanie spełniające wszystkie ograniczenia lub informuje, że takie rozwiązanie nie istnieje.

## Troubleshooting

**Problem: "BRAK ROZWIĄZANIA"**
- Sprawdź czy parametry nie są zbyt restrykcyjne
- Zwiększ `max_time_in_seconds` w solverze
- Zmniejsz wymagania (np. więcej maksymalnych zmian 11h, mniejsza minimalna obsada)

**Problem: Solver działa zbyt długo**
- Zwiększ `solver.parameters.max_time_in_seconds`
- Upewnij się, że wszystkie parametry są realistyczne

## Licencja

Projekt open-source do użytku wewnętrznego firmy.
