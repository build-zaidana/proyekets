@props(['severity' => 'Info'])

{{-- Ikon severity: kanal kedua di samping warna & teks (DESIGN_GUIDELINES §2.2).
     Severity tidak boleh dibedakan dari warna saja. --}}
@php
    $glyphs = [
        'Critical' => '⛔',
        'High' => '▲',
        'Medium' => '◆',
        'Low' => '●',
        'Info' => '○',
    ];
    $glyph = $glyphs[$severity] ?? '○';
@endphp

<span aria-hidden="true" class="sev-icon">{{ $glyph }}</span>
