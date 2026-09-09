---
title: Creating A GPX File From Raw Oura Data
description: How to create a GPX file from raw Oura data.
summary: How to create a GPX file from raw Oura data.
slug: creating-gpx-oura-data
date: 2026-07-25 00:00:01+0000
lastmod: 2026-09-08 00:00:01+0000
feature: henry-ren-8Eg9-cPCt00-unsplash.jpg
coverCaption: Photo by <a href="https://unsplash.com/@henryren?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Henry Ren</a> on <a href="https://unsplash.com/photos/a-spectator-holds-up-a-sign-at-a-running-race-8Eg9-cPCt00?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Unsplash</a>
draft: false
topics: [
    "Claude",
    "Git",
    "GitHub",
    "GPX",
    "Oura",
    "Python",
    "Strava",
]
---
## Post Updates

Update 9/8/2026: [Added a section](https://www.jaredszajkowski.com/posts/creating-gpx-oura-data/#script-versions) documenting the three versions of the extraction script, and updated the usage instructions to point at the current version.

## Introduction

I wear an Oura ring daily to track sleep, readiness, workouts, etc. I also use Strava to view and gain insights from the workouts, and the sync from Oura to Strava normally happens without issue.

As long as you manually track the workout in Oura (not an automatically detected activity), then end and save the workout, and then open the Strava app, Strava should automatically open the workout and prompt for additional details before saving it.

Recently, I tracked a workout with the Oura ring, but when I opened Strava to sync the workout, it didn't show the map, distance, or heart rate, which was a little disappointing. I ended up deleting that workout from Strava. My guess is that I hadn't opened Strava since the upgrade to Android 17 on my Pixel 7, and something happened with the cached data or the app simply just glitched.

I did some research through the Oura and Strava documentation, as well as numerous Reddit threads, but ultimately it seemed that if the workout didn't successfully sync to Strava on the first attempt, there was no way to attempt the sync again or add the workout manually.

The script has continued to evolve since I first published this post, mostly around cleaning up the raw GPS data - see [Script versions](#script-versions) below for what changed and why.

## Oura data export

I then ran across the Oura documentation for exporting raw data. This seemed promising at first - there must be a way to export a GPX file from Oura, and then manually upload to Strava, right? It turns out that when data is exported from Oura membership hub, it dumps CSV exports of (essentially) all the different data streams that are recorded, but it does not include any GPX files.

![Oura Data Export - 1](Oura_Data_1.png)
![Oura Data Export - 2](Oura_Data_2.png)

I started digging through the data, and quickly ran across the `workout.csv` file, which seemed to contain the high level workout data, including the session ID, activity type, calories burned, date, distance, start and end times, and a few other fields. I kept digging, and then found `rawlocation.csv`, `heartrate.csv`, and several other files that seemed relevant. Some of these files contain hundreds of thousands of lines, with second-by-second data.

## Script to create GPX file

With the CSV files in hand, I spun up Claude and began planning, with the initial prompt:

> I want to write a script that extracts all relevant data from each file in the repo for a specific session ID, to create a GPX file. Find the "id" column in "workouts.csv". From the session ID line in "workouts.csv", I want to extract the other column data for the session/workout. Then look through every other file in the repo for matching session ID data or data between the start and end dates of the workout.

I had the file name wrong (`workouts.csv` instead of `workout.csv`), but as expected Claude quickly figured out what I was referring to.

In short order, after a dozen or so prompt iterations, I created a Python script that took an input of the session ID, and produced a complete GPX file that could be uploaded into Strava or Garmin. The session export is attached below if you are interested in seeing the full prompt and response history.

There were a few clarifications along the way:

1. Claude wanted to know if I wanted sidecar JSON and Markdown files for data points that are not part of the GPX standard.
2. The script needed to isolate timestamps from the location file, based on the start and end times of the workout.
3. The timezone for the location data was UTC, not CT/CST, so Claude needed to correct for that.

After churning, it gave me the following response:

```text
● Here's everything the GPX carries. It's GPX 1.1 with the Garmin
  TrackPointExtension namespace.

  File-level (<metadata> + <trk>):
  - Track name — activity + day (e.g. running 2025-05-11)
  - Description — workout UUID + activity
  - Start time (UTC)

  Per trackpoint (<trkpt>), one point per rawlocation.csv row in the workout 
  window:

  ┌─────────────┬────────────────┬───────────────────────┬───────────────────┐
  │    Field    │  GPX element   │        Source         │       Notes       │
  ├─────────────┼────────────────┼───────────────────────┼───────────────────┤
  │             │                │                       │ always present    │
  │ Latitude    │ lat attribute  │ rawlocation.latitude  │ (points without   │
  │             │                │                       │ lat/lon are       │
  │             │                │                       │ skipped)          │
  ├─────────────┼────────────────┼───────────────────────┼───────────────────┤
  │ Longitude   │ lon attribute  │ rawlocation.longitude │ always present    │
  ├─────────────┼────────────────┼───────────────────────┼───────────────────┤
  │ Elevation   │ <ele>          │ rawlocation.altitude  │ meters; omitted   │
  │             │                │                       │ if blank          │
  ├─────────────┼────────────────┼───────────────────────┼───────────────────┤
  │ Timestamp   │ <time>         │ rawlocation.timestamp │ UTC, millisecond  │
  │             │                │                       │ precision         │
  ├─────────────┼────────────────┼───────────────────────┼───────────────────┤
  │ Heart rate  │ <gpxtpx:hr>    │ heartrate.bpm         │ nearest sample    │
  │             │                │                       │ within ±30 s      │
  ├─────────────┼────────────────┼───────────────────────┼───────────────────┤
  │             │                │                       │ derived           │
  │ Cadence     │ <gpxtpx:cad>   │ stepcount.steps       │ steps/min;        │
  │             │                │                       │ nearest bucket    │
  │             │                │                       │ within ±90 s      │
  ├─────────────┼────────────────┼───────────────────────┼───────────────────┤
  │             │                │                       │ nearest within ±5 │
  │ Temperature │ <gpxtpx:atemp> │ temperature.skin_temp │  min; this is     │
  │             │                │                       │ skin, not         │
  │             │                │                       │ ambient, temp     │
  ├─────────────┼────────────────┼───────────────────────┼───────────────────┤
  │             │                │                       │ m/s, taken        │
  │ Speed       │ <gpxtpx:speed> │ rawlocation.speed     │ directly from the │
  │             │                │                       │  same GPS row     │
  └─────────────┴────────────────┴───────────────────────┴───────────────────┘

  The four gpxtpx extension tags are each emitted only when a sample is found 
  within tolerance — so on a trackpoint where, say, HR is missing, that tag is
  simply omitted while position/time still render.

  A real enriched trackpoint (from the f4e23283… run):

  <trkpt lat="41.9143410" lon="-87.6682210">
    <ele>146.4</ele>
    <time>2025-05-11T10:56:26.192Z</time>
    <extensions>
      <gpxtpx:TrackPointExtension>
        <gpxtpx:hr>77</gpxtpx:hr>
        <gpxtpx:cad>150</gpxtpx:cad>
        <gpxtpx:atemp>22.9</gpxtpx:atemp>
        <gpxtpx:speed>0.00</gpxtpx:speed>
      </gpxtpx:TrackPointExtension>
    </extensions>
  </trkpt>

  What is not in the GPX (it lives only in the JSON/Markdown sidecars): the
  workout summary fields (calories, distance, intensity, label),
  motion/accelerometer data, ring battery, daily-summary scores
  (readiness/sleep/activity), workout-HR-session and activity-prediction
  records, and the raw GPS accuracy/course columns. Those don't have a standard
  GPX home, so they're reported alongside rather than embedded.

  Two of the embedded fields carry caveats worth repeating: cadence is computed
  from step counts (Oura has no true cadence sensor), and atemp is skin
  temperature that most tools will interpret as air temperature.
```

I tested it on a few workouts, and compared the resulting GPX file data to the native Oura data, and it matched up within reason (distance of 17.88 mi vs 17.71 mi, average speed of 14.4 mph vs 14.2 mph), certainly close enough for my purposes. Also note that the GPX file did upload to Strava without issue, including the map, distance, pace, speed, and heart rate data.

The one issue I encountered was that the GPX file for a cycling workout contained cadence data - which is not natively recorded by Oura. After bringing that issue to Claude's attention, it gated the cadence field for step-based workouts only (hiking, running, walking, etc.) to avoid incorrectly including cadence data.

I then asked Claude to create a new repo under my GitHub account, update the README, and push the changes to the repo, which can be found [here](https://github.com/jaredszajkowski/oura-data-analysis).

## Script versions

After using the script for a few weeks, I noticed the GPX tracks were inconsistent compared to the distance Oura itself reported, including roughly 10-15% short or long on distance, and 3-4x high on elevation gain. Rather than editing the script in place, I had Claude keep each iteration as a standalone file, so any change in output could be diffed against the version it replaced.

| Script | What it adds |
| --- | --- |
| `extract_session_create_gpx_v1.py` | The original. Emits every raw GPS fix as a trackpoint, in a single segment, with no cleanup. |
| `extract_session_create_gpx_v2_gap_adjusted.py` | Resamples the fixes onto a whole-second grid, and splits the track at app pauses and GPS dropouts instead of drawing a line across them. |
| `extract_session_create_gpx_v3_doppler_check.py` | Current. Drops bad fixes before resampling - re-emitted stale positions, and positions that contradict the receiver's own Doppler speed. |

Two separate problems drove those changes:

1. **`rawlocation.csv` logs faster than 1 Hz.** Fixes land at irregular sub-second offsets, and roughly 40% of seconds carry two of them a few hundred milliseconds apart. That pair is GPS jitter, not movement, so summing all of it is what inflates distance and elevation. Version 2 interpolates onto an exact whole-second grid, which is what Oura's own GPX export does.
2. **Some fixes are simply wrong.** The ring re-emits earlier positions out of order (on a couple of my rides, 47% of the fixes were stale repeats), and coming out of a GPS dropout the first fixes back are placed tens of meters behind the true position and then snap forward, charging several seconds of travel to a single step. Version 3 drops both before resampling, using the `speed` column as the arbiter, because it's Doppler-derived rather than computed by differencing positions, which makes it the only check on position that doesn't actually depend on the position data.

The difference is easiest to see at the top end. On a ride from 7/31/2026, max speed dropped from 28.3 mph to 22.1 mph (Strava reports 22.2 mph from Oura's own GPX file for that ride), and the worst single step went from 46 mph to 29 mph. I'd love to be riding 28.3 (or 46) mph, but it's not reality. :)

Version 3 is the one to use; passing `--no-doppler-filter` reproduces version 2's output if you want to compare.

## Creating the GPX file using the script

The README has complete instructions and other info, but here's a quick summary of the steps to create a GPX file from Oura data:

1. Clone the repo to your local machine.
2. Export your raw Oura data from the membership hub to `data`. In the `data` directory, you should see directories for `App Data` and `Subscriptions`.
3. Review the `workout.csv` file (located in the `App Data` directory) to find the workout ID of the workout you want to create a GPX file for.
4. Run the script with the workout ID of the workout you want to create a GPX file for:

   ```bash
   $ python src/extract_session_create_gpx_v3_doppler_check.py <workout_id>
   ```

5. Find the GPX file in the `sessions/<workout_id>` folder.

Note that the Oura data is only stored locally and not uploaded to GitHub for privacy reasons (see the `.gitignore` file).

## Conclusion

I'm certainly open to any feedback or suggestions for improvement, and I hope this is helpful to anyone else who may be in a similar situation.

## References

1. https://membership.ouraring.com/data-export
2. https://support.strava.com/en-us/articles/15402066-how-to-get-your-activities-to-strava
3. https://www.topografix.com/gpx.asp
4. [Claude session history](Extract_data_for_a_specific_workout.txt), which contains the full prompt and response history for creating the script (~1,300 lines)
