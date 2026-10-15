<?php

namespace App\Livewire;

use App\Models\Finding;
use Livewire\Attributes\Url;
use Livewire\Attributes\Layout;
use Livewire\Component;
use Livewire\WithPagination;

#[Layout('components.layouts.app')]
class FindingsIndex extends Component
{
    use WithPagination;

    #[Url]
    public string $severity = '';

    public function updatingSeverity(): void
    {
        $this->resetPage();
    }

    public function render()
    {
        $findings = Finding::query()
            ->when($this->severity !== '', fn ($q) => $q->where('severity', $this->severity))
            // Urut bobot severity, portabel MySQL & SQLite (hindari FIELD()).
            ->orderByRaw(
                "CASE severity WHEN 'Critical' THEN 4 WHEN 'High' THEN 3 ".
                "WHEN 'Medium' THEN 2 WHEN 'Low' THEN 1 ELSE 0 END DESC"
            )
            ->paginate(20);

        return view('livewire.findings-index', [
            'findings' => $findings,
            'severities' => array_keys(Finding::SEVERITY_WEIGHT),
        ]);
    }
}
