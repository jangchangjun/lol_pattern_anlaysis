# 미드라이너의 매치 지표를 통한 게임의 승패 예측

## 1. 개요

리그 오브 레전드 게임은 5명의 팀원을 탑, 미드, 정글, 바텀의 네 라인으로 나누어 상대팀의 넥서스를 파괴하여 승리를 쟁취하는 게임이다.
4개의 라인 모두 게임에서 중요한 역할을 하지만 그 중에서도 미드라이너의 역할이 가장 중심을 맡고있어 게임의 결과에 가장 큰 영향을 미친다.

<div><p align='center'><img src="img/lol.jpeg", width = "600", height = "500"></p></div>



이 프로젝트는 랜덤한 유저 30명의 미드 매치 데이터를 수집, 가공하여 만든 데이터셋을 활용해 매치의 승,패를 예측하는 프로그램을 만들고자한다.

## 2. 데이터 전처리

- 원본 데이터

  [솔로랭크 30](solo_rank_30 "solo rank30")<br/>

  각 유저의 데이터는 customData, matchData, timelineData로 이루어져 있으며
  custom 데이터는 킬, 데스, 어시스트 및 드래곤, total cs와 같은 개인 데이터로 이루어져있고
  match 데이터는 각 매치의 주요정보로 이루어져있으며
  마지막으로 timeline 데이터는 특정 시간에 발생한 이벤트의 유형, 플레이어의 상태, 피해량 통계와  
  같은 데이터로 이루어져있다.

- 예외 처리

  위 단계에선 모든 게임데이터 중 유저가 미드라이너로서 플레이한 데이터만을 추출해, 그 데이터에서
  유의미한 데이터를 찾아내는 단계이다.

  ```
  def extract_data(df_match, df_timeline, gamer_name, opposite=False):
    gamer_data =[]

    for j, match in enumerate(df_match['info'].values):
        if pd.isna(df_match['metadata'][j]):
            #print(f"No game in {j+1}th match")
            continue

        matchId = df_match['metadata'][j]['matchId']
        #print(matchId)

        timelineExist = False
        for k, timeline in enumerate(df_timeline['metadata']):
            if not pd.isna(timeline):
                if timeline['matchId'] == matchId:
                    match_timeline = df_timeline['info'][k]
                    timelineExist = True
                    #print(matchId, timeline['matchId'])
                    break

        if not timelineExist:
            #print(f"{matchId} does not exist in timeline data.")
            continue

        check_gamer_mid = False
        teamid = -1
        oteamid = -1

        for pid, participant in enumerate(match['participants']):
            if participant['riotIdGameName'] == gamer_name:
                if participant['teamPosition'] == "MIDDLE":
                    check_gamer_mid = True
                    teamid = pid
            else:
                if participant['teamPosition'] == "MIDDLE":
                    oteamid = pid

        #print(check_gamer_mid, teamid, oteamid)
        if opposite:
            tmp = teamid
            teamid = oteamid
            oteamid = tmp  
  ```

  게임 매치 데이터에서 메타데이터와 타임라인이 없는 경기를 건너뛰고, 미드라이너로서
  플레이한 데이터를 추출한 뒤 특정 플레이어와 상대 팀 정보를 추출하였다.


