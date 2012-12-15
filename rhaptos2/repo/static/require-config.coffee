# Configure paths to all the JS libs
require.config

  # If set to true, an error will be thrown if a script loads that does not call define() or have a shim exports string value that can be checked. See Catching load failures in IE for more information.
  enforceDefine: true

  #urlArgs: "cb=#{Math.random()}" # Cache Buster
  paths:
    'aloha': '../cdn/aloha/src/lib/aloha' # FIXME: Remove the '/cdn/' when aloha is moved into static/
    jquery: 'lib/jquery-1.8.3'
    'jquery-mockjax': 'lib/jquery.mockjax'
    bootstrap: 'lib/bootstrap/js/bootstrap'
    underscore: 'lib/underscore-1.4.3'
    backbone: 'lib/backbone-0.9.2'
    jasmine: 'lib/jasmine/jasmine'
    'jasmine-html': 'lib/jasmine/jasmine-html'
    mustache: 'lib/mustache'
    select2: 'lib/select2/select2'
    spin: 'lib/spin'
    spec: 'spec'
    'model/tools': 'model/tools'
    'atc/lang': 'js/languagelib'
    'atc/templates': 'authortools_client_templates'
    'mockjax-routes': 'tests/mockjax-routes'

  shim:
    jquery:
      exports: 'jQuery'
      # init: -> this.jQuery.noConflict(true)
    bootstrap:
      deps: ['jquery']
      exports: 'jQuery'

    underscore:
      exports: '_'

    backbone:
      deps: ['underscore', 'jquery']
      exports: 'Backbone'
      init: -> ret = @Backbone; delete @Backbone; ret

    jasmine:
      exports: 'jasmine'

    'jasmine-html':
      deps: ['jasmine']
      exports: 'jasmine'

    'jasmine-ajax':
      deps: ['jasmine']
      exports: 'jasmine'

    'jquery-mockjax':
      deps: ['jquery']
      exports: 'jQuery'

    mustache:
      exports: 'Mustache'
      init: -> ret = @Mustache; delete @Mustache; ret

    select2:
      deps: ['jquery']
      exports: 'Select2'
      init: -> ret = @Select2; delete @Select2; ret

    'atc/client':
      deps: ['jquery']
      exports: 'jQuery'

    'atc/lang':
      exports: 'Language'

    'mockjax-routes':
      deps: ['jquery']
      init: -> true

    'aloha':
      deps: ['jquery']
      exports: 'Aloha'

# requirejs special-cases jQuery and allows it to be a global (doesn't call the init code below to clean up the global vars)
# To stop it from doing that, we need to delete this property
#
# unlike the other jQuery plugins bootstrap depends on a global '$' instead of 'jQuery'
#delete define.amd.jQuery