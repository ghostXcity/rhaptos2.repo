
// <!--
// Copyright (c) Rice University 2012-3
// This software is subject to
// the provisions of the GNU Affero General
// Public License Version 3 (AGPLv3).
// See LICENCE.txt for details.
// -->


(function() {

  define(['backbone', 'exports', 'i18n!app/nls/strings'], function(Backbone, exports, __) {
    var CONTENT_PREFIX, WORKSPACE_PREFIX;
    CONTENT_PREFIX = '/content/';
    WORKSPACE_PREFIX = '/workspace/';
    exports.Content = Backbone.Model.extend({
      defaults: {
        title: __('Untitled'),
        subjects: [],
        keywords: [],
        authors: [],
        copyrightHolders: [],
        language: ((typeof navigator !== "undefined" && navigator !== null ? navigator.userLanguage : void 0) || (typeof navigator !== "undefined" && navigator !== null ? navigator.language : void 0) || 'en').toLowerCase()
      },
      url: function() {
        if (this.get('id')) {
          return "" + CONTENT_PREFIX + (this.get('id'));
        } else {
          return CONTENT_PREFIX;
        }
      },
      validate: function(attrs) {
        var isEmpty;
        isEmpty = function(str) {
          return str && !str.trim().length;
        };
        if (isEmpty(attrs.body)) {
          return 'ERROR_EMPTY_BODY';
        }
        if (isEmpty(attrs.title)) {
          return 'ERROR_EMPTY_TITLE';
        }
        if (attrs.title === __('Untitled')) {
          return 'ERROR_UNTITLED_TITLE';
        }
      }
    });
    exports.SearchResultItem = Backbone.Model.extend({
      defaults: {
        type: 'BUG_UNSPECIFIED_TYPE',
        title: 'BUG_UNSPECIFIED_TITLE'
      }
    });
    exports.Workspace = Backbone.Collection.extend({
      model: exports.SearchResultItem,
      url: WORKSPACE_PREFIX
    });
    return exports;
  });

}).call(this);

