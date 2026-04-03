import re
import json

with open('context/rain_tracker_spec.html', 'r', encoding='utf-8') as f:
    spec_html = f.read()

# Extract tasks
tasks = []
task_cards = re.findall(r'<div class="task-card">.*?</div>\s*</div>', spec_html, re.DOTALL)
for card in task_cards:
    num_m = re.search(r'<span class="task-num">#(.*?)</span>', card)
    svg_m = re.search(r'(<svg.*?</svg>)', card, re.DOTALL)
    title_m = re.search(r'<div class="task-title">(.*?)</div>', card)
    text_m = re.search(r'<div class="task-text">(.*?)</div>', card)
    
    if num_m and svg_m and title_m and text_m:
        tasks.append({
            'id': int(num_m.group(1)),
            'svg': svg_m.group(1),
            'title': title_m.group(1),
            'text': text_m.group(1)
        })

index_html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Люблю грозу в начале мая</title>
    <link rel="manifest" href="manifest.json">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Caveat:wght@400;600;700&display=swap');
        
        * {{ box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }}
        
        body {{
            font-family: 'Caveat', cursive;
            background: #F5F0E8;
            color: #1a1a1a;
            min-height: 100svh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
        }}

        .wrap {{
            max-width: 780px;
            margin: 0 auto;
            padding: 24px 16px;
            width: 100%;
        }}

        h1 {{
            font-size: 32px;
            font-weight: 700;
            text-align: center;
            margin-bottom: 24px;
        }}

        .divider {{
            border: none;
            border-top: 2px solid #1a1a1a;
            margin: 16px 0 24px;
        }}

        /* Screen 1: Welcome */
        #screen-welcome {{
            text-align: center;
            display: flex;
            flex-direction: column;
            gap: 24px;
            align-items: center;
            justify-content: center;
            flex: 1;
        }}

        .mode-btn {{
            background: #fff;
            border: 2px solid #1a1a1a;
            border-radius: 12px;
            padding: 16px 32px;
            font-family: 'Caveat', cursive;
            font-size: 24px;
            font-weight: 700;
            cursor: pointer;
            width: 200px;
            margin: 8px;
            transition: transform 0.1s;
        }}
        .mode-btn:active {{
            transform: scale(0.95);
        }}
        .mode-btn.yellow {{ background: #FFD54F; }}
        .mode-btn.blue {{ background: #90CAF9; }}
        .mode-btn.red {{ background: #EF9A9A; }}

        /* Screen 2: Tracker */
        #screen-tracker {{
            display: none;
        }}

        .progress-header {{
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 24px;
            gap: 8px;
        }}
        .progress-drop {{
            color: #90CAF9;
        }}

        .task-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
            gap: 16px;
        }}

        .task-card {{
            background: #fff;
            border: 2px solid #1a1a1a;
            border-radius: 12px;
            padding: 16px 12px;
            display: flex;
            flex-direction: column;
            align-items: center;
            cursor: pointer;
            position: relative;
            user-select: none;
            text-align: center;
            transition: transform 0.1s;
        }}
        .task-card:active {{
            transform: scale(0.98);
        }}
        .task-icon {{
            width: 60px;
            height: 60px;
            margin-bottom: 12px;
        }}
        .task-title {{
            font-size: 18px;
            font-weight: 600;
            line-height: 1.2;
        }}

        .task-card.completed .task-icon,
        .task-card.completed .task-title {{
            opacity: 0.5;
        }}
        .task-card.completed::after {{
            content: '';
            position: absolute;
            top: 50%;
            left: 10%;
            width: 80%;
            height: 3px;
            background: #1a1a1a;
            transform: translateY(-50%) rotate(-10deg);
            pointer-events: none;
        }}

        /* Modal Screen */
        #modal-overlay {{
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(26, 26, 26, 0.8);
            display: none;
            justify-content: center;
            align-items: center;
            padding: 24px;
            z-index: 100;
            opacity: 0;
            transition: opacity 0.2s;
        }}
        #modal-overlay.active {{
            display: flex;
            opacity: 1;
        }}

        .modal-card {{
            background: #F5F0E8;
            border: 3px solid #1a1a1a;
            border-radius: 16px;
            padding: 32px 24px;
            max-width: 320px;
            width: 100%;
            text-align: center;
            position: relative;
        }}
        .modal-close {{
            position: absolute;
            top: 8px; right: 12px;
            font-size: 32px;
            cursor: pointer;
            font-weight: bold;
        }}
        .modal-icon {{
            width: 100px;
            height: 100px;
            margin: 0 auto 16px;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            cursor: pointer;
        }}
        .modal-title {{
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 12px;
        }}
        .modal-text {{
            font-size: 18px;
            line-height: 1.4;
        }}
        .modal-hint {{
            font-size: 14px;
            color: #666;
            margin-top: 24px;
        }}

        .hidden {{ display: none !important; }}
    </style>
