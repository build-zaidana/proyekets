<div>
    <h1>New scan</h1>
    <p class="muted">Pilih target dari allowlist. Input URL bebas tidak diizinkan (§5.2).</p>

    <form wire:submit="save" class="card" style="margin-top:16px;max-width:560px">
        <label for="target" style="display:block;margin-bottom:8px">Target</label>
        <select id="target" wire:model="targetId" class="btn" style="width:100%;text-align:left">
            <option value="">— pilih target —</option>
            @foreach ($targets as $t)
                <option value="{{ $t->id }}">{{ $t->name }} ({{ $t->base_url }})</option>
            @endforeach
        </select>
        @error('targetId') <p style="color:var(--sev-critical);font-size:13px;margin-top:8px">{{ $message }}</p> @enderror

        <div style="margin-top:16px;display:flex;gap:8px">
            <button type="submit" class="btn btn--primary">Mulai scan</button>
            <a href="{{ route('scans.index') }}" class="btn">Batal</a>
        </div>

        @if ($targets->isEmpty())
            <p class="muted" style="margin-top:12px">
                Belum ada target. Jalankan <code>php artisan db:seed --class=Database\Seeders\TargetSeeder</code>.
            </p>
        @endif
    </form>
</div>
