const { chromium } = require('playwright');

async function testDashboardInteractions() {
  const browser = await chromium.launch({ headless: false }); // Set to true for headless
  const page = await browser.newPage();

  try {
    await page.setViewportSize({ width: 1920, height: 1080 });
    console.log('Navigating to dashboard...');
    await page.goto('http://localhost:3005', { waitUntil: 'networkidle' });

    // Wait for the page to load
    await page.waitForTimeout(3000);

    // Take initial screenshot
    await page.screenshot({ path: 'interaction-test-1-initial.png', fullPage: true });
    console.log('Initial screenshot taken');

    // Test clicking different stock buttons
    const stocks = ['Apple', 'Amazon', 'Google', 'Meta', 'NVIDIA'];

    for (let i = 0; i < stocks.length; i++) {
      const stock = stocks[i];
      console.log(`Clicking on ${stock}...`);

      // Click the stock button
      await page.click(`text=${stock}`);

      // Wait for any animations/changes
      await page.waitForTimeout(2000);

      // Take screenshot after clicking
      await page.screenshot({
        path: `interaction-test-${i + 2}-${stock.toLowerCase()}.png`,
        fullPage: true
      });

      console.log(`Screenshot taken for ${stock}`);
    }

    // Test clicking the Apply button
    console.log('Testing Apply button...');
    await page.fill('input[placeholder="Enter risk score (0-100)"]', '85');
    await page.click('text=Apply');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'interaction-test-apply.png', fullPage: true });

    console.log('All interaction tests completed!');

  } catch (error) {
    console.error('Error during interaction testing:', error);
  } finally {
    await browser.close();
  }
}

testDashboardInteractions();