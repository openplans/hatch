/*globals Backbone Handlebars $ _ Swiper */

var VisionLouisville = VisionLouisville || {};

(function(NS) {
  // App ======================================================================
  NS.app = new Backbone.Marionette.Application();

  NS.app.addRegions({
    mainRegion: '.main'
  });

  NS.app.addInitializer(function(options){
    this.homeView = new NS.HomeView({
      collection: this.visionCollection
    });

    this.mainRegion.show(this.homeView);

    // Init this here b/c we know we're inserted into the dom at this point.
    // Important for height calculations.
    this.homeView.swiper = new Swiper(this.homeView.$('.swiper-container').get(0), {
      loop: true,
      calculateHeight: true
    });

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