# VNBOT — App Flow

> **Documento:** Flujos de aplicación y recorridos de usuario
> **Producto:** VNBOT
> **Versión:** 1.0.0-draft
> **Estado:** Diseño de navegación y estados
> **Fecha:** 2026-07-16
> **Documentos relacionados:** [PRD](./01-PRD-VNBOT.md), [TRD](./02-TRD-VNBOT.md), [Backend](./03-ESQUEMA-BACKEND-VNBOT.md), [UI/UX](./05-DISENO-UI-UX-VNBOT.md)

---

# 1. Propósito

Este documento describe cómo una persona atraviesa VNBOT desde que abre la aplicación hasta que captura información, crea recordatorios, consulta su memoria, configura agentes y conecta herramientas MCP.

El App Flow define:

- Pantallas.
- Rutas.
- Estados.
- Transiciones.
- Decisiones.
- Errores.
- Confirmaciones.
- Flujos online/offline.
- Diferencias entre web, APK, desktop y CLI.

El flujo de VNBOT debe lograr que una función compleja internamente parezca simple para el usuario, pero sin ocultar las consecuencias de una acción. La IA puede interpretar lenguaje natural, pero el usuario debe comprender cuándo se ha guardado una memoria, cuándo se ha creado un recordatorio y cuándo una herramienta externa está a punto de actuar.

---

# 2. Principios de flujo

## 2.1. Captura rápida, acción explicada

La captura debe ser inmediata. La ejecución debe ser explícita cuando tenga consecuencias.

```text
Capturar → Interpretar → Mostrar propuesta → Confirmar si aplica → Ejecutar → Informar
```

## 2.2. No fingir éxito

Si una operación fue encolada pero todavía no terminó, el estado debe ser “En cola” o “Procesando”, no “Completado”.

## 2.3. Recuperación en cada error

Cada error debe indicar:

- Qué sucedió.
- Qué datos se conservaron.
- Qué parte no se pudo completar.
- Si se reintentará.
- Qué puede hacer el usuario.

## 2.4. Online y offline deben ser explícitos

El usuario debe saber si trabaja:

- Localmente.
- Sin conexión.
- Con sincronización pendiente.
- Contra un servidor.
- Mediante un proveedor cloud.

## 2.5. Un flujo, varias interfaces

Web, APK, desktop y CLI deben compartir los mismos estados de dominio, aunque su presentación sea diferente.

---

# 3. Mapa de navegación

```text
/                         Landing o entrada
/onboarding               Configuración inicial
/auth/login               Inicio de sesión remoto
/auth/register            Registro
/unlock                    Desbloqueo de bóveda
/today                     Centro operativo
/chat                      Conversación
/chat/:conversationId     Conversación específica
/memory                    Lista de memorias
/memory/:id               Detalle de memoria
/graph                     Grafo de memoria
/lists                     Listas
/agents                    Agentes
/agents/new               Crear agente
/agents/:id               Detalle/configuración de agente
/skills                    Catálogo de skills
/integrations              Integraciones
/integrations/mcp/new      Conectar MCP
/activity                  Actividad y auditoría
/settings                  Configuración
/settings/privacy          Privacidad y datos
/settings/models           Modelos LLM
/settings/notifications    Notificaciones
/settings/security         Seguridad
/diagnostics               Diagnóstico
```

En la aplicación local puede omitirse `/auth/login` si el usuario utiliza una bóveda local sin servidor.

---

# 4. Estados globales de la aplicación

```text
BOOTING
FIRST_RUN
AUTH_REQUIRED
LOCKED
READY
OFFLINE
SYNC_PENDING
DEGRADED_LLM
DEGRADED_WORKER
MCP_REAUTH_REQUIRED
MAINTENANCE
FATAL_ERROR
```

## 4.1. `BOOTING`

La aplicación:

- Carga configuración.
- Comprueba versión de schema local.
- Inicializa IndexedDB/SQLite.
- Comprueba conectividad.
- Recupera sesión no sensible.

No debe mostrar un chat interactivo hasta conocer el estado de almacenamiento.

## 4.2. `FIRST_RUN`

No existe bóveda ni configuración inicial. Se dirige al onboarding.

## 4.3. `AUTH_REQUIRED`

El servidor requiere autenticación. Se muestra login o registro.

## 4.4. `LOCKED`

La aplicación está instalada, pero la bóveda está cerrada. El usuario puede desbloquearla mediante passphrase, biometría futura o sesión local.

## 4.5. `READY`

La aplicación puede utilizar todas las capacidades disponibles según permisos y conexión.

## 4.6. `OFFLINE`

Se puede trabajar con capacidades locales. Las operaciones remotas pasan a cola.

## 4.7. `SYNC_PENDING`

Existen cambios locales que todavía no se han sincronizado.

## 4.8. `DEGRADED_LLM`

