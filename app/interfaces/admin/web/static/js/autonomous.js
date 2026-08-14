(function () {
    "use strict";

    const text = (value, fallback = "—") =>
        value === null || value === undefined || value === "" ? fallback : String(value);

    const date = value => {
        if (!value) return "—";
        const parsed = new Date(value);
        return Number.isNaN(parsed.getTime()) ? text(value) : parsed.toLocaleString();
    };

    const number = (value, digits = 2) =>
        value === null || value === undefined || value === ""
            ? "—"
            : Number(value).toLocaleString(undefined, {maximumFractionDigits: digits});

    const percent = value => value === null || value === undefined
        ? "—"
        : `${(Number(value) * 100).toFixed(1)}%`;

    const badge = value => statusBadge(text(value, "unknown"));

    const showEmpty = (node, message) => {
        node.innerHTML = `<div class="empty-state"><h3>${escapeHtml(message)}</h3></div>`;
    };

    const showError = (node, error) => {
        node.innerHTML = `<div class="empty-state"><h3>Unable to load data</h3><p>${escapeHtml(error.message || "Request failed.")}</p></div>`;
    };

    const confirmAction = (message, operation) => {
        if (!window.confirm(message)) return Promise.resolve(false);
        return operation().then(() => true);
    };

    window.AutonomousUI = {text, date, number, percent, badge, showEmpty, showError, confirmAction};
})();
