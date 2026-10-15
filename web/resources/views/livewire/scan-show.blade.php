{{-- Detail scan: feed ReAct (kiri) + temuan (kanan). Polling hanya saat berjalan. --}}
<div @if ($polling) wire:poll.2s @endif class="scan-detail">
    <header class="scan-detail__head" style="display:flex;justify-content:space-between;align-items:center">
        <div>
            <h1 style="margin-bottom:4px">{{ $scan->target->name ?? 'Target' }}</h1>
            <span class="badge badge--run-{{ $scan->status }}">{{ ucfirst($scan->status) }}</span>
        </div>
        <a class="btn" href="{{ route('scans.report', $scan) }}">Laporan</a>
    </header>

    <div class="scan-detail__grid" style="margin-top:16px">
        {{-- Agent activity feed (§3.4) --}}
        <section aria-label="Agent activity" aria-live="polite">
            <h2>Aktivitas Agen</h2>
            <ol class="feed">
                @forelse ($steps as $step)
                    <li class="feed__step feed__step--{{ $step->phase }}">
                        <span class="feed__phase">{{ ucfirst($step->phase) }}</span>
                        <code class="feed__content">{{ $step->content }}</code>
                    </li>
                @empty
                    <li class="feed__empty muted">Belum ada langkah.</li>
                @endforelse
            </ol>
        </section>

        {{-- Temuan masuk (§3.3) --}}
        <section aria-label="Findings">
            <h2>Temuan</h2>
            @forelse ($findings as $f)
                <article class="finding">
                    <div style="display:flex;align-items:center;gap:8px">
                        {{-- Severity: ikon + teks + warna, tidak pernah warna sendirian (§2.2) --}}
                        <span class="badge badge--sev-{{ Str::slug($f->severity) }}">
                            <x-severity-icon :severity="$f->severity" /> {{ $f->severity }}
                        </span>
                        <strong>{{ $f->vuln_type }}</strong>
                    </div>
                    <div class="finding__loc">{{ $f->location }}</div>
                    <details style="margin-top:6px">
                        <summary class="muted" style="cursor:pointer;font-size:13px">Evidence &amp; remediasi</summary>
                        <div class="evidence" style="margin-top:6px">{{ json_encode($f->evidence, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) }}</div>
                        <p style="font-size:13px"><strong>Remediasi:</strong> {{ $f->remediation }}</p>
                    </details>
                </article>
            @empty
                <p class="muted">Belum ada temuan tervalidasi.</p>
            @endforelse
        </section>
    </div>
</div>
