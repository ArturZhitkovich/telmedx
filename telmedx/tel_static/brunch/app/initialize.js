const DevicesView = require('main/devices');
const VideoView = require('main/video-view');
const AdminViews = require('admin/admin-views');

document.addEventListener('DOMContentLoaded', () => {
    DevicesView.init('#devices-page');
    VideoView.init('#device-video-page');
    AdminViews.init('#admin');
  }
);
