const fs = require("fs");
const path = require("path");

const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const googleMapsApiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_BROWSER_KEY || "";
const outputPath = path.join(__dirname, "app", "config.js");

fs.writeFileSync(
  outputPath,
  `window.APP_CONFIG = ${JSON.stringify({ apiUrl, googleMapsApiKey })};\n`,
);
