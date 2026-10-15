<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

// Audit setiap request agen. verdict: sent | blocked (PRD §3 S5).
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('audit_log', function (Blueprint $table) {
            $table->id();
            $table->foreignId('scan_id')->nullable()->constrained()->cascadeOnDelete();
            $table->string('ts');
            $table->string('method', 10);
            $table->text('url');
            $table->string('verdict')->index();
            $table->text('reason')->nullable();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('audit_log');
    }
};
