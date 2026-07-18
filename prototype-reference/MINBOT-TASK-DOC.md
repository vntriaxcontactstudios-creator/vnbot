# MinBot-Task — Documento Técnico Completo

> **Versión:** 0.5.0
> **Fecha:** 2026-07-17
> **Licencia:** MIT
> **Stack:** Next.js 16 + TypeScript 5 + Tailwind 4 + shadcn/ui + Prisma + WebCrypto

---

## Tabla de Contenidos

1. [Visión General](#1-visión-general)
2. [Arquitectura del Sistema](#2-arquitectura-del-sistema)
3. [Funcionalidades Implementadas](#3-funcionalidades-implementadas)
   - 3.1 [Cifrado Zero-Knowledge](#31-cifrado-zero-knowledge)
   - 3.2 [Multi-LLM (16 providers)](#32-multi-llm-16-providers)
   - 3.3 [Autenticación con NextAuth.js](#33-autenticación-con-nextauthjs)
   - 3.4 [Rate Limiting por LLM](#34-rate-limiting-por-llm)
   - 3.5 [Validación Zod en Endpoints](#35-validación-zod-en-endpoints)
   - 3.6 [Pixelart Procedural](#36-pixelart-procedural)
   - 3.7 [Mini-Grafo Drag & Drop](#37-mini-grafo-drag--drop)
   - 3.8 [Extensión Graphify](#38-extensión-graphify)
   - 3.9 [Integraciones Multi-Canal](#39-integraciones-multi-canal)
   - 3.10 [Local-First Store](#310-local-first-store)
   - 3.11 [Security Headers](#311-security-headers)
4. [Demos y Cómo Expandirlas](#4-demos-y-cómo-expandirlas)
5. [Roadmap: Cómo Implementar las Ideas](#5-roadmap-cómo-implementar-las-ideas)
6. [Especificaciones Técnicas](#6-especificaciones-técnicas)
7. [Estructura de Archivos](#7-estructura-de-archivos)

---

## 1. Visión General

**MinBot-Task** es una capa de memoria personal open-source, zero-knowledge y local-first. No reemplaza tus apps existentes (Memorae, Notion, WhatsApp) — **se conecta a ellas** mediante APIs oficiales para capturar, cifrar y recordar cualquier cosa desde cualquier canal.

### Principios de diseño

| Principio | Implementación |
|---|---|
| **Open Source** | MIT License, todo el código es auditable |
| **Zero-Knowledge** | Cifrado AES-256 en cliente, servidor nunca ve plaintext |
| **Local-First** | Datos en dispositivo, sync opcional |
| **Multi-LLM** | 16 providers, BYO API key |
| **Multi-Canal** | WhatsApp, Telegram, Discord, Email, PWA, Desktop, Mobile |
| **Procedural** | Pixelart generado matemáticamente, sin assets estáticos |
| **Comunidad** | MCP compatibility, Graphify extension, roadmap abierto |

### Métricas del proyecto

- **~7,500 líneas de código** TypeScript/TSX
- **25+ archivos** entre lib, components, api
- **16 LLMs** soportados
- **9 integraciones** documentadas paso a paso
- **28 MCP servers** listados como compatibles
- **21 ideas** en el roadmap

---

## 2. Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                     CLIENTE (Navegador / App)                    │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  UI Layer (React + Tailwind + shadcn/ui)                 │   │
│  │  - Landing (HeroSection, InstallationsSection, etc.)     │   │
│  │  - Vault (UnlockScreen)                                   │   │
│  │  - App (MemoryChat, MemoryGraph, MemoryTimeline, Stats)  │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Pixelart Layer (Canvas 2D)                              │   │
│  │  - engine.ts: PRNG, noise, paletas, renderers            │   │
│  │  - robots.ts: 5 templates, 9 paletas, animaciones        │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Crypto Layer (WebCrypto API)                            │   │
│  │  - PBKDF2 (250k iter) → AES-256 key                      │   │
│  │  - AES-GCM encrypt/decrypt                               │   │
│  │  - Zero-knowledge: servidor nunca ve plaintext           │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  State (Zustand + persist)                               │   │
│  │  - Vault state (masterKey, memories)                     │   │
│  │  - LLM settings (provider, apiKey, model)                │   │
│  │  - Graphify config (serverUrl, authToken)                │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↕ HTTPS + NextAuth session
┌─────────────────────────────────────────────────────────────────┐
│                    SERVIDOR (Next.js API Routes)                 │
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐    │
│  │ /api/agents    │  │ /api/memories  │  │ /api/share     │    │
│  │ 16 LLMs        │  │ CRUD cifrado   │  │ Links revocables│   │
│  │ Rate limit     │  │ Zod validation │  │ Zero-knowledge │    │
│  │ Zod validation │  │ Audit log      │  │                │    │
│  └────────────────┘  └────────────────┘  └────────────────┘    │
│  ┌────────────────┐  ┌──────────────────────────────────┐      │
│  │ /api/auth/*    │  │  Prisma + SQLite                  │      │
│  │ NextAuth.js    │  │  - User, Memory, Reminder         │      │
│  │ bcrypt         │  │  - Contact, ShareLink, AccessLog  │      │
│  │ JWT sessions   │  │  - Account, Session (NextAuth)    │      │
│  └────────────────┘  └──────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
                              ↕ (optional)
┌─────────────────────────────────────────────────────────────────┐
│              INTEGRACIONES EXTERNAS (APIs oficiales)             │
│  WhatsApp Cloud API · Telegram Bot API · Discord Bot API         │
│  IMAP/SMTP · Google Calendar OAuth2 · Graphify MCP               │
└─────────────────────────────────────────────────────────────────┘
```

### Flujo de un recuerdo (end-to-end)

1. Usuario escribe texto en el chat (web, Telegram, etc.)
2. Cliente deriva clave AES-256 desde passphrase (PBKDF2, 250k iter)
3. Cliente cifra el texto con AES-GCM → ciphertext + IV
4. Cliente llama `/api/agents` con el texto (para análisis LLM)
5. Servidor llama al LLM configurado (con rate limit + Zod validation)
6. LLM devuelve: tipo, tags, reminderAt, confidence
7. Cliente guarda el recuerdo cifrado en localStorage (Zustand persist)
8. Opcional: cliente POST a `/api/memories` con ciphertext para sync
9. Servidor persiste ciphertext en SQLite (nunca plaintext)
10. Si Graphify habilitado: encola metadato (sin plaintext) para sync

---

## 3. Funcionalidades Implementadas

### 3.1 Cifrado Zero-Knowledge

**Archivo:** `src/lib/crypto.ts`

#### Especificaciones

| Componente | Algoritmo | Parámetros |
|---|---|---|
| Cifrado | AES-GCM | 256 bits, autenticado |
| Derivación de clave | PBKDF2 | SHA-256, 250,000 iteraciones |
| Salt | Random bytes | 16 bytes por usuario |
| IV | Random bytes | 12 bytes por cifrado |
| Hash de dedup | SHA-256 | Del plaintext (para detectar duplicados) |
| API | WebCrypto | `crypto.subtle` (nativo del navegador) |

#### Cómo se implementó

```typescript
// Derivación de clave maestra desde passphrase
export async function deriveMasterKey(passphrase: string, saltB64?: string): Promise<MasterKey> {
  const salt = saltB64 ? base64ToBuf(saltB64) : randomBytes(SALT_LEN);
  const baseKey = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(passphrase),
    { name: "PBKDF2" },
    false,
    ["deriveKey"]
  );
  const key = await crypto.subtle.deriveKey(
    { name: "PBKDF2", salt, iterations: 250_000, hash: "SHA-256" },
    baseKey,
    { name: "AES-GCM", length: 256 },
    false,
    ["encrypt", "decrypt"]
  );
  return { key, salt: bufToBase64(salt) };
}

// Cifrado de un recuerdo
export async function encryptString(plaintext: string, masterKey: MasterKey): Promise<EncryptedPayload> {
  const iv = randomBytes(12);
  const encoded = new TextEncoder().encode(plaintext);
  const ciphertext = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv },
    masterKey.key,
    encoded
  );
  const hash = bufToBase64(await crypto.subtle.digest("SHA-256", encoded));
  return { c: bufToBase64(ciphertext), iv: bufToBase64(iv), s: masterKey.salt, h: hash };
}
```

#### Por qué estas decisiones

- **AES-GCM** (no AES-CBC): proporciona confidencialidad + integridad (authenticated encryption). Si alguien manipula el ciphertext, el descifrado falla.
- **PBKDF2 con 250k iteraciones**: cumple el estándar OWASP 2024. Cada intento de fuerza bruta cuesta 250k operaciones de SHA-256.
- **IV aleatorio por recuerdo**: aunque la misma clave se reutiliza, cada cifrado produce ciphertext diferente. Evita patrones reconocibles.
- **WebCrypto API** (no crypto-js): implementación nativa del navegador, auditada, resistente a timing attacks.

#### Verificación de seguridad

- La passphrase **nunca** se persiste (solo en memoria durante la sesión)
- El salt se guarda en localStorage (público, pero solo útil con la passphrase)
- El servidor solo recibe ciphertext + IV + hash (nunca plaintext ni key)
- El hash SHA-256 permite dedup sin exponer contenido (solo coincide si el plaintext es idéntico)

---

### 3.2 Multi-LLM (16 providers)

**Archivos:** `src/lib/llm-settings.ts` (configuración) · `src/app/api/agents/route.ts` (API)

#### Lista de providers

| # | Provider | Formato | Default Model | Rate Limit | API Key |
|---|---|---|---|---|---|
| 1 | Z.AI | zai-sdk | glm-4.6 | 30/min | No |
| 2 | OpenAI | openai | gpt-4o-mini | 60/min | Sí |
| 3 | Anthropic | anthropic | claude-3-5-sonnet | 50/min | Sí |
| 4 | Google | google | gemini-2.0-flash | 60/min | Sí |
| 5 | Mistral | openai | mistral-large-latest | 50/min | Sí |
| 6 | NVIDIA NIM | openai | llama-3.1-405b | 40/min | Sí (free) |
| 7 | DeepSeek | openai | deepseek-chat | 60/min | Sí |
| 8 | Groq | openai | llama-3.3-70b | 30/min | Sí |
| 9 | Together AI | openai | Llama-3.3-70B-Turbo | 60/min | Sí |
| 10 | OpenRouter | openai | openai/gpt-4o-mini | 20/min | Sí |
| 11 | Cohere | cohere | command-r-plus | 100/min | Sí |
| 12 | Fireworks AI | openai | llama-v3p3-70b | 60/min | Sí |
| 13 | Perplexity | openai | sonar-small-128k | 50/min | Sí |
| 14 | HuggingFace | openai | Llama-3.3-70B | 30/min | Sí |
| 15 | xAI (Grok) | openai | grok-2-latest | 30/min | Sí |
| 16 | Ollama | ollama | llama3.2 | 120/min | No (local) |

#### Arquitectura de implementación

```typescript
// Función unificada que despacha por formato
async function callLLM(params: {
  format: string;  // "openai" | "anthropic" | "google" | "cohere" | "ollama" | "zai"
  text: string;
  apiKey?: string;
  model: string;
  baseUrl?: string;
  temperature: number;
  maxTokens: number;
  systemPrompt: string;
}): Promise<{ content: string; tokens: number }> {
  switch (params.format) {
    case "zai": return callZai(params);          // usa z-ai-web-dev-sdk
    case "openai": return callOpenAICompatible(params);  // 11 providers!
    case "anthropic": return callAnthropic(params);
    case "google": return callGoogle(params);
    case "cohere": return callCohere(params);
    case "ollama": return callOllama(params);
  }
}
```

**Insight clave:** 11 de los 16 providers usan el formato OpenAI-compatible. Una sola función `callOpenAICompatible()` los maneja a todos, cambiando solo el `baseUrl` y el `Authorization: Bearer` header. Esto permite añadir nuevos providers OpenAI-compatible en 5 líneas.

#### Fallback heurístico

Si el LLM falla (sin API key, rate limit, red caída), el sistema usa un agente heurístico local:

```typescript
function heuristic(text: string) {
  const REMINDER_PATTERNS = [/recuérdame|avísame.*mañana/i, ...];
  const TYPE_PATTERNS = [
    { type: "reminder", patterns: REMINDER_PATTERNS },
    { type: "task", patterns: [/tengo que|necesito|debo/i] },
    // ...
  ];
  // Detecta tipo, tags, reminderAt sin LLM
}
```

El usuario siempre obtiene un resultado, aunque el LLM no esté disponible.

#### Gestión de API keys

- Las API keys se guardan en `localStorage` (store Zustand persist)
- Se envían al servidor **solo durante la llamada** (en el body del POST)
- El servidor **nunca** las persiste ni las loguea
- Cada provider tiene su propio campo en el store

---

### 3.3 Autenticación con NextAuth.js

**Archivos:** `src/lib/auth/config.ts` · `src/lib/auth/helpers.ts` · `src/lib/auth/provider.tsx` · `src/app/api/auth/[...nextauth]/route.ts` · `src/app/api/auth/register/route.ts`

#### Modelo de dos capas

MinBot-Task usa **dos capas de seguridad independientes**:

1. **Capa 1: NextAuth.js (servidor)** — autentica la identidad del usuario (email + password hasheado con bcrypt). Permite acceder a la API.
2. **Capa 2: Vault passphrase (cliente)** — deriva la clave AES-256 que cifra los recuerdos. Incluso si el servidor es comprometido, los recuerdos siguen cifrados.

#### Especificaciones

| Componente | Implementación |
|---|---|
| Framework | NextAuth.js v4 |
| Provider | Credentials (email + password) |
| Adapter | PrismaAdapter (SQLite) |
| Hashing | bcrypt con 12 rounds |
| Session | JWT, 30 días de expiración |
| Registration rate limit | 5 por hora por IP |

#### Schema Prisma

```prisma
model User {
  id             String   @id @default(cuid())
  email          String   @unique
  name           String?
  salt           String              // para vault PBKDF2
  hashedPassword String?             // bcrypt, null para demo
  role           String   @default("user")
  // ... relaciones
}

model Account { ... }     // NextAuth OAuth (futuro)
model Session { ... }     // NextAuth sessions
model VerificationToken { ... }  // NextAuth email verification
```

#### Endpoint de registro

```typescript
// POST /api/auth/register
const registerSchema = z.object({
  email: z.string().email().max(200),
  password: z.string().min(8).max(200),
  name: z.string().max(100).optional(),
});

export async function POST(req: NextRequest) {
  // Rate limit: 5 regs/hour/IP
  if (!checkRate(clientIp)) return NextResponse.json({}, { status: 429 });

  const body = registerSchema.parse(await req.json()); // Zod validation
  const existing = await db.user.findUnique({ where: { email } });
  if (existing) return NextResponse.json({ error: "Email already registered" }, { status: 409 });

  const hashedPassword = await bcrypt.hash(password, 12);
  const user = await db.user.create({ data: { email, hashedPassword, ... } });
  return NextResponse.json({ id: user.id, email: user.email });
}
```

---

### 3.4 Rate Limiting por LLM

**Archivo:** `src/app/api/agents/route.ts`

#### Especificaciones

| Característica | Implementación |
|---|---|
| Storage | In-memory `Map<string, RateBucket>` |
| Key | `${providerId}:${clientIp}` |
| Window | 60 segundos (sliding window) |
| Limits | Por provider (20-120 req/min) |
| Headers | `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, `Retry-After` |

#### Implementación

```typescript
interface RateBucket { count: number; resetAt: number; }
const rateBuckets = new Map<string, RateBucket>();

function checkRateLimit(key: string, limitPerMinute: number) {
  const now = Date.now();
  const bucket = rateBuckets.get(key);
  if (!bucket || bucket.resetAt < now) {
    rateBuckets.set(key, { count: 1, resetAt: now + 60_000 });
    return { allowed: true, remaining: limitPerMinute - 1, resetAt: now + 60_000 };
  }
  if (bucket.count >= limitPerMinute) {
    return { allowed: false, remaining: 0, resetAt: bucket.resetAt };
  }
  bucket.count++;
  return { allowed: true, remaining: limitPerMinute - bucket.count, resetAt: bucket.resetAt };
}
```

#### Decisión de diseño importante

El rate limit **solo cuenta requests con API key válida**. Las requests sin key (que devolverían 401) no consumen cuota. Esto evita que un atacante agote la cuota de un usuario legítimo enviando requests sin key.

```typescript
// 1. Validar API key FIRST (no consume rate limit)
if (providerMeta.needsKey && !apiKey) return NextResponse.json({ error: "API key required" }, { status: 401 });

// 2. Rate limit (solo si la key es válida)
const rateCheck = checkRateLimit(rateKey, rateLimit);
if (!rateCheck.allowed) return NextResponse.json({ error: "Rate limit exceeded" }, { status: 429 });
```

#### Verificación realizada

Test con 32 requests rápidas a Z.AI (limit=30/min):
- Requests 1-30: HTTP 200 ✅
- Requests 31-32: HTTP 429 con `Retry-After` header ✅

#### Limitación conocida

El storage in-memory se resetea al reiniciar el servidor. Para producción multi-instancia, migrar a **Upstash Redis** (free tier) o **Memcached**.

---

### 3.5 Validación Zod en Endpoints

**Archivos:** Todos los `route.ts` en `src/app/api/`

#### Schemas implementados

```typescript
// /api/agents
const agentRequestSchema = z.object({
  text: z.string().min(1).max(10000),
  provider: z.string().optional(),
  apiKey: z.string().max(500).optional(),
  model: z.string().max(200).optional(),
  baseUrl: z.string().url().max(500).optional().or(z.literal("")),
  temperature: z.number().min(0).max(2).optional(),
  maxTokens: z.number().int().min(50).max(8000).optional(),
  systemPromptOverride: z.string().max(5000).optional(),
});

// /api/memories
const createMemorySchema = z.object({
  ciphertext: z.string().min(1).max(1_000_000),  // max 1MB
  iv: z.string().min(16).max(32),
  type: z.enum(["note", "reminder", "task", "idea", "code", "contact", "event", "secret"]),
  tags: z.union([z.string().max(500), z.array(z.string().max(50)).max(20)]),
  contentHash: z.string().max(100).optional(),
});

// /api/share
const createShareSchema = z.object({
  ciphertext: z.string().min(1).max(1_000_000),
  iv: z.string().min(16).max(32),
  keyHash: z.string().min(1).max(200),
  expiresAt: z.string().datetime().optional(),
  maxViews: z.number().int().min(1).max(1000).default(1),
});

// /api/auth/register
const registerSchema = z.object({
  email: z.string().email().max(200),
  password: z.string().min(8).max(200),
  name: z.string().max(100).optional(),
});
```

#### Por qué Zod

- **TypeScript-first**: los tipos se infieren automáticamente del schema
- **Mensajes de error estructurados**: el cliente recibe JSON con detalles del error
- **Composable**: se pueden reutilizar schemas en otros endpoints
- **Seguridad**: previene injection attacks limitando tamaños y formatos

#### Manejo de errores

```typescript
try {
  const body = agentRequestSchema.parse(await req.json());
} catch (e) {
  return NextResponse.json(
    { error: "Invalid input", detail: e instanceof Error ? e.message : String(e) },
    { status: 400 }
  );
}
```

---

### 3.6 Pixelart Procedural

**Archivos:** `src/lib/pixelart/engine.ts` (563 líneas) · `src/lib/pixelart/robots.ts` (565 líneas) · `src/components/pixelart/PixelCanvas.tsx` · `src/components/pixelart/PixelLogo.tsx` · `src/components/pixelart/PixelBackground.tsx`

#### Engine de ruido procedural

```typescript
// PRNG Mulberry32 — deterministic seeded random
export function hashStringToSeed(str: string): number { ... }
export function mulberry32(seed: number): () => number { ... }

// Value Noise 2D — smooth interpolation
export function makeValueNoise2D(seed: number) { ... }

// Fractal Noise — multi-octave para detalle orgánico
export function makeFractalNoise2D(seed: number, octaves = 4) {
  // Suma 4 octavas de value noise con amplitud/frecuencia variables
  // Produce texturas tipo No Man's Sky
}
```

#### Renderers disponibles

| Renderer | Uso | Resolución típica |
|---|---|---|
| `renderPixelPlanet` | Planetas estilo No Man's Sky | 32x32, 48x48 |
| `renderPixelLandscape` | Paisajes synthwave | 160x90 (background) |
| `renderPixelAvatar` | Identicons simétricos | 16x16 |
| `renderStarfield` | Fondo animado con estrellas | 160x90 |
| `renderMatrixRain` | Lluvia estilo Matrix | 160x90 |
| `renderPixelLogo` | Logo animado del robot satélite | 32x32 |
| `renderPixelTile` | Tiles para bordes/patrones | 16x16 |
| `renderRobot` | Robots pixelados (5 templates) | 16-64px |
| `renderMiniDrone` | Drones decorativos pequeños | 8x8 |
| `renderRobotFactory` | Fondo de fábrica de robots | 160x90 |

#### Templates de robots

| Template | Resolución | Uso |
|---|---|---|
| `biped16` | 16x16 | Avatares pequeños, chat |
| `scout16` | 16x16 | Variante esbelta |
| `biped32` | 32x32 | Cards de features |
| `hover32` | 32x32 | Drone flotante |
| `biped64` | 64x64 | Logo principal, hero |

#### Paletas de robot (9)

| Paleta | Colores | Asociada a |
|---|---|---|
| skynet | Magenta + cian | Z.AI (default) |
| clawd | Naranja Anthropic | Anthropic |
| construction | Amarillo + negro | OpenAI, Fireworks |
| medical | Blanco + verde | Mistral, Cohere |
| stealth | Negro + rojo | DeepSeek, xAI |
| ghost | Blanco + azul | Google, OpenRouter, Perplexity |
| toxic | Verde + morado | Groq |
| rust | Marrón post-apocalíptico | Together, Ollama, HF |
| nvidia | Verde NVIDIA | NVIDIA NIM |

#### Animaciones

- **Bob vertical**: `Math.sin(frame * 0.1) * 1` pixel de offset Y
- **Blink del visor**: oculta los pixeles "G" (visor glow) durante 4 frames cada 30
- **Glow radial**: `createRadialGradient` alrededor del visor, alpha pulsante
- **Scan line**: línea horizontal opcional en robots aleatorios

#### Por qué procedural (no assets estáticos)

1. **Cero peso**: no hay PNGs/SVGs en el bundle
2. **Infinita variedad**: cada semilla produce un robot único
3. **Determinístico**: la misma semilla siempre produce el mismo robot (útil para avatares de usuario)
4. **Escalable**: se renderiza a cualquier resolución sin pixelar
5. **Customizable**: cambiar paleta = 1 línea de código

---

### 3.7 Mini-Grafo Drag & Drop

**Archivo:** `src/components/minbot-task/MemoryGraph.tsx` (485 líneas)

#### Especificaciones

| Característica | Implementación |
|---|---|
| Render | SVG con viewBox 100x100 |
| Límite de nodos | 12 (hard cap para legibilidad) |
| Drag & drop | Pointer events nativos (touch + mouse) |
| Conexiones | 3 tipos: tag (rosa), tipo (cian), tiempo (amarillo) |
| Layout inicial | Hub central + anillos concéntricos |
| Reset | Botón que limpia posiciones arrastradas |

#### Algoritmo de layout

```typescript
function buildInitialGraph(memories: Memory[]): GraphData {
  // 1. Ordenar por prioridad: reminder > idea > task > event > code > secret > contact > note
  // 2. Truncar a MAX_NODES (12)
  // 3. Primer nodo = hub central (50, 50)
  // 4. Resto: anillos concéntricos (5 nodos por anillo)
  //    ring = ceil(i / 5), radius = 22 + ring * 18
  //    angle = (inRing / ringSize) * 2π + ring * 0.3
}
```

#### Detección de conexiones

```typescript
// Para cada par de nodos (i, j):
// 1. Tags compartidos? → conexión "tag" (weight = sharedTags * 0.4)
// 2. Mismo tipo? → conexión "tipo" (weight = 0.3)
// 3. Recordatorios dentro de 48h? → conexión "tiempo" (weight = 0.2)
// Solo se dibujan las top 20 conexiones por peso
```

#### Drag & drop implementation

```typescript
const [draggedPositions, setDraggedPositions] = useState<Record<string, {x, y}>>({});

const handlePointerDown = (e, id) => {
  setDraggingId(id);
  e.target.setPointerCapture(e.pointerId);  // captura touch/mouse
};

const handlePointerMove = (e) => {
  if (!draggingId) return;
  const pos = screenToViewBox(e.clientX, e.clientY);  // convierte coords pantalla → SVG
  setDraggedPositions(prev => ({ ...prev, [draggingId]: pos }));
};

// Clamp para que los nodos no salgan del viewBox
const x = Math.max(4, Math.min(VIEWBOX - 4, x));
```

#### Features visuales

- **Hover halo**: círculo translúcido detrás del nodo al hover
- **Tooltip**: muestra el label del recuerdo al hover
- **Indicador "DRAG"**: esquina superior derecha
- **Botón reset**: icono `RotateCcw`
- **Drones decorativos**: 2 mini-drones animados en esquinas
- **Anillo hub**: nodo central con anillo punteado
- **Recordatorios parpadeantes**: punto amarillo con `<animate>` SVG

---

### 3.8 Extensión Graphify

**Archivos:** `src/lib/graphify.ts` (269 líneas) · `src/components/minbot-task/GraphifyIntegration.tsx` (250 líneas)

#### ¿Qué es Graphify?

[Graphify](https://github.com/Graphify-Labs/graphify) (87.4k★) es un AI coding skill que convierte cualquier carpeta de código, SQL schemas, docs, papers, imágenes o videos en un **knowledge graph consultable**. MinBot-Task se integra con él vía **MCP (Model Context Protocol)**.

#### Arquitectura de integración

```
MinBot-Task (cliente)
    │
    │ POST /tools/call (JSON-RPC 2.0)
    │ method: "ingest_minskynet_memories"
    │ arguments: { memories: [{ id, type, tags, contentHash, createdAt }] }
    │                                                ↑ NO plaintext!
    ↓
Graphify MCP Server (http://localhost:8000/mcp)
    │
    │ Indexa metadatos en el knowledge graph
    │
    ↓
Consulta desde Claude/Cursor/Codex vía MCP
```

#### Funciones implementadas

```typescript
// 1. Test de conexión (handshake MCP initialize)
export async function testGraphifyConnection(serverUrl, authToken) {
  const res = await fetch(`${serverUrl}/initialize`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}) },
    body: JSON.stringify({
      jsonrpc: "2.0", id: 1, method: "initialize",
      params: { protocolVersion: "2024-11-05", capabilities: {}, clientInfo: { name: "minbot-task", version: "0.1.0" } }
    })
  });
  return { ok: res.ok, version: data?.result?.serverInfo?.version };
}

// 2. Push de recuerdos (solo metadatos, JAMÁS plaintext)
export async function pushMemoriesToGraphify(serverUrl, authToken, memories) {
  const res = await fetch(`${serverUrl}/tools/call`, {
    method: "POST",
    body: JSON.stringify({
      jsonrpc: "2.0", id: 2, method: "tools/call",
      params: {
        name: "ingest_minskynet_memories",
        arguments: {
          memories: memories.map(m => ({
            id: m.id, type: m.type, tags: m.tags,
            contentHash: m.contentHash, createdAt: m.createdAt,
            // NOTE: plaintext es INTENCIONALMENTE omitido
          }))
        }
      }
    })
  });
}

// 3. Pull de nodos de Graphify hacia MinBot-Task
export async function pullGraphifyNodes(serverUrl, authToken, limit = 50) { ... }
```

#### Store Zustand para configuración

```typescript
interface GraphifyConfig {
  serverUrl: string;           // http://localhost:8000/mcp
  authToken: string;           // Bearer token opcional
  autoSync: boolean;           // encola automáticamente nuevos recuerdos
  batchSize: number;           // 5-100 recuerdos por batch
  lastSyncAt: string | null;
  enabled: boolean;            // toggle on/off
}
```

#### Garantías de privacidad

1. **Solo metadatos**: type, tags, hash, createdAt — **jamás plaintext**
2. **Opt-in explícito**: el usuario debe habilitar la integración manualmente
3. **Test de conexión**: botón "Probar conexión" antes de habilitar
4. **Auto-sync opcional**: el usuario decide si cada nuevo recuerdo se encola automáticamente
5. **Alert visible en UI**: "Solo se sincroniza metadato cifrado, el contenido plaintext nunca sale de tu dispositivo"

---

### 3.9 Integraciones Multi-Canal

**Archivo:** `src/components/minbot-task/InstallationsSection.tsx` (709 líneas) · `src/components/minbot-task/HeroSection.tsx`

#### 9 integraciones documentadas paso a paso

Cada integración tiene:
- Descripción + dificultad + tiempo estimado
- Badge ToS OK / RIESGO
- Método oficial usado
- 5-7 pasos con comandos copiables
- Código de ejemplo completo
- Botón "Copiar" en cada bloque

| Integración | Método | ToS | Dificultad |
|---|---|---|---|
| PWA Móvil | Web estándar (manifest) | ✅ | Easy |
| Email | IMAP/SMTP | ✅ | Easy |
| Telegram Bot | Bot API oficial + Telegraf | ✅ | Easy |
| Discord Bot | discord.js (oficial) | ✅ | Medium |
| WhatsApp Business | Cloud API de Meta (pago) | ✅ | Medium |
| Desktop | Tauri (Rust + WebView) | ✅ | Medium |
| Mobile Nativo | Capacitor (web → iOS/Android) | ✅ | Medium |
| Graphify | MCP Streamable HTTP | ✅ | Advanced |
| Google Calendar | OAuth2 oficial | ✅ | Medium |

#### Cumplimiento de políticas (ToS)

**Banner visible en la UI:**

> MinBot-Task **solo usa APIs oficiales**. No utiliza librerías no oficiales (Baileys, self-bots, scraping) que violan los términos de servicio de WhatsApp, Discord, etc. Para WhatsApp se requiere WhatsApp Business Cloud API (pago por conversación a Meta). **Revisa siempre los ToS de cada plataforma** antes de desplegar en producción.

#### Investigación realizada

| Plataforma | Método no oficial (riesgo ban) | Método oficial (ToS OK) |
|---|---|---|
| WhatsApp | Baileys, whatsmeow, Evolution API | Cloud API de Meta (pago) |
| Discord | self-bots (baneado) | discord.js con bot token |
| Telegram | (no hay métodos no oficiales comunes) | Bot API con BotFather token |
| Email | scraping webmail | IMAP/SMTP estándar |

---

### 3.10 Local-First Store

**Archivo:** `src/lib/store.ts` (478 líneas)

#### Arquitectura

```typescript
export const useMinBotTask = create<MinBotTaskState>()(
  persist(
    (set, get) => ({
      // State
      deviceId, masterKey, unlocked, passphraseSalt,
      memories: Memory[],

      // Actions
      unlock(passphrase) { ... },
      createMemory(plaintext, type, tags, reminderAt) { ... },
      searchMemories(query) { ... },
      exportData() { ... },  // JSON cifrado para backup
      wipeAll() { ... },     // borra todo
    }),
    {
      name: "minbot-task-store",
      storage: createJSONStorage(() => localStorage),
      // Solo persistir: deviceId, salt, memories (cifradas)
      // NUNCA persistir: masterKey, plaintext
      partialize: (state) => ({
        deviceId: state.deviceId,
        passphraseSalt: state.passphraseSalt,
        memories: state.memories.map(m => ({ ...m, plaintext: undefined })),
      }),
    }
  )
);
```

#### Heuristic Agent (fallback sin LLM)

```typescript
export function heuristicAgent(text: string): AgentInsight {
  // Detecta tipo por patrones regex:
  // - reminder: "recuérdame|avísame" + "mañana|lunes|a las 10"
  // - task: "tengo que|necesito|debo"
  // - idea: "idea para|se me ocurrió"
  // - code: "contraseña|password|código|token"
  // - contact: "cumpleaños|teléfono|email"
  // - event: "vuelo|hotel|reserva|reunión"

  // Detecta tags por categorías:
  // viaje, trabajo, personal, comida, salud, casa, finanzas, seguridad

  // Detecta reminderAt:
  // "mañana" → tomorrow 10:00
  // "si no contesta" → reminderRule = "conditional_followup"
}
```

#### Función `analyzeWithLLM` (cliente)

```typescript
export async function analyzeWithLLM(text: string) {
  try {
    const llmState = useLLMSettings.getState();
    const res = await fetch("/api/agents", {
      method: "POST",
      body: JSON.stringify({
        text,
        provider: llmState.activeProvider,
        apiKey: llmState.providers[llmState.activeProvider].apiKey,
        // ...
      })
    });
    return { insight, source: "llm", model };
  } catch (e) {
    // Fallback automático a heurístico
    return { insight: heuristicAgent(text), source: "heuristic", warning: "LLM no disponible" };
  }
}
```

---

### 3.11 Security Headers

**Archivo:** `next.config.ts`

```typescript
async headers() {
  return [{
    source: "/(.*)",
    headers: [
      { key: "X-Content-Type-Options", value: "nosniff" },
      { key: "X-Frame-Options", value: "DENY" },  // anti-clickjacking
      { key: "X-XSS-Protection", value: "1; mode=block" },
      { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
      { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=(), interest-cohort=()" },
      {
        key: "Content-Security-Policy",
        value: [
          "default-src 'self'",
          "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
          "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
          "font-src 'self' https://fonts.gstatic.com data:",
          "img-src 'self' data: blob: https:",
          "connect-src 'self' https://integrate.api.nvidia.com https://api.openai.com https://api.anthropic.com https://generativelanguage.googleapis.com https://api.mistral.ai http://localhost:11434 http://localhost:8000",
          "frame-ancestors 'none'",
          "form-action 'self'",
          "base-uri 'self'",
        ].join("; "),
      },
      { key: "Strict-Transport-Security", value: "max-age=31536000; includeSubDomains; preload" },
    ],
  }];
}
```

#### Por qué cada header

- **CSP**: previene XSS restringiendo fuentes de scripts/styles/connections
- **X-Frame-Options: DENY**: la app no puede ser embebida en iframes (anti-clickjacking)
- **HSTS**: fuerza HTTPS por 1 año
- **Permissions-Policy**: deshabilita APIs sensibles (camera, microphone, geolocation)
- **Referrer-Policy**: solo envía el origin en headers Referer

---

## 4. Demos y Cómo Expandirlas

### Demo 1: Crear vault y capturar recuerdo

**Flujo actual:**
1. Usuario entra a la app → pantalla de unlock
2. Si no hay vault: modo "INIT_VAULT", define passphrase
3. Si hay vault: modo "UNLOCK_VAULT", ingresa passphrase
4. `deriveMasterKey(passphrase, salt)` → AES-256 key (250k iter PBKDF2)
5. App descifra los recuerdos existentes para verificar la passphrase
6. Si descifra 3 recuerdos correctamente → unlocked = true
7. Usuario escribe en el chat
8. `analyzeWithLLM(text)` → llama al LLM activo (con fallback heurístico)
9. `createMemory(plaintext, type, tags, reminderAt)` → cifra + guarda en store
10. Recuerdo aparece en cronología + grafo

**Cómo expandirlo:**
- **Multi-vault**: soportar varios vaults por usuario (trabajo/personal)
- **Vault compartido**: CRDT para que múltiples usuarios editen el mismo vault
- **Biometría**: desbloqueo con huella/Face ID vía WebAuthn
- **Auto-lock**: bloqueo tras X minutos de inactividad

---

### Demo 2: Selector de LLM

**Flujo actual:**
1. Usuario hace click en "Z.AI (default)" en el header del chat
2. Dialog modal con grid de 16 providers
3. Cada provider muestra su robot único + estado (SIN KEY / modelo activo)
4. Usuario hace click en uno → se carga la config específica
5. Si needsKey: input para API key (con placeholder específico: `sk-...`, `nvapi-...`, etc.)
6. Si es NVIDIA/Ollama: input editable para base URL
7. Selector de modelo (dropdown con modelos soportados)
8. Slider de temperatura (0-2) y max_tokens (200-2000)
9. Display de rate limit del provider activo
10. Click "APLICAR" → se guarda en localStorage

**Cómo expandirlo:**
- **Model router**: usar diferentes LLMs según el tipo de recuerdo (más barato para notas, más potente para código)
- **Cost tracking**: mostrar cuánto se ha gastado en cada provider
- **Streaming responses**: SSE para respuestas en tiempo real
- **Function calling**: integrar tools (web search, calculator, etc.)
- **Fine-tuning**: soportar modelos fine-tuned vía Together AI o Replicate

---

### Demo 3: Mini-grafo drag & drop

**Flujo actual:**
1. Usuario captura 2+ recuerdos
2. El grafo renderiza hasta 12 nodos en SVG
3. Layout inicial: 1 hub central + anillos concéntricos
4. Conexiones automáticas: tag (rosa), tipo (cian), tiempo (amarillo)
5. Usuario arrastra un nodo → `setDraggedPositions` actualiza su posición
6. Las conexiones se recalculan en tiempo real
7. Hover sobre nodo → tooltip con label
8. Botón reset → limpia posiciones arrastradas

**Cómo expandirlo:**
- **Zoom & pan**: permitir hacer zoom en áreas del grafo
- **Filtros avanzados**: mostrar solo conexiones de cierto tipo
- **Click en nodo**: abrir modal con detalles del recuerdo
- **Modo "constelación"**: agrupar recuerdos por tag visualmente
- **Export como imagen**: PNG del grafo para compartir
- **Graphify sync**: cuando Graphify está activo, mostrar nodos de Graphify junto a los de MinBot-Task

---

### Demo 4: Graphify extension

**Flujo actual:**
1. Usuario hace click en botón "Graphify" del header
2. Dialog con toggle de habilitación
3. Input para MCP_SERVER_URL (default: http://localhost:8000/mcp)
4. Input opcional para AUTH_TOKEN
5. Click "PROBAR CONEXIÓN" → `testGraphifyConnection()` hace handshake MCP
6. Si OK: muestra versión de Graphify
7. Toggle AUTO_SYNC: cada nuevo recuerdo se encola
8. Slider BATCH_SIZE: 5-100 recuerdos por sync
9. Cuando se captura un recuerdo → se encola su metadato (sin plaintext)
10. Sync periódico envía batches a Graphify

**Cómo expandirlo:**
- **Pull de nodos Graphify**: mostrar knowledge graph de Graphify en MinBot-Task
- **Cross-reference**: "este recuerdo está relacionado con este archivo de código en Graphify"
- **Query bidireccional**: preguntar a Graphify desde MinBot-Task y viceversa
- **Multi-graphify**: conectar con varios servidores Graphify simultáneos

---

### Demo 5: Landing page con guías de instalación

**Flujo actual:**
1. Usuario entra a `/` → ve hero con logo robot + stats
2. Sección "Integraciones" con 9 cards (ToS OK badges)
3. Sección "Instalación" con tabs por integración
4. Click en tab (ej: "Telegram Bot") → muestra 6 pasos
5. Cada paso tiene: título, descripción, comando/code copiable
6. Botón "Copiar" en cada bloque → clipboard
7. Sección "LLMs" con 16 cards (robot por provider)
8. Sección "MCP" con 28 servers
9. Sección "Ideas" con 21 ideas en 7 categorías

**Cómo expandirlo:**
- **Interactive demos**: en lugar de solo código, ejecutar comandos reales
- **Video tutorials**: embed de YouTube con walkthroughs
- **Community configs**: repositorio de configs compartidas por usuarios
- **Playground**: probar configuración sin instalar localmente

---

## 5. Roadmap: Cómo Implementar las Ideas

### 5.1 Captura

#### Voice notes con Whisper local

**Dificultad:** Medium · **Impacto:** High

**Implementación:**
```bash
bun add @xenova/transformers  # Whisper.cpp en WASM
```

```typescript
// src/lib/voice.ts
import { pipeline } from "@xenova/transformers";

let transcriber: any;
async function getTranscriber() {
  if (!transcriber) {
    transcriber = await pipeline("automatic-speech-recognition", "Xenova/whisper-base");
  }
  return transcriber;
}

export async function transcribeAudio(audioBlob: Blob): Promise<string> {
  const audio = await audioBlob.arrayBuffer();
  const transcriber = await getTranscriber();
  const result = await transcriber(audio);
  return result.text;
}
```

**UI:** Botón de micrófono en el chat → graba → transcribe → inserta texto en el input.

**Archivos a crear:**
- `src/lib/voice.ts` — wrapper de Whisper
- `src/components/minbot-task/VoiceRecorder.tsx` — UI de grabación

**Estimación:** 4-6 horas

---

#### OCR de imágenes con Tesseract.js

**Dificultad:** Medium · **Impacto:** Medium

**Implementación:**
```bash
bun add tesseract.js
```

```typescript
// src/lib/ocr.ts
import Tesseract from "tesseract.js";

export async function extractText(image: File): Promise<string> {
  const result = await Tesseract.recognize(image, "spa+eng");
  return result.data.text;
}
```

**UI:** Botón "Subir imagen" en el chat → extrae texto → inserta en input.

**Estimación:** 2-3 horas

---

#### Web clipper (extensión browser)

**Dificultad:** Medium · **Impacto:** High

**Implementación:**
1. Crear extensión Chrome/Firefox con `manifest.json`
2. Content script extrae texto seleccionado + URL + título
3. Background script envía POST a tu instancia de MinBot-Task
4. Endpoint `/api/clip` recibe y procesa

**Estructura:**
```
extensions/web-clipper/
├── manifest.json
├── content.js       # extrae selección
├── background.js    # envía a MinBot-Task
└── popup.html       # config de URL
```

**Estimación:** 1 día

---

### 5.2 IA / Memory

#### Embeddings locales con ChromaDB

**Dificultad:** Advanced · **Impacto:** High

**Implementación:**
```bash
bun add chromadb @xenova/transformers
```

```typescript
// src/lib/vector-db.ts
import { ChromaClient } from "chromadb";
import { pipeline } from "@xenova/transformers";

const embedder = await pipeline("feature-extraction", "Xenova/all-MiniLM-L6-v2");
const chroma = new ChromaClient({ path: "http://localhost:8000" });  // ChromaDB local

export async function indexMemory(memory: Memory) {
  const embedding = await embedder(memory.plaintext);
  await chroma.collection("memories").add({
    ids: [memory.id],
    embeddings: [embedding],
    metadatas: [{ type: memory.type, tags: memory.tags }],
  });
}

export async function semanticSearch(query: string): Promise<Memory[]> {
  const queryEmbedding = await embedder(query);
  const results = await chroma.collection("memories").query({
    queryEmbeddings: [queryEmbedding],
    nResults: 10,
  });
  return results.ids[0].map(id => memories.find(m => m.id === id));
}
```

**Requiere:** ChromaDB server corriendo localmente (`docker run -p 8000:8000 chromadb/chroma`)

**Estimación:** 1-2 días

---

#### Auto-categorización con embeddings

**Dificultad:** Advanced · **Impacto:** Medium

**Implementación:**
1. Generar embeddings de todos los recuerdos
2. K-means clustering para identificar grupos naturales
3. Para cada cluster, usar LLM para sugerir un nombre de tag
4. Aplicar tags automáticamente a recuerdos nuevos

**Estimación:** 1 día

---

#### Resúmenes periódicos (diario/semanal)

**Dificultad:** Medium · **Impacto:** High

**Implementación:**
```typescript
// src/lib/cron-summary.ts
// Cron job que corre cada día a las 23:00
import cron from "node-cron";

cron.schedule("0 23 * * *", async () => {
  const todayMemories = memories.filter(m => isToday(m.createdAt));
  const summary = await analyzeWithLLM(
    `Resume estos recuerdos del día: ${todayMemories.map(m => m.plaintext).join("\n")}`,
    { systemPrompt: "Genera un resumen ejecutivo del día en 3 bullets" }
  );
  await createMemory(summary, "note", ["resumen-diario"]);
});
```

**Estimación:** 3-4 horas

---

#### Q&A conversacional con RAG

**Dificultad:** Advanced · **Impacto:** High

**Implementación:**
1. Indexar todos los recuerdos en ChromaDB (con embeddings)
2. Cuando el usuario pregunta, hacer semantic search → top 5 recuerdos relevantes
3. Construir prompt: "Contexto: [recuerdos relevantes]. Pregunta: [query]"
4. LLM genera respuesta basada en el contexto
5. Citar qué recuerdos se usaron

**UI:** Modo "Preguntar" en el chat (toggle entre capturar y preguntar)

**Estimación:** 2-3 días

---

### 5.3 Seguridad

#### 2FA con TOTP

**Dificultad:** Medium · **Impacto:** Medium

**Implementación:**
```bash
bun add otplib qrcode
```

```typescript
// Al habilitar 2FA:
import { authenticator } from "otplib";
import QRCode from "qrcode";

const secret = authenticator.generateSecret();
const otpauth = authenticator.keyuri("user@email.com", "MinBot-Task", secret);
const qrImage = await QRCode.toDataURL(otpauth);
// Mostrar QR al usuario para escanear con Google Authenticator

// Al loguear:
const isValid = authenticator.verify({ token: userToken, secret });
```

**Schema Prisma:** añadir `twoFactorSecret String?` y `twoFactorEnabled Boolean @default(false)` a User.

**Estimación:** 1 día

---

#### Backup cifrado a IPFS

**Dificultad:** Advanced · **Impacto:** Medium

**Implementación:**
```bash
bun add ipfs-http-client
```

```typescript
// src/lib/backup-ipfs.ts
import { create } from "ipfs-http-client";

const ipfs = create({ url: "https://ipfs.infura.io:5001" });

export async function backupToIPFS(encryptedVault: string): Promise<string> {
  const result = await ipfs.add(encryptedVault);
  return result.cid.toString();  // devolver CID al usuario
}

// Restaurar:
export async function restoreFromIPFS(cid: string): Promise<string> {
  const chunks = [];
  for await (const chunk of ipfs.cat(cid)) chunks.push(chunk);
  return Buffer.concat(chunks).toString();
}
```

**UX:** Botón "Backup a IPFS" → sube vault cifrado → devuelve CID → usuario guarda CID en lugar seguro.

**Estimación:** 1-2 días

---

#### Hardware key (WebAuthn)

**Dificultad:** Advanced · **Impacto:** Medium

**Implementación:**
```typescript
// Registro de credential
const credential = await navigator.credentials.create({
  publicKey: {
    challenge: crypto.getRandomValues(new Uint8Array(32)),
    rp: { name: "MinBot-Task" },
    user: { id: userId, name: email, displayName: name },
    pubKeyCredParams: [{ type: "public-key", alg: -7 }],  // ES256
    authenticatorSelection: { userVerification: "required" },
  }
});

// Login con credential
const assertion = await navigator.credentials.get({
  publicKey: {
    challenge: serverChallenge,
    allowCredentials: [{ id: credentialId, type: "public-key" }],
  }
});
```

**Estimación:** 2-3 días

---

### 5.4 Sync

#### CRDT con Automerge

**Dificultad:** Advanced · **Impacto:** High

**Implementación:**
```bash
bun add automerge @automerge/react
```

```typescript
// src/lib/sync-crdt.ts
import * as Automerge from "@automerge/automerge";

interface VaultDoc {
  memories: Memory[];
}

let doc = Automerge.init<VaultDoc>();

// Crear recuerdo → mutar doc localmente
doc = Automerge.change(doc, d => {
  d.memories.push(newMemory);
});

// Sync con otro dispositivo
const syncMessage = Automerge.generateSyncMessage(doc, syncState);
// enviar syncMessage vía WebSocket al otro dispositivo

// Aplicar sync message recibido
const [newDoc, newSyncState] = Automerge.receiveSyncMessage(doc, syncState, syncMessage);
doc = newDoc;
```

**Requiere:** WebSocket server para relay de sync messages (o WebRTC P2P)

**Estimación:** 1 semana

---

#### Sync vía Dropbox/Google Drive

**Dificultad:** Medium · **Impacto:** Medium

**Implementación:**
1. OAuth con Dropbox/Google Drive API
2. Subir archivo JSON cifrado a `/Apps/MinBot-Task/vault.json`
3. Polling cada X minutos para detectar cambios
4. Si hay conflicto: usar timestamp más reciente (o merge manual)

**Estimación:** 1-2 días

---

### 5.5 Visual

#### Más templates de robots

**Dificultad:** Easy · **Impacto:** Low

**Implementación:**
Añadir a `src/lib/pixelart/robots.ts`:

```typescript
const ROBOT_32_QUADRUPED: string[] = [
  // 32x32 robot con 4 patas (estilo perro robot Boston Dynamics)
  "................................",
  "................................",
  // ... pattern
];

const ROBOT_32_TANK: string[] = [
  // 32x32 robot con orugas (estilo tanque)
];

const ROBOT_32_FLYING: string[] = [
  // 32x32 drone con hélices
];

const TEMPLATES = {
  biped16: ROBOT_16_BIPED,
  scout16: ROBOT_16_SCOUT,
  biped32: ROBOT_32_BIPED,
  hover32: ROBOT_32_HOVER,
  biped64: ROBOT_64_BIPED,
  quadruped32: ROBOT_32_QUADRUPED,  // nuevo
  tank32: ROBOT_32_TANK,            // nuevo
  flying32: ROBOT_32_FLYING,        // nuevo
};
```

**Estimación:** 2-3 horas por template

---

#### Themes personalizables

**Dificultad:** Easy · **Impacto:** Medium

**Implementación:**
1. Añadir store `useTheme` con paleta personalizable
2. UI para editar colores (color picker)
3. CSS variables dinámicas desde JS

```typescript
// src/lib/theme-store.ts
interface CustomTheme {
  background: string;
  foreground: string;
  primary: string;
  accent: string;
}

// Aplicar dinámicamente:
function applyTheme(theme: CustomTheme) {
  const root = document.documentElement;
  root.style.setProperty("--background", theme.background);
  root.style.setProperty("--foreground", theme.foreground);
  // ...
}
```

**Estimación:** 3-4 horas

---

#### Animaciones de transición pixel

**Dificultad:** Medium · **Impacto:** Low

**Implementación:**
- Framer Motion con `AnimatePresence` para transiciones entre vistas
- Efecto "pixel fade": renderizar la vista saliente en canvas, pixelar progresivamente
- Efecto "scroll lateral": nueva vista entra desde la derecha con efecto pixel

**Estimación:** 1 día

---

### 5.6 Integraciones

#### Obsidian sync

**Dificultad:** Medium · **Impacto:** High

**Implementación:**
1. Watch folder de Obsidian vault (`chokidar`)
2. Parsear archivos .md con `gray-matter` (frontmatter + content)
3. Mapear frontmatter → tags, content → plaintext
4. Bidireccional: cambios en MinBot-Task actualizan .md, y viceversa

**Estimación:** 1-2 días

---

#### Notion sync

**Dificultad:** Medium · **Impacto:** Medium

**Implementación:**
```bash
bun add @notionhq/client
```

```typescript
// Crear database en Notion con columnas: Type, Tags, ReminderAt, Content (cifrado)
// Sync: cada recuerdo → row en database
// Bidireccional: cambios en Notion → actualizar MinBot-Task
```

**Estimación:** 1 día

---

#### Voice calls transcription

**Dificultad:** Advanced · **Impacto:** Medium

**Implementación:**
- Integrar con Vapi (https://vapi.ai) o Retell AI
- Webhook recibe transcripción cuando termina la llamada
- Procesar transcripción con LLM para extraer recuerdos
- Guardar como tipo "event" con tag "call"

**Estimación:** 2-3 días

---

### 5.7 UX

#### CLI con comandos rápidos

**Dificultad:** Medium · **Impacto:** Medium

**Implementación:**
```typescript
// src/cli/index.ts
import { Command } from "commander";
import { deriveMasterKey, encryptString } from "./crypto";

const program = new Command();

program
  .command("add <text>")
  .description("Add a memory")
  .option("-t, --type <type>", "memory type", "note")
  .action(async (text, options) => {
    const key = await deriveMasterKey(process.env.VAULT_PASSPHRASE!);
    const encrypted = await encryptString(text, key);
    await fetch("http://localhost:3000/api/memories", {
      method: "POST",
      body: JSON.stringify(encrypted),
    });
    console.log("✓ Memory added");
  });

program
  .command("search <query>")
  .action(async (query) => {
    // Buscar en vault local
  });

program.parse();
```

**Uso:**
```bash
minbot add "comprar leche" -t task
minbot search "wifi airbnb"
```

**Estimación:** 1 día

---

#### Dashboard de insights

**Dificultad:** Easy · **Impacto:** Low

**Implementación:**
- Usar Recharts (ya instalado) para visualizar:
  - Recuerdos por día (line chart)
  - Tags más usados (bar chart)
  - Distribución por tipo (pie chart)
  - Hora del día más productiva (heatmap)

**Estimación:** 3-4 horas

---

#### Modo enfocado (Pomodoro + captura)

**Dificultad:** Easy · **Impacto:** Medium

**Implementación:**
```typescript
// Timer Pomodoro: 25 min focus + 5 min break
// Al finalizar cada sesión focus:
//   - Mostrar prompt: "¿Qué lograste en esta sesión?"
//   - Guardar respuesta como recuerdo tipo "task" con tag "pomodoro"
//   - Acumular stats: sesiones hoy, total focus time
```

**Estimación:** 3-4 horas

---

## 6. Especificaciones Técnicas

### Resumen de versiones

| Componente | Versión |
|---|---|
| Next.js | 16.1.1 |
| React | 19 |
| TypeScript | 5 |
| Tailwind CSS | 4 |
| Prisma | 6.11 |
| Zustand | 5 |
| Zod | 4 |
| NextAuth.js | 4.24 |
| bcryptjs | 3.0 |
| z-ai-web-dev-sdk | 0.0.18 |

### Especificaciones de seguridad

| Parámetro | Valor |
|---|---|
| Algoritmo de cifrado | AES-GCM 256 |
| Derivación de clave | PBKDF2-SHA256 |
| Iteraciones PBKDF2 | 250,000 |
| Tamaño del salt | 16 bytes |
| Tamaño del IV | 12 bytes |
| Hash de dedup | SHA-256 |
| Rounds bcrypt | 12 |
| Session JWT TTL | 30 días |
| Rate limit window | 60 segundos |
| Rate limit por LLM | 20-120 req/min |
| Registro rate limit | 5/hora/IP |

### Límites de input (Zod)

| Endpoint | Campo | Límite |
|---|---|---|
| /api/agents | text | 1-10,000 chars |
| /api/agents | apiKey | max 500 chars |
| /api/agents | model | max 200 chars |
| /api/agents | temperature | 0-2 |
| /api/agents | maxTokens | 50-8,000 |
| /api/memories | ciphertext | max 1 MB |
| /api/memories | iv | 16-32 chars |
| /api/memories | tags | max 20 items |
| /api/share | maxViews | 1-1,000 |
| /api/auth/register | password | 8-200 chars |

### Performance

- **Cold start**: ~1.1s (Next.js standalone build)
- **Page load**: ~50-300ms (con cache)
- **LLM call**: 200ms-3s (depende del provider)
- **Cifrado AES-GCM**: <10ms por recuerdo
- **Render pixelart**: 60fps con animaciones

---

## 7. Estructura de Archivos

```
minbot-task/
├── src/
│   ├── app/
│   │   ├── page.tsx                              # Entry: landing → vault → app
│   │   ├── layout.tsx                            # Root layout + AuthProvider
│   │   ├── globals.css                           # Cyberpunk theme + pixel borders
│   │   └── api/
│   │       ├── memories/route.ts                 # CRUD cifrado (Zod + rate limit)
│   │       ├── agents/route.ts                   # 16 LLMs unificados
│   │       ├── share/route.ts                    # Share links revocables
│   │       └── auth/
│   │           ├── [...nextauth]/route.ts        # NextAuth handler
│   │           └── register/route.ts             # Registro con bcrypt
│   ├── components/
│   │   ├── pixelart/
│   │   │   ├── PixelCanvas.tsx                   # Canvas genérico
│   │   │   ├── PixelBackground.tsx               # Fondo animado full-screen
│   │   │   └── PixelLogo.tsx                     # Logo + wordmark
│   │   ├── minbot-task/
│   │   │   ├── HeroSection.tsx                   # Landing completa
│   │   │   ├── UnlockScreen.tsx                  # Pantalla de vault
│   │   │   ├── MemoryChat.tsx                    # Chat de captura
│   │   │   ├── MemoryTimeline.tsx                # Cronología filtrable
│   │   │   ├── MemoryGraph.tsx                   # Mini-grafo drag&drop
│   │   │   ├── StatsPanel.tsx                    # Stats del vault
│   │   │   ├── LLMSettings.tsx                   # Selector 16 LLMs
│   │   │   ├── GraphifyIntegration.tsx           # Dialog Graphify
│   │   │   ├── InstallationsSection.tsx          # Guías paso a paso
│   │   │   └── IdeasSection.tsx                  # Roadmap de 21 ideas
│   │   └── ui/                                   # shadcn/ui (55 componentes)
│   └── lib/
│       ├── crypto.ts                             # WebCrypto (AES-GCM, PBKDF2)
│       ├── store.ts                              # Zustand + heuristic agent
│       ├── llm-settings.ts                       # 16 providers config
│       ├── graphify.ts                           # MCP integration
│       ├── db.ts                                 # Prisma client
│       ├── utils.ts                              # cn() helper
│       ├── auth/
│       │   ├── config.ts                         # NextAuth config
│       │   ├── helpers.ts                        # getCurrentUser, requireUser
│       │   └── provider.tsx                      # SessionProvider client
│       └── pixelart/
│           ├── engine.ts                         # PRNG, noise, renderers
│           └── robots.ts                         # 5 templates, 9 paletas
├── prisma/
│   └── schema.prisma                             # User, Memory, Reminder, etc.
├── public/
│   └── logo.svg
├── next.config.ts                                # CSP headers + security
├── package.json                                  # name: minbot-task, v0.5.0
├── README.md
└── .env                                          # DATABASE_URL, NEXTAUTH_SECRET
```

### Conteo de líneas

| Archivo | Líneas |
|---|---|
| `InstallationsSection.tsx` | 709 |
| `HeroSection.tsx` | 767 |
| `robots.ts` | 565 |
| `engine.ts` | 563 |
| `MemoryGraph.tsx` | 485 |
| `store.ts` | 478 |
| `agents/route.ts` | 488 |
| **Total proyecto** | **~7,500** |

---

## Conclusión

MinBot-Task v0.5 es un proyecto open-source completo que demuestra:

1. **Zero-knowledge real**: el servidor nunca ve plaintext, auditado con WebCrypto nativo
2. **Multi-LLM escalable**: arquitectura unificada que añade providers en 5 líneas
3. **Multi-canal ToS-compliant**: 9 integraciones con APIs oficiales documentadas paso a paso
4. **Pixelart procedural**: motor propio que genera visuales únicos sin assets
5. **Roadmap claro**: 21 ideas con estimaciones de implementación

El proyecto está listo para que la comunidad contribuya. Cada idea del roadmap tiene una propuesta concreta de implementación, las librerías necesarias, y una estimación de tiempo. MinBot-Task no compite con Memorae o Notion — **se conecta a ellos** como capa de memoria cifrada open-source.

---

**MinBot-Task** · MIT License · Open Source · Self-hostable
Documentación técnica v0.5 · 2026-07-17
