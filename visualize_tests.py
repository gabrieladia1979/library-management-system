#!/usr/bin/env python
"""
visualize_tests.py
------------------
Script para ejecutar la suite de pruebas de pytest, recopilar métricas detalladas
por nivel de prueba (Unitario, Integración, Sistema) y generar un reporte visual interactivo en HTML
así como un resumen formateado en consola.

Uso:
    python visualize_tests.py
    python visualize_tests.py -m unit
    python visualize_tests.py -m integration
    python visualize_tests.py -m system
    python visualize_tests.py --no-open (para no abrir el navegador automáticamente)
"""

import contextlib
import json
import platform
import sys
import time
import webbrowser
from pathlib import Path

import pytest

# Configurar encoding utf-8 para la salida estándar si es posible en Windows
if sys.platform.startswith("win"):
    with contextlib.suppress(AttributeError):
        sys.stdout.reconfigure(encoding="utf-8")


# Códigos de color ANSI para una consola atractiva
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def color_text(text, color_code, bold=False):
    """Aplica formato de color si la salida es una consola interactiva."""
    if sys.stdout.isatty():
        prefix = Colors.BOLD if bold else ""
        return f"{prefix}{color_code}{text}{Colors.ENDC}"
    return text


class TestMetricsCollector:
    """Plugin de Pytest para recolectar datos de las pruebas durante su ejecución."""

    def __init__(self):
        self.tests = []
        self.start_time = 0.0
        self.end_time = 0.0
        self.exit_code = 0

    def pytest_sessionstart(self, session):
        self.start_time = time.time()

    def pytest_sessionfinish(self, session, exitstatus):
        self.end_time = time.time()
        self.exit_code = exitstatus

    def pytest_runtest_logreport(self, report):
        # Solo recolectamos resultados en la fase 'call' (ejecución real del test),
        # o si la fase 'setup' o 'teardown' falló (lo que genera un error/fail)
        if (
            report.when == "call"
            or report.when in ("setup", "teardown")
            and report.outcome != "passed"
        ):
            self._add_report(report)

    def _add_report(self, report):
        nodeid = report.nodeid

        # Determinar nivel de prueba por ruta de archivo
        if "tests/unit" in nodeid or "tests\\unit" in nodeid:
            level = "Unitario"
        elif "tests/integration" in nodeid or "tests\\integration" in nodeid:
            level = "Integración"
        elif "tests/system" in nodeid or "tests\\system" in nodeid:
            level = "Sistema"
        else:
            level = "Otros"

        # Extraer nombre descriptivo del test y archivo
        parts = nodeid.split("::")
        file_path = parts[0]
        test_class = parts[1] if len(parts) > 2 else ""
        test_name = parts[-1]

        # Limpiar nombre para visualización
        display_name = test_name.replace("test_", "").replace("_", " ").capitalize()
        if test_class:
            display_name = f"{test_class} -> {display_name}"

        outcome = report.outcome  # 'passed', 'failed', 'skipped'

        # Si ya existe el test en la lista (ej: falló en setup y luego reporta algo más), lo actualizamos
        existing = next((t for t in self.tests if t["nodeid"] == nodeid), None)

        error_msg = ""
        if report.failed and hasattr(report, "longrepr") and report.longrepr:
            error_msg = str(report.longrepr)

        test_data = {
            "nodeid": nodeid,
            "name": display_name,
            "raw_name": test_name,
            "file": file_path,
            "level": level,
            "outcome": outcome,
            "duration": getattr(report, "duration", 0.0),
            "error": error_msg,
        }

        if existing:
            if outcome != "passed":
                existing.update(test_data)
        else:
            self.tests.append(test_data)


def compute_metrics(tests, total_duration):
    """Calcula las métricas agrupadas por nivel y totales."""
    levels = ["Unitario", "Integración", "Sistema", "Otros"]
    metrics = {
        "summary": {
            "total": len(tests),
            "passed": sum(1 for t in tests if t["outcome"] == "passed"),
            "failed": sum(1 for t in tests if t["outcome"] == "failed"),
            "skipped": sum(1 for t in tests if t["outcome"] == "skipped"),
            "duration": total_duration,
            "success_rate": 0.0,
        },
        "levels": {
            lvl: {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "duration": 0.0,
                "avg_duration": 0.0,
                "success_rate": 0.0,
            }
            for lvl in levels
        },
    }

    # Calcular tasa de éxito global
    total = metrics["summary"]["total"]
    if total > 0:
        active_total = total - metrics["summary"]["skipped"]
        divisor = active_total if active_total > 0 else total
        metrics["summary"]["success_rate"] = round(
            (metrics["summary"]["passed"] / divisor) * 100, 2
        )

    # Agrupar datos por nivel
    for test in tests:
        lvl = test["level"]
        metrics["levels"][lvl]["total"] += 1
        metrics["levels"][lvl][test["outcome"]] += 1
        metrics["levels"][lvl]["duration"] += test["duration"]

    # Calcular porcentajes e índices para cada nivel
    for _, data in metrics["levels"].items():
        lvl_total = data["total"]
        if lvl_total > 0:
            active_total = lvl_total - data["skipped"]
            divisor = active_total if active_total > 0 else lvl_total
            data["success_rate"] = round((data["passed"] / divisor) * 100, 2)
            data["avg_duration"] = round(data["duration"] / lvl_total, 4)
            data["duration"] = round(data["duration"], 4)

    return metrics


