/**
 * Stylised SVG emblem — gold on dark navy.
 * SVG presentation attributes can't use CSS var() directly;
 * CSS classes (.emblem-*) in NationalEmblem.css bridge that.
 */
import './NationalEmblem.css';

export default function NationalEmblem({ size = 120 }) {
  const cx = size / 2;
  const cy = size / 2;
  const r  = size / 2;

  return (
    <svg
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      xmlns="http://www.w3.org/2000/svg"
      aria-label="National Security Emblem"
      role="img"
    >
      {/* Background circle */}
      <circle cx={cx} cy={cy} r={r - 2} className="emblem-bg" strokeWidth="2" />

      {/* Outer decorative ring */}
      <circle cx={cx} cy={cy} r={r - 12} className="emblem-ring" strokeWidth="1" strokeDasharray="4 3" />

      {/* Ashoka Chakra */}
      <circle cx={cx} cy={cy} r={r * 0.28} className="emblem-ring" strokeWidth="1.2" />
      {Array.from({ length: 24 }).map((_, i) => {
        const angle = (i * 15 * Math.PI) / 180;
        const inner = r * 0.12;
        const outer = r * 0.28;
        return (
          <line
            key={i}
            x1={cx + inner * Math.cos(angle)}
            y1={cy + inner * Math.sin(angle)}
            x2={cx + outer * Math.cos(angle)}
            y2={cy + outer * Math.sin(angle)}
            className="emblem-ring"
            strokeWidth="0.7"
          />
        );
      })}
      <circle cx={cx} cy={cy} r={r * 0.07} className="emblem-fill" />

      {/* Arc label */}
      <defs>
        <path
          id="emblem-arc"
          d={`M ${cx - r + 14} ${cy} A ${r - 14} ${r - 14} 0 0 0 ${cx + r - 14} ${cy}`}
        />
      </defs>
      <text fontSize={size * 0.075} className="emblem-text" letterSpacing="2">
        <textPath href="#emblem-arc" startOffset="50%" textAnchor="middle">
          BHARAT SURAKSHA
        </textPath>
      </text>
    </svg>
  );
}
