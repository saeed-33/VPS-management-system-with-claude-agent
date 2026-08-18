/**
 * صفحة إدارة Monitoring Profiles وassignments. تحمل profiles/commands، وتدير ربط الأوامر وترتيبها وتفعيلها عبر Admin API.
 */
let monitoringProfiles = [];
let monitoringCommands = [];
let selectedProfileId = null;

/**
 * ينفذ خطوة واجهة باسم loadMonitoringProfiles ضمن صفحة Admin Web.
 * يقرأ state من DOM أو API ويحدث العرض؛ الفشل يظهر للمستخدم أو يمرر للـcaller.
 */
async function loadMonitoringProfiles() {
    const list = document.getElementById(
        "profiles-list"
    );

    list.innerHTML = `
        <div class="empty-state">
            <span class="loading-spinner"></span>
        </div>
    `;

    try {
        monitoringProfiles = await apiRequest(
            "/api/monitoring-profiles"
        );

        renderProfiles();

        if (
            selectedProfileId &&
            monitoringProfiles.some(
                profile =>
                    profile.id === selectedProfileId
            )
        ) {
            await selectProfile(selectedProfileId);
        }

    } catch (error) {
        list.innerHTML = "";

        showToast(
            error.message,
            "error"
        );
    }
}

/**
 * ينفذ خطوة واجهة باسم loadMonitoringCommands ضمن صفحة Admin Web.
 * يقرأ state من DOM أو API ويحدث العرض؛ الفشل يظهر للمستخدم أو يمرر للـcaller.
 */
async function loadMonitoringCommands() {
    try {
        monitoringCommands = await apiRequest(
            "/api/commands"
        );

    } catch (error) {
        showToast(
            error.message,
            "error"
        );
    }
}

/**
 * ينفذ خطوة واجهة باسم renderProfiles ضمن صفحة Admin Web.
 * يقرأ state من DOM أو API ويحدث العرض؛ الفشل يظهر للمستخدم أو يمرر للـcaller.
 */
function renderProfiles() {
    const list = document.getElementById(
        "profiles-list"
    );

    if (!monitoringProfiles.length) {
        list.innerHTML = `
            <div class="empty-state">
                <h3>لا توجد ملفات مراقبة</h3>

                <p>
                    أنشئ أول ملف باستخدام النموذج أعلاه.
                </p>
            </div>
        `;

        return;
    }

    list.innerHTML = monitoringProfiles
        .map(profile => `
            <button
                type="button"
                class="profile-list-item ${
                    selectedProfileId === profile.id
                        ? "active"
                        : ""
                }"
                onclick="selectProfile(${profile.id})"
            >
                <span class="profile-list-content">
                    <strong>
                        ${escapeHtml(profile.name)}
                    </strong>

                    <small>
                        ${
                            escapeHtml(
                                profile.description ||
                                "بدون وصف"
                            )
                        }
                    </small>
                </span>

                <span
                    class="badge ${
                        profile.enabled
                            ? "badge-success"
                            : "badge-unknown"
                    }"
                >
                    ${
                        profile.enabled
                            ? "مفعل"
                            : "متوقف"
                    }
                </span>
            </button>
        `)
        .join("");
}

/**
 * ينفذ خطوة واجهة باسم selectProfile ضمن صفحة Admin Web.
 * يقرأ state من DOM أو API ويحدث العرض؛ الفشل يظهر للمستخدم أو يمرر للـcaller.
 */
async function selectProfile(profileId) {
    selectedProfileId = profileId;

    renderProfiles();

    const profile = monitoringProfiles.find(
        item => item.id === profileId
    );

    if (!profile) {
        return;
    }

    document.getElementById(
        "selected-profile-title"
    ).textContent = profile.name;

    document.getElementById(
        "selected-profile-description"
    ).textContent =
        profile.description || "بدون وصف";

    await loadProfileEditor(profile);
}

/**
 * ينفذ خطوة واجهة باسم loadProfileEditor ضمن صفحة Admin Web.
 * يقرأ state من DOM أو API ويحدث العرض؛ الفشل يظهر للمستخدم أو يمرر للـcaller.
 */
