const { chromium } = require('playwright');
const fs = require('fs');

const BASE_URL = 'http://astronauts.paper.private';
const ENGINEER_EMAIL = 'abdian.rizki@paper.id';

async function snap(page, filename, description) {
  await page.waitForTimeout(2000);
  await page.screenshot({ path: `screenshots/${filename}`, fullPage: false });
  console.log(`[OK] ${description} -> ${filename}`);
}

async function extractTable(page) {
  return page.evaluate(() => {
    const rows = document.querySelectorAll('table tr');
    return Array.from(rows).map(row => {
      const cells = row.querySelectorAll('td, th');
      return Array.from(cells).map(c => c.textContent.trim());
    }).filter(r => r.length > 0);
  });
}

async function clickMainTab(page, tabText) {
  await page.locator(`button.tab:has-text("${tabText}")`).click();
  await page.waitForTimeout(1500);
  console.log(`Clicked tab: ${tabText}`);
}

async function clickVisibleChip(page, chipText) {
  const chips = page.locator(`button.chip:has-text("${chipText}"), button:has-text("${chipText}")`);
  const count = await chips.count();
  for (let i = 0; i < count; i++) {
    if (await chips.nth(i).isVisible()) {
      await chips.nth(i).click();
      await page.waitForTimeout(800);
      console.log(`Clicked chip: ${chipText}`);
      return;
    }
  }
  console.log(`Chip not found: ${chipText}`);
}

