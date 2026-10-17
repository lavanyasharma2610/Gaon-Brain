import { test, expect } from '@playwright/test';

const BASE = process.env.BASE_URL || 'http://127.0.0.1:5173';

test.describe('Gaon Brain Demo Path', () => {
  test('home loads and navigates', async ({ page }) => {
    await page.goto(BASE);
    await expect(page.locator('h1')).toContainText('Gaon Brain');
  });

  test('Ek Awaaz: voice parse and confirm', async ({ page }) => {
    await page.goto(BASE);
    await page.waitForSelector('text=Ek Awaaz');
    
    // Type a sale event
    await page.fill('input[placeholder="Ya yahan type karo"]', '5 kilo gehu becha');
    await page.press('input[placeholder="Ya yahan type karo"]', 'Enter');
    
    // Wait for confirm card
    await page.waitForSelector('button:has-text("Haan")');
    await expect(page.locator('pre')).toContainText('record_sale');
    
    // Confirm
    await page.click('button:has-text("Haan")');
    await expect(page.locator('pre')).toContainText('saved');
  });

  test('Gaon Plan: run plan and show Kyun', async ({ page }) => {
    await page.goto(BASE + '/plan');
    await page.waitForSelector('button:has-text("Run Plan")');
    
    await page.click('button:has-text("Run Plan")');
    await page.waitForSelector('button:has-text("Kyun?")');
    
    await page.click('button:has-text("Kyun?")');
    await expect(page.locator('div[style*="white-space: pre-wrap"]')).toBeVisible();
  });

  test('Jhatka: shock chain runs', async ({ page }) => {
    await page.goto(BASE + '/jhatka');
    await page.waitForSelector('button:has-text("Blight on 3 plots")');
    
    await page.click('button:has-text("Blight on 3 plots")');
    await expect(page.locator('div[style*="white-space: pre-wrap"]')).toContainText('Radar');
  });

  test('Sanjha: tractor schedule loads', async ({ page }) => {
    await page.goto(BASE + '/sanjha');
    await page.waitForSelector('button:has-text("Load")');
    
    await page.click('button:has-text("Load")');
    await expect(page.locator('pre')).toBeVisible();
  });

  test('Radar: Fasal Doctor analyze', async ({ page }) => {
    await page.goto(BASE + '/radar');
    await page.waitForSelector('button:has-text("Analyze")');
    
    await page.click('button:has-text("Analyze")');
    await expect(page.locator('pre')).toBeVisible();
  });

  test('Bazaar: load lots', async ({ page }) => {
    await page.goto(BASE + '/bazaar');
    await page.waitForSelector('button:has-text("Load Lots")');
    
    await page.click('button:has-text("Load Lots")');
    await expect(page.locator('pre')).toBeVisible();
  });

  test('Suraksha: load sinchai', async ({ page }) => {
    await page.goto(BASE + '/suraksha');
    await page.waitForSelector('button:has-text("Load Sinchai")');
    
    await page.click('button:has-text("Load Sinchai")');
    await expect(page.locator('pre')).toBeVisible();
  });

  test('Simulation: adoption slider', async ({ page }) => {
    await page.goto(BASE + '/simulation');
    await page.waitForSelector('input[type="range"]');
    
    const slider = page.locator('input[type="range"]');
    await slider.fill('30');
    await expect(slider).toHaveValue('30');
  });
});