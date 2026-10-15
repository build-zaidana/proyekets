<?php

namespace App\Livewire;

use App\Models\Finding;
use Livewire\Attributes\Url;
use Livewire\Component;
use Livewire\WithPagination;

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
            ->orderByRaw(
                "FIELD(severity, 'Critical','High','Medium','Low','Info')"
            )
            ->paginate(20);

        return view('livewire.findings-index', [
            'findings' => $findings,
            'severities' => array_keys(Finding::SEVERITY_WEIGHT),
        ]);
    }
}
