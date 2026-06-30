const fs = require("fs");

const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const googleMapsApiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_BROWSER_KEY || "";

fs.writeFileSync(
  "app/config.js",
  `window.APP_CONFIG = ${JSON.stringify({ apiUrl, googleMapsApiKey })};\n`,
);
