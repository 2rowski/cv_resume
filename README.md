# CV – Michał Tworowski

Strona CV (EN/PL) i PDF-y generowane z jednego pliku: [`cv.yaml`](cv.yaml).

## Jak zaktualizować CV

1. Edytuj `cv.yaml` (każdy tekst ma wersję `en` i `pl`).
2. Zbuduj:
   ```
   .venv\Scripts\python build.py
   ```
3. Wynik:
   - `docs/index.html` – strona WWW (publikowana przez GitHub Pages)
   - `docs/*_CV_EN.pdf`, `docs/*_CV_PL.pdf` – PDF-y do pobrania ze strony (bez telefonu)
   - `out/*_CV_EN.pdf`, `out/*_CV_PL.pdf` – PDF-y do wysyłki rekruterom (z telefonem, nie trafiają do repozytorium)

## Pierwsze uruchomienie na nowym komputerze

```
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

Telefon trzymany jest w `private.yaml` (poza repozytorium):

```yaml
phone: "+48 ..."
```

PDF-y drukuje zainstalowana przeglądarka Edge lub Chrome w trybie headless.
