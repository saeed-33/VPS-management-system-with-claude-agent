/**
 * صفحة إدارة تعليمات المراقبة. تتعامل مع إنشاء وتعديل وحذف الأوامر وإعداد سياسة البصمة عبر الواجهة البرمجية.
 */
let currentCommands = [];

const fingerprintStrategyInformation = {
    full_output: {
        label: "المخرجات كاملة",
        description:
            "يستخدم المخرجات القياسية ومخرجات الأخطاء كاملتين بعد تنظيف المسافات. " +
            "أي اختلاف في المخرجات يؤدي غالبًا إلى بصمة جديدة."
    },

    status_only: {
        label: "حالة التنفيذ فقط",
        description:
            "يستخدم نجاح التعليمة ورمز الخروج فقط، " +
            "ويتجاهل المخرجات القياسية ومخرجات الأخطاء."
    },

    canonical_lines: {
        label: "أسطر مرتبة",
        description:
            "يرتب الأسطر ويزيل التكرار، لذلك لا يؤثر تغير " +
            "ترتيب الأسطر في البصمة."
    },

    error_signature: {
        label: "توقيع الأخطاء",
        description:
            "يستخدم النص بعد إزالة العناصر المتغيرة مثل " +
            "التواريخ، وفق إعدادات ضبط البصمة."
    },

    exclude_output: {
        label: "تجاهل المخرجات",
        description:
            "يتجاهل المخرجات القياسية ومخرجات الأخطاء، لكنه يحتفظ ببيانات " +
            "التعليمة وحالة تنفيذها."
    }
};


/**
 * ينفذ خطوة واجهة باسم loadCommands ضمن صفحة Admin Web.
 * يقرأ state من DOM أو API ويحدث العرض؛ الفشل يظهر للمستخدم أو يمرر للـcaller.
 */
async function loadCommands() {
    const table = document.getElementById(
        "commands-table"
    );

    table.innerHTML = `
        <tr>
            <td colspan="6" class="loading-row">
                <span class="loading-spinner"></span>
            </td>
        </tr>
    `;

    try {
        const response = await apiRequest(
            "/api/commands"
        );

        currentCommands = Array.isArray(response)
            ? response
            : response.items || [];

        document.getElementById(
            "commands-summary"
        ).textContent =
            `إجمالي التعليمات: ${currentCommands.length}`;

        if (!currentCommands.length) {
            table.innerHTML = `
                <tr>
                    <td colspan="6">
                        <div class="empty-state">
                            <h3>لا توجد تعليمات مراقبة</h3>

                            <p>
                                أنشئ أول تعليمة باستخدام
                                النموذج الموجود أعلى الصفحة.
                            </p>
                        </div>
                    </td>
                </tr>
            `;

            return;
        }

        table.innerHTML = currentCommands
            .map(renderCommandRow)
            .join("");

    } catch (error) {
        console.error(
            "تعذر تحميل التعليمات:",
            error
        );

        table.innerHTML = `
            <tr>
                <td colspan="6">
                    <div class="empty-state">
                        <h3>تعذر تحميل التعليمات</h3>

                        <p>
                            ${escapeHtml(
                                error.message ||
                                "حدث خطأ غير معروف"
                            )}
                        </p>

                        <button
                            type="button"
                            class="button button-secondary"
                            onclick="loadCommands()"
                        >
                            إعادة المحاولة
                        </button>
                    </div>
                </td>
            </tr>
        `;

        showToast(
            error.message ||
            "تعذر تحميل التعليمات.",
            "error"
        );
    }
}


/**
 * ينفذ خطوة واجهة باسم renderCommandRow ضمن صفحة Admin Web.
 * يقرأ state من DOM أو API ويحدث العرض؛ الفشل يظهر للمستخدم أو يمرر للـcaller.
 */
