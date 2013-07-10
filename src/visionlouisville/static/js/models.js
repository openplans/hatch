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
      collectionType: 'ReplyCollection',
      reverseRelation: {
        key: 'vision',
        includeInJSON: Backbone.Model.prototype.idAttribute,
      }
    },{
      type: Backbone.HasMany,
      key: 'support',
      relatedModel: 'SupportModel',
      includeInJSON: Backbone.Model.prototype.idAttribute,
      collectionType: 'SupportCollection',
      reverseRelation: {
        key: 'vision',
        includeInJSON: Backbone.Model.prototype.idAttribute,
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

  NS.ReplyCollection = Backbone.Collection.extend({
    url: '/api/replies/',
    comparator: 'created_at',
    model: NS.ReplyModel
  });

  // Support ==================================================================
  NS.SupportModel = Backbone.RelationalModel.extend({});

  NS.SupportCollection = Backbone.Collection.extend({
    url: '/api/support/',
    comparator: 'created_at',
    model: NS.SupportModel
  });
}(VisionLouisville));