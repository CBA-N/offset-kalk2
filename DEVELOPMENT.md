# Development Workflow

## Branch Strategy

- `main` - production-ready code
- `genspark_ai_developer` - active development branch

## Setup Instructions

### Prerequisites
- Python 3.7+
- Flask >= 2.0.0
- requests >= 2.28.0

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
cd backend
python3 app.py
```

The application will be available at: http://127.0.0.1:7018

## Project Structure

```
offset-kalk/
├── backend/           # Backend logic
│   ├── app.py        # Main Flask application
│   ├── kalkulator_druku_v2.py
│   ├── slowniki_manager.py
│   └── ...
├── frontend/         # Frontend templates
│   └── templates/
├── data/            # JSON databases
│   ├── slowniki_data.json
│   ├── historia_ofert.json
│   └── kontrahenci.json
├── docs/            # Documentation
└── tests/           # Test files
```

## Features (v1.3)

✨ **New in v1.3:**
- ✂️ Paper cutting from B1 format (700×1000mm)
- 📐 Flexible billing units (piece, metric, weight)
- 🧮 Automatic cutting cost calculation
- 🎯 Intelligent cutting orientation optimization

## Development Guidelines

1. Always work on the `genspark_ai_developer` branch
2. Commit changes with descriptive messages
3. Test thoroughly before creating PR
4. Keep documentation up to date

## Testing

Run tests:
```bash
python3 test_kompletny.py
python3 test_all_components.py
python3 test_stawki.py
```

## Contributing

1. Fetch latest changes: `git fetch origin main`
2. Rebase your branch: `git rebase origin/main`
3. Squash commits before PR
4. Create PR with detailed description
5. Wait for review and approval

---

**Last updated:** 2025-10-24
