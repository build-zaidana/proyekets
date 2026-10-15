<?php

namespace App\Livewire;

use App\Models\Scan;
use Livewire\Attributes\Layout;
use Livewire\Component;
use Livewire\WithPagination;

#[Layout('components.layouts.app')]
class ScanIndex extends Component
{
    use WithPagination;

    public function render()
    {
        $scans = Scan::with('target')->latest()->paginate(15);

        // Polling hanya bila ada scan yang masih berjalan (hemat query saat idle).
        $anyRunning = $scans->getCollection()
            ->contains(fn (Scan $s) => $s->isRunning());

        return view('livewire.scan-index', [
            'scans' => $scans,
            'polling' => $anyRunning,
        ]);
    }
}
