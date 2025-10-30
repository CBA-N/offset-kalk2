# Wyniki testu cachowania formularza (Playwright)

Uruchomiono skrypt Playwright, który:

1. Wypełnił formularz kalkulatora niestandardowymi wartościami (nazwa produktu, nakład, rodzaj pracy, papier, gramatura, kolorystyka, kontrahent, opcjonalne dodatki oraz konfiguracja kosztów).
2. Przeszedł do modułu Historii, po czym powrócił na stronę kalkulatora i potwierdził, że wszystkie wartości zostały odtworzone z pamięci przeglądarki.
3. Kliknął przycisk **Wyczyść ofertę** i zweryfikował, że formularz wrócił do wartości domyślnych, a dane w `localStorage` zostały usunięte.

Fragment logu ze skryptu:

```
Cache before clear: {"nazwa_produktu":"Test cache produkt","naklad":"4321","rodzaj_pracy":"Folder A4","format_szerokosc":"210","format_wysokosc":"297","kategoria_papieru":"Powlekany","rodzaj_papieru":"Kreda błysk","gramatura":"170","kolorystyka":"4+4","ilosc_form":"6","pakowanie":"Kartony indywidualne (po 100 szt)","transport":"Kurier paletowy (1 paleta)","marza_procent":"27","priorytet_optymalizacji":"Najniższy koszt","kontrahent_id":"2","kolory_specjalne":["Pantone Metallic"],"uszlachetnienia":["Lakier UV wybiórczy"],"obrobka":["Bigowanie"],"wymaga_ciecia_papieru":false,"odwracanka":false,"odwracanka_bazowa_ilosc_form":6}
Cache after clear: None
Paper selection after clear: None
```
