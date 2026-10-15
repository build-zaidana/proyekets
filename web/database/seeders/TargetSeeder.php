<?php

namespace Database\Seeders;

use App\Models\Target;
use Illuminate\Database\Seeder;

/**
 * Isi tabel targets dengan target lab default (cermin config/targets.allowlist).
 * Allowlist file tetap sumber kebenaran guardrail; tabel hanya untuk pilihan di UI.
 */
class TargetSeeder extends Seeder
{
    public function run(): void
    {
        $defaults = [
            ['name' => 'DVWA (lokal)', 'base_url' => 'http://localhost:8080'],
            ['name' => 'OWASP Juice Shop (lokal)', 'base_url' => 'http://localhost:3000'],
        ];

        foreach ($defaults as $t) {
            Target::updateOrCreate(['base_url' => $t['base_url']], $t + ['is_active' => true]);
        }
    }
}