- 매치 추출

  이 단계예선 앞선 예외처리를 진행한 데이터에서 특정 매치의 정보를 추출하였다.

  ```
   target_data = {}
        if check_gamer_mid and match['gameDuration'] > 1200:
            match_p = match['participants'][teamid]
            match_o = match['participants'][oteamid]
            target_data["riotIdGameName"] = match_p['riotIdGameName']
            target_data["matchId"] = df_match['metadata'][0]['matchId']
            target_data["gameCreation"] = match['gameCreation']
            target_data["gameDuration"] = match_p['challenges']['gameLength']
            target_data["participantId"] = match_p['participantId']
            target_data["opponentpId"] = match_o['participantId']
            target_data["teamId"] = match_p['teamId']
            target_data["teamPosition"] = match_p['teamPosition']
            target_data["win"] = match_p['win']

            target_data['kda'] = match_p['challenges']['kda']
            target_data['kills'] = match_p['kills']
            target_data['deaths'] = match_p['deaths']
            target_data['assists'] = match_p['assists']

            solo_kill, solo_death = 0, 0
            for frame in match_timeline['frames']:
                for event in frame['events']:
                    if (event['type'] == "CHAMPION_KILL") and ('assistingParticipantIds' not in event):  # 1 vs 1 구도
                        if (event['killerId'] == target_data['participantId']):
                            solo_kill += 1
                        elif (event['victimId'] == target_data['participantId']):
                            solo_death += 1

            target_data['solokills'] = solo_kill
            target_data['solodeaths'] = solo_death

            target_data['totalDamageDealtToChampions'] = match_p['totalDamageDealtToChampions']
            target_data['totalDamageTaken'] = match_p['totalDamageTaken']
            target_data['totalMinionsKilled'] = match_p['totalMinionsKilled']
            target_data['totalCS'] = target_data['totalMinionsKilled'] + match_p['totalEnemyJungleMinionsKilled']
            target_data['goldEarned'] = match_p['goldEarned']
            target_data['totalXP'] = match_timeline['frames'][-1]['participantFrames'][str(target_data['participantId'])][
                'xp']

            duration = target_data['gameDuration'] / 60
            target_data['dpm'] = target_data['totalDamageDealtToChampions'] / duration
            target_data['dtpm'] = target_data['totalDamageTaken'] / duration
            target_data['mpm'] = target_data['totalMinionsKilled'] / duration
            target_data['cspm'] = target_data['totalCS'] / duration
            target_data['xpm'] = target_data['totalXP'] / duration
            target_data['gpm'] = target_data['goldEarned'] / duration
            target_data['dpd'] = target_data['totalDamageDealtToChampions'] / (
                1 if target_data['deaths'] == 0 else target_data['deaths'])
            target_data['dpg'] = target_data['totalDamageDealtToChampions'] / target_data['goldEarned']
  ```

  예외 처리를 한 데이터에서 1200초 이상 즉 20분 이상 게임이 지속된 매치만을 추출하였으며
  해당 플레이어 데이터인 match_p와 상대 미들 포지션 데이터인 match_o로 나누어 추출을 진행하였다.

  target_data는 경기의 메타데이터, kda 성과데이터, 그 안에서의 솔로 킬/데스 그리고 추가적인 성과데이터와 분당 지표를 계산한 데이터로 구성했다.

  우선 경기의 메타데이터는 플레이어의 이름, 경기 id와 생성시간, 참여자와 상대의 id, 팀 id, 포지션 마지막으로 매치의 승패 여부 데이터로 구성되어있다.

  ```
  target_data["riotIdGameName"] = match_p['riotIdGameName']
  target_data["matchId"] = df_match['metadata'][0]['matchId']
  target_data["gameCreation"] = match['gameCreation']
  target_data["gameDuration"] = match_p['challenges']['gameLength']
  target_data["participantId"] = match_p['participantId']
  target_data["opponentpId"] = match_o['participantId']
  target_data["teamId"] = match_p['teamId']
  target_data["teamPosition"] = match_p['teamPosition']
  target_data["win"] = match_p['win']
  ```

  kda 성과데잍터는 각 매치의 플레이어의 킬 데스 어시스트 수를 저장하였으며 그 뒤 1:1 상황에서 발생한 솔로 킬 및 데스를 계산하여 추가하였다.

  #### kda

  ```
  target_data['kda'] = match_p['challenges']['kda']
  target_data['kills'] = match_p['kills']
  target_data['deaths'] = match_p['deaths']
  target_data['assists'] = match_p['assists']
  ```
  

  #### solo 킬/데스

  ```
  solo_kill, solo_death = 0, 0
  for frame in match_timeline['frames']:
      for event in frame['events']:
          if (event['type'] == "CHAMPION_KILL") and ('assistingParticipantIds' not in event):
              if (event['killerId'] == target_data['participantId']):
                  solo_kill += 1
              elif (event['victimId'] == target_data['participantId']):
                  solo_death += 1
  ```
  champio_kill 이벤트중 assist가 없는 경우를 솔로 상황으로 간주하였다.

  마지막으로 추가 성과데이터와 분당 성과 지표는 챔피언에게 가한 총 피해량, 받은 총 피해량, 처치한 미니언의 수, 획들 골드와 총 경험치 그리고 이 데이터를 활용해 만든 분당 지표로 이루어져있다,

 #### 추가 성과데이터

  ```
  target_data['totalDamageDealtToChampions'] = match_p['totalDamageDealtToChampions']
  target_data['totalDamageTaken'] = match_p['totalDamageTaken']
  target_data['totalMinionsKilled'] = match_p['totalMinionsKilled']
  target_data['totalCS'] = target_data['totalMinionsKilled'] + match_p['totalEnemyJungleMinionsKilled']
  target_data['goldEarned'] = match_p['goldEarned']
  target_data['totalXP'] = match_timeline['frames'][-1]['participantFrames'][str(target_data['participantId'])]['xp']
  ```

  #### 분당 지표 데이터

  ```
duration = target_data['gameDuration'] / 60
target_data['dpm'] = target_data['totalDamageDealtToChampions'] / duration
target_data['dtpm'] = target_data['totalDamageTaken'] / duration
target_data['mpm'] = target_data['totalMinionsKilled'] / duration
target_data['cspm'] = target_data['totalCS'] / duration
target_data['xpm'] = target_data['totalXP'] / duration
target_data['gpm'] = target_data['goldEarned'] / duration
  ```

