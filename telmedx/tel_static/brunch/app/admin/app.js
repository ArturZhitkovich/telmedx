const $ = require('jquery');
const bootstrap = require('bootstrap-sass/assets/javascripts/bootstrap');
const AdminViews = require('./admin-views');

document.addEventListener('DOMContentLoaded', () => {
  AdminViews.init('#admin');
});
