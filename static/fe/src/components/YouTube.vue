<template>
    <div>
        <youtube style="width: 98vw; height: 90vh;" autoplay :video-id="videoId" ref="youtube" @playing="playing" @ready="readyHandler" @paused="paused"></youtube>
        <a href="/video_dash" @click="handle_click">To analysis</a>
    </div>
</template>

<script>
    import axios from 'axios';

    const headers = {
        'Content-Type': 'application/json',
    }

    export default {
        name: 'YouTube',

        data() {
            return {
                videoId: '6hlx2Jr-oG0',
                player: null
            }
        },

        methods: {
            handle_click(e) {
                e.preventDefault()
                axios.post("/stop_emo_tracking")
                    .then(() => {
                        window.location.href = "/video_dash"
                    })
            },
            async readyHandler() {
                this.player = this.$refs.youtube.player;

                axios({
                    method: 'post',
                    url: '/api/video',
                    data: await this.player.getDuration(),
                    headers: headers
                });
            },

            async handleState() {
                const state = await this.player.getPlayerState();
                const time = await this.player.getCurrentTime();
                console.log(this.player.getVideoData);

                axios({
                    method: 'post',
                    url: '/api/video_state',
                    data:  {
                        video_name: 'kek',
                        current_time: time,
                        current_state: state
                    },
                    headers: headers
                })
            },

            playVideo() {
                this.player.playVideo()
            },

            paused(e) {
                this.handleState();
                clearInterval(this.interval);
            },

            playing(e) {
                this.interval = setInterval(this.handleState, 1000)
            }
        },

        mounted() {
            clearInterval(this.interval);
        }
    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
