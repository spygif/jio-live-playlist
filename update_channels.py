import re
import urllib.request
import urllib.error
import ssl
import subprocess
import time
import os
import sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set console encoding to UTF-8
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(SCRIPT_DIR, "update_channels.log")
STB_DEFAULT_IPS = ["192.168.1.8", "192.168.1.18"]
STB_PORT = "5555"
MASTER_M3U_PATH = os.path.join(SCRIPT_DIR, "playlist.m3u")
STB_DEST_PATH = "/sdcard/Download/playlist.m3u"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*'
}

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{ts}] {msg}"
    print(formatted)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as lf:
            lf.write(formatted + "\n")
    except Exception:
        pass

# 1. Devotional / Religious Blacklist
DEVOTIONAL_KEYWORDS = [
    'aastha', 'sanskar', 'sadhna', 'bhakti', 'darshan', 'divya', 'chintpurni',
    'ishwar', 'paras gold', 'peace of mind', 'shubh', 'shubhsandesh', 'zb bhakti',
    'aadinath', 'aaseervatham', 'adhyatm', 'amrit', 'anandpur', 'angel tv', 'aradana',
    'awakening', 'bhagyam', 'calvary', 'dharshan', 'fateh tv', 'goodness tv', 'grace tv',
    'hare krsna', 'harvest tv', 'hindu dharmam', 'hope channel', 'hosanna', 'lord',
    'jinvani', 'katyayani', 'kaumudy', 'kripalu', 'mahuaa bhaktii', 'mandir', 'mh 1 shraddha',
    'munsif', 'namah', 'navgrh', 'paras tv', 'paul tv', 'prarthana', 'prasanna',
    'quran', 'rohi', 'saadhna', 'sadgurukrupa', 'sadguru', 'salvation', 'santvani', 'satsang',
    'shalom', 'shirdi', 'shree sankat', 'soham', 'sparsh', 'subhavaartha', 'vedic', 'vr live',
    'vaanavil', 'valam', 'vissa', 'vyas nic', 'daystar', 'madha tv', 'mahotsav tv', 'mangalmay',
    'mei alai', 'mercy tv', 'nambikkai', 'nanaksar', 'nireekshana', 'om tv', 'powervision',
    'svbc', 'sadvidya', 'sai tv', 'sairam', 'salaam tv', 'sana plus', 'sana tv', 'sankara',
    'sarv dharm', 'sharnam', 'shekinah', 'shree hazur', 'shree sanatan', 'sindh tv', 'swastik tv',
    'tehzeeb tv', 'the voice tv', 'mh one shraddha', 'alankar tv', 'anand tv', 'disha tv',
    'fgn channel', 'joy tv', 'subin tv', 'astroscience', 'channel win', 'sathiyam', 'goodnews',
    'shiksha tv', 'sada tv', 'medibiztv', 'life tv', 'ttn24', 'tv30 india', 'gangaur tv', 'prime news',
    'islam', 'prophet', 'bible', 'church', 'mandir', 'masjid', 'gurbani', 'kirtan', 'bhajan',
    'yesu', 'god stands', 'llbn', 'kanshi tv', 'akaal', 'dukh nivaran', 'sikh', 'jewish life',
    'hope channel', 'mission tv', 'lifevisiontv'
]

