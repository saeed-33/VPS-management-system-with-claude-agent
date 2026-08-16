"""
أداة CLI لإدارة database أو تشغيل MCP أو سيناريو خارجي.

الموقع في المعمارية: Operational tooling.
يُستدعى بواسطة: مشغل الأداة أو deployment workflow.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يضيف endpoint أو capability تلقائيًا إلى التطبيق.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import http.client
import http.server
import json
import multiprocessing as mp
import os
import random
import socket
import subprocess
import tempfile
import threading
import time
from pathlib import Path


SCENARIOS = (
    "cpu",
    "memory",
    "disk-io",
    "process-churn",
    "tcp-listener",
    "http-local",
    "mixed",
)


def now() -> float:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Operational tooling.

    تُستدعى عندما يصل المسار إلى now؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد float أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return time.time()


def busy_worker(end_at: float) -> None:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Operational tooling.

    تُستدعى عندما يصل المسار إلى busy_worker؛ المدخلات المهمة: end_at.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    value = 1
    while time.time() < end_at:
        value = (
            (value * 1103515245 + 12345)
            & 0x7FFFFFFF
        )


def cpu_scenario(args, end_at):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Operational tooling.

    تُستدعى عندما يصل المسار إلى cpu_scenario؛ المدخلات المهمة: args، end_at.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    workers = max(1, min(args.cpu_workers, 8))
    processes = [
        mp.Process(
            target=busy_worker,
            args=(end_at,),
        )
        for _ in range(workers)
    ]
    for process in processes:
        process.start()
    for process in processes:
        process.join()
    return {
        "cpu_workers": workers,
    }


def memory_scenario(args, end_at):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Operational tooling.

    تُستدعى عندما يصل المسار إلى memory_scenario؛ المدخلات المهمة: args، end_at.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    memory_mb = max(
        1,
        min(args.memory_mb, 1024),
    )
    payload = bytearray(
        memory_mb * 1024 * 1024
    )

    page = 4096
    for index in range(
        0,
        len(payload),
        page,
    ):
        payload[index] = (
            index // page
        ) % 251

    checksum = hashlib.sha256(
        payload[: min(len(payload), 1024 * 1024)]
    ).hexdigest()

    while time.time() < end_at:
        time.sleep(0.1)

    del payload

    return {
        "memory_mb": memory_mb,
        "sample_sha256": checksum,
    }


def disk_io_scenario(args, end_at):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Operational tooling.

    تُستدعى عندما يصل المسار إلى disk_io_scenario؛ المدخلات المهمة: args، end_at.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    disk_mb = max(
        1,
        min(args.disk_mb, 1024),
    )
    temp_dir = Path(args.temp_dir)
    temp_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    chunk = os.urandom(1024 * 1024)
    written = 0

    fd, name = tempfile.mkstemp(
        prefix="chat-system-load-",
        suffix=".bin",
        dir=str(temp_dir),
    )

    path = Path(name)

    try:
        with os.fdopen(fd, "wb") as handle:
            for _ in range(disk_mb):
                handle.write(chunk)
                written += len(chunk)
                if time.time() >= end_at:
                    break
            handle.flush()
            os.fsync(
                handle.fileno()
            )

        read_bytes = 0
        with path.open("rb") as handle:
            while (
                time.time() < end_at
            ):
                data = handle.read(
                    1024 * 1024
                )
                if not data:
                    handle.seek(0)
                    continue
                read_bytes += len(data)

        return {
            "path": str(path),
            "written_bytes": written,
            "read_bytes": read_bytes,
        }
    finally:
        try:
            path.unlink(
                missing_ok=True
            )
        except TypeError:
            if path.exists():
                path.unlink()


def process_churn_scenario(args, end_at):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Operational tooling.

    تُستدعى عندما يصل المسار إلى process_churn_scenario؛ المدخلات المهمة: args، end_at.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    max_children = max(
        1,
        min(args.processes, 64),
    )
    created = 0

    while time.time() < end_at:
        batch = []
        for _ in range(max_children):
            if time.time() >= end_at:
                break
            proc = subprocess.Popen(
                [
                    "/bin/sh",
                    "-c",
                    "printf test >/dev/null",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            batch.append(proc)
            created += 1

        for proc in batch:
            proc.wait()

        time.sleep(0.05)

    return {
        "children_created": created,
        "batch_cap": max_children,
    }


def tcp_listener_scenario(args, end_at):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Operational tooling.

    تُستدعى عندما يصل المسار إلى tcp_listener_scenario؛ المدخلات المهمة: args، end_at.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    )
    server.bind(
        ("127.0.0.1", 0)
    )
    server.listen(16)
    server.settimeout(0.2)
    port = server.getsockname()[1]
    accepted = 0
    stop = threading.Event()

    def accept_loop():
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Operational tooling.

        تُستدعى عندما يصل المسار إلى accept_loop؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        nonlocal accepted
        while not stop.is_set():
            try:
                conn, _ = server.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            with conn:
                conn.recv(64)
                conn.sendall(b"ok")
            accepted += 1

    thread = threading.Thread(
        target=accept_loop,
        daemon=True,
    )
    thread.start()

    clients = 0
    try:
        while time.time() < end_at:
            with socket.create_connection(
                ("127.0.0.1", port),
                timeout=1.0,
            ) as client:
                client.sendall(b"ping")
                client.recv(16)
            clients += 1
            time.sleep(0.05)
    finally:
        stop.set()
        server.close()
        thread.join(
            timeout=1.0
        )

    return {
        "port": port,
        "clients": clients,
        "accepted": accepted,
    }


class QuietHandler(
    http.server.BaseHTTPRequestHandler
):
    """
    يمثل QuietHandler جزءًا من طبقة Operational tooling.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه مشغل الأداة أو deployment workflow. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def do_GET(self):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Operational tooling.

        تُستدعى عندما يصل المسار إلى do_GET؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        body = b"chat-system-test"
        self.send_response(200)
        self.send_header(
            "Content-Length",
            str(len(body)),
        )
        self.end_headers()
        self.wfile.write(body)

    def log_message(
        self,
        format,
        *args,
    ):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Operational tooling.

        تُستدعى عندما يصل المسار إلى log_message؛ المدخلات المهمة: format.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return


