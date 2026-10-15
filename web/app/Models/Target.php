<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Target extends Model
{
    protected $fillable = ['name', 'base_url', 'is_active'];

    protected $casts = ['is_active' => 'boolean'];
}
