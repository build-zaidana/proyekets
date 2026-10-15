<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

// Temuan tervalidasi. severity: Critical|High|Medium|Low|Info (DESIGN_GUIDELINES §2.2)
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('findings', function (Blueprint $table) {
            $table->id();
            $table->foreignId('scan_id')->constrained()->cascadeOnDelete();
            $table->string('severity')->index();
            $table->string('confidence');
            $table->string('vuln_type');
            $table->string('cwe')->nullable();
            $table->string('location');
            $table->json('evidence')->nullable();
            $table->text('remediation')->nullable();
            $table->timestamp('created_at')->nullable();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('findings');
    }
};
