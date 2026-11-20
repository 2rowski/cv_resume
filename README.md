# CV – Michał Tworowski

**Strona:** https://2rowski.github.io/cv_resume/

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

Telefon i e-mail są w `private.yaml` (poza repozytorium). Telefon trafia tylko do PDF-ów w `out/`, a e-mail na stronę w postaci zakodowanej, żeby nie zbierały go boty:

```yaml
phone: "+48 ..."
email: adres@example.com
```

PDF-y drukuje zainstalowana przeglądarka Edge lub Chrome w trybie headless.

## Prawa / Rights

Treść CV, zdjęcie i dane osobowe w tym repozytorium należą do Michała Tworowskiego. Nie są udostępnione na żadnej wolnej licencji: możesz je przeglądać, ale nie kopiuj ich, nie modyfikuj ani nie publikuj w innym miejscu bez zgody.

The CV content, photo and personal data in this repository belong to Michał Tworowski. They are not released under any open licence: you may view them, but please do not copy, modify or republish them without permission.
