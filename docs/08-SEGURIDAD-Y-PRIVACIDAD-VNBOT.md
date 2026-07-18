# VNBOT — Seguridad y Privacidad

> **Documento:** Seguridad, privacidad y protección de datos
> **Producto:** VNBOT
> **Versión:** 1.0.0-draft
> **Estado:** Requisitos de seguridad
> **Fecha:** 2026-07-16
> **Documentos relacionados:** [PRD](./01-PRD-VNBOT.md), [TRD](./02-TRD-VNBOT.md), [Esquema Backend](./03-ESQUEMA-BACKEND-VNBOT.md), [Modelo de Datos](./07-MODELO-DATOS-VNBOT.md)
> **Nota:** Este documento define controles técnicos y de producto. No sustituye asesoramiento jurídico profesional ni la revisión de obligaciones aplicables a cada jurisdicción.

---

# 1. Propósito

VNBOT procesará información que puede ser íntima o sensible: recordatorios, relaciones personales, conversaciones, audios, documentos, datos de calendario, preferencias, correos y credenciales de integraciones.

Este documento define cómo proteger esa información en:

- Web/PWA.
- APK.
- Desktop.
- CLI.
- Backend.
- Workers.
- Base de datos.
- Object storage.
- LLM Router.
- MCP Gateway.
- Integraciones externas.
- CI/CD.
- Backups.
- Comunidad open source.

La seguridad no se limita a cifrar tablas. VNBOT debe:

1. Reducir la cantidad de datos recogidos.
2. Separar datos por usuario y workspace.
3. Limitar qué puede leer cada agente.
4. Explicar cuándo los datos salen del dispositivo.
5. Evitar acciones irreversibles sin confirmación.
6. Permitir exportar, corregir y eliminar.
7. Mantener trazabilidad sin registrar contenido privado innecesario.

---

# 2. Principios de seguridad

## 2.1. Privacidad por defecto

Las funciones que impliquen proveedores externos, lectura de correo, envío de mensajes o acceso a archivos deben estar deshabilitadas por defecto.

## 2.2. Mínimo privilegio

Cada usuario, agente, skill, integración y job recibe únicamente los permisos necesarios para su operación.

## 2.3. Separación de secretos y contenido

Una API key, un token OAuth o una contraseña no son memorias normales. Deben residir en un almacén de secretos separado y no aparecer en logs, embeddings, prompts ni exportaciones normales.

## 2.4. Transparencia operacional

El usuario debe poder saber:

- Qué modelo se utilizó.
- Qué herramienta se llamó.
- Qué datos se enviaron.
- Qué acción fue ejecutada.
- Qué quedó pendiente.
- Qué se guardó como memoria.

## 2.5. El LLM no es una frontera de seguridad

Las instrucciones del modelo pueden estar equivocadas o manipuladas. La autorización se aplica fuera del prompt mediante código determinista.

## 2.6. Fail closed para acciones de riesgo

Si el sistema no puede verificar permiso, identidad, fecha, destinatario o integridad, debe detener la operación y pedir revisión.

## 2.7. Portabilidad

El usuario debe poder exportar sus datos en un formato documentado y no depender exclusivamente de un proveedor.

## 2.8. Eliminación verificable

Borrar un dato implica considerar:

- Fuente.
- Versiones.
- Índices.
- Embeddings.
- Cache.
- Archivos.
- Backups según retención.

---

# 3. Modelo de amenaza

## 3.1. Activos protegidos

- Bóveda de memoria.
- Mensajes y conversaciones.
- Recordatorios.
- Relaciones del grafo.
- Audios.
- Imágenes y documentos.
- Calendarios.
- Correos.
- Contactos de terceros.
- API keys.
- Tokens OAuth.
- Configuración de agentes.
- Prompts privados.
- Skills instaladas.
- Backups.
- Logs y trazas.

## 3.2. Actores de amenaza

### Atacante remoto

Busca explotar API, autenticación, archivos, SSRF o dependencias.

### Atacante con XSS

Intenta ejecutar JavaScript en el navegador para robar sesión, modificar acciones o acceder a datos descifrados durante una sesión activa.

### Servidor comprometido

Puede intentar leer base de datos, archivos, variables de entorno o procesos.

