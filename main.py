import discord
from discord import app_commands
from discord.ext import commands
import random
import re
from database import Database
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import threading

# Bot Setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Required to detect member joins!
intents.guilds = True  # Required for guild information
intents.guild_reactions = True  # Required for reaction events!
bot = commands.Bot(command_prefix="!", intents=intents)
db = Database()

# Flask API for dashboard communication
api = Flask(__name__)

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
            color=discord.Color.from_rgb(0, 0, 0)
        )
        
        # Show result first - big and prominent
        if num_dice > 1 or modifier != 0:
            embed.add_field(name="Result:", value=f"**{total}**", inline=False)
            # Show details below in small text - using lowercase d
            embed.add_field(name="", value=f"-# Rolling {dice.lower()}\n-# Rolls: {rolls_str}{modifier_str}", inline=False)
        else:
            # Single die, no modifier - just show the result
            embed.add_field(name="Result:", value=f"**{rolls[0]}**", inline=False)
            embed.add_field(name="", value=f"-# Rolling {dice.lower()}", inline=False)
        
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"Error rolling dice: {str(e)}")

# Prefix command version of roll (works with Tupperbot!)
@bot.command(name="roll", aliases=["r"])
async def roll_prefix(ctx, *, dice: str):
    """Roll dice using prefix command with optional text (e.g., !roll [1d20], !roll Attack [1d20+5])"""
    try:
        # Extract all dice rolls in brackets [1d20], [2d6+5], etc.
        dice_pattern = r'\[(\d+d\d+(?:[+-]\d+)?)\]'
        matches = re.findall(dice_pattern, dice.lower())
        
        if not matches:
            await ctx.send("No dice found! Use brackets like: `!roll [1d20]` or `!roll Attack [1d20+5]`")
            return
        
        # Keep the original text for display
        display_text = dice
        
        embed = discord.Embed(
            title="<a:40586diceroll:1467250239181295657> ┃ Roll",
            color=discord.Color.from_rgb(0, 0, 0)
        )
        
        # Roll each dice expression found
        for dice_expr in matches:
            # Parse dice notation (e.g., "2d6+3")
            match = re.match(r'(\d+)d(\d+)([+-]\d+)?', dice_expr)
            if not match:
                continue
            
            num_dice = int(match.group(1))
            num_sides = int(match.group(2))
            modifier = int(match.group(3)) if match.group(3) else 0
            
            if num_dice > 100 or num_sides > 1000:
                await ctx.send("Too many dice or sides! Keep it reasonable.")
                return
            
            # Roll the dice
            rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
            total = sum(rolls) + modifier
            
            # Format the result
            rolls_str = ", ".join(map(str, rolls))
            modifier_str = f" {modifier:+d}" if modifier != 0 else ""
            
            # Replace the bracketed dice with the result in display text
            result_str = f"**{total}**" if (num_dice > 1 or modifier != 0) else f"**{rolls[0]}**"
            display_text = display_text.replace(f"[{dice_expr}]", result_str, 1)
            
            # Add result field - big and prominent
            field_name = f"-# Rolling: {dice_expr.upper()}"
            if num_dice > 1 or modifier != 0:
                field_value = f"-# Rolls: {rolls_str}{modifier_str}"
            else:
                field_value = f"-# {rolls[0]}"
            
            embed.add_field(name=field_name, value=field_value, inline=False)
        
        # Set description to show the text with results
        embed.description = display_text
        
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Error rolling dice: {str(e)}")


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
        title="🎯 ┃ Random Choice",
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
        title="🌍 ┃ Travel",
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
    
# Test Welcome Command
@bot.tree.command(name="testwelcome", description="Test the welcome message system")
async def test_welcome(interaction: discord.Interaction):
    """Manually trigger a welcome message to test it"""
    print(f"[TEST] Testing welcome message triggered by {interaction.user.name}")
    await interaction.response.send_message("Testing welcome message...", ephemeral=True)
    
    # Trigger the welcome event with the command user
    await on_member_join(interaction.user)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.event
