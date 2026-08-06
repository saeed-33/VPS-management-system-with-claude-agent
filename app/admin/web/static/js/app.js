const htmlElement = document.documentElement;
const sidebar = document.getElementById("sidebar");
const sidebarOverlay =
    document.getElementById("sidebar-overlay");

function escapeHtml(value) {
    const element = document.createElement("div");
    element.textContent = value ?? "";
    return element.innerHTML;
}

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

function formatDuration(milliseconds) {
    if (milliseconds === null ||
        milliseconds === undefined) {
        return "-";
    }

    if (milliseconds < 1000) {
        return `${Math.round(milliseconds)} ms`;
    }

    return `${(milliseconds / 1000).toFixed(2)} s`;
}

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
        failed: "فشل"
    };

    return `
        <span
            class="badge badge-${normalizedStatus}"
        >
            ${labels[normalizedStatus] ?? normalizedStatus}
        </span>
    `;
}

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

    const response = await fetch(
        url,
        requestOptions
    );

    if (response.status === 204) {
        return null;
    }

    const data = await response.json();

    if (!response.ok) {
        const detail =
            typeof data.detail === "string"
                ? data.detail
                : JSON.stringify(data.detail || data);

        throw new Error(detail);
    }

    return data;
}

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

function openSidebar() {
    sidebar?.classList.add("open");
    sidebarOverlay?.classList.add("visible");
}

function closeSidebar() {
    sidebar?.classList.remove("open");
    sidebarOverlay?.classList.remove("visible");
}

function initializeNavigation() {
    const currentPath =
        window.location.pathname;

    const pageTitles = {
        "/": "لوحة التحكم",
        "/servers": "إدارة السيرفرات",
        "/commands": "أوامر المراقبة",
        "/reports": "تقارير المراقبة",
        "/monitoring-profiles": "ملفات المراقبة",
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