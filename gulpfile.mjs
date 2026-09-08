////////////////////////////////
// Setup
////////////////////////////////

// Gulp and package
import { src, dest, parallel, series, task, watch } from 'gulp';
import pjson from './package.json' with { type: 'json' };

// Plugins
import autoprefixer from 'autoprefixer';
import browserSyncLib from 'browser-sync';
import concat from 'gulp-concat';
import cssnano from 'cssnano';
import plumber from 'gulp-plumber';
import postcss from 'gulp-postcss';
import rename from 'gulp-rename';
import gulpSass from 'gulp-sass';
import * as dartSass from 'sass';
import gulUglifyES from 'gulp-uglify-es';
import { Transform } from 'node:stream';

const browserSync = browserSyncLib.create();
const reload = browserSync.reload;
const sass = gulpSass(dartSass);
const uglify = gulUglifyES.default;

// Relative paths function
function pathsConfig() {
  const appName = `./${pjson.name}`;
  const vendorsRoot = 'node_modules';

  return {
    vendorsJs: [
      // bootstrap.bundle already contains Popper, so Popper is not listed
      // separately — including both would register two instances.
      `${vendorsRoot}/bootstrap/dist/js/bootstrap.bundle.js`,
    ],
    vendorsRoot,
    app: appName,
    templates: `${appName}/templates`,
    css: `${appName}/static/css`,
    sass: `${appName}/static/sass`,
    fonts: `${appName}/static/fonts`,
    images: `${appName}/static/images`,
    js: `${appName}/static/js`,
  };
}

const paths = pathsConfig();

////////////////////////////////
// Tasks
////////////////////////////////

// Styles autoprefixing and minification
function styles() {
  const processCss = [
    autoprefixer(), // adds vendor prefixes
  ];

  const minifyCss = [
    // svgo is disabled: it cannot parse Bootstrap's URL-encoded inline SVG
    // icons and logs a parser error for each one. Everything else still runs.
    cssnano({ preset: ['default', { svgo: false }] }), // minify result
  ];

  return src(`${paths.sass}/project.scss`)
    .pipe(
      sass({
        includePaths: [paths.sass, paths.vendorsRoot],
      }).on('error', sass.logError),
    )
    .pipe(plumber()) // Checks for errors
    .pipe(postcss(processCss))
    .pipe(dest(paths.css))
    .pipe(rename({ suffix: '.min' }))
    .pipe(postcss(minifyCss)) // Minifies the result
    .pipe(dest(paths.css));
}

// Javascript minification
function scripts() {
  return src(`${paths.js}/project.js`)
    .pipe(plumber()) // Checks for errors
    .pipe(uglify()) // Minifies the js
    .pipe(rename({ suffix: '.min' }))
    .pipe(dest(paths.js));
}

// Vendor Javascript minification.
//
// No source maps on purpose: `*.min.js.map` is gitignored, so a
// `//# sourceMappingURL=` comment would point at a file that never reaches
// production, and WhiteNoise's manifest storage refuses to collectstatic
// when a JS file references a missing map. Bootstrap's own comment is
// stripped for the same reason.
function stripSourceMapComments() {
  return new Transform({
    objectMode: true,
    transform(file, _encoding, callback) {
      if (file.isBuffer()) {
        file.contents = Buffer.from(
          file.contents.toString().replace(/^\/\/# sourceMappingURL=.*$/gm, ''),
        );
      }
      callback(null, file);
    },
  });
}

function vendorScripts() {
  return src(paths.vendorsJs)
    .pipe(concat('vendors.js'))
    .pipe(stripSourceMapComments())
    .pipe(dest(paths.js))
    .pipe(plumber()) // Checks for errors
    .pipe(uglify()) // Minifies the js
    .pipe(rename({ suffix: '.min' }))
    .pipe(dest(paths.js));
}

// Browser sync server for live reload
function initBrowserSync() {
  browserSync.init(
    [`${paths.css}/*.css`, `${paths.js}/*.js`, `${paths.templates}/*.html`],
    {
      // https://www.browsersync.io/docs/options/#option-open
      // Disable as it doesn't work from inside a container
      open: false,
      // https://www.browsersync.io/docs/options/#option-proxy
      proxy: {
        target: 'django:8000',
        proxyReq: [
          function (proxyReq, req) {
            // Assign proxy 'host' header same as current request at Browsersync server
            proxyReq.setHeader('Host', req.headers.host);
          },
        ],
      },
    },
  );
}

// Watch
function watchPaths() {
  watch(`${paths.sass}/*.scss`, styles);
  watch(`${paths.templates}/**/*.html`).on('change', reload);
  watch([`${paths.js}/*.js`, `!${paths.js}/*.min.js`], scripts).on(
    'change',
    reload,
  );
}

// Generate all assets
const build = parallel(styles, scripts, vendorScripts);

// Set up dev environment
const dev = parallel(initBrowserSync, watchPaths);

task('default', series(build, dev));
task('build', build);
task('dev', dev);