El LLM no está disponible. Se activa heurística o modo manual.

## 4.9. `DEGRADED_WORKER`

La API está disponible, pero el worker no responde. Se pueden recibir operaciones, pero las tareas asíncronas muestran estado pendiente.

## 4.10. Mapeo estado → mascota → visual

Cada estado global de la aplicación tiene una representación visual directa en la mascota del golem. Este mapeo asegura que el usuario reciba feedback visual inmediato del estado del sistema. Ver [UI/UX — Sección 19](./05-DISENO-UI-UX-VNBOT.md) para el detalle completo del sistema de sprites.

| Estado global | Estado mascota | Visor | Emote UI | Texto accesible |
|---|---|---|---|---|
| `BOOTING` | `processing` | Anillo multicolor | loading | "Iniciando VNBOT" |
| `FIRST_RUN` | `idle` | Cyan estable | neutral | "Bienvenido a VNBOT" |
| `AUTH_REQUIRED` | `sleeping` | Apagado | offline | "Inicia sesión para continuar" |
| `LOCKED` | `sleeping` | Apagado | sleepy | "Bóveda bloqueada" |
| `READY` | `idle` | Cyan estable | neutral | "Listo" |
| `OFFLINE` | `offline` | Apagado, sin brillo | offline | "Sin conexión" |
| `SYNC_PENDING` | `processing` | Anillo multicolor | loading | "Sincronizando cambios" |
| `DEGRADED_LLM` | `warning` | Amber intermitente | warning | "Modelo de IA no disponible. Usando modo local." |
| `DEGRADED_WORKER` | `error` | Rojo breve, luego quieto | error | "Servidor de tareas no disponible" |

### Reglas del mapeo

1. **Un estado global = un estado de mascota.** No hay estados visuales ambiguos.
2. **El texto accesible es obligatorio.** El sprite solo es complemento visual. El estado siempre se comunica también mediante texto con `aria-live="polite"`.
3. **Los emotes se usan en contextos compactos** (toasts, badges, notificaciones push) donde el sprite completo de 64px no cabe.
4. **Las transiciones son instantáneas entre estados globales**, no animadas (la animación es dentro de un estado, no entre estados).
5. **El componente `<MascotStateView>`** recibe el estado desde el store global y renderiza automáticamente el sprite correcto.

---

# 5. Flujo de arranque

```text
Abrir VNBOT
  ↓
BOOTING
  ↓
¿Primera ejecución?
  ├─ Sí → FIRST_RUN
  └─ No
       ↓
¿Modo servidor?
  ├─ Sí → ¿Sesión válida?
  │       ├─ No → AUTH_REQUIRED
  │       └─ Sí → ¿Bóveda desbloqueada?
  │                ├─ No → LOCKED
  │                └─ Sí → READY
  └─ No → ¿Bóveda desbloqueada?
           ├─ No → LOCKED
           └─ Sí → READY
```

## 5.1. Fallo durante arranque

Si falla una dependencia:

- SQLite/IndexedDB: no se debe fingir que los datos están disponibles.
- API: permitir modo local si existe.
- Redis: marcar workers degradados.
- LLM: activar heurística.
- MCP: mostrar integración desconectada.

---

# 6. Onboarding

## 6.1. Objetivo

Conseguir que el usuario llegue a su primer resultado útil sin recibir un formulario complejo.

## 6.2. Flujo

```text
Bienvenida
  ↓
¿Qué deseas configurar?
  ├─ Uso local
  └─ Conectar a servidor
  ↓
Zona horaria
  ↓
Idioma
  ↓
Bóveda
  ↓
Modelo
  ↓
Mascota
  ↓
Primer recordatorio
  ↓
Hoy
```

## 6.3. Selección de modo

### Uso local

- Crear bóveda local.
- Elegir LLM local o continuar sin LLM.
- No solicitar email obligatoriamente.

### Servidor

- Introducir URL.
- Probar conexión.
- Login/registro.
- Seleccionar workspace.
- Descargar configuración segura.

## 6.4. Configuración de bóveda

El usuario debe entender:

- Qué protege la passphrase.
- Qué ocurre si la pierde.
- Si existe recuperación.
- Qué datos se cifran.
- Qué datos puede ver el servidor según el modo.

No se debe presentar una promesa de “zero-knowledge” si el flujo posterior envía texto a un LLM remoto.

## 6.5. Primer resultado

Se propone una instrucción editable:

> “Recuérdame mañana a las 9 revisar VNBOT.”

El usuario puede cambiarla. La app muestra la interpretación y pide confirmación.

---

# 7. Flujo de autenticación

## 7.1. Registro

```text
Registro
  ↓
Email + contraseña
  ↓
Validación
  ↓
Creación de cuenta
  ↓
Workspace personal
  ↓
Configurar bóveda
  ↓
Hoy
```

