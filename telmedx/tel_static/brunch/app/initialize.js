const $ = require('jquery'),
    DevicesView = require('main/devices'),
    VideoView = require('main/video-view')
;

document.addEventListener('DOMContentLoaded', () => {

    DevicesView.init("#devices-page");
    VideoView.init("#device-video-page")

});
