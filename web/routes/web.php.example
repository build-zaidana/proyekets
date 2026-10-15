<?php

// Tambahkan ke routes/web.php Laravel (lihat web/README.md).
// `.example` agar tidak menimpa routes/web.php bawaan saat scaffold di-drop.

use App\Http\Controllers\ReportController;
use App\Livewire\AuditIndex;
use App\Livewire\Dashboard;
use App\Livewire\FindingsIndex;
use App\Livewire\ScanCreate;
use App\Livewire\ScanIndex;
use App\Livewire\ScanShow;
use App\Livewire\TargetsIndex;
use Illuminate\Support\Facades\Route;

Route::get('/', Dashboard::class)->name('dashboard');

Route::get('/scans', ScanIndex::class)->name('scans.index');
Route::get('/scans/create', ScanCreate::class)->name('scans.create');
Route::get('/scans/{scan}', ScanShow::class)->name('scans.show');
Route::get('/scans/{scan}/report', [ReportController::class, 'show'])->name('scans.report');

Route::get('/findings', FindingsIndex::class)->name('findings.index');
Route::get('/targets', TargetsIndex::class)->name('targets.index');
Route::get('/audit', AuditIndex::class)->name('audit.index');
