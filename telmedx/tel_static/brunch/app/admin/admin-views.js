const $ = require('jquery');
const panzoom = require('jquery.panzoom');
const jqueryUi = require('jquery-ui-bundle');

module.exports = {
  $el: null,
  CSRF_TOKEN_NAME: 'csrftoken',
  CSRF_HEADER_NAME: 'HTTP_X_CSRFTOKEN',

  init(el) {
    this.$el = $(el);

    if (this.$el.length) {
      this.bindUiActions();
    }
  },

  _getCsrfCookie() {
    let cookieValue;
    const name = this.CSRF_TOKEN_NAME;

    if (document.cookie && document.cookie !== '') {
      let cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        let cookie = jQuery.trim(cookies[i]);
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }

    return cookieValue;
  },

  /**
   * Shows user update modal and binds AJAX events to injected form.
   *
   * @param $el Modal element
   * @param formUrl URL where we will post to. This is generally provided
   *        in the action of the form element.
   * @param uid user id that is getting updated
   * @param mode either 'edit' or 'create'
   */
  showUserUpdateModal($el, formUrl, uid, mode) {
    $.get(formUrl, {
      uid: uid,
      mode: mode,
    }, (response) => {
      $el.find('.modal-body').html(response);

      // Bind events to form
      $el.find('#users-form').on('submit', (e) => {
        e.preventDefault();
        const status = this.postForm(e.target);
        if (status === 'OK') $el.modal('hide');
      });
    });
  },

  postForm(form) {
    const $form = $(form);
    const formData = new FormData(form);
    const formUrl = $form.attr('action');
    let ret = false;

    $.ajax(formUrl, {
      method: 'POST',
      data: formData,
      processData: false,
      contentType: false,
    }).done((response) => {
      ret = response.status;
    });

    return ret;
  },

  bindUiActions() {
    // Bind show modal to clicks of the edit button for users list
    $('.user-update-btn').click((e) => {
      const $currentTarget = $(e.currentTarget);
      const modalId = $currentTarget.data('target');
      const formUrl = $currentTarget.data('url');
      const uid = $currentTarget.data('upk');
      const mode = $currentTarget.data('mode');

      this.showUserUpdateModal($(modalId), formUrl, uid, mode);
    });
  },
};
