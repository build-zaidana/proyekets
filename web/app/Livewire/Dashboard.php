<?php

namespace App\Livewire;

use App\Models\Finding;
use App\Models\Scan;
use Illuminate\Support\Facades\DB;
use Livewire\Attributes\Layout;
use Livewire\Component;

#[Layout('components.layouts.app')]
class Dashboard extends Component
{
    public function render()
    {
        $counts = Finding::select('severity', DB::raw('count(*) as n'))
            ->groupBy('severity')
            ->pluck('n', 'severity')
            ->toArray();

        return view('livewire.dashboard', [
            'counts' => $counts,
            'totalFindings' => array_sum($counts),
            'totalScans' => Scan::count(),
            'runningScans' => Scan::whereIn('status', ['queued', 'running'])->count(),
            'recentScans' => Scan::with('target')->latest()->limit(5)->get(),
        ]);
    }
}
