# Guía: Deploy de VNBOT Demo en Netlify

Esta guía te lleva paso a paso para desplegar la **demo estática** de VNBOT en Netlify.
La demo usa datos mock (no necesita backend) — perfecta para mostrar la UI.

---

## ¿Qué necesitas antes de empezar?

1. **Cuenta en [Netlify](https://app.netlify.com/)** (gratuita, puedes hacer login con GitHub)
2. **Tu repo de VNBOT en GitHub**: `vntriaxcontactstudios-creator/vnbot`
3. El archivo `netlify.toml` YA ESTÁ en el repo root (lo acabamos de arreglar ✅)

---

## Paso 1: Entra a Netlify y crea un site

1. Ve a **[app.netlify.com](https://app.netlify.com/)**
2. Click en **"Add new site"** → **"Import an existing project"**
3. Click en **"GitHub"** (autoriza a Netlify a ver tus repos si es la primera vez)
4. Busca y selecciona tu repo: **`vntriaxcontactstudios-creator/vnbot`**

---

## Paso 2: Configuración de build

Netlify te va a pedir algunos datos. **Aquí está el truco**: como el `netlify.toml`
ya está en el repo root, Netlify debería detectarlo automáticamente y llenar los
campos. **Pero si no lo hace, rellena manualmente**:

| Campo | Valor |
|-------|-------|
| **Base directory** | _(déjalo vacío — usa el repo root)_ |
| **Build command** | `cd mvp && pnpm install --no-frozen-lockfile && pnpm --filter @vnbot/web build` |
| **Publish directory** | `mvp/apps/web/dist` |
| **Branch to deploy** | `main` |

> ⚠️ **NO pongas `mvp/` como "Base directory"** — eso rompería el `netlify.toml`.
> El `cd mvp` ya está en el build command, así que el repo root se queda como base.

---

## Paso 3: Variables de entorno

En la misma pantalla de configuración, baja hasta **"Advanced"** → **"Environment variables"**
y verifica que estén estas (el `netlify.toml` las setea, pero conviene confirmar):

| Key | Value |
|-----|-------|
| `VITE_DEMO_MODE` | `true` |
| `VITE_API_BASE_URL` | _(vacío)_ |
| `VITE_BASE_PATH` | `/` |
| `NODE_VERSION` | `20` |
| `PNPM_VERSION` | `9` |
| `NETLIFY_USE_PNPM` | `true` |

> 💡 **Si no aparecen automáticamente**, agrégalas manualmente. Las variables de
> `netlify.toml` deberían cargarse solas, pero a veces Netlify las sobreescribe
> con defaults.

---

## Paso 4: Click en "Deploy site"

1. Click en **"Deploy site"**
2. Netlify va a:
   - Clonar tu repo
   - Detectar `netlify.toml` automáticamente
   - Instalar pnpm 9
   - Instalar dependencias (`pnpm install`)
   - Construir la app (`pnpm --filter @vnbot/web build`)
   - Publicar `mvp/apps/web/dist/`
3. Tarda ~2-3 minutos la primera vez
4. Te asigna una URL tipo `https://amazing-vnbot-abc123.netlify.app`

---

## Paso 5: Verifica que funciona

1. Abre la URL que te dio Netlify
2. Deberías ver la UI de VNBOT cargando
3. Navega a **/memory**, **/skills**, **/learning** — todas deberían funcionar
4. Refresca la página estando en `/skills` — **no debería dar 404** (gracias al SPA fallback)

### Si te aparece el error 404 al refrescar:

Ese era exactamente tu problema anterior. Las causas eran:
- ❌ `netlify.toml` estaba en `mvp/` en vez del repo root → Netlify no lo leía
- ❌ El `[[redirects]]` con SPA fallback no se aplicaba
- ❌ `base: '/vnbot/'` hacía que todos los assets se cargaran de una ruta inexistente

**Ya está arreglado** con:
- ✅ `netlify.toml` movido al repo root
- ✅ `VITE_BASE_PATH='/'` para que los assets carguen desde la raíz
- ✅ Redirect `/* → /index.html` para SPA routing

---

## Paso 6 (opcional): Cambiar el nombre del site

La URL inicial es fea (`amazing-vnbot-abc123.netlify.app`). Para cambiarla:

1. En Netlify → **Site settings** → **Change site name**
2. Elige algo como `vnbot-demo` → URL final: `https://vnbot-demo.netlify.app`

---

## Paso 7 (opcional): Dominio personalizado

Si tienes un dominio propio:

1. **Site settings** → **Domain management** → **Add custom domain**
2. Sigue las instrucciones (Netlify te da los DNS records a configurar)
3. SSL se configura automáticamente (Let's Encrypt)

---

## Troubleshooting

### "Build failed" en Netlify

Abre los **Deploy logs** en Netlify. Los errores más comunes:

| Error | Causa | Solución |
|-------|-------|----------|
| `pnpm: command not found` | Netlify no detecta pnpm | Añade `NETLIFY_USE_PNPM=true` en env vars |
| `Cannot find module '@vnbot/pixelart'` | Workspace no se resuelve | Verifica que el `pnpm install` corra desde `mvp/` |
| `dist/ not found` | Publish path mal | Debe ser `mvp/apps/web/dist` (relativo al repo root) |
| `404 al cargar assets` | Base path mal | Asegúrate que `VITE_BASE_PATH='/'` |

### "Page Not Found" al refrescar /memory

Significa que el redirect SPA no se aplicó. Verifica en Netlify:
- **Site settings** → **Domain management** → ¿aparece el redirect `/* → /index.html`?
- Si no aparece, Netlify no leyó el `netlify.toml`. Asegúrate que está en el repo root.

### La UI carga pero los datos no aparecen

Eso NO es un error — es el **modo demo**. Como no hay backend, se inyectan datos
mock. Para ver datos reales necesitas correr el backend localmente.

---

## ¿Por qué Netlify y no GitHub Pages?

GitHub Pages tiene limitaciones que nos hicieron problemas antes:
- ❌ Solo sirve desde `/gh-pages/` branch o `docs/` folder
- ❌ Subpath `/vnbot/` rompe assets relativos
- ❌ GitHub Actions runner allocation fallaba

Netlify es mejor para demos porque:
- ✅ Build integrado (no necesitas CI separado)
- ✅ Detecta `netlify.toml` automáticamente
- ✅ SPA fallback nativo vía redirects
- ✅ Headers HTTP custom (cache, security)
- ✅ Deploy previews en cada PR
- ✅ SSL automático

---

## ¿Qué sigue después del deploy?

1. **Verifica la demo** — explora todas las rutas (`/today`, `/memory`, `/skills`, `/learning`)
2. **Comparte la URL** con quien quieras mostrar VNBOT
3. **Para uso real**: corre el backend localmente (`docker compose up -d`) y conecta el frontend a `http://localhost:8000`

La demo en Netlify es solo para mostrar la UI. Para funcionalidad completa
(recordatorios reales, memoria persistida, Hermes learning loop activo),
necesitas el stack completo corriendo en tu máquina (Fase 0.2 con Docker).
