<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Finding extends Model
{
    public $timestamps = false;

    protected $fillable = [
        'scan_id', 'severity', 'confidence', 'vuln_type',
        'cwe', 'location', 'evidence', 'remediation', 'created_at',
    ];

    protected $casts = [
        'evidence' => 'array',
        'created_at' => 'datetime',
    ];

    // Bobot untuk mengurutkan severity (DESIGN_GUIDELINES §2.2).
    public const SEVERITY_WEIGHT = [
        'Critical' => 4, 'High' => 3, 'Medium' => 2, 'Low' => 1, 'Info' => 0,
    ];
}
