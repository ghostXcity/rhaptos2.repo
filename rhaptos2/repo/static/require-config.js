// Generated by CoffeeScript 1.3.3
(function() {

  require.config({
    enforceDefine: true,
    paths: {
      'aloha': '../cdn/aloha/src/lib/aloha',
      jquery: 'lib/jquery-1.8.3',
      'jquery-mockjax': 'lib/jquery.mockjax',
      bootstrap: 'lib/bootstrap/js/bootstrap',
      underscore: 'lib/underscore-1.4.3',
      backbone: 'lib/backbone-0.9.2',
      jasmine: 'lib/jasmine/jasmine',
      'jasmine-html': 'lib/jasmine/jasmine-html',
      mustache: 'lib/mustache',
      select2: 'lib/select2/select2',
      spin: 'lib/spin',
      spec: 'spec',
      'model/tools': 'model/tools',
      'atc/lang': 'js/languagelib',
      'atc/templates': 'authortools_client_templates',
      'mockjax-routes': 'tests/mockjax-routes'
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
      jasmine: {
        exports: 'jasmine'
      },
      'jasmine-html': {
        deps: ['jasmine'],
        exports: 'jasmine'
      },
      'jasmine-ajax': {
        deps: ['jasmine'],
        exports: 'jasmine'
      },
      'jquery-mockjax': {
        deps: ['jquery'],
        exports: 'jQuery'
      },
      mustache: {
        exports: 'Mustache',
        init: function() {
          var ret;
          ret = this.Mustache;
          delete this.Mustache;
          return ret;
        }
      },
      select2: {
        deps: ['jquery'],
        exports: 'Select2',
        init: function() {
          var ret;
          ret = this.Select2;
          delete this.Select2;
          return ret;
        }
      },
      'atc/client': {
        deps: ['jquery'],
        exports: 'jQuery'
      },
      'atc/lang': {
        exports: 'Language'
      },
      'mockjax-routes': {
        deps: ['jquery'],
        init: function() {
          return true;
        }
      },
      'aloha': {
        deps: ['jquery'],
        exports: 'Aloha'
      }
    }
  });

}).call(this);