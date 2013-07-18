/*globals $ */

var VisionLouisville = VisionLouisville || {};

(function(NS) {

  /* ============================================================
   * Helper code for preparing blocks of user-contributed text
   * for output. Derived from https://gist.github.com/arbales/1654670
   * ============================================================
   */
  var LINK_DETECTION_REGEX = /(([a-z]+:\/\/)?(localhost|(([a-z0-9\-]+\.)+([a-z]{2}|aero|arpa|biz|com|coop|edu|gov|info|int|jobs|mil|museum|name|nato|net|org|pro|travel|local|internal)))(:[0-9]{1,5})?(\/[a-z0-9_\-\.~]+)*(\/([a-z0-9_\-\.]*)(\?[a-z0-9+_\-\.%=&amp;]*)?)?(#[a-zA-Z0-9!$&'()*+.=-_~:@/?]*)?).?(\s+|$)/gi;
  var TWITTER_USER_REGEX = /([^\w]|^)@([A-Za-z0-9_]{1,15})([^A-Za-z0-9_]|$)/;

  NS.Utils = {
    serializeObject: function(form) {
      var $form = $(form),
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

      return {
        headers: headers,
        attrs: attrs
      };
    },
    getCookie: function(name) {
      var cookieValue = null;
      if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
          var cookie = jQuery.trim(cookies[i]);
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    },

    // ====================================================
    // String utils

    // Replace URLs like https://github.com with <a href='https://github.com'>github.com</a>
    linkify: function(safeContent) {
      return safeContent.replace(LINK_DETECTION_REGEX, function(match, url) {
        var address = (/[a-z]+:\/\//.test(url) ? url : "http://" + url);
        url = match.replace(/^https?:\/\//, '');
        url = NS.Utils.truncateChars(url, 40);
        return "<a href='" + address + "' target='_blank'>" + url + "</a>";
      });
    },

    // Replace Twitter usernames like @atogle with <a href='https://twitter.com/atogle'>@atogle</a>
    twitterify: function(safeContent) {
      return safeContent.replace(TWITTER_USER_REGEX, function(match, leading, username, trailing) {
        var address = 'http://www.twitter.com/' + username;
        return leading + "<a href='" + address + "' target='_blank'>@" + username + "</a>" + trailing;
      });
    },

    // Line breaks become <br/>'s
    wrapify: function(safeContent) {
      return safeContent.replace(/\n/g, '<br/>');
    },

    truncateChars: function(text, maxLength, continuationString) {
      if (_.isUndefined(continuationString) || !_.isString(continuationString)) {
        continuationString = '...';
      }

      if (text && text.length > maxLength) {
        return text.slice(0, maxLength - continuationString.length) + continuationString;
      } else {
        return text;
      }
    }
  };

}(VisionLouisville));