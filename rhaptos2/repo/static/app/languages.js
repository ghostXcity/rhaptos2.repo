
// <!--
// Copyright (c) Rice University 2012-3
// This software is subject to
// the provisions of the GNU Affero General
// Public License Version 3 (AGPLv3).
// See LICENCE.txt for details.
// -->


(function() {

  define(['json!./languages/countries.json', 'json!./languages/languages.json', 'json!./languages/variants.json'], function(COUNTRIES, LANGUAGES, VARIANTS) {
    return {
      getCountries: function() {
        return COUNTRIES;
      },
      getLanguages: function() {
        return LANGUAGES;
      },
      getCombined: function() {
        return VARIANTS;
      },
      getNativeLanguageNames: function() {
        var info, lang_code, native_languages;
        native_languages = {};
        for (lang_code in LANGUAGES) {
          info = LANGUAGES[lang_code];
          native_languages[lang_code] = info['native'];
        }
        return native_languages;
      },
      getCombinedLanguageNames: function() {
        var combined_languages, info, lang_code;
        combined_languages = {};
        for (lang_code in COMBINED) {
          info = COMBINED[lang_code];
          combined_languages[lang_code] = info['english'];
        }
        return combined_languages;
      }
    };
  });

}).call(this);

