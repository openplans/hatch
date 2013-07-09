/*globals Backbone Handlebars $ _ Countable */

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

  NS.NoItemsView = Backbone.Marionette.ItemView.extend({
    template: '#no-items-tpl'
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

  NS.NoRepliesView = Backbone.Marionette.ItemView.extend({
    template: '#no-replies-tpl'
  });

  NS.VisionReplyView = Backbone.Marionette.ItemView.extend({
    template: '#reply-item-tpl',
    tagName: 'li'
  });

  NS.VisionDetailView = Backbone.Marionette.CompositeView.extend({
    template: '#item-tpl',
    itemView: NS.VisionReplyView,
    itemViewContainer: 'ul',
    emptyView: NS.NoRepliesView,
    events: {
      'click button.show-reply-btn': 'showReplyForm'
    },
    onRender: function() {
      console.log('init the char limit plugin');
      var self = this,
          area = this.$('.reply-text').get(0),
          $countLabel = this.$('.reply-count'),
          max = 132;

      Countable.live(area, function (counter) {
        var charsLeft = max - counter.all;
        $countLabel.html(charsLeft);

        if (charsLeft < 0) {
          self.$('.reply-container').removeClass('warning').addClass('error');
        } else if (charsLeft < 20) {
          self.$('.reply-container').removeClass('error').addClass('warning');
        } else {
          self.$('.reply-container').removeClass('warning error');
        }
      });
    },
    showReplyForm: function() {
      this.$('.reply-container').show();
      console.log('handleReplyBtnClick');
    }
  });

  NS.VisionFormView = Backbone.Marionette.ItemView.extend({
    template: '#form-tpl',
    events: {
      'submit form': 'handleFormSubmission'
    },
    handleFormSubmission: function(evt) {
      evt.preventDefault();
      var form = evt.target,
          $form = $(form),
          formArray = $form.serializeArray(),
          attrs = {},
          headers = {};

      _.each(formArray, function(obj){
        var $field = $form.find('[name="' + obj.name + '"]');
        if ($field.attr('data-placement') === 'header') {
          headers[obj.name] = obj.value;
        } else {
          attrs[obj.name] = obj.value;
        }
      });

      this.model.set(attrs, {silent: true});
      this.collection.add(this.model);
      this.model.save(null, {
        wait: true,
        headers: headers,
        error: function() {
          window.alert('Unable to save your vision. Please try again.');
        },
        success: function(model) {
          NS.app.router.navigate('/visions/' + model.id, {trigger: true});
        }
      });
    }
  });

}(VisionLouisville));