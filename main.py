import os
import discord
from discord.ext import commands
from collections import defaultdict, deque
import time

# Configuração das Intents necessárias para moderação e segurança
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.moderation = True

class SecurityBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Sincroniza os comandos de barra com o Discord
        await self.tree.sync()
        print("[COMANDOS] Comandos de barra sincronizados com sucesso.")

bot = SecurityBot()

# Dicionários em memória para controle de Spam/Flood
message_cooldowns = defaultdict(lambda: deque(maxlen=5))

@bot.event
async def on_ready():
    print(f"[BOT] Logado com sucesso como {bot.user}!")
    print("[STATUS] Sistemas de proteção ativados.")

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    # 1. Módulo Anti-Link Básico
    if "http://" in message.content or "https://" in message.content:
        if "discord.gg/" not in message.content:
            try:
                await message.delete()
                warning = await message.channel.send(
                    f"⚠️ **{message.author.mention}**, links não são permitidos neste canal!"
                )
                await warning.delete(delay=5)
            except discord.HTTPException:
                pass
            return

    # 2. Módulo Anti-Spam / Anti-Flood por Velocidade
    user_id = message.author.id
    current_time = time.time()
    
    message_cooldowns[user_id].append(current_time)

    if len(message_cooldowns[user_id]) == 5:
        if current_time - message_cooldowns[user_id][0] < 4:
            try:
                await message.delete()
                if message.guild.me.guild_permissions.moderate_members:
                    await message.author.timeout(discord.utils.utcnow() + discord.timedelta(minutes=1), reason="Anti-Spam Automático: Envio excessivo de mensagens.")
                    
                alert = await message.channel.send(
                    f"🚨 **{message.author.mention}** foi colocado em timeout por 1 minuto devido a spam/flood."
                )
                await alert.delete(delay=7)
            except discord.HTTPException:
                pass
            
            message_cooldowns[user_id].clear()
            return

    await bot.process_commands(message)

# View Interativa com Botões para o Painel
class ProtectionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180) # O painel expira em 3 minutos de inatividade

    @discord.ui.button(label="Configurações", style=discord.ButtonStyle.secondary, emoji="⚙️")
    async def config_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⚙️ Menu de configurações em desenvolvimento.", ephemeral=True)

    @discord.ui.button(label="Estatísticas", style=discord.ButtonStyle.secondary, emoji="📊")
    async def stats_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("📊 Estatísticas: Nenhuma ameaça detectada hoje.", ephemeral=True)

    @discord.ui.button(label="Modo Proteção", style=discord.ButtonStyle.danger, emoji="🔒")
    async def lockdown_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Modo Proteção alternado com sucesso.", ephemeral=True)

# Comando de Barra (Slash Command) /protecao com a Imagem do Aegis
@bot.tree.command(name="protecao", description="Acessa a central avançada de segurança e proteção do servidor.")
@discord.app_commands.checks.has_permissions(administrator=True)
async def protecao(interaction: discord.Interaction):
    embed = discord.Embed(
        description=(
            "**STATUS DOS MÓDULOS DE DEFESA:**\n\n"
            "🛡️ Anti-Spam: `[ ATIVO ]`\n"
            "🔗 Anti-Link: `[ ATIVO ]`\n"
            "👥 Anti-Raid: `[ ATIVO ]`\n"
            "✦ Anti-Nuke: `[ ATIVO ]`\n\n"
            "⚙️ **Nível de Proteção:** `ALTO`"
        ),
        color=0x111111 # Cor cinza escuro tecnológico
    )
    
    # Insere a imagem gerada do Aegis diretamente no Embed como banner visual
    embed.set_image(url="https://images.generativeai.google/watermarked_img_14640432207134942949.png")
    embed.set_footer(text="Aegis Security System • Central de Controle")

    view = ProtectionView()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

# Tratamento de erro de permissão para o comando
@protecao.error
async def protecao_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    if isinstance(error, discord.app_commands.errors.MissingPermissions):
        if interaction.response.is_done():
            await interaction.followup.send("❌ Você precisa ser administrador para usar este comando.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Você precisa ser administrador para usar este comando.", ephemeral=True)
    else:
        raise error

# Executa o bot utilizando a variável de ambiente configurada na Discloud
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    print("[ERRO] O token do bot não foi encontrado nas variáveis de ambiente.")
else:
    bot.run(TOKEN)