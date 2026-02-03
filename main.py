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
        
    @discord.ui.button(label="Main Info", style=discord.ButtonStyle.danger, custom_id="main_info")
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
                color=discord.Color.from_rgb(0, 0, 0) 
            )
            # Profile Name
            embed.add_field(
                name=f"<:15824redneonstar:1467170916017639615> ┃ **{self.profile_data['name']}**'s Profile", 
                value="", 
                inline=False
            )
            # Role
            embed.add_field(
                name=".✦ Role:", 
                value=self.profile_data['role'], 
                inline=True
            )
            
            # Currency
            currency_text = (
                f"<:bp:1467159740797681716> {self.profile_data['bloodpoints']:,} bp\n"
                f"<:ac:1467159725870154021> {self.profile_data['auric_cells']:,} ac"
            )
            embed.add_field(
                name=".✦ Currency:", 
                value=currency_text, 
                inline=True
            )
            return embed
            
        else:
            # Inventory Page with categories (NO EMOJIS)
            embed = discord.Embed(
                title=f"<:15824redneonstar:1467170916017639615> ┃ **{self.profile_data['name']}**'s Inventory",
                color=discord.Color.from_rgb(0, 0, 0) 
            )
            
            # Check if inventory has any items
            total_items = 0
            has_items = False
            
            for category, items in self.inventory_data.items():
                if items:
                    has_items = True
                    total_items += sum(item['quantity'] for item in items)
            
            if has_items:
                # Add each category as a field (NO EMOJIS)
                for category, items in self.inventory_data.items():
                    if items:  # Only show categories with items
                        items_list = "\n".join([
                            f"{item['item_name']} ― `{item['quantity']}`"
                            for item in items
                        ])
                        embed.add_field(
                            name=f"·········•✦ {category}",  # No emoji prefix
                            value=items_list,
                            inline=False
                        )
                
                # Add total count (removed unique items)
                embed.set_footer(text=f"Total: {total_items} items")
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
            title="<a:error:1467157734817398946> ┃ Error!",
            description=f"Profile **{name}** not found!",
            color=discord.Color.from_rgb(116, 7, 14)  # #74070E
        )
        await interaction.response.send_message(embed=embed)

# Currency Commands
@bot.tree.command(name="addcurrency", description="Add Bloodpoints or Auric Cells to a character")
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
    success, message = db.add_currency(name, currency.value, amount)
    if success:
        embed = discord.Embed(
            title="<a:check:1467157700831088773> ┃ Currency added!",
            description=f"Added **{amount:,}** {currency.name} to **{name}**!",
            color=discord.Color.from_rgb(0, 0, 0)
        )
    else:
        embed = discord.Embed(
            title="<a:error:1467157734817398946> ┃ Error!",
            description=message,
            color=discord.Color.from_rgba(230, 1, 18)
        )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="removecurrency", description="Remove Bloodpoints or Auric Cells from a character")
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
    success, message = db.remove_currency(name, currency.value, amount)
    if success:
        embed = discord.Embed(
            title="<a:check:1467157700831088773> ┃ Currency removed!",
            description=f"Removed **{amount:,}** {currency.name} from **{name}**!",
            color=discord.Color.from_rgb(0, 0, 0)
        )
    else:
        embed = discord.Embed(
            title="<a:error:1467157734817398946> ┃ Error!",
            description=message,
            color=discord.Color.from_rgba(230, 1, 18)
        )
    await interaction.response.send_message(embed=embed)

# Shop Command (NO EMOJIS)
@bot.tree.command(name="shop", description="View available items for purchase")
async def shop(interaction: discord.Interaction):
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT item_name, price, description, currency_type FROM shop_items ORDER BY price")
    items = cursor.fetchall()
    conn.close()
    
    if items:
        embed = discord.Embed(
            title="Shop",  # No emoji
            description="Purchase items with `/buy [name] [item]`",
            color=discord.Color.from_rgb(0, 0, 0)
        )
        
        items_text = []
        for item in items:
            item_name = item[0]
            price = item[1]
            description = item[2]
            # Handle currency_type (might be NULL or not exist in old databases)
            currency_type = item[3] if len(item) > 3 and item[3] else 'bloodpoints'
            
            # Determine currency abbreviation
            if currency_type == 'auric_cells':
                currency_abbr = "AC"
            else:
                currency_abbr = "BP"
            
            items_text.append(f"**{item_name}** - {price:,} {currency_abbr}\n*{description}*")
        
        embed.add_field(
            name="Available Items",  # No emoji
            value="\n".join(items_text),
            inline=False
        )
    else:
        embed = discord.Embed(
            title="Shop",  # No emoji
            description="No items available.",
            color=discord.Color.from_rgb(0, 0, 0)
        )
    
    await interaction.response.send_message(embed=embed)

