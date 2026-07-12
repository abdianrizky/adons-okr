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

    // Click Code Health main tab
    await page.locator('button.tab:has-text("Code Health")').click();
    await page.waitForTimeout(2000);

    await page.screenshot({ path: 'screenshots/ch-01-main.png' });

    // Log all visible buttons in code health section
    const allButtons = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('button')).map(b => ({
        text: b.textContent.trim(),
        class: b.className,
        dataSub: b.dataset.sub,
        dataTab: b.dataset.tab,
        id: b.id,
        visible: b.offsetParent !== null
      })).filter(b => b.visible);
    });
    console.log('Visible buttons on Code Health page:');
    allButtons.forEach(b => console.log(JSON.stringify(b)));

    // Look for "Services" sub-button within code health (not main tab)
    // Try clicking sub-tabs with data-sub
    const subBtns = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('[data-sub]')).map(b => ({
        text: b.textContent.trim(),
        dataSub: b.dataset.sub,
        visible: b.offsetParent !== null
      }));
    });
    console.log('\nAll data-sub elements:', JSON.stringify(subBtns, null, 2));

    // Try the "Services" sub-tab via data-sub
    const chServicesBtn = page.locator('[data-sub="ch-services-sub"], [data-sub="codehealth-services-sub"], [data-sub*="service"]').first();
    if (await chServicesBtn.count() > 0) {
      await chServicesBtn.click();
      await page.waitForTimeout(1500);
      console.log('Clicked services sub-tab via data-sub');
    } else {
      // Try by text, but only visible buttons that aren't main tabs
      const servicesBtns = page.locator('button:not(.tab):has-text("Services"), .sub-tab:has-text("Services")');
      if (await servicesBtns.count() > 0) {
        await servicesBtns.first().click();
        await page.waitForTimeout(1500);
        console.log('Clicked Services via sub-tab selector');
      } else {
        // Try by tab class that's visible in code health context
        console.log('Trying to click By BU / Services toggle...');
        const toggleBtns = page.locator('.view-toggle button, .sub-tabs button, .code-health-nav button');
        console.log('Toggle buttons found:', await toggleBtns.count());
      }
    }

    await page.screenshot({ path: 'screenshots/ch-02-after-services-click.png' });

    // Filter by Network
    const networkBtns = page.locator('button:has-text("Network"):not(.tab)');
    const networkCount = await networkBtns.count();
    console.log('\nNetwork buttons (non-tab):', networkCount);
    for (let i = 0; i < networkCount; i++) {
      const btn = networkBtns.nth(i);
      const isVisible = await btn.isVisible();
      const text = await btn.textContent();
      console.log(`  [${i}] "${text}" visible:${isVisible}`);
    }

    if (networkCount > 0) {
      for (let i = 0; i < networkCount; i++) {
        if (await networkBtns.nth(i).isVisible()) {
          await networkBtns.nth(i).click();
          await page.waitForTimeout(1500);
          console.log('Clicked Network filter');
          break;
        }
      }
    }

    await page.screenshot({ path: 'screenshots/ch-03-network-filter.png', fullPage: true });

    // Extract whatever table is visible
    const tableData = await page.evaluate(() => {
      const rows = document.querySelectorAll('table tr');
      return Array.from(rows).map(row => {
        const cells = row.querySelectorAll('td, th');
        return Array.from(cells).map(c => c.textContent.trim());
      }).filter(r => r.length > 0);
    });

    console.log('\nTable rows found:', tableData.length);
    tableData.slice(0, 15).forEach(row => console.log(' ', row.join(' | ')));

    fs.writeFileSync('data/codehealth-network-services.json', JSON.stringify(tableData, null, 2));

    // Also capture the full page text
    const pageText = await page.evaluate(() => document.body.innerText.slice(0, 8000));
    fs.writeFileSync('data/codehealth-full-page.txt', pageText);
    console.log('\nFull page text saved');

    // ---- ON-CALL individual profile with fresh approach ----
    console.log('\n--- On-Call profile (fresh approach) ---');
    await page.locator('button.tab:has-text("On-Call")').click();
    await page.waitForTimeout(1500);

    // Check what sub-tabs are visible
    const oncallSubBtns = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('[data-sub]')).filter(b => b.offsetParent !== null).map(b => ({
        text: b.textContent.trim(),
        dataSub: b.dataset.sub,
        class: b.className
      }));
    });
    console.log('On-call sub-tabs:', JSON.stringify(oncallSubBtns, null, 2));

    // Click individuals
    const indvBtn = page.locator('[data-sub="oncall-eng-sub"]');
    if (await indvBtn.count() > 0) {
      await indvBtn.click();
      await page.waitForTimeout(1000);
      console.log('Clicked oncall-eng-sub');
    }

    // DON'T filter by squad - show all engineers, then search
    // Search for abdian
    const searchBoxes = page.locator('input[type="search"], input[placeholder*="search" i], input[placeholder*="engineer" i]');
    const searchCount = await searchBoxes.count();
    console.log('Search boxes found:', searchCount);
    for (let i = 0; i < searchCount; i++) {
      const box = searchBoxes.nth(i);
      if (await box.isVisible()) {
        await box.fill('abdian');
        await page.waitForTimeout(1000);
        console.log('Filled search box with "abdian"');
        break;
      }
    }

    await page.screenshot({ path: 'screenshots/ch-04-oncall-search.png' });

    // Now find abdian link
    const abdianLinks = page.locator('text=abdian.rizki@paper.id');
    const abdianCount = await abdianLinks.count();
    console.log('abdian links found:', abdianCount);

    if (abdianCount > 0) {
      await abdianLinks.first().click();
      await page.waitForTimeout(2500);
      await page.screenshot({ path: 'screenshots/ch-05-oncall-profile.png', fullPage: true });
      console.log('[OK] On-call profile screenshot captured');

      // Extract profile data
      const profileText = await page.evaluate(() => document.body.innerText);
      fs.writeFileSync('data/oncall-profile-full.txt', profileText);

      const tables = await page.evaluate(() => {
        return Array.from(document.querySelectorAll('table')).map(t => {
          const rows = t.querySelectorAll('tr');
          return Array.from(rows).map(row => {
            const cells = row.querySelectorAll('td, th');
            return Array.from(cells).map(c => c.textContent.trim());
          }).filter(r => r.length > 0);
        });
      });
      fs.writeFileSync('data/oncall-profile-tables.json', JSON.stringify(tables, null, 2));
      console.log('Tables found:', tables.length);
      tables.forEach((t, i) => {
        console.log(`Table ${i} (${t.length} rows):`);
        t.slice(0, 5).forEach(r => console.log('  ', r.join(' | ')));
      });
    }

    console.log('\n=== Done ===');

  } catch (err) {
    console.error('Error:', err.message);
    await page.screenshot({ path: 'screenshots/error-ch.png', fullPage: true });
  } finally {
    await browser.close();
  }
}

main();
