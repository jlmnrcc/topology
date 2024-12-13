'''

'''

import pandas as pd
import json

def check_uniqueness(dataSeries):
    ans = []
    ds_list = dataSeries.to_list()
    for r in ds_list:
        if ds_list.count(r) > 1:
            ans.append(r)
    return set(ans)


def check_topology(dataFrames : list):
    '''
    Simple validation of market topology
    '''
    metaData_df = dataFrames[0]
    biddingZones_df = dataFrames[1]
    biddingZoneBorders_df = dataFrames[2]
    hvdc_df = dataFrames[3]
    lineset_df = dataFrames[4]

    errCount=0
    
    # check bidding zone uniqueness
    fields = ['shortName', 'eic']
    for field in fields:
        nonUnique = check_uniqueness(biddingZones_df[field])
        if len(nonUnique) > 0:
            print("Non-unique " + field + " in bidding zone definition: " + str(nonUnique))
            errCount += 1
    
    # check bidding zone border uniqueness
    fields = ["name"]
    for field in fields:
        nonUnique = check_uniqueness(biddingZoneBorders_df[field])
        if len(nonUnique) > 0:
            print("Non-unique " + field + " in bidding zone border definition: " + str([s + ", " for s in nonUnique]))
            errCount += 1
        
    # check from and to bidding zones exist in list of bidding zones
    shortNameList = biddingZones_df['shortName'].to_list()
    missingFromBz = biddingZoneBorders_df.loc[ biddingZoneBorders_df['from'].isin(shortNameList) == False ]
    for m in missingFromBz['name']:
        print("From- bidding zone of " + m + " was not found in list of bidding zones")
        errCount += 1
    missingToBz = biddingZoneBorders_df.loc[ biddingZoneBorders_df['to'].isin(shortNameList) == False ]
    for m in missingToBz['name']:
        print("To- bidding zone of " + m + " was not found in list of bidding zones")    
        errCount += 1
    
    # check that each bidding zone has pairwise in- and out going borders
    for n in biddingZones_df['shortName']:
        outGoingConnections = biddingZoneBorders_df.loc[biddingZoneBorders_df['from'].isin([n])]
        inGoingConnections = biddingZoneBorders_df.loc[biddingZoneBorders_df['to'].isin([n])]
        for index,m in outGoingConnections.iterrows():
            if not inGoingConnections['from'].isin([m['to']]).any():
                print(m['name'] + " is not matched by an opposite bidding zone border")
                errCount += 1
        for index,m in inGoingConnections.iterrows():
            if not outGoingConnections['to'].isin([m['from']]).any():
                print(m['name'] + " is not matched by an opposite bidding zone border")
                errCount += 1
            
    # check that each bidding zone has the same number of in and out going borders:        
    for n in biddingZones_df['shortName']:
        outGoingConnections = biddingZoneBorders_df.loc[biddingZoneBorders_df['from'].isin([n])]
        inGoingConnections = biddingZoneBorders_df.loc[biddingZoneBorders_df['to'].isin([n])]
        if not len(outGoingConnections) == len(inGoingConnections):
            print(n + " has " + str(len(outGoingConnections)) + " out going and " + str(len(inGoingConnections)) + " ingoing bidding zone borders.")
            errCount += 1
        if len(outGoingConnections) == 0:
            print(n + " has no out going bidding zone borders.")
            errCount += 1
        if len(inGoingConnections) == 0:
            print(n + " has no in going bidding zone borders.")
            errCount += 1
    
    # check that border type is one of: [AC, HVDC, lineset]
    for index,m in biddingZoneBorders_df.iterrows():
        if not (m['type'] == "AC" or m['type'] == "HVDC" or m['type'] == "lineset"):
            print("Bidding zone border: " + m['name'] + " has unknown border type: " + m['type'])
            errCount += 1
    
    # Check that borders that are referenced by HVDC definition exist in list of bidding zone borders
    hvdc_bzbs = []
    for index,m in hvdc_df.iterrows():
        for bzb in m['biddingZoneBorders']:
            # print(bzb)
            if not biddingZoneBorders_df['name'].isin([bzb]).any():
                print('HvdcLink: ' + m['name'] + ' is referencing a bidding zone border: ' + bzb + ' which is not in list of bidding zone borders.')
                errCount += 1
            hvdc_bzbs.append(bzb)

    # check that borders of type HVDC are referenced by an HVDC definiiton
    for index,m in biddingZoneBorders_df.iterrows():
        if m['type']=='HVDC':
            if not (m['name'] in hvdc_bzbs):
                print('Bidding zone border: ' + m['name'] + ' is labelled as type: HVDC. But is not associated to an hvdc definition.')
                errCount += 1
    
    # check that borders of type lineset exist among the lineset definitions
    for index,m in biddingZoneBorders_df.iterrows():
        if m['type']=='lineset':
            if not lineset_df['name'].isin([m['name']]).any():
                print('Bidding zone border: ' + m['name'] + ' is labelled as type: lineset. But borderName is not found in lineset definitions')
                errCount += 1

    # check that borders referenced by a lineset exist in the borders list
    for index,m in lineset_df.iterrows():
        for mb in m['mappedBorders']:
            if not biddingZoneBorders_df['name'].isin([mb]).any():
                print('Lineset: ' + m['name'] + ' has mapped border: ' + mb + ' which is non-existing in the borders definition')
                errCount += 1
                
    print('Validation of topology file: ' + metaData_df['name'].values[0] + ' terminated with ' + str(errCount) + ' errors.')
    
    # if errCount == 0:
        # exportTopology(topologyFileName,metaData_df,biddingZones_df,biddingZoneBorders_df,hvdc_df,lineset_df)        

    return errCount == 0

