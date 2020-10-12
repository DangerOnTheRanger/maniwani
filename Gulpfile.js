const { series, parallel, src, dest } = require('gulp')
var gulp = require('gulp')
var sass = require('gulp-sass')
sass.compiler = require('node-sass')
var del = require('del')
var browserSync = require("browser-sync").create();

function clean() {
	return del('static/**')
}

function maniwani_css() {
	return src('./scss/themes/*/theme-*.scss').pipe(
		sass({outputStyle: 'compressed',
			  includePaths: ['./scss/base', './node_modules/bootstrap/scss']}).on('error', sass.logError)).pipe(
			dest('./static/css/')).pipe(browserSync.stream())
}

function fontawesome_css() {
	return src('./node_modules/@fortawesome/fontawesome-free/css/all.min.css').pipe(
		dest('./static/fontawesome/'))
}

function fontawesome_webfonts() {
	return src('./node_modules/@fortawesome/fontawesome-free/webfonts/fa-solid-900.+(ttf|woff|woff2)').pipe(
		dest('./static/webfonts/'))
}

function firasans_webfonts_index() {
	return src(['./node_modules/fontsource-fira-sans/index.css', ]).pipe(
		dest('./static/webfonts/firasans/'))
}

function firasans_webfonts_woff() {
	return src('./node_modules/fontsource-fira-sans/files/*').pipe(
		dest('./static/webfonts/firasans/files'))
}

function watch() {
	browserSync.init
	({
		proxy: '127.0.0.1:5000',
		port: 5000
  });
	gulp.watch('./scss/**/*.scss', maniwani_css ).on('change', browserSync.reload);
	gulp.watch("./templates/*.html").on("change", browserSync.reload);
}

exports.watch = watch
exports.clean = clean
exports.css = parallel(maniwani_css, fontawesome_css)
exports.fonts = parallel(fontawesome_webfonts, firasans_webfonts_index, firasans_webfonts_woff)
exports.build = series(clean, parallel(exports.css, exports.fonts))
exports.default = exports.build
