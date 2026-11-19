# Design System

## 1. Design Direction
Style: Modern Technical / Clean Utility / Windows Native-Compliant
Mood: Reliable, fast, unobtrusive, trustworthy, and precise.
Design Principles:
- **Clarity Over Clutter**: Every element serves an operational purpose. Complex conditions and regex rules are rendered with clear visual pills and legible typography.
- **Safety Indicators**: Destructive actions (permanent deletion, rule deletion) are unmistakably distinguished from safe operations (Recycle Bin moves, dry-run simulations).
- **Dual-Theme Fidelity**: Seamless light and dark mode experiences with high contrast, crisp borders, and dark slate backgrounds tailored for desktop monitoring workflows.

## 2. Brand
Brand Name: FileFlow
Logo: Minimalist folder icon with high-voltage lightning overlay (`Folder` + `Zap` in Lucide React), gradient from Indigo-500 (`#6366F1`) to Violet-600 (`#7C3AED`).
Brand Voice: Direct, developer-friendly, precise, and reassuring. Avoids jargon while providing exact technical details (byte counts, SHA-256 hashes, execution timestamps).

## 3. Color Palette

### Light Mode (Default)
Primary: `#4F46E5` (Indigo-600)
Secondary: `#0EA5E9` (Sky-500)
Background: `#F8FAFC` (Slate-50)
Surface: `#FFFFFF` (White)
Text: `#0F172A` (Slate-900)
Muted Text: `#64748B` (Slate-500)
Border: `#E2E8F0` (Slate-200)
Success: `#10B981` (Emerald-500)
Warning: `#F59E0B` (Amber-500)
Error: `#EF4444` (Red-500)

### Dark Mode (Supported via `dark` class)
Primary: `#6366F1` (Indigo-500)
Secondary: `#38BDF8` (Sky-400)
Background: `#0F172A` (Slate-900)
Surface: `#1E293B` (Slate-800)
Text: `#F8FAFC` (Slate-50)
Muted Text: `#94A3B8` (Slate-400)
Border: `#334155` (Slate-700)
Success: `#34D399` (Emerald-400)
Warning: `#FBBF24` (Amber-400)
Error: `#F87171` (Red-400)

## 4. Typography
Font Family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif
Heading Font: "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif
Body Font: "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif
Monospace (Paths/Hashes): "Cascadia Code", "Consolas", "Courier New", monospace
H1: 24px (1.5rem) / Weight: 700 / Line Height: 1.25
H2: 18px (1.125rem) / Weight: 600 / Line Height: 1.35
H3: 15px (0.9375rem) / Weight: 600 / Line Height: 1.4
Body: 14px (0.875rem) / Weight: 400 / Line Height: 1.5
Small: 12px (0.75rem) / Weight: 500 / Line Height: 1.4

## 5. Spacing
Base Unit: 4px
Spacing Scale: 4px (`p-1`) / 8px (`p-2`) / 12px (`p-3`) / 16px (`p-4`) / 24px (`p-6`) / 32px (`p-8`) / 48px (`p-12`) / 64px (`p-16`) / 96px (`p-24`)

## 6. Border Radius
Small: 4px (`rounded`) - badges, small chips, scrollbar handles
Medium: 8px (`rounded-lg`) - buttons, input fields, selects
Large: 12px (`rounded-xl`) - cards, modals, preview containers
Pill: 9999px (`rounded-full`) - status badges, condition operator chips, notification tags

## 7. Shadows
Small: `0 1px 2px 0 rgb(0 0 0 / 0.05)` (`shadow-sm`) - card edges, secondary buttons
Medium: `0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)` (`shadow-md`) - active cards, dropdown popovers
Large: `0 20px 25px -5px rgb(0 0 0 / 0.2), 0 8px 10px -6px rgb(0 0 0 / 0.2)` (`shadow-xl`) - modals, system dialog overlays

## 8. Buttons
Primary Button:
- Background: `bg-indigo-600 hover:bg-indigo-700 text-white`
- Radius: `rounded-lg`, Padding: `px-4 py-2 text-sm font-medium`
- Shadow: `shadow-sm transition-all duration-150 flex items-center gap-2`
Secondary Button:
- Background: `bg-slate-100 hover:bg-slate-200 text-slate-700 dark:bg-slate-800 dark:hover:bg-slate-700 dark:text-slate-200`
- Radius: `rounded-lg`, Border: `border border-slate-300 dark:border-slate-600`
Danger Button:
- Background: `bg-red-600 hover:bg-red-700 text-white`
- Radius: `rounded-lg`, Padding: `px-3 py-1.5 text-sm font-medium`
Disabled:
- `opacity-50 cursor-not-allowed pointer-events-none`
Loading:
- Primary button styles preserved with inline spinning `Loader2` SVG icon and text replacement (e.g., "Scanning...").