async function loadProfileEditor(profile) {
    const editor = document.getElementById(
        "profile-editor"
    );

    editor.innerHTML = `
        <div class="empty-state">
            <span class="loading-spinner"></span>
        </div>
    `;

    try {
        const assignments = await apiRequest(
            `/api/monitoring-profiles/` +
            `${profile.id}/commands`
        );

        const assignedCommandIds = new Set(
            assignments.map(
                assignment => assignment.command_id
            )
        );

        const availableCommands =
            monitoringCommands.filter(
                command =>
                    !assignedCommandIds.has(
                        command.id
                    )
            );

        editor.innerHTML = `
            <div class="profile-toolbar">
                <div class="form-group">
                    <label class="form-label">
                        إضافة تعليمة
                    </label>

                    <select
                        id="profile-command-select"
                        class="form-control"
                    >
                        <option value="">
                            اختر تعليمة
                        </option>

                        ${availableCommands
                            .map(command => `
                                <option value="${command.id}">
                                    ${escapeHtml(command.name)}
                                </option>
                            `)
                            .join("")}
                    </select>
                </div>

                <div class="form-group">
                    <label class="form-label">
                        ترتيب التنفيذ
                    </label>

                    <input
                        id="profile-command-order"
                        class="form-control"
                        type="number"
                        min="1"
                        value="${assignments.length + 1}"
                    >
                </div>

                <div class="form-group">
                    <label class="form-label">
                        مهلة مخصصة
                    </label>

                    <input
                        id="profile-command-timeout"
                        class="form-control"
                        type="number"
                        min="1"
                        placeholder="اختياري"
                    >
                </div>

                <div class="profile-toolbar-action">
                    <button
                        type="button"
                        class="button button-primary"
                        data-required-permission="profile.write"
                        onclick="assignCommandToProfile()"
                    >
                        إضافة
                    </button>
                </div>
            </div>

            <div class="profile-settings">
                <button
                    type="button"
                    class="button ${
                        profile.enabled
                            ? "button-warning"
                            : "button-success"
                    } button-sm"
                    data-required-permission="profile.write"
                    onclick="toggleProfileStatus(
                        ${profile.id},
                        ${profile.enabled}
                    )"
                >
                    ${
                        profile.enabled
                            ? "إيقاف الملف"
                            : "تفعيل الملف"
                    }
                </button>

                <button
                    type="button"
                    class="button button-danger button-sm"
                    data-required-permission="profile.write"
                    onclick="deleteProfile(${profile.id})"
                >
                    حذف الملف
                </button>
            </div>

            <div class="table-container">
                <table class="data-table">
                    <thead>
                    <tr>
                        <th>الترتيب</th>
                        <th>التعليمة</th>
                        <th>المهلة</th>
                        <th>الحالة</th>
                        <th>الإجراءات</th>
                    </tr>
                    </thead>

                    <tbody>
                        ${
                            assignments.length
                                ? assignments
                                    .map(
                                        assignment =>
                                            renderAssignmentRow(
                                                profile.id,
                                                assignment
                                            )
                                    )
                                    .join("")
                                : `
                                    <tr>
                                        <td colspan="5">
                                            <div class="empty-state">
                                                <h3>
                                                    الملف فارغ
                                                </h3>

                                                <p>
                                                    أضف تعليمات مراقبة
                                                    إلى هذا الملف.
                                                </p>
                                            </div>
                                        </td>
                                    </tr>
                                `
                        }
                    </tbody>
                </table>
            </div>
        `;

    } catch (error) {
        editor.innerHTML = "";

        showToast(
            error.message,
            "error"
        );
    }
}

/**
 * ينفذ خطوة واجهة باسم renderAssignmentRow ضمن صفحة Admin Web.
 * يقرأ state من DOM أو API ويحدث العرض؛ الفشل يظهر للمستخدم أو يمرر للـcaller.
 */