| 분당 지표 | 지표 데이터                |
|-----------|---------------------------|
| dpm       | 분당 가한 피해량.         |
| dtpm      | 분당 받은 피해량.         |
| mpm       | 분당 처치한 미니언 수.    |
| cspm      | 분당 총 CS.               |
| xpm       | 분당 경험치.              |
| gpm       | 분당 획득 골드.           |



- 라인전 전, 후 구분

  라인전 전, 후의 기준을 14분으로 설정해 라인전 전인 at14 데이터와 af14 데이터로 나누어 데이터를 추출하였으며 그 뒤 기존 데이터셋인 target데이터 셋에 저장하였다.

  ```
  at14_target_data = {}
            match_timeline_at14 = match_timeline['frames'][:15]
            at14_kill, at14_death, at14_assist = 0, 0, 0
            at14_solo_kill, at14_solo_death = 0, 0
            for frame in match_timeline_at14:
                for event in frame['events']:
                    if (event['type'] == "CHAMPION_KILL") and ('assistingParticipantIds' not in event):
                        if (event['killerId'] == target_data['participantId']):
                            at14_solo_kill += 1
                            at14_kill += 1
                        elif (event['victimId'] == target_data['participantId']):
                            at14_solo_death += 1
                            at14_death += 1
                    elif (event['type'] == "CHAMPION_KILL"):
                        if target_data['participantId'] in event['assistingParticipantIds']:
                            at14_assist += 1
                        elif event['killerId'] == target_data['participantId']:
                            at14_kill += 1
                        elif event['victimId'] == target_data['participantId']:
                            at14_death += 1
            at14_target_data['kills'] = at14_kill
            at14_target_data['deaths'] = at14_death
            at14_target_data['assists'] = at14_assist
            at14_target_data['solokills'] = at14_solo_kill
            at14_target_data['solodeaths'] = at14_solo_death

            match_timeline_14 = match_timeline['frames'][14]
            match_timeline_14_target = match_timeline_14['participantFrames'][str(target_data['participantId'])]
            at14_target_data['gameDuration'] = match_timeline_14['timestamp'] / 1000
            at14_target_data['totalDamageDealtToChampions'] = match_timeline_14_target['damageStats'][
                'totalDamageDoneToChampions']
            at14_target_data['totalDamageTaken'] = match_timeline_14_target['damageStats']['totalDamageTaken']
            at14_target_data['totalMinionsKilled'] = match_timeline_14_target['minionsKilled']
            at14_target_data['totalCS'] = at14_target_data['totalMinionsKilled'] + match_timeline_14_target[
                'jungleMinionsKilled']
            at14_target_data['totalXP'] = match_timeline_14_target['xp']
            at14_target_data['goldEarned'] = match_timeline_14_target['totalGold']

            at14_duration = at14_target_data['gameDuration'] / 60
            at14_target_data['dpm'] = at14_target_data['totalDamageDealtToChampions'] / at14_duration
            at14_target_data['dtpm'] = at14_target_data['totalDamageTaken'] / at14_duration
            at14_target_data['dpd'] = at14_target_data['totalDamageDealtToChampions'] / (
                1 if at14_target_data['deaths'] == 0 else at14_target_data['deaths'])
            at14_target_data['dpg'] = at14_target_data['totalDamageDealtToChampions'] / at14_target_data['goldEarned']
            at14_target_data['gpm'] = at14_target_data['goldEarned'] / at14_duration
            at14_target_data['xpm'] = at14_target_data['totalXP'] / at14_duration
            at14_target_data['mpm'] = at14_target_data['totalMinionsKilled'] / at14_duration
            at14_target_data['cspm'] = at14_target_data['totalCS'] / at14_duration

            # at14와 동일한 항목으로 af14 채워보기 (힌트 : target_data에서 at14_target_data 항목을 뺀다)
            af14_target_data = {}

            af14_target_data['kills'] = target_data['kills'] - at14_target_data['kills']
            af14_target_data['deaths'] = target_data['deaths'] - at14_target_data['deaths']
            af14_target_data['assists'] = target_data['assists'] - at14_target_data['assists']
            af14_target_data['solokills'] = target_data['solokills'] - at14_target_data['solokills']
            af14_target_data['solodeaths'] = target_data['solodeaths'] - at14_target_data['solodeaths']

            af14_target_data['gameDuration'] = target_data['gameDuration'] - at14_target_data['gameDuration']
            af14_target_data['totalDamageDealtToChampions'] = target_data['totalDamageDealtToChampions'] - at14_target_data[
                'totalDamageDealtToChampions']
            af14_target_data['totalDamageTaken'] = target_data['totalDamageTaken'] - at14_target_data['totalDamageTaken']
            af14_target_data['totalMinionsKilled'] = target_data['totalMinionsKilled'] - at14_target_data[
                'totalMinionsKilled']
            af14_target_data['totalCS'] = target_data['totalCS'] - at14_target_data['totalCS']
            af14_target_data['totalXP'] = target_data['totalXP'] - at14_target_data['totalXP']
            af14_target_data['goldEarned'] = target_data['goldEarned'] - at14_target_data['goldEarned']

            af14_target_data['dpm'] = af14_target_data['totalDamageDealtToChampions'] / (
                        af14_target_data['gameDuration'] / 60)
            af14_target_data['dtpm'] = af14_target_data['totalDamageTaken'] / (af14_target_data['gameDuration'] / 60)
            af14_target_data['dpd'] = af14_target_data['totalDamageDealtToChampions'] / (
                1 if af14_target_data['deaths'] == 0 else af14_target_data['deaths'])
            af14_target_data['dpg'] = af14_target_data['totalDamageDealtToChampions'] / af14_target_data['goldEarned']
            af14_target_data['gpm'] = af14_target_data['goldEarned'] / (af14_target_data['gameDuration'] / 60)
            af14_target_data['xpm'] = af14_target_data['totalXP'] / (af14_target_data['gameDuration'] / 60)
            af14_target_data['cspm'] = af14_target_data['totalCS'] / (af14_target_data['gameDuration'] / 60)
            af14_target_data['mpm'] = af14_target_data['totalMinionsKilled'] / (af14_target_data['gameDuration'] / 60)

            target_data['at14'] = at14_target_data
            target_data['af14'] = af14_target_data
            # print(f"{j+1}번째 게임 데이터\n{target_data}")
            # print()
            gamer_data.append(target_data)
  ```

