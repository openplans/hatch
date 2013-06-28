/*globals Handlebars */

var VisionLouisville = VisionLouisville || {};

(function(NS) {

  Handlebars.registerHelper('category_prompt', function(category) {
    return NS.Config.categories[category].prompt;
  });

}(VisionLouisville));