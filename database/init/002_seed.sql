INSERT INTO places (name, category, subtype, phone, website, address_text, lat, lng, wilaya, commune, source_status, verification_score, last_verified_at, google_place_id, google_maps_url)
VALUES
  ('Mode El Bahia', 'clothing_store', 'women', '+213 41 22 10 01', 'https://example.com/mode-el-bahia', 'Rue Larbi Ben M''hidi, Oran', 35.6993, -0.6352, 'Oran', 'Oran', 'verified', 86, now(), 'demo-oran-store-1', 'https://maps.google.com/?q=Mode+El+Bahia'),
  ('Boutique Jasmin', 'clothing_store', 'women', '+213 41 22 10 02', NULL, 'Centre-ville, Oran', 35.7011, -0.6331, 'Oran', 'Oran', 'verified', 74, now(), 'demo-oran-store-2', 'https://maps.google.com/?q=Boutique+Jasmin+Oran'),
  ('City Wear Oran', 'clothing_store', 'men', '+213 41 22 10 03', NULL, 'Rue Khemisti, Oran', 35.6968, -0.6370, 'Oran', 'Oran', 'candidate', 58, NULL, 'demo-oran-store-3', 'https://maps.google.com/?q=City+Wear+Oran'),
  ('Kids Corner Oran', 'clothing_store', 'kids', NULL, NULL, 'Plateau Saint Michel, Oran', 35.6936, -0.6287, 'Oran', 'Oran', 'verified', 68, now(), 'demo-oran-store-4', 'https://maps.google.com/?q=Kids+Corner+Oran'),
  ('Sport Mode Akid', 'clothing_store', 'sportswear', '+213 41 22 10 06', 'https://example.com/sport-mode', 'Akid Lotfi, Oran', 35.7302, -0.5564, 'Oran', 'Bir El Djir', 'verified', 82, now(), 'demo-oran-store-6', 'https://maps.google.com/?q=Sport+Mode+Akid'),
  ('Boutique Narjess', 'clothing_store', 'women', NULL, NULL, 'Akid Lotfi, Oran', 35.7281, -0.5596, 'Oran', 'Bir El Djir', 'candidate', 52, NULL, 'demo-oran-store-7', 'https://maps.google.com/?q=Boutique+Narjess+Oran'),
  ('Urban Shoes Oran', 'clothing_store', 'shoe_store', '+213 41 22 10 08', NULL, 'Bir El Djir', 35.7270, -0.5535, 'Oran', 'Bir El Djir', 'verified', 77, now(), 'demo-oran-store-8', 'https://maps.google.com/?q=Urban+Shoes+Oran'),
  ('Es Senia Fashion', 'clothing_store', 'general', '+213 41 22 10 09', NULL, 'Es Senia', 35.6512, -0.6243, 'Oran', 'Es Senia', 'verified', 81, now(), 'demo-oran-store-9', 'https://maps.google.com/?q=Es+Senia+Fashion'),
  ('Boutique Salam', 'clothing_store', 'men', NULL, NULL, 'Es Senia', 35.6539, -0.6206, 'Oran', 'Es Senia', 'candidate', 47, NULL, 'demo-oran-store-10', 'https://maps.google.com/?q=Boutique+Salam+Es+Senia'),
  ('Yalidine Oran Hub', 'delivery_company', 'courier', '+213 41 55 10 01', 'https://yalidine.com', 'Oran logistics zone', 35.6910, -0.6159, 'Oran', 'Oran', 'verified', 92, now(), 'demo-oran-delivery-1', 'https://maps.google.com/?q=Yalidine+Oran'),
  ('ZR Express Oran', 'delivery_company', 'last_mile', '+213 41 55 10 02', 'https://zr-express.com', 'Bir El Djir', 35.7234, -0.5682, 'Oran', 'Bir El Djir', 'verified', 88, now(), 'demo-oran-delivery-2', 'https://maps.google.com/?q=ZR+Express+Oran'),
  ('Nord Ouest Livraison', 'delivery_company', 'shipping', '+213 41 55 10 03', NULL, 'Es Senia', 35.6628, -0.6125, 'Oran', 'Es Senia', 'candidate', 61, NULL, 'demo-oran-delivery-3', 'https://maps.google.com/?q=livraison+Es+Senia')
ON CONFLICT DO NOTHING;

INSERT INTO place_sources (place_id, source_type, source_url, source_confidence, raw_reference_id)
SELECT id, 'google_places', google_maps_url, CASE WHEN source_status = 'verified' THEN 0.88 ELSE 0.62 END, google_place_id
FROM places
WHERE google_place_id IS NOT NULL
ON CONFLICT DO NOTHING;

INSERT INTO verification_checks (place_id, check_type, result, details, checked_by)
SELECT id, 'google_business_status', 'pass', 'Seeded candidate source says business exists; admin should verify active status.', 'seed'
FROM places
ON CONFLICT DO NOTHING;
