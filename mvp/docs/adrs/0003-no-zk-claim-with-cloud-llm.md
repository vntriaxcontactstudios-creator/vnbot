# ADR-0003: Do not call zero-knowledge a flow that sends plaintext to LLM

## Estado

Aceptada

## Contexto

Muchos productos prometen "zero-knowledge" como marketing genérico. En VNBOT, esta promesa es falsa cuando el flujo envía plaintext a un LLM cloud (Z.AI, OpenAI, Anthropic, etc.). El proveedor cloud puede técnicamente leer el contenido durante el request, incluso si está cifrado en reposo en su base de datos.

El TRD §24 #16 prohibe esta práctica. El doc 08 §5 define una tabla precisa de qué descripción usar según el caso real.

## Decisión

**NO usar el término "zero-knowledge" como promesa genérica.** En su lugar, describir explícitamente en cada flujo:

| Caso | Descripción correcta |
|------|---------------------|
| Vault local + LLM local (Ollama) | "Procesamiento local" |
| DB ciphertext + cloud API para análisis | "Cifrado en reposo, no ZK total" |
| Servidor propio con proceso que descifra | "Servidor privado" |
| WebCrypto con LLM externo | "Cifrado local parcial" |

La UI debe mostrar esta descripción antes de activar cualquier proveedor externo, listando:

- Proveedor (Z.AI, OpenAI, etc.)
- Modelo (glm-4.6, gpt-4o-mini, etc.)
- Datos excluidos del envío (memorias secret, credentials, tokens)
- Política de retención del proveedor (si es conocida)

## Consecuencias

- **Positivas**: Honestidad con el usuario, expectativas correctas, cumplimiento del principio "el usuario controla sus datos".
- **Negativas**: Marketing menos impactante que "zero-knowledge".
- **Riesgos**: Usuarios que no leen las descripciones pueden sorprenderse — mitigar con UI prominente.

## Alternativas consideradas

1. **E2E encryption con FHE (fully homomorphic encryption)** — inviable hoy (latencia 100-1000x mayor), no hay FHE práctico para LLMs.
2. **Solo LLM local (Ollama)** — restringe accesibilidad, no todos tienen GPU/CPU potente.
3. **"Zero-knowledge" como marketing** — deshonesto, viola principio central de VNBOT.

## Referencias

- TRD §24 #16 (frozen decision)
- Seguridad §5 (precise ZK definition table)
- Seguridad §4.3 (Modo LLM Externo)
- ADR relacionado: ADR-0007 (mandatory heuristic fallback)
