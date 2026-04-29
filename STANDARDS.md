# TRAK Application

A PyQt5-based Spotify or Youtube to mp3 downloader with metadata extraction.

## Purpose
Dieses Dokument definiert **technische Entwicklungs- und Architekturstandards** für Senior-Entwickler in **Java (Spring Boot)** und **Python**.  
Es dient als **Richtlinie für AI Coding Agents** und Menschen, um Codequalität, Wartbarkeit und Systemkonsistenz sicherzustellen.  
*Keine* funktionalen Anforderungen sind enthalten.

## Senior Software Engineering Standards (Java • Spring Boot • Python)

This document defines strict technical implementation rules for AI
coding agents. It intentionally excludes functional or business
requirements.

The goal is to ensure: - maintainable code - clear architecture
boundaries - testability - production-ready implementations

AI agents must follow these rules when generating, modifying, or reviewing code.
Der Agent **MUSS** diese Standards bei **jedem** Code-Snippet, jeder Datei und jedem Refactoring automatisch und vollständig einhalten. Abweichungen sind nur erlaubt, wenn die Aufgabe explizit eine Ausnahme fordert – und auch dann muss der Agent die Abweichung kommentieren und eine Compliance-Alternative vorschlagen.

## 1. Allgemeine technische Prinzipien

- Schreibe **deterministischen**, **idempotenten** und **testbaren** Code.  
- Bevorzuge **Immutability** und reine Funktionen, außer im I/O‑ oder Persistenzkontext.  
- Implementiere **Clean Separation of Concerns** (Business, Transport, Infrastructure).  
- Definiere strikt **Interface Contracts** und **Dependency Boundaries**.  
- Verwende **Dependency Injection** durch Framework oder Factory Patterns.  
- Jede Methode soll **max. eine Verantwortlichkeit** haben (SRP).  
- **Logging**: Verwende strukturierte Logs mit Korrelation‑Id (SLF4J/MDC oder `structlog`).
- **Error Handling**: Jede Exception wird gefangen, geloggt und fachneutral neu geworfen oder in HTTP‑Fehler übersetzt.

### 1.1 Code Quality

- Jede Methode/Funktion ≤ 25 Zeilen (Ausnahme nur bei sehr komplexer Berechnung, dann mit ausführlichem Kommentar).
- Single Responsibility Principle **streng** einhalten.
- DRY, KISS, YAGNI, SOLID – ohne Ausnahme.
- Keine Magic Numbers, Magic Strings oder Hardcoded Values.
- Namen sind **selbsterklärend** (keine Abkürzungen außer Standard-Abbreviations wie `id`, `dto`).
- Immutable-first: Datenstrukturen standardmäßig unveränderlich machen.
- Alle generierte Code mussen folgenden folgen:
    *   Clean Code principles
    *   SOLID design principles
    *   Single responsibility per class
    *   Small and focused methods
    *   Readable and maintainable structure
- Zu vermeiden:
    * God classes 
    * deep inheritance hierarchies 
    * hidden sideeffects 
    * tightly coupled modules 
    * static utility abuse
- Präferenz: 
    * composition über inheritance 
    * immutable objekte 
    * explizit dependencies 
    * pure functions wenn möglich

### 1.2 Fehlerbehandlung & Resilience
- Kein stilles Schlucken von Exceptions (`catch (Exception e) {}` verboten).
- Zentrale Error-Handling-Komponente (Framework-spezifisch).
- Jede Exception enthält Kontext (Message + Cause + relevante Daten).
- Circuit Breaker / Retry / Timeout Pattern bei externen Calls (wo Framework unterstützt).

### 1.3 Testing (non-negotiable)
- Unit-Test-Coverage ≥ 90 % für neuen Code, ≥ 80 % bei Refactoring.
- Jeder öffentliche Methoden-Endpunkt + Edge-Cases + Error-Pfade getestet.
- AAA-Pattern, aussagekräftige Test-Namen (`given_when_then` oder `should_`).
- Tests sind **deterministisch** (keine `Thread.sleep`, keine reale Zeit).
- Integrationstests mit Testcontainers / in-memory DBs.

## Python Standards

### Environment & Style
- Python Version: **≥ 3.11**
- Code Style: **PEP 8** enforced via **flake8**, **black**, **isort**.
- Typisierung verpflichtend: `mypy` als statischer Prüfer.
- Verwende **virtualenv** oder **Poetry** zur Paketverwaltung.
- Strict Imports: relative Imports vermeiden; nur absolute nutzen.

### Code Architecture
- Trennung von **domain**, **infrastructure**, **api**, **core**, **tests**.
- Businesslogik kapseln, kein direkter Zugriff auf Datenquellen aus API‑Layer.
- Konfiguration über `.env` oder `pydantic.BaseSettings`.
- Logging mit `structlog` (JSON‑Format für observability).
- Fehlerbehandlung zentral über Decorator oder Middleware (z.B. FastAPI ExceptionHandler).

### Framework Standards
- API Framework: **FastAPI** (präferiert) oder **Flask**.
- **FastAPI** als Default für neue APIs (wegen Async, Pydantic v2, OpenAPI).
- Bei Flask/Django: dieselben Regeln, nur angepasst an Framework.
- Non-bloking IO bevorzugen. Async Operations nur mit `async/await` und event‑loop‑safe Bibliotheken.
- Validierung und Serialisierung ausschließlich über **pydantic**.
- Task Queues über **Celery** oder **RQ**; keine threading‑basierten Systeme.
- Use dataclasses, pydantic for Data Models

### Testing & Quality
- Test Framework: **pytest**
- Coverage Ziel: >= 85%
- Mocking ausschließlich mit `unittest.mock` oder `pytest‑mock`
- Wiederholbare Tests (Seed festlegen bei Zufallsverhalten)
- autom. Linter/Formatter als Pre‑Commit Hooks
- pytest + pytest-asyncio + httpx + pytest-factoryboy.
- `respx` oder `httpx-mock` für externe Calls.

### Datenbanken & ORM
- SQLAlchemy 2.0+ (async) oder Prisma/Tortoise-ORM.
- Connection-Pooling + Statement-Caching.
- Kein raw SQL ohne `text()` + Parameter-Binding.

### Security & Config
- `pydantic-settings` für Settings-Management.
- Middleware für CORS, Rate-Limiting, Trusted-Hosts.
- `secrets` + `os.environ` – nie `hardcoded`.

## Features

- **Download Files**: Download files from provided URLs
- **Extract Metadata**: Automatically extract artist and title from URLs
- **Simple UI**: Clean and intuitive user interface
- **Smart Controls**: Search button only enabled when URL is provided
- **Error Handling**: Comprehensive error messages and logging

### UI-Requirements:
- The header containt the name of the application "TRAK"
- In the content left the text input for the url
- In the content right the button "Search" to handel the url
- the input and the button "search" are in the same line
- Donw below the retrieved information i.e. artist, title.
- down below the information we have the button download. To download the file.

### Functional Requirements:
- when the text input is empty, the button search is disabled else enabled.
- When the search button is clicked, the infomation will be display in the information board otherwise an not found modal dialog
- when the download button is clicked, the use should choose de download folder.