### Proveedor LLM externo

Puede recibir contexto si el usuario lo autoriza. El riesgo depende de su política, retención, ubicación y configuración.

### Servidor MCP malicioso

Puede devolver instrucciones manipuladoras, solicitar scopes excesivos o intentar extraer datos.

### Skill maliciosa

Puede usar instrucciones para pedir herramientas no necesarias o provocar acciones peligrosas.

### Extensión/navegador comprometido

Puede leer el DOM o interceptar eventos durante la sesión web.

### Persona con acceso al dispositivo

Puede acceder a archivos locales, backups, sesiones abiertas o claves almacenadas en el sistema.

### Usuario malicioso dentro de workspace

Puede intentar consultar memorias, archivos o integraciones de otro miembro.

## 3.3. Límites explícitos

No se puede garantizar protección absoluta contra:

- Un sistema operativo completamente comprometido.
- Malware con acceso al proceso desbloqueado.
- Un usuario que entregue voluntariamente sus credenciales.
- Un administrador del servidor que controle la máquina y las claves de ejecución.
- Un proveedor externo que procese datos enviados bajo su propia política.

La documentación debe explicar estos límites sin hacer promesas absolutas.

---

# 4. Modos de privacidad

## 4.1. Modo Local Estricto

### Características

- Memoria en SQLite/IndexedDB local.
- Embeddings locales.
- Audio local.
- LLM local mediante Ollama, llama.cpp u otra alternativa.
- Sin sincronización remota por defecto.
- Sin analytics de contenido.
- Exportación manual cifrada.

### Ventaja

El plaintext puede permanecer en el dispositivo si el usuario no conecta servicios externos.

### Límite

Si el dispositivo está comprometido o desbloqueado, el atacante podría acceder a datos procesados en memoria.

## 4.2. Modo Servidor Privado

### Características

- API y base de datos en servidor elegido.
- Acceso desde varios dispositivos.
- PostgreSQL, Redis y storage opcional.
- LLM local o proveedor configurado.

### Advertencia

El administrador del servidor puede tener capacidad técnica para inspeccionar procesos, archivos o memoria del sistema. El cifrado en reposo no equivale automáticamente a zero-knowledge.

## 4.3. Modo LLM Externo

### Características

- El usuario selecciona proveedor y modelo.
- Se envía el contexto mínimo necesario.
- Memorias secretas pueden bloquearse para proveedores externos.
- Se muestra el proveedor utilizado.
- Se registra el uso de forma agregada.

### Control de usuario

Antes de activar este modo se debe mostrar:

```text
El texto necesario para interpretar esta acción se enviará a:
Proveedor: X
Modelo: Y
Datos excluidos: memorias secretas, credenciales
```

---

# 5. Zero-knowledge: definición precisa

## 5.1. Qué significa

En VNBOT, “zero-knowledge” solo debe utilizarse si el componente concreto no puede leer el plaintext, incluyendo el flujo de interpretación necesario.

## 5.2. Casos

| Caso | ¿El servidor puede ver plaintext? | Descripción correcta |
|---|---:|---|
| Bóveda local + LLM local | No, fuera del dispositivo | Procesamiento local |
| DB con ciphertext + API cloud para analizar texto | Sí durante la solicitud | Cifrado en reposo, no ZK total |
| Servidor propio con proceso que descifra | Sí, el servidor puede leerlo | Servidor privado |
| WebCrypto con LLM externo | Sí, el proveedor recibe el texto | Cifrado local parcial |

## 5.3. Regla de comunicación

La documentación debe especificar siempre:

- Dónde se cifra.
- Dónde se descifra.
- Quién puede ver plaintext.
- Qué se envía a proveedores.
- Qué se almacena.
- Cuánto tiempo se conserva.

---

# 6. Criptografía

## 6.1. Datos en reposo

Opciones:

- AES-256-GCM.
- XChaCha20-Poly1305 cuando la librería soporte el algoritmo correctamente.
- Envelope encryption para servidores y backups.

## 6.2. Derivación de claves

Para claves derivadas desde una passphrase:

- Argon2id preferido.
- Salt aleatorio único.
- Parámetros documentados.
- Política de migración si se actualizan.
- Verificación de versión criptográfica.

