<?php

namespace App\Livewire;

use App\Models\Target;
use Livewire\Component;

/**
 * Daftar target (read-only dari UI). Target mencerminkan config/targets.allowlist;
 * penambahan dilakukan lewat file config + seeder, bukan dari UI (§5.2).
 */
class TargetsIndex extends Component
{
    public function render()
    {
        return view('livewire.targets-index', [
            'targets' => Target::orderBy('name')->get(),
        ]);
    }
}
