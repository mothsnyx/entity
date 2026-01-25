# The Entity
# 🎮 Dead by Daylight Discord Bot

A Discord bot with RPG elements based on Dead by Daylight, including a web dashboard for management.

## 📋 Features

### Discord Bot
- ✅ **Character Profiles** - Killer and Survivor roles
- ✅ **Currency System** - Bloodpoints & Auric Cells
- ✅ **Inventory System** - Collect and manage items
- ✅ **Shop System** - Buy items with Bloodpoints
- ✅ **Trial System** - Earn rewards through trials
- ✅ **Mini-Games** - Hunting, Fishing, Scavenging
- ✅ **Utility Commands** - Dice rolls, random choice, travel

### Web Dashboard
- 🌐 **Manage Realms** - Locations for travel command
- 🛒 **Shop Items** - Adjust prices and descriptions
- 🏆 **Trial Messages** - Configure Killer/Survivor messages
- 🎣 **Minigame Loot** - Items for Hunting/Fishing/Scavenging
- 👥 **Profile Overview** - View all created characters
- 🔐 **Login System** - Password-protected access

## 🚀 Installation

### Prerequisites
- Raspberry Pi (3/4/5) or other Linux server
- Python 3.8+
- Discord Bot Token ([Guide](https://discord.com/developers/applications))

### Quick Setup

```bash
# Clone repository
git clone https://github.com/YOUR-USERNAME/entity.git
cd cosmos

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
nano .env  # Insert token

# Start bot
python main.py

# Start dashboard (in new terminal)
python dashboard_secure.py
```

## ⚙️ Configuration

### Discord Bot Token

1. Create `.env` file:
```env
DISCORD_TOKEN=your-bot-token-here
DASHBOARD_SECRET=your-secure-random-key
```

2. **IMPORTANT:** `.env` is in `.gitignore` and will NOT be uploaded!

### Dashboard Password

Edit `dashboard_secure.py`:
```python
users = {
    "admin": generate_password_hash("YOUR-PASSWORD-HERE"),
}
```

## 📱 Discord Commands

### Profile Management
- `/create [name] [role]` - Create profile (Role: Killer or Survivor)
- `/editname [name] [new_name]` - Change name
- `/editrole [name] [new_role]` - Change role
- `/deleteprofile [name]` - Delete profile
- `/profile [name]` - View profile

### Currency
- `/addcurrency [name] [currency] [amount]` - Add currency (Bloodpoints/Auric Cells)
- `/removecurrency [name] [currency] [amount]` - Remove currency

### Inventory & Shop
- `/additem [name] [item]` - Add item
- `/removeitem [name] [item]` - Remove item
- `/buy [name] [item]` - Buy item

### Gameplay
- `/trial [name]` - Complete trial (Earn rewards!)
- `/hunting [name]` - Go hunting
- `/fishing [name]` - Go fishing
- `/scavenging [name]` - Go scavenging
- `/travel [name]` - Travel to random realm

### Utility
- `/roll [dice]` - Roll dice (e.g. 1d20, 2d6)
- `/choose [options]` - Random choice (comma separated)

## 🌐 Dashboard

### Access

**Local:**
```
http://localhost:5000
```

**On Network:**
```
http://RASPBERRY-PI-IP:5000
```

### Default Login
- Username: `admin`
- Password: (see `dashboard_secure.py`)

## 🔧 Systemd Services (Optional)

For automatic startup on boot:

```bash
# Setup services
sudo cp systemd/discord-bot.service /etc/systemd/system/
sudo cp systemd/discord-dashboard.service /etc/systemd/system/

# Enable services
sudo systemctl enable discord-bot
sudo systemctl enable discord-dashboard

# Start services
sudo systemctl start discord-bot
sudo systemctl start discord-dashboard
```

## 💾 Backup

### Automatic Backup

```bash
# Make backup script executable
chmod +x backup-bot.sh

# Setup cronjob (daily at 3 AM)
crontab -e
# Add: 0 3 * * * /path/to/backup-bot.sh
```

### Manual Backup

```bash
cp game_database.db game_database_backup_$(date +%Y%m%d).db
```

## 🗄️ Database

- **Engine:** SQLite
- **File:** `game_database.db`
- **Capacity:** Up to 1000+ users easily
- **ACID-compliant:** Data preserved during power outages

### Reset Database

```bash
# WARNING: Deletes all data!
rm game_database.db
python main.py  # Creates new empty DB
```

## 📊 Technology Stack

- **Bot:** Discord.py 2.3+
- **Web Framework:** Flask 3.0+
- **Database:** SQLite3
- **Auth:** Flask-HTTPAuth
- **Frontend:** Bootstrap 5 + Bootstrap Icons

## 🔒 Security

### Important Notes

- ⚠️ **NEVER** push Discord token!
- ⚠️ **NEVER** commit passwords in code!
- ✅ `.env` is in `.gitignore` → safe
- ✅ Dashboard has login protection
- ✅ Passwords are hashed

### .gitignore Entries

```gitignore
.env
*.db
__pycache__/
venv/
*.pyc
```

## 🐛 Troubleshooting

### Bot won't start
```bash
# Check logs
python main.py
# Check .env token
```

### Commands don't appear
- Wait 1 hour (Discord sync)
- Or use guild-specific commands (see code comments)

### Dashboard not accessible
```bash
# Check if port 5000 is free
sudo netstat -tulpn | grep 5000

# Allow port in firewall
sudo ufw allow 5000
```

## 📈 Performance

### Tested for:
- ✅ 1-50 users: Perfect
- ✅ 50-100 users: Very good
- ✅ 100-500 users: Good
- ⚠️ 500+ users: PostgreSQL migration recommended

### Resources (Raspberry Pi 4)
- **RAM:** ~100-200 MB
- **CPU:** < 5% idle
- **Disk:** ~50 MB + database (~1 MB per 100 users)

## 🤝 Contributing

As this is a private project:
- Fork the repo
- Create feature branch
- Commit your changes
- Push and create pull request

## 📝 License

Private project - All rights reserved.

Dead by Daylight™ is a trademark of Behaviour Interactive Inc.

## 🆘 Support

If you have issues:
1. Check logs: `sudo journalctl -u discord-bot -f`
2. Verify `.env` configuration
3. See Troubleshooting section above

## 📚 Documentation

Additional guides:
- [Raspberry Pi Setup](docs/raspberry-pi-setup.md)
- [Dashboard Guide](docs/dashboard-guide.md)
- [Performance Guide](docs/performance-guide.md)

## ✨ Credits

Created with ❤️ for the DBD community

---

**Version:** 1.0.0  
**Last Update:** January 2026