PBKDF2 puede mantenerse por compatibilidad web cuando sea necesario, pero debe documentarse como una decisión de compatibilidad y no como la única opción universal.

## 6.3. Claves por capas

```text
Passphrase del usuario
  ↓ KDF
Vault Key
  ↓ envelope encryption
Data Encryption Keys
  ↓
Memorias, archivos y backups
```

Las claves de integración no deben derivarse de una memoria ni almacenarse junto al contenido.

## 6.4. IV y nonce

- Generar aleatoriamente.
- Nunca reutilizar con la misma clave.
- Almacenar junto al ciphertext si es necesario.
- Validar tamaño y formato.

## 6.5. Integridad

El cifrado autenticado debe detectar modificación del contenido. Si la autenticación falla, no se debe intentar reparar o mostrar contenido parcial.

## 6.6. Hashes y deduplicación

No usar un hash público de plaintext sensible como identificador global. Para deduplicación privada se recomienda HMAC con clave derivada del workspace o de la bóveda.

---

# 7. Gestión de identidad

## 7.1. Contraseñas

- Argon2id.
- Longitud mínima razonable.
- No imponer reglas absurdas que incentiven reutilización.
- Rate limit.
- Mensajes que no revelen existencia de cuentas.
- Recuperación documentada.

## 7.2. Sesiones

- Cookies HttpOnly, Secure y SameSite.
- Expiración corta para access session.
- Refresh token rotatorio.
- Revocación server-side.
- Detección básica de reutilización.
- Cierre global de sesiones.

## 7.3. MFA

Fase posterior:

- TOTP.
- WebAuthn/passkeys.
- Códigos de recuperación almacenados con protección adecuada.

## 7.4. Dispositivos

- Identificador revocable.
- Último uso.
- Plataforma.
- Clave pública futura.
- Lista de dispositivos autorizados.

---

# 8. Autorización y aislamiento

## 8.1. Capas

```text
Identity
  ↓
Workspace membership
  ↓
Resource ownership
  ↓
Agent permission
  ↓
Skill permission
  ↓
Tool scope
  ↓
Action risk policy
```

## 8.2. Workspace isolation

Cada query debe filtrar por `workspace_id` antes de:

- Búsqueda textual.
- Búsqueda vectorial.
- Recorrido de grafo.
- Lectura de archivos.
- Selección de contexto para LLM.

## 8.3. Roles

```text
owner
admin
member
viewer
```

Los permisos del rol no deben otorgar automáticamente acceso a secretos o integraciones de alto riesgo.

## 8.4. Agentes

Un agente no hereda todos los permisos del usuario. Solo recibe:

- Memorias autorizadas.
- Skills activas.
- Tools aprobadas.
- Canales habilitados.
- Presupuesto asignado.

## 8.5. Denegación por defecto

Si no hay una política explícita, la operación se deniega o queda en espera de confirmación.

---

# 9. Seguridad del frontend

## 9.1. XSS

- Sanitizar Markdown y HTML.
- No insertar directamente contenido de LLM.
- No renderizar scripts, iframes o URLs peligrosas sin política.
- Usar CSP.
- Evitar `dangerouslySetInnerHTML`.

## 9.2. Almacenamiento local

No guardar en `localStorage`:

- API keys.
- Refresh tokens.
- Passphrases.
- Secretos.
- Plaintext sensible.

Usar:

- IndexedDB cifrado cuando corresponda.
- Keychain del sistema en desktop.
- Secure Storage en Android.
- Cookies HttpOnly para sesiones web.

## 9.3. Archivos

- Validar MIME real.
- Limitar tamaño.
- No ejecutar archivos subidos.
- No mostrar SVG no confiable sin sanitización.
- No permitir path traversal.
- Crear nombres internos.

## 9.4. CSP

La CSP debe ser estricta y mantenerse actualizada. No permitir `unsafe-eval` salvo que una dependencia indispensable lo requiera y esté justificado.

## 9.5. Microphone y permisos

- Solicitar permiso justo antes del uso.
- Mostrar estado de grabación.
- No grabar en background sin indicación.
- Detener al cambiar de vista cuando corresponda.
- Permitir eliminar el audio.

