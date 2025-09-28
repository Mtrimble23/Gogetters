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

    // Wait a bit for any animations to load
    await page.waitForTimeout(3000);

    // Take screenshot
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `dashboard-screenshot-${timestamp}.png`;

    await page.screenshot({
      path: filename,
      fullPage: true,
      type: 'png'
    });

    console.log(`Screenshot saved as: ${filename}`);

  } catch (error) {
    console.error('Error taking screenshot:', error.message);
  } finally {
    await browser.close();
  }
}

takeScreenshot();