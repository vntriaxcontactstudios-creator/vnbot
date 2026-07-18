# VNBOT — Product Requirements Document (PRD)

> **Documento:** Product Requirements Document
> **Producto:** VNBOT
> **Versión:** 1.0.0-draft
> **Estado:** Definición de producto
> **Fecha:** 2026-07-16
> **Licencia del código prevista:** MIT
> **Audiencia:** Producto, UX/UI, frontend, backend, IA, seguridad, testing y calidad, comunidad open source y contribuidores externos

---

## 1. Propósito del documento

Este documento define qué es VNBOT, para quién se construye, qué problemas resuelve, qué funcionalidades deben formar parte del producto, cuáles son sus límites y cómo se comprobará que cada versión cumple su propósito.

El PRD no describe en detalle la implementación interna. Las decisiones de infraestructura, modelos, servicios, protocolos y despliegue se documentan principalmente en el [TRD](./02-TRD-VNBOT.md), el [Esquema Backend](./03-ESQUEMA-BACKEND-VNBOT.md) y el [Plan de Implementación](./04-PLAN-IMPLEMENTACION-VNBOT.md).

Este documento debe ser la referencia para evitar que VNBOT se convierta en una colección desordenada de funciones de IA. El producto puede crecer de manera amplia, pero cada capacidad debe estar subordinada a cuatro objetivos:

1. Capturar información con el menor esfuerzo posible.
2. Convertirla en memoria, tarea, evento o recordatorio útil.
3. Recuperarla de forma confiable y contextual.
4. Mantener al usuario en control de sus datos y de las acciones del asistente.

---

# 2. Resumen ejecutivo

VNBOT será un asistente personal open source, privado, autoalojable y extensible que funcionará como una capa de memoria y ejecución sobre las herramientas del usuario.

El usuario podrá escribir, hablar, enviar una imagen o compartir un archivo. VNBOT interpretará la entrada y propondrá una estructura:

- Memoria.
- Recordatorio.
- Tarea.
- Lista.
- Evento.
- Relación entre entidades.
- Borrador de acción.
- Consulta sobre información previa.

La memoria personal se representará mediante un grafo limitado de nodos y relaciones. El usuario podrá inspeccionarlo, corregirlo, eliminarlo y exportarlo. Para ampliar la información fuera del núcleo, VNBOT podrá conectarse a herramientas externas mediante MCP, incluyendo calendarios, correo, archivos y repositorios de código como Graphify.

La identidad visual será propia y reconocible:

- Pixel art de alta calidad.
- Golem informático como mascota principal.
- Variantes de la mascota para cada agente.
- Estados visuales sincronizados con el funcionamiento real del sistema.
- Paneles HUD cyberpunk angulares.
- Interfaz legible, accesible y sin depender de glassmorphism o blur.

VNBOT se distribuirá mediante:

- Demo estática en GitHub Pages.
- Aplicación web/PWA.
- APK Android.
- Aplicación de escritorio para Windows, macOS y Linux.
- Imágenes Docker para servidores.
- CLI para usuarios avanzados y administradores.

---

# 3. Visión del producto

## 3.1. Visión a largo plazo

VNBOT aspira a ser una plataforma personal de memoria y agentes donde cada usuario pueda decidir:

- Qué información se almacena.
- Qué información se olvida.
- Qué modelo de IA se utiliza.
- Qué agentes existen.
- Qué herramientas puede usar cada agente.
- Qué acciones necesitan confirmación.
- Dónde viven sus datos.
- Si el procesamiento se realiza localmente o mediante un proveedor externo.

La visión no es crear una caja negra que actúe de manera ilimitada sin supervisión. La visión es crear una plataforma abierta y modular que permita capacidades muy amplias con permisos visibles, revocables y auditables.

## 3.2. Declaración de valor

> VNBOT ayuda al usuario a sacar información de su cabeza, convertirla en estructuras útiles y volver a encontrarla en el momento correcto, sin obligarlo a entregar el control total de sus datos a un servicio cerrado.

## 3.3. Promesa principal del MVP

> Escribe o dicta una instrucción en lenguaje natural; VNBOT la entiende, te muestra lo que va a hacer, la guarda correctamente y te la presenta cuando corresponda.

---

# 4. Problema que se desea resolver

## 4.1. Fragmentación de información