## 9.6. Clickjacking y navegación

- `frame-ancestors 'none'`.
- `X-Content-Type-Options: nosniff`.
- `Referrer-Policy` restrictiva.
- Enlaces externos con `noopener noreferrer`.
- No abrir herramientas externas sin confirmación contextual.

---

# 10. Seguridad del backend

## 10.1. Validación

Todos los endpoints deben validar:

- Tipo.
- Longitud.
- Enumeraciones.
- Fechas.
- Tamaño de archivos.
- URLs.
- Identificadores.
- JSON estructurado.

## 10.2. Rate limiting

Límites por:

- IP.
- Usuario.
- Workspace.
- Agente.
- Proveedor.
- Herramienta.
- Tipo de operación.
- Coste/token.

En despliegues múltiples se debe usar Redis u otro almacén compartido.

## 10.3. SSRF

Toda herramienta que haga requests debe:

- Bloquear IPs privadas por defecto.
- Resolver DNS y verificar destino final.
- Limitar redirects.
- Aplicar timeout.
- Limitar respuesta.
- Usar allowlist configurable.

## 10.4. SQL y comandos

- Usar queries parametrizadas/ORM seguro.
- No ejecutar comandos del sistema desde texto del usuario.
- No permitir shell a agentes en MVP.
- Si algún plugin necesita comandos, usar sandbox separado.

## 10.5. Webhooks

- Firma HMAC.
- Timestamp.
- Nonce.
- Protección replay.
- Idempotency key.
- Validación de proveedor.
- Respuesta rápida y procesamiento asíncrono.

## 10.6. Deserialización

No deserializar objetos arbitrarios provenientes de archivos, MCP o integraciones. Usar schemas explícitos.

---

# 11. Seguridad de LLM

## 11.1. Prompt injection

El contenido de emails, webs, documentos, notas y servidores MCP debe tratarse como datos no confiables. Un texto externo no puede cambiar las instrucciones de seguridad del agente.

## 11.2. Separación de instrucciones

```text
System policy
  ↓ prioridad máxima
Skill instructions
  ↓
Agent configuration
  ↓
User request
  ↓
External content/data
```

## 11.3. Tool calling

El LLM propone una tool call; no la ejecuta directamente. El backend debe:

1. Validar nombre.
2. Validar argumentos.
3. Comprobar permiso.
4. Evaluar riesgo.
5. Pedir confirmación si aplica.
6. Ejecutar con timeout.
7. Auditar.

## 11.4. Minimización de contexto

No enviar:

- Todas las memorias.
- Secretos no relacionados.
- Tokens.
- Prompts de otros agentes.
- Datos de otros workspaces.

## 11.5. Salidas no confiables

Las respuestas del LLM deben validarse, escaparse y tratarse como texto no confiable. No deben transformarse directamente en HTML, SQL, comandos o rutas de archivos.

---

# 12. Seguridad de MCP

## 12.1. MCP como frontera de integración

MCP no es una capa automática de confianza. Un servidor MCP puede estar mal configurado, comprometido o diseñado para solicitar más datos de los necesarios.

## 12.2. Registro seguro

Al registrar un MCP se debe mostrar:

- Nombre.
- Origen.
- Transporte.
- Endpoint/comando.
- Versión.
- Tools.
- Resources.
- Scopes.
- Riesgo.
- Fecha del último healthcheck.

## 12.3. Scopes

```text
graph.read
graph.write
memory.read
memory.write
calendar.read
calendar.write
email.read
email.draft
email.send
filesystem.read
filesystem.write
web.fetch
```

## 12.4. Herramientas peligrosas

Las siguientes requieren confirmación fuerte:

- `email.send`.
- `filesystem.write`.
- `memory.delete_many`.
- `calendar.delete_event`.
- `share.create`.
- Herramientas con efectos externos irreversibles.

## 12.5. Aislamiento

- Credenciales por integración.
- Timeouts.
- Límites de respuesta.
- Límite de tool calls.
- Sin acceso a variables de entorno globales.
- Red restringida.
- No ejecutar servidores externos como root.
- Revocación inmediata.

## 12.6. Servidores locales

Los servidores `stdio` deben ejecutarse con:

