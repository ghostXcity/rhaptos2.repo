
// <!--
// Copyright (c) Rice University 2012-3
// This software is subject to
// the provisions of the GNU Affero General
// Public License Version 3 (AGPLv3).
// See LICENCE.txt for details.
// -->


(function() {

  require.config({
    baseUrl: 'static/',
    urlArgs: '',
    paths: {
      i18n: 'i18n-custom',
      text: 'lib/require-text/text',
      json: 'lib/requirejs-plugins/json',
      hbs: 'lib/require-handlebars-plugin/hbs',
      jquery: 'lib/jquery-1.8.3',
      underscore: 'lib/underscore-1.4.3',
      backbone: 'lib/backbone-0.9.9',
      marionette: 'lib/backbone.marionette',
      aloha: '../cdn/aloha/src/lib/aloha',
      bootstrap: 'lib/bootstrap/js/bootstrap',
      select2: 'lib/select2/select2',
      spin: 'lib/spin',
      handlebars: 'lib/require-handlebars-plugin/Handlebars',
      i18nprecompile: 'lib/require-handlebars-plugin/hbs/i18nprecompile',
      json2: 'lib/require-handlebars-plugin/hbs/json2',
      'font-awesome': 'lib/font-awesome/css/font-awesome'
    },
    shim: {
      jquery: {
        exports: 'jQuery',
        init: function() {}
      },
      underscore: {
        exports: '_'
      },
      backbone: {
        deps: ['underscore', 'jquery'],
        exports: 'Backbone'
      },
      marionette: {
        deps: ['underscore', 'backbone'],
        exports: 'Backbone',
        init: function() {
          var ret;
          ret = this.Backbone.Marionette;
          delete this.Backbone.Marionette;
          delete this.Backbone;
          return ret;
        }
      },
      bootstrap: {
        deps: ['jquery', 'css!lib/bootstrap/css/bootstrap'],
        exports: 'jQuery'
      },
      select2: {
        deps: ['jquery', 'css!./select2'],
        exports: 'Select2',
        init: function() {
          var ret;
          ret = this.Select2;
          delete this.Select2;
          return ret;
        }
      },
      aloha: {
        deps: ['bootstrap', 'aloha-config', 'css!../cdn/aloha/src/css/aloha'],
        exports: 'Aloha'
      }
    },
    map: {
      '*': {
        text: 'lib/require-text',
        css: 'lib/require-css/css',
        less: 'lib/require-less/less',
        json: 'lib/requirejs-plugins/src/json'
      }
    },
    hbs: {
      disableI18n: true
    }
  });

}).call(this);