Las personas guardan información en múltiples lugares:

- Aplicaciones de notas.
- Mensajería.
- Correo electrónico.
- Calendarios.
- Capturas de pantalla.
- Archivos locales.
- Historial del navegador.
- Documentos.
- Memoria informal.

El problema no es solamente que existan muchas aplicaciones. El problema es que cada aplicación conserva una parte aislada del contexto y el usuario debe recordar dónde guardó cada cosa.

## 4.2. Recordatorios débiles

Las aplicaciones tradicionales suelen requerir que el usuario complete formularios, elija una fecha, seleccione una repetición y defina una notificación. Esto funciona para tareas planificadas, pero falla cuando la idea aparece en medio de una conversación.

Además, un recordatorio aislado no siempre contiene el contexto necesario:

- Con quién está relacionado.
- Por qué importa.
- Qué ocurrió antes.
- Qué debe suceder después.
- Qué canal es adecuado.

## 4.3. Asistentes sin continuidad

La mayoría de los chats de IA pueden responder bien en una sesión, pero olvidan con facilidad:

- Preferencias del usuario.
- Relaciones entre personas.
- Decisiones anteriores.
- Reglas de trabajo.
- Tareas pendientes.
- Correcciones hechas anteriormente.

VNBOT debe tratar la memoria como una entidad visible y administrable, no como contexto invisible acumulado sin controles.

## 4.4. Falta de control y privacidad

Los usuarios pueden enviar información sensible a un asistente sin saber:

- Qué se almacena.
- Qué proveedor lo procesa.
- Cuánto tiempo se conserva.
- Qué integraciones tienen acceso.
- Qué datos se usan para generar embeddings.
- Qué acciones puede ejecutar el sistema.

VNBOT debe hacer visible esta información y ofrecer un modo local o autoalojable.

## 4.5. Automatizaciones frágiles

Una automatización incorrecta puede:

- Crear una fecha equivocada.
- Enviar un correo a la persona equivocada.
- Exponer información privada.
- Crear recordatorios duplicados.
- Borrar o modificar datos sin intención.

Por eso, VNBOT debe separar claramente:

```text
Interpretar → Proponer → Validar → Confirmar → Ejecutar → Auditar
```

---

# 5. Objetivos del producto

## 5.1. Objetivos del MVP

### O-01 — Captura rápida

Permitir que un usuario registre una idea, una tarea o un recordatorio en lenguaje natural sin aprender comandos especiales.

**Criterio:** un usuario nuevo debe poder crear su primer recordatorio sin consultar documentación.

### O-02 — Recordatorios confiables

Crear un sistema de recordatorios que sobreviva a cierres, reinicios, fallos temporales y reintentos del worker.

**Criterio:** no deben producirse duplicados cuando un job sea reintentado.

### O-03 — Memoria controlable

Permitir guardar, consultar, editar, corregir y olvidar memorias.

**Criterio:** el usuario debe poder identificar por qué existe una memoria y eliminarla sin intervención administrativa.

### O-04 — Grafo comprensible

Representar relaciones personales de forma visual y limitada, sin convertir el panel en un diagrama ilegible.

**Criterio:** una consulta debe mostrar únicamente el subgrafo relevante, con alternativa en forma de lista.

### O-05 — Privacidad verificable

Ofrecer diferentes modos de procesamiento y explicar claramente qué datos salen del dispositivo.

**Criterio:** cada integración y proveedor debe indicar el tipo de datos que puede recibir.

### O-06 — Independencia de proveedor

Permitir usar un LLM local, un proveedor externo o un endpoint compatible con OpenAI.

**Criterio:** el núcleo debe funcionar con heurísticas básicas incluso sin LLM.

### O-07 — Base extensible

Permitir que agentes, skills y conectores MCP se añadan sin modificar todo el núcleo.

**Criterio:** una integración nueva debe implementarse como adaptador o plugin sin reescribir memoria y recordatorios.

### O-08 — Distribución multiplataforma

Preparar el producto para web, APK, desktop, Docker y CLI.

**Criterio:** las interfaces deben consumir contratos API comunes y no duplicar las reglas de negocio.

## 5.2. Objetivos posteriores al MVP

