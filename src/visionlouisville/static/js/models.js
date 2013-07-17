/*globals Backbone $ _ */

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
    },{
      type: Backbone.HasMany,
      key: 'sharers',
      relatedModel: 'UserModel',
    }]
  });

  NS.VisionCollection = Backbone.Collection.extend({
    url: '/api/visions/',
    comparator: function(vision) {
      var dateString = vision.get('created_at'),
          date = new Date(_.isUndefined(dateString) ? null : dateString);
      return -(date.valueOf());
    },
    model: NS.VisionModel,
    getMostSupportedByCategory: function() {
      function sortByCategory(a, b) {
        var aLen = a.get('supporters').length,
            bLen = b.get('supporters').length;

        if (aLen < bLen) {
          return -1;
        } else if (bLen < aLen) {
          return 1;
        }
        return 0;
      }

      var visionsByCategory = this.groupBy('category'),
          mostSupported = [];

      _.each(visionsByCategory, function(modelList, cat) {
        var model = _.last(modelList.sort(sortByCategory));
        mostSupported.push(model);
      });

      return mostSupported;
    }
  });

  NS.InputStreamCollection = Backbone.Collection.extend({
    url: '/api/stream/'
  });

  // Replies ==================================================================
  NS.ReplyModel = Backbone.RelationalModel.extend({});

  NS.ReplyCollection = Backbone.Collection.extend({
    url: '/api/replies/',
    comparator: 'created_at',
    model: NS.ReplyModel
  });

  // Users ====================================================================
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
    share: function(vision) {
      var sharers = vision.get('sharers');

      if (!sharers.contains(this)) {
        sharers.add(this);

        $.ajax({
          type: 'POST',
          url: vision.url() + '/share',
          error: function() { sharers.remove(this); }
        });
      }
    },
    isAuthenticated: function() {
      return !this.isNew();
    },
    isInGroup: function(group) {
      return (this.get('groups').indexOf(group) !== -1);
    }
  });

  NS.UserCollection = Backbone.Collection.extend({
    url: '/api/users/',
    comparator: function(user1, user2) {
      var orderByGroup = function(group) {
            if (user1.isInGroup(group) && !user2.isInGroup(group)) {
              return -1;
            } else if (user2.isInGroup(group) && !user1.isInGroup(group)) {
              return 1;
            }
          },
          orderByLastLoginDate = function() {
            var dateString1 = user1.get('last_login'),
                dateString2 = user2.get('last_login');
            if (dateString1 === dateString2) {
              return 0;
            } else if (dateString1 < dateString2) {
              return 1;
            } else if (dateString1 > dateString2) {
              return -1;
            }
          }

      // Mayors come first, then VIPs, then allies, then most recently active
      return orderByGroup('mayors') ||
            orderByGroup('vips') ||
            orderByGroup('allies') ||
            orderByLastLoginDate();
    },
    model: NS.UserModel
  });

}(VisionLouisville));