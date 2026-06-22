import { ImageResponse } from "next/og";

export const size = { width: 64, height: 64 };
export const contentType = "image/png";

export default function Icon() {
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
          borderRadius: 14,
        }}
      >
        <svg width="52" height="52" viewBox="0 0 32 32" fill="none">
          <rect x="1" y="1" width="30" height="30" rx="8" fill="rgba(85,107,71,0.12)" />
          <rect
            x="1"
            y="1"
            width="30"
            height="30"
            rx="8"
            stroke="rgba(85,107,71,0.22)"
            strokeWidth="1"
          />
          <rect
            x="7"
            y="6"
            width="13"
            height="18"
            rx="2"
            fill="rgba(85,107,71,0.12)"
            stroke="#556b47"
            strokeWidth="1.75"
          />
          <path
            d="M10 10.5h7M10 13.5h5"
            stroke="#556b47"
            strokeWidth="1.4"
            strokeLinecap="round"
            opacity="0.55"
          />
          <rect x="10" y="17.5" width="2.4" height="4" rx="0.6" fill="#556b47" />
          <rect x="13.2" y="15.5" width="2.4" height="6" rx="0.6" fill="#6d8560" />
          <rect x="16.4" y="13.5" width="2.4" height="8" rx="0.6" fill="#465a3b" />
          <path
            d="M21.5 8.2l.75 1.5 1.5.75-1.5.75-.75 1.5-.75-1.5-1.5-.75 1.5-.75z"
            fill="#556b47"
          />
          <circle cx="23.8" cy="12.2" r="1.35" fill="#6d8560" />
          <path
            d="M22.2 11c1.2-.45 2.1.35 2.55 1.55"
            stroke="#556b47"
            strokeWidth="1.35"
            strokeLinecap="round"
          />
        </svg>
      </div>
    ),
    { ...size },
  );
}
