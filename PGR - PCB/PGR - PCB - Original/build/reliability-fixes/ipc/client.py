from pathlib import Path
import sys,time,uuid
sys.path.insert(0,str(Path(__file__).parent/'bindings'))
import pynng
from google.protobuf import symbol_database,message_factory,json_format
from google.protobuf.empty_pb2 import Empty
from common import envelope_pb2 as envelope
from common.commands import base_commands_pb2 as base,editor_commands_pb2 as editor,project_commands_pb2 as project
from common.types import base_types_pb2 as types,enums_pb2 as enums
from board import board_types_pb2 as board,board_commands_pb2 as bc
from schematic import schematic_types_pb2 as sch,schematic_commands_pb2 as sc
ROOT=Path(__file__).resolve().parents[3]
SOCKET='/tmp/pgr-reliability-20261025.sock'
def unpack(a):
 d=symbol_database.Default().pool.FindMessageTypeByName(a.TypeName());m=message_factory.GetMessageClass(d)();assert a.Unpack(m);return m
class API:
 def __init__(self):
  self.connection=pynng.Req0(dial='ipc://'+SOCKET,block_on_dial=True,send_timeout=30000,recv_timeout=30000);self.token='';self.request(base.Ping(),Empty)
 def request(self,c,response_type):
  for retry in range(60):
   q=envelope.ApiRequest();q.header.client_name='works.backplane.pgr-reliability-fixes';q.header.kicad_token=self.token;q.message.Pack(c);self.connection.send(q.SerializeToString());a=envelope.ApiResponse.FromString(self.connection.recv());self.token=a.header.kicad_token
   if a.status.status==envelope.AS_BUSY:time.sleep(.2);continue
   if a.status.status!=envelope.AS_OK:raise RuntimeError(str(a.status)+' for '+c.DESCRIPTOR.full_name)
   out=response_type();assert a.message.Unpack(out),a;return out
  raise RuntimeError('API stayed busy')
 def open(self,kind):
  try:
   docs=self.request(editor.GetOpenDocuments(type=kind),editor.GetOpenDocumentsResponse)
   if docs.documents:return docs.documents[0]
  except RuntimeError as e:
   if 'AS_UNHANDLED' not in str(e):raise
  return self.request(project.OpenDocument(type=kind,path=str(ROOT/('PGR.kicad_pcb' if kind==types.DOCTYPE_PCB else 'PGR.kicad_sch'))),project.OpenDocumentResponse).document
 def items(self,d,ts):
  r=self.request(editor.GetItems(header=types.ItemHeader(document=d),types=ts),editor.GetItemsResponse);assert r.status==types.IRS_OK,r;return [unpack(x) for x in r.items]
 def update(self,d,items):
  c=editor.UpdateItems(header=types.ItemHeader(document=d))
  for x in items:c.items.add().Pack(x)
  r=self.request(c,editor.UpdateItemsResponse)
  assert r.status==types.IRS_OK,r
  for x in r.updated_items:assert x.status.code==editor.ISC_OK,r
  return r
 def create(self,d,items):
  c=editor.CreateItems(header=types.ItemHeader(document=d))
  for x in items:c.items.add().Pack(x)
  r=self.request(c,editor.CreateItemsResponse);assert r.status==types.IRS_OK,r
  for x in r.created_items:assert x.status.code==editor.ISC_OK,r
  return r
 def delete(self,d,ids):
  c=editor.DeleteItems(header=types.ItemHeader(document=d),item_ids=[types.KIID(value=i) for i in ids]);r=self.request(c,editor.DeleteItemsResponse);return r
 def begin(self,d):return self.request(editor.BeginCommit(header=types.ItemHeader(document=d)),editor.BeginCommitResponse).id
 def end(self,d,id,msg,drop=False):return self.request(editor.EndCommit(header=types.ItemHeader(document=d),id=id,action=editor.CMA_DROP if drop else editor.CMA_COMMIT,message=msg),editor.EndCommitResponse)
 def save(self,d):return self.request(project.SaveDocument(document=d),Empty)
def v(x,y):return types.Vector2(x_nm=round(x*1e6),y_nm=round(y*1e6))
def xy(o):return (o.x_nm/1e6,o.y_nm/1e6)
def clone(x):y=type(x)();y.CopyFrom(x);return y
if __name__=='__main__':
 api=API()
 for kind,ts,name in [(types.DOCTYPE_SCHEMATIC,[enums.KOT_SCH_SYMBOL,enums.KOT_SCH_LINE,enums.KOT_SCH_JUNCTION,enums.KOT_SCH_NO_CONNECT],'schematic'),(types.DOCTYPE_PCB,[enums.KOT_PCB_FOOTPRINT,enums.KOT_PCB_TRACE,enums.KOT_PCB_VIA,enums.KOT_PCB_ZONE],'board')]:
  d=api.open(kind);print(name,d)
  items=api.items(d,ts)
  (Path(__file__).parent/(name+'-before.json')).write_text(json_format.MessageToJson(editor.GetItemsResponse(items=[__import__('google.protobuf.any_pb2',fromlist=['Any']).Any() for _ in []]))) if False else None
  import json
  (Path(__file__).parent/(name+'-before.json')).write_text(json.dumps([json_format.MessageToDict(x,preserving_proto_field_name=True) | {'_type':x.DESCRIPTOR.full_name} for x in items],indent=2))
  for x in items:
   if x.DESCRIPTOR.name=='SchematicSymbolInstance' and x.reference_field.text.text in ['U3','U4','R22','R23','C15'] or x.DESCRIPTOR.name=='FootprintInstance' and x.reference_field.text.text in ['U3','U4','R22','R23','C15','U8']:
    print(x)
