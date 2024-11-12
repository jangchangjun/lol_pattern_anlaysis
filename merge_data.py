import pandas as pd
import json

def merge_combat(target, opponent):
    combat = {}
    combat_kills = 0
    if not (target['kills'] == 0 and opponent['kills'] == 0):
        combat_kills = target['kills'] / (target['kills'] + opponent['kills'])
    combat['killsRatio'] = combat_kills

    combat_deaths = 0
    if not (target['deaths'] == 0 and opponent['deaths'] == 0):
        combat_deaths = target['deaths'] / (target['deaths'] + opponent['deaths'])
    combat['deathsRatio'] = combat_deaths

    combat_assists = 0
    if not (target['assists'] == 0 and opponent['assists'] == 0):
        combat_assists = target['assists'] / (target['assists'] + opponent['assists'])
    combat['assistsRatio'] = combat_assists

    combat_solokills = 0
    if not (target['solokills'] == 0 and opponent['solokills'] == 0):
        combat_solokills = target['solokills'] / (target['solokills'] + opponent['solokills'])
    combat['solokillsRatio'] = combat_solokills

    combat_solodeaths = 0
    if not (target['solodeaths'] == 0 and opponent['solodeaths'] == 0):
        combat_solodeaths = target['solodeaths'] / (target['solodeaths'] + opponent['solodeaths'])
    combat['solodeathsRatio'] = combat_solodeaths

    combat['dpm'] = target['dpm']
    combat['dtpm'] = target['dtpm']

    combat['targetKDA'] = {
        "kills" : target['kills'],
        "deaths" : target['deaths'],
        "assists" : target['assists']
    }

    combat['targetSoloKDA'] = {
        "solokills" : target['solokills'],
        "solodeaths" : target['solodeaths']
    }

    combat['opponentKDA'] = {
        "kills": opponent['kills'],
        "deaths": opponent['deaths'],
        "assists": opponent['assists']
    }

    combat['opponentSoloKDA'] = {
        "solokills": opponent['solokills'],
        "solodeaths": opponent['solodeaths']
    }

    return combat

def merge_manage(target):
    manage = {}
    manage['cspm'] = target['cspm']
    manage['gpm'] = target['gpm']
    manage['xpm'] = target['xpm']
    manage['dpd'] = target['dpd']
    manage['dpg'] = target['dpg']
    return manage

def merge_diff(target, opponent):
    diff = {}
    diff['dpm'] = target['dpm'] - opponent['dpm']
    diff['dtpm'] = target['dtpm'] - opponent['dtpm']
    diff['cspm'] = target['cspm'] - opponent['cspm']
    diff['gpm'] = target['gpm'] - opponent['gpm']
    diff['xpm'] = target['xpm'] - opponent['xpm']
    diff['dpd'] = target['dpd'] - opponent['dpd']
    diff['dpg'] = target['dpg'] - opponent['dpg']
    return diff

def merge_data(target, opponent):
    merged_data = {
        "GamaName" : target.iloc[0]['riotIdGameName'],
        "matches" : []
    }

    for j in range(len(target)):
        match = {}
        match["matchId"] = target.iloc[j]['matchId']
        match["gameCreation"] = int(target.iloc[j]['gameCreation'])
        match["gameDuration"] = float(target.iloc[j]['gameDuration'])
        match["riotIdGameName"] = target.iloc[j]['riotIdGameName']
        match["participantId"] = int(target.iloc[j]['participantId'])
        match["opponentRiotIdGameName"] = opponent.iloc[j]['riotIdGameName']
        match["opponentParticipantId"] = int(opponent.iloc[j]['participantId'])
        match["targetTeamId"] = int(target.iloc[j]['teamId'])
        match["targetWin"] = bool(target.iloc[j]['win'])

        at14 = {}
        at14["gameDuration"] = target.iloc[j]['at14']['gameDuration']
        at14["combat"] = merge_combat(target.iloc[j]['at14'], opponent.iloc[j]['at14'])
        at14["manage"] = merge_manage(target.iloc[j]['at14'])
        at14["diff"] = merge_diff(target.iloc[j]['at14'], opponent.iloc[j]['at14'])
        match["at14"] = at14

        af14 = {}
        af14["gameDuration"] = target.iloc[j]['af14']['gameDuration']
        af14["combat"] = merge_combat(target.iloc[j]['af14'], opponent.iloc[j]['af14'])
        af14["manage"] = merge_manage(target.iloc[j]['af14'])
        af14["diff"] = merge_diff(target.iloc[j]['af14'], opponent.iloc[j]['af14'])
        match["af14"] = af14

        merged_data["matches"].append(match)
    return merged_data

df_target   = pd.read_json("./extracted_full_data.json")
df_opponent = pd.read_json("./extracted_full_data_o.json")

total_data = []

for j in range(len(df_target)):
    target = pd.DataFrame(df_target.iloc[j]['match'])
    opponent = pd.DataFrame(df_opponent.iloc[j]['match'])

    gamer_data = merge_data(target, opponent)
    print(gamer_data)

    total_data.append(gamer_data)

with open('merged_data_full.json', 'w', encoding='utf-8') as f:
    json.dump(total_data, f, ensure_ascii=False, indent=4)