# Buy Command
@bot.tree.command(name="buy", description="Purchase an item from the shop")
@app_commands.describe(
    name="Character name",
    item="Item name"
)
async def buy_item(interaction: discord.Interaction, name: str, item: str):
    success, message, price, currency_type = db.buy_item(name, item)
    
    if success:
        # Determine currency display
        if currency_type == 'auric_cells':
            currency_name = "Auric Cells"
            currency_abbr = "AC"
        else:
            currency_name = "Bloodpoints"
            currency_abbr = "BP"
        
        embed = discord.Embed(
            title="<a:check:1467157700831088773> ┃ Purchase successful!",
            description=f"**{name}** purchased **{item}** for **{price:,}** {currency_name}!",
            color=discord.Color.from_rgb(0, 0, 0)
        )
    else:
        embed = discord.Embed(
            title="<a:error:1467157734817398946> ┃ Error!",
            description=message,
            color=discord.Color.from_rgb(116, 7, 14)
        )
    
    await interaction.response.send_message(embed=embed)

# Inventory Management
@bot.tree.command(name="additem", description="Add an item to a character's inventory")
@app_commands.describe(
    name="Character name",
    item="Item name"
)
async def add_item(interaction: discord.Interaction, name: str, item: str):
    success, message = db.add_item(name, item)
    if success:
        embed = discord.Embed(
            title="<a:check:1467157700831088773> ┃ Item added!",
            description=f"Added **{item}** to **{name}**'s inventory!",
            color=discord.Color.from_rgb(0, 0, 0)
        )
    else:
        embed = discord.Embed(
            title="<a:error:1467157734817398946> ┃ Error!",
            description=message,
            color=discord.Color.from_rgba(230, 1, 18)
        )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="removeitem", description="Remove an item from a character's inventory")
@app_commands.describe(
    name="Character name",
    item="Item name"
)
async def remove_item(interaction: discord.Interaction, name: str, item: str):
    success, message = db.remove_item(name, item)
    if success:
        embed = discord.Embed(
            title="<a:check:1467157700831088773> ┃ Item removed!",
            description=f"Removed **{item}** from **{name}**'s inventory!",
            color=discord.Color.from_rgb(0, 0, 0)
        )
    else:
        embed = discord.Embed(
            title="<a:error:1467157734817398946> ┃ Error!",
            description=message,
            color=discord.Color.from_rgba(230, 1, 18)
        )
    await interaction.response.send_message(embed=embed)

#  Command
@bot.tree.command(name="trial", description="Complete a trial and earn rewards")
@app_commands.describe(name="Character name")
async def trial(interaction: discord.Interaction, name: str):
    result = db.complete_trial(name)
    if result:
        embed = discord.Embed(
            title=f"<a:loading:1467153150015180800> ┃ {result['role']} Trial",
            description=result['message'],
            color=discord.Color.from_rgb(116, 7, 14)  # #74070E
        )
        embed.add_field(
            name="Result:",
            value=result['performance_text'],
            inline=True
        )
        embed.add_field(
            name="Rewards",
            value=f"<:bp:1467159740797681716> **{result['bloodpoints']:,}** Bloodpoints\n<:ac:1467159725870154021> **{result['auric_cells']}** Auric Cells",
            inline=True
        )
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="<a:error:1467157734817398946> ┃ Error!",
            description=f"Profile **{name}** not found!",
            color=discord.Color.from_rgb(116, 7, 14)  # #74070E
        )
        await interaction.response.send_message(embed=embed)

# Dice Roll Command
@bot.tree.command(name="roll", description="Roll dice (e.g., 1d20, 2d6)")
@app_commands.describe(dice="Dice notation (e.g., 1d20, 2d6+5)")
async def roll_dice(interaction: discord.Interaction, dice: str):
    try:
        # Parse dice notation (e.g., "2d6+3")
        match = re.match(r'(\d+)d(\d+)([+-]\d+)?', dice.lower())
        if not match:
            await interaction.response.send_message("Invalid dice format! Use format like: 1d20, 2d6, or 1d20+5")
            return
        
        num_dice = int(match.group(1))
        num_sides = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0
        
        if num_dice > 100 or num_sides > 1000:
            await interaction.response.send_message("Too many dice or sides! Keep it reasonable.")
            return
        
        # Roll the dice
        rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
        total = sum(rolls) + modifier
        
        # Format the result
        rolls_str = ", ".join(map(str, rolls))
        modifier_str = f" {modifier:+d}" if modifier != 0 else ""
        
        embed = discord.Embed(
            title="<a:40586diceroll:1467250239181295657> ┃ Roll",
            description=f"Rolling **{dice}**",
            color=discord.Color.from_rgb(0, 0, 0)
        )
        embed.add_field(name="You rolled:", value=rolls_str, inline=False)
        
        # Only show total if rolling multiple dice OR if there's a modifier
        if num_dice > 1 or modifier != 0:
            embed.add_field(name="Total:", value=f"**{total}**{modifier_str}", inline=False)
        
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"Error rolling dice: {str(e)}")

