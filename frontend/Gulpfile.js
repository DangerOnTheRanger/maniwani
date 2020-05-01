const { series, parallel, src, dest } = require('gulp');
var gulp = require('gulp');
var babel = require('gulp-babel');

function compile_jsx() {
    return gulp.src('src/**/*.jsx').
        pipe(babel({
            plugins: ['@babel/transform-react-jsx', '@babel/plugin-transform-modules-commonjs']
        })).
        pipe(gulp.dest('build/'));
}
function copy_js() {
	return gulp.src('src/**/*.js').pipe(gulp.dest('build/'));
}

exports.jsx = compile_jsx;
exports.js = copy_js;
exports.build = parallel(exports.jsx, exports.js);
exports.default = exports.build;

