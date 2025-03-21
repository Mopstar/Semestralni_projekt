from flask.cli import load_dotenv # Načtení proměnných z .env souboru
from requests_oauthlib import OAuth2Session # Správa Oauth 2.0 autorizace a API komunikace
from flask import Flask, redirect, request, session, render_template, url_for # Prvky Flask pro funkčnost web stránek
import os # Poskytuje přístup k proměnným prostředím

load_dotenv() # Načtení proměnných ze souboru .env (CLIENT_ID, CLIENT_SECRET, KEY)

""" Nastavení Flask aplikace """
app = Flask(__name__) # Spuštění Flask aplikace
app.secret_key = os.getenv("KEY") # Zavedení tajného klíče (uložen v .env)

""" Nastavení OAuth 2.0 pro Google Books API """
CLIENT_ID = os.getenv("ID") # Client ID vygenerované v Google Cloud Console (uloženo v .env)
CLIENT_SECRET = os.getenv("SECRET") # Client Secret vygenerované v Google Cloud Console (uloženo v .env)
AUTHORIZATION_BASE_URL = "https://accounts.google.com/o/oauth2/auth" # URL určené pro autorizaci uživatele
TOKEN_URL = "https://accounts.google.com/o/oauth2/token" # URL pro výměnu autorizačního kódu za přístupový token
REDIRECT_URI = "http://127.0.0.1:5000/callback" # URI pro přesměrování (určeno v Google Console)
SCOPE = ['https://www.googleapis.com/auth/books'] # Oprávnění jenž aplikace žádá: přístup k Google Books informacím

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # Povolení HTTP pro testování

@app.route('/')
def home():
    """Přesměrování uživatele na autorizaci OAuth 2.0 přes Google"""
    google = OAuth2Session(CLIENT_ID, scope=SCOPE, redirect_uri=REDIRECT_URI) # Vytvoření OAuth 2.0 spojení s potřebnýmí požadavky a URI pro přesměrování
    authorization_url, state = google.authorization_url(AUTHORIZATION_BASE_URL) # Vytvoření URL autorizace a uložení stavu pro zpětné volání
    session['oauth_state'] = state # Uložení OAuth stavu pro pozdější ověření
    return redirect(authorization_url) # Přesměrování uživatele na autorizační stránky Google


@app.route('/callback')
def callback():
    """ Reakce OAuth po autorizaci uživatele. """
    """ Vyměna autorizační kód za přístupový token a načtení uživatelovy knihovny."""
    google = OAuth2Session(CLIENT_ID, state=session['oauth_state'], redirect_uri=REDIRECT_URI) # Obnovení OAuth 2.0 relace pomocí uloženého stavu a URI přesměrování
    token = google.fetch_token(TOKEN_URL, client_secret=CLIENT_SECRET, authorization_response=request.url) # Výměna autorizačního kódu za přístupový token
    session['oauth_token'] = token # Uložení přístupového tokenu pro buoducí API volání

    # Načtení uživatelské knihovny pomocí přistupového tokenu
    shelves_response = google.get('https://www.googleapis.com/books/v1/mylibrary/bookshelves')
    shelves = shelves_response.json().get('items', []) # Extrahování informací knihovny z API odpovědi

    return render_template('bookshelves.html', shelves=shelves) # Zobrazení načtených dat knihovny v grafickém rozhraní

@app.route('/bookshelves')
def bookshelves():
    """Načtení a zobrazení knihovny uživatele"""
    google = OAuth2Session(CLIENT_ID, token=session['oauth_token']) # Vytvoření autorizace OAuth 2.0 pomocí přístupového tokenu
    shelves_response = google.get('https://www.googleapis.com/books/v1/mylibrary/bookshelves') # Načtení seznamu podsložek knihovny pomocí Google Books API
    shelves = shelves_response.json().get('items', []) # Extrahování informací z knihovny
    return render_template('bookshelves.html', shelves=shelves) # Zobrazení načtených dat knihovny v grafickém rozhraní

