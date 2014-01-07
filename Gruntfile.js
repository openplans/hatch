module.exports = function(grunt) {

  // Project configuration.
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    uglify: {
      options: {
        banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n'
      },
      dist: {
        files: [
          {
            dest: 'src/hatch/static/js/components.min.js',
            src: [
              'src/hatch/static/bower_components/jquery/jquery.js',
              'src/hatch/static/bower_components/handlebars.js/dist/handlebars.js',
              'src/hatch/static/bower_components/underscore/underscore-min.js',
              'src/hatch/static/bower_components/backbone/backbone.js',
              'src/hatch/static/bower_components/backbone-relational/backbone-relational.js',
              'src/hatch/static/bower_components/backbone.marionette/lib/backbone.marionette.js',
              'src/hatch/static/bower_components/moment/moment.js',
              'src/hatch/static/bower_components/Countable/Countable.js',
              'src/hatch/static/bower_components/exif-js/binaryajax.js',
              'src/hatch/static/bower_components/exif-js/exif.js',
              'src/hatch/static/bower_components/blueimp-load-image/js/load-image.js',
              'src/hatch/static/bower_components/blueimp-canvas-to-blob/js/canvas-to-blob.js',
              'src/hatch/static/bower_components/spin.js/spin.js',
              'src/hatch/static/bower_components/swiper/dist/idangerous.swiper-2.4.1.js'
            ]
          },
          {
            dest: 'src/hatch/static/js/app.min.js',
            src: [
              'src/hatch/static/js/config.js',
              'src/hatch/static/js/django-csrf.js',
              'src/hatch/static/js/utils.js',
              'src/hatch/static/js/handlebars-helpers.js',
              'src/hatch/static/js/models.js',
              'src/hatch/static/js/views.js',
              'src/hatch/static/js/app.js'
            ]
          },
          {
            dest: 'src/hatch/static/js/modernizr.min.js',
            src: [
              'src/hatch/static/bower_components/modernizr/modernizr.js'
            ]
          }
        ]
      }
    },
    cssmin: {
      options: {
        banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n'
      },
      dist: {
        files: [
          {
            dest: 'src/hatch/static/css/components.min.css',
            src: [
              'src/hatch/static/bower_components/normalize-css/normalize.css',
              'src/hatch/static/bower_components/hint.css/hint.css',
              'src/hatch/static/bower_components/swiper/dist/idangerous.swiper.css'
            ]
          },
          {
            dest: 'src/hatch/static/css/styles.min.css',
            src: [
              'src/hatch/static/css/styles.css'
            ]
          }
        ]
      }
    }
  });

  // Load the plugins
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-cssmin');

  // Default task(s).
  grunt.registerTask('default', ['uglify', 'cssmin']);

};