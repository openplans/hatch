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

    events: {
      'click .swiper-link': 'handleSwiperLinkClick'
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

    onRender: function() {
      this.renderRegions();
      this.delegateEvents();
    },

    onClose: function() {
      this.stopListening(this.collection);
    },

    handleSwiperLinkClick: function(evt) {
      var $link = $(evt.target),
          $parent = $link.parents('li'),
          index = $parent.index();

      evt.preventDefault();

      this.swiper.swipeTo(index, 500, true);
    }
  });

  NS.HomeVisionView = Backbone.Marionette.ItemView.extend({
    template: '#home-vision-tpl',
    tagName: 'p'
  });

  NS.NoItemsView = Backbone.Marionette.ItemView.extend({
    template: '#no-items-tpl'
  });


  NS.VisionListItemView = Backbone.Marionette.ItemView.extend({
    template: '#list-item-tpl',
    tagName: 'li'
  });

  NS.VisionListView = Backbone.Marionette.CompositeView.extend({
    template: '#list-tpl',
    itemView: NS.VisionListItemView,
    itemViewContainer: 'ul',
    emptyView: NS.NoItemsView
  });

  NS.VisionItemView = Backbone.Marionette.ItemView.extend({
    template: '#item-tpl'
  });


}(VisionLouisville));