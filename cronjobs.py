from apscheduler.schedulers.blocking import BlockingScheduler

from download_videos_yt import download_random_song, update_videos_url_from_playlist

# Create an instance of scheduler and add function.
scheduler = BlockingScheduler()
scheduler.add_job(download_random_song, "interval", days=3)
scheduler.add_job(update_videos_url_from_playlist, "interval", days=30)

scheduler.start()
