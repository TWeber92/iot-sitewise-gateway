import boto3
import time
import os
import json
import csv
from datetime import datetime

# os.environ['AWS_PROFILE'] = 'default' # console profile
# os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

assetMeasurements =['Y Servo Motor Temperature',
'B Servo Motor Temperature',
'C Servo Motor Temperature',
'Y Encoder Temperature',
'B Encoder Temperature',
'C Encoder Temperature',
'Y Insulation Resistance',
'B Insulation Resistance',
'C Insulation Resistance',
'Y Positioning Average Torque',
'B Positioning Average Torque',
'C Positioning Average Torque',
'Y Positioning Max Torque',
'B Positioning Max Torque',
'C Positioning Max Torque',
'Spindle 1 Motor Temp',
'Spindle 1 Insulation Resistance',
'WTC Servo Motor Temperature',
'X1 Servo Motor Temperature',
'X1 Encoder Temperature',
'X1 Insulation Resistance',
'X1 Positioning Max Torque',
'X1 Positioning Average Torque',
'Z1 Servo Motor Temperature',
'Z1 Encoder Temperature',
'Z1 Insulation Resistance',
'Z1 Positioning Average Torque',
'Z1 Positioning Max Torque',
'K1 Servo Motor Temperature',
'K1 Encoder Temperature',
'K1 Insulation Resistance',
'K1 Positioning Average Torque',
'K1 Positioning Max Torque',
'Y1 Encoder Temperature '
'Spindle 2 Insulation Resistance',
'U Servo Motor Temperature '
'U Encoder Temperature '
'U Positioning Max Torque '
'Spindle 2 Motor Temp'
'X Servo Motor Temperature',
'Z Servo Motor Temperature',
'A Servo Motor Temperature',
'X Encoder Temperature',
'Z Encoder Temperature',
'A Encoder Temperature',
'X Insulation Resistance',
'Z Insulation Resistance',
'A Insulation Resistance',
'X Positioning Average Torque',
'Z Positioning Average Torque',
'A Positioning Average Torque',
'X Positioning Max Torque',
'Z Positioning Max Torque',
'A Positioning Max Torque',
'U Insulation Resistance',
'U Positioning Average Torque',
'W Encoder Temperature',
'W Insulation Resistance',
'W Positioning Average Torque',
'W Positioning Max Torque',
'W Servo Motor Temperature',
'Y1 Servo Motor Temperature',
'Y2 Servo Motor Temperature',
'Y2 Encoder Temperature',
'Y1 Insulation Resistance',
'Y2 Insulation Resistance',
'Y1 Positioning Average Torque',
'Y2 Positioning Average Torque',
'Y1 Positioning Max Torque',
'Y2 Positioning Max Torque',
'A2 Servo Motor Temperature',
'X2 Servo Motor Temperature',
'A2 Encoder Temperature',
'X2 Encoder Temperature',
'A2 Insulation Resistance',
'X2 Insulation Resistance',
'A2 Positioning Average Torque',
'X2 Positioning Average Torque',
'A2 Positioning Max Torque',
'X2 Positioning Max Torque',
'Z2 Servo Motor Temperature',
'Z2 Encoder Temperature',
'Z2 Insulation Resistance',
'Z2 Positioning Average Torque',
'Z2 Positioning Max Torque',
'K2 Servo Motor Temperature',
'K2 Encoder Temperature',
'K2 Insulation Resistance',
'K2 Positioning Average Torque',
'K2 Positioning Max Torque',
'ARM Insulation Resistance',
'XC1 Servo Motor Temperature',
'YA2 Servo Motor Temperature',
'XC1 Encoder Temperature',
'YA2 Encoder Temperature',
'XC1 Insulation Resistance',
'YA2 Insulation Resistance',
'XC1 Positioning Average Torque',
'YA2 Positioning Average Torque',
'XC1 Positioning Max Torque',
'YA2 Positioning Max Torque',
'YS Servo Motor Temperature',
'AT Servo Motor Temperature',
'AM1 Servo Motor Temperature',
'YS Encoder Temperature',
'AT Encoder Temperature',
'AM1 Encoder Temperature',
'YS Insulation Resistance',
'AT Insulation Resistance',
'AM1 Insulation Resistance',
'YS Positioning Average Torque',
'AT Positioning Average Torque',
'AM1 Positioning Average Torque',
'YS Positioning Max Torque',
'AT Positioning Max Torque',
'AM1 Positioning Max Torque',
'BMG Servo Motor Temperature',
'BMG Encoder Temperature',
'BMG Insulation Resistance',
'BMG Positioning Average Torque',
'BMG Positioning Max Torque',
'WTC Encoder Temperature',
'WTC Insulation Resistance',
'WTC Positioning Average Torque',
'WTC Positioning Max Torque',]

