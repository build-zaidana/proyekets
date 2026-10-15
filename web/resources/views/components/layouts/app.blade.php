<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ $title ?? 'AutoDAST' }}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono&display=swap" rel="stylesheet">
    @vite(['resources/css/app.css', 'resources/js/app.js'])
    @livewireStyles
</head>
<body>
    <div class="shell">
        <header class="shell__topbar">
            <strong>AutoDAST</strong>
            <span class="muted">Agentic AI DAST</span>
        </header>

        <nav class="shell__side" aria-label="Navigasi utama">
            <a href="{{ route('dashboard') }}" @if (request()->routeIs('dashboard')) aria-current="page" @endif>Dashboard</a>
            <a href="{{ route('scans.index') }}" @if (request()->routeIs('scans.*')) aria-current="page" @endif>Scans</a>
            <a href="{{ route('findings.index') }}" @if (request()->routeIs('findings.*')) aria-current="page" @endif>Findings</a>
            <a href="{{ route('targets.index') }}" @if (request()->routeIs('targets.*')) aria-current="page" @endif>Targets</a>
            <a href="{{ route('audit.index') }}" @if (request()->routeIs('audit.*')) aria-current="page" @endif>Audit</a>
        </nav>

        <main class="shell__main">
            {{ $slot }}
        </main>
    </div>

    @livewireScripts
</body>
</html>
