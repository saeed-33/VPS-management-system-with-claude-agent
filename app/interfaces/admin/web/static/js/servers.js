console.log("Servers page script loaded");

    async function assignProfileToServer(
    serverId,
    selectedValue
) {
    const profileId = selectedValue
        ? Number(selectedValue)
        : null;

    try {
        await apiRequest(
            `/api/servers/` +
            `${serverId}/monitoring-profile`,
            {
                method: "PUT",
                body: JSON.stringify({
                    profile_id: profileId
                })
            }
        );

        showToast(
            profileId
                ? "تم ربط ملف المراقبة بالسيرفر."
                : "تم فصل ملف المراقبة عن السيرفر.",
            "success"
        );

        await loadServers();

    } catch (error) {
        showToast(
            error.message,
            "error"
        );

        await loadServers();
    }
}
    async function loadAvailableMonitoringProfiles() {
        availableMonitoringProfiles =
            await apiRequest(
                "/api/monitoring-profiles"
            );
    }
    async function loadServers() {
        const table =
            document.getElementById("servers-table");

        table.innerHTML = `
        <tr>
            <td colspan="5" class="loading-row">
                <span class="loading-spinner"></span>
            </td>
        </tr>
    `;

            try {
            const servers =
                await apiRequest("/api/servers");

            currentServers = servers;

            if (!servers.length) {
                table.innerHTML = `
                <tr>
                    <td colspan="5">
                        <div class="empty-state">
                            <div class="empty-state-icon">
                                <svg viewBox="0 0 24 24">
                                    <path d="M4 5.5A2.5 2.5 0 0 1 6.5 3h11A2.5 2.5 0 0 1 20 5.5v3A2.5 2.5 0 0 1 17.5 11h-11A2.5 2.5 0 0 1 4 8.5v-3Z"/>
                                </svg>
                            </div>

                            <h3>لا توجد سيرفرات</h3>

                            <p>
                                استخدم النموذج أعلاه لإضافة
                                أول سيرفر.
                            </p>
                        </div>
                    </td>
                </tr>
            `;

                return;
            }

            table.innerHTML = servers
                .map(server => `
                <tr>
                    <td>
                        <span class="table-primary-text">
                            ${escapeHtml(server.name)}
                        </span>

                        <span class="table-secondary-text">
                            ${escapeHtml(server.username)}
                            @
                            ${escapeHtml(server.host)}
                            :
                            ${server.port}
                        </span>
                    </td>

                    <td>
                        ${statusBadge(server.status)}
                    </td>

                    <td>
    <div class="server-monitoring-cell">
        ${
            server.monitor_enabled
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

        <select
            class="form-control compact-profile-select"
            onchange="assignProfileToServer(
                ${server.id},
                this.value
            )"
        >
            <option value="">
                بدون ملف مراقبة
            </option>

            ${availableMonitoringProfiles
                .map(profile => `
                    <option
                        value="${profile.id}"
                        ${
                            profile.id ===
                            server.monitoring_profile_id
                                ? "selected"
                                : ""
                        }
                    >
                        ${escapeHtml(profile.name)}
                    </option>
                `)
                .join("")}
        </select>
    </div>
</td>

                    <td>
                        ${formatDate(
                        server.last_checked_at
                    )}
                    </td>

                    <td>
                        <div class="table-actions">
    <button
        class="button button-secondary button-sm"
        data-required-permission="server.write"
        onclick="openEditServerModal(${server.id})"
    >
        تعديل
    </button>

    <button
        class="button ${server.monitor_enabled
                        ? "button-warning"
                        : "button-success"
                    } button-sm"
        data-required-permission="monitoring.control"
        onclick="toggleMonitoring(
            ${server.id},
            ${server.monitor_enabled}
        )"
    >
        ${server.monitor_enabled
                        ? "إيقاف المراقبة"
                        : "تفعيل المراقبة"
                    }
    </button>

    <button
        class="button button-secondary button-sm"
        data-required-permission="monitoring.control"
        onclick="testServer(${server.id})"
    >
        اختبار SSH
    </button>

    <button
        class="button button-danger button-sm"
        data-required-permission="server.write"
        onclick="deleteServer(${server.id})"
    >
        حذف
    </button>
</div>
                    </td>
                </tr>
            `)
                .join("");

        } catch (error) {
            table.innerHTML = "";

            showToast(
                error.message,
                "error"
            );
        }
    }

    document
        .getElementById("server-form")
        ?.addEventListener(
            "submit",
            async event => {
                event.preventDefault();

                const submitButton =
                    event.target.querySelector(
                        'button[type="submit"]'
                    );

                submitButton.disabled = true;

                try {
                    await apiRequest(
                        "/api/servers",
                        {
                            method: "POST",
                            body: JSON.stringify({
                                name:
                                    document.getElementById(
                                        "server-name"
                                    ).value.trim(),
                                host:
                                    document.getElementById(
                                        "server-host"
                                    ).value.trim(),
                                port:
                                    Number(
                                        document.getElementById(
                                            "server-port"
                                        ).value
                                    ),
                                username:
                                    document.getElementById(
                                        "server-username"
                                    ).value.trim(),
                                interval_seconds:
                                    Number(
                                        document.getElementById(
                                            "server-interval"
                                        ).value
                                    ),
                                private_key_path:
                                    document.getElementById(
                                        "server-key"
                                    ).value.trim() || null,
                                description:
                                    document.getElementById(
                                        "server-description"
                                    ).value.trim() || null,
                                monitor_enabled: true
                            })
                        }
                    );

                    showToast(
                        "تمت إضافة السيرفر بنجاح.",
                        "success"
                    );

                    event.target.reset();

                    document.getElementById(
                        "server-port"
                    ).value = 22;

                    document.getElementById(
                        "server-username"
                    ).value = "monitor";

                    document.getElementById(
                        "server-interval"
                    ).value = 60;

                    await loadServers();

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

    async function testServer(serverId) {
        try {
            showToast(
                "جارٍ اختبار اتصال SSH...",
                "info"
            );

            const result = await apiRequest(
                `/api/servers/${serverId}/test`,
                {
                    method: "POST"
                }
            );

            if (!result.success) {
                throw new Error(result.message);
            }

            showToast(
                `نجح الاتصال بالسيرفر: ${result.hostname || "Unknown"
                }`,
                "success"
            );

        } catch (error) {
            showToast(
                error.message,
                "error"
            );
        }
    }

    async function deleteServer(serverId) {
        const confirmed = window.confirm(
            "هل تريد حذف هذا السيرفر نهائيًا؟"
        );

        if (!confirmed) {
            return;
        }

        try {
            await apiRequest(
                `/api/servers/${serverId}`,
                {
                    method: "DELETE"
                }
            );

            showToast(
                "تم حذف السيرفر.",
                "success"
            );

            await loadServers();

        } catch (error) {
            showToast(
                error.message,
                "error"
            );
        }
    }

    document
        .getElementById("reload-servers")
        ?.addEventListener(
            "click",
            loadServers
        );
async function toggleMonitoring(
    serverId,
    currentlyEnabled
) {
    const newState = !currentlyEnabled;

    const actionText = newState
        ? "تفعيل المراقبة"
        : "إيقاف المراقبة";

    const confirmed = window.confirm(
        `هل تريد ${actionText} لهذا السيرفر؟`
    );

    if (!confirmed) {
        return;
    }

    try {
        await apiRequest(
            `/api/servers/${serverId}`,
            {
                method: "PATCH",
                body: JSON.stringify({
                    monitor_enabled: newState
                })
            }
        );

        showToast(
            newState
                ? "تم تفعيل المراقبة الدورية."
                : "تم إيقاف المراقبة الدورية.",
            "success"
        );

        await loadServers();

    } catch (error) {
        showToast(
            error.message,
            "error"
        );
    }
}
async function initializeServersPage() {
    const table = document.getElementById(
        "servers-table"
    );

    try {
        console.log(
            "Initializing servers page..."
        );

        await loadAvailableMonitoringProfiles();

        console.log(
            "Monitoring profiles loaded:",
            availableMonitoringProfiles
        );

        await loadServers();

        console.log(
            "Servers loaded successfully."
        );

    } catch (error) {
        console.error(
            "Servers page initialization failed:",
            error
        );

        if (table) {
            table.innerHTML = `
                <tr>
                    <td colspan="5">
                        <div class="empty-state">
                            <h3>
                                تعذر تحميل السيرفرات
                            </h3>

                            <p>
                                ${escapeHtml(
                                    error.message ||
                                    "حدث خطأ غير معروف"
                                )}
                            </p>

                            <button
                                type="button"
                                class="button button-secondary"
                                onclick="initializeServersPage()"
                            >
                                إعادة المحاولة
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }

        showToast(
            error.message ||
            "تعذر تحميل صفحة السيرفرات.",
            "error"
        );
    }
}

initializeServersPage();

// Edit server modal handlers
function openEditServerModal(serverId) {
    const server = currentServers.find(
        item => item.id === serverId
    );

    if (!server) {
        showToast(
            "تعذر العثور على بيانات السيرفر.",
            "error"
        );

        return;
    }

    document.getElementById(
        "edit-server-id"
    ).value = server.id;

    document.getElementById(
        "edit-server-name"
    ).value = server.name;

    document.getElementById(
        "edit-server-host"
    ).value = server.host;

    document.getElementById(
        "edit-server-port"
    ).value = server.port;

    document.getElementById(
        "edit-server-username"
    ).value = server.username;

    document.getElementById(
        "edit-server-interval"
    ).value = server.interval_seconds;

    document.getElementById(
        "edit-server-key"
    ).value = server.private_key_path || "";

    document.getElementById(
        "edit-server-description"
    ).value = server.description || "";

    document.getElementById(
        "edit-server-monitor-enabled"
    ).value = String(
        server.monitor_enabled
    );

    const profileSelect =
        document.getElementById(
            "edit-server-profile"
        );

    profileSelect.innerHTML = `
        <option value="">
            بدون ملف مراقبة
        </option>
    ` + availableMonitoringProfiles
        .map(profile => `
            <option
                value="${profile.id}"
                ${
                    profile.id ===
                    server.monitoring_profile_id
                        ? "selected"
                        : ""
                }
            >
                ${escapeHtml(profile.name)}
            </option>
        `)
        .join("");

    const modal = document.getElementById(
        "edit-server-modal"
    );

    modal.hidden = false;

    document.body.classList.add(
        "modal-open"
    );
}

function closeEditServerModal() {
    const modal = document.getElementById(
        "edit-server-modal"
    );

    modal.hidden = true;

    document.body.classList.remove(
        "modal-open"
    );
}

    document
    .getElementById("edit-server-form")
    ?.addEventListener(
        "submit",
        async event => {
            event.preventDefault();

            const serverId = Number(
                document.getElementById(
                    "edit-server-id"
                ).value
            );

            const selectedProfileValue =
                document.getElementById(
                    "edit-server-profile"
                ).value;

            const profileId =
                selectedProfileValue
                    ? Number(selectedProfileValue)
                    : null;

            const submitButton =
                event.target.querySelector(
                    'button[type="submit"]'
                );

            submitButton.disabled = true;

            try {
                await apiRequest(
                    `/api/servers/${serverId}`,
                    {
                        method: "PATCH",
                        body: JSON.stringify({
                            name:
                                document.getElementById(
                                    "edit-server-name"
                                ).value.trim(),

                            host:
                                document.getElementById(
                                    "edit-server-host"
                                ).value.trim(),

                            port:
                                Number(
                                    document.getElementById(
                                        "edit-server-port"
                                    ).value
                                ),

                            username:
                                document.getElementById(
                                    "edit-server-username"
                                ).value.trim(),

                            interval_seconds:
                                Number(
                                    document.getElementById(
                                        "edit-server-interval"
                                    ).value
                                ),

                            private_key_path:
                                document.getElementById(
                                    "edit-server-key"
                                ).value.trim() || null,

                            description:
                                document.getElementById(
                                    "edit-server-description"
                                ).value.trim() || null,

                            monitor_enabled:
                                document.getElementById(
                                    "edit-server-monitor-enabled"
                                ).value === "true"
                        })
                    }
                );

                await apiRequest(
                    `/api/servers/` +
                    `${serverId}/monitoring-profile`,
                    {
                        method: "PUT",
                        body: JSON.stringify({
                            profile_id: profileId
                        })
                    }
                );

                closeEditServerModal();

                showToast(
                    "تم تحديث معلومات السيرفر.",
                    "success"
                );

                await loadServers();

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
    .getElementById("edit-server-modal")
    ?.addEventListener(
        "click",
        event => {
            if (
                event.target.id ===
                "edit-server-modal"
            ) {
                closeEditServerModal();
            }
        }
    );