@app.route('/books/<shelf_id>')
def view_books(shelf_id):
    """Zobrazení obsahu určité podsložky knihovny"""
    google = OAuth2Session(CLIENT_ID, token=session['oauth_token']) # Vytvoření autorizace OAuth 2.0 pomocí přístupového tokenu
    response = google.get(f'https://www.googleapis.com/books/v1/mylibrary/bookshelves/{shelf_id}')

    bookshelf = response.json() # Zpracování API odpovědi
    shelf_title = bookshelf.get('title', 'Bookshelf')  # Získaní názvu podsložky nebo použití výchozí hodnoty

    books_response = google.get(f'https://www.googleapis.com/books/v1/mylibrary/bookshelves/{shelf_id}/volumes')
    books = books_response.json().get('items', []) # Extrahování informací knih z API odpovědi

    return render_template('books.html', books=books, shelf_title=shelf_title) # Zobrazení načtených dat knihovny v grafickém rozhraní

@app.route('/add_book_page')
def add_book_page():
    """Zobrazení strákny pro přidávání knih do uživatelovy knihovny"""
    return render_template('add_book.html') # Zobrazení formuláře pro přidání knih


@app.route('/add_book', methods=['POST'])
def add_book():
    """Zpracování logiky pro přidávání knih do určité knihovny"""
    google = OAuth2Session(CLIENT_ID, token=session['oauth_token'])  # Vytvoření autorizace OAuth 2.0 pomocí přístupového tokenu
    shelf_id = request.form['shelf_id'] # Získání ID knihovny z formuláře
    volume_id = request.form['volume_id'] # Získání ID knihovny z formuláře

    try:
        # Odeslání požadavku pro přidání knihy do určité knihovny
        response = google.post(
            f'https://www.googleapis.com/books/v1/mylibrary/bookshelves/{shelf_id}/addVolume',
            params={'volumeId': volume_id}
        )

        """ Zpracování odpovědi podle stavového hlášení """
        if response.status_code == 200:
            message = "Book successfully added!"
        else:
            # Zpracování informací o chybě, pokud jsou k dispozici
            error_details = response.json().get('error', {}).get('message', 'Unknown error')
            message = f"Failed to add book: {error_details}"
            print(f"Failed to add book. Status: {response.status_code}, Response: {response.text}")

    except Exception as e:
        # Zaznamenání neočekáváné vyjímky
        print(f"Error during book addition: {str(e)}")
        message = "An unexpected error occurred. Please try again."

    return render_template('add_book_result.html', message=message) # Zobrazení výsledku v grafickém rozhraní

@app.route('/remove_book_page')
def remove_book_page():
    """Zpracování logiky pro odstranění knihy z uživatelské knihovny"""
    return render_template('remove_book.html') # Zobrazení formuláře pro odstranění knihy


@app.route('/remove_book', methods=['POST'])
def remove_book():
    """Zpracování logiky pro odstranění knihy z uživatelské knihovny"""
    google = OAuth2Session(CLIENT_ID, token=session['oauth_token'])  # Vytvoření autorizace OAuth 2.0 pomocí přístupového tokenu
    shelf_id = request.form['shelf_id'] # Získání ID knihovny z formuláře
    volume_id = request.form['volume_id'] # Získání ID knihy z formuláře

    try:
        # Odeslání požadavku pro odstranění knihy z určité části knihovny
        response = google.post(
            f'https://www.googleapis.com/books/v1/mylibrary/bookshelves/{shelf_id}/removeVolume',
            params={'volumeId': volume_id}
        )

        """ Zpracování odpovědi podle stavového hlášení """
        if response.status_code == 200:
            message = "Book successfully removed!"
        else:
            # Zpracování informací o chybě, pokud jsou k dispozici
            error_details = response.json().get('error', {}).get('message', 'Unknown error')
            message = f"Failed to remove book: {error_details}"
            print(f"Failed to remove book. Status: {response.status_code}, Response: {response.text}")

    except Exception as e:
        # Zaznamenání neočekáváné vyjímky
        print(f"Error during book removal: {str(e)}")
        message = "An unexpected error occurred. Please try again."

    return render_template('remove_book_result.html', message=message) # Zobrazení výsledku v grafickém rozhraní

