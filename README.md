# Jio STB Auto-Updating IPTV Master Playlist

An automated, self-healing, zero-maintenance live IPTV playlist engine for the **Jio Set-Top Box (JMSB200A / Android TV)** and **OwnTV / TiviMate**.

This repository runs automatically in the cloud via **GitHub Actions** every 6 hours to fetch, probe, filter, and synchronize live IPTV streams.

---

## 📺 How to Use in OwnTV (On Your Jio STB)

Once this repository is on your GitHub account, your playlist will be permanently available at:

```text
https://raw.githubusercontent.com/<YOUR_GITHUB_USERNAME>/<REPO_NAME>/main/playlist.m3u
```

### Steps to Set Up on Your TV:
1. Turn on your **Jio Set-Top Box** and open **OwnTV**.
2. Press **Left** on your remote to open the side menu → select **Settings** (Gear icon).
3. Navigate to **Sources & guide** → **Playlists**.
4. Select your existing playlist (or click **Add playlist** → **M3U playlist**):
   - **Type**: `M3U Playlist`
   - **Playlist URL**: Enter your GitHub raw URL (e.g. `https://raw.githubusercontent.com/username/jio-live-playlist/main/playlist.m3u`)
   - **Playlist name**: `Jio Master TV`
5. Go to **Auto-update**:
   - Change from *Disabled* to **At app start** or **Every 12 hours**.
6. Click **Save / Apply**.

**That's it!** OwnTV will now silently download and refresh the working channels automatically without ever needing your PC to be on.

---

## ⚡ How It Works (Cloud Architecture)

* **Multi-Threaded Live Stream Health Probing**:
  - Pulls candidate feeds from [aria-tv/aria](https://github.com/aria-tv/aria).
  - Probes streams concurrently using 30 threads in ~20 seconds.
  - Drops broken streams, placeholder clips (`channeldead.mp4`), and dead CDNs.
* **Content Filtering**:
  - Keeps Hindi Entertainment/Movies/News, Sports, Kids, and British channels (BBC Three, BBC Four, Sky Atlantic, Discovery UK, STV, Great! TV/Movies, U&Eden).
  - Removes unwanted foreign/regional channels and teleshopping.
* **JioTV Go Integration**:
  - Bundles the local `http://127.0.0.1:5350/...` channel links. Because OwnTV runs directly on the STB, `127.0.0.1` resolves to the local JioTV Go server on the STB.
* **Runs Continuously (Continuous Active Commits)**:
  - Updates channel states and logs automatically on schedule, keeping repository activity active without third-party dependencies.