- Procesamiento de voz local y remoto.
- OCR e interpretación de imágenes.
- Briefings diarios y semanales.
- Integración oficial con calendarios.
- Lectura y borradores de correo.
- Telegram y WhatsApp Business API.
- Agentes personalizados.
- Skills comunitarias firmadas.
- Grafo temporal avanzado.
- Sincronización entre dispositivos.
- Espacios familiares o de equipo.

---

# 6. No objetivos del MVP

Los siguientes elementos quedan fuera del primer lanzamiento aunque se contemplen en la visión futura:

## 6.1. Agente autónomo general

VNBOT no podrá navegar libremente por el sistema del usuario ni ejecutar cualquier acción disponible. La autonomía se añadirá gradualmente y estará limitada por herramientas, scopes, presupuesto y confirmaciones.

## 6.2. Mensajería automática a terceros

El MVP no enviará mensajes a familiares, compañeros o clientes sin una configuración explícita y una política de consentimiento.

## 6.3. Acceso completo al correo

La primera integración de correo, cuando exista, debe comenzar con lectura limitada o creación de borradores. El envío automático no será parte del MVP.

## 6.4. Operaciones financieras

No se permitirán pagos, transferencias, compras ni acciones bancarias.

## 6.5. Vigilancia continua del micrófono

La captura de audio será explícita y visible. No habrá escucha permanente en segundo plano en la primera versión.

## 6.6. Grafo ilimitado

El grafo visible tendrá límites de profundidad, cantidad de nodos y filtros. La escalabilidad de datos no implica renderizar todos los nodos simultáneamente.

## 6.7. Marketplace abierto de skills

Primero se necesita un sistema seguro de manifest, permisos, versionado y revisión. El marketplace queda para una etapa posterior.

---

# 7. Usuarios objetivo

## 7.1. Usuario personal con alta carga mental

Necesita recordar citas, pagos, compras, compromisos, ideas y tareas pequeñas. Valora una captura rápida y notificaciones confiables.

## 7.2. Profesional o freelancer

Gestiona proyectos, clientes, entregas, reuniones y seguimientos. Necesita relacionar personas, tareas y fechas.

## 7.3. Estudiante

Guarda apuntes, fechas de exámenes, temas de estudio, enlaces y recordatorios recurrentes.

## 7.4. Usuario técnico

Quiere integrar VNBOT con repositorios, terminal, servidores, modelos locales y MCP.

## 7.5. Usuario orientado a privacidad

Prefiere ejecutar el sistema en su propio equipo o servidor, elegir el modelo y exportar todos sus datos.

## 7.6. Administrador autoalojado

Necesita Docker, healthchecks, backups, logs, migraciones y una instalación reproducible.

## 7.7. Usuarios fuera del foco inicial

No se priorizan inicialmente:

- Grandes empresas con requisitos completos de compliance corporativo.
- Automatización bancaria.
- Atención médica automatizada.
- Supervisión de empleados.
- Comunicación masiva.
- Sistemas críticos de seguridad física.

---

# 8. Casos de uso principales

## CU-01 — Crear un recordatorio

**Entrada:** “Recuérdame pagar la electricidad mañana a las 8 de la mañana.”

**Resultado esperado:**

1. Detectar intención de recordatorio.
2. Resolver “mañana” según zona horaria.
3. Mostrar fecha completa.
4. Mostrar hora y canal.
5. Solicitar confirmación si falta información.
6. Crear recordatorio y ocurrencia.
7. Confirmar al usuario.

## CU-02 — Recordatorio recurrente

**Entrada:** “Todos los lunes recuérdame revisar el presupuesto.”

**Resultado esperado:** crear una regla de recurrencia, no una lista de recordatorios duplicados. La regla debe poder pausarse, modificarse y cancelarse.

## CU-03 — Guardar una memoria

**Entrada:** “Guarda que Daniel prefiere que las reuniones sean por la tarde.”

**Resultado esperado:** crear o actualizar nodos de persona y preferencia, relacionarlos con procedencia explícita y permitir editar el hecho.

## CU-04 — Consultar contexto

**Entrada:** “¿Qué tenía pendiente con Daniel?”

**Resultado esperado:** buscar memorias, tareas y recordatorios relacionados, mostrar fuentes y distinguir hechos confirmados de inferencias.

## CU-05 — Captura por audio

**Entrada:** nota de voz.

**Resultado esperado:** solicitar permisos, transcribir, mostrar texto editable y ejecutar el mismo flujo del chat. El sistema no debe actuar sobre una transcripción no revisada si la acción tiene riesgo medio o alto.

