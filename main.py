import discord
from discord import app_commands
from discord.ext import commands
import random
import re
from database import Database
import os
from dotenv import load_dotenv

# Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
db = Database()

# Profile Commands
@bot.tree.command(name="create", description="Create a character profile")
@app_commands.describe(
    name="Character name",
    role="Character role (Killer or Survivor)"
)
@app_commands.choices(role=[
    app_commands.Choice(name="Killer", value="Killer"),
    app_commands.Choice(name="Survivor", value="Survivor")
])
async def create_profile(interaction: discord.Interaction, name: str, role: app_commands.Choice[str]):
    success, message = db.create_profile(name, role.value)
    if success:
        embed = discord.Embed(
            title="<a:check:1467157700831088773> ┃ Profile Created!",
            description=f"Successfully created profile for **{name}** as **{role.value}**!",
            color=discord.Color.from_rgb(0, 0, 0) 
        )
    else:
        embed = discord.Embed(
            title="<a:error:1467157734817398946> ┃ Error!",
            description=message,
            color=discord.Color.from_rgba(230, 1, 18)
        )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="editname", description="Edit a character's name")
@app_commands.describe(
    name="Current character name",
    new_name="New character name"
)
async def edit_profile_name(interaction: discord.Interaction, name: str, new_name: str):
    success, message = db.edit_profile_name(name, new_name)
    if success:
        embed = discord.Embed(
            title="<a:check:1467157700831088773> ┃ Name updated!",
            description=f"Successfully renamed **{name}** to **{new_name}**!",
            color=discord.Color.from_rgb(0, 0, 0) 
        )
    else:
        embed = discord.Embed(
            title="<a:error:1467157734817398946> ┃ Error!",
            description=message,
            color=discord.Color.from_rgba(230, 1, 18)
        )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="editrole", description="Edit a character's role")
@app_commands.describe(
    name="Character name",
    new_role="New role (Killer or Survivor)"
)
@app_commands.choices(new_role=[
    app_commands.Choice(name="Killer", value="Killer"),
    app_commands.Choice(name="Survivor", value="Survivor")
])
async def edit_profile_role(interaction: discord.Interaction, name: str, new_role: app_commands.Choice[str]):
    success, message = db.edit_profile_role(name, new_role.value)
    if success:
        embed = discord.Embed(
            title="<a:check:1467157700831088773> ┃ Role updated!",
            description=f"Successfully changed **{name}**'s role to **{new_role.value}**!",
            color=discord.Color.from_rgb(0, 0, 0) 
        )
    else:
        embed = discord.Embed(
            title="<a:error:1467157734817398946> ┃ Error!",
            description=message,
            color=discord.Color.from_rgba(230, 1, 18)
        )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="deleteprofile", description="Delete a character profile")
@app_commands.describe(name="Character name to delete")
async def delete_profile(interaction: discord.Interaction, name: str):
    success, message = db.delete_profile(name)
    if success:
        embed = discord.Embed(
            title="<a:check:1467157700831088773> ┃ Profile deleted!",
            description=f"Successfully deleted profile for **{name}**!",
            color=discord.Color.from_rgb(0, 0, 0) 
        )
    else:
        embed = discord.Embed(
            title="<a:error:1467157734817398946> ┃ Error!",
            description=message,
            color=discord.Color.from_rgba(230, 1, 18)
        )
    await interaction.response.send_message(embed=embed)