async function main() {
  fs.mkdirSync('screenshots', { recursive: true });
  fs.mkdirSync('data', { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1600, height: 900 });

  try {
    await page.goto(BASE_URL, { waitUntil: 'networkidle', timeout: 15000 });
    await snap(page, '00-overview.png', 'Overview');

    // --- SPRINT POINTS ---
    console.log('\n--- Sprint Points ---');
    await clickMainTab(page, 'Sprint Points');
    await page.locator('[data-sub="sp-individuals-sub"]').click();
    await page.waitForTimeout(1000);
    await clickVisibleChip(page, 'RnG Squad 2');
    await snap(page, '01-sprintpoints-rng2.png', 'Sprint Points - RnG Squad 2 Individuals');

    // Extract main table
    const spTable = await extractTable(page);
    fs.writeFileSync('data/sprintpoints-table.json', JSON.stringify(spTable, null, 2));

    // Open abdian profile
    const abdianSP = page.locator(`text=${ENGINEER_EMAIL}`).first();
    if (await abdianSP.isVisible()) {
      await abdianSP.click();
      await page.waitForTimeout(2000);
      await snap(page, '02-sprintpoints-profile.png', 'Sprint Points - abdian profile');
      const profileData = await page.evaluate(() => {
        // Get all text from the modal/panel
        const modal = document.querySelector('.modal, .profile-panel, .side-panel, [class*="modal"], [class*="panel"]');
        if (modal) return modal.innerText;
        return document.body.innerText.slice(0, 3000);
      });
      fs.writeFileSync('data/sprintpoints-profile.txt', profileData);
      // Also get table data inside profile
      const profileTable = await extractTable(page);
      fs.writeFileSync('data/sprintpoints-profile-table.json', JSON.stringify(profileTable, null, 2));
      await page.keyboard.press('Escape');
      await page.waitForTimeout(800);
    }

    // --- ON-CALL ---
    console.log('\n--- On-Call ---');
    await clickMainTab(page, 'On-Call');
    await page.locator('[data-sub="oncall-eng-sub"]').click();
    await page.waitForTimeout(1000);
    await clickVisibleChip(page, 'RnG Squad 2');

    // Search for abdian
    const searchInput = page.locator('input[placeholder*="search" i], input[type="search"]').first();
    if (await searchInput.isVisible()) {
      await searchInput.fill('abdi');
      await page.waitForTimeout(1000);
    }

    await snap(page, '03-oncall-rng2.png', 'On-Call - RnG Squad 2 filtered abdian');
    const oncallTable = await extractTable(page);
    fs.writeFileSync('data/oncall-table.json', JSON.stringify(oncallTable, null, 2));

    // Open abdian profile
    const abdianOC = page.locator(`text=${ENGINEER_EMAIL}`).first();
    if (await abdianOC.isVisible()) {
      await abdianOC.click();
      await page.waitForTimeout(2000);
      await snap(page, '04-oncall-profile.png', 'On-Call - abdian profile');
      const profileTable = await extractTable(page);
      fs.writeFileSync('data/oncall-profile-table.json', JSON.stringify(profileTable, null, 2));
      const profileText = await page.evaluate(() => {
        const modal = document.querySelector('.modal, .profile-panel, .side-panel, [class*="modal"], [class*="panel"], [class*="overlay"]');
        if (modal) return modal.innerText;
        return '';
      });
      fs.writeFileSync('data/oncall-profile.txt', profileText);
      await page.keyboard.press('Escape');
      await page.waitForTimeout(800);
    }

    // --- DEPLOYMENTS ---
    console.log('\n--- Deployments ---');
    await clickMainTab(page, 'Deployments');

    // Try squad filter buttons
    const rngDepl = page.locator('button:has-text("RnG Squad 2")');
    const rngDeplCount = await rngDepl.count();
    console.log(`Found ${rngDeplCount} RnG Squad 2 buttons in Deployments`);
    for (let i = 0; i < rngDeplCount; i++) {
      if (await rngDepl.nth(i).isVisible()) {
        await rngDepl.nth(i).click();
        await page.waitForTimeout(1000);
        break;
      }
    }

    // Also check for squad dropdown
    const squadSelect = page.locator('select').first();
    if (await squadSelect.isVisible()) {
      const options = await squadSelect.evaluate(el => Array.from(el.options).map(o => o.text));
      console.log('Dropdown options:', options);
      if (options.some(o => o.includes('RnG Squad 2'))) {
        await squadSelect.selectOption({ label: 'RnG Squad 2' });
        await page.waitForTimeout(1000);
      }
    }

    await snap(page, '05-deployments-rng2.png', 'Deployments - RnG Squad 2');
    const deplTable = await extractTable(page);
    fs.writeFileSync('data/deployments.json', JSON.stringify(deplTable, null, 2));

    // Get full deployments page text
    const deplText = await page.evaluate(() => {
      const main = document.querySelector('main, #deployments, .tab-content');
      return main ? main.innerText : document.body.innerText.slice(0, 5000);
    });
    fs.writeFileSync('data/deployments.txt', deplText);

    // --- CODE HEALTH ---
    console.log('\n--- Code Health ---');
    await clickMainTab(page, 'Code Health');

    // Switch to Services
    const servicesBtnCH = page.locator('button:has-text("Services")').first();
    if (await servicesBtnCH.isVisible()) {
      await servicesBtnCH.click();
      await page.waitForTimeout(1000);
    }

    // Filter Network BU
    const networkChip = page.locator('button:has-text("Network")').first();
    if (await networkChip.isVisible()) {
      await networkChip.click();
      await page.waitForTimeout(1500);
    }

    await snap(page, '06-codehealth-network.png', 'Code Health - Network BU Services');
    const codeTable = await extractTable(page);
    fs.writeFileSync('data/codehealth.json', JSON.stringify(codeTable, null, 2));

    const codeText = await page.evaluate(() => {
      const main = document.querySelector('main, #code-health, .tab-content');
      return main ? main.innerText : document.body.innerText.slice(0, 5000);
    });
    fs.writeFileSync('data/codehealth.txt', codeText);

    console.log('\n=== All data scraped! ===');
    console.log('Screenshots: screenshots/');
    console.log('Data files: data/');
    console.log(fs.readdirSync('screenshots').join(', '));
    console.log(fs.readdirSync('data').join(', '));

  } catch (err) {
    console.error('Error:', err.message);
    await page.screenshot({ path: 'screenshots/error.png', fullPage: true });
  } finally {
    await browser.close();
  }
}

main();
