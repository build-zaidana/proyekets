<?php

namespace App\Livewire;

use App\Models\Scan;
use Livewire\Attributes\On;
use Livewire\Component;

/**
 * Halaman detail scan: feed langkah ReAct + temuan, polling ~2 dtk (DESIGN_GUIDELINES §3.4).
 *
 * Tanpa websocket. `wire:poll.2s` pada view memanggil render ulang; selama scan
 * masih berjalan, langkah & temuan baru dari worker Python muncul otomatis.
 */
class ScanShow extends Component
{
    public Scan $scan;

    public function mount(Scan $scan): void
    {
        $this->scan = $scan;
    }

    public function render()
    {
        $this->scan->refresh()->load(['steps', 'findings', 'target']);

        $findings = $this->scan->findings
            ->sortByDesc(fn ($f) => \App\Models\Finding::SEVERITY_WEIGHT[$f->severity] ?? -1)
            ->values();

        return view('livewire.scan-show', [
            'steps' => $this->scan->steps,
            'findings' => $findings,
            'polling' => $this->scan->isRunning(),
        ]);
    }
}
