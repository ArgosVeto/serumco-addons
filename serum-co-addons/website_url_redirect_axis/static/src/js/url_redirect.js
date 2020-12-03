odoo.define('website_seo_redirection.website_seo_mod', function(require) {
    jQuery(function($) {
  var path =  window.location.href;
  var hash = window.location.href + '#'
  if (path != hash && !window.location.hash) {
      window.location = window.location + '#';
      window.location.reload();
  }
});
});