## 7.2. Login

```text
Login
  ↓
Validar sesión
  ↓
¿MFA?
  ├─ Sí → Código/WebAuthn
  └─ No
       ↓
¿Bóveda bloqueada?
  ├─ Sí → Unlock
  └─ No → Hoy
```

## 7.3. Sesión caducada

La aplicación debe preservar el borrador local, mostrar sesión caducada y no eliminar automáticamente información escrita.

```text
Sesión caducada
  ↓
Guardar borrador local
  ↓
Solicitar login
  ↓
Revalidar workspace
  ↓
Reanudar operación o descartar
```

## 7.4. Cierre de sesión

- Revocar sesión remota.
- Bloquear bóveda local.
- Limpiar tokens temporales.
- Mantener datos cifrados locales.
- Preguntar si se desea eliminar la sesión del dispositivo.

---

# 8. Flujo de desbloqueo

```text
LOCKED
  ↓
Introducir passphrase
  ↓
Derivar clave
  ↓
Verificar payload de control
  ├─ Correcta → READY
  └─ Incorrecta → Error + reintentar
```

## 8.1. Protección

- No indicar detalles que faciliten ataques de fuerza bruta.
- Backoff tras varios intentos.
- Auto-lock configurable.
- No persistir passphrase en texto.
- Borrar material criptográfico de memoria al bloquear.

## 8.2. Pérdida de passphrase

El flujo debe indicar si existe:

- Backup con clave externa.
- Recuperación de cuenta sin recuperar la bóveda.
- Restauración desde exportación.

Nunca prometer recuperación de contenido cifrado si la clave se perdió y no existe un mecanismo válido.

---

# 9. Flujo principal del chat

## 9.1. Vista inicial

```text
Chat vacío
  ├─ Capturar algo
  ├─ Preguntar a mi memoria
  ├─ Crear recordatorio
  └─ Crear lista
```

## 9.2. Enviar texto

```text
Usuario escribe
  ↓
Enviar
  ↓
Validar longitud y archivos
  ↓
Crear mensaje
  ↓
Mascota LISTENING/THINKING
  ↓
Clasificar intención
  ↓
Recuperar contexto autorizado
  ↓
Generar propuesta
```

## 9.3. Resultado informativo

Si la intención es una consulta:

```text
Pregunta
  ↓
Buscar memoria
  ↓
Filtrar permisos
  ↓
Generar respuesta con fuentes
  ↓
Mostrar respuesta
  ↓
Opciones: guardar / convertir en tarea / crear recordatorio
```

## 9.4. Resultado operativo

Si la intención crea o modifica algo:

```text
Mensaje
  ↓
Propuesta estructurada
  ↓
¿Falta información?
  ├─ Sí → NEEDS_CLARIFICATION
  └─ No
       ↓
¿Riesgo requiere confirmación?
  ├─ Sí → WAITING_CONFIRMATION
  └─ No → QUEUED/EXECUTING
```

## 9.5. Respuesta del agente

Debe separar:

- Texto natural.
- Memorias utilizadas.
- Acción propuesta.
- Estado.
- Herramienta.
- Controles.

---

# 10. Flujo de crear un recordatorio

## 10.1. Entrada clara

Entrada:

> “Recuérdame pagar la electricidad mañana a las 8.”

Flujo:

```text
Detectar intent
  ↓
Extraer título
  ↓
Resolver mañana
  ↓
Resolver 08:00
  ↓
Aplicar timezone
  ↓
Crear propuesta
  ↓
Mostrar fecha completa
  ↓
Confirmar
  ↓
Crear Reminder
  ↓
Crear Occurrence
  ↓
Programar delivery
  ↓
Success
```

## 10.2. Entrada ambigua

Entrada:

> “Recuérdame pagar la electricidad el viernes.”

Respuesta:

```text
Puedo crear el recordatorio para el viernes 17 de julio de 2026.
¿Qué hora prefieres?

[08:00] [12:00] [18:00] [Elegir hora]
```

No debe inventarse una hora silenciosamente.

## 10.3. Recordatorio recurrente

Entrada:

> “Cada lunes a las 9 recuérdame revisar el presupuesto.”

Debe crearse una regla recurrente. La vista de confirmación debe indicar:

- Día.
- Hora.
- Zona horaria.
- Próxima ocurrencia.
- Recurrencia.
- Canal.

## 10.4. Recordatorio a tercero

No se activa en MVP, pero el flujo futuro será:

```text
Crear recordatorio externo
  ↓
Identificar destinatario
  ↓
Verificar canal y consentimiento
  ↓
Mostrar mensaje exacto
  ↓
Definir frecuencia máxima
  ↓
Confirmación fuerte
  ↓
Enviar primer contacto
  ↓
Registrar respuesta/opt-out
```

---

# 11. Flujo de completar y posponer

## Completar

