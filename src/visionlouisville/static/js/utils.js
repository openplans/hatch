/*globals $ */

var VisionLouisville = VisionLouisville || {};

(function(NS) {
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
    }
  };

}(VisionLouisville));