def get_asset_details(asset_id):
    asset_properties = []
    try:
        #Assuming asset relationship hierarchy is not more that the maxResults, if more than maxResults then this function has to be modified
        response = iotsitewise_client.describe_asset(assetId=asset_id)
        for ap in response['assetProperties']:
            if ("alias" in ap):# and ap["name"] in assetMeasurements
                asset_property = {}
                asset_property["name"]=ap["name"]
                asset_property["alias"]=ap["alias"]
                asset_properties.append(asset_property)
            else:
                continue
        return asset_properties
    except Exception as e:
        return ""

def get_assetModel_properties(asset_id):
    asset_properties = []
    try:
        #Assuming asset relationship hierarchy is not more that the maxResults, if more than maxResults then this function has to be modified
        response = iotsitewise_client.describe_asset_model(assetModelId=asset_id)
        for ap in response['assetModelProperties']:
            asset_property = {}
            asset_property["name"]=ap["name"]
            # asset_property["dataType"]=ap["dataType"]
            
            if ("parentAssetId" in response['assetModelProperties']):
                asset_property["typename"] = 'attribute';
            elif("measurement" in response['assetModelProperties']):
                asset_property["typename"] = 'measurement';
            else: asset_property["typename"] = 'other';
            asset_properties.append(asset_property)  
        return asset_properties
    except Exception as e:
        return ""


def get_parent_asset_name(asset_id):
    
    try:
        #Assuming asset relationship hierarchy is not more that the maxResults, if more than maxResults then this function has to be modified
        response = iotsitewise_client.list_asset_relationships(assetId=asset_id, traversalType='PATH_TO_ROOT', maxResults=response_max_results)
        hierarchy_info = response["assetRelationshipSummaries"][0]["hierarchyInfo"]
        
        if ("parentAssetId" in hierarchy_info):
            parent_asset_id =  hierarchy_info["parentAssetId"]
            parent_asset_name = iotsitewise_client.describe_asset(assetId=parent_asset_id)["assetName"]
        else:
            parent_asset_id = ""
            parent_asset_name = ""

        return parent_asset_id, parent_asset_name 
    except Exception as e:
        return "", ""


def list_asset_models():
    print("list_asset_models method call>> open")
    asset_models = []
    next_token = ""
    
    while next_token != None:
        if(next_token == ""):
            response = iotsitewise_client.list_asset_models(maxResults=response_max_results)
        else:
            response = iotsitewise_client.list_asset_models(nextToken=next_token, maxResults=response_max_results)
        
        for ams in response['assetModelSummaries']:
            asset_model = {}
            asset_model["id"]=ams["id"]
            asset_model["name"]=ams["name"]
            asset_model["status"]=ams["status"]
            asset_models.append(asset_model)    
            
        next_token=response.get('nextToken')
    
    print("list_asset_models method call>> closed") 
    return asset_models       


