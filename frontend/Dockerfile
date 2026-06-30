FROM nginx:1.27-alpine

COPY app /usr/share/nginx/html

EXPOSE 80

CMD ["/bin/sh", "-c", "printf 'window.APP_CONFIG = { apiUrl: \"%s\", googleMapsApiKey: \"%s\" };\\n' \"${NEXT_PUBLIC_API_URL:-http://localhost:8000}\" \"${NEXT_PUBLIC_GOOGLE_MAPS_BROWSER_KEY:-}\" > /usr/share/nginx/html/config.js && nginx -g 'daemon off;'"]
