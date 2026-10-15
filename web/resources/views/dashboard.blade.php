<x-layouts.app title="Dashboard — AutoDAST">
    <h1>Dashboard</h1>
    <p class="muted">Distribusi temuan per severity dan scan terbaru (§3.2).</p>

    <div class="card" style="margin-top:16px">
        <p>TODO: chart distribusi severity (§3.6) &mdash; satu sumbu, label angka
            langsung, warna sebagai kanal sekunder. Sediakan tampilan tabel sebagai
            alternatif.</p>
        <a class="btn btn--primary" href="{{ route('scans.create') }}">New scan</a>
    </div>

    <footer class="muted" style="margin-top:24px;font-size:12px">
        Pengujian dilakukan pada sistem milik sendiri atau yang diizinkan. Penggunaan
        terhadap sistem pihak ketiga tanpa izin adalah ilegal.
    </footer>
</x-layouts.app>
