<?php

namespace Tests\Feature;

use App\Livewire\ScanCreate;
use App\Models\Finding;
use App\Models\Scan;
use App\Models\Target;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Livewire\Livewire;
use Tests\TestCase;

class ScanFlowTest extends TestCase
{
    use RefreshDatabase;

    public function test_creating_a_scan_writes_a_queued_row(): void
    {
        $target = Target::create([
            'name' => 'DVWA', 'base_url' => 'http://localhost:8080', 'is_active' => true,
        ]);

        Livewire::test(ScanCreate::class)
            ->set('targetId', $target->id)
            ->call('save');

        $this->assertDatabaseHas('scans', [
            'target_id' => $target->id,
            'status' => 'queued',
        ]);
    }

    public function test_scan_create_rejects_missing_target(): void
    {
        Livewire::test(ScanCreate::class)
            ->set('targetId', null)
            ->call('save')
            ->assertHasErrors('targetId');

        $this->assertDatabaseCount('scans', 0);
    }

    public function test_findings_ordered_by_severity_weight(): void
    {
        $target = Target::create(['name' => 'T', 'base_url' => 'http://localhost:8080']);
        $scan = Scan::create(['target_id' => $target->id, 'status' => 'done']);
        foreach (['Low', 'Critical', 'Medium'] as $sev) {
            Finding::create([
                'scan_id' => $scan->id, 'severity' => $sev, 'confidence' => 'High',
                'vuln_type' => 'VT-'.$sev, 'location' => 'loc', 'evidence' => [],
            ]);
        }

        // Verifikasi urutan di tabel (CASE weight), bukan di dropdown filter.
        $this->get(route('findings.index'))->assertOk()
            ->assertSeeInOrder(['VT-Critical', 'VT-Medium', 'VT-Low']);
    }

    public function test_dashboard_and_pages_render(): void
    {
        $this->get(route('dashboard'))->assertOk();
        $this->get(route('scans.index'))->assertOk();
        $this->get(route('targets.index'))->assertOk();
        $this->get(route('audit.index'))->assertOk();
    }
}