def http_local_scenario(args, end_at):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Operational tooling.

    تُستدعى عندما يصل المسار إلى http_local_scenario؛ المدخلات المهمة: args، end_at.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    server = http.server.ThreadingHTTPServer(
        ("127.0.0.1", 0),
        QuietHandler,
    )
    port = server.server_port

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )
    thread.start()

    requests = 0
    try:
        while time.time() < end_at:
            conn = http.client.HTTPConnection(
                "127.0.0.1",
                port,
                timeout=1.0,
            )
            conn.request(
                "GET",
                "/",
            )
            response = conn.getresponse()
            response.read()
            conn.close()
            requests += 1
            time.sleep(0.05)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(
            timeout=2.0
        )

    return {
        "port": port,
        "requests": requests,
    }


def mixed_scenario(args, end_at):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Operational tooling.

    تُستدعى عندما يصل المسار إلى mixed_scenario؛ المدخلات المهمة: args، end_at.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    cpu_end = min(
        end_at,
        time.time()
        + max(1.0, args.duration / 2),
    )
    cpu_result = cpu_scenario(
        args,
        cpu_end,
    )

    if time.time() >= end_at:
        return {
            "cpu": cpu_result,
        }

    memory_end = min(
        end_at,
        time.time()
        + max(1.0, args.duration / 4),
    )
    memory_result = memory_scenario(
        args,
        memory_end,
    )

    disk_result = {}
    if time.time() < end_at:
        disk_result = disk_io_scenario(
            args,
            end_at,
        )

    return {
        "cpu": cpu_result,
        "memory": memory_result,
        "disk_io": disk_result,
    }


def parse_args():
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Operational tooling.

    تُستدعى عندما يصل المسار إلى parse_args؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Generate bounded, reproducible "
            "Linux workloads for chat_system testing."
        )
    )
    parser.add_argument(
        "--scenario",
        choices=(
            *SCENARIOS,
            "random",
        ),
        default="random",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=15.0,
    )
    parser.add_argument(
        "--cpu-workers",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--memory-mb",
        type=int,
        default=64,
    )
    parser.add_argument(
        "--disk-mb",
        type=int,
        default=64,
    )
    parser.add_argument(
        "--processes",
        type=int,
        default=8,
    )
    parser.add_argument(
        "--temp-dir",
        default="/tmp",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
    )
    return parser.parse_args()


def main():
    """
    يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Operational tooling.

    تُستدعى عندما يصل المسار إلى main؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    args = parse_args()

    if args.duration <= 0:
        raise SystemExit(
            "--duration must be > 0"
        )

    randomizer = random.Random(
        args.seed
    )

    selected = (
        randomizer.choice(
            SCENARIOS
        )
        if args.scenario == "random"
        else args.scenario
    )

    summary = {
        "scenario": selected,
        "requested_scenario": (
            args.scenario
        ),
        "seed": args.seed,
        "duration": args.duration,
        "limits": {
            "cpu_workers": args.cpu_workers,
            "memory_mb": args.memory_mb,
            "disk_mb": args.disk_mb,
            "processes": args.processes,
            "temp_dir": args.temp_dir,
        },
        "dry_run": args.dry_run,
    }

    if args.dry_run:
        print(
            json.dumps(
                summary,
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    started = now()
    end_at = started + args.duration

    handlers = {
        "cpu": cpu_scenario,
        "memory": memory_scenario,
        "disk-io": disk_io_scenario,
        "process-churn": (
            process_churn_scenario
        ),
        "tcp-listener": (
            tcp_listener_scenario
        ),
        "http-local": (
            http_local_scenario
        ),
        "mixed": mixed_scenario,
    }

    try:
        result = handlers[selected](
            args,
            end_at,
        )
        status = "completed"
        error = None
    except KeyboardInterrupt:
        result = {}
        status = "interrupted"
        error = "KeyboardInterrupt"
    except Exception as exc:
        result = {}
        status = "failed"
        error = (
            f"{type(exc).__name__}: "
            f"{exc}"
        )

    finished = now()

    summary.update(
        {
            "status": status,
            "started_at_epoch": started,
            "finished_at_epoch": finished,
            "elapsed_seconds": (
                finished - started
            ),
            "result": result,
            "error": error,
        }
    )

    print(
        json.dumps(
            summary,
            indent=2,
            sort_keys=True,
        )
    )

    return (
        0
        if status == "completed"
        else 2
    )


if __name__ == "__main__":
    raise SystemExit(main())
