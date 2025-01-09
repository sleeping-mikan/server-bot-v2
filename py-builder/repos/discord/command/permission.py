#!ignore
from ...imports import *
from ...constant import *
from ...logger.logger_create import *
from ...minecraft.read_properties import *
from ...assets.text_dat import *
from ...assets.utils import *
#!end-ignore

# グループの設定
# root
command_group_permission = app_commands.Group(name="permission",description="permission group")

#/admin force <add/remove>
@command_group_permission.command(name="change",description=COMMAND_DESCRIPTION[lang]["permission"]["change"])
async def change(interaction: discord.Interaction,level: int,user:discord.User):
    await print_user(admin_logger,interaction.user)
    embed = ModifiedEmbeds.DefaultEmbed(title = f"/permission change {level} {user}")
    if await user_permission(interaction.user) < COMMAND_PERMISSION["permission change"]:
        await not_enough_permission(interaction,lang_logger)
        return
    async def read_force_admin():
        global bot_admin
        bot_admin = config["discord_commands"]["admin"]["members"]
    # 権限レベル1~4を付与
    if level >= 1 and level <= USER_PERMISSION_MAX:
        if user.id in config["discord_commands"]["admin"]["members"]:
            embed.add_field(name="",value=RESPONSE_MSG["permission"]["change"]["already_added"],inline=False)
            await interaction.response.send_message(embed=embed)
            return
        config["discord_commands"]["admin"]["members"][str(user.id)] = level
        #configファイルを変更する
        await rewrite_config(config)
        await read_force_admin()
        embed.add_field(name="",value=RESPONSE_MSG["permission"]["change"]["add_success"].format(user),inline=False)
        await interaction.response.send_message(embed=embed)
        admin_logger.info(f"exec force admin add {user}")
    elif level == 0:
        if user.id not in config["discord_commands"]["admin"]["members"]:
            embed.add_field(name="",value=RESPONSE_MSG["permission"]["change"]["already_removed"],inline=False)
            await interaction.response.send_message(embed=embed)
            return
        config["discord_commands"]["admin"]["members"].pop(str(user.id))
        #configファイルを変更する
        await rewrite_config(config)
        await read_force_admin()
        embed.add_field(name="",value=RESPONSE_MSG["permission"]["change"]["remove_success"].format(user),inline=False)
        await interaction.response.send_message(embed=embed)
        admin_logger.info(f"exec force admin remove {user}")
    else:
        embed.add_field(name="",value=RESPONSE_MSG["permission"]["change"]["invalid_level"].format(USER_PERMISSION_MAX,level),inline=False)
        await interaction.response.send_message(embed=embed)
        admin_logger.info("invalid level")

#/permission <user>
@command_group_permission.command(name="view",description=COMMAND_DESCRIPTION[lang]["permission"]["view"])
async def view(interaction: discord.Interaction,user:discord.User,detail:bool):
    await print_user(permission_logger,interaction.user)
    embed = ModifiedEmbeds.DefaultEmbed(title = f"/permission view {user} {detail}")
    COMMAND_MAX_LENGTH = max([len(key) for key in COMMAND_PERMISSION])
    value = {"admin":"☐","force_admin":"☐"}
    if await is_administrator(user): value["admin"] = f"☑({USER_PERMISSION_MAX})"
    value["force_admin"] = await user_permission(user)
    if detail:
        my_perm_level = await user_permission(user)
        can_use_cmd = {f"{key}":("☑" if COMMAND_PERMISSION[key] <= my_perm_level else "☐") + f"({COMMAND_PERMISSION[key]})" for key in COMMAND_PERMISSION}
        embed.add_field(name="",value=RESPONSE_MSG["permission"]["success"].format(user,value["admin"],value["force_admin"]) + "\n```\n"+"\n".join([f"{key.ljust(COMMAND_MAX_LENGTH)} : {value}" for key,value in can_use_cmd.items()]) + "\n```",inline=False)
        await interaction.response.send_message(embed=embed)
    else:
        embed.add_field(name="",value=RESPONSE_MSG["permission"]["success"].format(user,value["admin"],value["force_admin"]),inline=False)
        await interaction.response.send_message(embed=embed)
    permission_logger.info("send permission info : " + str(user.id) + f"({user})")

tree.add_command(command_group_permission)