</head>
<body>

<div class="wrap">
    <!-- Screen 1 -->
    <div id="screen-welcome">
        <h1 id="welcome-title">🌧 Люблю грозу в начале мая</h1>
        <p style="font-size: 20px; color: #555;">Выбери количество дождливых заданий</p>
        <div style="display:flex; flex-direction:column; gap:12px; margin-top:24px;">
            <button class="mode-btn yellow" onclick="startApp(12)">12 заданий</button>
            <button class="mode-btn blue" onclick="startApp(22)">22 задания</button>
            <button class="mode-btn red" onclick="startApp(30)">30 заданий</button>
        </div>
    </div>

    <!-- Screen 2 -->
    <div id="screen-tracker">
        <h1 id="reset-trigger">🌧 Люблю грозу в начале мая</h1>
        <hr class="divider">
        <div class="progress-header">
            Выполнено <span id="progress-val">0</span> из <span id="progress-total">12</span> <span class="progress-drop">💧</span>
        </div>
        <div class="task-grid" id="task-grid"></div>
    </div>
</div>

<div id="modal-overlay">
    <div class="modal-card">
        <div class="modal-close" onclick="closeModal()">×</div>
        <div class="modal-icon" id="modal-icon" onclick="completeFromModal()"></div>
        <div class="modal-title" id="modal-title"></div>
        <div class="modal-text" id="modal-text"></div>
        <div class="modal-hint">коснись рисунка — отметить выполненным</div>
    </div>
</div>

