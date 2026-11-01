import assert from "node:assert/strict";
import fs from "node:fs/promises";
import path from "node:path";
import { chromium } from "playwright";
import AxeBuilder from "@axe-core/playwright";

const base = process.env.BASE_URL || "http://127.0.0.1:5000";
const evidence = path.resolve(process.env.EVIDENCE_DIR || ".impeccable/review");
await fs.mkdir(evidence, { recursive: true });
const browser = await chromium.launch({
  channel: process.env.BROWSER_CHANNEL || "chrome",
  headless: true,
});
const report = { base, viewports: [], checks: [] };
try {
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1000 },
  });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (message) => {
    if (
      message.type() === "error" &&
      !message.location().url.endsWith("/pickup-requests")
    )
      errors.push(message.text());
  });
  assert.equal((await page.goto(base)).status(), 200);
  await page.evaluate(() => document.fonts.ready);
  await page.locator(".hero-photo").evaluate((img) => img.decode());
  for (const [name, width, height] of [
    ["desktop", 1440, 1000],
    ["tablet", 768, 1024],
    ["mobile", 390, 844],
    ["small-mobile", 320, 740],
  ]) {
    await page.setViewportSize({ width, height });
    await page.evaluate(() => window.scrollTo({ top: 0, behavior: "instant" }));
    await page.screenshot({
      path: path.join(evidence, `${name}.png`),
      animations: "disabled",
    });
    const layout = await page.evaluate(() => ({
      inner: innerWidth,
      scroll: document.documentElement.scrollWidth,
      title: document.querySelector("h1").textContent,
    }));
    assert.ok(
      layout.scroll <= layout.inner,
      `Horizontal overflow at ${width}px: ${layout.scroll}`,
    );
    report.viewports.push({ name, width, height, overflow: false });
  }
  // Mobile navigation, Escape, and calculator-to-form handoff.
  await page.setViewportSize({ width: 390, height: 844 });
  await page.getByRole("button", { name: "Menu", exact: true }).click();
  assert.equal(
    await page.locator(".menu-toggle").getAttribute("aria-expanded"),
    "true",
  );
  await page.keyboard.press("Escape");
  assert.equal(
    await page.locator(".menu-toggle").getAttribute("aria-expanded"),
    "false",
  );
  await page.locator("#calc-service").selectOption("ironing");
  await page.locator("#calc-weight").fill("6.5");
  assert.match(await page.locator("#calc-total").textContent(), /520\.00/);
  await page.locator("#weight-plus").click();
  assert.match(await page.locator("#calc-total").textContent(), /560\.00/);
  await page.locator("#calc-weight").fill("0");
  assert.equal(
    await page.locator("#use-estimate").getAttribute("aria-disabled"),
    "true",
  );
  await page.locator("#calc-weight").fill("6.5");
  await page.locator("#use-estimate").click();
  assert.equal(await page.locator("#service").inputValue(), "ironing");
  assert.equal(await page.locator("#weight").inputValue(), "6.5");
  await page
    .locator("#pickup")
    .screenshot({
      path: path.join(evidence, "mobile-pickup.png"),
      animations: "disabled",
    });
  report.checks.push(
    "mobile menu / Escape",
    "calculator / invalid weight / estimate handoff",
  );

  await page.locator("#pickup-form [type=submit]").click();
  assert.equal(
    await page.locator("#name").getAttribute("aria-invalid"),
    "true",
  );
  assert.equal(
    await page.locator("#name").evaluate((el) => el === document.activeElement),
    true,
  );
  await page.locator("#name").fill("Browser Test Customer");
  await page.locator("#phone").fill("0917 123 4567");
  await page
    .locator("#address")
    .fill("12 Test Street, Test Barangay, Test City");
  await page
    .locator("#date")
    .fill(await page.locator("#date").getAttribute("min"));
  await page.locator("#time").selectOption("morning");
  const responsePromise = page.waitForResponse((response) =>
    response.url().endsWith("/pickup-requests"),
  );
  await page.locator("#pickup-form [type=submit]").click();
  const response = await responsePromise;
  const result = await response.json();
  if (process.env.EXPECT_LIVE === "1") {
    assert.equal(response.status(), 201);
    assert.match(result.reference, /^DINA-[A-F0-9]{12}$/);
    await page.locator("#booking-success").waitFor({ state: "visible" });
    assert.equal(
      await page.locator("#booking-reference").textContent(),
      result.reference,
    );
    await page
      .locator("#pickup-form")
      .screenshot({
        path: path.join(evidence, "booking-success.png"),
        animations: "disabled",
      });
    report.checks.push("live browser booking saved / confirmation reference");
  } else {
    assert.equal(response.status(), 503);
    assert.equal(result.ok, false);
    await page.getByText(/This is a preview\. Pickup requests/).waitFor();
    assert.equal(
      await page.locator("#name").inputValue(),
      "Browser Test Customer",
    );
    assert.equal(await page.locator("#booking-success").isVisible(), false);
    report.checks.push(
      "demo submit is blocked / data retained / no false success",
    );
  }
  report.checks.push("client validation / first error focus");

  await page.goto(base);
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page
    .locator("#estimate")
    .screenshot({
      path: path.join(evidence, "desktop-estimate.png"),
      animations: "disabled",
    });
  await page
    .locator("#pickup")
    .screenshot({
      path: path.join(evidence, "desktop-pickup.png"),
      animations: "disabled",
    });
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: "instant" }));
  await page.screenshot({
    path: path.join(evidence, "desktop-full.png"),
    fullPage: true,
    animations: "disabled",
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: "instant" }));
  await page.screenshot({
    path: path.join(evidence, "mobile-full.png"),
    fullPage: true,
    animations: "disabled",
  });
  const accessibility = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
    .analyze();
  report.accessibility = accessibility.violations.map((v) => ({
    id: v.id,
    impact: v.impact,
    description: v.description,
    nodes: v.nodes.map((n) => n.target),
  }));
  assert.equal(
    report.accessibility.length,
    0,
    JSON.stringify(report.accessibility, null, 2),
  );
  await page.emulateMedia({ reducedMotion: "reduce" });
  assert.equal(
    await page
      .locator(".laundry-tag")
      .evaluate((el) => getComputedStyle(el).animationName),
    "none",
  );
  report.checks.push("WCAG A/AA automated scan", "reduced motion");
  assert.deepEqual(errors, [], `Browser errors: ${errors.join("\n")}`);
  report.checks.push("no browser console errors or missing assets");
  await context.close();
  // A form submitted without JavaScript receives meaningful server errors.
  const noJS = await browser.newContext({ javaScriptEnabled: false });
  const noJSPage = await noJS.newPage();
  await noJSPage.goto(base);
  assert.equal(await noJSPage.locator("#navigation").isVisible(), true);
  await noJSPage.locator("#name").fill("No JavaScript Test");
  await noJSPage.locator("#phone").fill("invalid-phone");
  await noJSPage
    .locator("#address")
    .fill("12 Test Street, Test Barangay, Test City");
  await noJSPage.locator("#service").selectOption("bedding");
  await noJSPage.locator("#weight").fill("3");
  await noJSPage
    .locator("#date")
    .fill(await noJSPage.locator("#date").getAttribute("min"));
  await noJSPage.locator("#time").selectOption("afternoon");
  await Promise.all([
    noJSPage.waitForNavigation(),
    noJSPage.locator("#pickup-form [type=submit]").click(),
  ]);
  assert.equal(await noJSPage.locator("#phone-error").isVisible(), true);
  report.checks.push(
    "no JavaScript / server validation / accessible navigation",
  );
  await noJS.close();
  console.log(JSON.stringify(report, null, 2));
} finally {
  await fs.writeFile(
    path.join(evidence, "browser-report.json"),
    JSON.stringify(report, null, 2),
  );
  await browser.close();
}
