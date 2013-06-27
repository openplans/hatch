var VisionLouisville = VisionLouisville || {};

(function(NS) {
  // Handlebars support for Marionette
  Backbone.Marionette.TemplateCache.prototype.compileTemplate = function(rawTemplate) {
    return Handlebars.compile(rawTemplate);
  };

  // Views ====================================================================
  NS.HomeView = Backbone.Marionette.Layout.extend({
    className: 'container',
    template: '#home-tpl',
    regions: {
      economy: '.economy .vision',
      health: '.health .vision',
      energy: '.energy .vision',
      living: '.living .vision',
      connectivity: '.connectivity .vision',
      identity: '.identity .vision',
      creativity: '.creativity .vision'
    },

    initialize: function() {
      this.listenTo(this.collection, 'reset', this.renderRegions);
    },

    renderRegions: function() {
      var self = this;
      _.each(this.regions, function(selector, id) {
        var len = self.collection.size(),
            i = 0,
            model;

        for (i=0; i<len; i++) {
          model = self.collection.at(i);
          if (model.get('category').toLowerCase() === id) {
            self[id].show(new NS.HomeVisionView({model: model}));
            break;
          }
        }
      });
    },

    onClose: function() {
      this.stopListeningobject(this.collection);
    }
  });

  NS.HomeVisionView = Backbone.Marionette.ItemView.extend({
    template: '#home-vision-tpl',
    tagName: 'p'
  });

}(VisionLouisville));