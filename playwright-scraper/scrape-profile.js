const { chromium } = require('playwright');
const fs = require('fs');

const BASE_URL = 'http://astronauts.paper.private';
const ENGINEER_EMAIL = 'abdian.rizki@paper.id';

async function main() {
  fs.mkdirSync('screenshots', { recursive: true });
  fs.mkdirSync('data', { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1600, height: 1000 });

  try {
    await page.goto(BASE_URL, { waitUntil: 'networkidle', timeout: 15000 });

    // ---- ON-CALL PROFILE ----
    console.log('\n--- On-Call: abdian profile ---');
    await page.locator('button.tab:has-text("On-Call")').click();
    await page.waitForTimeout(1500);

    // Switch to Individuals
    await page.locator('[data-sub="oncall-eng-sub"]').click();
    await page.waitForTimeout(1000);

    // Filter RnG Squad 2
    const rngChips = page.locator('button.chip:has-text("RnG Squad 2")');
    for (let i = 0; i < await rngChips.count(); i++) {
      if (await rngChips.nth(i).isVisible()) {
        await rngChips.nth(i).click();
        break;
      }
    }
    await page.waitForTimeout(1000);

    // Click abdian.rizki link
    const abdianLink = page.locator(`text=${ENGINEER_EMAIL}`).first();
    if (await abdianLink.isVisible()) {
      await abdianLink.click();
      await page.waitForTimeout(2500);

      // Screenshot of full profile
      await page.screenshot({ path: 'screenshots/oncall-profile-full.png', fullPage: true });
      console.log('[OK] on-call profile screenshot saved');

      // Extract all text from the profile overlay/modal
      const profileText = await page.evaluate(() => {
        // Try multiple selectors for modal
        const selectors = ['.overlay', '.modal', '.profile-overlay', '.profile-modal', '[class*="overlay"]', '[class*="modal"]', '[class*="profile"]', '.side-panel'];
        for (const sel of selectors) {
          const el = document.querySelector(sel);
          if (el && el.innerText.length > 50) return el.innerText;
        }
        // Fallback: get everything after main content
        return document.body.innerText;
      });
      fs.writeFileSync('data/oncall-profile.txt', profileText);
      console.log('[OK] on-call profile text saved');

      // Extract tables inside profile
      const tables = await page.evaluate(() => {
        const selectors = ['.overlay', '.modal', '[class*="overlay"]', '[class*="modal"]'];
        let container = null;
        for (const sel of selectors) {
          const el = document.querySelector(sel);
          if (el && el.innerText.length > 50) { container = el; break; }
        }
        if (!container) container = document;

        const rows = container.querySelectorAll('table tr');
        return Array.from(rows).map(row => {
          const cells = row.querySelectorAll('td, th');
          return Array.from(cells).map(c => c.textContent.trim());
        }).filter(r => r.length > 0);
      });
      fs.writeFileSync('data/oncall-profile-table.json', JSON.stringify(tables, null, 2));
      console.log('[OK] on-call profile tables saved, rows:', tables.length);

      // Close modal
      await page.keyboard.press('Escape');
      await page.waitForTimeout(500);
    } else {
      console.log('abdian link not found in on-call individuals');
    }

    // ---- CODE HEALTH: Services > Network BU ----
    console.log('\n--- Code Health: Services > Network BU ---');
    await page.locator('button.tab:has-text("Code Health")').click();
    await page.waitForTimeout(2000);

    // Switch to Services
    const servicesBtnAll = page.locator('button:has-text("Services")');
    for (let i = 0; i < await servicesBtnAll.count(); i++) {
      if (await servicesBtnAll.nth(i).isVisible()) {
        await servicesBtnAll.nth(i).click();
        break;
      }
    }
    await page.waitForTimeout(1000);

    // Click Network filter
    const networkBtns = page.locator('button:has-text("Network")');
    for (let i = 0; i < await networkBtns.count(); i++) {
      if (await networkBtns.nth(i).isVisible()) {
        await networkBtns.nth(i).click();
        break;
      }
    }
    await page.waitForTimeout(2000);

    await page.screenshot({ path: 'screenshots/codehealth-services-network.png', fullPage: true });
    console.log('[OK] code health network screenshot');

    // Extract the services table
    const codeHealthText = await page.evaluate(() => {
      const main = document.querySelector('#code-health, .code-health-section, main');
      return main ? main.innerText : document.body.innerText;
    });
    fs.writeFileSync('data/codehealth-services.txt', codeHealthText);

    const codeHealthTable = await page.evaluate(() => {
      const rows = document.querySelectorAll('table tr');
      return Array.from(rows).map(row => {
        const cells = row.querySelectorAll('td, th');
        return Array.from(cells).map(c => c.textContent.trim());
      }).filter(r => r.length > 0);
    });
    fs.writeFileSync('data/codehealth-services.json', JSON.stringify(codeHealthTable, null, 2));
    console.log('[OK] code health services table, rows:', codeHealthTable.length);
    codeHealthTable.forEach(row => console.log(' ', row.join(' | ')));

    // ---- SPRINT POINTS PROFILE ----
    console.log('\n--- Sprint Points: abdian profile ---');
    await page.locator('button.tab:has-text("Sprint Points")').click();
    await page.waitForTimeout(1500);

    await page.locator('[data-sub="sp-individuals-sub"]').click();
    await page.waitForTimeout(1000);

    const spRngChips = page.locator('button.chip.sp-chip:has-text("RnG Squad 2")');
    if (await spRngChips.count() > 0) {
      await spRngChips.first().click();
      await page.waitForTimeout(1000);
    }

    const abdianSPLink = page.locator(`text=${ENGINEER_EMAIL}`).first();
    if (await abdianSPLink.isVisible()) {
      await abdianSPLink.click();
      await page.waitForTimeout(2500);
      await page.screenshot({ path: 'screenshots/sprintpoints-profile.png', fullPage: true });
      console.log('[OK] sprint points profile screenshot');

      const spText = await page.evaluate(() => {
        const selectors = ['.overlay', '.modal', '[class*="overlay"]', '[class*="modal"]', '[class*="profile"]'];
        for (const sel of selectors) {
          const el = document.querySelector(sel);
          if (el && el.innerText.length > 50) return el.innerText;
        }
        return document.body.innerText;
      });
      fs.writeFileSync('data/sprintpoints-profile.txt', spText);
      console.log('[OK] sprint points profile text saved');
    }

    console.log('\n=== Done ===');
    console.log('Files:', fs.readdirSync('data').join(', '));

  } catch (err) {
    console.error('Error:', err.message);
    await page.screenshot({ path: 'screenshots/error-profile.png', fullPage: true });
  } finally {
    await browser.close();
  }
}

main();
