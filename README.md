# README
Vítejte v projektu jednoduché webové aplikace pro správu knih a knihoven, postavené na architektuře Flask. Níže naleznete informace o instalaci, spuštění a základním použití.
## 1. Přehled
Tento projekt umožňuje:
- Prohlížet dostupné knihovny (knihovny zde reprezentují „bookshelves“).
- Přidávat knihy do vybraných knihoven.
- Odebírat knihy z knihoven.
- Vyhledávat knihy podle klíčových slov.
- Získávat personalizovaná doporučení na základě obsahu konkrétní knihovny.

## 2. Požadavky
- Python 3.13 nebo vyšší.
- Balíčky uvedené v souboru requirements (případně je lze nainstalovat ručně – například Flask, requests atp.).
- Google Books API (je vyžadováno pro některé funkce komunikující se službou Google Books – je nutné mít příslušné klientské ID a tajný klíč).

## 3. Instalace
1. Naklonujte si projekt do svého prostředí:
``` bash
   git clone https://example.com/your-repo.git](https://github.com/Mopstar/Semestralni_projekt.git
```
1. Přejděte do složky s projektem:
``` bash
   cd your-repo
```
1. Nainstalujte potřebné balíčky:
``` bash
   pip install -r requirements.txt
```
Pokud není k dispozici soubor requirements.txt, můžete nainstalovat jednotlivé balíčky ručně, např.:
``` bash
   pip install Flask requests
```

## 4. Konfigurace
Některé funkce využívají Google Books API s OAuth 2.0. Proto je potřeba nastavit proměnné prostředí (např. v .env nebo systémově) pro správné fungování autentizace:
- CLIENT_ID
- CLIENT_SECRET
- AUTHORIZATION_BASE_URL
- TOKEN_URL
- REDIRECT_URI

Tyto údaje získáte v Google API Console. Ujistěte se, že jsou nastaveny před spuštěním aplikace.
## 5. Spuštění aplikace
1. Ujistěte se, že máte správně nastavené proměnné prostředí.
2. Spusťte aplikaci příkazem:
``` bash
   python main.py
```
Aplikace se spustí na adrese například [http://127.0.0.1:5000](http://127.0.0.1:5000) (dle konfigurace Flasku).
## 6. Základní použití
- **Knihovny (bookshelves)**:
Na úvodní stránce lze přejít ke správě dostupných „polic“ (tzv. bookshelves).
- **Přidání knihy**:
Prostřednictvím formuláře zadáte ID knihovny a ID knihy, čímž knihu do dané knihovny přidáte.
- **Odebrání knihy**:
Zadáním ID knihovny a ID knihy lze knihu z vybrané knihovny odebrat.
- **Vyhledávání**:
Lze vyhledávat knihy dle zadaného klíčového slova.
- **Personalizovaná doporučení**:
Pokud zvolíte konkrétní knihovnu, aplikace se pokusí na základě obsahu nabídnout podobné nebo doporučené knihy.

## 7. Struktura projektu
- Hlavní spouštěcí soubor aplikace se nachází v souboru `main.py`.
- Šablony a styly se nacházejí v samostatných HTML souborech.
- Logika pro přidání, odebrání a vyhledávání knih je definována v příslušných funkcích ve `main.py`.
