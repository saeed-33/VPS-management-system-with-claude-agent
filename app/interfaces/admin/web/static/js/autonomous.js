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
        return Number.isNaN(parsed.getTime()) ? text(value) : parsed.toLocaleString("ar");
    };

    /**
     * دالة مساعدة number لتنسيق أو تحديث state في واجهة الإدارة.
     */
    const number = (value, digits = 2) =>
        value === null || value === undefined || value === ""
            ? "—"
            : Number(value).toLocaleString("ar", {maximumFractionDigits: digits});

    /**
     * دالة مساعدة percent لتنسيق أو تحديث state في واجهة الإدارة.
     */
    const percent = value => value === null || value === undefined
        ? "—"
        : `${(Number(value) * 100).toFixed(1)}%`;

    const labels = {
        start_service: "بدء الخدمة",
        stop_service: "إيقاف الخدمة",
        restart_service: "إعادة تشغيل الخدمة",
        reload_service: "إعادة تحميل الخدمة",
        clear_cache: "مسح الذاكرة المؤقتة",
        rotate_logs: "تدوير السجلات",
        low: "منخفض",
        medium: "متوسط",
        high: "عالٍ",
        critical: "حرج",
        eligible_for_policy_review: "مؤهل لمراجعة السياسة",
        insufficient_verified_successes: "نجاحات موثقة غير كافية",
        failure_rate_too_high: "معدل الفشل مرتفع",
        rollback_failure_rate_too_high: "معدل فشل التراجع مرتفع",
        sandbox_required: "يتطلب بيئة اختبار",
        rollback_required: "يتطلب تراجعًا",
        tripped: "مفعّل بسبب التعثر",
        not_suspended: "غير موقوف",
        pending: "قيد الانتظار",
        approved: "تمت الموافقة",
        rejected: "مرفوض",
        expired: "منتهي الصلاحية",
        consumed: "مستهلك",
        issued: "صادر",
        executed: "نُفذ",
        failed: "فشل",
        passed: "اجتاز التحقق",
        review: "بحاجة إلى مراجعة",
        eligible: "مؤهل"
    };

    const label = (value, fallback = "غير معروف") => {
        if (value === null || value === undefined || value === "") return fallback;
        return labels[value] || fallback;
    };

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
        node.innerHTML = `<div class="empty-state"><h3>تعذر تحميل البيانات</h3><p>${escapeHtml(error.message || "فشل الطلب.")}</p></div>`;
    };

    const structured = value => {
        if (value === null || value === undefined || value === "") {
            return "<span class=\"muted-text\">لا توجد بيانات</span>";
        }

        if (Array.isArray(value)) {
            if (!value.length) return "<span class=\"muted-text\">لا توجد عناصر</span>";
            return `<div class="structured-list">${value.map(item => `<div class="structured-list-item">${structured(item)}</div>`).join("")}</div>`;
        }

        if (typeof value === "object") {
            const entries = Object.entries(value);
            if (!entries.length) return "<span class=\"muted-text\">لا توجد بيانات</span>";
            return `<div class="structured-data-grid">${entries.map(([key, item]) => `<div class="structured-data-item"><strong>${escapeHtml(key)}</strong><span>${structured(item)}</span></div>`).join("")}</div>`;
        }

        if (typeof value === "boolean") return value ? "نعم" : "لا";
        return escapeHtml(String(value));
    };

    const additionalDetails = (items, label = "تفاصيل إضافية") => {
        const rows = (items || []).map(([title, value]) => `<div class="admin-kv"><strong>${escapeHtml(title)}</strong><span>${structured(value)}</span></div>`).join("");
        return `<details class="additional-details"><summary class="button button-secondary button-sm">${escapeHtml(label)}</summary><div class="additional-details-body"><div class="admin-kv-grid">${rows || `<p class="muted-text">لا توجد تفاصيل.</p>`}</div></div></details>`;
    };

    /**
     * دالة مساعدة confirmAction لتنسيق أو تحديث state في واجهة الإدارة.
     */
    const confirmAction = (message, operation) => {
        if (!window.confirm(message)) return Promise.resolve(false);
        return operation().then(() => true);
    };

    window.AutonomousUI = {text, date, number, percent, label, badge, showEmpty, showError, confirmAction, structured, additionalDetails};
})();
