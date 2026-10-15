<?php

namespace App\Livewire;

use App\Models\Target;
use Livewire\Attributes\Layout;
use Livewire\Component;

/**
 * Daftar target (read-only dari UI). Target mencerminkan config/targets.allowlist;
 * penambahan dilakukan lewat file config + seeder, bukan dari UI (§5.2).
 */
#[Layout('components.layouts.app')]
class TargetsIndex extends Component
{
    public function render()
    {
        return view('livewire.targets-index', [
            'targets' => Target::orderBy('name')->get(),
        ]);
    }
}
