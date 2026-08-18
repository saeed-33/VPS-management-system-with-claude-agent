/**
 * مشترك بين صفحات Admin Web. يدير permission visibility، theme/navigation، تنسيق القيم وطلبات API. الحالة الأساسية في DOM وsession/browser state؛ لا يمنح الصلاحية بل يعكس قرار الخادم.
 */
console.log("تم تحميل واجهة الإدارة المشتركة");

const adminContext =
    window.ADMIN_CONTEXT || {
        permissions: []
    };

/**
 * ينفذ خطوة واجهة باسم hasAdminPermission ضمن صفحة Admin Web.
 * يقرأ state من DOM أو API ويحدث العرض؛ الفشل يظهر للمستخدم أو يمرر للـcaller.
 */
function hasAdminPermission(permission) {
    return (adminContext.permissions || []).includes(permission);
}

/**
 * ينفذ خطوة واجهة باسم applyPermissionVisibility ضمن صفحة Admin Web.
 * يقرأ state من DOM أو API ويحدث العرض؛ الفشل يظهر للمستخدم أو يمرر للـcaller.
 */
function applyPermissionVisibility() {
    document
        .querySelectorAll("[data-required-permission]")
        .forEach(element => {
            if (!hasAdminPermission(element.dataset.requiredPermission)) {
                element.hidden = true;
                element.setAttribute("aria-hidden", "true");
            }
        });

    const dynamicPermissionSelectors = [
        ["[onclick^=\"openEditServerModal\"]", "server.write"],
        ["[onclick^=\"toggleMonitoring\"]", "monitoring.control"],
        ["[onclick^=\"testServer\"]", "monitoring.control"],
        ["[onclick^=\"deleteServer\"]", "server.write"],
        ["[onclick^=\"openEditCommandModal\"]", "command.write"],
        ["[onclick^=\"toggleCommand\"]", "command.write"],
        ["[onclick^=\"deleteCommand\"]", "command.write"],
        ["[onclick^=\"toggleProfileStatus\"]", "profile.write"],
        ["[onclick^=\"deleteProfile\"]", "profile.write"],
        ["[onclick^=\"saveAssignment\"]", "profile.write"],
        ["[onclick^=\"toggleAssignment\"]", "profile.write"],
        ["[onclick^=\"removeCommandFromProfile\"]", "profile.write"],
        ["[onchange^=\"assignProfileToServer\"]", "server.write"],
        ["[onclick^=\"editSource\"]", "knowledge.write"],
        ["[onclick^=\"toggleSource\"]", "knowledge.write"],
        ["[onclick^=\"deleteSource\"]", "knowledge.write"],
        ["[onclick^=\"editSpecialist\"]", "specialist.write"],
        ["[onclick^=\"toggleSpecialist\"]", "specialist.write"],
        ["[onclick^=\"deleteSpecialist\"]", "specialist.write"]
    ];
    dynamicPermissionSelectors.forEach(([selector, permission]) => {
        if (!hasAdminPermission(permission)) {
            document.querySelectorAll(selector).forEach(element => {
                element.hidden = true;
                element.setAttribute("aria-hidden", "true");
            });
        }
    });
}

const htmlElement = document.documentElement;
const sidebar = document.getElementById("sidebar");
const sidebarOverlay =
    document.getElementById("sidebar-overlay");

/**
 * ينفذ خطوة واجهة باسم escapeHtml ضمن صفحة Admin Web.
 * يقرأ state من DOM أو API ويحدث العرض؛ الفشل يظهر للمستخدم أو يمرر للـcaller.
 */
function escapeHtml(value) {
    const element = document.createElement("div");
    element.textContent = value ?? "";
    return element.innerHTML;
}

/**
 * ينفذ خطوة واجهة باسم formatDate ضمن صفحة Admin Web.
 * يقرأ state من DOM أو API ويحدث العرض؛ الفشل يظهر للمستخدم أو يمرر للـcaller.
 */
function formatDate(value) {
    if (!value) {
        return "لم يُفحص بعد";
    }

    return new Intl.DateTimeFormat(
        "ar",
        {
            dateStyle: "medium",
            timeStyle: "short"
        }
    ).format(new Date(value));
}

/**
 * ينفذ خطوة واجهة باسم formatDuration ضمن صفحة Admin Web.
 * يقرأ state من DOM أو API ويحدث العرض؛ الفشل يظهر للمستخدم أو يمرر للـcaller.
 */
function formatDuration(milliseconds) {
    if (milliseconds === null ||
        milliseconds === undefined) {
        return "-";
    }

    if (milliseconds < 1000) {
        return `${new Intl.NumberFormat("ar").format(Math.round(milliseconds))} مللي ثانية`;
    }

    return `${new Intl.NumberFormat("ar", {maximumFractionDigits: 2}).format(milliseconds / 1000)} ثانية`;
}

