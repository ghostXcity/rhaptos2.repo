// Generated by CoffeeScript 1.3.3
(function() {

  require.config({
    enforceDefine: true,
    paths: {
      i18n: 'i18n-custom',
      jquery: 'lib/jquery-1.8.3',
      underscore: 'lib/underscore-1.4.3',
      backbone: 'lib/backbone-0.9.2',
      jasmine: 'lib/jasmine/jasmine',
      'jasmine-html': 'lib/jasmine/jasmine-html',
      'jquery-mockjax': 'lib/jquery.mockjax',
      spec: 'tests/spec',
      'aloha': '../cdn/aloha/src/lib/aloha',
      bootstrap: 'lib/bootstrap/js/bootstrap',
      select2: 'lib/select2/select2',
      spin: 'lib/spin',
      hbs: 'lib/require-handlebars-plugin/hbs',
      handlebars: 'lib/require-handlebars-plugin/Handlebars',
      i18nprecompile: 'lib/require-handlebars-plugin/hbs/i18nprecompile',
      json2: 'lib/require-handlebars-plugin/hbs/json2'
    },
    shim: {
      jquery: {
        exports: 'jQuery'
      },
      bootstrap: {
        deps: ['jquery'],
        exports: 'jQuery'
      },
      underscore: {
        exports: '_'
      },
      backbone: {
        deps: ['underscore', 'jquery'],
        exports: 'Backbone',
        init: function() {
          var ret;
          ret = this.Backbone;
          delete this.Backbone;
          return ret;
        }
      },
      aloha: {
        deps: ['css!../cdn/aloha/src/css/aloha']
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
      'spec/routes': {
        deps: ['jquery'],
        init: function() {
          return true;
        }
      },
      'aloha': {
        deps: ['jquery'],
        exports: 'Aloha'
      },
      jasmine: {
        exports: 'jasmine'
      },
      'jasmine-html': {
        deps: ['jasmine'],
        exports: 'jasmine'
      },
      'jquery-mockjax': {
        deps: ['jquery'],
        exports: 'jQuery'
      }
    },
    map: {
      '*': {
        css: 'lib/require-css/css',
        less: 'lib/require-less/less'
      }
    },
    hbs: {
      disableI18n: true
    },
    config: {
      i18n: {
        warn: true
      }
    }
  });

}).call(this);
