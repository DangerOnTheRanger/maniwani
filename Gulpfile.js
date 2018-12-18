const { series, parallel, src, dest } = require('gulp')
var sass = require('gulp-sass')
sass.compiler = require('node-sass')
var del = require('del')

function clean() {
	return del('static/**')
}

function maniwani_css() {
	return src('./scss/maniwani.scss').pipe(
		sass({outputStyle: 'compressed',
			  includePaths: './node_modules/bootstrap/scss'}).on('error', sass.logError)).pipe(
			dest('./static/css/'))
}

function popper() {
	return src('./node_modules/popper.js/dist/umd/popper.min.js').pipe(
		dest('./static/popperjs/umd'))
}

function jquery() {
	return src('./node_modules/jquery/dist/jquery.min.js').pipe(
		dest('./static/jquery/'))
}

function imagesloaded() {
	return src('./node_modules/imagesloaded/imagesloaded.pkgd.min.js').pipe(
		dest('./static/imagesloaded/'))
}

function masonry() {
	return src('./node_modules/masonry-layout/dist/masonry.pkgd.min.js').pipe(
		dest('./static/masonry/'))
}

function bootstrap_js() {
	return src('./node_modules/bootstrap/dist/js/bootstrap.min.js').pipe(
		dest('./static/bootstrap/'))
}

function fontawesome_css() {
	return src('./node_modules/@fortawesome/fontawesome-free/css/all.min.css').pipe(
		dest('./static/fontawesome/'))
}

function fontawesome_webfonts() {
	return src('./node_modules/@fortawesome/fontawesome-free/webfonts/fa-solid-900.+(ttf|woff|woff2)').pipe(
		dest('./static/webfonts/'))
}


exports.clean = clean
exports.css = parallel(maniwani_css, fontawesome_css)
exports.fonts = fontawesome_webfonts
exports.js = parallel(popper, jquery, bootstrap_js, imagesloaded, masonry)
exports.build = series(clean, parallel(exports.css, exports.js, exports.fonts))
exports.default = exports.build
