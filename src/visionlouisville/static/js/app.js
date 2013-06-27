/*globals Backbone Handlebars $ _ */

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
    // this.recentVisionsView = new NS.RecentVisionsView({
    //   collection: this.visionCollection
    // });

    this.mainRegion.show(this.homeView);

    // this.homeView.visionsRegion.show(this.recentVisionsView);
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