## CU-06 — Explorar el grafo

**Entrada:** el usuario abre Memoria/Grafo.

**Resultado esperado:** mostrar un mapa limitado de nodos, filtros, búsqueda, detalle, procedencia y acción de olvidar/corregir.

## CU-07 — Conectar Graphify

**Entrada:** el usuario añade un servidor MCP de Graphify.

**Resultado esperado:** mostrar origen, transporte, herramientas, scopes, healthcheck, riesgos y confirmación antes de activar. Graphify no debe recibir datos personales sin permiso específico.

## CU-08 — Crear un agente

**Entrada:** el usuario configura un agente de estudio.

**Resultado esperado:** seleccionar mascota, instrucciones, modelo, skills, memoria permitida, herramientas y nivel de autonomía. El sistema debe mostrar un resumen de permisos antes de activar.

## CU-09 — Modo offline

**Entrada:** el usuario pierde conexión.

**Resultado esperado:** crear capturas y recordatorios locales, marcar sincronización pendiente y sincronizar posteriormente con idempotency keys.

## CU-10 — Exportar y olvidar

**Entrada:** el usuario solicita exportar y eliminar su cuenta.

**Resultado esperado:** generar backup cifrado, pedir confirmación fuerte, revocar integraciones, eliminar datos activos y presentar el resultado de la operación.

---

# 9. Requisitos funcionales

## 9.1. Cuenta y espacios

| ID | Requisito | Prioridad |
|---|---|---|
| FR-001 | Permitir modo local sin cuenta remota | Must |
| FR-002 | Permitir cuenta en servidor privado | Must |
| FR-003 | Separar usuarios y workspaces | Must |
| FR-004 | Configurar zona horaria e idioma | Must |
| FR-005 | Bloquear automáticamente la bóveda | Should |
| FR-006 | MFA/WebAuthn | Should |

## 9.2. Chat

| ID | Requisito | Prioridad |
|---|---|---|
| FR-010 | Chat de texto | Must |
| FR-011 | Mostrar estado del agente | Must |
| FR-012 | Mostrar acción propuesta | Must |
| FR-013 | Editar propuesta antes de ejecutar | Must |
| FR-014 | Mostrar fuentes y memorias utilizadas | Must |
| FR-015 | Adjuntar audio | Should |
| FR-016 | Adjuntar imagen/documento | Could |
| FR-017 | Streaming de respuesta | Should |

## 9.3. Memoria y grafo

| ID | Requisito | Prioridad |
|---|---|---|
| FR-020 | Crear memoria explícita | Must |
| FR-021 | Crear nodos y relaciones | Must |
| FR-022 | Buscar por texto | Must |
| FR-023 | Buscar semánticamente | Should |
| FR-024 | Ver procedencia | Must |
| FR-025 | Editar nodo | Must |
| FR-026 | Corregir contradicción | Should |
| FR-027 | Olvidar nodo y relaciones | Must |
| FR-028 | Ver subgrafo limitado | Must |
| FR-029 | Vista alternativa en lista | Must |
| FR-030 | Importar/exportar grafo | Must |

## 9.4. Recordatorios

| ID | Requisito | Prioridad |
|---|---|---|
| FR-040 | Crear recordatorio puntual | Must |
| FR-041 | Crear recurrencia | Must |
| FR-042 | Resolver zona horaria | Must |
| FR-043 | Detectar ambigüedad | Must |
| FR-044 | Posponer | Must |
| FR-045 | Completar | Must |
| FR-046 | Cancelar | Must |
| FR-047 | Reintentar entrega | Must |
| FR-048 | Evitar duplicados | Must |
| FR-049 | Historial de entregas | Should |
| FR-050 | Ventanas de silencio | Should |

## 9.5. Agentes y skills

| ID | Requisito | Prioridad |
|---|---|---|
| FR-060 | Crear agente | Should |
| FR-061 | Seleccionar modelo | Should |
| FR-062 | Asignar skills | Should |
| FR-063 | Asignar herramientas | Should |
| FR-064 | Limitar memoria accesible | Should |
| FR-065 | Definir autonomía | Should |
| FR-066 | Mostrar permisos antes de activar | Must |
| FR-067 | Revocar herramienta | Must |

