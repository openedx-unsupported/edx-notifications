var gulp = require('gulp');
var Server = require('karma').Server;
var coverageOnOff = 'coverage';

/**
 * Run test once and exit
 */
gulp.task('test', function (done) {
  new Server({
    configFile: __dirname + '/karma.conf.js',
    singleRun: true
  }, function (exitCode) {
    exitCode ? process.exit(exitCode) : done();
  }).start();
});

/**
 * Watch for file changes and re-run tests on each change
 */
gulp.task('tdd', function (done) {
  new Server({
    configFile: __dirname + '/karma.conf.js',
  }, function (exitCode) {
    exitCode ? process.exit(exitCode) : done();
  }).start();
});

gulp.task('default', gulp.series(['tdd']));


/**
 * Run test in debug mode
 */
gulp.task('debug', function (done) {
  new Server({
    configFile: __dirname + '/karma.conf.js',
    singleRun: false
  }, function (exitCode) {
    exitCode ? process.exit(exitCode) : done();
  }).start();
});