# Color Palette - BiashaRaiq

## Primary Colors

| Color Name | Hex Value | Usage | CSS Variable |
|------------|-----------|-------|--------------|
| **Primary Navy** | `#0A2540` | Cards, Headers, Primary Backgrounds | `--primary-navy` |
| **White** | `#FFFFFF` | Text on dark backgrounds, Secondary backgrounds | `--text-white` |

## Semantic Colors

| Color Name | Hex Value | Usage | CSS Variable |
|------------|-----------|-------|--------------|
| **Success Green** | `#2E7D32` | Positive balances, Income, Growth indicators | `--success-green` / `--accent-green` |
| **Error Red** | `#D32F2F` | Spending, Outgoing transactions, Alerts | `--error-red` / `--accent-red` |
| **Text Dark Gray** | `#1E1E1E` | Body text, Primary text | `--text-dark` / `--text-primary` |
| **Background Light Gray** | `#F5F5F5` | Backgrounds, Borders, Subtle elements | `--bg-light-gray` |

## Accent Colors (Optional)

| Color Name | Hex Value | Usage | CSS Variable |
|------------|-----------|-------|--------------|
| **Visa Blue** | `#1A1F71` | Optional accent, Premium features | `--accent-blue` |
| **Visa Gold** | `#F9A825` | Optional accent, Premium features, Highlights | `--accent-gold` |

## Usage Guide

### Tailwind Classes

Use the configured color palettes in your Tailwind classes:

```html
<!-- Navy backgrounds -->
<div class="bg-navy-950">Primary Navy</div>

<!-- Semantic colors -->
<div class="bg-semantic-success">Success (Green)</div>
<div class="bg-semantic-error">Error (Red)</div>
<div class="bg-semantic-textLight">Light background</div>

<!-- Text colors -->
<div class="text-semantic-textDark">Dark text</div>
```

### CSS Variables

Access colors via CSS variables in your stylesheets:

```css
.my-element {
  background: var(--primary-navy);
  color: var(--text-white);
  border: 1px solid var(--bg-light-gray);
}

.success-indicator {
  color: var(--success-green);
  box-shadow: 0 0 24px rgba(46, 125, 50, 0.25);
}

.error-indicator {
  color: var(--error-red);
  box-shadow: 0 0 20px rgba(211, 47, 47, 0.15);
}
```

### Component Examples

#### Cards
- Background: `--primary-navy` (#0A2540)
- Text: `--text-white` (#FFFFFF)
- Border: `--bg-light-gray` (#F5F5F5)

#### Positive Balance Indicators
- Text Color: `--success-green` (#2E7D32)
- Glow: `0 0 24px rgba(46, 125, 50, 0.25)`

#### Spending/Negative Indicators
- Text Color: `--error-red` (#D32F2F)
- Glow: `0 0 20px rgba(211, 47, 47, 0.15)`

#### Premium Features
- Accent: `--accent-gold` (#F9A825)
- Alternative: `--accent-blue` (#1A1F71)

## Color Harmony

**Light Theme Backgrounds:**
- Primary: #F5F5F5 (Light Gray)
- Secondary: #FFFFFF (White)

**Dark Theme Backgrounds:**
- Primary: #0A2540 (Navy)
- Hover: #134282 (Navy Light)

**Text:**
- On Light: #1E1E1E (Dark Gray)
- On Dark: #FFFFFF (White)

**Interactive Elements:**
- Success: #2E7D32 (Green)
- Error: #D32F2F (Red)
- Accent: #F9A825 (Gold) or #1A1F71 (Blue)

## Configuration Files

Colors are configured in:
- **Tailwind**: `tailwind.config.js` (color definitions)
- **CSS**: `src/app/globals.css` (CSS variables)

Update these files when modifying the color scheme.