# 2. Regional Language & Foreign Blacklist (Zero non-Hindi/English)
REGIONAL_KEYWORDS = [
    'telugu', 'tamil', 'malayalam', 'kannada', 'etv', 'star maa', 'vanitha',
    'mojo tv', 'big tv', 'tv5 news', 'inews', 'ashwaveega', 'vcv', 'dheeran', 'peppers tv',
    'raj digital', 'raj tv', 'vijay takkar', 'suriya', 'suriyan', 'm nadu', 'madhimugam',
    'malai murasu', 'puthuyugam', 'tamilan', 'wow kidz tamil', 'tunes 6', 'village tv',
    'media one', 'kerala', 'pulari', 'pravasi', 'kappa tv', '7s music', 'public movies',
    'public music', 'news 1st', 'power tv', 'south station', 'mk six', 'studio one +',
    'bangla', 'bengal', 'kolkata', 'aakaash aath', 'ctvn', 'rongeen', 'taaza tv',
    'rang', 'spondon', 'zillarbarta', 'dhoom music', 'punjab', 'punjabi', 'balle balle',
    'pitaara', 'rozana', 'spokesman', 'hamdard', 'tabbar', 'mh 1', 'living india',
    'daily post', 'desi channel', '7x music', 'channel y', 'marathi', 'majha', 'saam tv',
    'pudhari', 'lokshahi', 'soneri cinema', 'gujarat', 'gujarati', 'mantavya', 'gs tv',
    'odisha', 'odia', 'argus', 'nandighosha', 'mbc tv', 'nk tv', 'northeast', 'ne news',
    'rengoni', 'hornbill', 'tripura', 'mizoram', 'arun prabha', 'dd goa', 'nepal',
    'urdu', 'kashmiri', 'koshur', 'manipur', 'nagaland', 'bihar', 'bhojpuri', 'jharkhand',
    'kashish', '22scope', 'b4u bhojpuri', 'zee biskope', 'dabangg', 'big ganga',
    'galavision', 'aliento', 'lbc international', 'spanish', 'espanol', 'español',
    'telemundo', 'univision', 'universo', 'unimas', 'unimás', 'rtve', 'telefe',
    'azteca', 'multimedios', 'caracol', 'rcn', 'persian', 'arabic', 'comedia',
    'cazarrecompensas', 'estrellas', 'reino infantil', 'novelas'
]

def parse_m3u(content):
    channels = []
    lines = content.splitlines()
    header = ""
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTM3U'):
            header = line
            i += 1
            continue
        if line.startswith('#EXTINF'):
            extinf = line
            i += 1
            ext_lines = []
            while i < len(lines) and not lines[i].strip().startswith('#EXTINF'):
                if lines[i].strip():
                    ext_lines.append(lines[i].strip())
                i += 1
            url = ""
            for s in ext_lines:
                if s.startswith(('http://', 'https://')):
                    url = s
                    break
            
            name_m = re.search(r',([^,]+)$', extinf)
            name = name_m.group(1).strip() if name_m else ''
            
            grp_m = re.search(r'group-title="([^"]*)"', extinf)
            grp = grp_m.group(1).strip() if grp_m else 'General'
            
            logo_m = re.search(r'tvg-logo="([^"]*)"', extinf)
            logo = logo_m.group(1).strip() if logo_m else ''
            
            id_m = re.search(r'tvg-id="([^"]*)"', extinf)
            tid = id_m.group(1).strip() if id_m else ''

            if url:
                channels.append({
                    'name': name,
                    'group': grp,
                    'logo': logo,
                    'tvg_id': tid,
                    'url': url,
                    'extinf': extinf,
                    'ext_lines': ext_lines
                })
        else:
            i += 1
    return header, channels

def norm(text):
    return re.sub(r'[^a-z0-9]', '', text.lower())

def is_rejected(name, grp, url):
    u = url.lower()
    if 'channeldead.mp4' in u or not u.startswith(('http://', 'https://')):
        return True, "Dead stream placeholder"
    
    text = f"{name} {grp}".lower()
    for kw in DEVOTIONAL_KEYWORDS:
        if kw in text:
            return True, f"Devotional: {kw}"
    for kw in REGIONAL_KEYWORDS:
        if kw in text:
            return True, f"Regional/Foreign: {kw}"
    return False, ""

def probe_stream(url, timeout=4):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            body = r.read(256)
            if r.status in [200, 206] and len(body) > 0:
                if b'channeldead' not in body:
                    return True, f"HTTP {r.status}"
            return False, f"Status {r.status}"
    except Exception as e:
        return False, str(e)