function renderAssignmentRow(
    profileId,
    assignment
) {
    const effectiveTimeout =
        assignment.custom_timeout_seconds ??
        assignment.default_timeout_seconds;

    return `
        <tr>
            <td>
                <input
                    id="order-${assignment.command_id}"
                    class="form-control compact-control"
                    type="number"
                    min="1"
                    value="${assignment.execution_order}"
                >
            </td>

            <td>
                <span class="table-primary-text">
                    ${escapeHtml(assignment.name)}
                </span>

                <code class="code-block">
                    ${escapeHtml(assignment.command)}
                </code>
            </td>

            <td>
                <input
                    id="timeout-${assignment.command_id}"
                    class="form-control compact-control"
                    type="number"
                    min="1"
                    value="${effectiveTimeout}"
                >

                <span class="table-secondary-text">
                    الافتراضي:
                    ${assignment.default_timeout_seconds}
                </span>
            </td>

            <td>
                <span class="badge ${
                    assignment.enabled
                        ? "badge-success"
                        : "badge-unknown"
                }">
                    ${
                        assignment.enabled
                            ? "مفعل"
                            : "متوقف"
                    }
                </span>
            </td>

            <td>
                <div class="table-actions">
                    <button
                        type="button"
                        class="button button-secondary button-sm"
                        onclick="saveAssignment(
                            ${profileId},
                            ${assignment.command_id},
                            ${assignment.enabled}
                        )"
                    >
                        حفظ
                    </button>

                    <button
                        type="button"
                        class="button ${
                            assignment.enabled
                                ? "button-warning"
                                : "button-success"
                        } button-sm"
                        onclick="toggleAssignment(
                            ${profileId},
                            ${assignment.command_id},
                            ${assignment.enabled}
                        )"
                    >
                        ${
                            assignment.enabled
                                ? "إيقاف"
                                : "تفعيل"
                        }
                    </button>

                    <button
                        type="button"
                        class="button button-danger button-sm"
                        onclick="removeCommandFromProfile(
                            ${profileId},
                            ${assignment.command_id}
                        )"
                    >
                        إزالة
                    </button>
                </div>
            </td>
        </tr>
    `;
}

/**
 * ينفذ خطوة واجهة باسم assignCommandToProfile ضمن صفحة Admin Web.
 * يقرأ state من DOM أو API ويحدث العرض؛ الفشل يظهر للمستخدم أو يمرر للـcaller.
 */
async function assignCommandToProfile() {
    const commandId = Number(
        document.getElementById(
            "profile-command-select"
        ).value
    );

    const executionOrder = Number(
        document.getElementById(
            "profile-command-order"
        ).value
    );

    const timeoutInput =
        document.getElementById(
            "profile-command-timeout"
        ).value;

    if (!commandId) {
        showToast(
            "اختر تعليمة أولًا.",
            "warning"
        );

        return;
    }

    try {
        await apiRequest(
            `/api/monitoring-profiles/` +
            `${selectedProfileId}/commands/` +
            `${commandId}`,
            {
                method: "POST",
                body: JSON.stringify({
                    execution_order: executionOrder,
                    enabled: true,
                    custom_timeout_seconds:
                        timeoutInput
                            ? Number(timeoutInput)
                            : null
                })
            }
        );

        showToast(
            "تمت إضافة التعليمة إلى الملف.",
            "success"
        );

        await selectProfile(
            selectedProfileId
        );

    } catch (error) {
        showToast(
            error.message,
            "error"
        );
    }
}

/**
 * ينفذ خطوة واجهة باسم saveAssignment ضمن صفحة Admin Web.
 * يقرأ state من DOM أو API ويحدث العرض؛ الفشل يظهر للمستخدم أو يمرر للـcaller.
 */
async function saveAssignment(
    profileId,
    commandId,
    currentlyEnabled
) {
    const executionOrder = Number(
        document.getElementById(
            `order-${commandId}`
        ).value
    );

    const timeoutValue =
        document.getElementById(
            `timeout-${commandId}`
        ).value;

    try {
        await apiRequest(
            `/api/monitoring-profiles/` +
            `${profileId}/commands/${commandId}`,
            {
                method: "PATCH",
                body: JSON.stringify({
                    execution_order: executionOrder,
                    enabled: currentlyEnabled,
                    custom_timeout_seconds:
                        timeoutValue
                            ? Number(timeoutValue)
                            : null
                })
            }
        );

        showToast(
            "تم تحديث إعدادات التعليمة.",
            "success"
        );

        await selectProfile(profileId);

    } catch (error) {
        showToast(
            error.message,
            "error"
        );
    }
}

/**
 * ينفذ خطوة واجهة باسم toggleAssignment ضمن صفحة Admin Web.
 * يقرأ state من DOM أو API ويحدث العرض؛ الفشل يظهر للمستخدم أو يمرر للـcaller.
 */