- 격차 및 비율 데이터 산출

  그 뒤 플레이어 데이터인 target데이터와 상대방의 데이터인 opponent데이터를 합쳐 두 데이터의 격차와 비율데이터 산출 과정을 진행하였다.

```
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
```

우선 combat, manage, diff의 데이터로 나누어 구성을 진행하였다.
처음으로 combat 데이터는 플레이어의 킬/데스/어시스트/솔로킬/솔로데스 비율, 분당지표 (dpm, dtpm), 플레이어와 상대의 kda데이터를 취합하였다.

두번째로 manage 데이터는 플레이어의 게임 관리 관련 데이터를 취합한것으로 
cspm (분당 CS), gpm (분당 골드), xpm (분당 경험치),dpd (가한 피해량/데스), dpg (가한 피해량/획득 골드) 로 구성되어있다.
  
마지막으로 플레이어와 상대의 격차를 나타내는 diff 데이터는 dpm, dtpm, cspm, gpm, xpm, dpd, dpg 데이터를 플레이어와 상대의 데이터 차이를 계산해 축가하였다.

- 데이터 가공

그 뒤 마지막으로 윗 단계에서 가공한 데이터들을 merge하여 결과 데이터셋을 완성하였다.

```
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
```

그 뒤 위 데이터를 간단한 테이블 형식의 데이터셋으로 다시금 구성하였다.

