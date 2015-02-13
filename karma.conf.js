module.exports = function(config) {
  config.set({

    // plugins required for running the karma tests
    plugins:[
        'karma-jasmine',
        'karma-requirejs',
        'karma-firefox-launcher',
        'karma-phantomjs-launcher',
        'karma-coverage'
    ],

    // start the browser
    browsers: ['PhantomJS'],

    //frameworks to use
    frameworks: ['jasmine'],

    //patterns to load all files in child folders
    files: [
        {pattern: 'edx_notifications/server/web/static/edx_notifications/js/vendor/dev/mock-ajax.js'},
        {pattern: 'edx_notifications/server/web/static/edx_notifications/js/vendor/dev/jquery-1.11.2.min.js'},
        {pattern: 'edx_notifications/server/web/static/edx_notifications/js/vendor/dev/underscore.js'},
        {pattern: 'edx_notifications/server/web/static/edx_notifications/js/vendor/dev/backbone.js'},
        {pattern: 'edx_notifications/server/web/static/edx_notifications/js/models/user_notification_model.js'},
        {pattern: 'edx_notifications/server/web/static/edx_notifications/js/models/counter_icon_model.js'},
        {pattern: 'edx_notifications/server/web/static/edx_notifications/js/models/notification_collection_model.js'},
        {pattern: 'edx_notifications/server/web/static/edx_notifications/js/views/*.js'},
        {pattern: 'edx_notifications/server/web/static/edx_notifications/js/test/specs/counter_icon_view_spec.js'}
//        {pattern: 'edx_notifications/server/web/static/edx_notifications/js/vendor/dev/**/*.js'},
//        {pattern: 'edx_notifications/server/web/static/edx_notifications/js/models/**/*.js'},
//        {pattern: 'edx_notifications/server/web/static/edx_notifications/js/views/**/*.js'}
    ],


    // preprocess matching files before serving them to the browser
    // available preprocessors: https://npmjs.org/browse/keyword/karma-preprocessor
    preprocessors: {
        'edx_notifications/server/web/static/edx_notifications/js/vendor/dev/**/*.js': ['coverage'],
        'edx_notifications/server/web/static/edx_notifications/js/models/**/*.js': ['coverage'],
        'edx_notifications/server/web/static/edx_notifications/js/views/**/*.js': ['coverage']
    },

    // test results reporter to use
    // possible values: 'dots', 'progress'
    // available reporters: https://npmjs.org/browse/keyword/karma-reporter
    reporters: ['progress', 'coverage'],

    coverageReporter: {
        dir:'build', subdir: 'coverage-js',
        reporters:[
            {type: 'html', subdir: 'coverage-js/html'},
            {type: 'cobertura', file: 'coverage.xml'},
            {type: 'text-summary'}
        ]
    },

    // enable / disable colors in the output (reporters and logs)
    colors: true,


     // level of logging
     // possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN || config.LOG_INFO || config.LOG_DEBUG
     logLevel: config.LOG_INFO,


     // enable / disable watching file and executing tests whenever any file changes
     autoWatch: true,

     captureTimeout: 60000,

     // Continuous Integration mode
     // if true, Karma captures browsers, runs the tests and exits
     singleRun: false

  });
};