- Directorios permitidos.
- Usuario sin privilegios.
- Entorno mínimo.
- Logs separados.
- Límite de CPU/memoria cuando sea posible.

---

# 13. Seguridad de agentes y skills

## 13.1. Manifest obligatorio

Cada skill declara:

- ID.
- Versión.
- Licencia.
- Autor/origen.
- Herramientas.
- Scopes.
- Riesgo.
- Input/output schema.
- Necesidad de confirmación.

## 13.2. Instalación

Antes de activar una skill:

- Verificar origen.
- Mostrar cambios de permisos.
- Revisar firma si existe.
- Validar schema.
- Probar en modo simulación.

## 13.3. Actualización

Si una actualización aumenta scopes o riesgo, el agente debe quedar pausado hasta que el usuario confirme.

## 13.4. Skills comunitarias

No deben ejecutar código arbitrario por defecto. El sistema debe separar:

- Instrucciones.
- Schemas.
- Herramientas autorizadas.
- Código opcional aislado.

---

# 14. Audio, imágenes y documentos

## 14.1. Audio

- Captura explícita.
- Consentimiento.
- Cifrado temporal.
- Transcripción local o proveedor indicado.
- Retención elegible.
- Borrado después de transcribir si se selecciona.

## 14.2. Imágenes

- Validar tipo y tamaño.
- No enviar automáticamente a un modelo multimodal sin informar.
- Detectar documentos sensibles.
- Mostrar preview de extracción.
- Pedir confirmación antes de crear eventos o acciones.

## 14.3. Documentos

- No confiar en instrucciones incluidas dentro del documento.
- Aplicar límites de páginas/tamaño.
- Procesar en worker aislado.
- Eliminar temporales.
- Registrar solo metadata necesaria.

## 14.4. Malware

Para servidores públicos se recomienda análisis antivirus o sandbox. En modo local, se debe advertir que el usuario es responsable de los archivos que introduce.

---

# 15. Protección de datos de terceros

VNBOT puede recibir nombres, números, emails o información de personas que no son usuarios.

## Reglas

- No crear perfiles completos de terceros sin necesidad.
- Permitir eliminar referencias.
- No enviar mensajes a terceros sin base de consentimiento y canal oficial.
- Informar al usuario que el dato pertenece a un tercero.
- Aplicar retención mínima.
- No utilizar esos datos para telemetría o entrenamiento.

## Recordatorios externos

Debe existir:

- Identificación del destinatario.
- Canal oficial.
- Mensaje visible.
- Límite de frecuencia.
- Mecanismo de opt-out.
- Registro de entrega.

---

# 16. Logs, auditoría y telemetría

## 16.1. Logs operativos permitidos

- Request ID.
- Operation ID.
- Job ID.
- Estado.
- Duración.
- Error code.
- Modelo/proveedor.
- Conteos.
- Tamaño agregado.

## 16.2. No registrar por defecto

- Plaintext.
- Audio.
- Passwords.
- API keys.
- OAuth tokens.
- Cookies.
- Contenido completo de email.
- Prompt completo si contiene datos privados.

## 16.3. Auditoría visible al usuario

El usuario puede ver:

- Qué agente actuó.
- Qué skill se utilizó.
- Qué herramienta se llamó.
- Qué confirmación otorgó.
- Cuándo ocurrió.
- Resultado.
- Error resumido.

## 16.4. Telemetría opt-in

Si se incorpora telemetría, debe:

- Estar desactivada por defecto en modo privado.
- No incluir contenido.
- Ser agregada.
- Documentar eventos.
- Permitir desactivar.
- No utilizar identificadores personales innecesarios.

---

# 17. Backups y recuperación

## 17.1. Backup cifrado

El backup debe cifrarse antes de salir del dispositivo o servidor.

## 17.2. Separación de claves

La clave de backup no debe almacenarse junto al archivo. Puede conservarse en:

- Passphrase del usuario.
- Keychain.
- Secret manager.
- Hardware key futura.

## 17.3. Prueba de restauración

Un backup no se considera válido hasta que pueda restaurarse en un entorno de prueba.

## 17.4. Ransomware y corrupción

- Mantener versiones.
- Checksums.
- Backups offline o inmutables cuando sea posible.
- Detectar cambios anómalos.
- No sobrescribir el único backup.

