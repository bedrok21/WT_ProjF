mongo_url = "mongodb+srv://bedrok:88888888@cluster0.fvbyipn.mongodb.net/?retryWrites=true&w=majority"

import azure.functions as func
import json
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr


client = AsyncIOMotorClient(mongo_url)

database = client['obmen']
users_collection = database["users"]

class User(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str

app = func.FunctionApp()

@app.route(route="user", auth_level=func.AuthLevel.ANONYMOUS)
async def http_method1(req: func.HttpRequest) -> func.HttpResponse:

    if req.method == 'GET':
        users = []
        cursor = users_collection.find()
        async for document in cursor:
            document["_id"] = str(document["_id"])
            users.append(document)
        return func.HttpResponse(body=json.dumps({"message":"Ok", "data": users}),
                                 status_code=200,
                                 headers= {
                                    "Content-Type": "application/json",
                                })

    if req.method == 'POST':
        try:
            data = json.loads(req.get_body().decode('utf-8'))
            user = User
            user.model_validate_json(req.get_body().decode('utf-8'))
            await users_collection.insert_one(data)
            return func.HttpResponse(body=json.dumps({"message":"Ok"}),
                                    status_code=200,
                                    headers= {
                                        "Content-Type": "application/json",
                                    })
        except:
            return func.HttpResponse(body=json.dumps({"message":"Error"}),
                                    status_code=200,
                                    headers= {
                                        "Content-Type": "application/json",
                                    })


@app.route(route="user/{_id}", auth_level=func.AuthLevel.ANONYMOUS)
async def http_method2(req: func.HttpRequest) -> func.HttpResponse:

    if req.method == 'GET':
        user = None
        cursor = users_collection.find({"_id": ObjectId(req.route_params["_id"])})
        async for document in cursor:
            document["_id"] = str(document["_id"])
            user = document
            break
        if user is not None:
            return func.HttpResponse(body=json.dumps({"message":"Ok", "data": user}),
                                    status_code=200,
                                    headers= {
                                        "Content-Type": "application/json",
                                    })
        else:
            return func.HttpResponse(body=json.dumps({"message":"Not Found"}),
                                status_code=200,
                                headers= {
                                    "Content-Type": "application/json",
                                })

    if req.method == 'DELETE':
        result = await users_collection.delete_one({"_id": ObjectId(req.route_params["_id"])})
        if result.deleted_count > 0:
            return func.HttpResponse(body=json.dumps({"message":"Deleted"}),
                                    status_code=200,
                                    headers= {
                                        "Content-Type": "application/json",
                                    })
        else:
            return func.HttpResponse(body=json.dumps({"message":"Not Found"}),
                                    status_code=200,
                                    headers= {
                                        "Content-Type": "application/json",
                                    })