# Profile View with Pages
class ProfileView(discord.ui.View):
    def __init__(self, profile_data, inventory_data):
        super().__init__(timeout=180)
        self.profile_data = profile_data
        self.inventory_data = inventory_data
        self.current_page = 0
        
    @discord.ui.button(label="Main Info", style=discord.ButtonStyle.primary, custom_id="main_info")
    async def main_info_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 0
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Inventory", style=discord.ButtonStyle.secondary, custom_id="inventory")
    async def inventory_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 1
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    def create_embed(self):
        if self.current_page == 0:
            # Main Info Page
            embed = discord.Embed(
                title=f"─── ⋆⋅♱⋅⋆ {self.profile_data['name']}'s Profile ⋆⋅♱⋅⋆ ──",
                color=discord.Color.from_rgb(0, 0, 0) 
            )
            embed.add_field(name="‎", value="", inline=False)
            embed.add_field(name="── .✦ Role", value=self.profile_data['role'], inline=True)
            embed.add_field(name="‎", value="", inline=False)
            embed.add_field(name="── .✦ Bloodpoints", value=f"{self.profile_data['bloodpoints']:,}",\n embed.add_field(name="── .✦ Auric Cells", value=f"{self.profile_data['auric_cells']:,}", inline=True)
            embed.add_field(name="‎", value="", inline=False)
            return embed
        else:
            # Inventory Page with categories
            embed = discord.Embed(
                title=f"<:Dbdsurvivorinteractivesummary:1467161545661485139> {self.profile_data['name']}'s Inventory",
                color=discord.Color.from_rgb(0, 0, 0) 
            )
            
            # Check if inventory has any items
            total_items = 0
            unique_items = 0
            has_items = False
            
            for category, items in self.inventory_data.items():
                if items:
                    has_items = True
                    unique_items += len(items)
                    total_items += sum(item['quantity'] for item in items)
            
            if has_items:
                # Category emojis
                category_emojis = {
                    'Consumables': '💊',
                    'Tools': '🔧',
                    'Collectibles': '💎',
                    'Miscellaneous': '📦'
                }
                
                # Add each category as a field
                for category, items in self.inventory_data.items():
                    if items:  # Only show categories with items
                        emoji = category_emojis.get(category, '📦')
                        items_list = "\n".join([
                            f"**{item['item_name']}** × `{item['quantity']}`"
                            for item in items
                        ])
                        embed.add_field(
                            name=f"{emoji} {category}",
                            value=items_list,
                            inline=False
                        )
                
                # Add total count
                embed.set_footer(text=f"Total: {unique_items} unique items • {total_items} total items")
            else:
                embed.description = "*Inventory is empty*\n\nUse `/buy` to purchase items or play minigames to collect loot!"
            
            return embed

@bot.tree.command(name="profile", description="Show a character's profile")
@app_commands.describe(name="Character name")
async def show_profile(interaction: discord.Interaction, name: str):
    profile = db.get_profile(name)
    if profile:
        inventory = db.get_inventory(name)
        view = ProfileView(profile, inventory)
        embed = view.create_embed()
        await interaction.response.send_message(embed=embed, view=view)
    else:
        embed = discord.Embed(
            title="❌ Error",
            description=f"Profile **{name}** not found!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

# Currency Commands
@bot.tree.command(name="addcurrency", description="Add currency to a character")
@app_commands.describe(
    name="Character name",
    currency="Currency type",
    amount="Amount to add"
)
@app_commands.choices(currency=[
    app_commands.Choice(name="Bloodpoints", value="bloodpoints"),
    app_commands.Choice(name="Auric Cells", value="auric_cells")
])
async def add_currency(interaction: discord.Interaction, name: str, currency: app_commands.Choice[str], amount: int):
    if amount <= 0:
        embed = discord.Embed(
            title="❌ Error",
            description="Amount must be positive!",
            color=discord.Color.from_rgb(116, 7, 14)  # #74070E
        )
        await interaction.response.send_message(embed=embed)
        return
    
    success, message = db.add_currency(name, currency.value, amount)
    if success:
        currency_name = "Bloodpoints" if currency.value == "bloodpoints" else "Auric Cells"
        embed = discord.Embed(
            title="✅ Currency Added",
            description=f"Added **{amount:,}** {currency_name} to **{name}**!",
            color=discord.Color.from_rgb(69, 70, 42)  # #45462A (Add color)
        )
    else:
        embed = discord.Embed(
            title="❌ Error",
            description=message,
            color=discord.Color.from_rgb(116, 7, 14)  # #74070E
        )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="removecurrency", description="Remove currency from a character")
@app_commands.describe(
    name="Character name",
    currency="Currency type",
    amount="Amount to remove"
)
@app_commands.choices(currency=[
    app_commands.Choice(name="Bloodpoints", value="bloodpoints"),
    app_commands.Choice(name="Auric Cells", value="auric_cells")
])
async def remove_currency(interaction: discord.Interaction, name: str, currency: app_commands.Choice[str], amount: int):
    if amount <= 0:
        embed = discord.Embed(
            title="❌ Error",
            description="Amount must be positive!",
            color=discord.Color.from_rgb(116, 7, 14)  # #74070E
        )
        await interaction.response.send_message(embed=embed)
        return
    
    success, message = db.remove_currency(name, currency.value, amount)
    if success:
        currency_name = "Bloodpoints" if currency.value == "bloodpoints" else "Auric Cells"
        embed = discord.Embed(
            title="✅ Currency Removed",
            description=f"Removed **{amount:,}** {currency_name} from **{name}**!",
            color=discord.Color.from_rgb(116, 7, 14)  # #74070E
        )
    else:
        embed = discord.Embed(
            title="❌ Error",
            description=message,
            color=discord.Color.from_rgb(116, 7, 14)  # #74070E
        )
    await interaction.response.send_message(embed=embed)

# Inventory Commands
@bot.tree.command(name="additem", description="Add an item to a character's inventory")
@app_commands.describe(
    name="Character name",
    item_name="Item name"
)
async def add_item(interaction: discord.Interaction, name: str, item_name: str):
    success, message = db.add_item(name, item_name)
    if success:
        embed = discord.Embed(
            title="✅ Item Added",
            description=f"Added **{item_name}** to **{name}**'s inventory!",
            color=discord.Color.from_rgb(69, 70, 42)  # #45462A (Add color)
        )
    else:
        embed = discord.Embed(
            title="❌ Error",
            description=message,
            color=discord.Color.from_rgb(116, 7, 14)  # #74070E
        )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="removeitem", description="Remove an item from a character's inventory")
