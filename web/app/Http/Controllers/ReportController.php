<?php

namespace App\Http\Controllers;

use App\Models\Scan;

/**
 * Laporan HTML satu scan (DESIGN_GUIDELINES §4). Dirender dari DB; bisa dicetak PDF
 * lewat print browser. Struktur: ringkasan -> temuan (urut severity) -> lampiran audit.
 */
class ReportController extends Controller
{
    public function show(Scan $scan)
    {
        $scan->load(['target', 'findings', 'auditLogs']);

        $counts = $scan->findings
            ->groupBy('severity')
            ->map->count();

        $findings = $scan->findings
            ->sortByDesc(fn ($f) => \App\Models\Finding::SEVERITY_WEIGHT[$f->severity] ?? -1)
            ->values();

        return view('report', compact('scan', 'counts', 'findings'));
    }
}