@app.route('/search_books', methods=['GET', 'POST'])
def search_books():
    """Navrhnutí knihy na základě vyplněného formuláře nebo výchozího slova"""
    if request.method == 'POST':
        query = request.form.get('query')  # Získání slova z formuláře
    else:
        query = "bestsellers"  # Výchozí odpověď pokud není žádné slovo napsáno

    google = OAuth2Session(CLIENT_ID, token=session['oauth_token']) # Vytvoření autorizace OAuth 2.0 pomocí přístupového tokenu

    # Odeslání požadavku API na získání knih
    response = google.get(
        'https://www.googleapis.com/books/v1/volumes',
        params={'q': query, 'orderBy': 'relevance', 'maxResults': 25, 'printType': 'books', 'langRestrict': 'en'}
    )

    if response.status_code == 200: # Pokud požadavek je úspěšný
        books = response.json().get('items', []) # Extrahování infomrací o knihách z API dopovědi
        return render_template('search.html', books=books, query=query) # Grafické zobrazení extrahovaných informací
    else:
        error_message = response.json().get('error', {}).get('message', 'Unknown error') # Zpracování chyby API
        return f"Error fetching suggestions: {error_message}", response.status_code

@app.route('/personalized_menu', methods=['GET', 'POST'])
def personalized_menu():
    """
        Zobrazí menu, kde si uživatel vybere knihovnu pro doporučení.
        Pokud uživatel odešle formulář, je přesměrován na stránku s doporučeními.
    """
    if request.method == 'POST': # Kontrola, zda byl formulář odeslán
        shelf_id = request.form.get('shelf_id')  # Získá ID vybrané knihovny z formuláře
        return redirect(url_for('personalized_suggestions', shelf_id=shelf_id)) # Přesměruje uživatele na doporučení

    return render_template('personalized_menu.html')  # Zobrazení formuláře s výběrem knihoven


@app.route('/personalized_suggestions/<shelf_id>', methods=['GET'])
def personalized_suggestions(shelf_id):
    """
        Načtení knih z vybrané knihovny uživatele, zpracování a vytvoření personalizovaná doporučení.
    """
    google = OAuth2Session(CLIENT_ID, token=session['oauth_token'])  # Vytvoření autorizace OAuth 2.0 pomocí přístupového tokenu

    # Poslání požadavku na API Google Books pro získání knih z vybrané knihovny
    bookshelf_response = google.get(
        f'https://www.googleapis.com/books/v1/mylibrary/bookshelves/{shelf_id}/volumes'
    )

    if bookshelf_response.status_code != 200: # Kontrola, zda byl požadavek úspěšně splněn
        error_message = bookshelf_response.json().get('error', {}).get('message', 'Unknown error')
        return f"Error fetching bookshelf: {error_message}", bookshelf_response.status_code # Návrat chybové zprávy

    books = bookshelf_response.json().get('items', [])  # Extrahuje seznam knih z odpovědi API
    if not books:
        # Pokud je knihovna prázdná, zobrazí se stránka bez doporučení
        return render_template('personalized_suggestions.html', books=[], suggestions=[], shelf_id=shelf_id) # Zobrazení formuláře s doporučenými knihami

    # Výběr informací o autorech a kategoriích pro generování doporučení
    recommendation_queries = []
    for book in books:
        volume_info = book.get('volumeInfo', {}) # Získá podrobnosti o knize
        authors = volume_info.get('authors', []) # Získá seznam autorů (pokud existuje)
        categories = volume_info.get('categories', []) # Získá seznam kategorií (pokud existuje)

        # Add authors and categories to the recommendation queries
        recommendation_queries.extend(authors)
        recommendation_queries.extend(categories)

    recommendation_queries = list(set(recommendation_queries))[:5]  # Odstranění duplikátů a omezení počtu dotazů (5)

    # Načtení doporučených knih pomocí Google Books API
    suggestions = []
    for query in recommendation_queries:
        suggestion_response = google.get(
            'https://www.googleapis.com/books/v1/volumes',
            params = {'q': query, 'maxResults': 5, 'printType': 'books'} # Vyhledá knihy podle paramterů
        )
        if suggestion_response.status_code == 200:  # Pokud byl požadavek úspěšný
            suggestions.extend(suggestion_response.json().get('items', []))  # Přidání knih do seznamu doporučení

    return render_template('personalized_suggestions.html', # Zobrazení formuláře s doporučenými knihami
        books = books, # Seznam knih z uživatelovy knihovny
        suggestions = suggestions, # Seznam doporučených knih
        shelf_id = shelf_id # ID vybrané knihovny, které se zobrazí na stránce
    )

if __name__ == '__main__':
    app.run(debug=True) # Spuštění Flask aplikace ve vývojářském režimu