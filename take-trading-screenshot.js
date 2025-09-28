const { chromium } = require('playwright');

async function takeScreenshot() {
  // Launch browser
  const browser = await chromium.launch();
  const page = await browser.newPage();

  try {
    // Set viewport to see the full dashboard
    await page.setViewportSize({ width: 1920, height: 1080 });

    // Navigate to your local dashboard
    console.log('Navigating to http://localhost:3004...');
    await page.goto('http://localhost:3004', { waitUntil: 'networkidle' });

    // Wait for initial load
    await page.waitForTimeout(2000);

    // Click on the Trading button to switch to trading page
    console.log('Clicking Trading button...');
    await page.click('button:has-text("Trading")');

    // Wait for the trading page to load
    await page.waitForTimeout(5000);

    // Take screenshot
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `trading-screenshot-${timestamp}.png`;

    await page.screenshot({
      path: filename,
      fullPage: true,
      type: 'png'
    });

    console.log(`Trading page screenshot saved as: ${filename}`);

  } catch (error) {
    console.error('Error taking screenshot:', error.message);
  } finally {
    await browser.close();
  }
}

takeScreenshot();