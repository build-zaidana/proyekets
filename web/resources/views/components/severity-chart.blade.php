@props(['counts' => []])

{{-- Distribusi temuan per severity (DESIGN_GUIDELINES §3.6).
     Satu sumbu, label angka langsung, urutan severity tetap, warna kanal sekunder
     (ikon + teks selalu ada), fallback tabel untuk aksesibilitas. --}}
@php
    $order = ['Critical', 'High', 'Medium', 'Low', 'Info'];
    $max = max(1, max(array_map(fn ($s) => $counts[$s] ?? 0, $order)));
@endphp

<figure class="sev-chart" role="group" aria-label="Distribusi temuan per severity">
    @foreach ($order as $sev)
        @php $n = $counts[$sev] ?? 0; @endphp
        <div class="sev-chart__row">
            <span class="sev-chart__label">
                <x-severity-icon :severity="$sev" /> {{ $sev }}
            </span>
            <span class="sev-chart__track">
                <span class="sev-chart__bar sev-bar--{{ Str::slug($sev) }}"
                      style="width: {{ $n ? max(3, round($n / $max * 100)) : 0 }}%"></span>
            </span>
            <span class="sev-chart__val">{{ $n }}</span>
        </div>
    @endforeach

    {{-- Fallback tabel (disembunyikan visual, dibaca screen reader & tersedia) --}}
    <figcaption class="sr-only">
        @foreach ($order as $sev) {{ $sev }}: {{ $counts[$sev] ?? 0 }}. @endforeach
    </figcaption>
</figure>