## 9.6. MCP e integraciones

| ID | Requisito | Prioridad |
|---|---|---|
| FR-070 | Registrar servidor MCP | Should |
| FR-071 | Realizar handshake/healthcheck | Should |
| FR-072 | Mostrar tools y resources | Should |
| FR-073 | Seleccionar scopes | Should |
| FR-074 | Confirmar operaciones de riesgo | Must |
| FR-075 | Desconectar y revocar credenciales | Must |
| FR-076 | Registrar ejecución | Must |

## 9.7. Distribución

| ID | Requisito | Prioridad |
|---|---|---|
| FR-080 | Demo mock en GitHub Pages | Must |
| FR-081 | Docker Compose local | Must |
| FR-082 | Build APK | Should |
| FR-083 | Build desktop | Should |
| FR-084 | CLI de diagnóstico | Should |
| FR-085 | Exportación portable | Must |

---

# 10. Requisitos no funcionales

## 10.1. Privacidad

- El modo local no debe enviar contenido fuera del dispositivo salvo activación explícita.
- Cada proveedor externo debe estar identificado.
- No se debe presentar como zero-knowledge un flujo donde el proveedor pueda leer plaintext.
- El usuario debe poder eliminar memorias, archivos, embeddings y logs asociados.

## 10.2. Seguridad

- Contraseñas con Argon2id.
- Cookies seguras y sesiones revocables.
- Validación de todos los payloads.
- CSP y sanitización de contenido generado por LLM.
- Protección SSRF para web/MCP.
- Rate limiting distribuido en servidor.
- Tokens de integración separados.
- Auditoría de acciones.
- Escaneo de dependencias y secretos.

## 10.3. Disponibilidad

Un recordatorio confirmado debe sobrevivir a:

- Reinicio de API.
- Reinicio de worker.
- Reintento del job.
- Pérdida temporal de red.
- Actualización de contenedor.

## 10.4. Rendimiento

Objetivos iniciales:

- Primera respuesta de interfaz local: menor de 200 ms cuando los datos estén en cache.
- Búsqueda textual local: P95 menor de 300 ms para 10.000 memorias.
- Búsqueda híbrida: P95 menor de 1 segundo en instalación personal razonable.
- Creación de job de audio: menor de 500 ms, aunque la transcripción sea asíncrona.
- Grafo inicial: menor de 1 segundo para hasta 100 nodos visibles.

## 10.5. Accesibilidad

- Contraste mínimo AA.
- Navegación por teclado.
- Etiquetas para controles.
- Estados no comunicados solo por color.
- `prefers-reduced-motion`.
- Alternativa de lista para el grafo.
- Texto legible en pantallas pequeñas.

## 10.6. Portabilidad

- Chrome, Firefox y Edge modernos.
- Android soportado por el APK definido para cada release.
- Windows, Linux y macOS según matriz de builds.
- Docker en Linux x64 y ARM64 cuando sea posible.
- SQLite para modo local.
- PostgreSQL para servidor.

---

# 11. Diseño de privacidad del producto

VNBOT debe presentar tres modos comprensibles:

## 11.1. Modo Local Estricto

- Memoria en dispositivo.
- Embeddings locales.
- Audio local.
- Ollama, llama.cpp o modelo integrado.
- Sin sincronización remota por defecto.
- Exportación manual.

## 11.2. Modo Servidor Privado

- API y base de datos en servidor elegido por el usuario.
- El administrador del servidor puede tener acceso técnico al proceso, por lo que debe explicarse la diferencia entre servidor propio y zero-knowledge.
- Integraciones y backups controlados por el propietario.

## 11.3. Modo LLM Externo

- El proveedor LLM recibe el contexto mínimo necesario.
- El usuario selecciona proveedor.
- Se muestran proveedor, modelo y política de datos.
- Se pueden bloquear memorias sensibles para proveedores externos.

---

# 12. Experiencia visual como requisito de producto

La estética no será una capa decorativa añadida al final. Será parte de la identidad funcional de VNBOT.

## 12.1. Mascota principal

El golem informático será la representación de VNBOT. Debe ser reconocible a 32x32, 64x64 y 128x128.

## 12.2. Mascotas por agente

Cada agente tendrá una variante coherente de la familia de golems. La variación se expresará mediante:

- Visor.
- Accesorio.
- Paleta.
- Silueta secundaria.
- Animación.

