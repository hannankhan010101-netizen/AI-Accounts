import { ImageResponse } from "next/og";

export const size = { width: 180, height: 180 };
export const contentType = "image/png";

export default function AppleIcon() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "linear-gradient(145deg, #f4f7f0 0%, #e4ebe0 55%, #d8e2d0 100%)",
          borderRadius: 36,
          border: "3px solid rgba(85, 107, 71, 0.18)",
        }}
      >
        <svg width="108" height="108" viewBox="0 0 24 24" fill="none">
          <rect
            x="3.5"
            y="2.5"
            width="13.5"
            height="18"
            rx="2.25"
            stroke="#556b47"
            strokeWidth="1.65"
          />
          <path
            d="M6.75 7.25h7.5M6.75 10h5.5"
            stroke="#556b47"
            strokeWidth="1.35"
            strokeLinecap="round"
            opacity="0.45"
          />
          <rect x="6.75" y="14.25" width="2.1" height="3.75" rx="0.55" fill="#556b47" />
          <rect x="9.65" y="12.35" width="2.1" height="5.65" rx="0.55" fill="#6d8560" />
          <rect x="12.55" y="10.45" width="2.1" height="7.55" rx="0.55" fill="#465a3b" />
          <path
            d="M16.25 4.35l.55 1.1 1.1.55-1.1.55-.55 1.1-.55-1.1-1.1-.55 1.1-.55z"
            fill="#556b47"
          />
          <circle cx="18.35" cy="8.15" r="1.05" fill="#6d8560" />
          <path
            d="M16.9 7.1c1.15-.35 2 .35 2.45 1.45"
            stroke="#556b47"
            strokeWidth="1.2"
            strokeLinecap="round"
            opacity="0.75"
          />
          <path
            d="M18.35 9.2v2.35M17.2 10.35h2.3"
            stroke="#6d8560"
            strokeWidth="1.1"
            strokeLinecap="round"
            opacity="0.55"
          />
        </svg>
      </div>
    ),
    { ...size },
  );
}
