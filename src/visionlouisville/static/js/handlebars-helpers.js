/*globals Handlebars $ _ moment */

var VisionLouisville = VisionLouisville || {};

(function(NS) {
  Handlebars.registerHelper('authenticated', function(options) {
    return !!NS.currentUserData ? options.fn(this) : options.inverse(this);
  });

  Handlebars.registerHelper('if_is_moment', function(options) {
    return (this.id.toString().slice(0,6) === 'moment') ? options.fn(this) : options.inverse(this);
  });

  Handlebars.registerHelper('if_supported', function(options) {
    var userId, supportingIDs;
    
    if (!NS.currentUserData) return options.inverse(this);

    userId = NS.currentUserData['id'],
    supportingIds = _.pluck(this.supporters, 'id');
    return _.contains(supportingIds, userId) ? options.fn(this) : options.inverse(this);
  });

  Handlebars.registerHelper('if_shared', function(options) {
    var userId, sharingIDs;
    
    if (!NS.currentUserData) return options.inverse(this);

    userId = NS.currentUserData['id'],
    sharingIds = _.pluck(this.sharers, 'id');
    return _.contains(sharingIds, userId) ? options.fn(this) : options.inverse(this);
  });

  Handlebars.registerHelper('STATIC_URL', function() {
    return NS.staticURL;
  });

  Handlebars.registerHelper('LOGIN_URL', function(redirectTo, options) {
    if (arguments.length === 1) {
      options = redirectTo;
      redirectTo = undefined;
    }
    return NS.getLoginUrl(redirectTo);
  });

  function linebreaks(text) {
    return text.replace(/\n/g, '<br />');
  }

  Handlebars.registerHelper('category_prompt', function(category) {
    return NS.Config.categories[category].prompt;
  });

  Handlebars.registerHelper('window_location', function() {
    return window.location.toString();
  });

  Handlebars.registerHelper('truncated_window_location', function(maxLength) {
    return truncateChars(window.location.toString(), maxLength);
  })

  // usage: {{pluralize collection.length 'quiz' 'quizzes'}}
  Handlebars.registerHelper('pluralize', function(number, single, plural) {
    return (number === 1) ? single : plural;
  });

  Handlebars.registerHelper('fromnow', function(datetime) {
    if (datetime) {
      return moment(datetime).fromNow();
    }
    return '';
  });

  Handlebars.registerHelper('formatdatetime', function(datetime, format) {
    if (datetime) {
      return moment(datetime).format(format);
    }
    return '';
  });

  Handlebars.registerHelper('select', function(value, options) {
    var $el = $('<div/>').html(options.fn(this)),
      selectValue = function(v) {
        $el.find('[value="'+v+'"]').attr({
          checked: 'checked',
          selected: 'selected'
        });
      };

    if (_.isArray(value)) {
      _.each(value, selectValue);
    } else {
      selectValue(value);
    }

    return $el.html();
  });

  /* ============================================================
   * Helper code for preparing blocks of user-contributed text 
   * for output. Derived from https://gist.github.com/arbales/1654670
   * ============================================================
   */
  var LINK_DETECTION_REGEX = /(([a-z]+:\/\/)?(([a-z0-9\-]+\.)+([a-z]{2}|aero|arpa|biz|com|coop|edu|gov|info|int|jobs|mil|museum|name|nato|net|org|pro|travel|local|internal))(:[0-9]{1,5})?(\/[a-z0-9_\-\.~]+)*(\/([a-z0-9_\-\.]*)(\?[a-z0-9+_\-\.%=&amp;]*)?)?(#[a-zA-Z0-9!$&'()*+.=-_~:@/?]*)?).?(\s+|$)/gi;
   
  // Handlebars is presumed, but you could swap out 
  var ESCAPE_EXPRESSION_FUNCTION = Handlebars.Utils.escapeExpression;
  var MARKSAFE_FUNCTION = function(str) { return new Handlebars.SafeString(str); };
   
  // Replace URLs like https://github.com with <a href='https://github.com'>github.com</a>
  function linkify(safeContent) {
    return safeContent.replace(LINK_DETECTION_REGEX, function(match, url) {
      var address = (/[a-z]+:\/\//.test(url) ? url : "http://" + url);
      url = match.replace(/^https?:\/\//, '');
      url = truncateChars(url, 40)
      return "<a href='" + address + "' target='_blank'>" + url + "</a>";
    });
  }

  // Line breaks become <br/>'s
  function wrapify(safeContent) {
    return safeContent.replace(/\n/g, '<br/>');
  }

  function truncateChars(text, maxLength) {
    if (text.length > maxLength) {
      return text.slice(0, maxLength-3) + '...';
    } else {
      return text
    }
  }

  function formatTextForHTML(content) {
    // Start by escaping expressions in the content to make them safe.
    var safeContent = ESCAPE_EXPRESSION_FUNCTION(content);
    safeContent = linkify(safeContent);
    safeContent = wrapify(safeContent);
    return MARKSAFE_FUNCTION(safeContent); // Mark our string as safe, since it is.
  }

  Handlebars.registerHelper('formattext', formatTextForHTML);
  Handlebars.registerHelper('truncatechars', truncateChars);

}(VisionLouisville));
