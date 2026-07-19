# ADR-0008: Single-user personal assistant (no multi-user accounts)

## Estado

Aceptada

## Contexto

VNBOT fue diseñado desde el inicio como un asistente personal open source, privado y autoalojable. Los documentos canónicos (docs/00 §2, docs/01 §7, docs/08 §4) definen tres modos de privacidad: Local Estricto, Servidor Privado y LLM Externo. Los tres modos asumen un único usuario dueño de la instancia.

Sin embargo, durante la implementación del Sprint 1, se heredaron del esquema de datos original (docs/07) entidades multi-usuario como `Workspace`, `WorkspaceMember`, `User.email`, `User.password_hash`, y endpoints como `/auth/register`, `/auth/login`. Estas entidades añaden complejidad innecesaria y contradicen la naturaleza single-user del producto.

El usuario aclaró explícitamente: <i>"Este proyecto no busca ser multiusuario. Ya que es para uno mismo, como un asistente que va haciendo esas cositas y recordando detalles. No un sistema que va obteniendo información de los usuarios por medio de cuentas. Cada quien es dueño de su propio VNBOT por así decirlo."</i>

## Decisión

**VNBOT es single-user por diseño.** Cada instalación es propiedad de un único usuario. No hay sistema de cuentas, registro, ni roles multi-usuario.

Reglas:

1. **No multi-user accounts**: No se implementa `/auth/register`, `/auth/login` con email/password, ni `WorkspaceMember`.
2. **Single workspace**: Cada instalación tiene exactamente un workspace personal. El `workspace_id` se mantiene como campo en el schema (para futura export/import entre instancias), pero no hay UI para crear/gestionar workspaces.
3. **Auth simplificado**: La autenticación se reduce a una passphrase del vault local (para cifrar/descifrar memories). No hay sesiones de usuario con cookies.
4. **Modo Server (0.3) redefinido**: El "Server" no es para multi-usuario — es para acceso multi-dispositivo del mismo usuario. Un único usuario accede a su VNBOT desde web + APK + desktop + CLI, todos sincronizando con la misma instancia server.
5. **Self-hosting**: Cada usuario instala su propio VNBOT (Docker, APK, desktop, CLI). No hay SaaS centralizado.
6. **No analytics/telemetry**: Como no hay cuentas de usuario, no hay tracking. La telemetría (si se añade) es local-only y opt-in.
7. **Distribución**: GitHub Releases para binarios, Docker para self-hosting, GitHub Pages para demo estática.

## Consecuencias

- **Positivas**:
  - Simplificación significativa del schema y la API
  - Menor superficie de ataque (no hay auth bypass, IDOR entre usuarios, etc.)
  - Mejor alineación con el principio "el usuario controla sus datos"
  - Onboarding más simple: instalar + set passphrase + usar
  - No hay GDPR/compliance overhead (no hay datos de terceros)
- **Negativas**:
  - No hay colaboración entre usuarios (compartir memories requiere export/import manual)
  - No hay sincronización en la nube "mágica" (cada usuario gestiona su propio server)
  - Futuras features colaborativas (workspaces compartidos) requerirán un cambio arquitectónico
- **Riesgos**:
  - Si un usuario quiere compartir memories con familia/equipo, no hay path claro → mitigar con export/import +未来 "shared bundles" cifrados

## Alternativas consideradas

1. **Multi-user con roles** — rechazada por contradecir el principio "single-user personal assistant" y añadir complejidad innecesaria.
2. **Multi-user opcional (feature flag)** — rechazada porque introduce dos codepaths paralelas y duplica el testing.
3. **Family/team mode como plugin post-1.0** — aceptada como posibilidad futura si hay demanda, pero no en el core.

## Referencias

- docs/00 §2 (principios canónicos: local-first, user controls data)
- docs/01 §7 (personas: 7.1 personal user, 7.5 privacy-oriented, 7.6 self-hosting admin)
- docs/08 §4 (modos de privacidad: Local Estricto, Servidor Privado, LLM Externo)
- Aclaración del usuario (2026-07-19): "Este proyecto no busca ser multiusuario..."