## 12.3. Estados

La mascota indicará el estado real del sistema:

- Escuchando.
- Pensando.
- Procesando.
- Esperando confirmación.
- Ejecutando.
- Completado.
- Advertencia.
- Error.
- Desconectado.

Toda animación debe acompañarse de texto o estado accesible.

## 12.4. UI

Los paneles HUD, las retículas y los marcos pixel art no deben impedir la lectura. Los mensajes, formularios, permisos y logs deben priorizar claridad.

---

# 13. Métricas de éxito

## 13.1. Métricas de producto

- Tiempo hasta el primer recordatorio.
- Porcentaje de usuarios que completan onboarding.
- Porcentaje de recordatorios creados correctamente en el primer intento.
- Tasa de memorias encontradas en consultas de prueba.
- Número de memorias corregidas o eliminadas por el usuario.
- Uso de exportación.
- Activación de modo local.
- Número de agentes configurados.

## 13.2. Métricas de confiabilidad

- Entregas correctas.
- Duplicados por cada 10.000 ocurrencias.
- Jobs perdidos.
- Jobs reintentados con éxito.
- Tiempo medio de recuperación.
- Estado de backups.

## 13.3. Métricas de comunidad

- Contribuidores activos.
- Pull requests aceptados.
- Issues resueltos.
- Plugins/skills revisados.
- Instalaciones Docker.
- Descargas de Releases.
- Documentación consultada.

Ninguna métrica de producto debe requerir enviar el contenido privado del usuario a un servicio de analítica.

---

# 14. Riesgos de producto y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---:|---|
| Fecha mal interpretada | Alto | Fecha completa y confirmación |
| Memoria inventada | Alto | Procedencia, confianza y respuesta basada en fuentes |
| Exceso de notificaciones | Medio | Silencio, agrupación y aprendizaje controlado |
| Costes LLM | Medio | Router, límites y modelos locales |
| MCP malicioso | Alto | Allowlist, scopes, sandbox y revocación |
| Complejidad excesiva | Alto | MVP pequeño y arquitectura por plugins |
| Assets incompatibles | Medio | Inventario y auditoría de licencias |
| Pérdida de datos | Alto | Backups, exportación y pruebas de restore |
| Falsa promesa de privacidad | Alto | Documentar claramente cada modo |
| Dependencia de una plataforma | Medio | Adaptadores y canales oficiales |

---

# 15. Roadmap de producto

## VNBOT 0.1 — Demo

- Landing en GitHub Pages.
- Chat simulado.
- Grafo con datos ficticios.
- Mascota y estados visuales.
- Documentación inicial.

## VNBOT 0.2 — Local

- PWA.
- IndexedDB.
- Bóveda local.
- Recordatorios locales.
- Heurística.
- Exportación.

## VNBOT 0.3 — Backend privado

- FastAPI.
- SQLite/PostgreSQL.
- Worker.
- Scheduler.
- Docker.
- Healthchecks.
- LLM Router.

## VNBOT 0.4 — Plataformas

- APK.
- Desktop.
- CLI.
- Notificaciones nativas.
- GitHub Releases.

## VNBOT 0.5 — Memoria

- Grafo real.
- Búsqueda híbrida.
- Procedencia.
- Correcciones.
- Expiración.

## VNBOT 0.6 — MCP

- MCP interno.
- Gateway externo.
- Permisos.
- Graphify opcional.
- Calendario opcional.

## VNBOT 0.7 — Agentes

- Skills.
- Agentes especializados.
- Mascotas por agente.
- Presupuestos.
- Auditoría.

## VNBOT 1.0 — Plataforma estable

- Instalación documentada.
- Backups verificados.
- Releases firmados.
- Plugin SDK.
- Suite de pruebas.
- Guía de seguridad.

---

# 16. Criterios de lanzamiento del MVP

VNBOT podrá considerarse listo para una primera versión pública cuando:

1. Un usuario pueda instalarlo sin editar código fuente.
2. El flujo de captura funcione sin LLM mediante heurística básica.
3. Los recordatorios sean persistentes e idempotentes.
4. Exista una vista clara de tareas y recordatorios.
5. La memoria tenga edición, eliminación y procedencia.
6. El grafo tenga una alternativa textual.
7. El modo local no dependa de servicios cloud.
8. El sistema tenga healthchecks y diagnóstico CLI.
9. Exista exportación y restauración probada.
10. Los errores no expongan secretos ni contenido privado en logs.
11. El repositorio tenga CI, licencia, seguridad y guía de contribución.
12. La demo de GitHub Pages no solicite datos reales.

