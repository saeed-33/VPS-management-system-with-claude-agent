/**
 * مشترك لواجهات Autonomous Remediation. ينسق تحميل projections والأحداث والأزرار الخاصة بالـpolicy/authorization/history، مع بقاء enforcement في Python.
 */
(function () {
    "use strict";

    /**
     * دالة مساعدة text لتنسيق أو تحديث state في واجهة الإدارة.
     */
    const text = (value, fallback = "—") =>
        value === null || value === undefined || value === "" ? fallback : String(value);

    /**
     * دالة مساعدة date لتنسيق أو تحديث state في واجهة الإدارة.
     */
    const date = value => {
        if (!value) return "—";
        const parsed = new Date(value);
        return Number.isNaN(parsed.getTime()) ? text(value) : parsed.toLocaleString();
    };

    /**
     * دالة مساعدة number لتنسيق أو تحديث state في واجهة الإدارة.
     */
    const number = (value, digits = 2) =>
        value === null || value === undefined || value === ""
            ? "—"
            : Number(value).toLocaleString(undefined, {maximumFractionDigits: digits});

    /**
     * دالة مساعدة percent لتنسيق أو تحديث state في واجهة الإدارة.
     */
    const percent = value => value === null || value === undefined
        ? "—"
        : `${(Number(value) * 100).toFixed(1)}%`;

    /**
     * دالة مساعدة badge لتنسيق أو تحديث state في واجهة الإدارة.
     */
    const badge = value => statusBadge(text(value, "unknown"));

    /**
     * دالة مساعدة showEmpty لتنسيق أو تحديث state في واجهة الإدارة.
     */
    const showEmpty = (node, message) => {
        node.innerHTML = `<div class="empty-state"><h3>${escapeHtml(message)}</h3></div>`;
    };

    /**
     * دالة مساعدة showError لتنسيق أو تحديث state في واجهة الإدارة.
     */
    const showError = (node, error) => {
        node.innerHTML = `<div class="empty-state"><h3>Unable to load data</h3><p>${escapeHtml(error.message || "Request failed.")}</p></div>`;
    };

    /**
     * دالة مساعدة confirmAction لتنسيق أو تحديث state في واجهة الإدارة.
     */
    const confirmAction = (message, operation) => {
        if (!window.confirm(message)) return Promise.resolve(false);
        return operation().then(() => true);
    };

    window.AutonomousUI = {text, date, number, percent, badge, showEmpty, showError, confirmAction};
})();
