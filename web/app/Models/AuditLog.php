<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class AuditLog extends Model
{
    public $timestamps = false;

    protected $table = 'audit_log'; // tabel singular, bukan 'audit_logs'

    protected $fillable = ['scan_id', 'ts', 'method', 'url', 'verdict', 'reason'];
}
