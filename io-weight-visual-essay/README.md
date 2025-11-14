# The Weight of I/O

An interactive, two-act visual essay that makes the physics of data storage visceral through stunning animations and visceral interactions.

## Overview

This is not just a demo—it's an art piece designed to engrain fundamental database concepts in your mind. Experience the brutal trade-offs between B-Trees and LSM-Trees through physics-based animations that make you *feel* the latency, the waste, and the profound elegance of these data structures.

### The Core Thesis

We tell a story of trade-offs:
- Start with the lie of a "fast write"
- Reveal its true cost: chaotic cascading hunts across dozens of files (Read Amplification)
- Zoom into the fundamental law of disk I/O that governs everything
- Discover the one data structure honest enough to obey it

## Features

### Act I: The Choice
Choose your world:
- **The Citadel** (RDBMS B-Tree): Perfect order. Precise reads. Expensive writes.
- **The Frontier** (LSM-Tree): Chaotic freedom. Instant writes. Costly reads.

### Act II: The Nature of Storage

#### The Citadel (B-Tree)
- **Write Operations**: Watch the brutal in-place modification
  - Multi-step disk seeks through tree levels
  - Page locking and blocking
  - Heavy reorganization to maintain sort order
  - The spectacular split cascade when pages overflow

- **Read Operations**: Experience the precise, predictable path
  - Clean logarithmic traversal
  - Direct navigation through index levels
  - Guaranteed O(log n) performance

#### The Frontier (LSM-Tree)
- **Write Operations**: Feel the instant append-only magic
  - Lightning-fast memtable absorption
  - Batched disk writes on flush
  - Deceptively cheap... at first

- **Read Operations**: Live through "The Hunt"
  - Sequential scanning through overlapping SSTables
  - Unpredictable I/O costs
  - The price of write optimization

### Act III: The Synthesis
A dashboard revealing the brutal truth of your workload:
- Average write I/O comparison
- Average read I/O comparison
- Total operation counts
- Key insights about trade-offs

## Technical Stack

- **React 18** with TypeScript
- **Vite** for blazing-fast builds
- **Framer Motion** for physics-based animations
- **Dark brutalist aesthetic** inspired by Awwwards.com
- Fully responsive design

## Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Design Philosophy

### Aesthetic
- **Dark Mode**: Deep blacks (#0A0A0A) with electric accents
- **Brutalist Typography**: Bold, uppercase, high-contrast
- **Physics-Based Motion**: Every animation has weight and momentum
- **Two Accent Colors**:
  - Cyan (#00FFC2) for The Citadel/B-Tree
  - Magenta (#FF006E) for The Frontier/LSM-Tree

### Interaction Design
- **Visceral Feedback**: Every I/O operation is visible and felt
- **Progressive Revelation**: Concepts unfold through interaction
- **No Hand-Holding**: Users discover trade-offs through experience
- **Memorable Moments**: The split cascade, the hunt, the synthesis

## Educational Goals

After experiencing this essay, users will:

1. **Understand** the fundamental trade-off between read and write performance
2. **Feel** the cost of maintaining perfect order (B-Tree writes)
3. **Experience** the chaos of read amplification (LSM-Tree reads)
4. **Recognize** that there is no "best" data structure
5. **Remember** these concepts viscerally, not just intellectually

## Architecture

```
src/
├── components/
│   ├── TheChoice.tsx          # Landing page - world selection
│   ├── TheCitadel.tsx         # B-Tree visualization
│   ├── TheFrontier.tsx        # LSM-Tree visualization
│   ├── TheDashboard.tsx       # Results comparison
│   ├── IOCounter.tsx          # Animated I/O counter
│   └── WorldToggle.tsx        # Navigation toggle
├── types.ts                   # TypeScript definitions
├── App.tsx                    # Main app orchestration
└── index.css                  # Global styles
```

## Key Concepts Demonstrated

### B-Tree (The Citadel)
- In-place updates requiring reads before writes
- Page-level locking and concurrency issues
- Node splitting and tree rebalancing
- Predictable O(log n) reads
- Write amplification from maintaining order

### LSM-Tree (The Frontier)
- Append-only writes to memtable
- Batched flushing to SSTables
- Multiple overlapping levels
- Read amplification from scanning multiple files
- Write optimization at the cost of read performance

## Inspiration

This project draws inspiration from:
- **Martin Kleppmann's** "Designing Data-Intensive Applications"
- **Richard Feynman's** approach to teaching physics
- **Awwwards.com** brutalist design trends
- **Bret Victor's** explorable explanations

## Performance

- Fast initial load (< 1s)
- Smooth 60fps animations
- Optimized React rendering
- Minimal bundle size with code splitting

## Browser Support

- Chrome/Edge (recommended)
- Firefox
- Safari
- Mobile browsers (responsive design)

## License

MIT

## Credits

Built with passion for teaching the beauty and brutality of database internals.

---

**Remember**: There is no best. There is only the weight of I/O. Choose your trade-off.