/**
 * ينفذ خطوة واجهة باسم statusBadge ضمن صفحة Admin Web.
 * يقرأ state من DOM أو API ويحدث العرض؛ الفشل يظهر للمستخدم أو يمرر للـcaller.
 */
function statusBadge(status) {
    const normalizedStatus =
        String(status || "unknown").toLowerCase();

    const labels = {
        online: "متصل",
        offline: "غير متصل",
        degraded: "متدهور",
        unknown: "غير معروف",
        success: "ناجح",
        partial_failure: "فشل جزئي",
        connection_failed: "فشل الاتصال",
        failed: "فشل",
        pending: "قيد الانتظار",
        queued: "في قائمة الانتظار",
        running: "قيد التشغيل",
        executing: "قيد التنفيذ",
        completed: "مكتمل",
        cancelled: "ملغى",
        canceled: "ملغى",
        approved: "تمت الموافقة",
        rejected: "مرفوض",
        enabled: "مفعّل",
        disabled: "معطّل",
        active: "نشط",
        inactive: "غير نشط",
        suspended: "موقوف",
        eligible: "مؤهل للمراجعة",
        review: "بحاجة إلى مراجعة",
        rolled_back: "تم التراجع",
        verified: "تم التحقق",
        not_started: "لم يبدأ",
        authorization_required: "يتطلب تفويضًا",
        created: "منشأ",
        reserved: "محجوز",
        consumed: "مستهلك",
        expired: "منتهي الصلاحية",
        denied: "مرفوض",
        blocked: "محجوب",
        passed: "اجتاز التحقق",
        stale: "منتهي الصلاحية",
        auto_execute: "تنفيذ تلقائي",
        require_human_approval: "يتطلب موافقة بشرية",
        deny: "مرفوض",
        valid: "صالح",
        revoked: "ملغى"
    };

    return `
        <span
            class="badge badge-${normalizedStatus}"
        >
            ${labels[normalizedStatus] ?? "غير معروف"}
        </span>
    `;
}

/**
 * ينفذ خطوة واجهة باسم showToast ضمن صفحة Admin Web.
 * يقرأ state من DOM أو API ويحدث العرض؛ الفشل يظهر للمستخدم أو يمرر للـcaller.
 */
function showToast(
    message,
    type = "info",
    title = null
) {
    const container =
        document.getElementById("toast-container");

    if (!container) {
        return;
    }

    const titles = {
        success: "تمت العملية",
        error: "حدث خطأ",
        warning: "تنبيه",
        info: "معلومة"
    };

    const toast = document.createElement("div");

    toast.className = `toast ${type}`;

    toast.innerHTML = `
        <div>
            <strong>
                ${escapeHtml(title || titles[type])}
            </strong>

            <p>
                ${escapeHtml(message)}
            </p>
        </div>
    `;

    container.appendChild(toast);

    window.setTimeout(
        () => toast.remove(),
        4500
    );
}

/**
 * ينفذ خطوة واجهة باسم apiRequest ضمن صفحة Admin Web.
 * يقرأ state من DOM أو API ويحدث العرض؛ الفشل يظهر للمستخدم أو يمرر للـcaller.
 */
