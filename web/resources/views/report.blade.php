<x-layouts.app title="Laporan — {{ $scan->target->name ?? 'scan' }}">
    <article class="report">
        <h1>Laporan DAST — {{ $scan->target->name ?? 'Target' }}</h1>
        <p class="muted">
            {{ $scan->target->base_url ?? '' }} ·
            {{ $scan->started_at?->format('Y-m-d H:i') ?? '—' }} ·
            status {{ $scan->status }}
        </p>
        <blockquote class="muted" style="font-size:13px">
            Pengujian dilakukan pada sistem milik sendiri atau yang diizinkan.
            Penggunaan terhadap sistem pihak ketiga tanpa izin adalah ilegal.
        </blockquote>

        <h2>Ringkasan</h2>
        <x-severity-chart :counts="$counts->toArray()" />

        <h2>Temuan</h2>
        @forelse ($findings as $f)
            <article class="finding">
                <span class="badge badge--sev-{{ Str::slug($f->severity) }}">
                    <x-severity-icon :severity="$f->severity" /> {{ $f->severity }}
                </span>
                <strong>{{ $f->vuln_type }}</strong>
                <div class="muted" style="font-size:13px;margin:4px 0">
                    {{ $f->cwe }} · {{ $f->location }} · confidence {{ $f->confidence }}
                </div>
                <div class="evidence">{{ json_encode($f->evidence, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) }}</div>
                <p><strong>Remediasi:</strong> {{ $f->remediation }}</p>
            </article>
        @empty
            <p class="muted">Tidak ada temuan tervalidasi.</p>
        @endforelse

        <h2>Lampiran — Audit request</h2>
        <table class="data">
            <thead><tr><th>Waktu</th><th>Method</th><th>URL</th><th>Verdict</th></tr></thead>
            <tbody>
                @forelse ($scan->auditLogs as $a)
                    <tr>
                        <td class="mono" style="font-size:12px">{{ $a->ts }}</td>
                        <td>{{ $a->method }}</td>
                        <td class="mono" style="font-size:12px">{{ $a->url }}</td>
                        <td>{{ $a->verdict }}</td>
                    </tr>
                @empty
                    <tr><td colspan="4" class="muted">Tidak ada entri audit.</td></tr>
                @endforelse
            </tbody>
        </table>
    </article>
</x-layouts.app>
