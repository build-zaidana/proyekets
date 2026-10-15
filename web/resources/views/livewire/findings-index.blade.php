<div>
    <h1>Findings</h1>

    {{-- Filter severity: satu baris di atas tabel (§3.6 interaction) --}}
    <div style="margin:16px 0">
        <label for="sev" class="muted">Severity:</label>
        <select id="sev" wire:model.live="severity" class="btn">
            <option value="">Semua</option>
            @foreach ($severities as $s)
                <option value="{{ $s }}">{{ $s }}</option>
            @endforeach
        </select>
    </div>

    @if ($findings->isEmpty())
        <p class="muted">Tidak ada temuan.</p>
    @else
        <table class="data">
            <thead>
                <tr><th>Severity</th><th>Tipe</th><th>Lokasi</th><th>Confidence</th></tr>
            </thead>
            <tbody>
                @foreach ($findings as $f)
                    <tr wire:key="f-{{ $f->id }}">
                        <td>
                            <span class="badge badge--sev-{{ Str::slug($f->severity) }}">
                                <x-severity-icon :severity="$f->severity" /> {{ $f->severity }}
                            </span>
                        </td>
                        <td>{{ $f->vuln_type }}</td>
                        <td class="mono" style="font-size:13px">{{ $f->location }}</td>
                        <td>{{ $f->confidence }}</td>
                    </tr>
                @endforeach
            </tbody>
        </table>
        <div style="margin-top:16px">{{ $findings->links() }}</div>
    @endif
</div>
