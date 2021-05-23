from apscheduler.schedulers.blocking import BlockingScheduler

from download_videos_yt import download_random_song

# Create an instance of scheduler and add function.
scheduler = BlockingScheduler()
scheduler.add_job(download_random_song, "interval", days=7)

scheduler.start()