```text
Notificación
  ↓
Completar
  ↓
¿Recurrente?
  ├─ Sí → completar ocurrencia y generar próxima
  └─ No → cerrar recordatorio
  ↓
Actualizar memoria/actividad
```

## Posponer

```text
Posponer
  ↓
Opciones rápidas
  ├─ 15 minutos
  ├─ 1 hora
  ├─ Mañana
  └─ Elegir fecha
  ↓
Validar nueva fecha
  ↓
Actualizar occurrence
  ↓
Registrar evento
```

## Error de entrega

```text
Delivery failed
  ↓
¿Error temporal?
  ├─ Sí → retry/backoff
  └─ No → pedir reconexión
  ↓
Recordatorio sigue visible como pendiente
```

---

# 12. Flujo de guardar una memoria

## 12.1. Memoria explícita

Entrada:

> “Guarda que Daniel prefiere reuniones después de las 4.”

```text
Detectar save_memory
  ↓
Resolver persona Daniel
  ↓
Extraer preferencia
  ↓
Buscar duplicados/contradicciones
  ↓
Mostrar propuesta
  ↓
Confirmar o guardar según política
  ↓
Crear/actualizar nodos
  ↓
Crear relación PREFERS
  ↓
Indexar async
  ↓
Mostrar fuente
```

## 12.2. Memoria inferida

Si una preferencia se detecta en una conversación sin que el usuario diga “recuerda”, debe marcarse como sugerencia:

```text
Parece que prefieres reuniones después de las 16:00.
¿Quieres guardarlo como preferencia?
[Guardar] [No guardar] [No volver a sugerir]
```

## 12.3. Contradicción

Si existe:

> “Daniel prefiere reuniones por la mañana.”

La UI muestra:

```text
Encontré una preferencia anterior que podría contradecir esta.
[Conservar ambas con fechas]
[Reemplazar anterior]
[Descartar nueva]
```

---

# 13. Flujo de búsqueda de memoria

```text
Usuario escribe pregunta
  ↓
Clasificar como query
  ↓
Detectar entidades y fecha
  ↓
Búsqueda textual/semántica/grafo
  ↓
Filtrar por workspace y sensibilidad
  ↓
Reordenar resultados
  ↓
Construir respuesta
  ↓
Mostrar fuentes
```

## 13.1. Sin resultados

```text
No encontré una memoria confirmada.

Puedes:
[Buscar de forma más amplia]
[Guardar esta pregunta]
[Crear una memoria nueva]
```

No se debe inventar respuesta para llenar el vacío.

## 13.2. Resultados conflictivos

Mostrar primero el conflicto y no ocultarlo en el resumen.

## 13.3. Conversión de respuesta

Desde una respuesta el usuario puede:

- Guardar resumen.
- Crear tarea.
- Crear recordatorio.
- Abrir nodos relacionados.

---

# 14. Flujo de audio

## 14.1. Permisos

```text
Pulsar micrófono
  ↓
¿Permiso concedido?
  ├─ No → explicar permiso y ofrecer texto
  └─ Sí → LISTENING
```

## 14.2. Grabación

- Mostrar tiempo.
- Permitir pausa.
- Permitir cancelar.
- Mostrar estado de micrófono.
- No grabar al cerrar accidentalmente sin advertencia.

## 14.3. Transcripción

```text
Detener grabación
  ↓
Guardar audio temporal
  ↓
Elegir transcripción local/cloud
  ↓
Crear job
  ↓
TRANSCRIBING
  ↓
Mostrar transcript editable
```

## 14.4. Procesar transcript

```text
Transcript revisado
  ↓
Enviar al flujo de chat
  ↓
Detectar intent
  ↓
Proponer acción
  ↓
Confirmar según riesgo
```

## 14.5. Retención

Después de procesar:

- Eliminar audio.
- Conservar audio.
- Conservar durante periodo.

La decisión debe ser visible antes o inmediatamente después del procesamiento.

---

# 15. Flujo de memoria y grafo

## 15.1. Abrir grafo

```text
Memoria → Grafo
  ↓
Cargar subgrafo inicial
  ↓
Mostrar leyenda
  ↓
Permitir búsqueda/filtros
```

## 15.2. Seleccionar nodo

```text
Click nodo
  ↓
Inspector
  ├─ Resumen
  ├─ Fuente
  ├─ Relaciones
  ├─ Historial
  └─ Acciones
```

## 15.3. Expandir

```text
Expandir conexiones
  ↓
Solicitar profundidad/nodos
  ↓
Aplicar permisos
  ↓
Mostrar nuevos nodos
  ↓
Indicar si hubo truncamiento
```

## 15.4. Editar arista

```text
Seleccionar relación
  ↓
Ver procedencia
  ↓
Editar o invalidar
  ↓
Confirmar
  ↓
Actualizar índices
```

