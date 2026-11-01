import { calculateEstimate, pesos } from "./calculator.js";

const menu = document.querySelector(".menu-toggle");
const nav = document.querySelector("#navigation");
if (menu && nav) {
  menu.hidden = false;
  nav.dataset.enhanced = "true";
  const closeMenu = () => menu.setAttribute("aria-expanded", "false");
  menu.addEventListener("click", () =>
    menu.setAttribute(
      "aria-expanded",
      String(menu.getAttribute("aria-expanded") !== "true"),
    ),
  );
  nav.addEventListener("click", (event) => {
    if (event.target.closest("a")) closeMenu();
  });
  document.addEventListener("keydown", (event) => {
    if (
      event.key === "Escape" &&
      menu.getAttribute("aria-expanded") === "true"
    ) {
      closeMenu();
      menu.focus();
    }
  });
  document.addEventListener("click", (event) => {
    if (!event.target.closest(".header-inner")) closeMenu();
  });
}

const calculator = document.querySelector("#calculator");
const pickupForm = document.querySelector("#pickup-form");
if (calculator) {
  const service = calculator.querySelector("#calc-service");
  const weight = calculator.querySelector("#calc-weight");
  const total = calculator.querySelector("#calc-total");
  const breakdown = calculator.querySelector("#calc-breakdown");
  const error = calculator.querySelector("#calc-error");
  const useEstimate = calculator.querySelector("#use-estimate");
  const update = () => {
    const rate = service.selectedOptions[0].dataset.rate;
    const estimate = calculateEstimate(rate, weight.value);
    const valid = estimate !== null;
    total.textContent = valid ? pesos.format(estimate) : "—";
    breakdown.textContent = valid
      ? `${Number(weight.value)} kg × ${pesos.format(rate)}/kg`
      : "Enter a valid weight to see an estimate";
    error.hidden = valid;
    error.textContent = valid
      ? ""
      : "Use a weight from 0.5 to 100 kg, with at most one decimal place.";
    weight.setAttribute("aria-invalid", String(!valid));
    useEstimate.setAttribute("aria-disabled", String(!valid));
    calculator.querySelector("#weight-minus").disabled =
      valid && Number(weight.value) <= 0.5;
    calculator.querySelector("#weight-plus").disabled =
      valid && Number(weight.value) >= 100;
  };
  calculator.addEventListener("submit", (event) => event.preventDefault());
  service.addEventListener("change", update);
  weight.addEventListener("input", update);
  for (const [id, delta] of [
    ["weight-minus", -0.5],
    ["weight-plus", 0.5],
  ]) {
    calculator.querySelector(`#${id}`).addEventListener("click", () => {
      const value = Number(weight.value);
      weight.value = Math.min(
        100,
        Math.max(0.5, (Number.isFinite(value) ? value : 5) + delta),
      ).toFixed(1);
      update();
    });
  }
  useEstimate.addEventListener("click", (event) => {
    if (useEstimate.getAttribute("aria-disabled") === "true") {
      event.preventDefault();
      weight.focus();
      return;
    }
    if (pickupForm) {
      pickupForm.elements.service.value = service.value;
      pickupForm.elements.weight.value = weight.value;
      pickupForm.elements.service.dispatchEvent(new Event("change"));
      pickupForm.elements.weight.dispatchEvent(new Event("input"));
    }
  });
  update();
}

document.querySelectorAll("[data-service]").forEach((link) =>
  link.addEventListener("click", () => {
    if (pickupForm) {
      pickupForm.elements.service.value = link.dataset.service;
      pickupForm.elements.service.dispatchEvent(new Event("change"));
    }
  }),
);

