import asyncio
import re
import discord
from datetime import datetime, timedelta


async def integerPrefix(ordinal):
    switcher = {
        "1": "1st",
        "2": "2nd",
        "3": "3rd",
        "4": "4th",
        "5": "5th",
        "6": "6th",
        "7": "7th",
        "8": "8th",
        "9": "9th",
        "10": "10th",
        "11": "11th",
        "12": "12th",
        "13": "13th",
        "14": "14th",
        "15": "15th",
        "16": "16th",
        "17": "17th",
        "18": "18th",
        "19": "19th",
        "20": "20th",
    }
    return switcher.get(str(ordinal), "???")


async def getTournamentId(tournament):
    tournament = tournament.upper()
    switcher = {
        "LCS": "104174992692075107",
        "LEC": "104169295253189561",
        "LCK": "104174613295388764",
        "LPL": "104282610668475466",
        "OPL": "104151038596540368",
        "CBLOL": "104202471497759152",
        "TCL": "104248884617992857",
        "LJL": "104169308670244006",
        "LCSA": "104174601803063383",
    }
    return switcher.get(tournament, "Invalid League")


async def getLeagueId(league):
    league = league.upper()
    switcher = {
        "EUM": "100695891328981122",
        "TAL": "101097443346691685",
        "LLA": "101382741235120470",
        "WORLDS": "98767975604431411",
        "ALL-STARS": "98767991295297326",
        "LCS": "98767991299243165",
        "LEC": "98767991302996019",
        "LCK": "98767991310872058",
        "LPL": "98767991314006698",
        "MSI": "98767991325878492",
        "OPL": "98767991331560952",
        "CBLOL": "98767991332355509",
        "TCL": "98767991343597634",
        "NAC": "98767991349120232",
        "LCSA": "99332500638116286",
        "LJL": "98767991349978712",
    }
    return switcher.get(league, "Invalid League")


async def sanitizeinput(inputs):
    return re.sub(r"[^a-zA-Z0-9-]", "", inputs)


async def timeformatting(days, hours, minutes):
    if days == "0":
        if hours == "0":
            if minutes == "0":
                remainingtime = "Starting soon!\n"
            elif minutes == "1":
                remainingtime = minutes + " minute\n"
            else:
                remainingtime = minutes + " minutes\n"
        if hours == "1":
            if minutes == "0":
                remainingtime = hours + " hour\n"
            elif minutes == "1":
                remainingtime = hours + " hour, " + minutes + " minute\n"
            else:
                remainingtime = hours + " hour, " + minutes + " minutes\n"
        else:
            if minutes == "0":
                remainingtime = hours + " hours\n"
            elif minutes == "1":
                remainingtime = hours + " hours, " + minutes + " minute\n"
            else:
                remainingtime = hours + " hours, " + minutes + " minutes\n"
    elif days == "1":
        if hours == "0":
            if minutes == "0":
                remainingtime = days + " day\n"
            elif minutes == "1":
                remainingtime = days + " day, " + minutes + " minute\n"
            else:
                remainingtime = days + " day, " + minutes + " minutes\n"
        if hours == "1":
            if minutes == "0":
                remainingtime = days + " day, " + hours + " hour\n"
            elif minutes == "1":
                remainingtime = days + " day, " + hours + " hour\n"
            else:
                remainingtime = days + " day, " + hours + " hour\n"
        else:
            if minutes == "0":
                remainingtime = days + " day, " + hours + " hours\n"
            elif minutes == "1":
                remainingtime = days + " day, " + hours + " hours\n"
            else:
                remainingtime = days + " day, " + hours + " hours\n"
    else:
        if hours == "0":
            if minutes == "0":
                remainingtime = days + " days\n"
            elif minutes == "1":
                remainingtime = days + " days, " + minutes + " minute\n"
            else:
                remainingtime = days + " days, " + minutes + " minutes\n"
        if hours == "1":
            if minutes == "0":
                remainingtime = days + " days, " + hours + " hour\n"
            elif minutes == "1":
                remainingtime = days + " days, " + hours + " hour\n"
            else:
                remainingtime = days + " days, " + hours + " hour\n"
        else:
            if minutes == "0":
                remainingtime = days + " days, " + hours + " hours\n"
            elif minutes == "1":
                remainingtime = days + " days, " + hours + " hours\n"
            else:
                remainingtime = days + " days, " + hours + " hours\n"
    return remainingtime


