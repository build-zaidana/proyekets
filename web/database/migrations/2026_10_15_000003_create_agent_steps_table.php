<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

// Langkah ReAct streaming. Worker INSERT; Livewire polling membacanya (§3.4).
// phase: thought | action | observation | blocked
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('agent_steps', function (Blueprint $table) {
            $table->id();
            $table->foreignId('scan_id')->constrained()->cascadeOnDelete();
            $table->unsignedInteger('seq');
            $table->string('phase');
            $table->text('content');
            $table->timestamp('created_at')->nullable();
            $table->index(['scan_id', 'seq']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('agent_steps');
    }
};
