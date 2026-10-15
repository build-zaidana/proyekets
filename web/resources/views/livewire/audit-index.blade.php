<div>
    <h1>Audit log</h1>
    <p class="muted">Setiap request agen (terkirim / diblokir guardrail). PRD §3 S5.</p>

    <table class="data" style="margin-top:16px">
        <thead><tr><th>Waktu</th><th>Scan</th><th>Method</th><th>URL</th><th>Verdict</th></tr></thead>
        <tbody>
            @forelse ($rows as $r)
                <tr wire:key="a-{{ $r->id }}">
                    <td class="mono" style="font-size:12px">{{ $r->ts }}</td>
                    <td>#{{ $r->scan_id }}</td>
                    <td>{{ $r->method }}</td>
                    <td class="mono" style="font-size:12px">{{ $r->url }}</td>
                    <td><span class="badge badge--run-{{ $r->verdict === 'blocked' ? 'blocked' : 'done' }}">{{ $r->verdict }}</span></td>
                </tr>
            @empty
                <tr><td colspan="5" class="muted">Belum ada entri.</td></tr>
            @endforelse
        </tbody>
    </table>
    <div style="margin-top:16px">{{ $rows->links() }}</div>
</div>