## 15.5. Graphify

```text
Grafo → Fuentes externas
  ↓
Ver Graphify conectado
  ↓
Consultar solo lectura
  ↓
Mostrar origen externo
  ↓
Crear referencia opcional
```

Los datos externos deben marcarse visualmente como externos.

---

# 16. Flujo de crear un agente

```text
Agentes
  ↓
Crear agente
  ↓
Nombre y descripción
  ↓
Elegir mascota
  ↓
Elegir modelo
  ↓
Definir instrucciones
  ↓
Asignar skills
  ↓
Asignar memoria
  ↓
Asignar herramientas
  ↓
Definir autonomía
  ↓
Definir presupuesto
  ↓
Revisar permisos
  ↓
Simular
  ↓
Activar
```

## 16.1. Resumen de permisos

Antes de activar:

```text
Este agente podrá:
✓ Leer memorias de trabajo
✓ Crear recordatorios
✓ Consultar Graphify
✕ Enviar correos
✕ Leer archivos personales
✕ Eliminar memorias
```

## 16.2. Simulación

El usuario escribe una instrucción y el agente muestra:

- Qué memoria consultaría.
- Qué herramienta usaría.
- Qué acción propondría.
- Qué permiso necesitaría.

No se ejecuta ningún efecto externo durante la simulación.

---

# 17. Flujo de skills

## 17.1. Instalar skill

```text
Skills
  ↓
Abrir detalle
  ↓
Revisar versión/licencia
  ↓
Revisar herramientas
  ↓
Revisar riesgo
  ↓
Instalar
  ↓
Asignar a agentes
```

## 17.2. Actualizar skill

- Mostrar cambios de permisos.
- Mostrar versión anterior/nueva.
- Solicitar confirmación si aumenta el riesgo.
- Permitir rollback si la instalación lo soporta.

## 17.3. Desinstalar

- Desactivar primero.
- Mantener datos creados por la skill salvo que el usuario solicite borrarlos.
- Revocar herramientas asociadas.
- Registrar la operación.

---

# 18. Flujo de conectar MCP

```text
Integraciones
  ↓
Añadir MCP
  ↓
Elegir local stdio o remoto HTTP
  ↓
Introducir configuración
  ↓
Probar handshake
  ↓
Mostrar serverInfo/capabilities
  ↓
Mostrar tools/resources
  ↓
Seleccionar scopes
  ↓
Probar healthcheck
  ↓
Guardar credenciales
  ↓
Activar
```

## 18.1. Fallos

### Handshake fallido

Mostrar endpoint, transporte y código de error sin revelar token.

### Tool no disponible

Marcar integración degradada y mantener el resto de VNBOT funcional.

### Reautenticación

Conservar configuración, pausar llamadas y pedir reconectar.

### Respuesta mal formada

No ejecutar acciones derivadas. Registrar error de protocolo.

---

# 19. Flujo de modo offline

```text
Se pierde conexión
  ↓
Mostrar OFFLINE
  ↓
¿Operación local?
  ├─ Sí → ejecutar
  └─ No → guardar en outbox
       ↓
SYNC_PENDING
       ↓
Vuelve conexión
       ↓
Validar sesión
       ↓
Enviar outbox con idempotency key
       ↓
Resolver conflictos
       ↓
SYNCED
```

## 19.1. Operaciones permitidas offline

- Crear memoria local.
- Editar memoria local.
- Crear recordatorio local.
- Completar recordatorio local.
- Consultar datos cacheados.
- Grabar audio si el dispositivo lo permite.

## 19.2. Operaciones no ejecutadas offline

- Enviar email.
- Consultar MCP remoto.
- Crear evento externo.
- Sincronizar con calendario.
- Generar respuesta mediante LLM cloud.

## 19.3. Conflictos

Si el mismo nodo cambió local y remotamente:

```text
Conflicto detectado
[Usar versión local]
[Usar versión del servidor]
[Comparar y combinar]
```

---

# 20. Flujo de exportación

```text
Ajustes → Datos → Exportar
  ↓
Elegir alcance
  ├─ Todo
  ├─ Workspace
  ├─ Memoria
  └─ Recordatorios
  ↓
Elegir incluir archivos/audio
  ↓
Elegir cifrado
  ↓
Crear job
  ↓
Preparar ZIP
  ↓
Verificar checksum
  ↓
Descargar/guardar
```

## 20.1. Exportación sensible

Debe advertir que el archivo exportado puede contener información privada y que la seguridad de la copia queda bajo responsabilidad del usuario.

## 20.2. Importación

```text
Seleccionar backup
  ↓
Verificar manifest/checksum
  ↓
Mostrar resumen
  ↓
Elegir workspace destino
  ↓
Detectar duplicados
  ↓
Confirmar
  ↓
Importar por jobs
  ↓
Mostrar reporte
```

---

