# Hero Design Principles

## Core Purpose

A hero section should create an emotional first impression that reflects the brand personality — establishing what visitors should feel upon arrival.

## Strategic Questions Before Designing

- What emotional response matters most?
- What visual assets exist?
- What action should visitors take?
- Which device dominates traffic?
- What's the brand personality?

## Three Primary Approaches

### Image-Dominant
Use when strong photography exists. Let imagery lead while keeping text minimal and purposefully placed within the composition.

- Let the image do the work, minimal text overlay
- One clear focal point in the image
- Text placed within the image's natural composition, not slapped on top
- Overlay only when necessary for legibility

### Typography-Dominant
Choose when imagery is weak but brand voice is distinctive. Make typography itself the design through dramatic hierarchy and generous whitespace.

- Font choice, size, weight, spacing IS the design
- Generous whitespace as active design element
- Colour blocking or subtle texture instead of stock photos
- Strong headline hierarchy: hero title 3-4x body size

### Balanced/Split
Employ when both strong copy and visuals exist, ensuring one element slightly dominates to maintain visual direction.

- One side dominates slightly — true 50/50 feels indecisive
- On mobile, order matters — which element first in vertical stack?
- Image side can use background shapes or overlapping elements for depth

## Industry-Specific Patterns

### Emergency Services
Bold, high-contrast typography with prominent phone numbers and trust signals. Phone number visible without scrolling. Direct language: "24/7 Emergency Plumber" not "Welcome to Our Plumbing Company."

### Luxury/Hospitality
Generous whitespace as a design feature. Atmospheric, full-bleed imagery. Refined typography. Minimal text. Let the experience sell itself.

### Professional Services
Clean structure with clear value proposition. Credentials visible early. Confident but not flashy. Structured layout that implies reliability.

### Creative/Agency
Bold, unconventional choices. Typography as personality. Show your work, don't just tell. Design should demonstrate your design capabilities.

## Design Red Flags (Avoid)

- Perfect centering with equal visual weight on all elements
- Generic overlays on stock photos
- "Learn More" or "Get Started" as hero CTA
- Cookie-cutter template layouts
- Decorative elements serving no purpose
- Text that doesn't respect image composition

## Hallmarks of Human Design

- Clear visual dominance by one element
- Intentional asymmetry and tension
- Specific, opinionated headlines
- Purposeful whitespace
- Explainable design decisions ("this is large because...")
- Appropriate restraint — not every technique used

## Responsive Behaviour

- Hero images need art direction at breakpoints, not just scaling
- Typography uses `clamp()` for fluid sizing: `clamp(2.5rem, 6vw, 5rem)`
- Mobile hero should prioritise CTA visibility
- Consider different image crops for mobile vs desktop
- Stack split layouts vertically on mobile — content order matters

## Page-Specific Heroes

### Homepage
Biggest, boldest hero. Brand statement + primary CTA. Full-height or near-full-height acceptable.

### Service Pages
Smaller hero. Service name + brief description. Trust signal if relevant. Don't compete with homepage hero size.

### About Page
Can be more personal — team photo, founder story angle. Doesn't need a CTA.

### Contact Page
Minimal hero or none. The form IS the content. Don't put barriers before the form.

### Blog/Content
Article title IS the hero. Author, date, reading time. Featured image optional.
