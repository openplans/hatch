/*globals Handlebars $ _ moment */

var VisionLouisville = VisionLouisville || {};

(function(NS) {
  Handlebars.registerHelper('authenticated', function(options) {
    return !!NS.currentUserData ? options.fn(this) : options.inverse(this);
  });

  Handlebars.registerHelper('STATIC_URL', function() {
    return NS.staticURL;
  });

  Handlebars.registerHelper('category_prompt', function(category) {
    return NS.Config.categories[category].prompt;
  });

  Handlebars.registerHelper('window_location', function() {
    return window.location.toString();
  });

  Handlebars.registerHelper('fromnow', function(datetime) {
    if (datetime) {
      return moment(datetime).fromNow();
    }
    return '';
  });

  Handlebars.registerHelper('formatdatetime', function(datetime, format) {
    if (datetime) {
      return moment(datetime).format(format);
    }
    return '';
  });

  Handlebars.registerHelper('select', function(value, options) {
    var $el = $('<div/>').html(options.fn(this)),
      selectValue = function(v) {
        $el.find('[value="'+v+'"]').attr({
          checked: 'checked',
          selected: 'selected'
        });
      };

    if (_.isArray(value)) {
      _.each(value, selectValue);
    } else {
      selectValue(value);
    }

    return $el.html();
  });

}(VisionLouisville));