# 21. Flujo de eliminación

## 21.1. Eliminar memoria

```text
Abrir memoria
  ↓
Olvidar
  ↓
Mostrar relaciones afectadas
  ↓
Confirmar
  ↓
Soft delete
  ↓
Invalidar índices
  ↓
Purgar según política
```

## 21.2. Eliminar cuenta

```text
Ajustes → Seguridad → Eliminar cuenta
  ↓
Exportación recomendada
  ↓
Reautenticación
  ↓
Confirmación fuerte
  ↓
Revocar integraciones
  ↓
Encolar purga
  ↓
Cerrar sesiones
  ↓
Mostrar estado de eliminación
```

No se debe afirmar que los datos fueron eliminados instantáneamente si existen backups o colas de purga pendientes. La UI debe explicar los tiempos de retención.

---

# 22. Flujo de notificación

## 22.1. Notificación estándar

```text
Occurrence due
  ↓
Job delivery
  ↓
Comprobar cancelación/completado
  ↓
Comprobar silencio
  ↓
Seleccionar canal
  ↓
Enviar
  ↓
Registrar delivery
```

## 22.2. Usuario interactúa desde notificación

- Completar.
- Posponer.
- Abrir detalle.
- Ignorar.

Cada acción debe pasar por API o almacenamiento local con idempotencia.

---

# 23. Flujo de actividad y diagnóstico

```text
Actividad
  ↓
Filtrar operaciones
  ↓
Abrir evento
  ↓
Ver timeline
  ├─ Entrada
  ├─ Interpretación
  ├─ Confirmación
  ├─ Herramienta
  ├─ Resultado
  └─ Reintentos
```

## 23.1. `vnbot doctor`

En desktop/CLI:

```text
Comprobar versión
Comprobar permisos
Comprobar almacenamiento
Comprobar migraciones
Comprobar API
Comprobar Redis
Comprobar worker
Comprobar LLM
Comprobar MCP
Comprobar espacio
Comprobar backup
```

## 23.2. Fallo de worker

La UI debe mostrar:

```text
El servidor está disponible, pero el worker no responde.
Tus recordatorios siguen guardados.
Las notificaciones pendientes se procesarán cuando el worker vuelva.
[Ver diagnóstico] [Reintentar conexión]
```

---

# 24. Flujo de GitHub Pages

```text
Visitar sitio
  ↓
Landing
  ↓
Demo
  ↓
Elegir escenario
  ├─ Crear recordatorio
  ├─ Explorar grafo
  └─ Cambiar agente
  ↓
Resultado simulado
  ↓
Instalar VNBOT
  ├─ APK
  ├─ Desktop
  ├─ Docker
  └─ Desarrollo
```

La demo no debe hacer creer que una acción externa se ejecutó realmente.

---

# 25. Diferencias por plataforma

## Web/PWA

- Notificaciones web.
- IndexedDB.
- Service Worker.
- Permisos de navegador.
- Pérdida posible de contexto si se borra el sitio.

## Android

- Notificaciones locales.
- Permiso de micrófono.
- Estado de red.
- Restricciones de background.
- Filesystem móvil.

## Desktop

- Notificaciones nativas.
- SQLite local.
- Integración con archivos.
- Atajos de teclado.
- Menú de bandeja posterior.

## CLI

- Texto y JSON.
- No depende del layout visual.
- Debe exponer estados y errores.
- Puede funcionar en servidores sin GUI.

---

# 26. Estados de error globales

## Error de validación

Mostrar campo y corrección recomendada.

## Error de autenticación

Preservar borrador local y solicitar sesión.

## Error de proveedor LLM

Activar heurística y mostrar degradación.

## Error de MCP

Mantener la integración aislada y el resto operativo.

## Error de base de datos

No aceptar acciones que no puedan persistirse.

## Error de notificación

Conservar recordatorio como pendiente.

## Error de almacenamiento

No descartar audio/archivo sin informar.

## Error fatal

Mostrar diagnóstico, versión, request_id y opción de exportar logs sanitizados.

---

# 27. Flujos de confirmación

## Bajo riesgo

Puede ejecutarse automáticamente si el usuario activó esa política:

- Guardar una nota.
- Crear lista local.
- Crear recordatorio propio.

## Riesgo medio

Mostrar propuesta antes de ejecutar:

- Crear evento externo.
- Modificar relación.
- Cambiar preferencia.
- Sincronizar datos.

## Alto riesgo

Confirmación fuerte:

- Enviar email.
- Compartir contenido.
- Escribir archivos.
- Contactar terceros.
- Borrar muchas memorias.

## Crítico

No disponible en MVP:

- Acciones financieras.
- Cambios de permisos globales.
- Ejecución arbitraria del sistema.

---

# 28. App Flow resumido de extremo a extremo

