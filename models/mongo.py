#10.100.11.161   lab-mongo-01
#10.100.11.162   lab-mongo-02
#10.100.11.163   lab-mongo-03

from pymongo import MongoClient

class MongoConnection():
    def __init__(self, instance):
        self.instance = instance

    def client(self):
        client = MongoClient(f"mongodb://{self.instance}:27017/")
        return client.EMV
        
client = MongoClient("10.100.11.161", username='evm', password='abc1234', authSource='evm')
db = client["evm"]
db.atividade.insert_one({"id": 4076, "nome": "Analise de Vulnerabilidade do Ambiente", "idservico": 4075, "idportfolio": 77, "idcontrato": 12})
#tb = db["atividade"]
#query={"id":4076}
#mydoc = tb.find(query)
#print(mydoc)
#for x in mydoc:
    #print(x.get("nome"))

#db.command("createUser", "evm", pwd="abc1234", roles=[{'role':'readWrite','db':'evm'}])
#print(client.list_database_names())