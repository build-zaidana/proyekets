<div @if ($polling) wire:poll.2s @endif>
    <div style="display:flex;justify-content:space-between;align-items:center">
        <h1>Scans</h1>
        <a class="btn btn--primary" href="{{ route('scans.create') }}">New scan</a>
    </div>

    @if ($scans->isEmpty())
        <p class="muted">Belum ada scan. Mulai dari target di allowlist.</p>
    @else
        <table class="data" style="margin-top:16px">
            <thead>
                <tr><th>Target</th><th>Status</th><th>Mulai</th><th>Temuan</th></tr>
            </thead>
            <tbody>
                @foreach ($scans as $scan)
                    <tr wire:key="scan-{{ $scan->id }}" style="cursor:pointer"
                        onclick="window.location='{{ route('scans.show', $scan) }}'">
                        <td>{{ $scan->target->name ?? '—' }}</td>
                        <td><span class="badge badge--run-{{ $scan->status }}">{{ ucfirst($scan->status) }}</span></td>
                        <td class="muted">{{ $scan->started_at?->diffForHumans() ?? '—' }}</td>
                        <td>{{ $scan->findings()->count() }}</td>
                    </tr>
                @endforeach
            </tbody>
        </table>
        <div style="margin-top:16px">{{ $scans->links() }}</div>
    @endif
</div>