def export_topology(outFile:str, dataFrames:list):
    # result = {}
    result = json.loads(dataFrames[0].to_json(orient="records"))[0]
    # a = json.loads(dataFrames[0].to_json(orient="records"))
    # a[0]['newField']=10
    # print(a)
    result["biddingZones"] = json.loads(dataFrames[1].to_json(orient="records"))
    result["biddingZoneBorders"] = json.loads(dataFrames[2].to_json(orient="records"))
    result["hvdcLinks"] = json.loads(dataFrames[3].to_json(orient="records"))
    result["linesets"] = json.loads(dataFrames[4].to_json(orient="records"))
    
    with open(outFile,'+w') as f:
        json.dump(result, f, indent=4)


def load_topology_from_excel(topologyFileName:str):

    metaData_df = pd.read_excel(topologyFileName, sheet_name="metaData")

    biddingZones_df = pd.read_excel(topologyFileName, sheet_name="biddingZones")

    biddingZoneBorders_df = pd.read_excel(topologyFileName, sheet_name="biddingZoneBorders")

    hvdc_df = pd.read_excel(topologyFileName, sheet_name="hvdcLinks")
    hvdc_df['biddingZoneBorders'] = hvdc_df.biddingZoneBorders.apply(lambda x: eval(x))
    
    lineset_df = pd.read_excel(topologyFileName, sheet_name="linesets")
    lineset_df['mappedBorders'] = lineset_df.mappedBorders.apply(lambda x: eval(x))
    
    dataFrames = [metaData_df, biddingZones_df, biddingZoneBorders_df, hvdc_df, lineset_df]

    return dataFrames



def load_map_from_excel(map_file_name:str):
    metaData_df = pd.read_excel(map_file_name, sheet_name="metaData")
    
    map_df = pd.read_excel(map_file_name, sheet_name="map")
    
    mapDataFrames = [metaData_df, map_df]

    return mapDataFrames


def export_topology_map(outputFileName:str, mapDataFrames:list):
    result = {}
    result["metaData"] = json.loads(mapDataFrames[0].to_json(orient="records"))
    result["map"] = json.loads(mapDataFrames[1].to_json(orient="records"))
    
    with open(outputFileName,'+w') as f:
        json.dump(result, f, indent=4)



def validate_map(map_dataFrames : list, topology1_dataFrames : list, topology2_dataFrames : list):
    errCount = 0
    mapMetaData, map_df = map_dataFrames
    
    top1_metaData, top1_biddingZones, top1_biddingZoneBorders, top1_hvdc, top1_lineset = topology1_dataFrames
    top2_metaData, top2_biddingZones, top2_biddingZoneBorders, top2_hvdc, top2_lineset = topology2_dataFrames
    
    if not mapMetaData['topology1Name'].values == top1_metaData['name'].values:
        errCount += 1
        print('Error: Mapped name topology 1 does not match name of topology 1')
    if not mapMetaData['topology1version'].values == top1_metaData['version'].values:
        errCount += 1
        print('Error: Mapped version topology 1 does not match version of topology 1')

    if not mapMetaData['topology2Name'].values == top2_metaData['name'].values:
        errCount += 1
        print('Error: Mapped name topology 2 does not match name of topology 2')
    if not mapMetaData['topology2version'].values == top2_metaData['version'].values:
        errCount += 1
        print('Error: Mapped version topology 2 does not match version of topology 2')

    # a key is not found in topology1 -> error
    # a value is not founf in topology2 -> error

    # for index,k in map_df.iterrows():
        # if not top1_biddingZoneBorders['name'].isin([k['key']]).any():
            # errCount += 1
            # print('Error: Map key ' + k['key'].values + ' was not found in topology1 bidding zone borders')
        # if not top2_biddingZoneBorders['name'].isin([k['value']]).any():
            # errCount += 1
            # print('Error: Map value ' + k['key'].values + ' was not found in topology2 bidding zone borders')

    #todo:  a bidding zone border in topology1 is not found in the list of keys -> warning
    #todo: a bidding zone botder in topology2 is not found in the list of values -> warning

    return errCount == 0