@app_commands.describe(
    name="Character name",
    item_name="Item name"
)
async def remove_item(interaction: discord.Interaction, name: str, item_name: str):
    success, message = db.remove_item(name, item_name)
    if success:
        embed = discord.Embed(
            title="✅ Item Removed",
            description=f"Removed **{item_name}** from **{name}**'s inventory!",
            color=discord.Color.from_rgb(116, 7, 14)  # #74070E
        )
    else:
        embed = discord.Embed(
            title="❌ Error",
            description=message,
            color=discord.Color.from_rgb(116, 7, 14)  # #74070E
        )
    await interaction.response.send_message(embed=embed)

# Shop Command
@bot.tree.command(name="buy", description="Buy an item from the shop")
@app_commands.describe(
    name="Character name",
    item_name="Item to buy"
)
async def buy_item(interaction: discord.Interaction, name: str, item_name: str):
    success, message, cost = db.buy_item(name, item_name)
    if success:
        embed = discord.Embed(
            title="✅ Purchase Successful",
            description=f"**{name}** bought **{item_name}** for **{cost:,}** Bloodpoints!",
            color=discord.Color.from_rgb(69, 70, 42)  # #45462A (Add color)
        )
    else:
        embed = discord.Embed(
            title="❌ Error",
            description=message,
            color=discord.Color.from_rgb(116, 7, 14)  # #74070E
        )
    await interaction.response.send_message(embed=embed)

# Trial System
@bot.tree.command(name="trial", description="Start a trial and earn rewards")
@app_commands.describe(name="Character name")
async def trial(interaction: discord.Interaction, name: str):
    result = db.complete_trial(name)
    if result:
        role = result['role']
        message = result['message']
        bloodpoints = result['bloodpoints']
        auric_cells = result['auric_cells']
        performance = result['performance']
        performance_text = result['performance_text']
        
        # Different colors for Killer vs Survivor
        if role == "Killer":
            color = discord.Color.from_rgb(117, 6, 8)  # #750608 (Dark Red)
            emoji = "🔪"
        else:
            color = discord.Color.from_rgb(116, 165, 190)  # #74A5BE (Light Blue)
            emoji = "🏃"
        
        embed = discord.Embed(
            title=f"{emoji} Trial Complete - {role}",
            description=message,
            color=color
        )
        
        # Add performance field
        embed.add_field(
            name="📊 Performance",
            value=f"**{performance_text}**",
            inline=False
        )
        
        # Add rewards field
        embed.add_field(
            name="💰 Rewards Earned", 
            value=f"🩸 **{bloodpoints:,}** Bloodpoints\n💎 **{auric_cells}** Auric Cells", 
            inline=False
        )
        
        embed.set_footer(text=f"{name} | Role: {role}")
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ Error",
            description=f"Profile **{name}** not found! Create one with `/create` first.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