---

# 18. Retención y eliminación

## 18.1. Categorías

| Dato | Retención inicial sugerida |
|---|---|
| Memoria activa | Hasta que el usuario la elimine o expire |
| Conversación | Configurable |
| Audio original | Eliminar después de transcripción por defecto |
| Archivo temporal | Hasta completar job + periodo corto |
| Propuesta no confirmada | Expiración corta |
| Logs operativos | Periodo limitado |
| Auditoría | Configurable, con minimización |
| Backups | Política del administrador/usuario |

## 18.2. Derecho a eliminar

El producto debe proporcionar una operación clara para:

- Eliminar memoria.
- Eliminar conversación.
- Eliminar archivo.
- Eliminar agente.
- Revocar integración.
- Exportar datos.
- Eliminar cuenta.

## 18.3. Purga completa

La purga debe incluir datos derivados. La UI debe explicar si existen copias en backups que expirarán posteriormente.

---

# 19. Cumplimiento y documentación legal

VNBOT será un proyecto open source bajo MIT, pero la licencia de software no sustituye las obligaciones legales derivadas del tratamiento de datos.

La documentación pública debe incluir como mínimo:

- Privacy Policy.
- Terms of Use.
- Cookie Policy si aplica.
- Security Policy.
- Subprocessor/Provider list cuando exista servicio administrado.
- Data deletion instructions.
- Contacto de seguridad.
- Licencias de terceros.
- Política de contribuciones.

Si se ofrece una instancia administrada, será necesario revisar obligaciones aplicables al operador, transferencias internacionales, proveedores, datos de salud, datos de menores y comunicaciones a terceros.

---

# 20. Seguridad de la cadena de suministro

## Repositorio

- Branch protection.
- CODEOWNERS.
- Pull requests obligatorios.
- Revisiones de seguridad.
- Gitleaks.
- Dependabot/Renovate.
- Lockfiles.

## CI/CD

- Build reproducible cuando sea posible.
- SAST.
- DAST.
- Trivy.
- SBOM.
- Firma de artefactos.
- Checksums.
- Releases etiquetados.

## Dependencias

Antes de agregar una dependencia:

- Revisar licencia.
- Revisar mantenimiento.
- Revisar vulnerabilidades.
- Revisar tamaño.
- Revisar permisos.
- Revisar si introduce código nativo.

## Assets visuales

- Registrar origen.
- Registrar modelo de generación.
- Registrar prompt y fecha.
- Revisar restricciones del modelo.
- No incluir watermarks.
- Auditar similitud con obras existentes.

---

# 21. Seguridad del despliegue

## Docker

- Imágenes mínimas.
- Usuario no root.
- Volúmenes mínimos.
- Red interna.
- Secrets externos.
- Healthchecks.
- No exponer Postgres/Redis públicamente por defecto.
- Actualizaciones controladas.

## Servidor

- HTTPS.
- HSTS.
- Firewall.
- Backups.
- Actualizaciones.
- Acceso administrativo separado.
- Monitorización.
- Rotación de credenciales.

## Desktop

- Firmar instaladores.
- Validar actualizaciones.
- Keychain del sistema.
- Permisos de filesystem mínimos.
- No ejecutar binarios descargados sin verificación.

## Android

- Firmar APK.
- Solicitar permisos mínimos.
- No incluir API keys en la app.
- Proteger almacenamiento local.
- Documentar permisos.

---

# 22. Gestión de incidentes

## 22.1. Clasificación

```text
P0 — exposición activa o pérdida masiva
P1 — vulnerabilidad explotable o servicio crítico afectado
P2 — impacto limitado o configuración incorrecta
P3 — mejora o vulnerabilidad de bajo impacto
```

## 22.2. Flujo

```text
Detectar
  ↓
Contener
  ↓
Evaluar alcance
  ↓
Revocar/rotar credenciales
  ↓
Preservar evidencia mínima
  ↓
Corregir
  ↓
Verificar
  ↓
Comunicar según corresponda
  ↓
Postmortem
```

## 22.3. Casos

### Token MCP expuesto

- Revocar integración.
- Rotar token.
- Revisar logs de uso.
- Informar al usuario.
- Verificar scopes.

