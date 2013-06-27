/*globals Backbone Handlebars $ _ Swiper */

var VisionLouisville = VisionLouisville || {};

(function(NS) {
  // Router ===================================================================
  NS.Router = Backbone.Marionette.AppRouter.extend({
    appRoutes: {
      '!\/list/:category': 'list',
      '!\/new': 'new',
      '!\/:id': 'item',
      '*anything': 'home'
    }
  });

  NS.controller = {
    list: function(category) {
      // TODO: this is not very efficient
      var collection = new NS.VisionCollection();

      collection.fetch({
        reset: true,
        data: {
          category: category
        }
      });

      NS.app.mainRegion.show(new NS.VisionListView({
        collection: collection
      }));
    },
    new: function() {},
    item: function(id) {
      id = parseInt(id, 10);
      var render = function(modelId) {
            var model = NS.app.visionCollection.get(id);
            NS.app.mainRegion.show(new NS.VisionItemView({
              model: model
            }));
          };

      // Nothing in the collection? It's not done fetching. Let's wait for it.
      if (NS.app.visionCollection.size() === 0) {
        // Render when the collection resets
        NS.app.visionCollection.once('reset', function() {
          render(id);
        });
      } else {
        render(id);
      }
    },
    home: function() {
      NS.app.mainRegion.show(NS.app.homeView);
      // Init this here b/c we know we're inserted into the dom at this point.
      // Important for height calculations.
      NS.app.homeView.swiper = new Swiper(NS.app.homeView.$('.swiper-container').get(0), {
        loop: true,
        calculateHeight: true
      });
    }
  };

  // App ======================================================================
  NS.app = new Backbone.Marionette.Application();

  NS.app.addRegions({
    mainRegion: '.main'
  });

  NS.app.addInitializer(function(options){
    this.homeView = new NS.HomeView({
      collection: this.visionCollection
    });
  });

  NS.app.addInitializer(function(options){
    // Construct a new app router
    this.router = new NS.Router({
      controller: NS.controller
    });
    Backbone.history.start();
  });

  // Init =====================================================================
  $(function() {
    NS.app.visionCollection = new NS.VisionCollection();
    NS.app.visionCollection.fetch({
      reset: true
    });

    NS.app.start({
      visionCollection: NS.app.visionCollection
    });
  });

}(VisionLouisville));