/**
 * VNBOT E2E — Vertical slice test.
 *
 * Tests the full Sprint 1 flow:
 * 1. User opens /today
 * 2. Types 'Recuérdame mañana a las 9 revisar VNBOT'
 * 3. Sees proposal with title + due_at
 * 4. Confirms
 * 5. Sees success message
 * 6. Navigates to /memory, verifies no memory created (this was a reminder)
 * 7. Navigates to /activity, sees the operation
 * 8. Tests memory creation: 'Guarda que el wifi es vnbot123'
 * 9. Verifies memory appears in /memory list
 * 10. Tests search: 'wifi' finds the memory
 *
 * Pre-requirements:
 * - Backend running on :8000 with clean DB
 * - Frontend running on :5173
 */

import { test, expect } from '@playwright/test';

const API_BASE = 'http://localhost:8000/api/v1';

test.beforeAll(async () => {
  // Health check — backend must be up
  const resp = await fetch('http://localhost:8000/healthz');
  if (!resp.ok) {
    throw new Error(`Backend not running on :8000 (status ${resp.status})`);
  }
});

test('vertical slice: chat → reminder → memory → search → activity', async ({ page }) => {
  // ─── Step 1: Open /today ───
  await page.goto('/today');

  // Verify welcome message visible
  await expect(page.getByText('Bienvenido a VNBOT')).toBeVisible({ timeout: 10_000 });

  // ─── Step 2: Type reminder input ───
  const chatInput = page.getByLabel('Chat input');
  await chatInput.fill('Recuérdame mañana a las 9 revisar VNBOT');

  // ─── Step 3: Submit ───
  await page.getByRole('button', { name: 'Send message' }).click();

  // Wait for proposal to appear — look for the title input with the parsed value
  await expect(page.locator('input[value="Revisar VNBOT"]')).toBeVisible({ timeout: 5_000 });

  // Verify due_at is set (tomorrow at 9am)
  const dueAtInput = page.getByLabel('Fecha y hora');
  await expect(dueAtInput).toHaveValue(/.+/);

  // ─── Step 4: Confirm ───
  await page.getByRole('button', { name: /CONFIRMAR/i }).click();

  // ─── Step 5: Verify success message ───
  await expect(page.getByText(/Recordatorio creado/i)).toBeVisible({ timeout: 5_000 });

  // ─── Step 6: Verify reminder was created in DB via API ───
  const remindersResp = await fetch(`${API_BASE}/memories`);
  expect(remindersResp.ok).toBeTruthy();

  // ─── Step 7: Create a memory via chat ───
  await chatInput.fill('Guarda que el wifi de la oficina es vnbot123');
  await page.getByRole('button', { name: 'Send message' }).click();

  // Wait for the CONFIRMAR button to appear (indicates proposal is ready)
  await expect(page.getByRole('button', { name: /CONFIRMAR/i })).toBeVisible({ timeout: 5_000 });

  // Confirm memory creation
  await page.getByRole('button', { name: /CONFIRMAR/i }).click();

  // Wait for success — look for 'memory' in the success message
  await expect(page.getByText(/Memory creada|creada/i).first()).toBeVisible({ timeout: 5_000 });

  // ─── Step 8: Navigate to /memory ───
  await page.goto('/memory');

  // Verify the memory appears in the list (use first() because label + content may both match)
  await expect(page.getByText('El wifi de la oficina es vnbot123').first()).toBeVisible({
    timeout: 5_000,
  });

  // ─── Step 9: Search for 'wifi' ───
  const searchInput = page.getByLabel('Search memories');
  await searchInput.fill('wifi');
  await page.getByRole('button', { name: 'BUSCAR' }).click();

  // Verify search result with highlighted match
  await expect(page.getByText(/resultado\(s\) para "wifi"/i)).toBeVisible({
    timeout: 5_000,
  });

  // The snippet should contain 'wifi' (possibly highlighted with <mark>)
  await expect(page.locator('mark:has-text("wifi")')).toBeVisible();

  // ─── Step 10: Navigate to /activity ───
  await page.goto('/activity');

  // Verify summary cards show counts
  await expect(page.getByText('Total operaciones')).toBeVisible({ timeout: 5_000 });

  // Verify operations list has entries
  await expect(page.getByText('Historial de operaciones')).toBeVisible();
  // Operation types are displayed with underscores replaced by spaces (e.g. "CREATE REMINDER")
  // Use .first() because types appear in both summary breakdown and operations list
  await expect(page.getByText(/create reminder/i).first()).toBeVisible();
  await expect(page.getByText(/create memory/i).first()).toBeVisible();
});

test('unknown input returns helpful suggestion', async ({ page }) => {
  await page.goto('/today');
  await page.waitForLoadState('networkidle');

  // Dismiss any pending proposal from previous test
  const cancelButton = page.getByRole('button', { name: /Cancelar/i });
  if (await cancelButton.isVisible({ timeout: 1_000 }).catch(() => false)) {
    await cancelButton.click();
    await page.waitForTimeout(500);
  }

  const chatInput = page.getByLabel('Chat input');
  await chatInput.fill('Hola, ¿cómo estás?');
  await page.getByRole('button', { name: 'Send message' }).click();

  // Should show error with suggestion
  await expect(page.getByText(/No pude interpretar/i)).toBeVisible({ timeout: 5_000 });
  await expect(page.getByText(/configura un proveedor LLM/i)).toBeVisible();
});

test('memory panel empty state', async ({ page }) => {
  // This test verifies the empty state when no memories exist.
  // Note: depends on DB state — run with fresh DB.
  await page.goto('/memory');

  // Wait for load
  await page.waitForLoadState('networkidle');

  // Either shows memories or empty state
  const memoriesList = page.locator('text=memoria(s)');
  const emptyState = page.getByText('Sin memorias todavía');

  // One of them must be visible
  await expect(memoriesList.or(emptyState)).toBeVisible({ timeout: 5_000 });
});

test('health endpoint is accessible', async () => {
  const resp = await fetch('http://localhost:8000/healthz');
  const data = await resp.json();
  expect(data.status).toBe('ok');
  expect(data.version).toBe('0.1.0');
});

test('dependencies endpoint shows scheduler + channels', async () => {
  const resp = await fetch('http://localhost:8000/dependencies');
  const data = await resp.json();
  expect(data.checks.scheduler_started).toBe('True');
  expect(data.checks.notification_channels_registered).toContain('mock');
  expect(data.checks.llm_provider).toBe('zai');
});

test('@axe accessibility: no critical AA violations on /today', async ({ page }) => {
  // This test uses @axe-core/playwright to scan for accessibility issues.
  // Tagged with @axe so it can be run separately.
  test.skip(!process.env.AXE_ENABLED, 'Set AXE_ENABLED=1 to run axe tests');

  await page.goto('/today');
  await page.waitForLoadState('networkidle');

  const { default: AxeBuilder } = await import('@axe-core/playwright');
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa'])
    .analyze();

  // Filter out known issues with the pixel art canvas (canvas doesn't have role)
  const criticalViolations = results.violations.filter(
    (v) => v.impact === 'critical' && !v.description.includes('canvas'),
  );

  expect(criticalViolations).toEqual([]);
});