function renderCommandRow(command) {
    const strategy =
        command.fingerprint_strategy ||
        "canonical_lines";

    const strategyData =
        fingerprintStrategyInformation[strategy] ||
        fingerprintStrategyInformation.canonical_lines;

    return `
        <tr>
            <td>
                <span class="table-primary-text">
                    ${escapeHtml(command.name)}
                </span>

                <span class="table-secondary-text">
                    ${
                        escapeHtml(
                            command.description ||
                            "بدون وصف"
                        )
                    }
                </span>
            </td>

            <td>
                <code
                    class="command-table-code"
                    dir="ltr"
                    title="${escapeHtml(command.command)}"
                >
                    ${escapeHtml(command.command)}
                </code>
            </td>

            <td>
                <span class="table-primary-text">
                    ${command.timeout_seconds}
                    ثانية
                </span>
            </td>

            <td>
                <span class="badge badge-info">
                    ${escapeHtml(strategyData.label)}
                </span>

                <span class="table-secondary-text">
                    ${escapeHtml(strategy)}
                </span>
            </td>

            <td>
                ${
                    command.enabled
                        ? `
                            <span class="badge badge-success">
                                مفعلة
                            </span>
                        `
                        : `
                            <span class="badge badge-unknown">
                                متوقفة
                            </span>
                        `
                }
            </td>

            <td>
                <div class="table-actions">
                    <button
                        type="button"
                        class="button button-secondary button-sm"
                        data-required-permission="command.write"
                        onclick="openEditCommandModal(${command.id})"
                    >
                        تعديل
                    </button>

                    <button
                        type="button"
                        class="button ${
                            command.enabled
                                ? "button-warning"
                                : "button-success"
                        } button-sm"
                        data-required-permission="command.write"
                        onclick="toggleCommand(
                            ${command.id},
                            ${command.enabled}
                        )"
                    >
                        ${
                            command.enabled
                                ? "إيقاف"
                                : "تفعيل"
                        }
                    </button>

                    <button
                        type="button"
                        class="button button-danger button-sm"
                        data-required-permission="command.write"
                        onclick="deleteCommand(${command.id})"
                    >
                        حذف
                    </button>
                </div>
            </td>
        </tr>
    `;
}


/**
 * ينفذ خطوة واجهة باسم fingerprintConfigFromForm ضمن صفحة Admin Web.
 * يحول خيارات سياسة الذاكرة المرئية إلى إعدادات الطلب دون عرض بنية تقنية.
 */
function fingerprintConfigFromForm(
    checkboxId
) {
    const checkbox = document.getElementById(
        checkboxId
    );

    return {
        remove_timestamps: Boolean(
            checkbox && checkbox.checked
        )
    };
}


function applyFingerprintConfigToForm(
    checkboxId,
    config
) {
    const checkbox = document.getElementById(
        checkboxId
    );

    if (checkbox) {
        checkbox.checked = config?.remove_timestamps !== false;
    }
}


function updateFingerprintOptionState(
    strategyId,
    checkboxId
) {
    const strategy = document.getElementById(
        strategyId
    );
    const checkbox = document.getElementById(
        checkboxId
    );

    if (strategy && checkbox) {
        checkbox.disabled = strategy.value !== "error_signature";
    }
}


/**
 * ينفذ خطوة واجهة باسم updateStrategyHelp ضمن صفحة Admin Web.
 * يقرأ state من DOM أو API ويحدث العرض؛ الفشل يظهر للمستخدم أو يمرر للـcaller.
 */
function updateStrategyHelp(
    selectId,
    helpId
) {
    const select = document.getElementById(
        selectId
    );

    const help = document.getElementById(
        helpId
    );

    if (!select || !help) {
        return;
    }

    const strategy =
        fingerprintStrategyInformation[
            select.value
        ];

    help.textContent = strategy
        ? strategy.description
        : "";
}


/**
 * ينفذ خطوة واجهة باسم resetCreateCommandForm ضمن صفحة Admin Web.
 * يقرأ state من DOM أو API ويحدث العرض؛ الفشل يظهر للمستخدم أو يمرر للـcaller.
 */
function resetCreateCommandForm() {
    document.getElementById(
        "command-timeout"
    ).value = "20";

    document.getElementById(
        "command-enabled"
    ).value = "true";

    document.getElementById(
        "command-fingerprint-strategy"
    ).value = "canonical_lines";

    applyFingerprintConfigToForm(
        "command-remove-timestamps",
        {}
    );

    updateStrategyHelp(
        "command-fingerprint-strategy",
        "command-strategy-help"
    );
    updateFingerprintOptionState(
        "command-fingerprint-strategy",
        "command-remove-timestamps"
    );
}


