/**
 * Minimal SVG representation of the Flag of Bharat (India).
 * Three horizontal bands: saffron, white, green — with Ashoka Chakra in center.
 *
 * NOTE: Flag colors (#FF9933, #138808, #000080) are constitutionally mandated
 * values defined in global.css as --color-flag-* tokens. SVG fill attributes
 * cannot consume CSS variables directly, so these are the only raw values
 * permitted in JSX — they map 1:1 to their global.css counterparts.
 */
export default function BharatFlag() {
  return (
    <svg
      width="36"
      height="24"
      viewBox="0 0 36 24"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="Flag of Bharat"
      role="img"
      className="rounded-sm shadow-md"
    >
      {/* Saffron — var(--color-flag-saffron) */}
      <rect x="0" y="0" width="36" height="8" fill="#FF9933" />
      {/* White — var(--color-flag-white) */}
      <rect x="0" y="8" width="36" height="8" fill="#FFFFFF" />
      {/* Green — var(--color-flag-green) */}
      <rect x="0" y="16" width="36" height="8" fill="#138808" />
      {/* Ashoka Chakra — var(--color-flag-chakra) */}
      <circle cx="18" cy="12" r="3.2" fill="none" stroke="#000080" strokeWidth="0.6" />
      {Array.from({ length: 24 }).map((_, i) => {
        const angle = (i * 360) / 24;
        const rad = (angle * Math.PI) / 180;
        const x1 = 18 + 1.1 * Math.cos(rad);
        const y1 = 12 + 1.1 * Math.sin(rad);
        const x2 = 18 + 3.2 * Math.cos(rad);
        const y2 = 12 + 3.2 * Math.sin(rad);
        return (
          <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke="#000080" strokeWidth="0.4" />
        );
      })}
      <circle cx="18" cy="12" r="0.7" fill="#000080" />
    </svg>
  );
}
