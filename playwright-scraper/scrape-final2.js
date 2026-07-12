const { chromium } = require('playwright');
const fs = require('fs');

const BASE_URL = 'http://astronauts.paper.private';

async function main() {
  fs.mkdirSync('screenshots', { recursive: true });
  fs.mkdirSync('data', { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1600, height: 1000 });

  try {
    await page.goto(BASE_URL, { waitUntil: 'networkidle', timeout: 15000 });

    // ============================
    // CODE HEALTH > ch-services sub-tab > Network
    // ============================
    console.log('--- Code Health > Services > Network ---');
    await page.locator('button.tab[data-tab="codehealth"]').click();
    await page.waitForTimeout(1500);

    // Check what's currently visible in code health
    const chContent = await page.evaluate(() => {
      const chSection = document.querySelector('#codehealth, [id="codehealth"]');
      if (chSection) return { found: true, text: chSection.innerText.slice(0, 500) };
      // Try by visible area
      return { found: false, body: document.body.innerText.slice(0, 500) };
    });
    console.log('Code health section:', JSON.stringify(chContent));

    // Click ch-services
    await page.locator('[data-sub="ch-services"]').click();
    await page.waitForTimeout(2000);

    await page.screenshot({ path: 'screenshots/ch-services-01.png' });

    // Check what's visible now
    const afterClick = await page.evaluate(() => {
      // Find all visible sections
      const allText = document.body.innerText;
      // Find coverage-related content
      const coverageIdx = allText.indexOf('Coverage');
      const serviceIdx = allText.indexOf('Service');
      return {
        bodyLength: allText.length,
        coverageAt: coverageIdx,
        serviceAt: serviceIdx,
        sample: allText.slice(0, 1000)
      };
    });
    console.log('After ch-services click:', JSON.stringify(afterClick, null, 2));

    // Look for the services table with per-sprint coverage
    // Try clicking Network chip
    const allChips = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('button')).filter(b => b.offsetParent).map(b => ({
        text: b.textContent.trim(),
        class: b.className,
        dataSub: b.dataset.sub
      }));
    });
    console.log('Visible buttons after ch-services:', JSON.stringify(allChips));

    // Find and click Network chip
    for (const chip of allChips) {
      if (chip.text === 'Network' && !chip.dataSub && chip.class.includes('chip')) {
        const btn = page.locator(`button.${chip.class.split(' ').join('.')}:has-text("Network")`).first();
        if (await btn.count() > 0 && await btn.isVisible()) {
          await btn.click();
          await page.waitForTimeout(1500);
          console.log('Clicked Network chip');
          break;
        }
      }
    }

    // Try another approach - click any visible Network button
    const networkBtns = await page.locator('button').all();
    for (const btn of networkBtns) {
      try {
        const txt = await btn.textContent();
        const vis = await btn.isVisible();
        if (txt.trim() === 'Network' && vis) {
          await btn.click();
          await page.waitForTimeout(1500);
          console.log('Clicked Network via all-buttons approach');
          break;
        }
      } catch {}
    }

    await page.screenshot({ path: 'screenshots/ch-services-network.png', fullPage: true });

    // Get all table data visible now
    const servicesData = await page.evaluate(() => {
      const tables = document.querySelectorAll('table');
      const result = [];
      tables.forEach((t, ti) => {
        const rows = Array.from(t.querySelectorAll('tr')).map(row =>
          Array.from(row.querySelectorAll('td, th')).map(c => c.textContent.trim())
        ).filter(r => r.length > 0);
        if (rows.length > 0) result.push({ tableIndex: ti, rows });
      });
      return result;
    });
    fs.writeFileSync('data/ch-services-network.json', JSON.stringify(servicesData, null, 2));
    console.log('Services tables found:', servicesData.length);
    servicesData.forEach(t => {
      console.log(`  Table ${t.tableIndex} (${t.rows.length} rows), header: ${t.rows[0]?.join(' | ')}`);
      t.rows.slice(1, 6).forEach(r => console.log('    ', r.join(' | ')));
    });

    // ============================
    // ON-CALL profile - fixed selector
    // ============================
    console.log('\n--- On-Call profile ---');
    await page.locator('button.tab[data-tab="oncall"]').click();
    await page.waitForTimeout(1500);

    await page.locator('[data-sub="oncall-eng-sub"]').click();
    await page.waitForTimeout(1000);

    // Search using the search box
    const searchBox = page.locator('input[placeholder="Search engineer…"]');
    if (await searchBox.count() > 0) {
      await searchBox.fill('abdian');
      await page.waitForTimeout(1200);
      console.log('Filled search with "abdian"');
    }

    await page.screenshot({ path: 'screenshots/oncall-search.png' });

    // Find abdian using evaluate
    const abdianRowFound = await page.evaluate(() => {
      const cells = document.querySelectorAll('td');
      for (const cell of cells) {
        if (cell.textContent.includes('abdian.rizki')) {
          return { found: true, text: cell.textContent.trim() };
        }
      }
      return { found: false };
    });
    console.log('abdian row found:', JSON.stringify(abdianRowFound));

    if (abdianRowFound.found) {
      // Click via JavaScript
      await page.evaluate(() => {
        const cells = document.querySelectorAll('td');
        for (const cell of cells) {
          if (cell.textContent.includes('abdian.rizki')) {
            cell.click();
            return;
          }
        }
      });
      await page.waitForTimeout(2500);
      await page.screenshot({ path: 'screenshots/oncall-profile.png', fullPage: true });
      console.log('[OK] On-call profile screenshot');

      const tables = await page.evaluate(() => {
        return Array.from(document.querySelectorAll('table')).map((t, ti) => ({
          tableIndex: ti,
          rows: Array.from(t.querySelectorAll('tr')).map(row =>
            Array.from(row.querySelectorAll('td, th')).map(c => c.textContent.trim())
          ).filter(r => r.length > 0)
        }));
      });
      fs.writeFileSync('data/oncall-profile-tables.json', JSON.stringify(tables, null, 2));
      console.log('Tables in on-call profile:', tables.length);
      tables.forEach(t => {
        console.log(`  Table ${t.tableIndex} (${t.rows.length} rows):`);
        t.rows.slice(0, 10).forEach(r => console.log('    ', r.join(' | ')));
      });
    }

    // ============================
    // SPRINT POINTS profile
    // ============================
    console.log('\n--- Sprint Points profile ---');
    await page.locator('button.tab[data-tab="sprint-points"]').click();
    await page.waitForTimeout(1500);

    await page.locator('[data-sub="sp-individuals-sub"]').click();
    await page.waitForTimeout(1000);

    // Click RnG Squad 2 chip
    const spChips = await page.locator('button').all();
    for (const chip of spChips) {
      try {
        const txt = await chip.textContent();
        const vis = await chip.isVisible();
        if (txt.trim() === 'RnG Squad 2' && vis) {
          await chip.click();
          await page.waitForTimeout(800);
          console.log('Clicked RnG Squad 2 chip for SP');
          break;
        }
      } catch {}
    }

    // Click abdian via JS
    const abdianSPFound = await page.evaluate(() => {
      const cells = document.querySelectorAll('td');
      for (const cell of cells) {
        if (cell.textContent.includes('abdian.rizki')) {
          return { found: true, text: cell.textContent };
        }
      }
      return { found: false };
    });
    console.log('abdian in SP:', JSON.stringify(abdianSPFound));

    if (abdianSPFound.found) {
      await page.evaluate(() => {
        const cells = document.querySelectorAll('td');
        for (const cell of cells) {
          if (cell.textContent.includes('abdian.rizki')) {
            cell.click();
            return;
          }
        }
      });
      await page.waitForTimeout(2500);
      await page.screenshot({ path: 'screenshots/sp-profile.png', fullPage: true });

      const tables = await page.evaluate(() => {
        return Array.from(document.querySelectorAll('table')).map((t, ti) => ({
          tableIndex: ti,
          rows: Array.from(t.querySelectorAll('tr')).map(row =>
            Array.from(row.querySelectorAll('td, th')).map(c => c.textContent.trim())
          ).filter(r => r.length > 0)
        }));
      });
      fs.writeFileSync('data/sp-profile-tables.json', JSON.stringify(tables, null, 2));
      console.log('SP profile tables:', tables.length);
      tables.forEach(t => {
        console.log(`  Table ${t.tableIndex} (${t.rows.length} rows):`);
        t.rows.slice(0, 10).forEach(r => console.log('    ', r.join(' | ')));
      });
    }

    console.log('\n=== Done ===');

  } catch (err) {
    console.error('Error:', err.message);
    await page.screenshot({ path: 'screenshots/error-f2.png', fullPage: true });
  } finally {
    await browser.close();
  }
}

main();
