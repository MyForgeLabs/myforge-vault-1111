---
name: WordPress Schema.org bővítés mu-plugin mintával
description: Yoast-on túl gazdag JSON-LD strukturált adat (Dentist/LocalBusiness/Person/MedicalProcedure/FAQPage) — minta-implementáció
type: wiki
created: 2026-05-04
tags: ["#tech/wordpress", "#tech/seo", "#tech/schema-org"]
---

# Schema.org bővítés WordPress-ben mu-plugin-nel

Yoast SEO default csak alap schema-t emit-el (`WebPage`, `WebSite`, `BreadcrumbList`). Lokális üzletek (orvosi rendelő, étterem, bolt) **gazdagabb schema-val** rangsorolnak jobban a Google-on (Knowledge Graph, Rich Snippets, Local Pack).

## A 5 leggyakrabban hiányzó schema-típus

| Schema | Mit ad | Hol emit-elni |
|---|---|---|
| `LocalBusiness` (subtype: `Dentist`, `Restaurant`, `Store`, …) | Cím, GPS, nyitvatartás, telefon → Google Maps + lokális SEO | Minden oldalon |
| `Person` | Vezető, szakorvos, séf — képesítés, szakmai-tagság | About / Rólunk oldalakon |
| `Service` / `MedicalProcedure` | Egyéni szolgáltatás | Service-detail page-ek |
| `FAQPage` | Q&A → Google rich-snippet ("expand FAQ") | Bármely accordion-tartalmú page |
| `Review` / `AggregateRating` | Vásárlói vélemények csillag-értékelés | Termék/szolgáltatás-page-ek |

## Mu-plugin minta-szerkezet

```php
<?php
/**
 * Plugin Name: My Site — Schema.org structured data
 */
if (!defined('ABSPATH')) exit;

// 1. Site-wide LocalBusiness (minden oldalon)
add_action('wp_head', 'my_schema_localbusiness', 5);
function my_schema_localbusiness() {
  if (is_admin()) return;
  $data = [
    "@context" => "https://schema.org",
    "@graph" => [[
      "@type" => ["Dentist", "LocalBusiness"],
      "@id"   => home_url('/') . '#business',
      "name"  => get_bloginfo('name'),
      "telephone" => "+36-30-XXX-YYYY",
      "address" => [
        "@type" => "PostalAddress",
        "streetAddress"   => "...",
        "addressLocality" => "Budapest",
        "postalCode"      => "1024",
        "addressCountry"  => "HU",
      ],
      "geo" => [
        "@type" => "GeoCoordinates",
        "latitude"  => 47.5067,
        "longitude" => 19.0247,
      ],
      "openingHoursSpecification" => [[
        "@type" => "OpeningHoursSpecification",
        "dayOfWeek" => ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "opens"  => "08:00",
        "closes" => "18:00",
      ]],
      "medicalSpecialty" => ["Orthodontics", "Dentistry"],
    ]]
  ];
  echo '<script type="application/ld+json">' . wp_json_encode($data, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . "</script>\n";
}

// 2. Person (about-pages-en)
add_action('wp_head', 'my_schema_person', 6);
function my_schema_person() {
  global $post;
  if (!is_singular() || !in_array($post->ID, [17, 586])) return; // about-page IDs
  // ... Person schema with @id, alma mater, memberOf, knowsLanguage, knowsAbout
}

// 3. FAQPage — DINAMIKUSAN accordion-widget tartalmából
add_action('wp_head', 'my_schema_faqpage', 8);
function my_schema_faqpage() {
  global $post;
  if (!is_singular()) return;
  $raw = get_post_meta($post->ID, '_elementor_data', true);
  $data = json_decode($raw, true);
  $faqs = [];
  $walker = function ($node) use (&$walker, &$faqs) {
    if (is_array($node)) {
      if (($node['widgetType'] ?? '') === 'foxxi-accordions') {
        foreach (($node['settings']['accordions'] ?? []) as $a) {
          $q = trim(wp_strip_all_tags($a['question'] ?? ''));
          $ans = trim(wp_strip_all_tags($a['answer'] ?? ''));
          if ($q && $ans) $faqs[] = ['q' => $q, 'a' => $ans];
        }
      }
      foreach ($node as $v) if (is_array($v)) $walker($v);
    }
  };
  $walker($data);
  if (empty($faqs)) return;
  $entities = array_map(fn($f) => [
    "@type" => "Question",
    "name" => $f['q'],
    "acceptedAnswer" => ["@type" => "Answer", "text" => $f['a']]
  ], $faqs);
  $faqpage = [
    "@context" => "https://schema.org",
    "@type" => "FAQPage",
    "mainEntity" => $entities
  ];
  echo '<script type="application/ld+json">' . wp_json_encode($faqpage) . "</script>\n";
}
```

## WPML-aware (multilingual)

A schema-output-ot a current language alapján kell adaptálni:

```php
$is_en = defined('ICL_LANGUAGE_CODE') && ICL_LANGUAGE_CODE === 'en';
$name = $is_en ? 'English Name' : 'Magyar név';
$desc = $is_en ? 'English description' : 'Magyar leírás';
```

Plus Person-szintű `jobTitle`, `description` is nyelvfüggő.

## Validation

Google Rich Results Test:
- https://search.google.com/test/rich-results
- Beilleszteni az élő URL-t
- Várt eredmény: a schema-típusok detekt-elve + példa-rich-snippet preview

Ha hiba van, a tool megmondja melyik field hiányzik / érvénytelen.

## Common gotchas

- **JSON_UNESCAPED_SLASHES + JSON_UNESCAPED_UNICODE** — a Schema-validátorok jobban kezelik a olvasható verziót
- **`@id`** mindig egyedi URL legyen (`home_url('/') . '#business'`) — egyébként a Google duplikátnak látja
- **Nested `@id`-referencia** (pl. Person → worksFor → @id Business-ra) — összeköti a graph-ban
- **`Dentist` + `LocalBusiness` array** — több @type-ot egyszerre lehet (mindkettő illik)

## Kapcsolódó

- [[wp-yoast-llms-txt-customization]]
- [[wpml-acf-elementor-multilingual-mirror]]