---

# 17. Backlog inicial priorizado

## P0 — Imprescindible

- [ ] Crear monorepo.
- [ ] Implementar modelo de dominio.
- [ ] Crear almacenamiento local SQLite/IndexedDB.
- [ ] Crear chat base.
- [ ] Crear parser heurístico de recordatorios.
- [ ] Crear scheduler y ocurrencias.
- [ ] Crear notificación local.
- [ ] Crear CRUD de memoria.
- [ ] Crear exportación.
- [ ] Crear healthchecks.
- [ ] Crear demo mock para GitHub Pages.

## P1 — Necesario para beta

- [ ] FastAPI.
- [ ] PostgreSQL.
- [ ] Redis y workers.
- [ ] LLM Router.
- [ ] Búsqueda híbrida.
- [ ] Grafo visual.
- [ ] Docker Compose.
- [ ] Audio.
- [ ] APK.
- [ ] Desktop.

## P2 — Expansión

- [ ] MCP Gateway.
- [ ] Graphify adapter.
- [ ] Calendario.
- [ ] Skills.
- [ ] Agentes personalizados.
- [ ] Briefings.
- [ ] Telegram.
- [ ] Gmail como borrador.

## P3 — Comunidad y escala

- [ ] Plugin SDK.
- [ ] Marketplace de skills.
- [ ] Sincronización multi-dispositivo.
- [ ] Espacios compartidos.
- [ ] Grafo temporal avanzado.
- [ ] Métricas agregadas opt-in.

---

# 18. Fallback heurístico sin LLM — Experiencia mínima aceptable

VNBOT debe funcionar sin un proveedor LLM conectado. El fallback heurístico define el piso de experiencia cuando no hay IA disponible.

### 18.1. Alcance del fallback

El sistema heurístico debe cubrir al menos las siguientes intenciones sin LLM:

| Intención | Método | Ejemplo |
|---|---|---|
| Crear recordatorio | Regex + parsing de fecha/hora natural | "recuérdame llamar a Ana mañana a las 5" → recordatorio puntual |
| Crear memoria | Captura directa sin estructura | "mi código postal es 1040" → memoria tipo fact |
| Consultar memorias | Búsqueda textual exacta y fuzzy | "buscar Daniel" → coincidencias por texto |
| Listar recordatorios | Query directa a storage | "¿qué tengo hoy?" → recordatorios del día |
| Completar recordatorio | Match por ID o texto parcial | "ya llamé a Ana" → marcar completado |
| Crear lista | Comando estructurado | "lista de compras: leche, pan" → lista con items |

### 18.2. Límites del fallback

Lo que el fallback NO debe intentar:

- Inferir relaciones entre memorias (requiere embeddings o reglas complejas).
- Interpretar imágenes o audio (requiere modelos específicos).
- Generar resúmenes o briefings.
- Operar herramientas MCP.
- Manejar contexto conversacional multi-turno complejo.

Cuando el fallback no pueda interpretar una intención, debe responder con un mensaje claro: "No pude interpretar eso sin un modelo de IA conectado. [Instrucciones para configurar un proveedor]."

### 18.3. Criterios de aceptación

- Un usuario puede crear, consultar y completar recordatorios sin LLM.
- Un usuario puede capturar y buscar memorias sin LLM.
- La experiencia sin LLM está documentada en el onboarding.
- El fallback tiene tests unitarios con al menos 20 casos de entrada documentados.
- El mensaje de "no disponible sin LLM" incluye enlace a configuración.

---

# 19. Requisitos de accesibilidad

### 19.1. Estándar objetivo

VNBOT debe cumplir WCAG 2.2 nivel AA como mínimo en todas sus interfaces. El nivel AAA es un objetivo aspiracional para componentes críticos (chat, recordatorios, confirmaciones de acciones).

### 19.2. Métricas concretas

