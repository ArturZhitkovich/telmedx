const DevicesView = require('main/devices');
const VideoView = require('main/video-view');

document.addEventListener('DOMContentLoaded', () => {

    DevicesView.init("#devices-page");
    VideoView.init("#device-video-page");

});
