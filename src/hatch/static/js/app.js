/*globals Backbone Handlebars $ _ Swiper Modernizr */

var Hatch = Hatch || {};

(function(NS) {
  'use strict';

  // Helpers ==================================================================
  NS.setIsFetched = function(obj) {
    obj.isFetched = true;
    obj.trigger('fetched', obj);
  };

  NS.getCategory = function(name) {
    return NS.app.categoryCollection.findWhere({name: name});
  };

  NS.getSubCollection = function(collectionMap, key, CollectionType, collectionFilter) {
    if (!collectionMap[key]) {
      collectionMap[key] = new CollectionType();
      collectionMap[key].fetch({
        data: collectionFilter,
        traditional: true,
        success: NS.setIsFetched
      });
    }
    return collectionMap[key];
  };

  NS.getVisionCollection = function(category) {
    return NS.getSubCollection(
      NS.app.visionCollections, category, NS.VisionCollection, { category: category }
    );
  };

  NS.getUserCollection = function(groups, visibleOnHome) {
    groups = groups.sort();
    var posgroups = _.filter(groups, function(group) { return group[0] !== '-'; }),
        neggroups = _.chain(groups)
          .filter(function(group) { return group[0] === '-'; })
          .map(function(neggroup) { return neggroup.slice(1); })
          .value(),
        filterOpts = { group: posgroups, notgroup: neggroups };

    if (visibleOnHome) { filterOpts['visible_on_home'] = 'on'; }

    return NS.getSubCollection(
      NS.app.userCollections, groups.join(',') + (visibleOnHome ? ':home' : ''), NS.UserCollection, filterOpts
    );
  };

  // Create a view and show it in a region only AFTER you get results back from
  // the model or collection.
  NS.showViewInRegion = function(obj, region, getView, options) {
    var $regionEl = $(region.el),
        origMinHeight = $regionEl.css('min-height'),

    render = function() {
      $regionEl.css({minHeight: origMinHeight});
      var view = getView(obj, options);
      region.show(view);
    },

    hasBeenFetched = function(obj) {
      if (obj.isFetched) { return true; }
      if (obj.collection) { return hasBeenFetched(obj.collection); }
      if (obj.parent) { return hasBeenFetched(obj.parent); }
      return false;
    };

    // If the object hasn't been fetched yet, lets wait for it.
    if (!hasBeenFetched(obj)) {

      // Show a spinner until we load the content.
      if (options && options.spinner) {
        $regionEl.css({minHeight: (options.spinner.radius*2 + (options.spinner.length + options.spinner.width)*2) * 1.5});
        new Spinner(options.spinner).spin($regionEl[0]);
      }

      // Render when the collection resets
      obj.once('fetched', function() {
        render();
      });
    }

    // If it has already been fetched, render it immediately.
    else {
      render();
    }
  };

  NS.scrollTops = {};
  // Router ===================================================================

  var appRoutes = {};
  appRoutes[NS.appConfig.vision_plural + '/:category/new']  =  'newVision';
  appRoutes[NS.appConfig.vision_plural + '/:category']      =  'home';
  appRoutes[NS.appConfig.vision_plural + '/:category/:id']  =  'showVision';

  _.extend(appRoutes, {
    'users/list':     'listUsers',
    'users/list/:id': 'listUsers',
    'users/:id/:tab': 'showUser',
    'users/:id':      'showUser',
    'notifications':  'userNotifications',
    'ally':           'allySignup',
    '':               'home',
    '*anything':      'anything'
  });

  NS.Router = Backbone.Marionette.AppRouter.extend({
    appRoutes: appRoutes,
    navigate: function(fragment, options) {
      var __super__ = Backbone.Marionette.AppRouter.prototype,
          path = NS.getCurrentPath();
      options = options || {};

      NS.scrollTops[path] = document.body.scrollTop || document.documentElement.scrollTop || 0;
      this.noscroll = options.noscroll;
      return __super__.navigate.call(this, fragment, options);
    }
  });

  NS.controller = {
    allySignup: function() {
      // TODO: Move to the config settings
      document.title = NS.appConfig.title + ' | Become an '+NS.appConfig.ally+'!';

      NS.app.mainRegion.show(new NS.AllySignupView({
        model: NS.app.currentUser
      }));
    },
    listVisions: function(category) {
      category = category || NS.app.activeCategoryName;

      // TODO: Move to the config settings
      document.title = NS.appConfig.title + ' | ' + NS.getCategory(category).get('prompt');

      NS.app.mainRegion.show(new NS.VisionListView({
        model: new Backbone.Model({category: category}),
        collection: NS.app.visionCollections[category]
      }));
    },
    newVision: function(category) {
      // TODO: Move to the config settings
      document.title = NS.appConfig.title + ' | What\'s your ' + NS.appConfig.vision +'?';
      NS.Utils.log('send', 'event', 'vision', 'new');

      // Protect against unauthenticated users.
      if (!NS.app.currentUser.isAuthenticated()) {
        NS.app.router.navigate('/', { trigger: true });
        return;
      }

      NS.app.mainRegion.show(new NS.VisionFormView({
        category: category,
        collection: NS.app.visionCollections[category],
        model: new NS.VisionModel({
          category: category,
          author: NS.app.currentUser.get('id')
        })
      }));
    },
    showVision: function(category, visionId) {
      var model;

      // Set to an int
      visionId = parseInt(visionId, 10);

      if (_.isNaN(visionId)) {
        this.home();
        return;
      }

      function renderVision(model) {
        var layout = new NS.VisionDetailLayout({
              model: model
            });

        // TODO: Move to the config settings
        document.title = NS.appConfig.title + ' | "' + NS.Utils.truncateChars(model.get('text'), 70) + '" by @' + model.get('author_details').username;
        NS.Utils.log('send', 'event', 'vision', 'show', visionId);

        // TODO: why is this necessary?
        layout.on('show', function() {
          layout.replies.show(new NS.ReplyListView({
            model: model,
            collection: model.get('replies')
          }));

          layout.support.show(new NS.SupportListView({
            model: model,
            collection: model.get('supporters')
          }));
        });

        NS.app.mainRegion.show(layout);

        if (NS.app.currentUser) {
          NS.app.currentUser.viewVision(visionId);
        }

      }

      if (NS.app.visionCollections[category] && NS.app.visionCollections[category].get(visionId)) {
        model = NS.app.visionCollections[category].get(visionId);
        renderVision(model);
      } else {
        model = new NS.VisionModel({id: visionId});
        model.fetch({
          success: function(model, response, options) {
            renderVision(model);
          }
        });
      }
    },
    home: function(category) {
      category = category || NS.app.activeCategoryName;

      // TODO: Move to the config settings
      document.title = NS.appConfig.title + ' | What\'s your '+ NS.appConfig.vision +'?';

      var categoryModel = NS.getCategory(category),
          homeView = new NS.HomeView({
            model: categoryModel
          }),

          inFirst = function(model, collection, count) {
            return _.chain(collection.models)
              .first(count)
              .pluck('cid')
              .contains(model.cid)
              .value();
          },

          getVisionsListView = function(collection) {
            return new NS.VisionListView({
              model: new Backbone.Model({category: category}),
              collection: collection
            });
          },

          getVisionariesListView = function(collection) {
            return new NS.UserAvatarListView({
              collection: new NS.FilteredCollection(collection, function(model) { return inFirst(model, collection, 20); }),
              template: '#home-visionaries-tpl'
            });
          },

          getAlliesListView = function(collection) {
            return new NS.UserAvatarListView({
              collection: new NS.FilteredCollection(collection, function(model) { return inFirst(model, collection, 20); }),
              template: '#home-allies-tpl'
            });
          };

      // Render the main view
      NS.app.mainRegion.show(homeView);

      homeView.category.show(new NS.HomeCategoryView({
        model: categoryModel
      }));

      // Render the visions
      NS.showViewInRegion(NS.getVisionCollection(category), homeView.visions, getVisionsListView, {spinner: NS.app.bigSpinnerOptions});
      // Render visionaries
      NS.showViewInRegion(NS.getUserCollection(['-allies'], true), homeView.visionaries, getVisionariesListView, {spinner: NS.app.smallSpinnerOptions});
      // Render allies
      NS.showViewInRegion(NS.getUserCollection(['allies'], true), homeView.allies, getAlliesListView);
    },
    anything: function() {
      NS.app.router.navigate('', {replace: true});
      this.home();
    },
    listUsers: function(id) {
      document.title = NS.appConfig.title + ' | See the ' + NS.Utils.capitalize(id || 'visionaries');

      var showAllies = (id === 'allies'),
          userListLayout = new NS.UserListLayout({
            model: new Backbone.Model({show_allies: showAllies})
          }),
          getUserListView = function(collection) {
            return new NS.UserListWithFilterView({collection: collection});
          };

      NS.app.mainRegion.show(userListLayout);
      NS.showViewInRegion(NS.getUserCollection([(showAllies ? '' : '-') + 'allies']), userListLayout.userList, getUserListView, {id: id, spinner: NS.app.bigSpinnerOptions});
    },
    showUser: function(id, tab) {
      var model, userId = id;

      // Set to an int
      userId = parseInt(userId, 10);

      if (_.isNaN(userId)) {
        this.home();
        return;
      }

      var getUserDetailView = function(model) {
        var view = new NS.UserDetailView({
              model: model
            }),
            isPersonal = (NS.app.currentUser.isAuthenticated() && id === NS.app.currentUser.id),
            logPrefix = isPersonal ? 'my-' : '',
            logSuffix = tab ? '-' + tab : '';

        document.title = NS.appConfig.title + ' | ' + model.get('full_name') + '\'s profile';

        view.on('show', function() {
          if (tab) {
            if (tab === 'supported') {
              view.showSupported();
            } else if (tab === 'replies') {
              view.showReplies();
            } else if (tab === NS.appConfig.vision_plural) {
              view.showVisions();
            }
          } else {
            // NOTE: this order matters
            if (model.get('visions').length) {
              view.showVisions();
            } else if(model.get('supported').length) {
              view.showSupported();
            } else if (model.get('replies').length) {
              view.showReplies();
            }
          }
          NS.Utils.log('send', 'event', logPrefix + 'profile' + logSuffix, 'show', id + ' (' + model.get('username') + '/' + model.get('full_name') + ')');
        });

        return view;
      };

      var visionariesCollection = NS.app.userCollections['-allies'] || NS.app.userCollections['-allies:home'],
          alliesCollection = NS.app.userCollections['allies'] || NS.app.userCollections['allies:home'],
          relatedUserCollection = Backbone.Relational.store.getCollection(NS.UserModel);

      if (visionariesCollection && visionariesCollection.get(userId)) {
        model = visionariesCollection.get(userId);
      }
      else if (alliesCollection && alliesCollection.get(userId)) {
        model = alliesCollection.get(userId);
      }
      else {
        // We need to check the Backbone.Relational.store's cached collection
        // first, because Backbone.Relational doesn't like more than one copy
        // of a model floating around (it'll throw an Error).
        model = relatedUserCollection.get(userId) || new NS.UserModel({id: userId});
        model.fetch({success: NS.setIsFetched});
      }

      NS.showViewInRegion(model, NS.app.mainRegion, getUserDetailView, {id: id, spinner: NS.app.bigSpinnerOptions});
    },
    userNotifications: function() {
      if (NS.currentUserData) {
        // TODO: Move to the config settings
        document.title = NS.appConfig.title + ' | Notifications';

        NS.app.mainRegion.show(new NS.NotificationListView({
          model: NS.app.currentUser,
          collection: NS.app.currentUser.notifications
          // collection: new Backbone.Collection([{id: 1}])
        }));

        NS.app.currentUser.checkNotifications();
      } else {
        this.home();
      }
    }
  };

  NS.getCurrentPath = function() {
    var root = Backbone.history.root,
        fragment = Backbone.history.fragment;
    return root + fragment;
  };

  NS.getLoginUrl = function(redirect) {
    if (!redirect) {
      redirect = NS.getCurrentPath();
    }
    return NS.loginURL + '?next=' + redirect;
  };

  // App ======================================================================
  NS.app = new Backbone.Marionette.Application();

  // Show a spinner until we load the main region content.
  NS.app.bigSpinnerOptions = {
    lines: 13, length: 0, width: 10, radius: 30, corners: 1, rotate: 0,
    direction: 1, color: '#000', speed: 1, trail: 60, shadow: false,
    hwaccel: false, className: 'spinner', zIndex: 2e9, top: 'auto',
    left: 'auto'
  };

  NS.app.smallSpinnerOptions = {
    lines: 13, length: 0, width: 3, radius: 10, corners: 1, rotate: 0,
    direction: 1, color: '#000', speed: 1, trail: 60, shadow: false,
    hwaccel: false, className: 'spinner', zIndex: 2e9, top: 'auto',
    left: 'auto'
  };

  NS.app.addRegions({
    mainRegion: '.main'
  });


  NS.app.addInitializer(function(options){
    // Construct a new app router
    this.router = new NS.Router({
      controller: NS.controller
    });

    // Gobal-level events
    this.router.bind('route', function(route, router) {
      var path = NS.getCurrentPath(),
          scrollTop = NS.scrollTops[path] || 0;

      NS.Utils.log('send', 'pageview', NS.getCurrentPath());
      if (!this.noscroll) {
        document.body.scrollTop = document.documentElement.scrollTop = scrollTop;
      }
      $('.authentication-link-login').attr('href', NS.getLoginUrl());
      $('.user-menu').removeClass('is-open');
    });

    $('.user-menu-avatar').click(function(evt) {
      evt.preventDefault();
      $('.user-menu').toggleClass('is-open');
    });

    Backbone.history.start({ pushState: Modernizr.history, silent: true });
    if(!Modernizr.history) {
      var rootLength = Backbone.history.options.root.length,
          fragment = window.location.pathname.substr(rootLength),
          url;

      if (fragment) {
        Backbone.history.navigate(fragment, { trigger: true });
        url = window.location.protocol + '//' + window.location.host +
            Backbone.history.options.root + '#' + fragment;

        // Do a full redirect so we don't get urls like /visions/7#visions/7
        window.location = url;
      } else {
        Backbone.history.loadUrl(Backbone.history.getFragment());
      }
    } else {
      Backbone.history.loadUrl(Backbone.history.getFragment());
    }

    // Globally capture clicks. If they are internal and not in the pass
    // through list, route them through Backbone's navigate method.
    $(document).on('click', 'a[href^="/"]', function(evt) {
      var $link = $(evt.currentTarget),
          href = $link.attr('href'),
          noscroll = !_.isUndefined($link.attr('data-noscroll')),
          replace = !_.isUndefined($link.attr('data-replace')),
          url;

      // Allow shift+click for new tabs, etc.
      if ((href === '/' ||
           href.indexOf('/' + NS.appConfig.vision_plural) === 0 ||
           href.indexOf('/users') === 0 ||
           href.indexOf('/notifications') === 0) &&
           !evt.altKey && !evt.ctrlKey && !evt.metaKey && !evt.shiftKey) {
        evt.preventDefault();

        if (href.indexOf('new') !== -1) {
          if (!NS.app.currentUser.isAuthenticated()) {
            window.alert('Sign in to share your story!');
            return;
          }
        }

        // Remove leading slashes and hash bangs (backward compatablility)
        url = href.replace(/^\//, '').replace('#!/', '');

        // # Instruct Backbone to trigger routing events
        NS.app.router.navigate(url, {
          trigger: true,
          noscroll: noscroll,
          replace: replace
        });

        return false;

      } else if (href.indexOf('/login') === 0) {
        NS.Utils.log('send', 'event', 'authentication', 'login');

      } else if (href.indexOf('/logout') === 0) {
        NS.Utils.log('send', 'event', 'authentication', 'logout');
      }

    });
  });

  NS.app.updateNotificationCount = function() {
    if (NS.app.currentUser) {
      var notifications = NS.app.currentUser.notifications,
          count = notifications.where({'is_new': true}).length,
          $notificationsCount = $('.notifications-count');

      $notificationsCount.html(count);

      if (count === 0) {
        $notificationsCount.addClass('is-hidden');
      } else {
        $notificationsCount.removeClass('is-hidden');
      }
    }
  };

  // Init =====================================================================
  $(function() {
    NS.app.categoryCollection = new Backbone.Collection(NS.categories);
    NS.app.activeCategoryName = NS.app.categoryCollection.findWhere({active: true}).get('name');
    NS.app.visionCollections = {};
    NS.app.userCollections = {};

    // Init and fetch the active collection
    NS.getVisionCollection(NS.app.activeCategoryName);

    // NS.app.userCollection = new NS.UserCollection();
    // NS.app.userCollection.on('reset', setIsFetched);
    // NS.app.userCollection.fetch({
    //   reset: true,
    //   cache: false,
    //   data: { visible_on_home: true }
    // });

    NS.app.currentUser = new NS.UserModel(NS.currentUserData || {});
    NS.app.currentUser.notifications = new Backbone.Collection(NS.notificationsData);
    NS.app.updateNotificationCount();

    NS.app.currentUser.notifications.on('change', function() {
      NS.app.updateNotificationCount();
    });

    // Set the appropriate authentication info for analytics
    var currentUserStatus;
    if (NS.app.currentUser.isAuthenticated()) {
      if (NS.app.currentUser.isInGroup('allies')) {
        currentUserStatus = 'ally';
      } else {
        currentUserStatus = 'visionary';
      }
    } else {
      currentUserStatus = 'anonymous';
    }
    NS.Utils.log('set', 'dimension1', currentUserStatus);

    NS.app.start();
  });

}(Hatch));