def list_assets(asset_models):
    models_assets = []
    print("List_assets method call>> open")

    # asset_models = [{"id":"b6b0ca76-56d2-4df1-985b-45bdd70672ff","name":"TMMK-PWT-CNC-FANUC"}]
    # asset_models = [{"id":"98ecadb1-7ec7-446f-9fb8-6bc611beba54","name":"TMMK-PWT-CNC-FANUC"}]#QA Model
    if asset_models == None:
        asset_models = list_asset_models()

    for ams in asset_models:
        next_token = ""

        while next_token != None:
            if(next_token == ""):
                response = iotsitewise_client.list_assets(maxResults=response_max_results, assetModelId=ams["id"])
            else:
                response = iotsitewise_client.list_assets(nextToken=next_token, maxResults=response_max_results, assetModelId=ams["id"])
            
            for asset_summary in response['assetSummaries']:
                print("Calling get_asset_details() for:",asset_summary["id"])   
                astprp= get_asset_details(asset_summary["id"])
                for asset_property in astprp:
                    model_asset = {}
                    model_asset["asset_id"]=asset_summary["id"]
                    model_asset["asset_name"]=asset_summary["name"]
                    model_asset["asset_status"]=asset_summary["status"]
                    if("description" in asset_summary):
                        model_asset["asset_description"]=asset_summary["description"]
                    else:
                        model_asset["asset_description"]=""
                    # model_asset["parent_asset_id"]=get_parent_asset_name(asset_summary["id"])[0]
                    # model_asset["parent_asset_name"]=get_parent_asset_name(asset_summary["id"])[1]
                    model_asset["model_name"]=ams["name"]
                    model_asset["model_id"]=ams["id"]
                    model_asset["asset_propertyname"]=asset_property["name"]
                    model_asset["asset_alias"]=asset_property["alias"]
                    models_assets.append(model_asset)
                
            next_token=response.get('nextToken') 
    
    print("List_assets method call>closed.")    
    return models_assets


def write_to_csv(header, rows, csv_filepath):
    with open(csv_filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for row in rows:
            #data = [row["asset_id"], row["asset_name"], row["asset_description"], row["parent_asset_id"], row["parent_asset_name"], row["model_name"], row["model_id"]]
            # data = [row["asset_name"], row["parent_asset_name"], row["model_name"], row["asset_odepropertyname"], row["asset_alias"]]
            data = [row["asset_name"], row["model_name"], row["asset_propertyname"], row["asset_alias"]]
            writer.writerow(data)

if __name__ == "__main__":
    print("Asset mapping from IoT sitewise started.")
    starttime = datetime.now()
    sitewise_env = "Measurements_QA"
    response_max_results = 250
    iotsitewise_client = boto3.client('iotsitewise') 
    
    # assetprop = get_assetModel_properties("b6b0ca76-56d2-4df1-985b-45bdd70672ff")
    # astprp= get_asset_details("0d53c0b9-a190-4e44-a023-fe941b99f0d7")
    
    
    # #csv_headers = ["AssetId", "AssetName", "AssetDescription", "ParentAssetId", "ParentAssetName", "ModelName", "ModelId"]
    # csv_headers = ["AssetName", "ParentAssetName", "ModelName", "PropertyName", "Alias"]
    csv_headers = ["AssetName", "ModelName", "PropertyName", "Alias"]
    asset_models = [{"id":"057bdfea-2dc4-4d21-8d0f-c54ffec0e36c","name":"Extrusion Line 2"}]
    # asset_modelsQa = [{"id":"e7de3d56-e300-498a-a890-bac851b75468","name":"ProductionLines"}]
    
    csv_rows = list_assets(asset_models)
    write_to_csv(csv_headers, csv_rows,  f"assets_{sitewise_env}.csv")  

    print("Asset mapping from IoT sitewise ended for Dev.")
    # os.environ['AWS_PROFILE'] = 'QA' # console profile
    # sitewise_env = "QA"
    # iotsitewise_client = boto3.client('iotsitewise') 
    
    # csv_headers = ["AssetName", "ModelName", "PropertyName", "Alias"]
    # asset_models = [{"id":"98ecadb1-7ec7-446f-9fb8-6bc611beba54","name":"TMMK-PWT-CNC-FANUC"}]#QA Model
    # csv_rows = list_assets(asset_models)
    # write_to_csv(csv_headers, csv_rows,  f"assets_{sitewise_env}.csv")  

    difftime = datetime.now() - starttime
    print("Asset mapping from IoT sitewise completed.")
    print("Utility took time(mins):", divmod(difftime.total_seconds(), 60)[0] )