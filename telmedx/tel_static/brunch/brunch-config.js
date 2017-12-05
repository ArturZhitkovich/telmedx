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
      'app.css': 'app/styles/app.scss',
      'vendor.css': /^node_modules/
    }
  }
};

exports.npm = {
  enabled: true,

  // Required for jquery plugins like jquery-ui
  globals: {
    $: 'jquery',
    jQuery: 'jquery'
  },

  // Required for jquery-ui
  styles: {
    'jquery-ui-bundle': ['jquery-ui.css']
  }
};

exports.plugins = {
  babel: { presets: ['latest'] },
  sass: {
    options: {
      includePaths: [
        'node_modules/bootstrap-sass/assets/stylesheets'
      ]
    }
  },
  cssnano: {
    discardComments: {
      removeAll: true
    }
  },
  uglify: {},
  afterBrunch: [

    // Requires uglify installed globally via npm
    'uglifyjs public/app.js -o public/app.min.js',
    'uglifyjs public/vendor.js -o public/vendor.min.js',

    // Copy over images to public dir so Django can get it
    'cp -r app/assets/img public',

    // Required for jquery-ui
    'cp -r node_modules/jquery-ui-bundle/images public'
  ],
  copyfilemon: {
    fonts: [
      'node_modules/bootstrap-sass/assets/fonts'
    ]
  }
};
