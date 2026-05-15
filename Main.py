from flask import Flask, render_template_string, request, jsonify
import discord
from discord.ext import commands
import asyncio
import threading
import time
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

bot = None
is_logged_in = False
PREFIX = "+"
bot_loop = asyncio.new_event_loop()

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Feather Selfbot V1.3</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body { background: #0a0a0c; color: white; font-family: system-ui; }
    .glass { background: rgba(15,15,20,0.95); backdrop-filter: blur(20px); }
    .shiny { background: linear-gradient(90deg, #ddd, #fff, #ddd); -webkit-background-clip: text; background-clip: text; color: transparent; animation: shine 3s linear infinite; }
    @keyframes shine { 0% { background-position: 200%; } 100% { background-position: -200%; } }
    .glow { text-shadow: 0 0 25px #22ff88, 0 0 50px #22ff88; }
  </style>
</head>
<body class="min-h-screen flex items-center justify-center p-4">
  <div class="max-w-md w-full">

    <!-- Login Screen -->
    <div id="login" class="glass rounded-3xl p-8 border border-white/20">
      <h1 class="text-5xl font-bold text-center shiny mb-1">Feather</h1>
      <p class="text-center text-zinc-400 text-xl mb-8">Selfbot V1.3</p>
      
      <input type="password" id="token" 
             class="w-full bg-zinc-900 border border-white/30 rounded-2xl px-6 py-4 text-center mb-6 focus:outline-none focus:border-emerald-400"
             placeholder="Enter Discord Token">

      <button onclick="deploy()" id="deployBtn"
              class="w-full bg-white text-black font-bold py-4 rounded-2xl text-lg hover:scale-105 transition">
        DEPLOY SELFBOT
      </button>

      <div class="mt-6 text-center text-xs text-zinc-500">
        Prefix: <span class="text-white">+</span>
      </div>
    </div>

    <!-- Success Screen -->
    <div id="success" class="hidden glass rounded-3xl p-10 border border-emerald-500/30 text-center">
      <div class="text-7xl mb-6">🔑</div>
      <h1 class="text-4xl font-bold glow text-emerald-400 mb-2">Congratulations</h1>
      <h2 class="text-3xl font-semibold mb-8">Welcome To Feather</h2>
      
      <div class="bg-zinc-900/80 border border-emerald-500/20 rounded-2xl p-6 mb-8 space-y-4">
        <p class="text-white text-lg">Your Prefix is <span class="text-emerald-400 font-bold">+</span></p>
        <p class="text-zinc-400">Check On a Safe Server</p>
      </div>

      <button onclick="logout()" 
              class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-medium py-4 rounded-2xl transition">
        Logout & Restart
      </button>
    </div>
  </div>

  <script>
    async function deploy() {
      const token = document.getElementById('token').value.trim();
      if (!token) return alert("Please enter your Discord Token");

      const btn = document.getElementById('deployBtn');
      btn.innerHTML = "DEPLOYING...";
      btn.disabled = true;

      try {
        const res = await fetch('/api/validate_token', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({token})
        });
        const data = await res.json();

        if (data.success) {
          document.getElementById('login').classList.add('hidden');
          document.getElementById('success').classList.remove('hidden');
        } else {
          alert(data.message || "Invalid Token");
          btn.innerHTML = "DEPLOY SELFBOT";
          btn.disabled = false;
        }
      } catch(e) {
        alert("Server Error - Check Render Logs");
        btn.innerHTML = "DEPLOY SELFBOT";
        btn.disabled = false;
      }
    }

    function logout() {
      location.reload();
    }
  </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/api/validate_token', methods=['POST'])
def validate_token():
    global bot, is_logged_in

    if is_logged_in:
        return jsonify({"success": True})

    data = request.get_json()
    token = data.get('token')

    if not token:
        return jsonify({"success": False, "message": "Token required"}), 400

    def run_bot():
        global bot, is_logged_in
        try:
            asyncio.set_event_loop(bot_loop)
            intents = discord.Intents.all()
            bot = commands.Bot(command_prefix=PREFIX, self_bot=True, intents=intents, help_command=None)

            @bot.event
            async def on_ready():
                nonlocal is_logged_in
                is_logged_in = True
                print(f"✅ Feather Selfbot Logged In As → {bot.user}")

            @bot.command()
            async def help(ctx):
                await ctx.send("**Feather Selfbot V1.3 is Online**\nUse +menu for commands")

            bot_loop.run_until_complete(bot.start(token))
        except discord.LoginFailure:
            print("❌ Invalid Token")
        except Exception as e:
            print(f"Bot Error: {e}")

    threading.Thread(target=run_bot, daemon=True).start()
    time.sleep(6)

    return jsonify({"success": is_logged_in, "message": "Logged in" if is_logged_in else "Login failed"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    print("🚀 Feather Selfbot V1.3 Starting...")
    app.run(host="0.0.0.0", port=port)
