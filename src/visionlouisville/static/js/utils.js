/*globals _ jQuery */

var VisionLouisville = VisionLouisville || {};

(function(NS) {

  /* ============================================================
   * Helper code for preparing blocks of user-contributed text
   * for output. Derived from https://gist.github.com/arbales/1654670
   * ============================================================
   */
  var LINK_DETECTION_REGEX = new RegExp(
      "(" +
        // The URL scheme (e.g. 'http://' or 'ftp://')
        "(?:[a-z]+:\\/\\/)?" +

        // The domain
        "(?:" +
          "localhost|" +
          "(?:" +
            "(?:[a-z0-9\\-]+\\.)+" +
            "(?:[a-z]{2}|aero|arpa|biz|com|coop|edu|gov|info|int|jobs|mil|museum|name|nato|net|org|pro|travel|local|internal)" +
          ")" +
        ")" +

        // The port (optional)
        "(?::[0-9]{1,5})?" +

        // The path and querystring
        "(?:\\/[a-z0-9_\\-\\.~]+)*" +
        "(?:" +
          "\\/" +
          "(?:[a-z0-9_\\-\\.]*)" +
          "(?:\\?[a-z0-9+_\\-\\.%=&]*)?" +
        ")?" +

        // The hash
        "(?:#[a-zA-Z0-9!$&'\\(\\)*+.=-_~:@\\/?]*)?" +
      ")" +

      // Must be followed by non-URL characters, and white space or
      // the end of the string.
      "(" +
        "[^a-z0-9_\\-\\.]*" +
        "(?:\\s+|$)" +
      ")",

      'gi'
    );

  var TWITTER_USER_REGEX = new RegExp(
    // Preceded by any non-word character or the beginning of a string. We do
    // non-word because we don't want this to match an email address.
    "([^\\w]|^)" +

    // No more than 15 characters
    "@([a-z0-9_]{1,15})" +

    // Followed by non-valid Twitter username characters
    "([^a-z0-9_]|$)",

    'gi'
  );

  NS.Utils = {
    serializeObject: function(form) {
      var $form = jQuery(form),
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
    // Analytics

    log: function() {
      if (window.ga) {
        window.ga.apply(window, arguments);
      } else if (window.console.log) {
        window.console.log(Array.prototype.slice.call(arguments, 0));
      }
    },

    // ====================================================
    // String utils

    // Replace URLs like https://github.com with <a href='https://github.com'>github.com</a>
    linkify: function(safeContent) {
      return safeContent.replace(LINK_DETECTION_REGEX, function(match, url, suffix) {
        var address = (/[a-z]+:\/\//.test(url) ? url : "http://" + url);

        if (address[address.length-1] === '.') {
          address = address.slice(0, address.length-1);
          url = url.slice(0, url.length-1);
          suffix = '.' + suffix;
        }

        url = url.replace(/^https?:\/\//, '');
        url = NS.Utils.truncateChars(url, 40);
        return "<a href='" + address + "' target='_blank'>" + url + "</a>" + suffix;
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
    },

    // ====================================================
    // File and Image Handling

    // Convert from array buffer to string
    ab2str: function(buf) {
      return String.fromCharCode.apply(null, new Uint16Array(buf));
    },

    // Convert from string to array buffer
    str2ab: function(str) {
      var buf = new ArrayBuffer(str.length*2); // 2 bytes for each char
      var bufView = new Uint16Array(buf);
      for (var i=0, strLen=str.length; i<strLen; i++) {
        bufView[i] = str.charCodeAt(i);
      }
      return buf;
    },

    fileToCanvas: function(file, callback, options) {
      var fr = new FileReader();

      fr.onloadend = function() {
          // get EXIF data
          var exif = EXIF.readFromBinaryFile(new BinaryFile(this.result)),
              orientation = exif.Orientation;

          loadImage(file, function(canvas) {
            // rotate the image, if needed
            var rotated = NS.Utils.fixImageOrientation(canvas, orientation);
            callback(rotated);
          }, options);
      };

      fr.readAsArrayBuffer(file); // read the file
    },

    fixImageOrientation: function(canvas, orientation) {
      var rotated = document.createElement('canvas'),
          ctx = rotated.getContext('2d'),
          width = canvas.width,
          height = canvas.height;

      switch (orientation) {
          case 5:
          case 6:
          case 7:
          case 8:
              rotated.width = canvas.height;
              rotated.height = canvas.width;
              break;
          default:
              rotated.width = canvas.width;
              rotated.height = canvas.height;
      }


      switch (orientation) {
          case 1:
              // nothing
              break;
          case 2:
              // horizontal flip
              ctx.translate(width, 0);
              ctx.scale(-1, 1);
              break;
          case 3:
              // 180 rotate left
              ctx.translate(width, height);
              ctx.rotate(Math.PI);
              break;
          case 4:
              // vertical flip
              ctx.translate(0, height);
              ctx.scale(1, -1);
              break;
          case 5:
              // vertical flip + 90 rotate right
              ctx.rotate(0.5 * Math.PI);
              ctx.scale(1, -1);
              break;
          case 6:
              // 90 rotate right
              ctx.rotate(0.5 * Math.PI);
              ctx.translate(0, -height);
              break;
          case 7:
              // horizontal flip + 90 rotate right
              ctx.rotate(0.5 * Math.PI);
              ctx.translate(width, -height);
              ctx.scale(-1, 1);
              break;
          case 8:
              // 90 rotate left
              ctx.rotate(-0.5 * Math.PI);
              ctx.translate(-width, 0);
              break;
          default:
              break;
      }

      ctx.drawImage(canvas, 0, 0);

      return rotated;
    }
  };

}(VisionLouisville));