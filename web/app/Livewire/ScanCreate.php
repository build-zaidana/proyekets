<?php

namespace App\Livewire;

use App\Models\Scan;
use App\Models\Target;
use Livewire\Attributes\Validate;
use Livewire\Component;

/**
 * Form "New scan". Target dipilih dari tabel `targets` (cermin allowlist), BUKAN
 * input URL bebas (DESIGN_GUIDELINES §5.2). Hanya menulis job 'queued' ke DB —
 * worker Python yang menjalankan. Laravel tidak pernah menyentuh target.
 */
class ScanCreate extends Component
{
    #[Validate('required|exists:targets,id')]
    public ?int $targetId = null;

    public function save()
    {
        $this->validate();

        // Pertahanan tambahan: target harus aktif. Guardrail sebenarnya tetap di
        // worker Python (§5.3) — ini hanya mencegah job sia-sia.
        $target = Target::where('id', $this->targetId)->where('is_active', true)->firstOrFail();

        $scan = Scan::create(['target_id' => $target->id, 'status' => 'queued']);

        return $this->redirect(route('scans.show', $scan), navigate: true);
    }

    public function render()
    {
        return view('livewire.scan-create', [
            'targets' => Target::where('is_active', true)->orderBy('name')->get(),
        ]);
    }
}
