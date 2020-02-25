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
    return switcher.get(ordinal, "???")


async def getTournamentId(tournament):
    tournament = tournament.upper()
    switcher = {
        "LCS": "103462439438682788",
        "LEC": "103462459318635408",
        "LCK": "103540363364808496",
        "LPL": "103462420723438502",
        "OPL": "103535401218775284",
        "CBLOL": "103478354329449186",
        "TCL": "103495775740097550",
        "LJL": "103540397353089204",
        "LCSA": "103462454280724883",
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
