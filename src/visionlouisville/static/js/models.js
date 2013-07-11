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
      collectionType: 'ReplyCollection',
      reverseRelation: {
        key: 'vision',
        includeInJSON: Backbone.Model.prototype.idAttribute,
      }
    },{
      type: Backbone.HasMany,
      key: 'supporters',
      relatedModel: 'UserModel',
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

  // User ====================================================================`
  NS.UserModel = Backbone.RelationalModel.extend({
    support: function(vision) {
      var supporters = vision.get('supporters');

      if (!supporters.contains(this)) {
        supporters.add(this);

        $.ajax({
          type: 'PUT',
          url: vision.url() + '/support',
          error: function() { supporters.remove(this); }
        });
      }
    },
    unsupport: function(vision) {
      var supporters = vision.get('supporters');

      if (supporters.contains(this)) {
        supporters.remove(this);

        $.ajax({
          type: 'DELETE',
          url: vision.url() + '/support',
          error: function() { supporters.add(this); }
        });
      }
    },
    isAuthenticated: function() {
      return !this.isNew();
    }
  });

}(VisionLouisville));