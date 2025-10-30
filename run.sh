#!/bin/bash

# Kalkulator Druku Offsetowego v1.2 - Startup Script
# Uruchamia serwer Flask z konfiguracją deweloperską

echo "======================================"
echo "Kalkulator Druku Offsetowego v1.2"
echo "======================================"
echo ""

# Sprawdzenie Pythona
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 nie jest zainstalowany!"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✅ Znaleziono: $PYTHON_VERSION"

# Sprawdzenie zależności
echo ""
echo "Sprawdzanie zależności..."

if ! python3 -c "import flask" 2>/dev/null; then
    echo "❌ Flask nie jest zainstalowany!"
    echo "📦 Instaluję zależności z requirements.txt..."
    pip3 install -q -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "✅ Zależności zainstalowane"
    else
        echo "❌ Błąd instalacji zależności"
        exit 1
    fi
else
    echo "✅ Flask zainstalowany"
fi

# Sprawdzenie struktury projektu
echo ""
echo "Sprawdzanie struktury projektu..."

REQUIRED_DIRS=("backend" "frontend/templates" "data" "docs")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "✅ $dir/"
    else
        echo "❌ Brak katalogu: $dir/"
        exit 1
    fi
done

REQUIRED_FILES=("backend/app.py" "data/slowniki_data.json" "data/kontrahenci.json")
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ Brak pliku: $file"
        exit 1
    fi
done

# Przejście do katalogu backend
cd backend

# Konfiguracja Flask
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# Uruchomienie serwera
echo ""
echo "======================================"
echo "🚀 Uruchamiam serwer Flask..."
echo "======================================"
echo ""
PROTOCOL="http"
if [[ -n "$FLASK_SSL_CERT" && -n "$FLASK_SSL_KEY" ]]; then
    PROTOCOL="https"
    echo "🔐 HTTPS aktywny (użyto FLASK_SSL_CERT oraz FLASK_SSL_KEY)"
elif [[ -n "$FLASK_SSL_CERT" || -n "$FLASK_SSL_KEY" ]]; then
    echo "⚠️  HTTPS wymaga ustawienia obu zmiennych: FLASK_SSL_CERT oraz FLASK_SSL_KEY"
fi

echo "📍 Adres: ${PROTOCOL}://127.0.0.1:7018"
echo "🛑 Zatrzymaj: Ctrl+C"
echo ""
echo "======================================"
echo ""

python3 app.py

# Kod wyjścia
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Serwer zakończył się błędem"
    exit 1
fi