/**
 * ينفذ خطوة واجهة باسم openEditCommandModal ضمن صفحة Admin Web.
 * يقرأ state من DOM أو API ويحدث العرض؛ الفشل يظهر للمستخدم أو يمرر للـcaller.
 */
function openEditCommandModal(commandId) {
    const command = currentCommands.find(
        item => item.id === commandId
    );

    if (!command) {
        showToast(
            "تعذر العثور على التعليمة.",
            "error"
        );

        return;
    }

    document.getElementById(
        "edit-command-id"
    ).value = command.id;

    document.getElementById(
        "edit-command-name"
    ).value = command.name;

    document.getElementById(
        "edit-command-text"
    ).value = command.command;

    document.getElementById(
        "edit-command-description"
    ).value = command.description || "";

    document.getElementById(
        "edit-command-timeout"
    ).value = command.timeout_seconds;

    document.getElementById(
        "edit-command-enabled"
    ).value = String(command.enabled);

    document.getElementById(
        "edit-command-fingerprint-strategy"
    ).value =
        command.fingerprint_strategy ||
        "canonical_lines";

    applyFingerprintConfigToForm(
        "edit-command-remove-timestamps",
        command.fingerprint_config || {}
    );

    updateStrategyHelp(
        "edit-command-fingerprint-strategy",
        "edit-command-strategy-help"
    );
    updateFingerprintOptionState(
        "edit-command-fingerprint-strategy",
        "edit-command-remove-timestamps"
    );

    const modal = document.getElementById(
        "edit-command-modal"
    );

    modal.hidden = false;

    document.body.classList.add(
        "modal-open"
    );
}


/**
 * ينفذ خطوة واجهة باسم closeEditCommandModal ضمن صفحة Admin Web.
 * يقرأ state من DOM أو API ويحدث العرض؛ الفشل يظهر للمستخدم أو يمرر للـcaller.
 */
function closeEditCommandModal() {
    const modal = document.getElementById(
        "edit-command-modal"
    );

    modal.hidden = true;

    document.body.classList.remove(
        "modal-open"
    );
}


/**
 * ينفذ خطوة واجهة باسم toggleCommand ضمن صفحة Admin Web.
 * يقرأ state من DOM أو API ويحدث العرض؛ الفشل يظهر للمستخدم أو يمرر للـcaller.
 */
