<?php

namespace App\Livewire;

use App\Models\AuditLog;
use Livewire\Component;
use Livewire\WithPagination;

class AuditIndex extends Component
{
    use WithPagination;

    public function render()
    {
        return view('livewire.audit-index', [
            'rows' => AuditLog::latest('id')->paginate(30),
        ]);
    }
}
