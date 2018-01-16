const $ = require('jquery');
const panzoom = require('jquery.panzoom');
const jqueryUi = require('jquery-ui-bundle');

module.exports = {
  $el: null,

  init(el) {
    this.$el = $(el);

    if (this.$el.length) {
      this.bindUiActions();
    }
  },

  showUserUpdateModal($el, formUrl, uid) {
    let data;
    $.get(formUrl, {
      uid: uid,
    }, (response) => {
      console.log(response);
      $el.find('.modal-body').html(response);
    });
  },

  bindUiActions() {
    // Bind show modal to clicks of the edit button for users list
    $('.user-update-btn').click((e) => {
      const $currentTarget = $(e.currentTarget);
      const modalId = $currentTarget.data('target');
      const formUrl = $currentTarget.data('url');
      const uid = $currentTarget.data('upk');

      this.showUserUpdateModal($(modalId), formUrl, uid);
    });
  },
};
