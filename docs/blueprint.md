Implement the Instrument vertical slice for the Market Intel backend.

## Goal

Create a stable entity representing a tradable security. Instruments must be reusable across scan runs so that company identity is not duplicated every time a symbol appears.

Do not modify ScanCandidate yet. In particular, do not remove or replace ScanCandidate.symbol in this task. The ScanCandidate migration will happen in a separate vertical slice after Instrument is complete and tested.

## Architecture

Follow the existing backend architecture:

API → Service → Repository → Database

Repositories must not commit transactions.

Services own commit, rollback, and refresh behavior.

Use the existing SQLAlchemy 2.x, FastAPI, Pydantic, Alembic, pytest, Ruff, and mypy conventions already present in the project.

## Instrument model

Create:

app/models/instrument.py

Fields:

- id: UUID primary key
- symbol: string, required
- name: string, nullable
- exchange: string, nullable
- asset_type: enum, required
- sector: string, nullable
- industry: string, nullable
- currency: string, required, default USD
- is_active: boolean, required, default true
- created_at: timezone-aware datetime
- updated_at: timezone-aware datetime

Create an InstrumentAssetType enum with these initial values:

- STOCK
- ETF
- ADR

Database requirements:

- symbol must be unique
- symbol must be indexed
- symbol should be stored in uppercase
- currency should be stored in uppercase
- updated_at should change whenever the row is updated

Use the same UUID and timestamp patterns already used by ScanRun and ScanCandidate.

Register Instrument in:

app/models/**init**.py

Do not import models from app/db/base.py.

## Schemas

Create:

app/schemas/instrument.py

Schemas:

### InstrumentCreate

Fields:

- symbol
- name
- exchange
- asset_type
- sector
- industry
- currency, default USD

Validation and normalization:

- trim surrounding whitespace from text fields
- normalize symbol to uppercase
- normalize currency to uppercase
- reject an empty symbol
- symbol maximum length: 20
- currency length: exactly 3

### InstrumentUpdate

All fields optional:

- name
- exchange
- asset_type
- sector
- industry
- currency
- is_active

Do not allow symbol changes through this schema.

### InstrumentRead

Return every persisted Instrument field.

Use ConfigDict(from_attributes=True).

## Repository

Create:

app/repositories/instrument.py

Implement:

- create(...)
- get_by_id(instrument_id)
- get_by_symbol(symbol)
- list_all()
- update(instrument, data)
- search(query, limit, offset)

Repository behavior:

- repositories must use flush where necessary
- repositories must not commit
- get_by_symbol must normalize the lookup symbol to uppercase
- list_all should order active instruments first, then symbol alphabetically
- search should perform a case-insensitive match against symbol or name
- search results should be ordered by symbol
- duplicate symbols must result in a domain-specific DuplicateInstrumentError rather than leaking IntegrityError

Be careful with rollback ownership. The repository should translate database errors, but transaction ownership must remain in the service. Do not commit inside the repository.

## Service

Create:

app/services/instrument.py

Implement:

- create_instrument(data)
- get_instrument(instrument_id)
- get_instrument_by_symbol(symbol)
- list_instruments()
- update_instrument(instrument_id, data)
- search_instruments(query, limit, offset)

Domain errors:

- InstrumentNotFoundError
- DuplicateInstrumentError

Service behavior:

- create, update, and other write operations own commit, rollback, and refresh
- reads must not commit
- reject duplicate symbols with DuplicateInstrumentError
- update must raise InstrumentNotFoundError when the record does not exist

## API

Create:

app/api/instruments.py

Register the router in main.py.

Endpoints:

### POST /instruments

- request: InstrumentCreate
- response: InstrumentRead
- status: 201
- duplicate symbol: 409

### GET /instruments

Return all instruments.

Support optional query parameters:

- query: search symbol or name
- limit: default 50, minimum 1, maximum 200
- offset: default 0, minimum 0

When query is present, use the search service.

### GET /instruments/{instrument_id}

- return InstrumentRead
- missing instrument: 404

### PATCH /instruments/{instrument_id}

- request: InstrumentUpdate
- response: InstrumentRead
- missing instrument: 404

### GET /instruments/by-symbol/{symbol}

- return InstrumentRead
- perform a case-insensitive lookup
- missing instrument: 404

Ensure `/instruments/by-symbol/{symbol}` is declared before `/instruments/{instrument_id}` if route ordering could cause FastAPI to interpret `by-symbol` as a UUID.

## Alembic

Generate an Alembic migration for the instruments table.

Review the generated migration manually.

The migration must include:

- instruments table
- UUID primary key
- unique constraint on symbol
- index on symbol
- asset type enum or the project’s established enum representation
- defaults and nullability matching the model

Do not alter scan_candidates in this migration.

## Tests

Create:

tests/test_instruments_api.py

Cover at least:

1. create an instrument
2. normalize a lowercase symbol to uppercase
3. normalize currency to uppercase
4. reject an empty symbol
5. reject invalid currency length
6. reject duplicate symbols regardless of input casing
7. list instruments
8. active instruments appear before inactive instruments
9. retrieve by ID
10. retrieve by lowercase symbol
11. missing ID returns 404
12. missing symbol returns 404
13. update instrument metadata
14. deactivate an instrument
15. PATCH cannot change symbol
16. search by partial symbol
17. search by partial company name
18. search is case-insensitive
19. limit and offset work
20. invalid limit returns 422

Use the existing shared fixtures in tests/conftest.py.

## Documentation

Update docs/blueprint.md only if implementation reveals a meaningful discrepancy with the approved blueprint.

Do not add speculative fields or unrelated features.

## Verification

Run:

uv run ruff format .
uv run ruff check . --fix
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy .

All checks must pass.

Report:

- files added or changed
- migration name
- test count
- any architectural decisions or deviations