if (pickupForm) {
  pickupForm.noValidate = true;
  const status = document.querySelector("#form-status");
  const submit = pickupForm.querySelector('[type="submit"]');
  const buttonLabel = submit.querySelector(".button-label");
  let busy = false;
  const validate = (field) => {
    const value = field.value.trim();
    switch (field.name) {
      case "name":
        return value.length >= 2 && value.length <= 100
          ? ""
          : "Enter your full name (2–100 characters).";
      case "phone":
        return /^(?:09\d{9}|\+639\d{9}|639\d{9})$/.test(
          value.replace(/[\s()\-]/g, ""),
        )
          ? ""
          : "Enter a Philippine mobile number, such as 0917 123 4567.";
      case "address":
        return value.length >= 10 && value.length <= 500
          ? ""
          : "Enter your complete pickup address (10–500 characters).";
      case "service":
        return ["wash-fold", "ironing", "bedding"].includes(value)
          ? ""
          : "Choose a laundry service.";
      case "weight":
        return calculateEstimate(1, value) !== null
          ? ""
          : "Enter a weight from 0.5 to 100 kg, with at most one decimal place.";
      case "date":
        return /^\d{4}-\d{2}-\d{2}$/.test(value) &&
          value >= field.min &&
          value <= field.max &&
          field.validity.valid
          ? ""
          : "Choose a date from tomorrow through the next 30 days (Philippine time).";
      case "time":
        return ["morning", "afternoon", "late-afternoon"].includes(value)
          ? ""
          : "Choose a preferred pickup time.";
      case "instructions":
        return value.length <= 1000
          ? ""
          : "Keep instructions within 1,000 characters.";
      default:
        return "";
    }
  };
  const showFieldError = (field, message) => {
    const target = document.querySelector(`[data-error-for="${field.name}"]`);
    if (!target) return;
    target.textContent = message;
    target.hidden = !message;
    field.setAttribute("aria-invalid", String(Boolean(message)));
  };
  const fields = [
    ...pickupForm.querySelectorAll(
      'input:not([type="hidden"]), select, textarea',
    ),
  ];
  fields.forEach((field) => {
    field.addEventListener("blur", () =>
      showFieldError(field, validate(field)),
    );
    field.addEventListener(
      field.tagName === "SELECT" ? "change" : "input",
      () => {
        if (field.getAttribute("aria-invalid") === "true")
          showFieldError(field, validate(field));
      },
    );
    if (
      document
        .querySelector(`[data-error-for="${field.name}"]`)
        ?.textContent.trim()
    )
      field.setAttribute("aria-invalid", "true");
  });

  pickupForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (busy) return;
    let firstInvalid;
    fields.forEach((field) => {
      const error = validate(field);
      showFieldError(field, error);
      if (error && !firstInvalid) firstInvalid = field;
    });
    if (firstInvalid) {
      status.textContent =
        "Please check the highlighted fields and submit again.";
      status.hidden = false;
      firstInvalid.focus();
      return;
    }
    busy = true;
    submit.disabled = true;
    pickupForm.setAttribute("aria-busy", "true");
    submit.querySelector(".spinner").hidden = false;
    buttonLabel.textContent = "Saving your request…";
    status.hidden = true;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 20000);
    try {
      const response = await fetch(pickupForm.action, {
        method: "POST",
        body: new FormData(pickupForm),
        headers: { Accept: "application/json" },
        signal: controller.signal,
      });
      const result = await response.json();
      if (!response.ok || result.ok !== true) {
        for (const [name, message] of Object.entries(result.errors || {})) {
          if (pickupForm.elements[name])
            showFieldError(pickupForm.elements[name], message);
        }
        throw new Error(
          result.message ||
            "We couldn’t confirm your request. Please try again.",
        );
      }
      if (!/^DINA-[A-F0-9]{12}$/.test(result.reference))
        throw new Error(
          "The confirmation was incomplete. Retry this form to retrieve your saved request reference.",
        );
      document.querySelector("#booking-reference").textContent =
        result.reference;
      document.querySelector("#pickup-fields").hidden = true;
      const success = document.querySelector("#booking-success");
      success.hidden = false;
      success.focus();
    } catch (error) {
      status.textContent =
        error.name === "AbortError" || error instanceof TypeError
          ? "We couldn’t confirm the connection. Your details are still here. Retry this form; a request already saved will not be duplicated."
          : error.message;
      status.hidden = false;
      status.focus();
    } finally {
      clearTimeout(timeout);
      busy = false;
      submit.disabled = false;
      pickupForm.removeAttribute("aria-busy");
      submit.querySelector(".spinner").hidden = true;
      buttonLabel.textContent = "Request my pickup";
    }
  });
  if (pickupForm.dataset.serverError) status.focus();
}
