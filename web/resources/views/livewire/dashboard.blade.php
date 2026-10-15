<div>
    <div style="display:flex;justify-content:space-between;align-items:center">
        <h1>Dashboard</h1>
        <a class="btn btn--primary" href="{{ route('scans.create') }}">New scan</a>
    </div>

    <div class="tiles" style="margin-top:16px">
        <div class="tile"><div class="tile__num">{{ $totalScans }}</div><div class="tile__label">Total scan</div></div>
        <div class="tile"><div class="tile__num">{{ $runningScans }}</div><div class="tile__label">Sedang berjalan</div></div>
        <div class="tile"><div class="tile__num">{{ $totalFindings }}</div><div class="tile__label">Total temuan</div></div>
    </div>

    <div class="card" style="margin-top:16px">
        <h2 style="margin-top:0">Distribusi severity</h2>
        <x-severity-chart :counts="$counts" />
    </div>

    <div class="card" style="margin-top:16px">
        <h2 style="margin-top:0">Scan terbaru</h2>
        @forelse ($recentScans as $scan)
            <div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--border)">
                <a href="{{ route('scans.show', $scan) }}">{{ $scan->target->name ?? '—' }}</a>
                <span class="badge badge--run-{{ $scan->status }}">{{ ucfirst($scan->status) }}</span>
            </div>
        @empty
            <p class="muted">Belum ada scan.</p>
        @endforelse
    </div>

    <footer class="muted" style="margin-top:24px;font-size:12px">
        Pengujian dilakukan pada sistem milik sendiri atau yang diizinkan. Penggunaan
        terhadap sistem pihak ketiga tanpa izin adalah ilegal.
    </footer>
</div>
