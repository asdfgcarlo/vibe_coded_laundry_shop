// Integer centavos keep PHP estimates consistent with server-side Decimal math.
export function calculateEstimate(rate, rawWeight) {
  const text = String(rawWeight).trim();
  if (!/^\d{1,3}(?:\.\d)?$/.test(text)) return null;
  const weight = Number(text);
  const cents = Math.round(Number(rate) * 100);
  if (
    !Number.isFinite(weight) ||
    weight < 0.5 ||
    weight > 100 ||
    !Number.isFinite(cents) ||
    cents <= 0
  )
    return null;
  return Math.round((cents * Math.round(weight * 10)) / 10) / 100;
}

export const pesos = new Intl.NumberFormat("en-PH", {
  style: "currency",
  currency: "PHP",
});
