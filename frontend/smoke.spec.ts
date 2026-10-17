import { test, expect } from '@playwright/test';

test('home loads', async ({ page }) => {
  await page.goto('http://127.0.0.1:5173/');
  await expect(page).toHaveTitle(/Gaon/);
});
EOF