def print_console_dashboard(metrics):
    """Muestra un dashboard hermoso en la consola usando caracteres de caja y colores."""
    summary = metrics["summary"]
    levels = metrics["levels"]

    print("\n" + "=" * 80)
    print(
        color_text(
            "[STATUS] METRICAS DE TESTING POR NIVEL - BIBLIOTECH",
            Colors.HEADER,
            bold=True,
        ).center(90)
    )
    print("=" * 80)

    # Fila de Resumen Global
    rate_color = (
        Colors.GREEN
        if summary["success_rate"] >= 95
        else (Colors.YELLOW if summary["success_rate"] >= 80 else Colors.RED)
    )

    print(
        f"  * {color_text('Total Pruebas:', Colors.BOLD)} {summary['total']}   "
        f"|   {color_text('Pasadas:', Colors.GREEN)} {summary['passed']}   "
        f"|   {color_text('Fallidas:', Colors.RED)} {summary['failed']}   "
        f"|   {color_text('Omitidas:', Colors.YELLOW)} {summary['skipped']}"
    )
    print(
        f"  * {color_text('Tasa de Exito:', Colors.BOLD)} {color_text(f'{summary['success_rate']}%', rate_color, bold=True)}   "
        f"|   {color_text('Tiempo Total:', Colors.BOLD)} {summary['duration']:.2f}s"
    )
    print("-" * 80)

    # Cabecera de Tabla
    header = f"  {'NIVEL DE TEST':<18} | {'TOTAL':^7} | {'PASADAS':^9} | {'FALLIDAS':^9} | {'OMITIDAS':^9} | {'EXITO':^8} | {'TIEMPO':^8}"
    print(color_text(header, Colors.CYAN, bold=True))
    print("  " + "-" * 76)

    # Detalle por nivel
    for lvl in ["Unitario", "Integración", "Sistema"]:
        data = levels[lvl]
        if data["total"] == 0:
            continue

        lvl_disp = f"{lvl}"
        total = f"{data['total']}"

        # Formateo manual para evitar problemas con longitudes al incluir códigos ANSI
        raw_passed = f"{data['passed']}"
        raw_failed = f"{data['failed']}"
        raw_skipped = f"{data['skipped']}"

        color_text(raw_passed, Colors.GREEN if data["passed"] > 0 else Colors.ENDC)
        color_text(raw_failed, Colors.RED if data["failed"] > 0 else Colors.ENDC)
        color_text(raw_skipped, Colors.YELLOW if data["skipped"] > 0 else Colors.ENDC)

        lvl_rate_color = (
            Colors.GREEN
            if data["success_rate"] >= 95
            else (Colors.YELLOW if data["success_rate"] >= 80 else Colors.RED)
        )
        color_text(f"{data['success_rate']}%", lvl_rate_color, bold=True)
        dur = f"{data['duration']:.2f}s"

        # Formatear la fila con strings limpios para alineación
        print(
            f"  {lvl_disp:<18} | {total:^7} | {raw_passed:^9} | {raw_failed:^9} | {raw_skipped:^9} | {data['success_rate']:>6}% | {dur:^8}"
        )

    print("=" * 80)

    # Barra de distribución visual sin caracteres exóticos para máxima compatibilidad
    total_active = summary["total"] - summary["skipped"]
    if total_active > 0:
        unit_pct = levels["Unitario"]["total"] / total_active
        int_pct = levels["Integración"]["total"] / total_active
        sys_pct = levels["Sistema"]["total"] / total_active

        bar_width = 30
        unit_chars = int(unit_pct * bar_width)
        int_chars = int(int_pct * bar_width)
        sys_chars = bar_width - unit_chars - int_chars

        # Rellenar posibles diferencias de redondeo
        if unit_chars + int_chars + sys_chars < bar_width:
            unit_chars += 1

        bar = (
            color_text("#" * unit_chars, Colors.BLUE)
            + color_text("=" * int_chars, Colors.CYAN)
            + color_text("*" * sys_chars, Colors.GREEN)
        )

        print(
            f"  {color_text('Distribucion:', Colors.BOLD)} [{bar}]  "
            f"(Unit: {unit_pct*100:.0f}%, Integ: {int_pct*100:.0f}%, Sist: {sys_pct*100:.0f}%)"
        )
        print("=" * 80 + "\n")


