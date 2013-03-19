
// <!--
// Copyright (c) Rice University 2012-3
// This software is subject to
// the provisions of the GNU Affero General
// Public License Version 3 (AGPLv3).
// See LICENCE.txt for details.
// -->


(function() {

  define(['jquery', 'jquery-mockjax'], function($) {
    var MOCK_CONTENT, RESPONSE_METADATA, SHORT;
    SHORT = 500;
    MOCK_CONTENT = {
      url: '/content/123.metadata',
      title: 'Test Module Title',
      language: 'sv-se',
      subjects: ['Arts', 'Business'],
      keywords: ['Quantum Mechanics', 'physics'],
      authors: ['John Smith']
    };
    RESPONSE_METADATA = $.extend({}, MOCK_CONTENT);
    $.mockjax({
      type: 'GET',
      url: '/content/*',
      responseTime: SHORT,
      contentType: 'application/json',
      responseText: RESPONSE_METADATA
    });
    $.mockjax({
      type: 'POST',
      url: '/content/*',
      responseTime: SHORT,
      contentType: 'application/json',
      response: function(settings) {
        var key;
        for (key in RESPONSE_METADATA) {
          delete RESPONSE_METADATA[key];
        }
        return $.extend(RESPONSE_METADATA, JSON.parse(settings.data));
      }
    });
    $.mockjax({
      type: 'GET',
      url: '/keywords/',
      responseTime: SHORT,
      contentType: 'application/json',
      responseText: ['alpha', 'beta', 'water', 'physics', 'organic chemistry']
    });
    $.mockjax({
      type: 'GET',
      url: '/users/',
      responseTime: SHORT,
      contentType: 'application/json',
      responseText: ['Bruce Wayne', 'Peter Parker', 'Clark Kent']
    });
    return $.extend(true, {}, MOCK_CONTENT);
  });

}).call(this);