async def on_member_join(member):
    """Send welcome message when a new member joins"""
    print(f"[WELCOME] Member joined: {member.name} (ID: {member.id})")
    try:
        # Get welcome settings
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT enabled, embed_id, channel_id FROM welcome_settings WHERE id = 1")
        settings = cursor.fetchone()
        
        print(f"[WELCOME] Settings: {settings}")
        
        if not settings:
            print("[WELCOME] No settings found in database!")
            conn.close()
            return
            
        if not settings[0]:  # Not enabled
            print("[WELCOME] Welcome messages are disabled!")
            conn.close()
            return
        
        embed_id = settings[1]
        channel_id = settings[2]
        
        print(f"[WELCOME] Embed ID: {embed_id}, Channel ID: {channel_id}")
        
        if not embed_id or not channel_id:
            print("[WELCOME] Missing embed_id or channel_id!")
            conn.close()
            return
        
        # Get embed data
        cursor.execute("SELECT title, description, color, footer_text, image_url, thumbnail_url FROM embeds WHERE id = ?", (embed_id,))
        embed_data = cursor.fetchone()
        conn.close()
        
        print(f"[WELCOME] Embed data: {embed_data}")
        
        if not embed_data:
            print("[WELCOME] No embed found with that ID!")
            return
        
        # Replace variables in embed
        def replace_vars(text):
            if not text:
                return text
            replacements = {
                '{user}': member.name,
                '{mention}': member.mention,
                '{member_count}': str(member.guild.member_count),
                '{server}': member.guild.name,
                '{user_tag}': str(member),
                '{user_id}': str(member.id)
            }
            for key, value in replacements.items():
                text = text.replace(key, value)
            return text
        
        # Create embed with replaced variables
        title = replace_vars(embed_data[0])
        description = replace_vars(embed_data[1])
        footer = replace_vars(embed_data[3])
        
        print(f"[WELCOME] Original title: {embed_data[0]}")
        print(f"[WELCOME] Replaced title: {title}")
        print(f"[WELCOME] Original footer: {embed_data[3]}")
        print(f"[WELCOME] Replaced footer: {footer}")
        
        embed = discord.Embed(
            title=title,
            description=description,
            color=int(embed_data[2] or '000000', 16)
        )
        
        if footer:
            embed.set_footer(text=footer)
        if embed_data[4]:
            embed.set_image(url=embed_data[4])
        if embed_data[5]:
            embed.set_thumbnail(url=embed_data[5])
        
        # Send to welcome channel
        channel = bot.get_channel(int(channel_id))
        print(f"[WELCOME] Channel object: {channel}")
        
        if channel:
            message = await channel.send(embed=embed)
            print(f"[WELCOME] ✅ Sent welcome message! Message ID: {message.id}")
        else:
            print(f"[WELCOME] ❌ Channel not found! ID: {channel_id}")
    except Exception as e:
        print(f"[WELCOME] ❌ Error: {e}")
        import traceback
        traceback.print_exc()

@bot.event
async def on_message(message):
    """Automatically detect and roll dice in brackets [1d20]"""
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Process commands first (important!)
    await bot.process_commands(message)
    
    # Check if message contains dice in brackets
    dice_pattern = r'\[(\d+d\d+(?:[+-]\d+)?)\]'
    matches = re.findall(dice_pattern, message.content.lower())
    
    # ONLY process webhook messages (Tupperbot messages)
    # Skip messages that start with ! (commands)
    if matches and not message.content.startswith('!'):
        # ONLY process if it's a webhook message (the actual Tupper character message)
        is_webhook = message.webhook_id is not None
        
        if not is_webhook:
            # Skip non-webhook messages (these are your trigger messages like "sk:[1d20]")
            return
            
        try:
            # Keep the original text for display
            display_text = message.content
            
            # Get the author info (webhook name and avatar)
            author_name = message.author.name
            
            # Get avatar - for webhooks, the avatar is in the author object
            # Webhooks show up as User objects with their avatar embedded
            author_avatar = message.author.default_avatar.url  # Start with default
            
            # Try to get the actual avatar
            try:
                if message.author.avatar:
                    # This works for webhook messages - avatar is a property
                    author_avatar = message.author.avatar.url
                elif message.author.display_avatar:
                    author_avatar = message.author.display_avatar.url
            except Exception as e:
                print(f"[AUTO ROLL] Avatar fetch warning: {e}")
                # Keep the default avatar as fallback
            
            embed = discord.Embed(
                color=discord.Color.from_rgb(0, 0, 0)
            )
            
            # Set author to show the character name and avatar
            embed.set_author(name=author_name, icon_url=author_avatar)
            
            # Store roll results to reuse them
            roll_results = []
            
            # Roll each dice expression found
            for dice_expr in matches:
                # Parse dice notation (e.g., "2d6+3")
                match = re.match(r'(\d+)d(\d+)([+-]\d+)?', dice_expr)
                if not match:
                    continue
                
                num_dice = int(match.group(1))
                num_sides = int(match.group(2))
                modifier = int(match.group(3)) if match.group(3) else 0
                
                if num_dice > 100 or num_sides > 1000:
                    continue  # Skip unreasonable dice
                
                # Roll the dice
                rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
                total = sum(rolls) + modifier
                
                # Store the results
                roll_results.append({
                    'dice_expr': dice_expr,
                    'num_dice': num_dice,
                    'num_sides': num_sides,
                    'modifier': modifier,
                    'rolls': rolls,
                    'total': total
                })
                
                # Replace the bracketed dice with the result in display text
                result_str = f"**{total}**" if (num_dice > 1 or modifier != 0) else f"**{rolls[0]}**"
                display_text = display_text.replace(f"[{dice_expr}]", result_str, 1)
            
            # Set description to show the text with results at the top
            embed.description = display_text
            
            # Add dice roll details - WITHOUT the "Result:" field for Tupper
            for result in roll_results:
                rolls_str = ", ".join(map(str, result['rolls']))
                modifier_str = f" {result['modifier']:+d}" if result['modifier'] != 0 else ""
                
                # Show only the dice details, no "Result:" field
                if result['num_dice'] > 1 or result['modifier'] != 0:
                    embed.add_field(name="", value=f"-# Rolling {result['dice_expr']}\n-# Rolls: {rolls_str}{modifier_str}", inline=False)
                else:
                    # Single die, no modifier
                    embed.add_field(name="", value=f"-# Rolling {result['dice_expr']}", inline=False)
            
            # Try to delete the original message (Tupper message)
            try:
                await message.delete()
            except:
                # If bot doesn't have permission to delete, just send the embed
                await message.channel.send(embed=embed)
                return
            
            # Send the embed (not as a reply since original is deleted)
            await message.channel.send(embed=embed)
            
        except Exception as e:
            print(f"[AUTO ROLL] Error: {e}")





