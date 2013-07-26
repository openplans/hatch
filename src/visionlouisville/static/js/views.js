/*globals Backbone Handlebars $ _ Countable Event Swiper */

var VisionLouisville = VisionLouisville || {};

(function(NS) {
  // Handlebars support for Marionette
  Backbone.Marionette.TemplateCache.prototype.compileTemplate = function(rawTemplate) {
    return Handlebars.compile(rawTemplate);
  };

  // Base mixins

  NS.OrderedCollectionMixin = {
    // https://github.com/marionettejs/backbone.marionette/wiki/Adding-support-for-sorted-collections
    // Inspired by the above link, but it doesn't work when you start with an
    // empty (or unsorted) list.
    appendHtml: function(collectionView, itemView, index){
      var childrenContainer = collectionView.itemViewContainer ? collectionView.$(collectionView.itemViewContainer) : collectionView.$el,
          children = childrenContainer.children(),
          indices = childrenContainer.data('indices') || [],
          sortNumber = function(a,b) { return a - b; },
          goHereIndex;
      // console.log(index, $(itemView.el).find('.feed-item-title').text());

      // console.log('before', indices);
      indices.push(index);
      indices.sort(sortNumber);
      // console.log('after', indices);
      goHereIndex = indices.indexOf(index);
      // console.log('at', goHereIndex);

      if(goHereIndex === 0) {
        childrenContainer.prepend(itemView.el);
        // console.log('prepend');
      } else {
        // console.log('insert after', childrenContainer.children().eq(goHereIndex-1).find('.feed-item-title').text());
        childrenContainer.children().eq(goHereIndex-1).after(itemView.el);
      }

      childrenContainer.data('indices', indices);
    }
  };

  // Views ====================================================================
  NS.HomeView = Backbone.Marionette.Layout.extend({
    template: '#home-tpl',
    regions: {
      visionaries: '.visionaries-region',
      allies: '.allies-region',
      visionCarousel: '.vision-carousel-region'
    }
  });

  NS.AllySignupView = Backbone.Marionette.ItemView.extend({
    template: '#ally-signup-tpl',
    tagName: 'p'
  });

  // Vision List ==============================================================
  NS.VisionCarouselItemView = Backbone.Marionette.ItemView.extend({
    template: '#vision-carousel-item-tpl',
    className: 'swiper-slide'
  });

  NS.VisionCarouselView = Backbone.Marionette.CompositeView.extend({
    template: '#vision-carousel-tpl',
    itemView: NS.VisionCarouselItemView,
    itemViewContainer: '.swiper-wrapper',
    initCarousel: function() {
      var self = this,
          interval = 8000,
          intervalId;

      // It is important for this everything to be in the DOM for swiper to
      // be a happy little plugin.
      this.swiper = new Swiper(this.$('.swiper-container').get(0), {
        loop: true,
        pagination: this.$('.pagination').get(0),
        paginationClickable: true,
        calculateHeight: true,
        onTouchStart: function() {
          if (intervalId) {
            window.clearInterval(intervalId);
          }
        },
        onTouchEnd: function(swiper) {
          intervalId = window.setInterval(function() {
            swiper.swipeNext();
          }, interval);
        }
      });

      intervalId = window.setInterval(function() {
        self.swiper.swipeNext();
      }, interval);
    }
  });

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
    itemViewContainer: 'ul.vision-list',
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

      NS.Utils.log('send', 'event', 'vision-reply', 'new', this.model.id);

      var $form = this.$('.reply-form').show(),
          $field = $form.find(':input[type!=hidden]:first'),
          val = $field.val();

      $field.focus().val('').val(val);
    },
    handleFormSubmission: function(evt) {

      NS.Utils.log('event', 'vision-reply', 'save', this.model.id);

      evt.preventDefault();
      var form = evt.target,
          data = NS.Utils.serializeObject(form),
          reply = data.attrs;

      reply.author = NS.app.currentUser.get('id');
      reply.author_details = NS.app.currentUser.toJSON();
      reply.created_at = (new Date()).toISOString();

      if (this.charsLeft >= 0 && this.chars > 0) {
        // Save the reply
        this.collection.create(reply);

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

  NS.ReplyToVisionItemView = Backbone.Marionette.ItemView.extend({
    template: '#reply-to-vision-tpl',
    tagName: 'li'
  });

  NS.ReplyToVisionListView = Backbone.Marionette.CollectionView.extend({
    template: '#reply-to-vision-tpl',
    tagName: 'ul',
    className: 'unstyled-list vision-list',
    itemView: NS.ReplyToVisionItemView

  });


  // Avatars ==================================================================
  NS.UserAvatarView = Backbone.Marionette.ItemView.extend({
    template: '#user-avatar-tpl',
    tagName: 'li'
  });

  NS.UserAvatarListView = Backbone.Marionette.CompositeView.extend({
    itemView: NS.UserAvatarView,
    itemViewContainer: 'ul.user-list',
    appendHtml: NS.OrderedCollectionMixin.appendHtml
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
      'click .cancel-retweet-action': 'handleCancelRetweet',
      'click .vision-media-container': 'handleVisionMediaClick'
    },
    showReplyForm: function(evt) {
      evt.preventDefault();

      if (NS.app.currentUser.isAuthenticated()) {
        this.regionManager.get('replies').currentView.showReplyForm(evt);
      } else {
        this.$('.support-login-prompt').addClass('is-hidden');
        this.$('.retweet-login-prompt').toggleClass('is-hidden');
      }
    },
    handleSupport: function(evt) {
      evt.preventDefault();

      if (NS.app.currentUser.isAuthenticated()) {
        var vision = this.model,
            supporters = vision.get('supporters'),
            user = NS.app.currentUser;

        if (supporters.contains(user)) {

          NS.Utils.log('send', 'event', 'vision-support', 'remove', this.model.id);

          user.unsupport(vision);
          this.$('.support').removeClass('supported');
        } else {

          NS.Utils.log('send', 'event', 'vision-support', 'add', this.model.id);

          user.support(vision);
          this.$('.support').addClass('supported');
        }

        this.updateSupportCount();
      } else {

        // It's nice to know when unauthenticated users click support too
        NS.Utils.log('send', 'event', 'vision-support', 'add', this.model.id);

        this.$('.retweet-login-prompt').addClass('is-hidden');
        this.$('.support-login-prompt').toggleClass('is-hidden');
      }
    },
    updateSupportCount: function() {
      this.$('.total-support-count').html(this.totalSupportString());
    },
    handleRetweet: function(evt) {
      evt.preventDefault();
      var vision = this.model,
          sharers = vision.get('sharers'),
          user = NS.app.currentUser,
          alreadyShared = user.isAuthenticated() && _.contains(sharers, user.id);

      if (!user.isAuthenticated() || !alreadyShared) {
        NS.Utils.log('send', 'event', 'vision-retweet', 'start', this.model.id);
      }

      if (user.isAuthenticated() && !alreadyShared) {
        this.$('.confirm-retweet-prompt').removeClass('is-hidden');
      } else {
        this.$('.support-login-prompt').addClass('is-hidden');
        this.$('.retweet-login-prompt').toggleClass('is-hidden');
      }
    },
    handleConfirmRetweet: function(evt) {
      evt.preventDefault();
      var vision = this.model,
          sharers = vision.get('sharers'),
          user = NS.app.currentUser;

      if (!_.contains(sharers, user.id)) {

        NS.Utils.log('send', 'event', 'vision-retweet', 'confirm', this.model.id);

        user.share(vision);
        this.$('.retweet-link').addClass('retweeted');
        this.$('.support').addClass('supported');
        this.updateSupportCount();
      }

      this.$('.confirm-retweet-prompt').addClass('is-hidden');
    },
    handleCancelRetweet: function(evt) {
      evt.preventDefault();

      NS.Utils.log('send', 'event', 'vision-retweet', 'cancel', this.model.id);

      this.$('.confirm-retweet-prompt').addClass('is-hidden');
    },
    handleVisionMediaClick: function(evt) {
      evt.preventDefault();
      this.$('.vision-media-container').toggleClass('is-collapsed');
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
      'change .vision-category-list input': 'handleCategoryChange',
      'change .vision-media input': 'handleMediaFileChange'
    },
    ui: {
      file: 'input[type=file]',
      imagePreview: '.image-preview',
      submit: 'input[type=submit]'
    },
    onRender: function() {
      this.handleCategoryChange();
    },
    getFirstInvalidElement: function(form) {
      var invalidEl = null,
          $form = $(form);

      // For each form element
      $form.find('input, select, textarea').each(function(i, el) {
        if (el.validity && el.validity.valid === false) {
          invalidEl = el;
          return false;
        }
      });

      return invalidEl;
    },
    handleFormSubmission: function(evt) {
      evt.preventDefault();
      var form = evt.currentTarget,
          invalidEl = this.getFirstInvalidElement(form);

      if (invalidEl) {

        NS.Utils.log('send', 'event', 'vision', 'save', 'invalid');

        $(invalidEl).focus();
        invalidEl.select();
      } else {
        this.saveForm(form);
      }
    },
    saveForm: function(form) {
      var self = this,
          data = NS.Utils.serializeObject(form);

      // Disable the submit button until we get a response
      this.ui.submit.prop('disabled', true);

      this.model.set(data.attrs, {silent: true});
      this.collection.add(this.model);
      this.model.save(null, {
        wait: true,
        headers: data.headers,
        error: function() {

          NS.Utils.log('send', 'event', 'vision', 'save', 'fail');

          self.ui.submit.prop('disabled', false);
          window.alert('Unable to save your vision. Please try again.');
        },
        success: function(model) {

          var tweetFlag = (this.$('.vision-tweet input').is(':checked') ? 1 : 0);
          NS.Utils.log('send', 'event', 'vision', 'save', 'success', tweetFlag);

          NS.app.router.navigate('/visions/' + model.id, {trigger: true});
        }
      });

    },
    handleCategoryChange: function() {
      var category = this.$('.vision-category-list input:checked').val();

      if (category) {
        NS.Utils.log('send', 'event', 'vision', 'change-category', category);
      }

      this.$('.category-prompt').addClass('is-hidden')
        .filter('.' + category + '-prompt').removeClass('is-hidden');
    },
    handleMediaFileChange: function(evt) {
      var self = this,
          file,
          attachment;

      if(evt.target.files && evt.target.files.length) {
        file = evt.target.files[0];

        // Is it an image?
        if (file.type.indexOf('image') !== 0) {
          window.alert('Sorry, we only support images.');
          this.ui.file.val('');
          return;
        }

        NS.Utils.fileToCanvas(file, function(canvas) {
          canvas.toBlob(function(blob) {

            NS.Utils.log('send', 'event', 'vision', 'add-image');

            self.model.set('media', blob);
            var previewUrl = canvas.toDataURL('image/jpeg');
            self.ui.imagePreview.attr('src', previewUrl).removeClass('is-hidden');
          }, 'image/jpeg');
        }, {
          // TODO: make configurable
          maxWidth: 800,
          maxHeight: 800,
          canvas: true
        });
      }
    }
  });

  // Users ====================================================================
  NS.UserListLayout = Backbone.Marionette.Layout.extend({
    template: '#user-list-tpl',
    regions: {
      userList: '.user-list-region'
    }
  });

  NS.UserListItemView = Backbone.Marionette.ItemView.extend({
    template: '#user-list-item-tpl',
    tagName: 'li'
  });

  NS.UserListView = Backbone.Marionette.CollectionView.extend({
    tagName: 'ul',
    className: 'vision-list unstyled-list',
    itemView: NS.VisionListItemView,
    emptyView: NS.NoItemsView
  });

  NS.UserListWithFilterView = Backbone.Marionette.CollectionView.extend({
    tagName: 'ul',
    className: 'unstyled-list',
    itemView: NS.UserListItemView
  });

  NS.UserDetailView = Backbone.Marionette.Layout.extend({
    template: '#user-detail-tpl',
    regions: {
      content: '.content-region'
    },
    showVisions: function() {
      this.$('.tab').removeClass('is-current');
      this.$('a[href*="visions"]').parent('.tab').addClass('is-current');
      this.content.show(new NS.UserListView({
        collection: new Backbone.Collection(this.model.get('visions'))
      }));
    },
    showSupported: function() {
      this.$('.tab').removeClass('is-current');
      this.$('a[href*="supported"]').parent('.tab').addClass('is-current');
      this.content.show(new NS.UserListView({
        collection: new Backbone.Collection(this.model.get('supported'))
      }));
    },
    showReplies: function() {
      this.$('.tab').removeClass('is-current');
      this.$('a[href*="replies"]').parent('.tab').addClass('is-current');
      this.content.show(new NS.ReplyToVisionListView({
        // NOTE: see comments in the UserModel for an explanation as to why
        // this is differnt than visions and supported regions.
        collection: new Backbone.Collection(this.model.get('replies'))
      }));
    }
  });

}(VisionLouisville));