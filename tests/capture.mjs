// Clean visual evidence from document top. No app state or style is modified.
import fs from "node:fs/promises";
import path from "node:path";
import { chromium } from "playwright";
const directory = path.resolve(".impeccable/review");
await fs.mkdir(directory, { recursive: true });
const browser = await chromium.launch({ channel: "chrome", headless: true });
try {
  const page = await browser.newPage();
  for (const [name, width, height] of [
    ["desktop", 1440, 1000],
    ["tablet", 768, 1024],
    ["mobile", 390, 844],
    ["small-mobile", 320, 740],
  ]) {
    await page.setViewportSize({ width, height });
    await page.goto(process.env.BASE_URL || "http://127.0.0.1:5000");
    await page.evaluate(() => document.fonts.ready);
    await page.locator(".hero-photo").evaluate((img) => img.decode());
    await page.screenshot({
      path: path.join(directory, name + ".png"),
      animations: "disabled",
    });
    if (name === "desktop" || name === "mobile") {
      await page.screenshot({
        path: path.join(directory, name + "-full.png"),
        fullPage: true,
        animations: "disabled",
      });
      const geometry = await page.evaluate(() =>
        Object.fromEntries(
          ["services", "estimate", "pickup", "faq", "contact"].map((id) => {
            const r = document.getElementById(id).getBoundingClientRect();
            return [
              id,
              {
                x: Math.floor(r.x),
                y: Math.floor(r.y),
                width: Math.ceil(r.width),
                height: Math.ceil(r.height),
              },
            ];
          }),
        ),
      );
      await fs.writeFile(
        path.join(directory, name + "-geometry.json"),
        JSON.stringify(geometry),
      );
    }
  }
} finally {
  await browser.close();
}
