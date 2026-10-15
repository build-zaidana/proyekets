/** @type {import('tailwindcss').Config} */
// Token dipetakan dari CSS variables (resources/css/app.css), sumber kebenaran di
// docs/DESIGN_GUIDELINES.md §2. Jangan menaruh nilai hex mentah di sini.
export default {
    content: [
        './resources/**/*.blade.php',
        './resources/**/*.js',
        './app/Livewire/**/*.php',
    ],
    theme: {
        extend: {
            colors: {
                bg: 'var(--bg)',
                surface: 'var(--surface)',
                'surface-2': 'var(--surface-2)',
                border: 'var(--border)',
                ink: 'var(--ink)',
                'ink-2': 'var(--ink-2)',
                'ink-muted': 'var(--ink-muted)',
                accent: 'var(--accent)',
                'accent-ink': 'var(--accent-ink)',
                severity: {
                    critical: 'var(--sev-critical)',
                    high: 'var(--sev-high)',
                    medium: 'var(--sev-medium)',
                    low: 'var(--sev-low)',
                    info: 'var(--sev-info)',
                },
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
                mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
            },
            borderRadius: {
                DEFAULT: '6px',
                card: '10px',
            },
        },
    },
    plugins: [],
}
