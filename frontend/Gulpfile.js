const { series, parallel, src, dest } = require('gulp');
var gulp = require('gulp');
var babel = require('gulp-babel');
var filter = require('gulp-filter');
var log = require('gulplog');
var tap = require('gulp-tap');
var uglify = require('gulp-uglify');
var browserify = require('browserify');
var buffer = require('vinyl-buffer');

function compile_jsx() {
    return gulp.src('src/**/*.jsx').
        pipe(babel({
            plugins: ['@babel/transform-react-jsx', '@babel/plugin-transform-modules-commonjs'],
			presets: ['@babel/env']
        })).
        pipe(gulp.dest('build/'));
}
function compile_js() {
	return gulp.src('src/**/*.js').
		pipe(babel({
			presets: ['@babel/env']})). 
		pipe(gulp.dest('build/'));
}
function compile_client() {
	return gulp.src('build/client/*.js').
		pipe(tap(function (file) {
			log.info('bundling ' + file.path);
			file.contents = browserify(file.path, {debug: true}).bundle();
		})).
		pipe(buffer()).
		//pipe(uglify()).
		pipe(gulp.dest('build/client-bundle'));
}

exports.jsx = compile_jsx;
exports.js = compile_js;
exports.build = series(parallel(exports.jsx, exports.js), compile_client);
exports.default = exports.build;

