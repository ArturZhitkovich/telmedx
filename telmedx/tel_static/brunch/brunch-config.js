// See http://brunch.io for documentation.
exports.modules = {
    autoRequire: {
        'app.js': ['initialize']
    }
};

exports.files = {
    javascripts: {
        joinTo: {
            'vendor.js': /^(?!app)/, // Files that are not in `app` dir.
            'app.js': /^app/
        }
    },
    stylesheets: {
        joinTo: {
            'app.css': 'app/styles/app.scss'
        }
    }
};

exports.plugins = {
    babel: {presets: ['latest']},
    sass: {
        options: {
            includePaths: ['node_modules/bootstrap-sass/assets/stylesheets']
        }
    },
    cssnano: {
    },
    uglify: {
    },
    afterBrunch: [
        // Requires uglify installed globally via npm
        'uglifyjs public/app.js -o public/app.min.js',
        'uglifyjs public/vendor.js -o public/vendor.min.js'
    ],
    copyfilemon: {
        'fonts': [
            'node_modules/bootstrap-sass/assets/fonts'
        ]
    }
};