@bot.event
@bot.event
async def on_raw_reaction_add(payload):
    """Handle reaction roles when user adds a reaction"""
    # Ignore bot's own reactions
    if payload.user_id == bot.user.id:
        return
    
    try:
        # Format emoji for comparison
        emoji_str = str(payload.emoji)
        # For custom emojis, format as <:name:id> or <a:name:id>
        if payload.emoji.id:
            if payload.emoji.animated:
                emoji_str = f"<a:{payload.emoji.name}:{payload.emoji.id}>"
            else:
                emoji_str = f"<:{payload.emoji.name}:{payload.emoji.id}>"
        
        print(f"[REACTION ROLE DEBUG] User reacted with: {emoji_str} on message {payload.message_id}")
        
        # Check if this message has reaction roles
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT role_id FROM reaction_roles WHERE message_id = ? AND emoji = ?",
                     (str(payload.message_id), emoji_str))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return  # Not a reaction role message
        
        role_id = int(result[0])
        
        # Get guild and member
        guild = bot.get_guild(payload.guild_id)
        if not guild:
            return
        
        member = guild.get_member(payload.user_id)
        if not member:
            return
        
        # Get role
        role = guild.get_role(role_id)
        if not role:
            print(f"[REACTION ROLE] Role {role_id} not found")
            return
        
        # Add role
        await member.add_roles(role)
        print(f"[REACTION ROLE] ✅ Added {role.name} to {member.name}")
        
    except Exception as e:
        print(f"[REACTION ROLE] Error adding role: {e}")
        import traceback
        traceback.print_exc()

@bot.event
async def on_raw_reaction_remove(payload):
    """Handle reaction roles when user removes a reaction"""
    try:
        # Format emoji for comparison
        emoji_str = str(payload.emoji)
        # For custom emojis, format as <:name:id> or <a:name:id>
        if payload.emoji.id:
            if payload.emoji.animated:
                emoji_str = f"<a:{payload.emoji.name}:{payload.emoji.id}>"
            else:
                emoji_str = f"<:{payload.emoji.name}:{payload.emoji.id}>"
        
        # Check if this message has reaction roles
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT role_id FROM reaction_roles WHERE message_id = ? AND emoji = ?",
                     (str(payload.message_id), emoji_str))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return  # Not a reaction role message
        
        role_id = int(result[0])
        
        # Get guild and member
        guild = bot.get_guild(payload.guild_id)
        if not guild:
            return
        
        member = guild.get_member(payload.user_id)
        if not member:
            return
        
        # Get role
        role = guild.get_role(role_id)
        if not role:
            return
        
        # Remove role
        await member.remove_roles(role)
        print(f"[REACTION ROLE] ❌ Removed {role.name} from {member.name}")
        
    except Exception as e:
        print(f"[REACTION ROLE] Error removing role: {e}")