def fetch_url(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
        return r.read().decode('utf-8', errors='ignore')

def main():
    log("=" * 65)
    log("  Jio STB Master Playlist Auto-Updater (India + UK + US Lineup)")
    log("=" * 65)
    
    # 1. Load Existing Master Playlist
    if not os.path.exists(MASTER_M3U_PATH):
        log(f"[!] Error: Master playlist not found at {MASTER_M3U_PATH}")
        return
    
    with open(MASTER_M3U_PATH, 'r', encoding='utf-8', errors='ignore') as f:
        master_raw = f.read()
    
    m_header, master_channels = parse_m3u(master_raw)
    log(f"[*] Loaded current master playlist: {len(master_channels)} channels")
    
    # 2. Fetch Latest Aria M3U
    log("[*] Fetching latest updates from aria-tv/aria on GitHub...")
    aria_sources = [
        'https://raw.githubusercontent.com/aria-tv/aria/main/aria+.m3u',
        'https://raw.githubusercontent.com/aria-tv/aria/main/aria.m3u'
    ]
    
    aria_raw_channels = []
    for src in aria_sources:
        try:
            content = fetch_url(src)
            _, chs = parse_m3u(content)
            log(f"    + Fetched {len(chs)} channels from {src.split('/')[-1]}")
            aria_raw_channels.extend(chs)
        except Exception as e:
            log(f"    [!] Failed to fetch {src}: {e}")
            
    # 3. Filter Target Aria Channels (India, UK, US)
    candidate_aria = []
    seen_urls = set()
    for ch in aria_raw_channels:
        u = ch['url']
        if u in seen_urls:
            continue
        seen_urls.add(u)
        
        g = ch['group']
        n = ch['name']
        g_lower = g.lower()
        n_lower = n.lower()
        
        is_target = any(k in g_lower for k in ['india', 'united kingdom', 'united states', '🇬🇧', '🇮🇳', '🇺🇸']) or \
                    bool(re.search(r'\b(uk|bbc|sky|tnt|cbs|nbc|abc|fox|hbo)\b', n_lower))
        
        if not is_target:
            continue
            
        rejected, reason = is_rejected(n, g, u)
        if rejected:
            continue
            
        candidate_aria.append(ch)
        
    log(f"[*] Filtered candidate channels from Aria: {len(candidate_aria)}")
    
    # 4. Concurrently Probe Candidate Streams
    log("[*] Probing candidate streams live (concurrent health check)...")
    working_aria = []
    
    def probe_wrapper(ch):
        ok, msg = probe_stream(ch['url'])
        return ch, ok, msg

    with ThreadPoolExecutor(max_workers=30) as executor:
        futs = [executor.submit(probe_wrapper, ch) for ch in candidate_aria]
        for f in as_completed(futs):
            ch, ok, msg = f.result()
            if ok:
                working_aria.append(ch)
                
    log(f"[*] Verified working Aria channels: {len(working_aria)}")
    
    # 5. Smart Merge with Master Playlist
    aria_map = {norm(c['name']): c for c in working_aria}
    updated_channels = []
    updated_count = 0
    
    for ch in master_channels:
        nm = norm(ch['name'])
        
        # Don't overwrite local JioTV server links
        if '127.0.0.1:5350' not in ch['url']:
            if nm in aria_map:
                new_ch = aria_map[nm]
                if ch['url'] != new_ch['url']:
                    ch['url'] = new_ch['url']
                    ch['ext_lines'] = [new_ch['url']]
                    if new_ch.get('logo'):
                        ch['logo'] = new_ch['logo']
                    updated_count += 1
                    
        updated_channels.append(ch)
        
    log(f"[*] Channels refreshed with newer live URLs: {updated_count}")
    log(f"[*] Total channels in master playlist: {len(updated_channels)}")
    
    # 6. Rebuild Playlist
    out_lines = [m_header if m_header else '#EXTM3U']
    for ch in updated_channels:
        logo_part = f' tvg-logo="{ch["logo"]}"' if ch.get("logo") else ''
        id_part = f' tvg-id="{ch["tvg_id"]}"' if ch.get("tvg_id") else f' tvg-id="{ch["name"]}"'
        extinf = f'#EXTINF:-1{id_part} tvg-name="{ch["name"]}"{logo_part} group-title="{ch["group"]}",{ch["name"]}'
        out_lines.append(extinf)
        for s in ch['ext_lines']:
            if s.startswith(('http://', 'https://')):
                out_lines.append(s)
                break
        else:
            out_lines.append(ch['url'])
            
    final_content = '\n'.join(out_lines) + '\n'
    
    with open(MASTER_M3U_PATH, 'w', encoding='utf-8') as f:
        f.write(final_content)
    log(f"[✓] Saved updated master playlist to {MASTER_M3U_PATH}")
    
    # Also mirror to 05_Uncategorized_Misc
    misc_path = r"E:\Downloads\05_Uncategorized_Misc\playlist.m3u"
    try:
        if os.path.exists(os.path.dirname(misc_path)):
            with open(misc_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
    except Exception:
        pass
    
    # 7. Deliver Playlist
    is_android_local = os.path.exists('/sdcard') and os.path.exists('/system/build.prop')
    is_cloud_mode = '--cloud' in sys.argv or '--no-adb' in sys.argv
    is_local_mode = '--local' in sys.argv or is_android_local

    if is_cloud_mode:
        log("[✓] Cloud mode: Master playlist saved to repository. Ready for remote streaming.")
        log("=" * 65)
        log("  Update Complete! Master playlist is fully synchronized.")
        log("=" * 65)
        return

    if is_local_mode:
        log("[*] Detected on-device execution (running directly on STB).")
        try:
            with open(STB_DEST_PATH, 'w', encoding='utf-8') as f:
                f.write(final_content)
            log(f"[✓] Directly wrote fresh playlist to STB storage: {STB_DEST_PATH}")
        except Exception as e:
            log(f"[!] Error writing directly to {STB_DEST_PATH}: {e}")
        log("=" * 65)
        log("  Update Complete! Master playlist is fully synchronized.")
        log("=" * 65)
        return

    # Push to Jio STB via ADB (from PC)
    adb_tool = os.path.join(SCRIPT_DIR, "adb", "adb.exe")
    if not os.path.exists(adb_tool):
        adb_tool = "adb"

    target_device = None
    # Check if a device is already attached
    try:
        dev_res = subprocess.run([adb_tool, "devices"], capture_output=True, text=True, timeout=5)
        for line in dev_res.stdout.splitlines():
            line = line.strip()
            if line and not line.startswith("List of") and "\tdevice" in line:
                target_device = line.split("\t")[0]
                log(f"[*] Found actively connected ADB target: {target_device}")
                break
    except Exception:
        pass

    # If no active device, check CLI argument or probe candidate IPs
    if not target_device:
        candidate_ips = []
        if len(sys.argv) > 1 and sys.argv[1].strip():
            candidate_ips.append(sys.argv[1].strip())
        candidate_ips.extend(STB_DEFAULT_IPS)

        for ip in candidate_ips:
            endpoint = f"{ip}:{STB_PORT}" if ":" not in ip else ip
            log(f"[*] Attempting ADB connection to {endpoint}...")
            try:
                conn_res = subprocess.run([adb_tool, "connect", endpoint], capture_output=True, text=True, timeout=6)
                if "connected" in conn_res.stdout.lower() and "cannot" not in conn_res.stdout.lower():
                    target_device = endpoint
                    log(f"[✓] Connected successfully to {endpoint}")
                    break
            except Exception:
                pass

    if target_device:
        try:
            log(f"[*] Pushing playlist to STB ({target_device}): {STB_DEST_PATH}...")
            push_res = subprocess.run([adb_tool, "-s", target_device, "push", MASTER_M3U_PATH, STB_DEST_PATH], capture_output=True, text=True, timeout=12)
            log(f"    Push Result: {push_res.stdout.strip()}")
            log("[✓] Successfully updated STB with fresh channels!")
        except Exception as e:
            log(f"[!] ADB push error: {e}")
    else:
        log("[i] STB is currently offline or sleeping. The local master playlist was updated and will sync on next connection.")
        
    log("=" * 65)
    log("  Update Complete! Master playlist is fully synchronized.")
    log("=" * 65)

if __name__ == '__main__':
    main()
