<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Scan extends Model
{
    protected $fillable = ['target_id', 'status', 'totals', 'started_at', 'finished_at'];

    protected $casts = [
        'totals' => 'array',
        'started_at' => 'datetime',
        'finished_at' => 'datetime',
    ];

    public function target(): BelongsTo
    {
        return $this->belongsTo(Target::class);
    }

    public function steps(): HasMany
    {
        return $this->hasMany(AgentStep::class)->orderBy('seq');
    }

    public function findings(): HasMany
    {
        return $this->hasMany(Finding::class);
    }

    public function isRunning(): bool
    {
        return in_array($this->status, ['queued', 'running'], true);
    }
}
