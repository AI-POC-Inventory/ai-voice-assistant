public function up(): void
    {
        Schema::create('ai_voice_assistants', function (Blueprint $table) {
            $table->id();
            
            // Link to the user who owns this AI assistant
            $table->foreignId('user_id')->constrained()->onDelete('cascade');
            
            // Twilio number assigned to the assistant
            $table->string('twilio_number')->unique();

            // Assistant basic info
            $table->string('assistant_name')->nullable();
            $table->string('role')->nullable(); // e.g., Virtual Agent, Receptionist

            // Language and accent configuration (JSON)
            $table->json('languages')->nullable(); // e.g., ["English", "French"]
            $table->json('accents')->nullable();   // e.g., ["British English", "Swiss German"]

            // Business sector configuration
            $table->string('business_sector')->nullable(); // e.g., Healthcare, Restaurant
            $table->json('sector_settings')->nullable();   // e.g., terminology, compliance settings

            // Voice & personality settings
            $table->string('voice_tone')->nullable(); // e.g., Professional, Friendly
            $table->string('speaking_speed')->nullable(); // e.g., Slow, Fast
            $table->json('personality_settings')->nullable(); // any other style adjustments

            // Conversation flow & question logic
            $table->json('conversation_flow')->nullable(); // sequential/conditional questions, etc.

            // Escalation rules
            $table->json('escalation_rules')->nullable(); // triggers, destinations, context summary

            // Platform adaptability flags
            $table->boolean('is_configurable')->default(true);
            $table->boolean('voice_enabled')->default(true);
            $table->boolean('text_enabled')->default(true);

            $table->timestamps();
        });
    }