async function toggleCommand(
    commandId,
    currentlyEnabled
) {
    try {
        await apiRequest(
            `/api/commands/${commandId}`,
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

        await loadCommands();

    } catch (error) {
        showToast(
            error.message,
            "error"
        );
    }
}


/**
 * ينفذ خطوة واجهة باسم deleteCommand ضمن صفحة Admin Web.
 * يقرأ state من DOM أو API ويحدث العرض؛ الفشل يظهر للمستخدم أو يمرر للـcaller.
 */
async function deleteCommand(commandId) {
    const command = currentCommands.find(
        item => item.id === commandId
    );

    const commandName =
        command?.name || `#${commandId}`;

    const confirmed = window.confirm(
        `هل تريد حذف التعليمة "${commandName}"؟\n\n` +
        "قد يفشل الحذف إذا كانت التعليمة مرتبطة " +
        "بملف مراقبة."
    );

    if (!confirmed) {
        return;
    }

    try {
        await apiRequest(
            `/api/commands/${commandId}`,
            {
                method: "DELETE"
            }
        );

        showToast(
            "تم حذف التعليمة.",
            "success"
        );

        await loadCommands();

    } catch (error) {
        showToast(
            error.message,
            "error"
        );
    }
}


document
    .getElementById("command-form")
    ?.addEventListener(
        "submit",
        async event => {
            event.preventDefault();

            const submitButton =
                document.getElementById(
                    "create-command-button"
                );

            submitButton.disabled = true;

            try {
                const fingerprintConfig =
                    fingerprintConfigFromForm(
                        "command-remove-timestamps"
                    );

                await apiRequest(
                    "/api/commands",
                    {
                        method: "POST",
                        body: JSON.stringify({
                            name:
                                document.getElementById(
                                    "command-name"
                                ).value.trim(),

                            description:
                                document.getElementById(
                                    "command-description"
                                ).value.trim() || null,

                            command:
                                document.getElementById(
                                    "command-text"
                                ).value.trim(),

                            timeout_seconds:
                                Number(
                                    document.getElementById(
                                        "command-timeout"
                                    ).value
                                ),

                            enabled:
                                document.getElementById(
                                    "command-enabled"
                                ).value === "true",

                            fingerprint_strategy:
                                document.getElementById(
                                    "command-fingerprint-strategy"
                                ).value,

                            fingerprint_config:
                                fingerprintConfig
                        })
                    }
                );

                showToast(
                    "تم إنشاء تعليمة المراقبة.",
                    "success"
                );

                event.target.reset();
                resetCreateCommandForm();

                await loadCommands();

            } catch (error) {
                showToast(
                    error.message,
                    "error"
                );

            } finally {
                submitButton.disabled = false;
            }
        }
    );


document
    .getElementById("edit-command-form")
    ?.addEventListener(
        "submit",
        async event => {
            event.preventDefault();

            const commandId = Number(
                document.getElementById(
                    "edit-command-id"
                ).value
            );

            const submitButton =
                event.target.querySelector(
                    'button[type="submit"]'
                );

            submitButton.disabled = true;

            try {
                const fingerprintConfig =
                    fingerprintConfigFromForm(
                        "edit-command-remove-timestamps"
                    );

                await apiRequest(
                    `/api/commands/${commandId}`,
                    {
                        method: "PATCH",
                        body: JSON.stringify({
                            name:
                                document.getElementById(
                                    "edit-command-name"
                                ).value.trim(),

                            description:
                                document.getElementById(
                                    "edit-command-description"
                                ).value.trim() || null,

                            command:
                                document.getElementById(
                                    "edit-command-text"
                                ).value.trim(),

                            timeout_seconds:
                                Number(
                                    document.getElementById(
                                        "edit-command-timeout"
                                    ).value
                                ),

                            enabled:
                                document.getElementById(
                                    "edit-command-enabled"
                                ).value === "true",

                            fingerprint_strategy:
                                document.getElementById(
                                    "edit-command-fingerprint-strategy"
                                ).value,

                            fingerprint_config:
                                fingerprintConfig
                        })
                    }
                );

                closeEditCommandModal();

                showToast(
                    "تم تحديث تعليمة المراقبة.",
                    "success"
                );

                await loadCommands();

            } catch (error) {
                showToast(
                    error.message,
                    "error"
                );

            } finally {
                submitButton.disabled = false;
            }
        }
    );


document
    .getElementById(
        "command-fingerprint-strategy"
    )
    ?.addEventListener(
        "change",
        () => {
            updateStrategyHelp(
                "command-fingerprint-strategy",
                "command-strategy-help"
            );
            updateFingerprintOptionState(
                "command-fingerprint-strategy",
                "command-remove-timestamps"
            );
        }
    );


document
    .getElementById(
        "edit-command-fingerprint-strategy"
    )
    ?.addEventListener(
        "change",
        () => {
            updateStrategyHelp(
                "edit-command-fingerprint-strategy",
                "edit-command-strategy-help"
            );
            updateFingerprintOptionState(
                "edit-command-fingerprint-strategy",
                "edit-command-remove-timestamps"
            );
        }
    );


document
    .getElementById("reload-commands")
    ?.addEventListener(
        "click",
        loadCommands
    );


document
    .getElementById("reset-command-form")
    ?.addEventListener(
        "click",
        () => {
            window.setTimeout(
                resetCreateCommandForm,
                0
            );
        }
    );


document
    .getElementById("edit-command-modal")
    ?.addEventListener(
        "click",
        event => {
            if (
                event.target.id ===
                "edit-command-modal"
            ) {
                closeEditCommandModal();
            }
        }
    );


document.addEventListener(
    "keydown",
    event => {
        if (event.key === "Escape") {
            closeEditCommandModal();
        }
    }
);


resetCreateCommandForm();
loadCommands();