async function apiRequest(
    url,
    options = {}
) {
    const requestOptions = {
        ...options,
        headers: {
            ...(options.body
                ? {
                    "Content-Type":
                        "application/json"
                }
                : {}),
            ...(options.headers || {})
        }
    };

    const method = (requestOptions.method || "GET").toUpperCase();
    if (["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
        const csrf = document.querySelector(
            'meta[name="csrf-token"]'
        )?.content;
        if (csrf) {
            requestOptions.headers["X-CSRF-Token"] = csrf;
        }
    }

    const response = await fetch(
        url,
        requestOptions
    );

    if (response.status === 204) {
        return null;
    }

    const responseText = await response.text();
    let data = {};
    if (responseText) {
        try {
            data = JSON.parse(responseText);
        } catch {
            data = {detail: responseText};
        }
    }

    if (!response.ok) {
        const detail =
            typeof data.detail === "string"
                ? data.detail
                : readableDetail(data.detail || data);

        const error = new Error(detail || `فشل الطلب (${response.status}).`);
        error.status = response.status;
        error.payload = data;
        if (response.status === 401) {
            showToast("انتهت جلسة الإدارة. يرجى تسجيل الدخول مرة أخرى.", "error");
        } else if (response.status === 403) {
            showToast("لا تملك الصلاحية لتنفيذ هذه العملية.", "error");
        }
        throw error;
    }

    return data;
}

function readableDetail(value) {
    if (value === null || value === undefined || value === "") {
        return "تعذر إكمال الطلب.";
    }

    if (Array.isArray(value)) {
        return value.map(item => readableDetail(item)).join("، ");
    }

    if (typeof value === "object") {
        return Object.entries(value)
            .map(([key, item]) => `${key}: ${readableDetail(item)}`)
            .join(" | ");
    }

    return String(value);
}

/**
 * ينفذ خطوة واجهة باسم initializeTheme ضمن صفحة Admin Web.
 * يقرأ state من DOM أو API ويحدث العرض؛ الفشل يظهر للمستخدم أو يمرر للـcaller.
 */
function initializeTheme() {
    const storedTheme =
        localStorage.getItem("dashboard-theme");

    const prefersDark =
        window.matchMedia(
            "(prefers-color-scheme: dark)"
        ).matches;

    const selectedTheme =
        storedTheme ||
        (prefersDark ? "dark" : "light");

    htmlElement.dataset.theme = selectedTheme;
}

/**
 * ينفذ خطوة واجهة باسم toggleTheme ضمن صفحة Admin Web.
 * يقرأ state من DOM أو API ويحدث العرض؛ الفشل يظهر للمستخدم أو يمرر للـcaller.
 */
function toggleTheme() {
    const nextTheme =
        htmlElement.dataset.theme === "dark"
            ? "light"
            : "dark";

    htmlElement.dataset.theme = nextTheme;

    localStorage.setItem(
        "dashboard-theme",
        nextTheme
    );
}

/**
 * ينفذ خطوة واجهة باسم openSidebar ضمن صفحة Admin Web.
 * يقرأ state من DOM أو API ويحدث العرض؛ الفشل يظهر للمستخدم أو يمرر للـcaller.
 */
function openSidebar() {
    sidebar?.classList.add("open");
    sidebarOverlay?.classList.add("visible");
}

/**
 * ينفذ خطوة واجهة باسم closeSidebar ضمن صفحة Admin Web.
 * يقرأ state من DOM أو API ويحدث العرض؛ الفشل يظهر للمستخدم أو يمرر للـcaller.
 */
function closeSidebar() {
    sidebar?.classList.remove("open");
    sidebarOverlay?.classList.remove("visible");
}

/**
 * ينفذ خطوة واجهة باسم initializeNavigation ضمن صفحة Admin Web.
 * يقرأ state من DOM أو API ويحدث العرض؛ الفشل يظهر للمستخدم أو يمرر للـcaller.
 */
function initializeNavigation() {
    const currentPath =
        window.location.pathname;

    const pageTitles = {
        "/": "لوحة التحكم",
        "/servers": "إدارة السيرفرات",
        "/commands": "أوامر المراقبة",
        "/reports": "تقارير المراقبة",
        "/monitoring-profiles": "ملفات المراقبة",
        "/investigations": "التحقيقات",
        "/reports": "تقارير المراقبة",
        "/specialists": "الوكلاء المتخصصون",
        "/knowledge-sources": "مصادر المعرفة",
        "/agent-runs": "تشغيلات الوكلاء",
        "/remediation": "المعالجة تحت الإشراف",
        "/autonomous-policies": "سياسات المعالجة الذاتية",
        "/autonomous-candidates": "مرشحو السياسات",
        "/autonomous-history": "سجل المعالجة الذاتية",
        "/autonomous-decisions": "قرارات المعالجة الذاتية",
        "/autonomous-runtime": "تشغيل المعالجة الذاتية",
        "/autonomous-reservations": "حجوزات التنفيذ",
        "/autonomous-authorizations": "التفويضات",
        "/audit": "التدقيق والعمليات",
        "/system": "النظام والسلامة",
    };

    document
        .querySelectorAll(".navigation-link[data-route]")
        .forEach(link => {
            const route =
                link.dataset.route;

            if (
                route === currentPath ||
                (
                    route !== "/" &&
                    currentPath.startsWith(route)
                )
            ) {
                link.classList.add("active");
            }
        });

    const titleElement =
        document.getElementById(
            "current-page-title"
        );

    if (titleElement) {
        titleElement.textContent =
            pageTitles[currentPath] ||
            Object.entries(pageTitles).find(([route]) =>
                route !== "/" && currentPath.startsWith(route)
            )?.[1] ||
            "إدارة النظام";
    }
}

initializeTheme();
initializeNavigation();

document
    .getElementById("theme-toggle")
    ?.addEventListener("click", toggleTheme);

document
    .getElementById("sidebar-open")
    ?.addEventListener("click", openSidebar);

document
    .getElementById("sidebar-close")
    ?.addEventListener("click", closeSidebar);

sidebarOverlay
    ?.addEventListener("click", closeSidebar);

document
    .getElementById("refresh-page")
    ?.addEventListener(
        "click",
        () => window.location.reload()
    );

window.escapeHtml = escapeHtml;
window.formatDate = formatDate;
window.formatDuration = formatDuration;
window.statusBadge = statusBadge;
window.showToast = showToast;
window.apiRequest = apiRequest;
window.hasAdminPermission = hasAdminPermission;
window.applyPermissionVisibility = applyPermissionVisibility;

applyPermissionVisibility();

new MutationObserver(applyPermissionVisibility).observe(
    document.documentElement,
    {childList: true, subtree: true}
);
