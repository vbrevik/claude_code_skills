---
name: shadcn-ui
description: "Add shadcn/ui components to a themed React project. Handles component installation, customisation, and combining components into working patterns."
---

# shadcn-ui Components

Add shadcn/ui components to a themed React project. This skill runs AFTER `tailwind-theme-builder` has set up CSS variables, ThemeProvider, and dark mode. It handles component installation, customisation, and combining components into working patterns.

**Prerequisite**: Theme infrastructure must exist (CSS variables, components.json, cn() utility). Use `tailwind-theme-builder` first if not set up.

## Installation Order

Install components in dependency order. Foundation components first, then feature components:

### Foundation (install first)

```bash
pnpm dlx shadcn@latest add button
pnpm dlx shadcn@latest add input label
pnpm dlx shadcn@latest add card
```

### Feature Components (install as needed)

```bash
# Forms
pnpm dlx shadcn@latest add form        # needs: react-hook-form, zod, @hookform/resolvers
pnpm dlx shadcn@latest add textarea select checkbox switch

# Feedback
pnpm dlx shadcn@latest add toast        # needs: sonner
pnpm dlx shadcn@latest add alert badge

# Overlay
pnpm dlx shadcn@latest add dialog sheet popover dropdown-menu

# Data Display
pnpm dlx shadcn@latest add table        # for data tables, also: @tanstack/react-table
pnpm dlx shadcn@latest add tabs separator avatar

# Navigation
pnpm dlx shadcn@latest add navigation-menu command
```

### External Dependencies

| Component | Requires |
|-----------|----------|
| Form | `react-hook-form`, `zod`, `@hookform/resolvers` |
| Toast | `sonner` |
| Data Table | `@tanstack/react-table` |
| Command | `cmdk` |
| Date Picker | `date-fns` (optional) |

Install external deps separately: `pnpm add react-hook-form zod @hookform/resolvers`

## Known Gotchas

### Radix Select — No Empty Strings

```tsx
// BREAKS
<SelectItem value="">All</SelectItem>

// WORKS — use sentinel value
<SelectItem value="__any__">All</SelectItem>
const actual = value === "__any__" ? "" : value
```

### React Hook Form — Null Values

```tsx
// Don't spread {...field} — it passes null which Input rejects
<Input
  value={field.value ?? ''}
  onChange={field.onChange}
  onBlur={field.onBlur}
  name={field.name}
  ref={field.ref}
/>
```

### Lucide Icons — Tree-Shaking

```tsx
// BREAKS in prod — dynamic import gets tree-shaken
import * as LucideIcons from 'lucide-react'
const Icon = LucideIcons[iconName]

// WORKS — explicit map
import { Home, Users, Settings, type LucideIcon } from 'lucide-react'
const ICON_MAP: Record<string, LucideIcon> = { Home, Users, Settings }
const Icon = ICON_MAP[iconName]
```

### Dialog Width Override

```tsx
// DOESN'T WORK — default sm:max-w-lg wins
<DialogContent className="max-w-6xl">

// WORKS — use same breakpoint prefix
<DialogContent className="sm:max-w-6xl">
```

## Customising Components

### Variant Extension

Add custom variants by editing the component file in `src/components/ui/`:

```tsx
// button.tsx — add a "brand" variant
const buttonVariants = cva("...", {
  variants: {
    variant: {
      default: "bg-primary text-primary-foreground",
      brand: "bg-brand text-brand-foreground hover:bg-brand/90",
    },
  },
})
```

### Colour Overrides

Use semantic tokens from your theme — never raw Tailwind colours:

```tsx
// WRONG
<Button className="bg-blue-500">

// RIGHT
<Button className="bg-primary">
<Card className="bg-card text-card-foreground">
```

## Workflow

### Step 1: Assess Needs

| Need | Components |
|------|-----------|
| Forms with validation | Form, Input, Label, Select, Textarea, Button, Toast |
| Data display with sorting | Table, Badge, Pagination |
| Admin CRUD interface | Dialog, Form, Table, Button, Toast |
| Marketing/landing page | Card, Button, Badge, Separator |
| Settings/preferences | Tabs, Form, Switch, Select, Toast |
| Navigation | NavigationMenu (desktop), Sheet (mobile), ModeToggle |

### Step 2: Install Components

Foundation first, then feature components for identified needs.

### Step 3: Build Recipes

Combine components into working patterns. See [references/recipes.md](references/recipes.md) for complete examples:

- **Contact Form** — Form + Input + Textarea + Button + Toast
- **Data Table** — Table + Column sorting + Pagination + Search
- **Modal CRUD** — Dialog + Form + Button
- **Navigation** — Sheet + NavigationMenu + ModeToggle
- **Settings Page** — Tabs + Form + Switch + Select + Toast

### Step 4: Customise

Apply project-specific colours and variants using semantic tokens.

## Reference Files

| When | Read |
|------|------|
| Choosing components, install commands, props | [references/component-catalogue.md](references/component-catalogue.md) |
| Building complete UI patterns | [references/recipes.md](references/recipes.md) |