# Dice Roll
@bot.tree.command(name="roll", description="Roll dice (e.g., 1d20, 2d6)")
@app_commands.describe(dice="Dice format (XdY)")
async def roll_dice(interaction: discord.Interaction, dice: str):
    try:
        pattern = r'(\d+)d(\d+)'
        match = re.match(pattern, dice.lower())
        
        if not match:
            raise ValueError("Invalid format")
        
        num_dice = int(match.group(1))
        num_sides = int(match.group(2))
        
        if num_dice > 100 or num_sides > 1000:
            raise ValueError("Too many dice or sides")
        
        rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
        total = sum(rolls)
        
        embed = discord.Embed(
            title=f"🎲 Rolling {dice}",
            color=discord.Color.from_rgb(116, 7, 14)  # #74070E
        )
        embed.add_field(name="Rolls", value=", ".join(map(str, rolls)), inline=False)
        embed.add_field(name="Total", value=f"**{total}**", inline=False)
        
        await interaction.response.send_message(embed=embed)
    except:
        embed = discord.Embed(
            title="❌ Error",
            description="Invalid dice format! Use format like: 1d20, 2d6, etc.",
            color=discord.Color.from_rgb(116, 7, 14)  # #74070E
        )
        await interaction.response.send_message(embed=embed)

# Choose Command
@bot.tree.command(name="choose", description="Choose a random option from a list")
@app_commands.describe(options="Options separated by commas")
async def choose_option(interaction: discord.Interaction, options: str):
    option_list = [opt.strip() for opt in options.split(',') if opt.strip()]
    
    if len(option_list) < 2:
        embed = discord.Embed(
            title="❌ Error",
            description="Please provide at least 2 options separated by commas!",
            color=discord.Color.from_rgb(116, 7, 14)  # #74070E
        )
        await interaction.response.send_message(embed=embed)
        return
    
    choice = random.choice(option_list)
    
    embed = discord.Embed(
        title="🎯 Random Choice",
        description=f"I choose: **{choice}**",
        color=discord.Color.from_rgb(116, 7, 14)  # #74070E
    )
    embed.add_field(name="Options", value=", ".join(option_list), inline=False)
    
    await interaction.response.send_message(embed=embed)

# Travel Command
@bot.tree.command(name="travel", description="Travel to a random realm")
@app_commands.describe(name="Character name")
async def travel(interaction: discord.Interaction, name: str):
    profile = db.get_profile(name)
    if not profile:
        embed = discord.Embed(
            title="❌ Error",
            description=f"Profile **{name}** not found!",
            color=discord.Color.from_rgb(116, 7, 14)  # #74070E
        )
        await interaction.response.send_message(embed=embed)
        return
    
    realm = db.get_random_realm()
    
    embed = discord.Embed(
        title="🌍 Travel",
        description=f"**{name}** has traveled to **{realm}**!",
        color=discord.Color.from_rgb(116, 7, 14)  # #74070E
    )
    
    await interaction.response.send_message(embed=embed)

# Hunting Minigame
@bot.tree.command(name="hunting", description="Go hunting for resources")
@app_commands.describe(name="Character name")
async def hunting(interaction: discord.Interaction, name: str):
    result = db.hunting_minigame(name)
    if result:
        embed = discord.Embed(
            title="🏹 Hunting",
            description=result['message'],
            color=discord.Color.from_rgb(0, 0, 0)  # Black (Minigame color)
        )
        if result['item']:
            embed.add_field(name="Found", value=f"**{result['item']}**", inline=False)
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ Error",
            description=f"Profile **{name}** not found!",
            color=discord.Color.from_rgb(116, 7, 14)  # #74070E
        )
        await interaction.response.send_message(embed=embed)

# Fishing Minigame
@bot.tree.command(name="fishing", description="Go fishing for resources")
@app_commands.describe(name="Character name")
async def fishing(interaction: discord.Interaction, name: str):
    result = db.fishing_minigame(name)
    if result:
        embed = discord.Embed(
            title="🎣 Fishing",
            description=result['message'],
            color=discord.Color.from_rgb(0, 0, 0)  # Black (Minigame color)
        )
        if result['item']:
            embed.add_field(name="Caught", value=f"**{result['item']}**", inline=False)
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ Error",
            description=f"Profile **{name}** not found!",
            color=discord.Color.from_rgb(116, 7, 14)  # #74070E
        )
        await interaction.response.send_message(embed=embed)

