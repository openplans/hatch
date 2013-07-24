/*globals Backbone Handlebars $ _ Swiper Modernizr */

var VisionLouisville = VisionLouisville || {};

(function(NS) {
  'use strict';

  // Router ===================================================================
  NS.Router = Backbone.Marionette.AppRouter.extend({
    appRoutes: {
      'visions/:category/new': 'newVision',
      'visions/:category/list': 'listVisions',
      'visions/new': 'newVision',
      'visions/list': 'listVisions',
      'visions/:id': 'showVision',
      'ally-signup': 'allySignup',
      '': 'home'
    }
  });

  NS.controller = {
    allySignup: function() {
      // TODO: Move to the config settings
      document.title = "#VizLou | Become an ally!";

      NS.app.mainRegion.show(new NS.AllySignupView({
        model: NS.app.currentUser
      }));
    },
    listVisions: function(listCategory) {
      // TODO: Move to the config settings
      document.title = "#VizLou | Explore visions" + (listCategory ? ' \u2014 ' + listCategory : '');

      var render = function() {
        var model, collection;

        if (listCategory) {
          model = new Backbone.Model({category: listCategory});
          collection = new Backbone.Collection(
            NS.app.visionCollection.filter(function(model) {
              var category = model.get('category');
              return (!!category ? category : '').toLowerCase() === listCategory;
            }));
        } else {
          model = new Backbone.Model();
          collection = NS.app.visionCollection;
        }

        NS.app.mainRegion.show(new NS.VisionListView({
          model: model,
          collection: collection
        }));
      };

      // Nothing in the collection? It's not done fetching. Let's wait for it.
      if (NS.app.visionCollection.size() === 0) {
        // Render when the collection resets
        NS.app.visionCollection.once('reset', function() {
          render();
        });
      } else {
        render();
      }
    },
    newVision: function(category, momentId) {
      // TODO: Move to the config settings
      document.title = "#VizLou | Add your vision";
      NS.Utils.log('send', 'event', 'vision-new');

      // Protect against unauthenticated users.
      if (!NS.app.currentUser.isAuthenticated()) {
        NS.app.router.navigate('/', { trigger: true });
        return;
      }

      NS.app.mainRegion.show(new NS.VisionFormView({
        category: category,
        collection: NS.app.visionCollection,
        model: new NS.VisionModel({
          category: category,
          inspiration: momentId,
          author: NS.app.currentUser.get('id')
        })
      }));
    },
    showVision: function(id) {
      function render() {
        var model = NS.app.visionCollection.get(id),
            layout = new NS.VisionDetailLayout({
              model: model
            });

        // TODO: Move to the config settings
        document.title = '#VizLou | "' + NS.Utils.truncateChars(model.get('text'), 70) + '" by @' + model.get('author_details').username;
        NS.Utils.log('send', 'event', 'vision-show', id);

        NS.app.mainRegion.show(layout);

        layout.replies.show(new NS.ReplyListView({
          model: model,
          collection: model.get('replies')
        }));

        layout.support.show(new NS.SupportListView({
          model: model,
          collection: model.get('supporters')
        }));
      }

      id = parseInt(id, 10);

      // Nothing in the collection? It's not done fetching. Let's wait for it.
      if (NS.app.visionCollection.size() === 0) {
        // Render when the collection resets
        NS.app.visionCollection.once('reset', function() {
          render();
        });
      } else {
        render();
      }
    },
    home: function() {
      // TODO: Move to the config settings
      document.title = "#VizLou | What's your vision for the future of Louisville?";

      var homeView = new NS.HomeView({
            collection: NS.app.visionCollection
          }),
          visionaryCollection = new NS.UserCollection(),
          allyCollection = new NS.UserCollection();

      function renderVisionCarousel() {
        var visionCarouselView = new NS.VisionCarouselView({
          collection: new NS.VisionCollection(
            NS.app.visionCollection.getFeatured()
          )
        });

        homeView.visionCarousel.on('show', function() {
          // Init the carousel after we're in the DOM
          visionCarouselView.initCarousel();
        });
        homeView.visionCarousel.show(visionCarouselView);
      }

      NS.app.mainRegion.show(homeView);

      visionaryCollection.fetch({
        data: {notgroup: 'allies', visible_on_home: true},
        success: function(collection, response, options) {
          homeView.visionaries.show(new NS.UserAvatarListView({
            collection: new NS.UserCollection(collection.slice(0, 20)),
            template: '#home-visionaries-tpl'
          }));
        }
      });

      allyCollection.fetch({
        data: {group: 'allies', visible_on_home: true},
        success: function(collection, response, options) {
          homeView.allies.show(new NS.UserAvatarListView({
            collection: new NS.UserCollection(collection.slice(0, 20)),
            template: '#home-allies-tpl'
          }));
        }
      });

      // Nothing in the collection? It's not done fetching. Let's wait for it.
      if (NS.app.visionCollection.size() === 0) {
        // Render when the collection resets
        NS.app.visionCollection.once('reset', function() {
          renderVisionCarousel();
        });
      } else {
        renderVisionCarousel();
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
      NS.Utils.log('send', 'pageview', NS.getCurrentPath());
      $('.authentication-link-login').attr('href', NS.getLoginUrl());
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
    $(document).on("click", "a[href^='/']", function(evt) {
      var href = $(evt.currentTarget).attr('href'),
          url;

      // Allow shift+click for new tabs, etc.
      if ((href === '/' ||
           href.indexOf('/visions') === 0) &&
           !evt.altKey && !evt.ctrlKey && !evt.metaKey && !evt.shiftKey) {
        evt.preventDefault();

        if (href.indexOf('new') !== -1) {
          if (!NS.app.currentUser.isAuthenticated()) {
            window.alert('Sign in to create a new vision!');
            return;
          }
        }

        // Remove leading slashes and hash bangs (backward compatablility)
        url = href.replace(/^\//, '').replace('#!/', '');

        // # Instruct Backbone to trigger routing events
        NS.app.router.navigate(url, { trigger: true });

        return false;
      }

    });
  });

  // Init =====================================================================
  $(function() {
    NS.app.visionCollection = new NS.VisionCollection();
    NS.app.visionCollection.fetch({
      reset: true,
      cache: false
    });

    NS.app.currentUser = new NS.UserModel(NS.currentUserData || {},
                                          {url: '/api/users/current/'});

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

    NS.app.start({
      visionCollection: NS.app.visionCollection
    });
  });

}(VisionLouisville));