# Choose Command
@bot.tree.command(name="choose", description="Pick a random option from a list")
@app_commands.describe(options="Comma-separated list of options")
async def choose(interaction: discord.Interaction, options: str):
    choices = [choice.strip() for choice in options.split(',') if choice.strip()]
    
    if len(choices) < 2:
        await interaction.response.send_message("Please provide at least 2 options separated by commas!")
        return
    
    chosen = random.choice(choices)
    
    embed = discord.Embed(
        title="<:IconAddon_bloodiedWater:1468241349856722944> ┃ Random Choice",
        description=f"I choose: **{chosen}**",
        color=discord.Color.from_rgb(0, 0, 0)
    )
    embed.set_footer(text=f"Options: {', '.join(choices)}")
    
    await interaction.response.send_message(embed=embed)

# Travel Command
@bot.tree.command(name="travel", description="Travel to a random realm")
@app_commands.describe(name="Character name")
async def travel(interaction: discord.Interaction, name: str):
    profile = db.get_profile(name)
    if not profile:
        embed = discord.Embed(
            title="<a:error:1467157734817398946> ┃ Error!",
            description=f"Profile **{name}** not found!",
            color=discord.Color.from_rgb(116, 7, 14)  # #74070E
        )
        await interaction.response.send_message(embed=embed)
        return
    
    realm = db.get_random_realm()
    
    embed = discord.Embed(
        title="<:IconSkills_ScoutInnate:1468241348594503791> ┃ Travel",
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
            title="<:DailyRitualIcon_hunter:1467234763495571477> ┃ Hunting",
            description=result.get('description', result['message']),
            color=discord.Color.from_rgb(0, 0, 0)  # Black (Minigame color)
        )
        if result['item']:
            embed.add_field(name="You found:", value=f"**{result['item']}**", inline=False)
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="<a:error:1467157734817398946> ┃ Error!",
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
            title="<:DailyRitualIcon_sacrifice:1467234766053970055> ┃ Fishing",
            description=result.get('description', result['message']),
            color=discord.Color.from_rgb(0, 0, 0)  # Black (Minigame color)
        )
        if result['item']:
            embed.add_field(name="You caught:", value=f"**{result['item']}**", inline=False)
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="<a:error:1467157734817398946> ┃ Error!",
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
            title="<:DailyRitualIcon_objectives:1467234764795809842> ┃ Scavenging",
            description=result.get('description', result['message']),
            color=discord.Color.from_rgb(0, 0, 0)  # Black (Minigame color)
        )
        if result['item']:
            embed.add_field(name="You found:", value=f"**{result['item']}**", inline=False)
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="<a:error:1467157734817398946> ┃ Error!",
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
            title="<:15824redneonstar:1467170916017639615> ┃ Character Profiles",
            description=f"Total characters: **{len(profiles)}**",
            color=discord.Color.from_rgb(116, 7, 14)  # #74070E
        )
        
        # Group by role
        killers = [p for p in profiles if p[1] == 'Killer']
        survivors = [p for p in profiles if p[1] == 'Survivor']
        
        if killers:
            killer_list = "\n".join([
                f"<:killer:1467160220009762837> **{p[0]}**"
                for p in killers
            ])
            embed.add_field(name="Killers", value=killer_list, inline=False)
        
        if survivors:
            survivor_list = "\n".join([
                f"<:survivor:1467160220982841345> **{p[0]}**"
                for p in survivors
            ])
            embed.add_field(name="Survivors", value=survivor_list, inline=False)
        
        embed.set_footer(text="Use /profile [name] to view detailed information.")
    else:
        embed = discord.Embed(
            title="<:15824redneonstar:1467170916017639615> ┃ Character Profiles",
            description="No profiles found. Create one with `/create`!",
            color=discord.Color.from_rgb(116, 7, 14)  # #74070E
        )
    
    await interaction.response.send_message(embed=embed)

# Help Command
@bot.tree.command(name="help", description="Show all available commands")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="<:15824redneonstar:1467170916017639615> ┃ Bot Commands Help",
        description="Here are all available commands for the bot:",
        color=discord.Color.from_rgb(116, 7, 14)  # #74070E
    )
    
    # Profile Management
    embed.add_field(
        name=".✦  Profile Management",
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
        name=".✦  Currency",
        value=(
            "`/addcurrency [name] [currency] [amount]` - Add Bloodpoints or Auric Cells\n"
            "`/removecurrency [name] [currency] [amount]` - Remove currency"
        ),
        inline=False
    )
    
    # Inventory & Shop
    embed.add_field(
        name=".✦  Inventory & Shop",
        value=(
            "`/buy [name] [item]` - Buy item from shop with Bloodpoints\n"
            "`/additem [name] [item]` - Add item to inventory\n"
            "`/removeitem [name] [item]` - Remove item from inventory"
        ),
        inline=False
    )
    
    # Gameplay
    embed.add_field(
        name=".✦  Gameplay",
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
        name=".✦  Utility",
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