| Métrica | Requisito | Verificación |
|---|---|---|
| Contraste de texto | Mínimo 4.5:1 (AA) para texto normal, 3:1 para texto grande | Lighthouse + axe-core en CI |
| Contraste de paneles HUD | Mínimo 3:1 entre borde de panel y fondo adyacente | Manual + herramienta |
| Tamaño mínimo de texto | 14px en móvil, 12px solo en labels de estado no esenciales | Design tokens |
| Touch targets | Mínimo 44×44px en móvil (WCAG 2.5.8) | Layout tests |
| Navegación por teclado | Todas las funciones accesibles sin ratón | Testing manual e2e |
| Screen reader | Labels ARIA en todos los componentes interactivos | axe-core + manual |
| Reduced motion | Respetar `prefers-reduced-motion: reduce` | CSS + tests visuales |
| Focus visible | Indicador de foco visible en todos los elementos interactivos | Automated + manual |

### 19.3. Plan de auditoría de accesibilidad

- Auditoría inicial antes de v0.2.
- Auditoría por cada release minor (0.x).
- axe-core automatizado en CI para cada PR.
- Auditoría manual con screen reader (NVDA/VoiceOver) antes de cada release major.
- Test con usuarios con discapacidades antes de v1.0.

---

# 20. Definición de “hecho” de una funcionalidad

Una funcionalidad se considera terminada cuando:

- Tiene requisito identificado.
- Tiene diseño UX.
- Tiene contrato de datos/API.
- Tiene estados de error.
- Tiene política de permisos.
- Tiene pruebas unitarias.
- Tiene prueba de integración.
- Tiene documentación.
- Tiene comportamiento offline o degradado definido.
- No filtra secretos en logs.
- Funciona en el entorno objetivo.
- Tiene criterio de rollback o migración si modifica datos.

---

# 21. Decisiones abiertas

Estas decisiones deberán cerrarse en documentos técnicos posteriores:

1. SQLite local con SQLAlchemy o una capa Rust/SQLite para desktop.
2. Capacitor frente a React Native si aumentan las funciones nativas.
3. Celery/Dramatiq frente a un worker Rust.
4. pgvector frente a un índice vectorial local dedicado.
5. WebAuthn en el MVP o en una release posterior.
6. Formato final de skills: Markdown + YAML o JSON Schema + Markdown.
7. Transporte MCP principal: stdio local y Streamable HTTP remoto.
8. Sistema de actualización automática de desktop.
9. Política final de retención de audios.
10. Compatibilidad exacta de licencias para assets generados y repositorios de referencia.

---

# 22. Relación con otros documentos

- [Documento Maestro](./00-DOCUMENTO-MAESTRO-VNBOT.md): visión canónica y decisiones generales.
- [TRD](./02-TRD-VNBOT.md): decisiones técnicas y requisitos de infraestructura.
- [Esquema Backend](./03-ESQUEMA-BACKEND-VNBOT.md): servicios, API, jobs y eventos.
- [Plan de Implementación](./04-PLAN-IMPLEMENTACION-VNBOT.md): fases y ejecución detallada.
- [Diseño UI/UX](./05-DISENO-UI-UX-VNBOT.md): interfaz, mascotas y sistema visual.
- [App Flow](./06-APP-FLOW-VNBOT.md): recorridos y estados de usuario.
- [Modelo de Datos](./07-MODELO-DATOS-VNBOT.md): entidades y persistencia.
- [Seguridad](./08-SEGURIDAD-Y-PRIVACIDAD-VNBOT.md): amenazas, controles y privacidad.
- [MCP y Skills](./09-MCP-Y-SKILLS-VNBOT.md): herramientas, agentes y permisos.
- [Roadmap](./10-ROADMAP-VNBOT.md): releases y prioridades.

---

# 23. Conclusión

VNBOT debe empezar como un sistema pequeño y fiable, no como un agente omnipotente. El núcleo del producto es la relación entre captura, memoria y recordatorio. Los LLM, MCP, agentes, canales y assets visuales deben ampliar ese núcleo sin ocultar su funcionamiento ni debilitar la privacidad.

La primera pregunta para cada nueva funcionalidad debe ser:

> ¿Ayuda al usuario a recordar, encontrar o ejecutar algo de manera más confiable y controlable?

Si la respuesta es afirmativa, la funcionalidad puede incorporarse mediante un módulo, skill, integración o agente con permisos claros. Si la respuesta es negativa, debe permanecer fuera del núcleo aunque sea técnicamente atractiva.