# ==================== FLASK API FOR EMBEDS ====================
@api.route('/send_embed', methods=['POST'])
def api_send_embed():
    try:
        data = request.json
        channel_id = int(data['channel_id'])
        reaction_roles = data.get('reaction_roles', [])
        
        # Create embed
        embed = discord.Embed(
            title=data.get('title'),
            description=data.get('description'),
            color=int(data.get('color', '000000'), 16)
        )
        
        if data.get('footer_text'):
            embed.set_footer(text=data['footer_text'])
        if data.get('image_url'):
            embed.set_image(url=data['image_url'])
        if data.get('thumbnail_url'):
            embed.set_thumbnail(url=data['thumbnail_url'])
        
        # Send via bot using asyncio
        async def send():
            # Try to get regular channel first
            channel = bot.get_channel(channel_id)
            
            # If not found, try to get thread (includes forum posts)
            if not channel:
                # Search all guilds for the thread
                for guild in bot.guilds:
                    thread = guild.get_thread(channel_id)
                    if thread:
                        channel = thread
                        break
            
            if not channel:
                return None
            
            message = await channel.send(embed=embed)
            
            # Add reactions for reaction roles
            for rr in reaction_roles:
                try:
                    await message.add_reaction(rr['emoji'])
                except Exception as e:
                    print(f"Failed to add reaction {rr['emoji']}: {e}")
            
            return message.id
        
        # Get the bot's event loop
        import asyncio
        future = asyncio.run_coroutine_threadsafe(send(), bot.loop)
        message_id = future.result(timeout=10)
        
        if message_id:
            return jsonify({'status': 'success', 'message_id': str(message_id)}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Channel not found'}), 404
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api.route('/update_embed', methods=['POST'])
def api_update_embed():
    try:
        data = request.json
        channel_id = int(data['channel_id'])
        message_id = int(data['message_id'])
        
        # Create embed
        embed = discord.Embed(
            title=data.get('title'),
            description=data.get('description'),
            color=int(data.get('color', '000000'), 16)
        )
        
        if data.get('footer_text'):
            embed.set_footer(text=data['footer_text'])
        if data.get('image_url'):
            embed.set_image(url=data['image_url'])
        if data.get('thumbnail_url'):
            embed.set_thumbnail(url=data['thumbnail_url'])
        
        # Update via bot using asyncio
        async def update():
            # Try to get regular channel first
            channel = bot.get_channel(channel_id)
            
            # If not found, try to get thread (includes forum posts)
            if not channel:
                # Search all guilds for the thread
                for guild in bot.guilds:
                    thread = guild.get_thread(channel_id)
                    if thread:
                        channel = thread
                        break
            
            if not channel:
                return False
            message = await channel.fetch_message(message_id)
            await message.edit(embed=embed)
            return True
        
        # Get the bot's event loop
        import asyncio
        future = asyncio.run_coroutine_threadsafe(update(), bot.loop)
        success = future.result(timeout=10)
        
        if success:
            return jsonify({'status': 'success'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Channel or message not found'}), 404
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api.route('/upload_image', methods=['POST'])
def api_upload_image():
    """Upload image to Discord and return the CDN URL"""
    try:
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file provided'}), 400
        
        file = request.files['file']
        if not file.filename:
            return jsonify({'status': 'error', 'message': 'Empty filename'}), 400
        
        # Get upload channel ID from env or use a default
        # You need to set UPLOAD_CHANNEL_ID in your .env file
        upload_channel_id = int(os.getenv('UPLOAD_CHANNEL_ID', '0'))
        
        if not upload_channel_id:
            return jsonify({'status': 'error', 'message': 'Upload channel not configured'}), 500
        
        # Upload to Discord
        async def upload():
            channel = bot.get_channel(upload_channel_id)
            if not channel:
                return None
            
            # Read file data
            file_data = file.read()
            discord_file = discord.File(io.BytesIO(file_data), filename=file.filename)
            
            # Send file to Discord channel
            message = await channel.send(file=discord_file)
            
            # Return the attachment URL
            if message.attachments:
                return message.attachments[0].url
            return None
        
        # Get the bot's event loop
        import asyncio
        import io
        future = asyncio.run_coroutine_threadsafe(upload(), bot.loop)
        image_url = future.result(timeout=10)
        
        if image_url:
            return jsonify({'status': 'success', 'url': image_url}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Failed to upload'}), 500
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def run_api():
    api.run(host='0.0.0.0', port=5002, debug=False)

# Run the bot
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

if not TOKEN:
    print("ERROR: Discord Token not found! Check .env file")
else:
    # Start Flask API in separate thread
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    print("🌐 API server started on port 5002")
    
    # Start Discord bot
    bot.run(TOKEN)
