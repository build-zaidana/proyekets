<div>
    <h1>Targets</h1>
    <p class="muted">Read-only. Target bersumber dari <code>config/targets.allowlist</code> (§5.2).</p>

    <table class="data" style="margin-top:16px">
        <thead><tr><th>Nama</th><th>Base URL</th><th>Aktif</th></tr></thead>
        <tbody>
            @forelse ($targets as $t)
                <tr>
                    <td>{{ $t->name }}</td>
                    <td class="mono" style="font-size:13px">{{ $t->base_url }}</td>
                    <td>{{ $t->is_active ? 'ya' : 'tidak' }}</td>
                </tr>
            @empty
                <tr><td colspan="3" class="muted">Belum ada target. Jalankan TargetSeeder.</td></tr>
            @endforelse
        </tbody>
    </table>
</div>
