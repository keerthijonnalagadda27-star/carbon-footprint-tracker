(() => {
  const FACTORS = {
    travel: {
      car: { label: "Car", unit: "km", kg: 0.21 },
      bus: { label: "Bus", unit: "km", kg: 0.089 },
      train: { label: "Train", unit: "km", kg: 0.041 },
      flight: { label: "Flight", unit: "km", kg: 0.255 },
      walk: { label: "Walk", unit: "km", kg: 0 },
      cycle: { label: "Cycle", unit: "km", kg: 0 }
    },
    electricity: {
      grid: { label: "Grid electricity", unit: "kWh", kg: 0.82 }
    },
    food: {
      meat: { label: "Meat-heavy meal", unit: "meals", kg: 3.5 },
      mixed: { label: "Mixed meal", unit: "meals", kg: 1.7 },
      veg: { label: "Vegetarian meal", unit: "meals", kg: 0.8 },
      vegan: { label: "Vegan meal", unit: "meals", kg: 0.5 }
    }
  };

  const KEYS = {
    user: "carbon.user",
    activities: "carbon.activities"
  };

  const config = window.CARBON_CONFIG || { apiUrl: "", defaultThresholdKg: 15 };

  function uid() {
    return crypto.randomUUID ? crypto.randomUUID() : String(Date.now());
  }

  function pad2(n) {
    return String(n).padStart(2, "0");
  }

  function formatLocalDate(d) {
    return `${d.getFullYear()}-${pad2(d.getMonth() + 1)}-${pad2(d.getDate())}`;
  }

  function todayIso() {
    return formatLocalDate(new Date());
  }

  function addDays(iso, delta) {
    const [year, month, day] = iso.split("-").map(Number);
    return formatLocalDate(new Date(year, month - 1, day + delta));
  }

  function loadUser() {
    const saved = JSON.parse(localStorage.getItem(KEYS.user) || "null");
    if (saved) return saved;
    const user = {
      id: uid(),
      name: "",
      email: "",
      thresholdKg: config.defaultThresholdKg
    };
    localStorage.setItem(KEYS.user, JSON.stringify(user));
    return user;
  }

  function saveUser(user) {
    localStorage.setItem(KEYS.user, JSON.stringify(user));
  }

  function loadActivities() {
    return JSON.parse(localStorage.getItem(KEYS.activities) || "[]");
  }

  function saveActivities(items) {
    localStorage.setItem(KEYS.activities, JSON.stringify(items));
  }

  function factorFor(category, type) {
    return (FACTORS[category] && FACTORS[category][type]) || { label: type || "-", unit: "", kg: 0 };
  }

  function estimate(category, type, amount) {
    const factor = factorFor(category, type);
    return Number((Number(amount || 0) * factor.kg).toFixed(2));
  }

  let user = loadUser();
  let activities = loadActivities();

  const els = {
    tabs: document.querySelectorAll(".tab"),
    views: document.querySelectorAll(".view"),
    date: document.getElementById("field-date"),
    category: document.getElementById("field-category"),
    type: document.getElementById("field-type"),
    amount: document.getElementById("field-amount"),
    amountLabel: document.getElementById("amount-label"),
    live: document.getElementById("live-estimate"),
    form: document.getElementById("activity-form"),
    formStatus: document.getElementById("form-status"),
    historyBody: document.getElementById("history-body"),
    historyEmpty: document.getElementById("history-empty"),
    settingsForm: document.getElementById("settings-form"),
    name: document.getElementById("field-name"),
    email: document.getElementById("field-email"),
    threshold: document.getElementById("field-threshold"),
    settingsStatus: document.getElementById("settings-status"),
    modeCaption: document.getElementById("mode-caption"),
    todayKg: document.getElementById("today-kg"),
    weekKg: document.getElementById("week-kg"),
    monthKg: document.getElementById("month-kg"),
    catTravel: document.getElementById("cat-travel"),
    catElectricity: document.getElementById("cat-electricity"),
    catFood: document.getElementById("cat-food"),
    fill: document.getElementById("threshold-fill"),
    caption: document.getElementById("threshold-caption"),
    chart: document.getElementById("week-chart")
  };

  function fillTypes() {
    const category = els.category.value;
    const options = FACTORS[category];
    els.type.innerHTML = Object.entries(options)
      .map(([key, value]) => `<option value="${key}">${value.label}</option>`)
      .join("");
    const first = options[els.type.value];
    const unitLabel =
      category === "travel"
        ? "Distance (km)"
        : category === "electricity"
          ? "Usage (kWh)"
          : "Meals";
    els.amountLabel.textContent = unitLabel;
    updateEstimate();
    return first;
  }

  function updateEstimate() {
    const kg = estimate(els.category.value, els.type.value, els.amount.value);
    els.live.innerHTML = `${kg.toFixed(2)} kg CO<sub>2</sub>`;
  }

  function inRange(date, start, end) {
    return date >= start && date <= end;
  }

  function sum(items) {
    return items.reduce((acc, item) => acc + Number(item.co2Kg), 0);
  }

  function dashboardStats() {
    const today = todayIso();
    const weekStart = addDays(today, -6);
    const monthStart = today.slice(0, 8) + "01";
    const todayItems = activities.filter((item) => item.date === today);
    const weekItems = activities.filter((item) => inRange(item.date, weekStart, today));
    const monthItems = activities.filter((item) => inRange(item.date, monthStart, today));
    return {
      today: sum(todayItems),
      week: sum(weekItems),
      month: sum(monthItems),
      travel: sum(todayItems.filter((item) => item.category === "travel")),
      electricity: sum(todayItems.filter((item) => item.category === "electricity")),
      food: sum(todayItems.filter((item) => item.category === "food")),
      weekSeries: Array.from({ length: 7 }, (_, i) => {
        const date = addDays(weekStart, i);
        return {
          date,
          kg: sum(activities.filter((item) => item.date === date))
        };
      })
    };
  }

  function drawChart(series) {
    const canvas = els.chart;
    const ctx = canvas.getContext("2d");
    const cssWidth = canvas.clientWidth || 640;
    canvas.width = cssWidth * 2;
    canvas.height = 180 * 2;
    ctx.scale(2, 2);
    ctx.clearRect(0, 0, cssWidth, 180);
    const max = Math.max(1, ...series.map((d) => d.kg));
    const gap = 12;
    const barWidth = (cssWidth - gap * (series.length + 1)) / series.length;
    series.forEach((point, i) => {
      const h = (point.kg / max) * 120;
      const x = gap + i * (barWidth + gap);
      const y = 140 - h;
      ctx.fillStyle = "#1f6b45";
      ctx.fillRect(x, y, barWidth, h);
      ctx.fillStyle = "#5c685e";
      ctx.font = "11px IBM Plex Sans, sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(point.date.slice(5), x + barWidth / 2, 158);
      ctx.fillText(point.kg.toFixed(1), x + barWidth / 2, y - 6);
    });
  }

  function renderDashboard() {
    const stats = dashboardStats();
    els.todayKg.textContent = stats.today.toFixed(2);
    els.weekKg.textContent = `${stats.week.toFixed(2)} kg`;
    els.monthKg.textContent = `${stats.month.toFixed(2)} kg`;
    els.catTravel.textContent = `${stats.travel.toFixed(2)} kg`;
    els.catElectricity.textContent = `${stats.electricity.toFixed(2)} kg`;
    els.catFood.textContent = `${stats.food.toFixed(2)} kg`;
    const pct = Math.min(100, (stats.today / user.thresholdKg) * 100);
    els.fill.style.width = `${pct}%`;
    els.fill.classList.toggle("is-over", stats.today > user.thresholdKg);
    els.caption.textContent =
      stats.today > user.thresholdKg
        ? `Over your ${user.thresholdKg} kg daily threshold`
        : `${stats.today.toFixed(2)} of ${user.thresholdKg} kg daily threshold`;
    drawChart(stats.weekSeries);
  }

  function renderHistory() {
    const rows = [...activities].sort((a, b) => (a.date < b.date ? 1 : -1));
    els.historyBody.innerHTML = rows
      .map((item) => {
        const factor = factorFor(item.category, item.type);
        return `<tr>
          <td>${item.date}</td>
          <td>${item.category}</td>
          <td>${factor.label}</td>
          <td>${item.amount} ${factor.unit}</td>
          <td>${Number(item.co2Kg).toFixed(2)} kg</td>
        </tr>`;
      })
      .join("");
    els.historyEmpty.hidden = rows.length > 0;
  }

  function renderSettings() {
    els.name.value = user.name || "Sree Keerthi";
    els.email.value = user.email || "keerthi.24bce8526@vitapstudent.ac.in";
    els.threshold.value = user.thresholdKg;
    els.modeCaption.textContent = config.apiUrl
      ? `AWS API Gateway connected: ${config.apiUrl}`
      : "Local mode: data stays in this browser until the Lambda API URL is set in config.js.";
  }

  function showView(name) {
    els.tabs.forEach((tab) => tab.classList.toggle("is-active", tab.dataset.view === name));
    els.views.forEach((view) =>
      view.classList.toggle("is-visible", view.id === `view-${name}`)
    );
    if (name === "dashboard") renderDashboard();
    if (name === "history") renderHistory();
  }

  function mapActivity(item) {
    return {
      id: item.activityId || item.id,
      date: item.date,
      category: item.category,
      type: item.type,
      amount: Number(item.amount),
      co2Kg: Number(item.co2Kg),
      createdAt: item.createdAt
    };
  }

  async function api(path, options = {}) {
    const response = await fetch(`${config.apiUrl}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {})
      }
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(data.error || data.detail || "Request failed");
    }
    return data;
  }

  async function refreshFromApi() {
    if (!config.apiUrl) return;
    const data = await api(`/activities?userId=${encodeURIComponent(user.id)}`);
    activities = (data.activities || []).map(mapActivity);
    saveActivities(activities);
  }

  async function persistActivity(entry) {
    if (!config.apiUrl) {
      activities.push(entry);
      saveActivities(activities);
      return;
    }
    await api("/activities", {
      method: "POST",
      body: JSON.stringify({
        ...entry,
        userId: user.id,
        thresholdKg: user.thresholdKg,
        email: user.email,
        name: user.name
      })
    });
    await refreshFromApi();
  }

  els.tabs.forEach((tab) =>
    tab.addEventListener("click", () => showView(tab.dataset.view))
  );
  els.category.addEventListener("change", fillTypes);
  els.type.addEventListener("change", updateEstimate);
  els.amount.addEventListener("input", updateEstimate);

  els.form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const category = els.category.value;
    const type = els.type.value;
    const amount = Number(els.amount.value);
    const entry = {
      id: uid(),
      date: els.date.value,
      category,
      type,
      amount,
      co2Kg: estimate(category, type, amount),
      createdAt: new Date().toISOString()
    };
    try {
      await persistActivity(entry);
      els.formStatus.hidden = false;
      els.formStatus.classList.remove("is-error");
      els.formStatus.textContent = `Saved ${entry.co2Kg.toFixed(2)} kg CO2.`;
      els.amount.value = "";
      updateEstimate();
      renderDashboard();
      renderHistory();
    } catch (err) {
      els.formStatus.hidden = false;
      els.formStatus.classList.add("is-error");
      els.formStatus.textContent = err.message;
    }
  });

  els.settingsForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    user = {
      ...user,
      name: els.name.value.trim(),
      email: els.email.value.trim(),
      thresholdKg: Number(els.threshold.value)
    };
    saveUser(user);
    try {
      if (config.apiUrl) {
        await api("/settings", {
          method: "PUT",
          body: JSON.stringify({
            userId: user.id,
            name: user.name,
            email: user.email,
            thresholdKg: user.thresholdKg
          })
        });
      }
      els.settingsStatus.hidden = false;
      els.settingsStatus.classList.remove("is-error");
      els.settingsStatus.textContent = "Settings saved.";
      renderDashboard();
    } catch (err) {
      els.settingsStatus.hidden = false;
      els.settingsStatus.classList.add("is-error");
      els.settingsStatus.textContent = err.message;
    }
  });

  async function start() {
    els.date.value = todayIso();
    fillTypes();
    renderSettings();
    try {
      await refreshFromApi();
    } catch (err) {
      els.modeCaption.textContent = `Could not load AWS data: ${err.message}`;
    }
    renderDashboard();
    renderHistory();
  }

  start();
})();