# Scavenging Minigame
@bot.tree.command(name="scavenging", description="Go scavenging for resources")
@app_commands.describe(name="Character name")
async def scavenging(interaction: discord.Interaction, name: str):
    result = db.scavenging_minigame(name)
    if result:
        embed = discord.Embed(
            title="🔍 Scavenging",
            description=result['message'],
            color=discord.Color.from_rgb(0, 0, 0)  # Black (Minigame color)
        )
        if result['item']:
            embed.add_field(name="Found", value=f"**{result['item']}**", inline=False)
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ Error",
            description=f"Profile **{name}** not found!",
            color=discord.Color.from_rgb(116, 7, 14)  # #74070E
        )
        await interaction.response.send_message(embed=embed)

# List Command
@bot.tree.command(name="list", description="Show all your character profiles")
async def list_profiles(interaction: discord.Interaction):
    # Get all profiles (you might want to filter by user ID in future)
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, role, bloodpoints, auric_cells FROM profiles ORDER BY name")
    profiles = cursor.fetchall()
    conn.close()
    
    if profiles:
        embed = discord.Embed(
            title="📋 All Character Profiles",
            description=f"Total characters: **{len(profiles)}**",
            color=discord.Color.from_rgb(116, 7, 14)  # #74070E
        )
        
        # Group by role
        killers = [p for p in profiles if p[1] == 'Killer']
        survivors = [p for p in profiles if p[1] == 'Survivor']
        
        if killers:
            killer_list = "\n".join([
                f"🔪 **{p[0]}** • 🩸 {p[2]:,} BP • 💎 {p[3]} AC"
                for p in killers
            ])
            embed.add_field(name="Killers", value=killer_list, inline=False)
        
        if survivors:
            survivor_list = "\n".join([
                f"🏃 **{p[0]}** • 🩸 {p[2]:,} BP • 💎 {p[3]} AC"
                for p in survivors
            ])
            embed.add_field(name="Survivors", value=survivor_list, inline=False)
        
        embed.set_footer(text="Use /profile [name] to view detailed information")
    else:
        embed = discord.Embed(
            title="📋 All Character Profiles",
            description="No profiles found. Create one with `/create`!",
            color=discord.Color.from_rgb(116, 7, 14)  # #74070E
        )
    
    await interaction.response.send_message(embed=embed)

# Help Command
@bot.tree.command(name="help", description="Show all available commands")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📚 Bot Commands Help",
        description="Here are all available commands for the Dead by Daylight Bot:",
        color=discord.Color.from_rgb(116, 7, 14)  # #74070E
    )
    
    # Profile Management
    embed.add_field(
        name="👤 Profile Management",
        value=(
            "`/create [name] [role]` - Create a new character profile\n"
            "`/profile [name]` - View character profile and inventory\n"
            "`/list` - Show all your character profiles\n"
            "`/editname [name] [new_name]` - Change character name\n"
            "`/editrole [name] [new_role]` - Change character role\n"
            "`/deleteprofile [name]` - Delete a character profile"
        ),
        inline=False
    )
    
    # Currency
    embed.add_field(
        name="💰 Currency",
        value=(
            "`/addcurrency [name] [currency] [amount]` - Add Bloodpoints or Auric Cells\n"
            "`/removecurrency [name] [currency] [amount]` - Remove currency"
        ),
        inline=False
    )
    
    # Inventory & Shop
    embed.add_field(
        name="🎒 Inventory & Shop",
        value=(
            "`/buy [name] [item]` - Buy item from shop with Bloodpoints\n"
            "`/additem [name] [item]` - Add item to inventory\n"
            "`/removeitem [name] [item]` - Remove item from inventory"
        ),
        inline=False
    )
    
    # Gameplay
    embed.add_field(
        name="🎮 Gameplay",
        value=(
            "`/trial [name]` - Complete a trial and earn rewards\n"
            "`/hunting [name]` - Go hunting for resources\n"
            "`/fishing [name]` - Go fishing for resources\n"
            "`/scavenging [name]` - Go scavenging for resources\n"
            "`/travel [name]` - Travel to a random realm"
        ),
        inline=False
    )
    
    # Utility
    embed.add_field(
        name="🎲 Utility",
        value=(
            "`/roll [dice]` - Roll dice (e.g., 1d20, 2d6)\n"
            "`/choose [options]` - Pick random option from comma-separated list"
        ),
        inline=False
    )
    
    embed.set_footer(text="💡 Tip: Use /profile to see your inventory organized by categories!")
    
    await interaction.response.send_message(embed=embed)
    
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# Run the bot
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

if not TOKEN:
    print("ERROR: Discord Token not found! Check .env file")
else:
    bot.run(TOKEN)
