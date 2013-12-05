/*globals Backbone $ _ */

var Hatch = Hatch || {};

(function(NS) {
  'use strict';

  Backbone.Relational.store.addModelScope(NS);

  // Visions ==================================================================
  NS.VisionModel = Backbone.RelationalModel.extend({
    urlRoot: '/api/visions/',
    relations: [{
      type: Backbone.HasMany,
      key: 'replies',
      relatedModel: 'ReplyModel',
      collectionType: 'ReplyCollection',
      reverseRelation: {
        key: 'vision',
        includeInJSON: Backbone.Model.prototype.idAttribute
      }
    },{
      type: Backbone.HasMany,
      key: 'supporters',
      relatedModel: 'UserModel'
    }],
    sync: function(method, model, options) {
      if (method === 'create' && model.get('media')) {
        var attr, val;

        // If we are saving media, submit the model as a form
        options = options || {};
        options.data = new FormData();

        // Add all the model attributes to the form
        for (attr in model.attributes) {
          val = model.get(attr);
          if (!_.isUndefined(val)) {
            options.data.append(attr, val);
          }
        }

        // Send multipart form data (see http://stackoverflow.com/a/5976031/123776 for details)
        options.contentType = false;
        options.processData = false;

        // Request to get JSON back
        options.dataType = 'json';
      }

      return Backbone.sync(method, model, options);
    }
  });

  NS.FilteredCollection = Backbone.Collection.extend({
    constructor: function(parent, key) {
      // Construct as a normal empty collection
      Backbone.Collection.apply(this);

      var self = this;
      this.parent = parent;
      this.key = key;

      // Listen to events on the parent to stay in sync
      parent.on('reset', function() {
        self.reset(parent.filter(key));
      });
      parent.on('add', function(model) {
        if (key(model)) self.add(model);
      });
      parent.on('remove', function(model) {
        if (self.get(model.cid)) self.remove(model);
      });

      this.reset(parent.filter(key));
    }
  });

  NS.PaginatedCollection = Backbone.Collection.extend({
    parse: function(response) {
      this.metadata = _.clone(response);
      delete this.metadata.results;

      return response.results;
    },

    hasNextPage: function(response) {
      return !!this.metadata.next;
    },

    fetchNextPage: function(success, error) {
      var collection = this;

      if (this.metadata.next) {
        collection.fetch({
          remove: false,
          url: collection.metadata.next,
          success: success,
          error: error
        });
      }
    }
  });

  NS.VisionCollection = NS.PaginatedCollection.extend({
    url: '/api/visions',
    comparator: function(vision) {
      var dateString = vision.get('tweeted_at'),
          date = new Date(_.isUndefined(dateString) ? null : dateString);
      return -(date.valueOf());
    },
    model: NS.VisionModel,
    getFeatured: function() {
      return this.where({'featured': true});
    }
  });

  // Replies ==================================================================
  NS.ReplyModel = Backbone.RelationalModel.extend({});

  NS.ReplyCollection = Backbone.Collection.extend({
    url: '/api/replies',
    comparator: 'tweeted_at',
    model: NS.ReplyModel
  });

  // Users ====================================================================
  NS.UserModel = Backbone.RelationalModel.extend({
    // Replies not added because the Vision model specifies (rightly) that
    // a reply should be rendered as an ID (to support saving a reply with a
    // vision ID). This does not allow us to render a reply on the user profile
    // page with the vision as context since we only have the ID. Instead,
    // we'll ignore the relationship and deal with an array of raw attributes
    // until we get smarter and think of a more elegant solution.

    // NOTE: This was causing a some sort of infinite loop.
    // TODO: Know enough about backbone-relational to know when and why an
    //       infinite loop would be caused by this. When you figure that out
    //       (and fix it), also change the user list view instantiations in
    //       the UserDetailView.
    //
    // relations: [{
    //   type: Backbone.HasMany,
    //   key: 'visions',
    //   relatedModel: 'VisionModel',
    //   collectionType: 'VisionCollection'
    // },{
    //   type: Backbone.HasMany,
    //   key: 'supported',
    //   relatedModel: 'VisionModel',
    //   collectionType: 'VisionCollection'
    // }],

    checkNotifications: function() {
      $.ajax({
        type: 'DELETE',
        url: '/api/notifications'
      });
    },
    viewVision: function(vision) {
      if (vision && vision.hasOwnProperty('id')) {
        vision = vision.id;
      }

      if (this.notifications) {
        var changed = false;

        this.notifications.each(function(notification) {
          if (notification.get('is_new') && notification.get('properties')['vision'] === vision) {
            notification.set({'is_new': false}, {silent: true});
            changed = true;
          }
        });

        if (changed) {
          this.notifications.trigger('change');
        }
      }
    },
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
      var sharers = vision.get('sharers'),
          supporters = vision.get('supporters'),
          alreadySupported = supporters.contains(this);

      if (!_.contains(sharers, this.id)) {
        supporters.add(this);
        vision.set('sharers', _.union(sharers, [this.id]));

        $.ajax({
          type: 'POST',
          url: vision.url() + '/share',
          error: function() {
            vision.set('sharers', sharers);
            if (!alreadySupported) {
              supporters.remove(this);
            }
          }
        });
      }
    },
    isAuthenticated: function() {
      return !this.isNew();
    },
    isInGroup: function(group) {
      if (_.isUndefined(this.get('groups'))) {
        return false;
      } else {
        return (this.get('groups').indexOf(group) !== -1);
      }
    }
  });

  NS.UserCollection = NS.PaginatedCollection.extend({
    url: '/api/users',
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
          };

      // Mayors come first, then VIPs, then allies, then most recently active
      return orderByGroup('mayors') ||
            orderByGroup('vips') ||
            orderByGroup('allies') ||
            orderByLastLoginDate();
    },
    model: NS.UserModel
  });

}(Hatch));