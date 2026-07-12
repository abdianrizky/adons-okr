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
    // CODE HEALTH > Services > Network BU
    // ============================
    console.log('--- Code Health > Services > Network ---');
    await page.locator('button.tab[data-tab="codehealth"]').click();
    await page.waitForTimeout(1500);

    // Click "Services" sub-tab (ch-services)
    await page.locator('[data-sub="ch-services"]').click();
    await page.waitForTimeout(1500);

    // Filter Network BU
    const networkChips = page.locator('button:has-text("Network"):not(.tab)');
    for (let i = 0; i < await networkChips.count(); i++) {
      if (await networkChips.nth(i).isVisible()) {
        await networkChips.nth(i).click();
        await page.waitForTimeout(1500);
        console.log('Clicked Network chip');
        break;
      }
    }

    await page.screenshot({ path: 'screenshots/ch-services-network.png', fullPage: true });
    console.log('[OK] Screenshot: Code Health Services Network');

    // Extract table
    const chTable = await page.evaluate(() => {
      const tables = document.querySelectorAll('table');
      const result = [];
      tables.forEach(t => {
        const rows = t.querySelectorAll('tr');
        rows.forEach(row => {
          const cells = row.querySelectorAll('td, th');
          const rowData = Array.from(cells).map(c => c.textContent.trim());
          if (rowData.length > 0) result.push(rowData);
        });
      });
      return result;
    });
    fs.writeFileSync('data/ch-services-network.json', JSON.stringify(chTable, null, 2));
    console.log('Code Health Services table rows:', chTable.length);
    chTable.slice(0, 20).forEach(row => console.log(' ', row.join(' | ')));

    // Also get text
    const chText = await page.evaluate(() => {
      const section = document.querySelector('#codehealth, .codehealth-section, main');
      return section ? section.innerText.slice(0, 8000) : document.body.innerText.slice(0, 8000);
    });
    fs.writeFileSync('data/ch-services-network.txt', chText);

    // ============================
    // ON-CALL > Individuals > abdian profile
    // ============================
    console.log('\n--- On-Call > Individuals > abdian ---');
    await page.locator('button.tab[data-tab="oncall"]').click();
    await page.waitForTimeout(1500);

    await page.locator('[data-sub="oncall-eng-sub"]').click();
    await page.waitForTimeout(1000);

    // Search for abdian WITHOUT squad filter first
    const searchInputs = page.locator('input');
    const inputCount = await searchInputs.count();
    console.log('Input fields found:', inputCount);
    for (let i = 0; i < inputCount; i++) {
      const input = searchInputs.nth(i);
      if (await input.isVisible()) {
        const ph = await input.getAttribute('placeholder') || '';
        console.log(`  input[${i}] placeholder="${ph}"`);
        if (ph.toLowerCase().includes('search') || ph.toLowerCase().includes('engineer') || ph.includes('abdi') || ph === '') {
          await input.fill('abdian');
          await page.waitForTimeout(1200);
          break;
        }
      }
    }

    await page.screenshot({ path: 'screenshots/oncall-search.png' });

    // Find abdian
    const abdianCell = page.locator('td:has-text("abdian.rizki@paper.id"), text=abdian.rizki@paper.id');
    const abdianCount = await abdianCell.count();
    console.log('abdian cells found:', abdianCount);

    if (abdianCount > 0) {
      await abdianCell.first().click();
      await page.waitForTimeout(2500);
      await page.screenshot({ path: 'screenshots/oncall-profile.png', fullPage: true });
      console.log('[OK] On-call profile screenshot captured');

      // Extract per-cycle SLA data from all tables
      const tables = await page.evaluate(() => {
        return Array.from(document.querySelectorAll('table')).map((t, ti) => {
          const rows = t.querySelectorAll('tr');
          return {
            tableIndex: ti,
            rows: Array.from(rows).map(row => {
              return Array.from(row.querySelectorAll('td, th')).map(c => c.textContent.trim());
            }).filter(r => r.length > 0)
          };
        });
      });
      fs.writeFileSync('data/oncall-profile-tables.json', JSON.stringify(tables, null, 2));
      console.log('Tables in on-call profile:', tables.length);
      tables.forEach(t => {
        console.log(`  Table ${t.tableIndex} (${t.rows.length} rows):`);
        t.rows.slice(0, 8).forEach(r => console.log('    ', r.join(' | ')));
      });

      const fullText = await page.evaluate(() => document.body.innerText.slice(0, 10000));
      fs.writeFileSync('data/oncall-profile.txt', fullText);
    } else {
      console.log('abdian not found - trying without search filter');
      await page.screenshot({ path: 'screenshots/oncall-no-result.png' });
    }

    // ============================
    // SPRINT POINTS > Individuals > abdian
    // ============================
    console.log('\n--- Sprint Points > Individuals > abdian ---');
    await page.locator('button.tab[data-tab="sprint-points"]').click();
    await page.waitForTimeout(1500);

    await page.locator('[data-sub="sp-individuals-sub"]').click();
    await page.waitForTimeout(1000);

    // Filter RnG Squad 2
    const spRngChip = page.locator('button.sp-chip:has-text("RnG Squad 2")');
    if (await spRngChip.count() > 0) {
      await spRngChip.first().click();
      await page.waitForTimeout(1000);
      console.log('Clicked RnG Squad 2 chip for SP');
    }

    const abdianSP = page.locator('text=abdian.rizki@paper.id').first();
    if (await abdianSP.isVisible()) {
      await abdianSP.click();
      await page.waitForTimeout(2500);
      await page.screenshot({ path: 'screenshots/sprintpoints-profile.png', fullPage: true });
      console.log('[OK] Sprint points profile screenshot');

      const tables = await page.evaluate(() => {
        return Array.from(document.querySelectorAll('table')).map((t, ti) => ({
          tableIndex: ti,
          rows: Array.from(t.querySelectorAll('tr')).map(row =>
            Array.from(row.querySelectorAll('td, th')).map(c => c.textContent.trim())
          ).filter(r => r.length > 0)
        }));
      });
      fs.writeFileSync('data/sp-profile-tables.json', JSON.stringify(tables, null, 2));
      console.log('Tables in SP profile:', tables.length);
      tables.forEach(t => {
        console.log(`  Table ${t.tableIndex} (${t.rows.length} rows):`);
        t.rows.slice(0, 8).forEach(r => console.log('    ', r.join(' | ')));
      });
    }

    console.log('\n=== All done ===');

  } catch (err) {
    console.error('Error:', err.message);
    await page.screenshot({ path: 'screenshots/error-final.png', fullPage: true });
  } finally {
    await browser.close();
  }
}

main();