```
import pandas as pd
import json

def extract_data_table(gamerName, matches):
    extracted_list = []
    for match in matches:
        match_data = {}
        match_data['gamerName'] = str(gamerName)
        match_data['opponentGamerName'] = match['opponentRiotIdGameName']
        match_data['matchID'] = match['matchId']
        match_data['gameCreation'] = match['gameCreation']
        match_data['gameDuration'] = match['gameDuration']
        match_data['at14gameDuration'] = match['at14']['gameDuration']
        match_data['targetTeamId'] = match['targetTeamId']
        match_data['targetWin'] = match['targetWin']

        # at14
        match_data['at14killsRatio'] = match['at14']['combat']['killsRatio']
        match_data['at14deathsRatio'] = match['at14']['combat']['deathsRatio']
        match_data['at14assistsRatio'] = match['at14']['combat']['assistsRatio']
        match_data['at14solokillsRatio'] = match['at14']['combat']['solokillsRatio']
        match_data['at14solodeathsRatio'] = match['at14']['combat']['solodeathsRatio']
        match_data['at14dpm'] = match['at14']['combat']['dpm']
        match_data['at14dtpm'] = match['at14']['combat']['dtpm']
        match_data['at14cspm'] = match['at14']['manage']['cspm']
        match_data['at14gpm'] = match['at14']['manage']['gpm']
        match_data['at14xpm'] = match['at14']['manage']['xpm']
        match_data['at14dpd'] = match['at14']['manage']['dpd']
        match_data['at14dpg'] = match['at14']['manage']['dpg']
        match_data['at14dpmdiff'] = match['at14']['diff']['dpm']
        match_data['at14dtpmdiff'] = match['at14']['diff']['dtpm']
        match_data['at14cspmdiff'] = match['at14']['diff']['cspm']
        match_data['at14gpmdiff'] = match['at14']['diff']['gpm']
        match_data['at14xpmdiff'] = match['at14']['diff']['xpm']
        match_data['at14dpddiff'] = match['at14']['diff']['dpd']
        match_data['at14dpgdiff'] = match['at14']['diff']['dpg']

        # af14
        match_data['af14killsRatio'] = match['af14']['combat']['killsRatio']
        match_data['af14deathsRatio'] = match['af14']['combat']['deathsRatio']
        match_data['af14assistsRatio'] = match['af14']['combat']['assistsRatio']
        match_data['af14solokillsRatio'] = match['af14']['combat']['solokillsRatio']
        match_data['af14solodeathsRatio'] = match['af14']['combat']['solodeathsRatio']
        match_data['af14dpm'] = match['af14']['combat']['dpm']
        match_data['af14dtpm'] = match['af14']['combat']['dtpm']
        match_data['af14cspm'] = match['af14']['manage']['cspm']
        match_data['af14gpm'] = match['af14']['manage']['gpm']
        match_data['af14xpm'] = match['af14']['manage']['xpm']
        match_data['af14dpd'] = match['af14']['manage']['dpd']
        match_data['af14dpg'] = match['af14']['manage']['dpg']
        match_data['af14dpmdiff'] = match['af14']['diff']['dpm']
        match_data['af14dtpmdiff'] = match['af14']['diff']['dtpm']
        match_data['af14cspmdiff'] = match['af14']['diff']['cspm']
        match_data['af14gpmdiff'] = match['af14']['diff']['gpm']
        match_data['af14xpmdiff'] = match['af14']['diff']['xpm']
        match_data['af14dpddiff'] = match['af14']['diff']['dpd']
        match_data['af14dpgdiff'] = match['af14']['diff']['dpg']
        extracted_list.append(match_data)
    return extracted_list

df = pd.read_json("./merged_data_full.json")

full_table = []

for j in range(len(df)):
    gamerName = df.iloc[j]['GamaName']
    matches = df.iloc[j]['matches']
    gamertable = extract_data_table(gamerName, matches)
    full_table = full_table + gamertable

with open('final_target_data.json', 'w', encoding='utf-8') as f:
    json.dump(full_table, f, ensure_ascii=False, indent=4)
```

