var VisionLouisville = VisionLouisville || {};

(function(NS) {
  // Models ===================================================================
  NS.VisionCollection = Backbone.Collection.extend({
    url: '/api/visions/',
    comparator: 'created_at'
  });

}(VisionLouisville));