const { chromium } = require('playwright');
const fs = require('fs');

const BASE_URL = 'http://astronauts.paper.private';
const SPRINT_FROM = '2.49';
const SPRINT_TO = '2.60';

async function setSprintRange(page) {
  // Set "From" sprint
  const fromSelects = page.locator('select');
  const count = await fromSelects.count();

  // Find sprint dropdowns by checking options
  for (let i = 0; i < count; i++) {
    const sel = fromSelects.nth(i);
    if (!await sel.isVisible()) continue;
    const opts = await sel.evaluate(el => Array.from(el.options).map(o => o.value));
    if (opts.includes(SPRINT_FROM)) {
      const ph = await sel.evaluate(el => el.querySelector('option:disabled')?.text || '');
      if (ph.includes('From') || i === 0) {
        await sel.selectOption(SPRINT_FROM);
        await page.waitForTimeout(500);
        console.log(`Set From: ${SPRINT_FROM}`);
      } else if (ph.includes('To') || i === 1) {
        await sel.selectOption(SPRINT_TO);
        await page.waitForTimeout(500);
        console.log(`Set To: ${SPRINT_TO}`);
      }
    }
  }

  // Alternative: find From/To selects by placeholder
  const allSelects = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('select')).map((s, i) => ({
      index: i,
      options: Array.from(s.options).map(o => o.value),
      firstOption: s.options[0]?.text
    }));
  });
  console.log('Sprint selects:', JSON.stringify(allSelects));

  // Set From to 2.49 (first sprint select)
  for (const s of allSelects) {
    if (s.options.includes('2.49') && s.options.includes('2.60')) {
      const sel = fromSelects.nth(s.index);
      if (s.firstOption?.includes('From')) {
        await sel.selectOption('2.49');
        console.log(`[From] set to 2.49`);
      } else if (s.firstOption?.includes('To')) {
        await sel.selectOption('2.60');
        console.log(`[To] set to 2.60`);
      }
      await page.waitForTimeout(300);
    }
  }

  await page.waitForTimeout(1000);
}

async function setSprintRangeDirect(page) {
  // Direct approach: find both sprint selects and set them
  const result = await page.evaluate(([from, to]) => {
    const selects = Array.from(document.querySelectorAll('select'));
    let fromSet = false, toSet = false;
    selects.forEach(sel => {
      const opts = Array.from(sel.options).map(o => o.value);
      if (!opts.includes(from)) return;
      const firstText = sel.options[0]?.text || '';
      if (firstText.includes('From') || firstText.includes('…')) {
        if (!fromSet) {
          sel.value = from;
          sel.dispatchEvent(new Event('change'));
          fromSet = true;
          return;
        }
      }
      if (firstText.includes('To') || (fromSet && !toSet)) {
        sel.value = to;
        sel.dispatchEvent(new Event('change'));
        toSet = true;
      }
    });
    return { fromSet, toSet, selectCount: selects.length };
  }, [SPRINT_FROM, SPRINT_TO]);
  console.log('Sprint range set:', result);
  await page.waitForTimeout(1500);
}

