module.exports = function(config) {
  config.set({
    browsers: ['PhantomJS'],
    frameworks: ['jasmine'],
    files: [
      'edx_notifications/static/js/HelloWorld.js',
      'edx_notifications/static/js/specs/hello-world-spec.js'
    ],

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


        // start these browsers
        // available browser launchers: https://npmjs.org/browse/keyword/karma-launcher
        // you can also add Chrome or other browsers too

      captureTimeout: 60000,

        // Continuous Integration mode
        // if true, Karma captures browsers, runs the tests and exits
        singleRun: false,


     // plugins required for running the karma tests
        plugins:[
            'karma-jasmine',
            'karma-requirejs',
            'karma-phantomjs-launcher',
            'karma-coverage'
        ]
  });
};

