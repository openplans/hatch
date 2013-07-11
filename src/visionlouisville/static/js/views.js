/*globals Backbone Handlebars $ _ Countable Event */

var VisionLouisville = VisionLouisville || {};

(function(NS) {
  // Handlebars support for Marionette
  Backbone.Marionette.TemplateCache.prototype.compileTemplate = function(rawTemplate) {
    return Handlebars.compile(rawTemplate);
  };

  // Views ====================================================================
  NS.HomeView = Backbone.Marionette.Layout.extend({
    className: 'container',
    template: '#home-tpl',
    regions: {
      visionaries: '.visionaries-region',
      allies: '.allies-region',
      // Visions
      economy: '.economy .vision',
      health: '.health .vision',
      energy: '.energy .vision',
      living: '.living .vision',
      connectivity: '.connectivity .vision',
      identity: '.identity .vision',
      creativity: '.creativity .vision'
    },

    events: {
      'click .swiper-link': 'handleSwiperLinkClick'
    },

    initialize: function() {
      this.listenTo(this.collection, 'reset', this.renderRegions);
    },

    renderRegions: function() {
      var self = this;
      _.each(this.regions, function(selector, id) {
        var len = self.collection.size(),
            i = 0,
            model;

        for (i=0; i<len; i++) {
          model = self.collection.at(i);
          if (model.get('category').toLowerCase() === id) {
            self[id].show(new NS.HomeVisionView({model: model}));
            break;
          }
        }
      });
    },

    onRender: function() {
      this.renderRegions();
      this.delegateEvents();
    },

    onClose: function() {
      this.stopListening(this.collection);
    },

    handleSwiperLinkClick: function(evt) {
      var $link = $(evt.target),
          $parent = $link.parents('li'),
          index = $parent.index();

      evt.preventDefault();

      this.swiper.swipeTo(index, 500, true);
    }
  });

  NS.HomeVisionView = Backbone.Marionette.ItemView.extend({
    template: '#home-vision-tpl',
    tagName: 'p'
  });

  // Vision List ==============================================================
  NS.NoItemsView = Backbone.Marionette.ItemView.extend({
    template: '#no-items-tpl',
    tagName: 'li'
  });

  NS.VisionListItemView = Backbone.Marionette.ItemView.extend({
    template: '#list-item-tpl',
    tagName: 'li'
  });

  NS.VisionListView = Backbone.Marionette.CompositeView.extend({
    template: '#list-tpl',
    itemView: NS.VisionListItemView,
    itemViewContainer: 'ul',
    emptyView: NS.NoItemsView
  });

  // Replies ==================================================================
  NS.NoRepliesView = Backbone.Marionette.ItemView.extend({
    template: '#no-replies-tpl',
    tagName: 'li'
  });

  NS.ReplyView = Backbone.Marionette.ItemView.extend({
    template: '#reply-item-tpl',
    tagName: 'li'
  });

  NS.ReplyListView = Backbone.Marionette.CompositeView.extend({
    template: '#reply-list-tpl',
    itemView: NS.ReplyView,
    itemViewContainer: 'ul.replies-list',
    emptyView: NS.NoRepliesView,
    events: {
      'click .show-reply': 'showReplyForm',
      'submit form.reply-form': 'handleFormSubmission'
    },
    onRender: function() {
      var self = this,
          $countLabel = this.$('.reply-count'),
          $replyForm = this.$('.reply-form'),
          $submitBtn = this.$('.reply-btn'),
          max = 132;

      this.$replyArea = this.$('.reply-text');

      if (this.$replyArea.length) {
        Countable.live(this.$replyArea.get(0), function (counter) {
          self.chars = counter.all;
          self.charsLeft = max - counter.all;
          $countLabel.html(self.charsLeft);

          if (self.chars > 0 && self.chars <= max) {
            $submitBtn.prop('disabled', false);
          } else {
            $submitBtn.prop('disabled', true);
          }

          if (self.charsLeft < 0) {
            $replyForm.removeClass('warning').addClass('error');
          } else if (self.charsLeft < 20) {
            $replyForm.removeClass('error').addClass('warning');
          } else {
            $replyForm.removeClass('warning error');
          }
        });
      }
    },
    showReplyForm: function(evt) {
      evt.preventDefault();
      this.$('.reply-form').show()
          .find(':input[type!=hidden]:first').focus();
    },
    handleFormSubmission: function(evt) {
      evt.preventDefault();
      var form = evt.target,
          data = NS.Utils.serializeObject(form),
          reply = data.attrs;

      reply.author = NS.app.currentUser.get('id');
      reply.author_details = NS.app.currentUser.toJSON();
      reply.created_at = (new Date()).toISOString();

      if (this.charsLeft >= 0 && this.chars > 0) {
        // Save the reply
        this.model.get('replies').create(reply);

        // Reset the form
        form.reset();

        // Really force the counter to reset
        if ('oninput' in document) {
          // This is because jQuery doens't support input for some reason
          this.$replyArea.get(0).dispatchEvent(new Event('input'));
        } else {
          this.$replyArea.trigger('keyup');
        }
      }
    }
  });

  // Avatars ==================================================================
  NS.UserAvatarView = Backbone.Marionette.ItemView.extend({
    template: '#user-avatar-tpl',
    tagName: 'li'
  });

  NS.UserAvatarListView = Backbone.Marionette.CompositeView.extend({
    itemView: NS.UserAvatarView,
    itemViewContainer: 'ul.user-list'
  });

  // Support ==================================================================
  NS.NoSupportView = Backbone.Marionette.ItemView.extend({
    template: '#no-support-tpl',
    tagName: 'li'
  });

  NS.SupportListView = Backbone.Marionette.CompositeView.extend({
    template: '#support-list-tpl',
    itemView: NS.UserAvatarView,
    itemViewContainer: 'ul.user-list',
    emptyView: NS.NoSupportView,

    collectionEvents: {
      "add": "collectionChanged",
      "remove": "collectionChanged",
      "reset": "collectionChanged"
    },

    collectionChanged: function() {
      this.renderSummary();
    },

    renderSummary: function() {
      var html = Handlebars.templates['support-summary-tpl'](this.model.toJSON());
      this.$('.support-summary').html(html);
    }
  });

  // Vision Details ===========================================================
  NS.VisionDetailLayout = Backbone.Marionette.Layout.extend({
    template: '#item-tpl',
    regions: {
      replies: '.replies-region',
      support: '.support-region'
    },
    events: {
      'click .show-reply': 'showReplyForm',
      'click .support-link': 'handleSupport',
      'click .retweet-link': 'handleRetweet',
      'click .confirm-retweet-action': 'handleConfirmRetweet',
      'click .cancel-retweet-action': 'handleCancelRetweet'
    },
    showReplyForm: function(evt) {
      evt.preventDefault();
      this.regionManager.get('replies').currentView.showReplyForm(evt);
    },
    handleSupport: function(evt) {
      evt.preventDefault();

      if (NS.app.currentUser.isAuthenticated()) {
        var vision = this.model,
            supporters = vision.get('supporters'),
            user = NS.app.currentUser;

        if (supporters.contains(user)) {
          user.unsupport(vision);
          this.$('.support').removeClass('supported');
        } else {
          user.support(vision);
          this.$('.support').addClass('supported');
        }

        this.$('.total-support-count').html(this.totalSupportString());
      } else {
        this.$('.support-login-prompt').toggleClass('is-hidden');
      }
    },
    handleRetweet: function(evt) {
      evt.preventDefault();

      if (NS.app.currentUser.isAuthenticated()) {
        this.$('.confirm-retweet-prompt').removeClass('is-hidden');
      } else {
        this.$('.retweet-login-prompt').toggleClass('is-hidden');
      }
    },
    handleConfirmRetweet: function(evt) {
      evt.preventDefault();
      var vision = this.model,
          sharers = vision.get('sharers'),
          user = NS.app.currentUser;

      if (!sharers.contains(user)) {
        user.share(vision);
        this.$('.retweet').addClass('retweeted');
      }
    },
    handleCancelRetweet: function(evt) {
      evt.preventDefault();
      this.$('.confirm-retweet-prompt').addClass('is-hidden');
    },
    totalSupportString: function() {
      var count = this.model.get('supporters').length,
          countString;

      if (count >= 1000000) {
        countString = (Math.floor(count/100000))/10 + 'M';
      }
      else if (count >= 100000) {
        countString = Math.floor(count/100000) + 'K';
      }
      else if (count >= 1000) {
        countString = (Math.floor(count/100))/10 + 'K';
      }
      else {
        countString = count.toString();
      }

      return countString;
    }
  });

  // Vision Form ==============================================================
  NS.VisionFormView = Backbone.Marionette.ItemView.extend({
    template: '#form-tpl',
    events: {
      'submit form': 'handleFormSubmission',
      'change .vision-category-list input': 'handleCategoryChange'
    },
    onRender: function() {
      this.handleCategoryChange();
    },
    handleFormSubmission: function(evt) {
      evt.preventDefault();
      var form = evt.target,
          data = NS.Utils.serializeObject(form);

      this.model.set(data.attrs, {silent: true});
      this.collection.add(this.model);
      this.model.save(null, {
        wait: true,
        headers: data.headers,
        error: function() {
          window.alert('Unable to save your vision. Please try again.');
        },
        success: function(model) {
          NS.app.router.navigate('/visions/' + model.id, {trigger: true});
        }
      });
    },
    handleCategoryChange: function() {
      var category = this.$('.vision-category-list input:checked').val();
      this.$('.category-prompt').addClass('is-hidden')
        .filter('.' + category + '-prompt').removeClass('is-hidden');
    }
  });

}(VisionLouisville));