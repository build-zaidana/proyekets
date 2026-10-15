<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class AgentStep extends Model
{
    public $timestamps = false;

    protected $fillable = ['scan_id', 'seq', 'phase', 'content', 'created_at'];

    protected $casts = ['created_at' => 'datetime'];
}
