import Vue from 'vue'
import App from './App.vue'
import store from './store'
import VueYoutube from 'vue-youtube'

window.addEventListener("DOMContentLoaded", function() {
          // get video dom element
        const video = document.querySelector('video');

        // request access to webcam
        navigator.mediaDevices.getUserMedia({video: {width: 426, height: 240}}).then((stream) => video.srcObject = stream);

        // returns a frame encoded in base64
        const getFrame = () => {
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            canvas.getContext('2d').drawImage(video, 0, 0);
            const data = canvas.toDataURL('image/png');
            return data;
        }
        const WS_URL = 'ws://localhost:5000/stream';
        const FPS = 3;
        const ws = new WebSocket(WS_URL);
        ws.onopen = () => {
            console.log(`Connected to ${WS_URL}`);
            setInterval(() => {
                ws.send(getFrame());
            }, 1000 / FPS);
        }
})

Vue.use(VueYoutube)
Vue.config.productionTip = false

new Vue({
  store,
  render: h => h(App)
}).$mount('#app')
