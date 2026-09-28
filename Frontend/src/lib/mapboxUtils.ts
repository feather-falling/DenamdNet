/**
 * Mapbox Localization and English Place Label Utilities
 *
 * Ensures all country and region place names displayed on the map are rendered
 * strictly in English across all zoom levels, overriding any local scripts
 * (such as Hindi, Arabic, Chinese, Russian, etc.).
 */

export interface CountryPlaceLabel {
  name: string;
  lat: number;
  lng: number;
  minZoom: number;
  maxZoom: number;
  isMajor?: boolean;
}

// Global Country Place Labels in English across all zoom levels
export const ENGLISH_COUNTRY_LABELS: CountryPlaceLabel[] = [
  // BRICS & Primary Nations
  { name: 'India', lat: 21.0, lng: 78.96, minZoom: 2, maxZoom: 10, isMajor: true },
  { name: 'Brazil', lat: -14.23, lng: -51.92, minZoom: 2, maxZoom: 10, isMajor: true },
  { name: 'South Africa', lat: -29.55, lng: 24.5, minZoom: 2, maxZoom: 10, isMajor: true },
  { name: 'China', lat: 35.86, lng: 104.19, minZoom: 2, maxZoom: 9, isMajor: true },
  { name: 'Russia', lat: 61.52, lng: 105.31, minZoom: 2, maxZoom: 8, isMajor: true },

  // Asia & Middle East (Guarantees English only, prevents Hindi/Arabic/Chinese)
  { name: 'Saudi Arabia', lat: 23.88, lng: 45.07, minZoom: 2, maxZoom: 9 },
  { name: 'Egypt', lat: 26.82, lng: 30.8, minZoom: 2, maxZoom: 9 },
  { name: 'United Arab Emirates', lat: 23.42, lng: 53.84, minZoom: 3, maxZoom: 10 },
  { name: 'Iran', lat: 32.42, lng: 53.68, minZoom: 3, maxZoom: 9 },
  { name: 'Turkey', lat: 38.96, lng: 35.24, minZoom: 3, maxZoom: 9 },
  { name: 'Pakistan', lat: 30.37, lng: 69.34, minZoom: 3, maxZoom: 10 },
  { name: 'Bangladesh', lat: 23.68, lng: 90.35, minZoom: 4, maxZoom: 10 },
  { name: 'Indonesia', lat: -0.78, lng: 113.92, minZoom: 3, maxZoom: 9 },
  { name: 'Japan', lat: 36.2, lng: 138.25, minZoom: 3, maxZoom: 9 },
  { name: 'South Korea', lat: 35.9, lng: 127.76, minZoom: 4, maxZoom: 10 },
  { name: 'Thailand', lat: 15.87, lng: 100.99, minZoom: 3, maxZoom: 10 },
  { name: 'Vietnam', lat: 14.05, lng: 108.27, minZoom: 3, maxZoom: 10 },
  { name: 'Philippines', lat: 12.87, lng: 121.77, minZoom: 3, maxZoom: 10 },
  { name: 'Malaysia', lat: 4.21, lng: 101.97, minZoom: 4, maxZoom: 10 },

  // Africa
  { name: 'Nigeria', lat: 9.08, lng: 8.67, minZoom: 3, maxZoom: 9 },
  { name: 'Kenya', lat: -0.02, lng: 37.9, minZoom: 3, maxZoom: 10 },
  { name: 'Ethiopia', lat: 9.14, lng: 40.48, minZoom: 3, maxZoom: 9 },
  { name: 'Ghana', lat: 7.94, lng: -1.02, minZoom: 4, maxZoom: 10 },
  { name: 'Tanzania', lat: -6.36, lng: 34.88, minZoom: 3, maxZoom: 10 },
  { name: 'Morocco', lat: 31.79, lng: -7.09, minZoom: 3, maxZoom: 9 },
  { name: 'Algeria', lat: 28.03, lng: 1.65, minZoom: 2, maxZoom: 8 },

  // Americas
  { name: 'United States', lat: 37.09, lng: -95.71, minZoom: 2, maxZoom: 8, isMajor: true },
  { name: 'Canada', lat: 56.13, lng: -106.34, minZoom: 2, maxZoom: 7, isMajor: true },
  { name: 'Mexico', lat: 23.63, lng: -102.55, minZoom: 3, maxZoom: 9 },
  { name: 'Argentina', lat: -38.41, lng: -63.61, minZoom: 3, maxZoom: 9 },
  { name: 'Colombia', lat: 4.57, lng: -74.29, minZoom: 3, maxZoom: 9 },
  { name: 'Chile', lat: -35.67, lng: -71.54, minZoom: 3, maxZoom: 9 },
  { name: 'Peru', lat: -9.19, lng: -75.01, minZoom: 3, maxZoom: 9 },

  // Europe
  { name: 'United Kingdom', lat: 55.37, lng: -3.43, minZoom: 3, maxZoom: 9 },
  { name: 'France', lat: 46.22, lng: 2.21, minZoom: 3, maxZoom: 9 },
  { name: 'Germany', lat: 51.16, lng: 10.45, minZoom: 3, maxZoom: 9 },
  { name: 'Italy', lat: 41.87, lng: 12.56, minZoom: 3, maxZoom: 9 },
  { name: 'Spain', lat: 40.46, lng: -3.74, minZoom: 3, maxZoom: 9 },

  // Oceania
  { name: 'Australia', lat: -25.27, lng: 133.77, minZoom: 2, maxZoom: 8, isMajor: true },
  { name: 'New Zealand', lat: -40.9, lng: 174.88, minZoom: 3, maxZoom: 9 }
];

/**
 * Specifically configures country and region place label layers in Mapbox to English only.
 * Overrides any default localized/browser languages (e.g. Hindi, Arabic, Chinese)
 * across all zoom levels where country labels appear.
 *
 * @param mapInstance Mapbox GL Map instance
 */
export function applyEnglishCountryLabels(mapInstance: any): void {
  if (!mapInstance) return;

  if (typeof mapInstance.getStyle === 'function') {
    const style = mapInstance.getStyle();
    if (style && style.layers) {
      style.layers.forEach((layer: any) => {
        // Target specifically country and region place label layers
        const isCountryOrRegionLabel =
          layer.id === 'country-label' ||
          layer.id.startsWith('country-label') ||
          layer.id.includes('place-country') ||
          layer.id === 'state-label' ||
          layer.id.startsWith('state-label') ||
          (layer.type === 'symbol' &&
            layer['source-layer'] === 'place_label' &&
            (layer.id.includes('country') || layer.id.includes('region')));

        if (isCountryOrRegionLabel && typeof mapInstance.setLayoutProperty === 'function') {
          try {
            // Apply language setting specifically to country/region place labels:
            // Force English text-field ('name_en' / 'name:en') and prevent Hindi, Arabic, Chinese
            mapInstance.setLayoutProperty(layer.id, 'text-field', [
              'coalesce',
              ['get', 'name_en'],
              ['get', 'name:en'],
              ['get', 'name']
            ]);
          } catch (e) {
            console.warn(`Could not set English text-field on layer ${layer.id}:`, e);
          }
        }
      });
    }

    // Explicit direct layout property targeting primary country-label layer
    if (typeof mapInstance.getLayer === 'function' && mapInstance.getLayer('country-label')) {
      try {
        mapInstance.setLayoutProperty('country-label', 'text-field', ['get', 'name_en']);
      } catch (e) {
        console.warn('Could not set country-label text-field:', e);
      }
    }
  }
}