async function main() {
  fs.mkdirSync('screenshots', { recursive: true });
  fs.mkdirSync('data', { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1600, height: 1000 });

  try {
    await page.goto(BASE_URL, { waitUntil: 'networkidle', timeout: 15000 });

    // Set sprint range 2.49 → 2.60 globally
    console.log('Setting sprint range 2.49 → 2.60...');
    await setSprintRangeDirect(page);
    await page.screenshot({ path: 'screenshots/00-range-set.png' });

    // ============================
    // CODE HEALTH > Services > Network
    // ============================
    console.log('\n--- Code Health > Services > Network ---');
    await page.locator('button.tab[data-tab="codehealth"]').click();
    await page.waitForTimeout(1000);
    await setSprintRangeDirect(page);  // re-apply after tab switch

    await page.locator('[data-sub="ch-services"]').click();
    await page.waitForTimeout(1500);
    await setSprintRangeDirect(page);

    // Click Network chip
    const allBtns = await page.locator('button').all();
    for (const btn of allBtns) {
      try {
        const txt = (await btn.textContent()).trim();
        const vis = await btn.isVisible();
        if (txt === 'Network' && vis) {
          await btn.click();
          await page.waitForTimeout(1500);
          console.log('Clicked Network BU chip');
          break;
        }
      } catch {}
    }

    await page.screenshot({ path: 'screenshots/ch-services-network.png', fullPage: true });

    const chText = await page.evaluate(() => {
      const codeHealthSection = document.querySelector('#codehealth');
      return codeHealthSection ? codeHealthSection.innerText : document.body.innerText.slice(0, 8000);
    });
    fs.writeFileSync('data/final-ch-services.txt', chText);
    console.log('Code Health Services text saved, length:', chText.length);

    // ============================
    // ON-CALL > Individuals > abdian
    // ============================
    console.log('\n--- On-Call > Individuals ---');
    await page.locator('button.tab[data-tab="oncall"]').click();
    await page.waitForTimeout(1000);
    await setSprintRangeDirect(page);

    await page.locator('[data-sub="oncall-eng-sub"]').click();
    await page.waitForTimeout(1000);

    // Search for abdian using the on-call specific search box
    const searchBox = page.locator('#oncall-search');
    if (await searchBox.count() > 0 && await searchBox.isVisible()) {
      await searchBox.fill('abdian');
      await page.waitForTimeout(1200);
    }

    await page.screenshot({ path: 'screenshots/oncall-search.png' });

    // Click abdian row via JS
    const clicked = await page.evaluate(() => {
      const cells = document.querySelectorAll('td');
      for (const cell of cells) {
        if (cell.textContent.includes('abdian.rizki')) {
          cell.click();
          return true;
        }
      }
      return false;
    });
    console.log('abdian clicked:', clicked);

    if (clicked) {
      await page.waitForTimeout(2500);
      await page.screenshot({ path: 'screenshots/oncall-profile.png', fullPage: true });

      const tables = await page.evaluate(() => {
        return Array.from(document.querySelectorAll('table')).map((t, ti) => ({
          tableIndex: ti,
          rows: Array.from(t.querySelectorAll('tr')).map(row =>
            Array.from(row.querySelectorAll('td, th')).map(c => c.textContent.trim())
          ).filter(r => r.length > 0)
        }));
      });
      fs.writeFileSync('data/final-oncall-tables.json', JSON.stringify(tables, null, 2));
      console.log('On-call tables:', tables.length);
      tables.forEach(t => {
        console.log(`  Table ${t.tableIndex} (${t.rows.length} rows):`);
        t.rows.slice(0, 15).forEach(r => console.log('    ', r.join(' | ')));
      });

      // Close overlay
      await page.keyboard.press('Escape');
      await page.waitForTimeout(500);
    }

    // ============================
    // SPRINT POINTS > Individuals > abdian
    // ============================
    console.log('\n--- Sprint Points > Individuals ---');
    await page.locator('button.tab[data-tab="sprint-points"]').click();
    await page.waitForTimeout(1000);
    await setSprintRangeDirect(page);

    await page.locator('[data-sub="sp-individuals-sub"]').click();
    await page.waitForTimeout(1000);

    // RnG Squad 2 chip
    const spBtns = await page.locator('button').all();
    for (const btn of spBtns) {
      try {
        const txt = (await btn.textContent()).trim();
        const vis = await btn.isVisible();
        if (txt === 'RnG Squad 2' && vis) {
          await btn.click();
          await page.waitForTimeout(800);
          break;
        }
      } catch {}
    }

    // Click abdian
    const spClicked = await page.evaluate(() => {
      const cells = document.querySelectorAll('td');
      for (const cell of cells) {
        if (cell.textContent.includes('abdian.rizki')) {
          cell.click();
          return true;
        }
      }
      return false;
    });
    console.log('abdian SP clicked:', spClicked);

    if (spClicked) {
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
      fs.writeFileSync('data/final-sp-tables.json', JSON.stringify(tables, null, 2));
      console.log('SP tables:', tables.length);
      tables.forEach(t => {
        console.log(`  Table ${t.tableIndex} (${t.rows.length} rows):`);
        t.rows.slice(0, 15).forEach(r => console.log('    ', r.join(' | ')));
      });
    }

    // ============================
    // DEPLOYMENTS > By Squad > RnG Squad 2
    // ============================
    console.log('\n--- Deployments > RnG Squad 2 ---');
    await page.locator('button.tab[data-tab="deployments"]').click();
    await page.waitForTimeout(1000);
    await setSprintRangeDirect(page);

    // Filter RnG Squad 2
    const deplBtns = await page.locator('button').all();
    for (const btn of deplBtns) {
      try {
        const txt = (await btn.textContent()).trim();
        const vis = await btn.isVisible();
        if (txt === 'RnG Squad 2' && vis) {
          await btn.click();
          await page.waitForTimeout(1000);
          console.log('Clicked RnG Squad 2 in Deployments');
          break;
        }
      } catch {}
    }

    await page.screenshot({ path: 'screenshots/deployments-rng2.png', fullPage: true });

    const deplText = await page.evaluate(() => {
      const section = document.querySelector('#deployments');
      return section ? section.innerText.slice(0, 5000) : document.body.innerText.slice(0, 5000);
    });
    fs.writeFileSync('data/final-deployments.txt', deplText);
    console.log('Deployments text saved');
    console.log(deplText.slice(0, 800));

    const deplTables = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('table')).map((t, ti) => ({
        tableIndex: ti,
        rows: Array.from(t.querySelectorAll('tr')).map(row =>
          Array.from(row.querySelectorAll('td, th')).map(c => c.textContent.trim())
        ).filter(r => r.length > 0)
      }));
    });
    fs.writeFileSync('data/final-deployments-tables.json', JSON.stringify(deplTables, null, 2));

    console.log('\n=== Done ===');
    console.log('Files:', fs.readdirSync('data').join(', '));

  } catch (err) {
    console.error('Error:', err.message);
    await page.screenshot({ path: 'screenshots/error.png', fullPage: true });
  } finally {
    await browser.close();
  }
}

main();
