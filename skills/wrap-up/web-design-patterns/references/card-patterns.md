# Card Design Principles

A thinking framework for card-based layouts that don't look AI-generated.

**Philosophy**: Cards are containers that signal "this is a discrete, scannable unit." But not every group of items should be cards, and not all cards should look identical.

---

## 1. When to Use Cards (vs. Other Patterns)

**Use cards when**:
- Items are independent and self-contained (services, team members, pricing tiers)
- Users need to scan and compare discrete options
- Each item has 2-4 distinct pieces of information (title, description, CTA)

**Don't use cards when**:
- Content is sequential (use numbered lists or timeline)
- There's a single narrative flow (use article layout or alternating rows)
- Items have deep hierarchy within them (use accordion or tabs)
- You have a single item (just use a content block)

## 2. Card Anatomy & Visual Hierarchy

Every card needs clear internal hierarchy. The eye should know where to look first, second, third.

**Typical reading order**:
1. Image or icon — instant visual recognition
2. Title — what is this?
3. Description — why should I care?
4. Metadata — supporting details
5. CTA — what's the next action?

---

## 3. Layout Decision Framework

### How Many Items? (Most Critical)

- **2 items**: Side-by-side equal OR one featured + one supporting
- **3 items**: Featured + 2 secondary OR equal 3-column
- **4 items**: Full-width featured + 3 below OR 2x2 grid
- **5 items**: Bento with 2x2 featured OR 2+3 rows
- **6 items**: Bento with 2x2 featured OR 3+3 rows
- **7+ items**: Alternating rows OR simple responsive grid

**The orphan problem**: Never leave 1 card alone on a row.

### Is There Hierarchy in Importance?

**When hierarchy exists**: Featured card pattern — make important card 2x size, stronger CTA.
**When all items are equal**: Uniform grid with consistent dimensions.

### Content Density

- **Image-heavy**: 2-3 columns max, larger cards
- **Text-heavy**: 3-4 columns, smaller cards
- **Mixed**: Feature the image cards, icon-only cards can be denser

---

## 4. Anti-Sameness Strategies

### Strategy 1: Vary Card Sizes Based on Importance
Primary offering at 2x size with image. Secondary at standard size with icons. Tertiary as compact cards or list items.

### Strategy 2: Mix Card Formats Within a Section
Card 1: Image + title + description + link. Card 2: Icon + title + description + pricing link. Card 3: Large stat number + title + brief text.

### Strategy 3: Consider Non-Card Alternatives
- **Alternating rows**: Better for 3-5 detailed items with images
- **Numbered list**: Better for sequential steps or ranked items
- **Timeline**: Better for chronological content
- **Simple text blocks**: Better for benefits/features without images
- **Icon list**: Better for simple feature lists

### Strategy 4: Vary Visual Treatment
Even with similar structure: some cards with images, some with icons, some with neither. Different padding for featured cards.

---

## 5. Grid Math & Responsive

**2-column**: Image-heavy, detailed comparisons. Works for even counts.
**3-column**: Standard services, team, blog. Watch orphans with 4, 7, 10 items.
**4-column**: Compact cards, icon features. Needs generous whitespace.

**Orphan solutions**: Featured card spanning 2+ cells, alternating rows, full-width last card.

**Responsive**: Desktop = full grid. Tablet = 2 columns. Mobile = 1 column stacked.

---

## 6. Business Context

- **Services**: Clear hierarchy, 3-5 max per screen, strong CTAs
- **Team**: Founder gets featured treatment, real photos, personality details
- **Pricing**: 2-3 tiers, highlight recommended, align features for comparison
- **Portfolio**: Minimal chrome, images are hero, bento/masonry works well
- **Features**: Consider if cards are even needed (icon list might be better)

---

## 7. CSS Pattern: Uniform Heights

```css
.card-grid {
  display: grid;
  gap: var(--space-8);
  grid-template-columns: repeat(2, 1fr);
  align-items: stretch;
}

.card {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.card__content {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  padding: var(--space-6);
}

.card__description { flex-grow: 1; }
.card__tags { margin-top: auto; }
```

---

## 8. Quick Reference

| Scenario | Best Pattern | Key Principle |
|----------|-------------|---------------|
| Services (main offering clear) | Featured + grid | Show hierarchy |
| Services (all equal) | Simple 3-col grid | Clean and scannable |
| Team (with founder) | Featured founder + grid | Leadership stands out |
| Pricing | 3-col with featured middle | Guide decision |
| Portfolio | Bento or masonry | Let work speak |
| Features | Dense 4-col or icon list | Fast scanning |
