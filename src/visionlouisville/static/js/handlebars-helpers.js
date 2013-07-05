/*globals Handlebars */

var VisionLouisville = VisionLouisville || {};

(function(NS) {

  Handlebars.registerHelper('category_prompt', function(category) {
    return NS.Config.categories[category].prompt;
  });

  Handlebars.registerHelper('window_location', function() {
    return window.location.toString();
  });

  Handlebars.registerHelper('select', function(value, options) {
  	var $el = $('<div/>').html(options.fn(this)),
  		selectValue = function(v) {
  		  $el.find('[value="'+v+'"]').attr({
  		  	checked: 'checked', 
  		  	selected: 'selected'
  		  });
  		}

  	if (_.isArray(value))
  	  _.each(value, selectValue);
  	else
  	  selectValue(value);

  	return $el.html();
  })

}(VisionLouisville));