```text
┌──────────────┐
│ Abrir VNBOT  │
└──────┬───────┘
       ▼
┌──────────────┐      ┌──────────────┐
│ Boot/health  │─────▶│ First run    │
└──────┬───────┘      └──────┬───────┘
       ▼                     ▼
┌──────────────┐      ┌──────────────┐
│ Auth/Unlock  │─────▶│ Onboarding   │
└──────┬───────┘      └──────┬───────┘
       └──────────────┬──────┘
                      ▼
               ┌──────────────┐
               │     Hoy      │
               └──────┬───────┘
                      ▼
               ┌──────────────┐
               │     Chat     │
               └──────┬───────┘
                      ▼
              ┌────────────────┐
              │ Intent/Context│
              └──────┬─────────┘
                     ▼
        ┌────────────┴─────────────┐
        │                          │
        ▼                          ▼
┌──────────────┐          ┌────────────────┐
│ Informativo  │          │ Acción         │
└──────┬───────┘          └──────┬─────────┘
       ▼                         ▼
┌──────────────┐          ┌────────────────┐
│ Fuentes      │          │ Propuesta      │
└──────────────┘          └──────┬─────────┘
                                 ▼
                        ┌────────────────┐
                        │ Confirmación   │
                        └──────┬─────────┘
                               ▼
                        ┌────────────────┐
                        │ Dominio/Job    │
                        └──────┬─────────┘
                               ▼
                        ┌────────────────┐
                        │ Resultado/log  │
                        └────────────────┘
```

---

# 29. Criterios de aceptación del App Flow

El flujo está correctamente definido cuando:

1. Cada pantalla tiene una entrada y una salida.
2. Cada operación tiene estado intermedio.
3. Las ambigüedades no se resuelven inventando datos.
4. Los errores tienen recuperación.
5. Online/offline son visibles.
6. Las acciones externas tienen confirmación.
7. Los jobs asíncronos no se presentan como completados antes de tiempo.
8. La memoria y los recordatorios tienen flujos separados pero conectables.
9. El grafo tiene alternativa textual.
10. La mascota refleja el estado del sistema.
11. El flujo funciona en web, APK, desktop y CLI.
12. El usuario puede exportar y eliminar sus datos.
13. Las integraciones pueden revocarse.
14. La demo no finge ejecuciones reales.
15. Las rutas críticas tienen pruebas E2E.

---

# 30. Mapa de pruebas E2E

## E2E-01 — Primer arranque

`Abrir → onboarding → bóveda → primer recordatorio → Hoy`.

## E2E-02 — Recordatorio ambiguo

`Chat → fecha sin hora → aclaración → confirmación → creación`.

## E2E-03 — Recordatorio recurrente

`Chat → recurrencia → ocurrencia → completar una → siguiente permanece`.

## E2E-04 — Fallo de LLM

`Chat → proveedor caído → heurística → propuesta visible`.

## E2E-05 — Fallo de worker

`Crear recordatorio → worker detenido → estado pendiente → worker recuperado → delivery`.

## E2E-06 — Memoria contradictoria

`Guardar preferencia → guardar contradicción → comparar → elegir versión`.

## E2E-07 — Offline

`Desconectar → crear memoria → reconectar → sincronizar → resolver conflicto`.

## E2E-08 — MCP

`Conectar → handshake → scope → tool call → confirmación → auditoría → revocar`.

## E2E-09 — Audio

`Permiso → grabar → transcribir → revisar → crear recordatorio`.

## E2E-10 — Eliminación

`Exportar → reautenticar → eliminar → revocar → verificar ausencia`.

---

# 33. Flujos offline-first

VNBOT está diseñado para funcionar sin conexión. El modo offline no es un error, es un estado normal de operación.

### 33.1. Estados de conexión

```text
online     → todas las operaciones disponibles
degraded   → servidor no alcanzable, LLM no disponible
offline    → sin conexión, solo operaciones locales
syncing    → reconectando, sincronizando cambios pendientes
conflict   → se detectaron conflictos durante sync
```

### 33.2. Comportamiento por estado

| Operación | Online | Degraded | Offline |
|---|---|---|---|
| Crear memoria | Inmediato + sync | Inmediato, encolado para sync | Inmediato, encolado |
| Crear recordatorio | Inmediato + sync | Inmediato (scheduler local) | Inmediato (scheduler local) |
| Buscar memorias | Textual + semántica | Solo textual | Solo textual |
| Chat con LLM | Completo | Fallback heurístico | Fallback heurístico |
| Usar MCP tool | Disponible | No disponible | No disponible |
| Exportar datos | Inmediato | Inmediato | Inmediato |
| Ver grafo | Completo | Local | Local |

### 33.3. Indicador al usuario

La UI debe mostrar siempre el estado de conexión de forma no intrusiva:

