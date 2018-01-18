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
    let title;

    if (mode === 'create') {
      title = 'Create User';
    } else if (mode === 'update') {
      title = 'Update User';
    }

    $el.find('.modal-title').html(title);

    $.get(formUrl, {
      uid: uid,
      mode: mode,
    }, (response) => {
      $el.find('.modal-body').html(response);
      const $usersForm = $el.find('#users-form');

      // Bind user save events -- form saves via AJAX
      $usersForm.on('submit', (e) => {
        e.preventDefault();
        const status = this.postForm(e.target);
        if (status === 'OK') $el.modal('hide');
      });

      // Bind user delete event
      $('.user-delete-btn').click((e) => {
        // Show confirmation modal, and setup close buttons.
        const $usersDeleteForm = $('#users-delete-form');
        $usersDeleteForm.modal('show');

        // Rebind close buttons since this is going to be a nested modal.
        // Without this (and removing data-dismiss from the modal), both the
        // delete and the user form modal will close when the delete modal
        // triggers a close.
        $usersDeleteForm.find('button.close').click((e) => {
          $usersDeleteForm.modal('hide');
        });
        $usersDeleteForm.find('button.close-btn').click((e) => {
          $usersDeleteForm.modal('hide');
        });
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

  deleteUser() {

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