## 9. Inputs
Default:
- `w-full px-3 py-2 text-sm bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-slate-100 placeholder-slate-400`
Focus:
- `outline-none ring-2 ring-indigo-500 border-transparent`
Error:
- `border-red-500 focus:ring-red-500 text-red-900 dark:text-red-300`
Disabled:
- `bg-slate-100 dark:bg-slate-800 text-slate-400 dark:text-slate-600 cursor-not-allowed`
Placeholder:
- `text-slate-400 dark:text-slate-500 italic`

## 10. Cards
- Padding: 20px (`p-5` or `p-6`)
- Border: `1px solid #E2E8F0` (`border-slate-200 dark:border-slate-800`)
- Radius: `12px` (`rounded-xl`)
- Shadow: `shadow-sm hover:shadow-md transition-shadow`
- Surface: `bg-white dark:bg-slate-800/80 backdrop-blur-sm`

## 11. Navigation
Header:
- Fixed or sticky top bar, `h-16 border-b border-slate-200 dark:border-slate-800 bg-white/95 dark:bg-slate-900/95 backdrop-blur px-6 flex items-center justify-between`.
- Contains Brand logo, App title, Theme switch toggle (`Sun`/`Moon`), and System Status indicators.
Tab Navigation:
- Horizontal tab pill navigation (`Rules`, `Monitored Folders`, `Duplicate Finder`, `Rule Tester`, `Audit Logs`).
- Active tab marked by `bg-indigo-50 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300 font-semibold rounded-lg px-3 py-2`.
Sidebar / Mobile Navigation:
- FileFlow is a desktop application targeted at standard 16:9 and 16:10 desktop monitors; primary navigation is housed in the top tab strip to preserve vertical canvas height for file listings and rule cards.

## 12. States
Loading:
- Subtle skeleton pulse (`animate-pulse bg-slate-200 dark:bg-slate-700 rounded`) or centered `Loader2` rotating spinner.
Empty:
- Illustrated empty state with Lucide icons (`FolderSearch`, `FileText`, `Sparkles`), comforting descriptive prompt, and a prominent call-to-action button (e.g. "+ Create Your First Rule").
Error:
- Red-tinted card (`bg-red-50 border-red-200 dark:bg-red-950/40 dark:border-red-800/60`), clear error message, and a "Retry" or "Dismiss" action.
Success:
- Emerald badge or ephemeral toast confirmation (`bg-emerald-50 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300`).
Disabled:
- Grayscale contrast reduction (`opacity-60 saturate-50`).

## 13. Icons
Icon Library: `lucide-react` (v0.359+)
Default Size: 18px (`w-[18px] h-[18px]` or `w-4 h-4` for compact inline elements)
Icon Style: Outline, 2px stroke width, consistent rounded caps and joins.

## 14. Responsive Design
Mobile: Not applicable (desktop-first Windows application).
Tablet / Compact Window: Min width 850px supported with stacked card layout.
Desktop: Standard desktop viewport (1024px to 1920px+). Fluid max-width containers (`max-w-7xl mx-auto px-6 py-6`).
Breakpoints:
- Compact Desktop: `850px - 1024px`
- Standard Desktop: `1024px - 1440px`
- Wide Desktop: `1440px+`

## 15. Accessibility
- Use semantic HTML tags (`<main>`, `<header>`, `<nav>`, `<section>`, `<article>`, `<button>`).
- Maintain sufficient contrast: minimum 4.5:1 text-to-background contrast ratio in both Light and Dark themes.
- Support keyboard navigation: Full tab navigation, `Enter` / `Space` activation on buttons and toggles, `Escape` key closes open modals.
- Provide visible focus states: High-visibility indigo outline rings on all focused interactive elements (`focus:ring-2 focus:ring-indigo-500`).
- Provide accessible labels: All icon-only buttons include `title`, `aria-label`, and screen-reader descriptive text.
- Do not rely only on color: Error, Warning, and Success indicators pair iconography (`CheckCircle`, `AlertTriangle`, `XCircle`) with descriptive textual labels.