### Base de datos expuesta

- Aislar red.
- Cambiar credenciales.
- Evaluar cifrado.
- Revisar acceso.
- Restaurar configuración segura.

### XSS

- Deshabilitar render problemático.
- Invalidar sesiones si es necesario.
- Corregir sanitización.
- Publicar parche.

### Job duplicado

- Detener scheduler si afecta a muchos usuarios.
- Revisar idempotencia.
- Corregir locks.
- Reconciliar deliveries.

---

# 23. Responsible disclosure

El repositorio debe incluir `SECURITY.md` con:

- Email o canal de reporte.
- Qué información incluir.
- No publicar vulnerabilidades antes del parche.
- Tiempo objetivo de respuesta.
- Política de créditos.
- Versiones afectadas.
- Proceso de CVE si aplica.

No se deben solicitar secretos o datos reales en issues públicos.

---

# 24. Pruebas de seguridad

## Autenticación

- Fuerza bruta.
- Sesiones caducadas.
- Refresh token reutilizado.
- Logout global.
- MFA.

## Autorización

- Acceso cruzado entre workspaces.
- IDOR.
- Agente con tool no asignada.
- Skill que intenta ampliar permisos.
- Exportación no autorizada.

## Aplicación

- XSS.
- CSRF.
- SSRF.
- SQL injection.
- Path traversal.
- Payloads enormes.
- Deserialización insegura.

## MCP/IA

- Prompt injection.
- Tool poisoning.
- Respuesta malformada.
- Servidor externo comprometido.
- Scope bypass.
- Filtración de contexto.

## Datos

- Cifrado/descifrado.
- Rotación de claves.
- Borrado de embeddings.
- Purga de archivos.
- Restore de backup.
- Conflicto de sincronización.

---

# 25. Checklist de privacidad para cada feature

Antes de aprobar una funcionalidad, responder:

1. ¿Qué datos recibe?
2. ¿Qué datos genera?
3. ¿Dónde se almacenan?
4. ¿Quién puede leerlos?
5. ¿Se envían a un proveedor externo?
6. ¿Se generan embeddings?
7. ¿Cuánto tiempo se conservan?
8. ¿Cómo se eliminan?
9. ¿Qué pasa offline?
10. ¿Qué ocurre si falla?
11. ¿Requiere confirmación?
12. ¿Cómo se audita?
13. ¿Qué permisos necesita?
14. ¿Qué datos de terceros intervienen?
15. ¿Qué documentación legal debe actualizarse?

---

# 26. Criterios de aceptación de seguridad

VNBOT cumple el baseline de seguridad cuando:

1. Las contraseñas no se almacenan en texto.
2. Los tokens se pueden revocar.
3. Un usuario no puede leer otro workspace.
4. Un agente no puede usar una herramienta no autorizada.
5. Las acciones de riesgo requieren confirmación.
6. Las respuestas de LLM no ejecutan código directamente.
7. MCP está sujeto a scopes y timeouts.
8. Los archivos no permiten path traversal.
9. Los logs no contienen secretos.
10. Las claves no viven en localStorage.
11. La aplicación tiene CSP y sanitización.
12. Los backups están cifrados.
13. Existe exportación y eliminación.
14. Se pueden reconstruir índices derivados.
15. Hay healthchecks y alertas.
16. Existe `SECURITY.md`.
17. La CI escanea secretos y dependencias.
18. Los releases tienen checksums o firma.
19. La política de privacidad distingue local, servidor privado y cloud.
20. Las integraciones oficiales se documentan con sus scopes y límites.

---

# 29. Testing de seguridad

### 29.1. Automatizado en CI (obligatorio desde día uno)

| Herramienta | Propósito | Frecuencia |
|---|---|---|
| Gitleaks | Detección de secretos en commits | Cada PR |
| Semgrep | SAST (análisis estático) | Cada PR |
| npm audit / pip-audit | Vulnerabilidades en dependencias | Cada PR y nightly |
| Trivy | Scan de contenedores Docker | Cada build de imagen |

### 29.2. Antes de cada release

