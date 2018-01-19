const $ = require('jquery');

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

  showGroupUpdateModal($el, formUrl, gid, mode) {
    let title;

    if (mode === 'create') {
      title = 'Create Group';
    } else if (mode === 'update') {
      title = 'Update Group';
    }

    $el.find('.modal-title').html(title);

    $.get(formUrl, {
      mode: mode,
    }, (response) => {
      $el.find('.modal-body').html(response);
      const $groupsForm = $el.find('#groups-form');

      $el.find('button.close.users-form-close').click((e) => {
        $el.modal('hide');
      });

      // Bind user save events -- form saves via AJAX
      $groupsForm.on('submit', (e) => {
        e.preventDefault();
        const status = this.updateUser(e.target);
        if (status === 'OK') $el.modal('hide');
      });

      // Bind user delete event
      $('.groups-delete-btn').click((e) => {
        // Show confirmation modal, and setup close buttons.
        const $groupsDeleteForm = $('#groups-delete-form-modal');
        $groupsDeleteForm.modal('show');

        $groupsDeleteForm.find('button.confirm-delete-btn').click((e) => {
          this.deleteUser(uid);
        });

        // Rebind close buttons since this is going to be a nested modal.
        // Without this (and removing data-dismiss from the modal), both the
        // delete and the user form modal will close when the delete modal
        // triggers a close.
        $.map([
          $groupsDeleteForm.find('button.close'),
          $groupsDeleteForm.find('button.close-btn')], (el) => {

          $(el).click(() => $groupsDeleteForm.modal('hide'));
        });
      });
    });
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
      mode: mode,
    }, (response) => {
      $el.find('.modal-body').html(response);
      const $usersForm = $el.find('#users-form');

      $el.find('button.close.users-form-close').click((e) => {
        $el.modal('hide');
      });

      // Bind user save events -- form saves via AJAX
      $usersForm.on('submit', (e) => {
        e.preventDefault();
        const status = this.updateUser(e.target);
        if (status === 'OK') $el.modal('hide');
      });

      // Bind user delete event
      $('.users-delete-btn').click((e) => {
        // Show confirmation modal, and setup close buttons.
        const $usersDeleteForm = $('#users-delete-form-modal');
        $usersDeleteForm.modal('show');

        $usersDeleteForm.find('button.confirm-delete-btn').click((e) => {
          this.deleteUser(uid);
        });

        // Rebind close buttons since this is going to be a nested modal.
        // Without this (and removing data-dismiss from the modal), both the
        // delete and the user form modal will close when the delete modal
        // triggers a close.
        $.map([
          $usersDeleteForm.find('button.close'),
          $usersDeleteForm.find('button.close-btn')], (el) => {

          $(el).click(() => $usersDeleteForm.modal('hide'));
        });
      });
    });
  },

  updateUser(form) {
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

  deleteUser(uid) {
    $.ajax(`/admin/users/${uid}/delete`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': this._getCsrfCookie(),
      }
    }).done((response) => {
      if (response.status === 'OK') {
        const $usersDeleteModal = $('#users-delete-form-modal');
        const $usersUpdateModal = $('#users-form-modal');
        $usersDeleteModal.modal('hide');
        $usersUpdateModal.modal('hide');

        $(`#user-item-${uid}`).remove();
      }
    });
  },

  bindUiActions() {
    // Bind show modal to clicks of the edit button for users list
    $('.users-update-btn, .users-create-btn').click((e) => {
      const $currentTarget = $(e.currentTarget);
      const modalId = $currentTarget.data('target');
      const formUrl = $currentTarget.data('url');
      const uid = $currentTarget.data('upk');
      const mode = $currentTarget.data('mode');

      this.showUserUpdateModal($(modalId), formUrl, uid, mode);
    });

    $('.groups-update-btn, .groups-create-btn').click((e) => {
      const $currentTarget = $(e.currentTarget);
      const modalId = $currentTarget.data('target');
      const formUrl = $currentTarget.data('url');
      const uid = $currentTarget.data('upk');
      const mode = $currentTarget.data('mode');

      this.showGroupUpdateModal($(modalId), formUrl, uid, mode);
    });
  },
};