def validate_all():
    # Todo: validate all topology files in directory
    return None


def export_excel():
    #Todo: export topology / topology map in excel file for easy editing.
    return None

def load_from_json():
    #Todo: import JSON formatted topology file / topology map.
    return None


def validate_and_export(topology1file, topology2file, top_map_file):
    topology1 = load_topology_from_excel(path + topology1file)
    if  check_topology(topology1):
        export_topology(path + topology1file.replace('.xlsx','.JSON'), topology1)    
    else:
        print("Topology validation failed. JSON export omitted.")

    topology2 = load_topology_from_excel(path + topology2file)
    if  check_topology(topology2):
        export_topology(path + topology2file.replace('.xlsx','.JSON'), topology2)    
    else:
        print("Topology validation failed. JSON export omitted.")
        
    top_map = load_map_from_excel(path + top_map_file)
    if validate_map(top_map, topology1, topology2):
        export_topology_map(path + top_map_file.replace('.xlsx','.JSON'), top_map)
    else:
        print('Validation of map: '+ top_map_file +' failed. No export created')

    return
    
    

if __name__=="__main__":
    
    path = "..\\data\\"
    
    # Todo: setup for commanline execution
    
    # test_top1 = load_topology_from_excel('topology_testSet.xlsx')
    # if  check_topology(test_top1):
        # export_topology('topology_testSet.JSON', test_top1)
    # else:
        # print("Topology validation failed. JSON export omitted.")

    # test_top_ntc = load_topology_from_excel(path + 'topology_NTC2024v1.xlsx')
    # if  check_topology(test_top_ntc):
        # export_topology(path + 'topology_NTC2024v1.JSON', test_top_ntc)    
    # else:
        # print("Topology validation failed. JSON export omitted.")

    # test_top_fb = load_topology_from_excel(path + 'topology_FB2024v1.xlsx')
    # if  check_topology(test_top_fb):
        # export_topology(path + 'topology_FB2024v1.JSON', test_top_fb)    
    # else:
        # print("Topology validation failed. JSON export omitted.")
        
    
    
    # fb_ntc_map = load_map_from_excel(path + 'map_FB2024v1-NTC2024v1.xlsx')
    # success=validate_map(fb_ntc_map, test_top_fb, test_top_ntc)
    # if success:
        # export_topology_map(path + "FB_to_NTC_map.JSON", fb_ntc_map)
    # else:
        # print('Validation of map failed. No export created')
    
    # ntc_fb_map = load_map_from_excel(path + 'map_NTC2024v1-FB2024v1.xlsx')
    # success=validate_map(ntc_fb_map, test_top_ntc, test_top_fb)
    # if success:
        # export_topology_map(path + "NTC_to_FB_map.JSON", ntc_fb_map)
    # else:
        # print('Validation of map failed. No export created')

    topology1file = "topology_entsoeTP.xlsx"
    topology2file = "topology_intradayNTC.xlsx"
    top_map_file = "map_entsoeTP-intradayNTC.xlsx"
    
    validate_and_export(path + "topology_entsoeTP.xlsx", path + "topology_intradayNTC.xlsx", path + "map_entsoeTP-intradayNTC.xlsx")
    
    validate_and_export(path + "topology_ig107.xlsx", path + "topology_intradayNTC.xlsx", path + "map_ig107-intradayNTC.xlsx")
    
    validate_and_export(path + "topology_FB2024v1.xlsx", path + "topology_intradayNTC.xlsx", path + "map_FB2024v1-intradayNTC.xlsx")

    validate_and_export(path + "topology_intradayNTC.xlsx", path + "topology_FB2024v1.xlsx", path + "map_intradayNTC-FB2024v1.xlsx")    
    
    validate_and_export(path + "topology_FB2024v1.xlsx", path + "topology_ig107.xlsx", path + "map_FB2024v1-ig107.xlsx")    
    
    validate_and_export(path + "topology_atceFB.xlsx", path + "topology_ig107.xlsx", path + "map_atceFB-ig107.xlsx")    

    # topology1 = load_topology_from_excel( path + "topology_atce_FB.xlsx")
    
    # if  check_topology(topology1):
        # export_topology(path + 'topology_atce_FB.JSON', topology1)    
    # else:
        # print("Topology validation failed. JSON export omitted.")    
    