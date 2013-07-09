/*globals Backbone */

var VisionLouisville = VisionLouisville || {};

(function(NS) {
  'use strict';

  Backbone.Relational.store.addModelScope(NS);

  // Visions ==================================================================
  NS.VisionModel = Backbone.RelationalModel.extend({
    relations: [{
      type: Backbone.HasMany,
      key: 'replies',
      relatedModel: 'ReplyModel',
      includeInJSON: Backbone.Model.prototype.idAttribute,
      // collectionType: 'ReplyCollection',
      reverseRelation: {
        key: 'vision'
      }
    }]
  });

  NS.VisionCollection = Backbone.Collection.extend({
    url: '/api/visions/',
    comparator: 'created_at',
    model: NS.VisionModel
  });

  // Replies ==================================================================
  NS.ReplyModel = Backbone.RelationalModel.extend({});

}(VisionLouisville));