<script>
    const allTasks = {json.dumps(tasks)};
    let state = {{ mode: null, completed: [], startedAt: null }};
    let currentModalId = null;
    let pressTimer;

    // Load State
    const saved = localStorage.getItem('rainTracker');
    if (saved) {{
        try {{
            state = JSON.parse(saved);
        }} catch(e) {{}}
    }}

    if (state.mode) {{
        renderTracker();
    }}

    function startApp(mode) {{
        state = {{
            mode: mode,
            completed: [],
            startedAt: new Date().toISOString()
        }};
        saveState();
        renderTracker();
    }}

    function saveState() {{
        localStorage.setItem('rainTracker', JSON.stringify(state));
    }}

    function renderTracker() {{
        document.getElementById('screen-welcome').style.display = 'none';
        document.getElementById('screen-tracker').style.display = 'block';
        
        document.getElementById('progress-total').textContent = state.mode;
        updateProgress();

        const grid = document.getElementById('task-grid');
        grid.innerHTML = '';
        
        const tasksToShow = allTasks.slice(0, state.mode);
        tasksToShow.forEach(task => {{
            const card = document.createElement('div');
            card.className = 'task-card' + (state.completed.includes(task.id) ? ' completed' : '');
            card.dataset.id = task.id;
            
            card.innerHTML = `
                <div class="task-icon">${{task.svg}}</div>
                <div class="task-title">${{task.title}}</div>
            `;

            // Touch events for tap vs hold
            let isHolding = false;
            let touchMoved = false;

            const startHold = (e) => {{
                touchMoved = false;
                isHolding = true;
                pressTimer = setTimeout(() => {{
                    if (isHolding && !touchMoved) {{
                        openModal(task.id);
                        isHolding = false; // Prevent tap event
                    }}
                }}, 500);
            }};

            const endHold = (e) => {{
                clearTimeout(pressTimer);
                if (isHolding && !touchMoved) {{
                    toggleTask(task.id);
                }}
                isHolding = false;
            }};
            
            const moveHold = () => {{ touchMoved = true; }};

            // Touch
            card.addEventListener('touchstart', startHold, {{passive: true}});
            card.addEventListener('touchend', (e) => {{ e.preventDefault(); endHold(e); }});
            card.addEventListener('touchmove', moveHold, {{passive: true}});
            card.addEventListener('touchcancel', () => {{ clearTimeout(pressTimer); isHolding = false; }});

            // Mouse (for desktop testing)
            card.addEventListener('mousedown', startHold);
            card.addEventListener('mouseup', (e) => {{ if(e.button === 0) endHold(e); }});
            card.addEventListener('mousemove', moveHold);
            card.addEventListener('mouseleave', () => {{ clearTimeout(pressTimer); isHolding = false; }});

            grid.appendChild(card);
        }});
    }}

    function toggleTask(id) {{
        const idx = state.completed.indexOf(id);
        if (idx > -1) {{
            state.completed.splice(idx, 1);
        }} else {{
            state.completed.push(id);
        }}
        saveState();
        renderTracker();
    }}

    function updateProgress() {{
        document.getElementById('progress-val').textContent = state.completed.length;
    }}

    function openModal(id) {{
        const task = allTasks.find(t => t.id === id);
        if (!task) return;
        currentModalId = id;
        document.getElementById('modal-icon').innerHTML = task.svg;
        document.getElementById('modal-title').textContent = task.title;
        document.getElementById('modal-text').textContent = task.text;
        
        const overlay = document.getElementById('modal-overlay');
        overlay.classList.add('active');
    }}

    function closeModal() {{
        document.getElementById('modal-overlay').classList.remove('active');
        currentModalId = null;
    }}

    function completeFromModal() {{
        if (currentModalId && !state.completed.includes(currentModalId)) {{
            state.completed.push(currentModalId);
            saveState();
            renderTracker();
        }}
        closeModal();
    }}

    document.getElementById('modal-overlay').addEventListener('click', (e) => {{
        if(e.target.id === 'modal-overlay') closeModal();
    }});

    // Reset progress by 5 fast taps on title
    let resetTaps = 0;
    let resetTimer;
    document.getElementById('reset-trigger').addEventListener('click', () => {{
        resetTaps++;
        clearTimeout(resetTimer);
        if (resetTaps >= 5) {{
            if(confirm('Сбросить весь прогресс?')) {{
                localStorage.removeItem('rainTracker');
                location.reload();
            }}
            resetTaps = 0;
        }} else {{
            resetTimer = setTimeout(() => resetTaps = 0, 1000);
        }}
    }});

    // PWA Service Worker Registration
    if ('serviceWorker' in navigator) {{
        window.addEventListener('load', () => {{
            navigator.serviceWorker.register('./sw.js')
                .then(r => console.log('SW registered'))
                .catch(e => console.error('SW err', e));
        }});
    }}
</script>
</body>
</html>
"""

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(index_html)

manifest_json = """{
  "name": "Дождь",
  "short_name": "Дождь",
  "icons": [
    {
      "src": "icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ],
  "start_url": "./index.html",
  "display": "standalone",
  "background_color": "#F5F0E8",
  "theme_color": "#1A1A1A"
}"""
with open('manifest.json', 'w', encoding='utf-8') as f:
    f.write(manifest_json)

sw_js = """
const CACHE_NAME = 'rain-tracker-v1';
const urlsToCache = [
  './',
  './index.html',
  './manifest.json',
  'https://fonts.googleapis.com/css2?family=Caveat:wght@400;600;700&display=swap'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
"""

with open('sw.js', 'w', encoding='utf-8') as f:
    f.write(sw_js)

print(f"Generated {len(tasks)} tasks.")