| Tipo | Herramienta | Alcance |
|---|---|---|
| DAST | OWASP ZAP | Todos los endpoints públicos |
| Dependencias | Snyk / Grype | Todo el árbol de dependencias |
| Permisos | Revisión manual | Archivos de configuración, Docker, CI |
| Secrets | TruffleHog | Historial completo del repo |

### 29.3. Antes de v1.0

- Pentest básico por un revisor externo.
- Revisión del threat model completo.
- Revisión de todos los scopes de MCP.
- Revisión de backups y restore.
- Revisión de exportación/importación.
- Test de recuperación ante desastre.

### 29.4. Continuo (post v1.0)

- Responsible disclosure policy (ver SECURITY.md).
- Bug bounty (si hay presupuesto).
- Revisión trimestral de dependencias.
- Revisión anual del threat model.

---

# 30. Seguridad de la sincronización

### 30.1. Principios

- La sync nunca envía contenido en texto claro sobre HTTP. Siempre TLS 1.2+.
- El version vector no contiene datos del usuario, solo metadatos operativos.
- Las operaciones pendientes se cifran en reposo (local encryption).
- Un dispositivo no autorizado no puede iniciar sync sin autenticación válida.

### 30.2. Protección de la queue local

- La `sync_operations` queue se almacena cifrada en el dispositivo.
- Si el dispositivo se pierde o es robado, el cifrado local protege las ops pendientes.
- Las credenciales de autenticación se almacenan en el keychain/keystore del sistema, no en la base de datos.

### 30.3. Conflicto = visibilidad

Los conflictos de sync nunca se resuelven silenciosamente. Siempre se presentan al usuario con la información suficiente para decidir.

### 30.4. Reset de sync

La operación `sync/full-reset` requiere:
- Autenticación completa.
- Confirmación doble con delay de 5 segundos.
- Auditoría inmediata.
- No se permite durante una sync activa.

---

# 31. Gobernanza de seguridad del proyecto

### 31.1. Política de reporte de vulnerabilidades

VNBOT debe tener un proceso definido para recibir y responder a reportes de seguridad. Ver [Gobernanza de Proyecto](./13-GOBERNANZA-DE-PROYECTO-VNBOT.md).

### 31.2. Revisión de contribuciones

- Toda PR que toque código de seguridad, autenticación, cifrado o permisos debe ser revisada por al menos un maintainer con expertise en seguridad.
- Toda PR que añada un nuevo MCP tool o integración debe incluir un análisis de seguridad.
- Toda PR que modifique el schema de base de datos debe incluir migración reversible y plan de rollback.

### 31.3. Inventario de componentes de seguridad

El proyecto mantiene un inventario actualizado de:

- Algoritmos de cifrado utilizados y sus versiones.
- Librerías criptográficas y sus versiones.
- Proveedores de autenticación.
- Proveedores de LLM y sus políticas de retención.
- Integraciones externas y sus scopes.

Este inventario se revisa en cada release.

---

# 32. Decisiones abiertas

1. Argon2id en todos los clientes o KDF específico por plataforma.
2. Gestión de claves con WebCrypto, libsodium o implementación multiplataforma.
3. Duración exacta de sesiones.
4. MFA dentro del MVP o posterior.
5. Retención exacta de logs.
6. Sistema de secret manager para self-hosting.
7. Malware scanning integrado o plugin.
8. Firma obligatoria de skills comunitarias.
9. Política de telemetría del proyecto.
10. Procesamiento de datos sensibles en servidores administrados.
11. Soporte de backups inmutables.
12. Requisitos legales por país cuando exista una instancia cloud oficial.

---

# 33. Conclusión

La seguridad de VNBOT no debe depender de una única función de cifrado. Debe surgir de la combinación de:

```text
Minimización de datos
+ aislamiento por workspace
+ permisos por agente
+ scopes MCP
+ validación determinista
+ cifrado adecuado
+ jobs auditables
+ logs sanitizados
+ backups verificables
+ exportación y borrado
+ documentación honesta
```

La regla central es:

> **VNBOT debe ser extensible en capacidades, pero restrictivo en autoridad.**

El usuario puede instalar agentes, skills, modelos e integraciones, pero cada una debe declarar qué puede leer, qué puede modificar, qué datos procesa, qué riesgo introduce y cómo puede revocarse.
