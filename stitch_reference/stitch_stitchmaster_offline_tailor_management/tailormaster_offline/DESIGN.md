---
name: TailorMaster Offline
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#45474c'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#75777d'
  outline-variant: '#c5c6cd'
  surface-tint: '#545f73'
  primary: '#091426'
  on-primary: '#ffffff'
  primary-container: '#1e293b'
  on-primary-container: '#8590a6'
  inverse-primary: '#bcc7de'
  secondary: '#5d5f5b'
  on-secondary: '#ffffff'
  secondary-container: '#e0e0db'
  on-secondary-container: '#62635f'
  tertiary: '#221000'
  on-tertiary: '#ffffff'
  tertiary-container: '#3f2200'
  on-tertiary-container: '#b58759'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d8e3fb'
  primary-fixed-dim: '#bcc7de'
  on-primary-fixed: '#111c2d'
  on-primary-fixed-variant: '#3c475a'
  secondary-fixed: '#e3e3de'
  secondary-fixed-dim: '#c6c7c2'
  on-secondary-fixed: '#1a1c19'
  on-secondary-fixed-variant: '#454744'
  tertiary-fixed: '#ffdcbd'
  tertiary-fixed-dim: '#f0bd8b'
  on-tertiary-fixed: '#2c1600'
  on-tertiary-fixed-variant: '#623f18'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  display:
    fontFamily: Public Sans
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Public Sans
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
  headline-md:
    fontFamily: Public Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Public Sans
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Public Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-lg:
    fontFamily: Public Sans
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Public Sans
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.04em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  sidebar_width: 280px
  header_height: 72px
  container_padding: 40px
  gutter: 24px
  stack_sm: 8px
  stack_md: 16px
  stack_lg: 32px
---

## Brand & Style

The design system is built for a premium, local craft environment. It balances the precision of tailoring with the warmth of a boutique experience. The visual language follows a **Corporate / Modern** approach with a **Tactile** influence, emphasizing high-quality materials through subtle textures and soft elevation.

The goal is to evoke a sense of organized mastery. The UI should feel lightweight and reliable, avoiding the "heavy enterprise" feel of typical management software in favor of an approachable, workshop-friendly interface. Whitespace is used as a primary design tool to ensure clarity for users who are often multitasking between physical craft and digital logging.

## Colors

The palette is rooted in heritage and professionalism.
- **Primary:** A deep, professional Navy (#1E293B) used for high-emphasis actions and navigational anchors.
- **Secondary/Surface:** Warm neutrals like Cream and Soft Beige (#F5F5F0) replace harsh whites to reduce eye strain and provide a premium "paper and fabric" feel.
- **Tertiary:** A muted gold/tan (#D4A373) used for subtle accents, highlights, or premium status indicators.
- **Status Colors:** High-contrast, classic tones for Success (Deep Green), Warning (Amber), and Urgent (Rich Red) to ensure immediate legibility against the warm neutral background.

## Typography

This design system utilizes **Public Sans** for its exceptional legibility and institutional yet friendly character. 

- **Scale:** The system prioritizes large font sizes for primary labels (16px-18px) to accommodate quick glancing in a busy shop environment.
- **Hierarchy:** Strong weight contrast is used to separate data labels from user-generated content.
- **Readability:** Line heights are generous (1.5x for body text) to ensure that measurements and customer details are never misread.

## Layout & Spacing

The layout is a **Fixed Grid** desktop model designed for structural stability.
- **Sidebar:** A permanent 280px left navigation bar provides a consistent anchor. It should use the primary navy color to differentiate the "control" area from the "work" area.
- **Header:** A clean 72px global header contains page titles and global actions (e.g., "New Order").
- **Main Content:** A spacious area with 40px outer padding. Content is organized in centralized cards to prevent information from stretching too wide on ultra-wide monitors.
- **Rhythm:** Use a 8px linear scale. Elements are grouped with 16px or 32px gaps to maintain a sense of airiness and reduce visual noise.

## Elevation & Depth

Visual hierarchy is achieved through **Tonal Layers** combined with **Ambient Shadows**.
- **Surface:** The main background is the secondary neutral (Soft Beige). 
- **Cards:** White surfaces (#FFFFFF) are lifted off the background using a soft, diffused shadow (0px 4px 20px rgba(0, 0, 0, 0.05)).
- **Active Elements:** Interactive elements like dropdowns or modals use a more pronounced shadow (0px 10px 30px rgba(0, 0, 0, 0.1)) to indicate they are closer to the user.
- **Interactive States:** Buttons subtly "press" down (reduce shadow and slightly darken color) to provide tactile feedback.

## Shapes

The shape language is consistently **Rounded**, reflecting the soft nature of fabrics and approachable service.
- **Standard Radius:** 12px (0.75rem) for cards and input fields.
- **Button Radius:** 12px for standard buttons; 16px for large "Call to Action" buttons.
- **Badges:** Fully pill-shaped (rounded-full) to distinguish them from interactive buttons.
- **Icons:** Use rounded-corner iconography (2px corner radius on glyphs) to match the UI container language.

## Components

### Buttons
- **Primary:** Navy background, white text, 12px-16px height padding. Must include a leading icon (e.g., + for New Order).
- **Secondary:** Cream background with a subtle 1px border (#CBD5E1), navy text.
- **Large Action:** Used for the main dashboard tasks; 64px height with `label-lg` typography.

### Input Fields
- **Design:** 12px rounded corners, 1px border (#CBD5E1). Focus state uses a 2px navy border.
- **Labels:** Always positioned above the input using `label-lg` for maximum clarity.

### Cards
- White background, 12px radius, soft ambient shadow. Used to wrap individual customer records or order details.

### Status Badges
- Small, pill-shaped tags. Background is a 10% opacity version of the status color (e.g., 10% Green), text is the full-strength status color.

### Lists
- Avoid dense table rows. Use "List Cards" where each row has its own white background and vertical breathing room, separated by 8px gaps rather than lines.

### Specialized Components
- **Measurement Grid:** A specialized input group using larger-than-standard font sizes for numeric entry (Inseam, Waist, etc.).
- **Order Timeline:** A vertical stepper indicating the stage of a garment (Cut, Sew, Fitting, Ready).