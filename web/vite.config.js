import { defineConfig } from 'vite';
import laravel from 'laravel-vite-plugin';
import tailwindcss from '@tailwindcss/vite';

// Font dimuat via <link> Google Fonts di layout (Inter + JetBrains Mono),
// bukan plugin font build-time, agar build tidak bergantung jaringan eksternal.
export default defineConfig({
    plugins: [
        laravel({
            input: ['resources/css/app.css', 'resources/js/app.js'],
            refresh: true,
        }),
        tailwindcss(),
    ],
});