async function toggleAssignment(
    profileId,
    commandId,
    currentlyEnabled
) {
    try {
        await apiRequest(
            `/api/monitoring-profiles/` +
            `${profileId}/commands/${commandId}`,
            {
                method: "PATCH",
                body: JSON.stringify({
                    enabled: !currentlyEnabled
                })
            }
        );

        showToast(
            currentlyEnabled
                ? "تم إيقاف التعليمة."
                : "تم تفعيل التعليمة.",
            "success"
        );

        await selectProfile(profileId);

    } catch (error) {
        showToast(
            error.message,
            "error"
        );
    }
}

/**
 * ينفذ خطوة واجهة باسم removeCommandFromProfile ضمن صفحة Admin Web.
 * يقرأ state من DOM أو API ويحدث العرض؛ الفشل يظهر للمستخدم أو يمرر للـcaller.
 */
async function removeCommandFromProfile(
    profileId,
    commandId
) {
    const confirmed = window.confirm(
        "هل تريد إزالة التعليمة من الملف؟"
    );

    if (!confirmed) {
        return;
    }

    try {
        await apiRequest(
            `/api/monitoring-profiles/` +
            `${profileId}/commands/${commandId}`,
            {
                method: "DELETE"
            }
        );

        showToast(
            "تمت إزالة التعليمة.",
            "success"
        );

        await selectProfile(profileId);

    } catch (error) {
        showToast(
            error.message,
            "error"
        );
    }
}

/**
 * ينفذ خطوة واجهة باسم toggleProfileStatus ضمن صفحة Admin Web.
 * يقرأ state من DOM أو API ويحدث العرض؛ الفشل يظهر للمستخدم أو يمرر للـcaller.
 */
async function toggleProfileStatus(
    profileId,
    currentlyEnabled
) {
    try {
        await apiRequest(
            `/api/monitoring-profiles/${profileId}`,
            {
                method: "PATCH",
                body: JSON.stringify({
                    enabled: !currentlyEnabled
                })
            }
        );

        showToast(
            currentlyEnabled
                ? "تم إيقاف ملف المراقبة."
                : "تم تفعيل ملف المراقبة.",
            "success"
        );

        await loadMonitoringProfiles();

    } catch (error) {
        showToast(
            error.message,
            "error"
        );
    }
}

/**
 * ينفذ خطوة واجهة باسم deleteProfile ضمن صفحة Admin Web.
 * يقرأ state من DOM أو API ويحدث العرض؛ الفشل يظهر للمستخدم أو يمرر للـcaller.
 */
async function deleteProfile(profileId) {
    const confirmed = window.confirm(
        "هل تريد حذف ملف المراقبة؟ " +
        "سيتم فصل الملف عن السيرفرات المرتبطة به."
    );

    if (!confirmed) {
        return;
    }

    try {
        await apiRequest(
            `/api/monitoring-profiles/${profileId}`,
            {
                method: "DELETE"
            }
        );

        selectedProfileId = null;

        document.getElementById(
            "profile-editor"
        ).innerHTML = `
            <div class="empty-state">
                <h3>لم يتم اختيار ملف</h3>
            </div>
        `;

        showToast(
            "تم حذف ملف المراقبة.",
            "success"
        );

        await loadMonitoringProfiles();

    } catch (error) {
        showToast(
            error.message,
            "error"
        );
    }
}

document
    .getElementById("profile-form")
    .addEventListener(
        "submit",
        async event => {
            event.preventDefault();

            try {
                const profile = await apiRequest(
                    "/api/monitoring-profiles",
                    {
                        method: "POST",
                        body: JSON.stringify({
                            name:
                                document.getElementById(
                                    "profile-name"
                                ).value.trim(),
                            description:
                                document.getElementById(
                                    "profile-description"
                                ).value.trim() || null,
                            enabled:
                                document.getElementById(
                                    "profile-enabled"
                                ).value === "true"
                        })
                    }
                );

                showToast(
                    "تم إنشاء ملف المراقبة.",
                    "success"
                );

                event.target.reset();

                selectedProfileId = profile.id;

                await loadMonitoringProfiles();

            } catch (error) {
                showToast(
                    error.message,
                    "error"
                );
            }
        }
    );

document
    .getElementById("reload-profiles")
    .addEventListener(
        "click",
        loadMonitoringProfiles
    );

Promise.all([
    loadMonitoringCommands(),
    loadMonitoringProfiles()
]);