async def days_hours_minutes(td):
    return str(td.days), str(td.seconds // 3600), str((td.seconds // 60) % 60)


async def championid_to_champion(championid: str):
    switcher = {
        "266": "Aatrox",
        "103": "Ahri",
        "84": "Akali",
        "12": "Alistar",
        "32": "Amumu",
        "34": "Anivia",
        "1": "Annie",
        "523": "Aphelios",
        "22": "Ashe",
        "136": "AurelionSol",
        "268": "Azir",
        "432": "Bard",
        "53": "Blitzcrank",
        "63": "Brand",
        "201": "Braum",
        "51": "Caitlyn",
        "164": "Camille",
        "69": "Cassiopeia",
        "31": "Chogath",
        "42": "Corki",
        "122": "Darius",
        "131": "Diana",
        "119": "Draven",
        "36": "DrMundo",
        "245": "Ekko",
        "60": "Elise",
        "28": "Evelynn",
        "81": "Ezreal",
        "9": "Fiddlesticks",
        "114": "Fiora",
        "105": "Fizz",
        "3": "Galio",
        "41": "Gangplank",
        "86": "Garen",
        "150": "Gnar",
        "79": "Gragas",
        "104": "Graves",
        "120": "Hecarim",
        "74": "Heimerdinger",
        "420": "Illaoi",
        "39": "Irelia",
        "427": "Ivern",
        "40": "Janna",
        "59": "JarvanIV",
        "24": "Jax",
        "126": "Jayce",
        "202": "Jhin",
        "222": "Jinx",
        "145": "Kaisa",
        "429": "Kalista",
        "43": "Karma",
        "30": "Karthus",
        "38": "Kassadin",
        "55": "Katarina",
        "10": "Kayle",
        "141": "Kayn",
        "85": "Kennen",
        "121": "Khazix",
        "203": "Kindred",
        "240": "Kled",
        "96": "KogMaw",
        "7": "Leblanc",
        "64": "LeeSin",
        "89": "Leona",
        "127": "Lissandra",
        "236": "Lucian",
        "117": "Lulu",
        "99": "Lux",
        "54": "Malphite",
        "90": "Malzahar",
        "57": "Maokai",
        "11": "MasterYi",
        "21": "MissFortune",
        "82": "Mordekaiser",
        "25": "Morgana",
        "267": "Nami",
        "75": "Nasus",
        "111": "Nautilus",
        "518": "Neeko",
        "76": "Nidalee",
        "56": "Nocturne",
        "20": "Nunu",
        "2": "Olaf",
        "61": "Orianna",
        "516": "Ornn",
        "80": "Pantheon",
        "78": "Poppy",
        "555": "Pyke",
        "246": "Qiyana",
        "133": "Quinn",
        "497": "Rakan",
        "33": "Rammus",
        "421": "RekSai",
        "58": "Renekton",
        "107": "Rengar",
        "92": "Riven",
        "68": "Rumble",
        "13": "Ryze",
        "113": "Sejuani",
        "235": "Senna",
        "875": "Sett",
        "35": "Shaco",
        "98": "Shen",
        "102": "Shyvana",
        "27": "Singed",
        "14": "Sion",
        "15": "Sivir",
        "72": "Skarner",
        "37": "Sona",
        "16": "Soraka",
        "50": "Swain",
        "517": "Sylas",
        "134": "Syndra",
        "223": "TahmKench",
        "163": "Taliyah",
        "91": "Talon",
        "44": "Taric",
        "17": "Teemo",
        "412": "Thresh",
        "18": "Tristana",
        "48": "Trundle",
        "23": "Tryndamere",
        "4": "TwistedFate",
        "29": "Twitch",
        "77": "Udyr",
        "6": "Urgot",
        "110": "Varus",
        "67": "Vayne",
        "45": "Veigar",
        "161": "Velkoz",
        "254": "Vi",
        "112": "Viktor",
        "8": "Vladimir",
        "106": "Volibear",
        "19": "Warwick",
        "62": "Wukong",
        "498": "Xayah",
        "101": "Xerath",
        "5": "XinZhao",
        "157": "Yasuo",
        "83": "Yorick",
        "350": "Yuumi",
        "154": "Zac",
        "238": "Zed",
        "115": "Ziggs",
        "26": "Zilean",
        "142": "Zoe",
        "143": "Zyra",
    }
    return switcher.get(championid)

async def champion_to_emoji(champion: str):
    champion.title()
    switcher = {
        "Aatrox": "<:aatrox:625790204132720650>",
        "Ahri": "<:ahri:625790195400441909>",
        "Akali": "<:akali:625790186105733151>",
        "Alistar": "<:alistar:625790176681132083>",
        "Amumu": "<:amumu:625790167474765852>",
        "Anivia": "<:anivia:625790157857095712>",
        "Annie": "<:annie:625790148810113044>",
        "Aphelios": "<:aphelios:664616395333435392>",
        "Ashe": "<:ashe:625790140153069598>",
        "AurelionSol": "<:aurelion_sol:625790131659472926>",
        "Azir": "<:azir:625790120351629333>",
        "Bard": "<:bard:625790110788485140>",
        "Blitzcrank": "<:blitzcrank:625790100294598667>",
        "Brand": "<:brand:625790090349903892>",
        "Braum": "<:braum:625790081034223629>",
        "Caitlyn": "<:caitlyn:625790069101428767>",
        "Camille": "<:camille:625790056623505442>",
        "Cassiopeia": "<:cassiopeia:625790044694904872>",
        "Chogath": "<:chogath:625790035299532811>",
        "Corki": "<:corki:625790026864787466>",
        "Darius": "<:darius:625790018195161098>",
        "Diana": "<:diana:625790010054017044>",
        "Draven": "<:draven:625789999517794305>",
        "DrMundo": "<:mundo:625789151098175508>",
        "Ekko": "<:ekko:625789987912155176>",
        "Elise": "<:elise:625789975392419861>",
        "Evelynn": "<:evelynn:625789962549198867>",
        "Ezreal": "<:ezreal:625789950255824917>",
        "Fiddlesticks": "<:fiddlesticks:625789925081481236>",
        "Fiora": "<:fiora:625789914155450389>",
        "Fizz": "<:fizz:625789897546006610>",
        "Galio": "<:galio:625789883830632472>",
        "Gangplank": "<:gangplank:625789869490438146>",
        "Garen": "<:garen:625789857125629953>",
        "Gnar": "<:gnar:625789845096235009>",
        "Gragas": "<:gragas:625789833855500328>",
        "Graves": "<:graves:625789821478109204>",
        "Hecarim": "<:hecarim:626289866304520203>",
        "Heimerdinger": "<:heimerdinger:625789789290889217>",
        "Illaoi": "<:illaoi:625789775575515138>",
        "Irelia": "<:irelia:625789760514031617>",
        "Ivern": "<:ivern:625789749994586163>",
        "Janna": "<:janna:625789735381762048>",
        "JarvanIV": "<:jarvan_iv:625789724899934269>",
        "Jax": "<:jax:625789709104316426>",
        "Jayce": "<:jayce:625789696257032192>",
        "Jhin": "<:jhin:625789684986937365>",
        "Jinx": "<:jinx:625789672366538783>",
        "Kaisa": "<:kaisa:625789659590426624>",
        "Kalista": "<:kalista:625789644138610693>",
        "Karma": "<:karma:625789630209327137>",
        "Karthus": "<:karthus:625789609728671789>",
        "Kassadin": "<:kassadin:625789591063887892>",
        "Katarina": "<:katarina:625789576274903070>",
        "Kayle": "<:kayle:625789555475349525>",
        "Kayn": "<:kayn:625789541361385472>",
        "Kennen": "<:kennen:625789525028765697>",
        "Khazix": "<:khazix:625789510562742313>",
        "Kindred": "<:kindred:625789453398573059>",
        "Kled": "<:kled:625789440475791412>",
        "KogMaw": "<:kogmaw:625789424340566016>",
        "Leblanc": "<:leblanc:625789403692007444>",
        "LeeSin": "<:lee_sin:625789389582237709>",
        "Leona": "<:leona:625789375866732574>",
        "Lissandra": "<:lissandra:625789361178542081>",
        "Lucian": "<:lucian:625789345349238804>",
        "Lulu": "<:lulu:625789323660230686>",
        "Lux": "<:lux:625789303796006912>",
        "Malphite": "<:malphite:625789285198594078>",
        "Malzahar": "<:malzahar:625789269201649677>",
        "Maokai": "<:maokai:625789252059529216>",
        "MasterYi": "<:master_yi:625789237178007552>",
        "MissFortune": "<:miss_fortune:625789204743323648>",
        "Mordekaiser": "<:mordekaiser:625789188373217291>",
        "Morgana": "<:morgana:625789170165612563>",
        "Nami": "<:nami:625789128059125810>",
        "Nasus": "<:nasus:625789108169605121>",
        "Nautilus": "<:nautilus:625789087395086346>",
        "Neeko": "<:neeko:625789071507324938>",
        "Nidalee": "<:nidalee:625789054172135437>",
        "Nocturne": "<:nocturne:625789038955200522>",
        "Nunu": "<:nunu_willump:625789022199087105>",
        "Olaf": "<:olaf:625789008831709219>",
        "Orianna": "<:orianna:625788991546982420>",
        "Ornn": "<:ornn:625788972504842261>",
        "Pantheon": "<:pantheon:625788948765212696>",
        "Poppy": "<:poppy:625788932633919518>",
        "Pyke": "<:pyke:625788916238385182>",
        "Qiyana": "<:qiyana:625788899523821571>",
        "Quinn": "<:quinn:625788884843888644>",
        "Rakan": "<:rakan:625788870927056911>",
        "Rammus": "<:rammus:625788779193565225>",
        "RekSai": "<:reksai:625788764316499977>",
        "Renekton": "<:renekton:625788579532242965>",
        "Rengar": "<:rengar:625788554957684777>",
        "Riven": "<:riven:625788521801580555>",
        "Rumble": "<:rumble:625788506983235613>",
        "Ryze": "<:ryze:625788476650160209>",
        "Sejuani": "<:sejuani:625788458916511755>",
        "Senna": ":senna:",
        "Sett": ":sett:",
        "Shaco": "<:shaco:625788438179872816>",
        "Shen": "<:shen:625788396966641674>",
        "Shyvana": "<:shyvana:625788376464752651>",
        "Singed": "<:singed:625788360002240518>",
        "Sion": "<:sion:625788259498197023>",
        "Sivir": "<:sivir:625788243270565990>",
        "Skarner": "<:skarner:625788202250403880>",
        "Sona": "<:sona:625788181320826890>",
        "Soraka": "<:soraka:625788161989279744>",
        "Swain": "<:swain:625788139906269194>",
        "Sylas": "<:sylas:625788119412768778>",
        "Syndra": "<:syndra:625788099355607051>",
        "TahmKench": "<:tahm_kench:625788073602711557>",
        "Taliyah": "<:taliyah:625787944761819156>",
        "Talon": "<:talon:625787923203358740>",
        "Taric": "<:taric:625787905381629952>",
        "Teemo": "<:teemo:625787886884618281>",
        "Thresh": "<:thresh:625787866450231336>",
        "Tristana": "<:tristana:625787846048874513>",
        "Trundle": "<:trundle:625787807016943651>",
        "Tryndamere": "<:tryndamere:625787788146769920>",
        "TwistedFate": "<:twisted_fate:625787771109244928>",
        "Twitch": "<:twitch:476951718089981962>",
        "Udyr": "<:udyr:625787732710653952>",
        "Urgot": "<:urgot:625787702121332736>",
        "Varus": "<:varus:625787655661289476>",
        "Vayne": "<:vayne:625787630591672368>",
        "Veigar": "<:veigar:625787567094235147>",
        "Velkoz": "<:velkoz:625787544029626373>",
        "Vi": "<:vi:625787523867607102>",
        "Viktor": "<:viktor:625787500086165534>",
        "Vladimir": "<:vladimir:625787473519443975>",
        "Volibear": "<:volibear:625787458566619168>",
        "Warwick": "<:warwick:625787438291222530>",
        "Wukong": "<:wukong:625787419316191232>",
        "Xayah": "<:xayah:625787401029156916>",
        "Xerath": "<:xerath:625787240714469386>",
        "XinZhao": "<:xin_zhao:625787221932376089>",
        "Yasuo": "<:yasuo:625787203468918785>",
        "Yorick": "<:yorick:625787178143973407>",
        "Yuumi": "<:yuumi:625786992843816981>",
        "Zac": "<:zac:625786978004107275>",
        "Zed": "<:zed:625786963433226250>",
        "Ziggs": "<:ziggs:625786950242140192>",
        "Zilean": "<a:zilean:623399160900485121>",
        "Zoe": "<:zoe:625786832973463609>",
        "Zyra": "<:zyra:625786818473885707>",
    }
    return switcher.get(champion, None)

async def valid_role(role: str):
    switcher = {
        "TOP": "Top",
        "JUNGLE": "Jungle",
        "MIDDLE": "Mid",
        "DUO_CARRY": "Bot",
        "DUO_SUPPORT": "Support"
    }
    return switcher.get(role, "")

async def region_to_valid_region(region: str):
    switcher = {
        "RU": "RU",
        "KR": "KR",
        "BR": "BR1",
        "OCE": "OC1",
        "JP": "JP1",
        "NA": "NA1",
        "EUNE": "EUN1",
        "EUW": "EUW1",
        "TR": "TR1",
        "LAN": "LA1",
        "LAS": "LA2",
    }
    return switcher.get(region, "Invalid Region")


async def get_start_time(time):
    starttime = re.sub("[T]", " ", time)
    starttime = re.sub("[Z]", "", starttime)
    starttime = datetime.strptime(starttime, "%Y-%m-%d %H:%M:%S")
    return starttime

async def embedgen(ctx, **args):
    discord_embed = {
        "title": "Test",
        "type": "rich",
        "description": "",
        "url": "",
        "timestamp": "",
        "color": 0xA9152B,
        "footer": "",
        "image": "",
        "thumbnail": "",
        "video": "",
        "provider": "",
        "author": "",
        "fields": [
            {"inline": False, "name": "Field0", "value": "Field0MSG"},
            {"inline": True, "name": "Field1", "value": "Field1MSG"},
        ],
    }
    return discord_embed

async def region_to_valid_server(region: str):
    switcher = {
        "NA1": "spectator.na2.lol.riotgames.com:80",
        "EUW1": "spectator.euw1.lol.riotgames.com:80"
    }
    return switcher.get(region, "Invalid Server")

async def division_to_number(division: str):
    switcher = {
        "I": 1,
        "II": 2,
        "III": 3,
        "IV": 4,
        "V": 5
    }
    return switcher.get(division, "error")

async def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor
    return bytes

async def role_reaction_emojis(key=None):
    reactions = {
            "NA": "<:NorthAmerica:701323008500957204>",
            "EUNE": "<:EuropeNE:701324408610095124>",
            "EUW": "<:EuropeWest:701324198143852545>",
            "OCE": "<:Oceania:701324676298702898>",
            "18": "🔞"
        }
    if key == None:
        return reactions
    else:
        key_list = list(reactions.keys())
        val_list = list(reactions.values())
        return key_list[val_list.index(key)]

async def role_reaction_roles(role):
    roles = {
        "NA": 662149881938575370,
        "EUW": 662150028474712066,
        "EUNE": 663462206284759051,
        "OCE": 663462621948805151,
        "18": 665331179528126496
    }
    return roles.get(role, "error")

async def spectategen(ctx, region, gameID, encryptionkey):
    server = await region_to_valid_server(region)
    if server == "Invalid Server":
        return False
    f = open("Spectate.bat", "w")
    f.write("""rem OP.GG Spectate 
    SETLOCAL enableextensions enabledelayedexpansion 
    @echo off

    echo -----------------------
    echo Spectate by op.gg
    echo -----------------------

    set RADS_PATH="C:\Riot Games\League of Legends"

    if exist "%RADS_PATH%\Game" (
        cd /d "!RADS_PATH!\Config"
        for /F "delims=" %%a in ('find "        locale: " LeagueClientSettings.yaml') do set "locale=%%a"
        for /F "tokens=2 delims=: " %%a in ("!locale!") do set "locale=%%a"

        SET RADS_PATH="!RADS_PATH!\Game"
        @cd /d !RADS_PATH!

        if exist "League of Legends.exe" (
            @start "" "League of Legends.exe" "spectator {} {} {} {}" "-UseRads" "-Locale=!locale!" "-GameBaseDir=.."
            goto :eof
        )
    )

    if exist "%RADS_PATH%\RADS" (
        SET RADS_PATH="!RADS_PATH!\RADS"
        @cd /d !RADS_PATH!

        @cd /d "!RADS_PATH!\projects"
        for /d %%D in (league_client_*) do (
            for /F "tokens=3,4 delims=_ " %%a in ("%%~nxD") do (
                set locale=%%a_%%b
            )
        )

        for /l %%a in (1,1,100) do if "!RADS_PATH:~-1!"==" " set RADS_PATH=!RADS_PATH:~0,-1!
        @cd /d "!RADS_PATH!\solutions\lol_game_client_sln\releases"

        set /a v0=0, v1=0, v2=0, v3=0
        set init=0
        for /d %%A in ("!RADS_PATH!\solutions\lol_game_client_sln\releases\*") do (
            set currentDirectory=%%~nxA

            for /F "tokens=1,2,3,4 delims=." %%i in ("!currentDirectory!") do (
                set /a test=%%i*1, test2=%%j*1, test3=%%k*1, test4=%%l*1

                if !init! equ 0 (
                    set /a init=1, flag=1
                ) else (
                    set flag=0

                    if !test! gtr !v0! (
                        set flag=1
                    ) else (
                        if !test2! gtr !v1! (
                            set flag=1
                        ) else (
                            if !test3! gtr !v2! (
                                set flag=1
                            ) else (
                                if !test4! gtr !v3! (
                                    set flag=1
                                )
                            )
                        )
                    )
                )

                if !flag! gtr 0 (
                    set /a v0=!test!, v1=!test2!, v2=!test3!, v3=!test4!
                )
            )
        )

        if !init! equ 0 goto cannotFind
        set lolver=!v0!.!v1!.!v2!.!v3!

        @cd /d "!RADS_PATH!\solutions\lol_game_client_sln\releases\!lolver!\deploy"
        if exist "League of Legends.exe" (
            @start "" "League of Legends.exe" "spectator {} {} {} {}" "-UseRads" "-Locale=!locale!" "-GameBaseDir=.."
            goto :eof
        )
    )

    echo ===================
    echo KR: LOL 
    echo EN: Cannot found LOL directory path for automatic. Please see our spectate help page: http://www.op.gg/help/observer
    echo ===================
    @pause

    :eof""".format(server, encryptionkey, gameID, region, server, encryptionkey, gameID, region)) 
    f.close()
    return