def generate_html_dashboard(metrics, tests, output_path):
    """Genera una página HTML interactiva y premium con el reporte de métricas."""
    summary = metrics["summary"]
    levels = metrics["levels"]
    total = summary["total"]

    # Serializar tests a JSON para búsqueda y filtros interactivos en el cliente
    tests_json = json.dumps(tests, ensure_ascii=False)

    # Plantilla HTML con placeholders para evitar warnings de f-string en Python
    html_template = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Métricas de Testing — BiblioTech</title>
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">

    <style>
        :root {
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-tertiary: #334155;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-blue: #3b82f6;
            --accent-cyan: #06b6d4;
            --accent-green: #10b981;
            --accent-yellow: #f59e0b;
            --accent-red: #ef4444;
            --card-border: rgba(255, 255, 255, 0.05);
            --font-display: 'Outfit', sans-serif;
            --font-body: 'Plus Jakarta Sans', sans-serif;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background-color: var(--bg-primary);
            color: var(--text-primary);
            font-family: var(--font-body);
            min-height: 100vh;
            padding: 2rem;
            line-height: 1.5;
        }

        .container {
            max-width: 1300px;
            margin: 0 auto;
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2.5rem;
            border-bottom: 1px solid var(--card-border);
            padding-bottom: 1.5rem;
        }

        .logo-area {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .logo-badge {
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-cyan));
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: var(--font-display);
            font-weight: 800;
            font-size: 1.5rem;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
        }

        .title-area h1 {
            font-family: var(--font-display);
            font-size: 1.75rem;
            font-weight: 700;
            letter-spacing: -0.025em;
            background: linear-gradient(to right, #ffffff, #94a3b8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .title-area p {
            color: var(--text-secondary);
            font-size: 0.875rem;
        }

        .meta-info {
            text-align: right;
            color: var(--text-secondary);
            font-size: 0.875rem;
        }

        .meta-info span {
            font-weight: 600;
            color: var(--text-primary);
        }

        /* Grid de KPIs */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2.5rem;
        }

        .kpi-card {
            background: var(--bg-secondary);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 1.5rem;
            position: relative;
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .kpi-card:hover {
            transform: translateY(-4px);
            border-color: rgba(255, 255, 255, 0.1);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        }

        .kpi-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: var(--accent-blue);
        }

        .kpi-card.passed::before { background: var(--accent-green); }
        .kpi-card.failed::before { background: var(--accent-red); }
        .kpi-card.rate::before { background: linear-gradient(to bottom, var(--accent-green), var(--accent-blue)); }

        .kpi-label {
            font-size: 0.875rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }

        .kpi-value {
            font-family: var(--font-display);
            font-size: 2.25rem;
            font-weight: 800;
            line-height: 1;
            margin-bottom: 0.5rem;
        }

        .kpi-subtext {
            font-size: 0.875rem;
            color: var(--text-secondary);
        }

        /* Grid de Niveles de Tests */
        .level-section-title {
            font-family: var(--font-display);
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 1.25rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .level-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }

        .level-card {
            background: var(--bg-secondary);
            border: 1px solid var(--card-border);
            border-radius: 20px;
            padding: 1.75rem;
            transition: all 0.3s ease;
        }

        .level-card:hover {
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.4);
            border-color: rgba(255, 255, 255, 0.1);
        }

        .level-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.25rem;
        }

        .level-name {
            font-family: var(--font-display);
            font-size: 1.25rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .level-tag {
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
        }

        .level-tag.unit { background: rgba(59, 130, 246, 0.15); color: var(--accent-blue); }
        .level-tag.int { background: rgba(6, 182, 212, 0.15); color: var(--accent-cyan); }
        .level-tag.sys { background: rgba(16, 185, 129, 0.15); color: var(--accent-green); }

        .level-rate {
            font-family: var(--font-display);
            font-size: 1.5rem;
            font-weight: 800;
        }

        .level-rate.success { color: var(--accent-green); }
        .level-rate.warn { color: var(--accent-yellow); }
        .level-rate.fail { color: var(--accent-red); }

        /* Barra de progreso de distribución */
        .progress-container {
            background: var(--bg-tertiary);
            height: 10px;
            border-radius: 9999px;
            margin-bottom: 1.5rem;
            overflow: hidden;
            display: flex;
        }

        .progress-bar {
            height: 100%;
        }

        .progress-bar.passed { background: var(--accent-green); }
        .progress-bar.failed { background: var(--accent-red); }
        .progress-bar.skipped { background: var(--accent-yellow); }

        .level-stats-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.875rem;
        }

        .level-stats-table tr {
            border-bottom: 1px solid rgba(255, 255, 255, 0.03);
        }

        .level-stats-table tr:last-child {
            border-bottom: none;
        }

        .level-stats-table td {
            padding: 0.5rem 0;
            color: var(--text-secondary);
        }

        .level-stats-table td.val {
            text-align: right;
            font-weight: 600;
            color: var(--text-primary);
        }

        /* Tabla de Explorador de Pruebas */
        .explorer-section {
            background: var(--bg-secondary);
            border: 1px solid var(--card-border);
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }

        .explorer-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
            gap: 1rem;
        }

        .explorer-title {
            font-family: var(--font-display);
            font-size: 1.25rem;
            font-weight: 700;
        }

        .filters-group {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }

        .filter-btn {
            background: var(--bg-tertiary);
            border: 1px solid transparent;
            color: var(--text-secondary);
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-size: 0.875rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .filter-btn:hover {
            background: rgba(255, 255, 255, 0.1);
            color: var(--text-primary);
        }

        .filter-btn.active {
            background: var(--accent-blue);
            color: white;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
        }

        .search-wrapper {
            position: relative;
            flex-grow: 1;
            max-width: 400px;
        }

        .search-input {
            width: 100%;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--card-border);
            color: var(--text-primary);
            padding: 0.625rem 1rem;
            border-radius: 10px;
            font-size: 0.875rem;
            outline: none;
            transition: all 0.2s ease;
        }

        .search-input:focus {
            border-color: var(--accent-blue);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
        }

        .table-container {
            overflow-x: auto;
            border-radius: 12px;
            border: 1px solid var(--card-border);
            background: rgba(15, 23, 42, 0.3);
            max-height: 550px;
            overflow-y: auto;
        }

        .test-table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 0.875rem;
        }

        .test-table th {
            background: rgba(15, 23, 42, 0.8);
            position: sticky;
            top: 0;
            padding: 1rem;
            color: var(--text-secondary);
            font-weight: 600;
            border-bottom: 1px solid var(--card-border);
            z-index: 10;
        }

        .test-table td {
            padding: 1rem;
            border-bottom: 1px solid var(--card-border);
        }

        .test-table tr {
            transition: background 0.15s ease;
        }

        .test-table tr:hover {
            background: rgba(255, 255, 255, 0.02);
        }

        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.375rem;
            padding: 0.25rem 0.625rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
        }

        .status-badge.passed { background: rgba(16, 185, 129, 0.12); color: var(--accent-green); }
        .status-badge.failed { background: rgba(239, 68, 68, 0.12); color: var(--accent-red); }
        .status-badge.skipped { background: rgba(245, 158, 173, 0.12); color: var(--accent-yellow); }

        .level-pill {
            display: inline-block;
            padding: 0.125rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .level-pill.unitario { background: rgba(59, 130, 246, 0.1); color: var(--accent-blue); border: 1px solid rgba(59, 130, 246, 0.2); }
        .level-pill.integración { background: rgba(6, 182, 212, 0.1); color: var(--accent-cyan); border: 1px solid rgba(6, 182, 212, 0.2); }
        .level-pill.sistema { background: rgba(16, 185, 129, 0.1); color: var(--accent-green); border: 1px solid rgba(16, 185, 129, 0.2); }

        .duration-text {
            font-variant-numeric: tabular-nums;
            font-weight: 500;
        }

        .error-btn {
            background: none;
            border: none;
            color: var(--accent-red);
            font-weight: 600;
            cursor: pointer;
            text-decoration: underline;
            padding: 0;
            font-size: 0.875rem;
        }

        .error-row {
            background: rgba(239, 68, 68, 0.02);
            display: none;
        }

        .error-container {
            padding: 1.25rem;
            background: #090d16;
            border: 1px solid rgba(239, 68, 68, 0.2);
            border-radius: 8px;
            margin: 0.5rem 1rem 1rem 1rem;
            font-family: 'Courier New', Courier, monospace;
            font-size: 0.75rem;
            color: #fca5a5;
            white-space: pre-wrap;
            overflow-x: auto;
            max-height: 300px;
        }

        .empty-state {
            padding: 3rem;
            text-align: center;
            color: var(--text-secondary);
            font-size: 1rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Encabezado -->
        <header>
            <div class="logo-area">
                <div class="logo-badge">B</div>
                <div class="title-area">
                    <h1>Métricas de Calidad de Software</h1>
                    <p>BiblioTech — Reporte y Análisis de Cobertura por Niveles de Test</p>
                </div>
            </div>
            <div class="meta-info">
                <p>Fecha de ejecución: <span id="run-date">__RUN_DATE__</span></p>
                <p>Plataforma: <span>__OS__</span> | Python: <span>__PYTHON_VERSION__</span></p>
            </div>
        </header>

        <!-- Fila de KPIs -->
        <div class="kpi-grid">
            <div class="kpi-card rate">
                <div class="kpi-label">Tasa de Éxito</div>
                <div class="kpi-value" style="color: __RATE_COLOR__;">__SUCCESS_RATE__%</div>
                <div class="kpi-subtext">Basado en pruebas activas</div>
            </div>

            <div class="kpi-card passed">
                <div class="kpi-label">Pruebas Exitosas</div>
                <div class="kpi-value" style="color: var(--accent-green);">__TOTAL_PASSED__</div>
                <div class="kpi-subtext">De __TOTAL_TESTS__ pruebas ejecutadas</div>
            </div>

            <div class="kpi-card failed">
                <div class="kpi-label">Pruebas Fallidas</div>
                <div class="kpi-value" style="color: __FAIL_VAL_COLOR__;">__TOTAL_FAILED__</div>
                <div class="kpi-subtext">Errores críticos detectados</div>
            </div>

            <div class="kpi-card">
                <div class="kpi-label">Tiempo de Ejecución</div>
                <div class="kpi-value" style="color: var(--accent-cyan);">__TOTAL_DURATION__s</div>
                <div class="kpi-subtext">Promedio: __AVG_DURATION__s por test</div>
            </div>
        </div>

        <h2 class="level-section-title">Análisis por Nivel de Pruebas</h2>

        <!-- Tarjetas por Nivel -->
        <div class="level-grid">
            <!-- Nivel Unitario -->
            <div class="level-card">
                <div class="level-header">
                    <div class="level-name">
                        <span class="level-tag unit">Unitario</span>
                        <span>Pruebas Unitarias</span>
                    </div>
                    <div class="level-rate __UNIT_RATE_COLOR_CLASS__">
                        __UNIT_RATE__%
                    </div>
                </div>

                <!-- Barra de Distribución -->
                <div class="progress-container">
                    <div class="progress-bar passed" style="width: __UNIT_PASSED_PERCENT__%"></div>
                    <div class="progress-bar failed" style="width: __UNIT_FAILED_PERCENT__%"></div>
                    <div class="progress-bar skipped" style="width: __UNIT_SKIPPED_PERCENT__%"></div>
                </div>

                <table class="level-stats-table">
                    <tr>
                        <td>Pruebas Totales</td>
                        <td class="val">__UNIT_TOTAL__</td>
                    </tr>
                    <tr>
                        <td>Exitosas</td>
                        <td class="val" style="color: var(--accent-green);">__UNIT_PASSED__</td>
                    </tr>
                    <tr>
                        <td>Fallidas</td>
                        <td class="val" style="color: __UNIT_FAIL_VAL_COLOR__;">__UNIT_FAILED__</td>
                    </tr>
                    <tr>
                        <td>Omitidas</td>
                        <td class="val" style="color: var(--accent-yellow);">__UNIT_SKIPPED__</td>
                    </tr>
                    <tr>
                        <td>Tiempo Total</td>
                        <td class="val">__UNIT_DURATION__s</td>
                    </tr>
                    <tr>
                        <td>Tiempo Promedio</td>
                        <td class="val">__UNIT_AVG_DURATION__s</td>
                    </tr>
                </table>
            </div>

            <!-- Nivel Integración -->
            <div class="level-card">
                <div class="level-header">
                    <div class="level-name">
                        <span class="level-tag int">Integración</span>
                        <span>Pruebas de Integración</span>
                    </div>
                    <div class="level-rate __INT_RATE_COLOR_CLASS__">
                        __INT_RATE__%
                    </div>
                </div>

                <!-- Barra de Distribución -->
                <div class="progress-container">
                    <div class="progress-bar passed" style="width: __INT_PASSED_PERCENT__%"></div>
                    <div class="progress-bar failed" style="width: __INT_FAILED_PERCENT__%"></div>
                    <div class="progress-bar skipped" style="width: __INT_SKIPPED_PERCENT__%"></div>
                </div>

                <table class="level-stats-table">
                    <tr>
                        <td>Pruebas Totales</td>
                        <td class="val">__INT_TOTAL__</td>
                    </tr>
                    <tr>
                        <td>Exitosas</td>
                        <td class="val" style="color: var(--accent-green);">__INT_PASSED__</td>
                    </tr>
                    <tr>
                        <td>Fallidas</td>
                        <td class="val" style="color: __INT_FAIL_VAL_COLOR__;">__INT_FAILED__</td>
                    </tr>
                    <tr>
                        <td>Omitidas</td>
                        <td class="val" style="color: var(--accent-yellow);">__INT_SKIPPED__</td>
                    </tr>
                    <tr>
                        <td>Tiempo Total</td>
                        <td class="val">__INT_DURATION__s</td>
                    </tr>
                    <tr>
                        <td>Tiempo Promedio</td>
                        <td class="val">__INT_AVG_DURATION__s</td>
                    </tr>
                </table>
            </div>

            <!-- Nivel Sistema -->
            <div class="level-card">
                <div class="level-header">
                    <div class="level-name">
                        <span class="level-tag sys">Sistema</span>
                        <span>Pruebas de Sistema / E2E</span>
                    </div>
                    <div class="level-rate __SYS_RATE_COLOR_CLASS__">
                        __SYS_RATE__%
                    </div>
                </div>

                <!-- Barra de Distribución -->
                <div class="progress-container">
                    <div class="progress-bar passed" style="width: __SYS_PASSED_PERCENT__%"></div>
                    <div class="progress-bar failed" style="width: __SYS_FAILED_PERCENT__%"></div>
                    <div class="progress-bar skipped" style="width: __SYS_SKIPPED_PERCENT__%"></div>
                </div>

                <table class="level-stats-table">
                    <tr>
                        <td>Pruebas Totales</td>
                        <td class="val">__SYS_TOTAL__</td>
                    </tr>
                    <tr>
                        <td>Exitosas</td>
                        <td class="val" style="color: var(--accent-green);">__SYS_PASSED__</td>
                    </tr>
                    <tr>
                        <td>Fallidas</td>
                        <td class="val" style="color: __SYS_FAIL_VAL_COLOR__;">__SYS_FAILED__</td>
                    </tr>
                    <tr>
                        <td>Omitidas</td>
                        <td class="val" style="color: var(--accent-yellow);">__SYS_SKIPPED__</td>
                    </tr>
                    <tr>
                        <td>Tiempo Total</td>
                        <td class="val">__SYS_DURATION__s</td>
                    </tr>
                    <tr>
                        <td>Tiempo Promedio</td>
                        <td class="val">__SYS_AVG_DURATION__s</td>
                    </tr>
                </table>
            </div>
        </div>

        <!-- Explorador Interactivo de Casos de Prueba -->
        <div class="explorer-section">
            <div class="explorer-header">
                <h2 class="explorer-title">Explorador de Casos de Prueba</h2>
                <div class="search-wrapper">
                    <input type="text" id="search-input" class="search-input" placeholder="Buscar prueba por nombre o archivo...">
                </div>
            </div>

            <div class="explorer-header" style="margin-bottom: 1rem;">
                <div class="filters-group" id="level-filters">
                    <button class="filter-btn active" data-filter-type="level" data-val="all">Todos los Niveles</button>
                    <button class="filter-btn" data-filter-type="level" data-val="Unitario">Unitarios</button>
                    <button class="filter-btn" data-filter-type="level" data-val="Integración">Integración</button>
                    <button class="filter-btn" data-filter-type="level" data-val="Sistema">Sistema</button>
                </div>

                <div class="filters-group" id="status-filters">
                    <button class="filter-btn active" data-filter-type="status" data-val="all">Todos los Estados</button>
                    <button class="filter-btn" data-filter-type="status" data-val="passed">Exitosos</button>
                    <button class="filter-btn" data-filter-type="status" data-val="failed">Fallidos</button>
                    <button class="filter-btn" data-filter-type="status" data-val="skipped">Omitidos</button>
                </div>
            </div>

            <div class="table-container">
                <table class="test-table" id="test-table">
                    <thead>
                        <tr>
                            <th>Nombre de la Prueba</th>
                            <th>Nivel</th>
                            <th>Archivo de Prueba</th>
                            <th style="text-align: right;">Duración</th>
                            <th style="text-align: center; width: 120px;">Estado</th>
                        </tr>
                    </thead>
                    <tbody id="table-body">
                        <!-- Se poblará con JavaScript -->
                    </tbody>
                </table>
                <div id="no-results" class="empty-state" style="display: none;">
                    No se encontraron pruebas que coincidan con los filtros seleccionados.
                </div>
            </div>
        </div>
    </div>

    <!-- Script de Filtro y Búsqueda Interactivos -->
    <script>
        const tests = __TESTS_JSON__;

        let currentFilters = {
            level: 'all',
            status: 'all',
            search: ''
        };

        function init() {
            renderTable();
            setupEventListeners();
        }

        function renderTable() {
            const tbody = document.getElementById('table-body');
            const noResults = document.getElementById('no-results');
            tbody.innerHTML = '';

            let filteredTests = tests.filter(test => {
                const matchLevel = currentFilters.level === 'all' || test.level === currentFilters.level;
                const matchStatus = currentFilters.status === 'all' || test.outcome === currentFilters.status;
                const matchSearch = test.name.toLowerCase().includes(currentFilters.search) ||
                                    test.file.toLowerCase().includes(currentFilters.search) ||
                                    test.raw_name.toLowerCase().includes(currentFilters.search);
                return matchLevel && matchStatus && matchSearch;
            });

            if (filteredTests.length === 0) {
                noResults.style.display = 'block';
                return;
            } else {
                noResults.style.display = 'none';
            }

            filteredTests.forEach((test, index) => {
                // Fila principal
                const tr = document.createElement('tr');
                tr.id = `test-row-${index}`;

                const levelClass = test.level.toLowerCase();
                const statusClass = test.outcome;
                const durationDisp = test.duration ? `${test.duration.toFixed(4)}s` : '0.0000s';

                let actionHtml = '';
                if (test.outcome === 'failed') {
                    actionHtml = ` <button class="error-btn" onclick="toggleError(${index})">Ver Detalle</button>`;
                }

                tr.innerHTML = `
                    <td>
                        <div style="font-weight: 600;">${test.name}</div>
                        ${actionHtml}
                    </td>
                    <td>
                        <span class="level-pill ${levelClass}">${test.level}</span>
                    </td>
                    <td style="color: var(--text-secondary); font-family: monospace; font-size: 0.8rem;">
                        ${test.file}
                    </td>
                    <td style="text-align: right;" class="duration-text">
                        ${durationDisp}
                    </td>
                    <td style="text-align: center;">
                        <span class="status-badge ${statusClass}">${test.outcome}</span>
                    </td>
                `;
                tbody.appendChild(tr);

                // Fila de error si aplica
                if (test.outcome === 'failed' && test.error) {
                    const errTr = document.createElement('tr');
                    errTr.id = `error-row-${index}`;
                    errTr.className = 'error-row';
                    errTr.innerHTML = `
                        <td colspan="5">
                            <div class="error-container">${escapeHtml(test.error)}</div>
                        </td>
                    `;
                    tbody.appendChild(errTr);
                }
            });
        }

        function toggleError(index) {
            const errRow = document.getElementById(`error-row-${index}`);
            if (errRow.style.display === 'table-row') {
                errRow.style.display = 'none';
            } else {
                errRow.style.display = 'table-row';
            }
        }

        function escapeHtml(str) {
            return str
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }

        function setupEventListeners() {
            // Búsqueda en vivo
            document.getElementById('search-input').addEventListener('input', (e) => {
                currentFilters.search = e.target.value.toLowerCase().trim();
                renderTable();
            });

            // Filtros de nivel y estado
            setupFilterGroup('level-filters', 'level');
            setupFilterGroup('status-filters', 'status');
        }

        function setupFilterGroup(groupId, filterName) {
            const group = document.getElementById(groupId);
            const buttons = group.querySelectorAll('.filter-btn');

            buttons.forEach(btn => {
                btn.addEventListener('click', () => {
                    buttons.forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    currentFilters[filterName] = btn.dataset.val;
                    renderTable();
                });
            });
        }

        window.onload = init;
    </script>
</body>
</html>
"""

    # Reemplazar placeholders en el HTML con datos dinámicos
    html_content = html_template

    # Datos globales
    html_content = html_content.replace(
        "__RUN_DATE__", time.strftime("%d/%m/%Y %H:%M:%S")
    )
    html_content = html_content.replace(
        "__OS__", f"{platform.system()} ({platform.machine()})"
    )
    html_content = html_content.replace("__PYTHON_VERSION__", platform.python_version())

    html_content = html_content.replace(
        "__SUCCESS_RATE__", str(summary["success_rate"])
    )
    html_content = html_content.replace("__TOTAL_TESTS__", str(summary["total"]))
    html_content = html_content.replace("__TOTAL_PASSED__", str(summary["passed"]))
    html_content = html_content.replace("__TOTAL_FAILED__", str(summary["failed"]))
    html_content = html_content.replace(
        "__TOTAL_DURATION__", f"{summary['duration']:.2f}"
    )

    avg_dur = (summary["duration"] / total) if total > 0 else 0
    html_content = html_content.replace("__AVG_DURATION__", f"{avg_dur:.3f}")

    rate_color = (
        "var(--accent-green)"
        if summary["success_rate"] >= 95
        else (
            "var(--accent-yellow)"
            if summary["success_rate"] >= 80
            else "var(--accent-red)"
        )
    )
    html_content = html_content.replace("__RATE_COLOR__", rate_color)

    fail_color = (
        "var(--accent-red)" if summary["failed"] > 0 else "var(--text-secondary)"
    )
    html_content = html_content.replace("__FAIL_VAL_COLOR__", fail_color)

    # Detalle por nivel: Unitario
    unit = levels["Unitario"]
    unit_div = unit["total"] if unit["total"] > 0 else 1
    html_content = html_content.replace("__UNIT_RATE__", str(unit["success_rate"]))
    html_content = html_content.replace("__UNIT_TOTAL__", str(unit["total"]))
    html_content = html_content.replace("__UNIT_PASSED__", str(unit["passed"]))
    html_content = html_content.replace("__UNIT_FAILED__", str(unit["failed"]))
    html_content = html_content.replace("__UNIT_SKIPPED__", str(unit["skipped"]))
    html_content = html_content.replace("__UNIT_DURATION__", f"{unit['duration']:.3f}")
    html_content = html_content.replace(
        "__UNIT_AVG_DURATION__", f"{unit['avg_duration']:.4f}"
    )
    html_content = html_content.replace(
        "__UNIT_PASSED_PERCENT__", str((unit["passed"] / unit_div) * 100)
    )
    html_content = html_content.replace(
        "__UNIT_FAILED_PERCENT__", str((unit["failed"] / unit_div) * 100)
    )
    html_content = html_content.replace(
        "__UNIT_SKIPPED_PERCENT__", str((unit["skipped"] / unit_div) * 100)
    )

    u_rate_class = (
        "success"
        if unit["success_rate"] >= 95
        else ("warn" if unit["success_rate"] >= 80 else "fail")
    )
    html_content = html_content.replace("__UNIT_RATE_COLOR_CLASS__", u_rate_class)
    u_fail_color = (
        "var(--accent-red)" if unit["failed"] > 0 else "var(--text-secondary)"
    )
    html_content = html_content.replace("__UNIT_FAIL_VAL_COLOR__", u_fail_color)

    # Detalle por nivel: Integración
    integ = levels["Integración"]
    integ_div = integ["total"] if integ["total"] > 0 else 1
    html_content = html_content.replace("__INT_RATE__", str(integ["success_rate"]))
    html_content = html_content.replace("__INT_TOTAL__", str(integ["total"]))
    html_content = html_content.replace("__INT_PASSED__", str(integ["passed"]))
    html_content = html_content.replace("__INT_FAILED__", str(integ["failed"]))
    html_content = html_content.replace("__INT_SKIPPED__", str(integ["skipped"]))
    html_content = html_content.replace("__INT_DURATION__", f"{integ['duration']:.3f}")
    html_content = html_content.replace(
        "__INT_AVG_DURATION__", f"{integ['avg_duration']:.4f}"
    )
    html_content = html_content.replace(
        "__INT_PASSED_PERCENT__", str((integ["passed"] / integ_div) * 100)
    )
    html_content = html_content.replace(
        "__INT_FAILED_PERCENT__", str((integ["failed"] / integ_div) * 100)
    )
    html_content = html_content.replace(
        "__INT_SKIPPED_PERCENT__", str((integ["skipped"] / integ_div) * 100)
    )

    i_rate_class = (
        "success"
        if integ["success_rate"] >= 95
        else ("warn" if integ["success_rate"] >= 80 else "fail")
    )
    html_content = html_content.replace("__INT_RATE_COLOR_CLASS__", i_rate_class)
    i_fail_color = (
        "var(--accent-red)" if integ["failed"] > 0 else "var(--text-secondary)"
    )
    html_content = html_content.replace("__INT_FAIL_VAL_COLOR__", i_fail_color)

    # Detalle por nivel: Sistema
    syst = levels["Sistema"]
    syst_div = syst["total"] if syst["total"] > 0 else 1
    html_content = html_content.replace("__SYS_RATE__", str(syst["success_rate"]))
    html_content = html_content.replace("__SYS_TOTAL__", str(syst["total"]))
    html_content = html_content.replace("__SYS_PASSED__", str(syst["passed"]))
    html_content = html_content.replace("__SYS_FAILED__", str(syst["failed"]))
    html_content = html_content.replace("__SYS_SKIPPED__", str(syst["skipped"]))
    html_content = html_content.replace("__SYS_DURATION__", f"{syst['duration']:.3f}")
    html_content = html_content.replace(
        "__SYS_AVG_DURATION__", f"{syst['avg_duration']:.4f}"
    )
    html_content = html_content.replace(
        "__SYS_PASSED_PERCENT__", str((syst["passed"] / syst_div) * 100)
    )
    html_content = html_content.replace(
        "__SYS_FAILED_PERCENT__", str((syst["failed"] / syst_div) * 100)
    )
    html_content = html_content.replace(
        "__SYS_SKIPPED_PERCENT__", str((syst["skipped"] / syst_div) * 100)
    )

    s_rate_class = (
        "success"
        if syst["success_rate"] >= 95
        else ("warn" if syst["success_rate"] >= 80 else "fail")
    )
    html_content = html_content.replace("__SYS_RATE_COLOR_CLASS__", s_rate_class)
    s_fail_color = (
        "var(--accent-red)" if syst["failed"] > 0 else "var(--text-secondary)"
    )
    html_content = html_content.replace("__SYS_FAIL_VAL_COLOR__", s_fail_color)

    # Inyección de JSON de pruebas
    html_content = html_content.replace("__TESTS_JSON__", tests_json)

    # Crear directorio si no existe
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)


def main():
    # Remover argumentos específicos de este script que puedan interferir con pytest
    args = sys.argv[1:]

    # Manejar flag especial --no-open para no abrir el navegador
    open_browser = True
    if "--no-open" in args:
        open_browser = False
        args.remove("--no-open")

    print(
        color_text(
            "\n[INFO] Iniciando suite de pruebas de BiblioTech con Pytest...",
            Colors.BLUE,
            bold=True,
        )
    )

    # Configurar nuestro plugin collector
    collector = TestMetricsCollector()

    # Ejecutar pytest programáticamente pasándole los argumentos de la consola
    # pytest.main retorna un código de salida (0 si OK, 1 si fallas, etc.)
    exit_code = pytest.main(args, plugins=[collector])

    # Si no se ejecutó ninguna prueba, avisar
    if not collector.tests:
        print(
            color_text(
                "\n[WARN] No se recolectaron resultados de pruebas. Verifique los parametros pasados.",
                Colors.YELLOW,
                bold=True,
            )
        )
        sys.exit(exit_code)

    # Calcular métricas
    duration = collector.end_time - collector.start_time
    metrics = compute_metrics(collector.tests, duration)

    # Mostrar resumen en la consola
    print_console_dashboard(metrics)

    # Definir ruta de salida para el reporte HTML
    report_path = Path("reports/test_report.html").resolve()

    # Generar reporte HTML
    try:
        generate_html_dashboard(metrics, collector.tests, report_path)
        print(
            color_text(
                "✨ Reporte interactivo detallado generado con exito en:",
                Colors.GREEN,
                bold=True,
            )
        )
        print(color_text(f"   {report_path.as_uri()}", Colors.CYAN, bold=True))

        if open_browser:
            print(
                color_text(
                    "🌍 Abriendo el reporte interactivo en su navegador predeterminado...",
                    Colors.BLUE,
                )
            )
            webbrowser.open(report_path.as_uri())
    except Exception as e:
        print(color_text(f"❌ Error al generar el reporte HTML: {e}", Colors.RED))

    # Salir con el código de retorno original de pytest para mantener compatibilidad con CI/CD
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
