# ADR-0002: Do not use localStorage as database

## Estado

Aceptada

## Contexto

El prototype MinBot-Task usaba localStorage (vía Zustand persist) para guardar memorias cifradas y metadatos del vault. Esto introduce problemas:

- **Persistencia no garantizada:** localStorage puede ser limpiado por el navegador, por el usuario, o por cuota (5-10 MB).
- **Sin queries estructuradas:** solo se puede iterar, no hacer FTS ni búsqueda semántica.
- **Sin transacciones:** una escritura fallida a mitad de operación deja estado inconsistente.
- **Multi-tab race conditions:** varias pestañas escribiendo al mismo tiempo causan data loss.

Las alternativas eran:

1. **IndexedDB (vía Dexie)** — síncrono, soporta índices, transacciones, mayor cuota.
2. **SQLite via sql.js** — SQLite compilado a WASM, persistido en IndexedDB.
3. **Server-only** — todo en PostgreSQL desde el día 1.

## Decisión

**NO usar localStorage como base de datos.** Reglas:

- `localStorage` puede usarse solo para: preferencias de UI pequeñas (theme, locale), session ID corto, salt del vault (público).
- Memorias, reminders, listas, agents, audit logs → IndexedDB (PWA) o SQLite (local/desktop) o PostgreSQL (server).
- La passphrase del vault NUNCA se persiste — solo en memoria durante la sesión.
- El `masterKey` derivado de la passphrase NUNCA se persiste — solo en memoria.
- Si se usa Zustand persist, el `partialize` debe excluir explícitamente `masterKey` y `plaintext`.

## Consecuencias

- **Positivas**: Datos persistentes y consultables, transacciones ACID, multi-tab consistente, base para sync en 0.4.5.
- **Negativas**: Mayor complejidad inicial (migraciones, schemas), mayor superficie de código.
- **Riesgos**: Migraciones de schema en cliente (PWA) — manejar con cuidado, siempre reversibles.

## Alternativas consideradas

1. **IndexedDB (Dexie)** — adoptada para PWA. Wrapper ergonómico, soporte de índices y transacciones.
2. **SQLite via sql.js** — viable pero añade 1.5 MB de WASM al bundle. Reevaluar para desktop.
3. **Server-only** — postergado a 0.3. Modo Local Estricto requiere persistencia local.

## Referencias

- TRD §24 #13 (frozen decision)
- Backend §4.1 (domain isolation)
- MinBot prototype §3.10 (pattern to follow with partialize)
- Seguridad §6 (encryption at rest)