- **Online:** sin indicador visible (estado normal).
- **Degraded:** icono sutil + tooltip "Servidor no alcanzable. Operaciones locales activas."
- **Offline:** icono + banner discreto "Sin conexión. Los datos se guardan localmente."
- **Syncing:** indicador de progreso con conteo de ops pendientes.
- **Conflict:** notificación con enlace a resolución de conflictos.

### 33.4. Queue local de operaciones

Todas las operaciones que generan cambios (crear, actualizar, borrar) se encolan localmente con:

- Operation type (create, update, delete).
- Entity type y entity ID.
- Timestamp local.
- Version vector del dispositivo.

Cuando la conexión se restablece, la queue se procesa en orden FIFO. Las operaciones fallidas se reintentan con backoff exponencial (máximo 3 intentos antes de marcar como conflicto manual).

---

# 34. Flujo de resolución de conflictos de sincronización

Este flujo se activa cuando dos dispositivos modifican la misma entidad sin conocimiento mutuo. Ver [Estrategia de Sync](./11-ESTRATEGIA-SYNC-VNBOT.md) para el diseño técnico completo.

### 34.1. Detección

Un conflicto se detecta cuando el servidor recibe una operación con un version vector que no coincide con el estado actual.

### 34.2. Notificación al usuario

```text
1. El usuario ve un badge en el panel de actividad.
2. Al abrir, ve la lista de conflictos con:
   - Nombre de la entidad.
   - Qué cambió en cada dispositivo.
   - Timestamp de cada versión.
3. El usuario elige:
   a. Mantener la versión local.
   b. Mantener la versión remota.
   c. Fusionar manualmente (abrir editor).
   d. Mantener ambas (crear una copia).
```

### 34.3. Reglas automáticas

Algunos conflictos se resuelven automáticamente:

- **Recordatorio completado en un dispositivo, modificado en otro:** prevalece el completado (no se puede "descompletar" sin acción explícita).
- **Memoria borrada en un dispositivo, editada en otro:** prevalece el borrado si el usuario lo confirmó. Se ofrece "recuperar" la versión editada.
- **Mismo campo modificado con el mismo valor:** no es conflicto, se ignora.

### 34.4. Flujo de pantalla

```text
[Notificación de conflicto]
        ↓
[Lista de conflictos pendientes]
        ↓ (seleccionar uno)
[Vista de diff: versión local vs remota]
        ↓
[Elegir: local | remota | fusionar | ambas]
        ↓
[Confirmación]
        ↓
[Conflicto resuelto → se sincroniza]
```

---

# 35. Flujo de captura con fallback heurístico

Cuando no hay LLM disponible, el flujo de captura cambia:

### 35.1. Proceso

```text
1. Usuario escribe o habla (si hay audio local).
2. El sistema intenta parsear con heurísticas:
   - Patrones de recordatorio: regex de fecha/hora + verbo de acción.
   - Patrones de memoria: captura directa si no coincide con nada más.
   - Patrones de consulta: si empieza con "buscar", "qué", "cuándo".
3. Si el parseo tiene confianza alta:
   - Se muestra la propuesta estructurada.
   - El usuario confirma o edita.
4. Si el parseo tiene confianza baja:
   - Se muestra un mensaje: "No pude interpretar eso con precisión. [Reintentar con diferentes palabras] o [Configurar un proveedor de IA]."
   - Se ofrece guardar como nota libre (memoria sin estructura).
5. La operación se ejecuta y se registra en auditoría.
```

### 35.2. El fallback NO intenta

- Inferir relaciones entre entidades.
- Generar resúmenes o briefings.
- Procesar imágenes o audio (sin modelos locales).
- Interpretar contexto conversacional complejo.

---

# 36. Decisiones abiertas

1. Navegación inferior definitiva en Android.
2. Uso de WebSocket o SSE para actualizaciones de jobs.
3. Flujo exacto de conflictos offline.
4. Auto-lock por plataforma.
5. Integración biométrica.
6. Uso de deep links para notificaciones.
7. Nivel de detalle de la timeline de auditoría para usuarios casuales.
8. Posibilidad de desactivar completamente la mascota.
9. Soporte de múltiples workspaces en móvil.
10. Modo terminal interactivo versus comandos simples.

---

# 37. Conclusión

El App Flow de VNBOT se basa en un ciclo controlado:

```text
Capturar
→ Interpretar
→ Explicar
→ Confirmar
→ Ejecutar
→ Auditar
→ Recuperar o corregir
```

Este ciclo permite que VNBOT sea fácil de usar sin convertirse en una caja negra. El usuario puede expresarse naturalmente, pero siempre puede revisar qué entendió el sistema, qué memoria utilizó, qué agente actuó, qué herramienta se llamó y cuál fue el resultado.

La experiencia final debe sentirse dinámica gracias a la mascota, los estados y el HUD, pero las decisiones importantes deben permanecer claras, reversibles y verificables.
